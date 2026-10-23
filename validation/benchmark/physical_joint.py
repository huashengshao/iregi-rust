#!/usr/bin/env python3
"""Run and qualify equivalent physical numerical pipelines, with retained evidence.

No numerical process runs without --execute. Separate timer runs are never
treated as paired samples. Run from the project root after scripts/env.sh.
"""
import argparse
import copy
import datetime
import json
import math
import os
from pathlib import Path
import platform
import random
import shutil
import signal
import statistics
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import physical_alignment as alignment

kernel = alignment.load("joint_kernel", HERE / "run.py")
workspace_builder = alignment.load("joint_workspace_builder", HERE / "build_workspace.py")
_saved = {name: sys.modules.get(name) for name in ["run", "build_physical"]}
try:
    sys.modules["run"] = kernel
    sys.modules["build_physical"] = alignment.load("joint_build", HERE / "build_physical.py")
    rust = alignment.load("joint_rust", HERE / "physical_run.py")
finally:
    for _name, _module in _saved.items():
        if _module is None:
            sys.modules.pop(_name, None)
        else:
            sys.modules[_name] = _module

STAGES = list(rust.HOT_STAGES)
REFERENCE_STAGES = ["numerator", "numerator_assembly", "reduction", "total"]
THREADS = ["RAYON_NUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"]


def timestamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def load(path):
    return json.loads(Path(path).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def positive_integer(value):
    return type(value) is int and value > 0


def require_phase_success(phase_record, engine):
    require(phase_record.get("status") == "complete" and type(phase_record.get("returncode")) is int
            and phase_record["returncode"] == 0, engine + " producer process did not complete successfully")


def checked_samples(values, expected=None):
    require(isinstance(values, list) and values, "missing timing samples")
    require(expected is None or len(values) == expected, "timing block count differs")
    require(all(type(value) in (int, float) and math.isfinite(value) and value > 0
                for value in values), "timings must be positive finite non-boolean numbers")
    return values


def independent_ratio(rust_samples, reference_samples, seed=161803, resamples=10000):
    """Ratio of medians; independent resampling, including unequal sample counts."""
    a, b = checked_samples(rust_samples), checked_samples(reference_samples)
    require(positive_integer(resamples), "invalid bootstrap sample count")
    def divide(numerator, denominator):
        value = numerator / denominator
        require(math.isfinite(value) and value > 0, "timing ratio exceeds representable positive range")
        return value
    rng = random.Random(seed)
    draws = [divide(statistics.median(rng.choices(a, k=len(a))),
                    statistics.median(rng.choices(b, k=len(b)))) for _ in range(resamples)]
    ratio = divide(statistics.median(a), statistics.median(b))
    low, high = (kernel.quantile(draws, p) for p in [0.005, 0.995])
    width = (high - low) / ratio
    require(0 < low <= high and all(math.isfinite(x) for x in [low, high, width]) and width >= 0,
            "bootstrap interval exceeds finite range")
    return dict(ratio=ratio, ci99=[low, high], relative_ci_width=width,
                statistical_gate=("inconclusive-noise" if width > 0.02 else
                                  "improvement" if high < 1 else
                                  "regression" if low > 1 else "parity"),
                method="independent bootstrap of ratio of medians; Rust / MadLoop ns per complete batch",
                resamples=resamples, seed=seed, sample_counts=[len(a), len(b)],
                confidence_scope="per-family operational interval, not simultaneous family confidence or a formal equivalence test")


def record_file(path, expected=None):
    path = Path(path).resolve()
    sha = kernel.digest(path)
    require(expected is None or sha == expected, f"file identity differs: {path}")
    return dict(path=str(path), sha256=sha)


def verify_file(record):
    return record_file(record["path"], record["sha256"])


def retain_file(source, destination, expected=None):
    source = Path(source)
    record_file(source, expected)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return record_file(destination, expected)


def validate_build_completion(build):
    """Resolve a compatible child manifest without inventing missing exit data.

    Early workspace exporters omitted returncode and before-build inventories.
    Their immutable parent and actual Cargo stream can supply that evidence;
    the original child/parent manifests are never edited or silently upgraded.
    """
    require(build.get("kind") == "physical-rust-build" and build.get("status") == "complete"
            and build.get("provenance_qualified") is True and "release" in build.get("profile", ""),
            "Rust build is not a qualified release build")
    parent_path = build.get("workspace_build_manifest")
    if not parent_path:
        require(type(build.get("returncode")) is int and build["returncode"] == 0, "missing successful standalone build exit")
        require(build["source_sha256_before"] == build["source_sha256"]
                and build["assets_sha256_before"] == build["assets_sha256"], "Rust build inputs changed")
        return dict(kind="standalone-build", returncode=0)
    parent_record = record_file(parent_path)
    parent = load(parent_path)
    require(parent.get("kind") == "workspace-benchmark-build"
            and parent.get("status") == "complete" and parent.get("provenance_qualified") is True,
            "workspace parent is not a completed qualified build")
    exit_code = parent.get("resources", {}).get("returncode")
    require(type(exit_code) is int and exit_code == 0, "parent has no recorded successful Cargo exit")
    if "returncode" in build:
        require(type(build["returncode"]) is int and build["returncode"] == exit_code, "child Cargo exit differs")
    require(Path(parent["manifest_path"]).resolve() == Path(parent_path).resolve(), "parent manifest path differs")
    shared_fields = ["status", "started_at", "finished_at", "command", "requested_revision", "source_revision",
                     "source_root", "master_backend", "backend_qualification", "environment", "profile", "rustc", "cargo",
                     "source_sha256", "assets_sha256", "provenance_qualified"]
    require(all(build[name] == parent[name] for name in shared_fields), "child and parent build identities differ")
    for field in ["source_sha256", "assets_sha256"]:
        require(parent[field + "_before"] == parent[field], "workspace inputs changed during compilation")
        if field + "_before" in build:
            require(build[field + "_before"] == parent[field + "_before"], "child before-build inventory differs")
    require(parent["master_backend"] in {"SymbolicaBatch", "RustBatch"}, "unknown scalar backend")
    cargo_path = Path(parent_path).parent / "cargo.jsonl"
    cargo_record = record_file(cargo_path)
    examples, libraries = workspace_builder.inspect_artifacts(cargo_path, parent["master_backend"] == "RustBatch")
    require(parent["cargo_artifacts"] == dict(examples=examples, libraries=libraries), "Cargo artifact stream differs from parent")
    artifact = parent["binaries"]["physical_benchmark"]
    event = examples["physical_benchmark"]
    require(artifact["path"] == build["binary_path"] and artifact["sha256"] == build["binary_sha256"],
            "child binary differs from retained parent artifact")
    require(event["executable"] == artifact["original_path"] and event["target"]["src_path"] ==
            str(Path(parent["source_root"]) / "crates/iregi-cli/examples/physical_benchmark.rs"),
            "Cargo executable/source binding differs")
    binary_record = record_file(artifact["path"], artifact["sha256"])
    library_paths = {path for event in libraries for path in event["filenames"] if path.endswith(".rlib")}
    require({entry["original_path"] for entry in parent["archives"]} == library_paths,
            "retained libraries differ from actual Cargo artifacts")
    archives = [record_file(entry["path"], entry["sha256"]) for entry in parent["archives"]]
    builders = [record_file(entry["retained_path"], entry["sha256"]) for entry in parent["builder"]["files"]]
    return dict(kind="verified-workspace-parent", returncode=exit_code, parent_manifest=parent_record,
                cargo_stream=cargo_record, binary=binary_record, archives=archives, builder_sources=builders,
                bound_fields=shared_fields, source_revision=parent["source_revision"],
                child_fields_supplied_by_parent=[field for field in ["returncode", "source_sha256_before", "assets_sha256_before"] if field not in build])


def reference_files(case, reference):
    """Resolve every producer/build object while this generated case still exists."""
    p = reference["provenance"]
    generated = ROOT / "target/physical" / case
    logs = Path(reference["log_directory"])
    files = {
        "producer.py": (ROOT / "validation/physical/madloop/benchmark.py", p["script_sha256"]),
        "capture.py": (ROOT / "validation/physical/madloop/run.py", p["capture_script_sha256"]),
        "check": (ROOT / p["executable_path"], p["executable_sha256"]),
        "libiregi-benchmark.a": (logs / "libiregi-benchmark.a", p["library_sha256"]),
        "param_card.dat": (generated / "Cards/param_card.dat", p["parameters_sha256"]),
        "MadLoopParams.dat": (generated / "SubProcesses/MadLoop5_resources/MadLoopParams.dat", p["reduction_card_sha256"]),
        "evaluation.log": (logs / "evaluation.log", None),
        "reference-build.json": (ROOT / "target/reference/provenance.json", None),
    }
    for field in ["generated_sources", "linked_archives"]:
        require(p.get(field), f"missing reference {field}")
        files.update({f"generated/{name}": (generated / name, sha) for name, sha in p[field].items()})
    require(load(files["reference-build.json"][0]) == p["reference_build"], "reference build manifest changed")
    return files


def retain_reference(case, reference, directory):
    alignment.validate_reference(case, reference)
    return {name: retain_file(source, directory / name, sha)
            for name, (source, sha) in reference_files(case, reference).items()}


def validate_reference_producer(case, reference, files, options):
    alignment.validate_reference(case, reference)
    for record in files.values():
        verify_file(record)
    p = reference["provenance"]
    for name, sha in [("producer.py", p["script_sha256"]), ("capture.py", p["capture_script_sha256"]),
                      ("check", p["executable_sha256"]), ("libiregi-benchmark.a", p["library_sha256"]),
                      ("param_card.dat", p["parameters_sha256"]), ("MadLoopParams.dat", p["reduction_card_sha256"])]:
        require(files[name]["sha256"] == sha, "retained reference provenance differs: " + name)
    require(p["script_sha256"] == alignment.digest(ROOT / "validation/physical/madloop/benchmark.py")
            and p["capture_script_sha256"] == alignment.digest(ROOT / "validation/physical/madloop/run.py"),
            "reference producer differs from the checked implementation")
    for field in ["generated_sources", "linked_archives"]:
        for name, sha in p[field].items():
            require(files[f"generated/{name}"]["sha256"] == sha, "generated reference input differs")
    require(load(files["reference-build.json"]["path"]) == p["reference_build"], "reference manifest differs")
    require("-O3" in reference["flags"] and "-O3" in p["reference_build"]["flags"], "reference is not optimized")
    requested = reference["requested_options"]
    for field, expected in dict(case=case, helicity=1, input_policy="preserve", cpu=options["cpu"],
                                repeats=options["repeats"], warmup=options["warmup"],
                                target_ms=options["block_ms"], batch_widths=options["batches"]).items():
        require(requested.get(field) == expected, "reference request mismatch: " + field)
    require(reference["cpu_affinity"] == [options["cpu"]] and reference["measurement_status"] == "pinned",
            "reference CPU pin differs")
    require(set(reference["samples"]) == set(map(str, options["batches"])), "reference batch set differs")
    require(reference["repeats"] == options["repeats"] and reference["warmup_blocks"] == options["warmup"]
            and reference["target_block_ms"] == options["block_ms"], "reference timing protocol differs")
    text = Path(files["evaluation.log"]["path"]).read_text()
    require(alignment.madloop.observed_modes(text) == reference["observed_call_modes"], "reference mode log differs")
    actual_policy = alignment.madloop.observed_input_policy(text, "preserve", reference["graph"]["group"])
    require(json.loads(json.dumps(actual_policy)) == reference["observed_input_policy"],
            "reference policy log differs")
    previous_case = alignment.capture.CASE
    try:
        alignment.capture.CASE = alignment.capture.CASES[case]
        records, metadata = alignment.capture.parse(Path(files["evaluation.log"]["path"]))
    finally:
        alignment.capture.CASE = previous_case
    require(metadata == reference["metadata"] and reference["reference_record"] in records,
            "ordinary reference output differs from retained log")
    logged = {}
    for line in text.splitlines():
        fields = line.split()
        if fields and fields[0] == "IREGI_BENCH_SAMPLE":
            require(len(fields) == 6, "malformed reference timing log")
            width, stage, repeat, iterations = map(int, fields[1:5])
            name = alignment.madloop.STAGES[stage]
            row = logged.setdefault((str(width), name), [])
            require(repeat == len(row) + 1, "duplicate or missing reference timing block")
            row.append((iterations, float(fields[5])))
    require(set(logged) == {(str(width), stage) for width in options["batches"] for stage in REFERENCE_STAGES},
            "reference log stage/batch set differs")
    for width in options["batches"]:
        stages = reference["samples"][str(width)]
        require(set(stages) == set(REFERENCE_STAGES + ["preparation", "masters"]), "reference stage set differs")
        for stage in REFERENCE_STAGES:
            row = stages[stage]
            checked_samples(row["samples_ns"], options["repeats"])
            require(row["unit"] == "ns/batch" and positive_integer(row["iterations_per_block"]), "reference units/iterations differ")
            require(logged[(str(width), stage)] == [(row["iterations_per_block"], x) for x in row["samples_ns"]],
                    "reference raw timing log differs from result")


def validate_rust_provenance(data, files, options):
    require(data["kind"] == "physical-pipeline-benchmark" and data["status"] == "complete", "Rust run incomplete")
    require(data["provenance_qualified"] is True and rust.provenance_qualified(data), "Rust provenance unqualified")
    for record in files.values():
        verify_file(record)
    build = data["build"]
    require(load(files["build"]["path"]) == build, "Rust build manifest differs")
    completion = validate_build_completion(build)
    require(kernel.source_hashes(Path(build["source_root"])) == build["source_sha256"], "retained Rust sources changed")
    require(files["binary"]["sha256"] == data["binary"]["sha256"] == build["binary_sha256"], "Rust binary differs")
    require(files["oracle"]["sha256"] == data["oracle"]["sha256"], "canonical oracle differs")
    require(files["inputs"]["sha256"] == data["inputs"]["sha256"], "Rust inputs differ")
    built_assets = rust.physical_asset_hashes(Path(build["source_root"]))
    live_assets = rust.physical_asset_hashes(ROOT)
    require(data["build_assets_sha256"] == build["assets_sha256"] == built_assets, "immutable physical assets changed")
    require(data["assets_sha256"] == live_assets and rust.numeric_asset_hashes(built_assets) == rust.numeric_asset_hashes(live_assets),
            "numerical assets differ from build or changed during run")
    require(data["validation_producer_sha256"] == rust.validation_producer_hashes(kernel.source_hashes(), live_assets),
            "live validation producer identity changed")
    require(data["environment"]["affinity"] == [options["cpu"]] and data["environment"]["cpu"] == options["cpu"],
            "Rust CPU pin differs")
    require(data["thread_environment"] == {name: "1" for name in THREADS}, "Rust thread policy differs")
    protocol = data["protocol"]
    for field, expected in dict(repeats=options["repeats"], warmup=options["warmup"], target_block_ms=options["block_ms"]).items():
        require(protocol[field] == expected, "Rust timing protocol differs: " + field)
    return completion


def check_output(case, width, output, configuration, canonical, reference):
    require(len(output.get("samples", [])) == width, "Rust returned wrong batch width")
    require(output.get("execution", {}).get("input_rows") == width, "Rust execution batch width differs")
    for lane in output["samples"]:
        for poles in lane.get("moments", []):
            require(len(poles) == 4, "incomplete native tensor slots")
            for pair in poles:
                alignment.finite_pair(pair)
    tensors = rust.check(output, configuration, case, canonical)
    graph = alignment.compare_rust_output(case, reference, output)
    require(tensors["passed"] and graph["passed"], "canonical tensors or preserved graph coefficients disagree")
    return dict(canonical_tensors=tensors, preserved_graph=graph)


def validate_rust_row(case, width, row, files, reference, options, backend):
    configuration = rust.request_configuration(case, "f64", 53, 53, "hybrid", width)
    require(row["status"] == "measured" and row["id"] == configuration["id"]
            and row["case"] == case and row["batch_width"] == width
            and row["precision"] == "f64" and row["bits"] == 53 and row["accuracy_bits"] == 53,
            "Rust family row is failed, missing or mismatched")
    require(row["master_backend"] == backend, "observed scalar backend differs from build")
    canonical = load(files["canonical"]["path"])
    sample = configuration["input"]["samples"][0]
    for record in canonical:
        mode = record["mode"]
        expected = {"id": f"{case.replace('-', '_')}_physical_benchmark_mode{mode}",
                    "api": "tensor", "mode": mode, "rank": sample["rank"], "dimension_shift": 0,
                    "mu": sample["mu"], "snap": False, "threshold": "1e-6", "propagators": sample["propagators"]}
        require(record["input"] == expected, "canonical oracle request differs")
        stdout = Path(files[f"canonical-mode{mode}-stdout"]["path"]).read_text()
        logged_results = [json.loads(line[7:]) for line in stdout.splitlines() if line.startswith("RESULT ")]
        require(logged_results == record.get("results", []), "canonical oracle raw output differs")
        if "error" not in record:
            require(record["returncode"] == 0 and len(record["results"]) == 1
                    and record["results"][0]["id"] == expected["id"], "canonical oracle result identity differs")
    initial = check_output(case, width, row["initial_output"], configuration, canonical, reference)
    responses = [json.loads(line) for line in Path(files["responses"]["path"]).read_text().splitlines()]
    require(responses and responses[0]["request"] == {"op": "prepare", "id": configuration["id"]},
            "missing or unexpected preparation response")
    require(responses[0]["response"]["output"] == row["initial_output"], "initial output differs from raw response")
    require(responses[0]["response"]["master_backend"] == backend, "raw preparation backend differs")
    measured = {stage: [] for stage in STAGES}
    pilots = set()
    profiles = []
    actual_order = []
    for index, entry in enumerate(responses):
        request, response = entry["request"], entry["response"]
        rust.validate_response(response, request, configuration["id"])
        check_output(case, width, response["output"], configuration, canonical, reference)
        if index == 0:
            continue
        require(request.get("op") == "measure" and request.get("stage") in STAGES, "unexpected adapter operation")
        stage = request["stage"]
        require(positive_integer(request["iterations"]) and request["repeats"] == 1, "invalid Rust block shape")
        checked_samples(response["total_ns"], 1)
        if request.get("profile", False):
            require(stage == "reduction" and request["warmup"] == 0 and len(pilots) == len(STAGES), "unexpected profile block")
            profiles.append(response)
        elif stage not in pilots:
            require(request["iterations"] == 1 and request["warmup"] == options["warmup"]
                    and not any(measured.values()), "missing or misplaced calibration block")
            pilots.add(stage)
        else:
            require(request["warmup"] == 0 and not profiles, "unexpected timed warmup or ordering")
            require(request["iterations"] == row["stages"][stage]["iterations_per_block"], "Rust iteration count differs")
            measured[stage].append(response["total_ns"][0])
            actual_order.append(stage)
    require(set(row["stages"]) == set(STAGES) and pilots == set(STAGES), "missing Rust stage")
    require(actual_order == [stage for order in row["stage_orders"] for stage in order]
            and len(row["stage_orders"]) == options["repeats"]
            and all(sorted(order) == sorted(STAGES) for order in row["stage_orders"]), "Rust stage order differs")
    require(len(profiles) == options["repeats"], "missing separate profiling blocks")
    summaries = {name: rust.summarized([response["profile_ns"][0][index] for response in profiles])
                 for index, name in enumerate(["arguments", "masters", "reduction", "total"])}
    require(row["profiled_components"] == summaries, "profile summaries differ from separate raw response blocks")
    for stage in STAGES:
        values = row["stages"][stage]
        require(positive_integer(values["iterations_per_block"]), "invalid Rust iterations")
        checked_samples(values["samples_ns"], options["repeats"])
        require(values["samples_ns"] == measured[stage], "Rust raw timing responses differ from result")
    return dict(initial=initial, checked_responses=len(responses), canonical=canonical)


def finish_rows(data, normal):
    for row in data["rows"]:
        if row["status"] == "pending":
            row.update(status="not_run", error="run ended before this family started")
        elif row["status"] == "running":
            row.update(status="interrupted", error="run ended during this family")
    data["status"] = "complete" if normal else "interrupted"
    data["performance_parity_established"] = normal and bool(data["rows"]) and all(
        row.get("gate") in {"improvement", "parity"} for row in data["rows"])
    data["counts"] = {status: sum(row["status"] == status for row in data["rows"])
                      for status in sorted({row["status"] for row in data["rows"]})}


def phase(command, directory, timeout, ledger, save):
    directory.mkdir(parents=True, exist_ok=True)
    ledger.update(status="running", command=command, started_utc=timestamp(), hostname=platform.node())
    save()
    process = None
    start = time.monotonic()
    try:
        with (directory / "process.log").open("w") as log:
            env = dict(os.environ, **{name: "1" for name in THREADS})
            process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                       env=env, start_new_session=True)
            code = process.wait(timeout=timeout)
            ledger.update(status="complete" if code == 0 else "failed", returncode=code)
    except subprocess.TimeoutExpired:
        ledger.update(status="timeout")
        raise
    finally:
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        if ledger["status"] == "running":
            ledger["status"] = "interrupted"
        ledger.update(finished_utc=timestamp(), wall_seconds=time.monotonic() - start,
                      log=record_file(directory / "process.log"))
        save()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Run both numerical engines (requires the coordinated runtime/quiet slot)")
    parser.add_argument("--rust", type=Path, default=Path("target/optimized/release/examples/physical_benchmark"))
    parser.add_argument("--build-manifest", type=Path, default=Path("target/benchmark/physical/physical-rust-build.json"))
    parser.add_argument("--oracle", type=Path, default=Path("target/reference/iregi-reference-original"))
    parser.add_argument("--cases", nargs="+", choices=alignment.physical.CASES, default=list(alignment.physical.CASES))
    parser.add_argument("--batches", nargs="+", type=int, default=[1, 32])
    parser.add_argument("--cpu", type=int, default=0)
    parser.add_argument("--build-cpus", default="16,17")
    parser.add_argument("--repeats", type=int, default=21)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--block-ms", type=float, default=30)
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--phase-timeout", type=float, default=3600)
    parser.add_argument("--quiet-window-note", default="", help="Recorded coordinated quiet-window context; omission keeps timing unqualified")
    parser.add_argument("--output", type=Path, default=Path("target/benchmark/physical-joint/results.json"))
    args = parser.parse_args(argv)
    require(Path.cwd().resolve() == ROOT, f"run from {ROOT}")
    require(len(set(args.cases)) == len(args.cases) and len(set(args.batches)) == len(args.batches), "duplicate families")
    require(all(positive_integer(x) for x in args.batches) and args.repeats >= 3 and args.warmup >= 0, "invalid counts")
    require(all(math.isfinite(x) and x > 0 for x in [args.block_ms, args.timeout, args.phase_timeout]), "invalid time limits")
    cpus = {int(x) for x in args.build_cpus.split(",")}
    require(cpus and cpus.issubset(os.sched_getaffinity(0)) and args.cpu in os.sched_getaffinity(0), "CPU outside available affinity")
    args.output = args.output.resolve()
    require(not args.output.parent.exists() or not any(args.output.parent.iterdir()),
            "refusing to overwrite joint evidence; choose a fresh output directory")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    options = dict(cpu=args.cpu, batches=args.batches, repeats=args.repeats, warmup=args.warmup, block_ms=args.block_ms)
    data = dict(schema_version=1, kind="equivalent-physical-pipeline-benchmark", status="running", started_utc=timestamp(),
                options=options, hostname=platform.node(), producer_sha256=kernel.source_hashes(),
                physical_assets_sha256=rust.physical_asset_hashes(ROOT),
                numerator_evidence=record_file(ROOT / "validation/physical/numerator-evidence.json"),
                quiet_window_note=args.quiet_window_note, thread_environment={name:"1" for name in THREADS},
                timing_design="sequential independent runs per graph; Rust first, MadLoop second; no pairing of block indices",
                limitations=["Separate runs are sensitive to drift between engines; bootstrap intervals describe within-run sampling only",
                             "A quiet-window note records coordination, not proof of absence of host interference",
                             "Repeated fixed-point lanes do not establish phase-space throughput"],
                phases={}, rows=[dict(case=case, batch_width=width, status="pending", gate="not_run")
                                for case in args.cases for width in args.batches], performance_parity_established=False)
    save = lambda: kernel.save(args.output, data)
    save()
    if not args.execute:
        data["status"] = "planned"
        save()
        print(args.output)
        return 0
    normal = False
    try:
        common = args.output.parent / "retained"
        retained = {"binary": retain_file(args.rust, common / "physical_benchmark"),
                    "oracle": retain_file(args.oracle, common / "iregi-reference-original"),
                    "build": retain_file(args.build_manifest, common / "physical-rust-build.json")}
        data["retained"] = retained
        data["build_completion"] = validate_build_completion(load(retained["build"]["path"]))
        save()
        for case in args.cases:
            rows = [row for row in data["rows"] if row["case"] == case]
            directory = args.output.parent / case
            directory.mkdir(parents=True, exist_ok=True)
            for row in rows:
                row.update(status="running", contract=alignment.contract(case))
            phases = data["phases"][case] = {}
            save()
            try:
                rust_path = directory / "rust.json"
                command = [sys.executable, str(HERE / "physical_run.py"), "--rust", retained["binary"]["path"],
                           "--build-manifest", retained["build"]["path"], "--oracle", retained["oracle"]["path"],
                           "--cases", case, "--precision", "f64", "--accuracy-bits", "53", "--algorithm", "hybrid",
                           "--batches", *map(str,args.batches), "--stages", *STAGES, "--repeats", str(args.repeats),
                           "--warmup", str(args.warmup), "--block-ms", str(args.block_ms), "--timeout", str(args.timeout),
                           "--cpu", str(args.cpu), "--output", str(rust_path)]
                phase(command, directory / "rust-phase", args.phase_timeout, phases.setdefault("rust", {}), save)
                require(rust_path.exists(), "Rust phase produced no result ledger")
                rust_data = load(rust_path)
                files = dict(retained, result=record_file(rust_path), inputs=record_file(Path(rust_data["inputs"]["path"])))
                phases["rust"]["files"] = files
                # Keep MadLoop failures visible even if Rust correctness already failed.
                command = ["taskset", "--cpu-list", ",".join(map(str, sorted(cpus | {args.cpu}))), sys.executable,
                           "validation/physical/madloop/benchmark.py", "--case", case, "--input-policy", "preserve",
                           "--cpu", str(args.cpu), "--repeats", str(args.repeats), "--warmup", str(args.warmup),
                           "--target-ms", str(args.block_ms), "--batch-widths", *map(str,args.batches)]
                phase(command, directory / "madloop-phase", args.phase_timeout, phases.setdefault("madloop", {}), save)
                reference_path = ROOT / f"target/physical/{case}-benchmark-preserve.json"
                reference = load(reference_path)
                phases["madloop"]["result"] = retain_file(reference_path, directory / "madloop.json")
                require_phase_success(phases["madloop"], "MadLoop")
                ref_files = retain_reference(case, reference, directory / "reference-provenance")
                phases["madloop"]["files"] = ref_files
                validate_reference_producer(case, reference, ref_files, options)
                require_phase_success(phases["rust"], "Rust")
                phases["rust"]["build_completion"] = validate_rust_provenance(rust_data, files, options)
                require(rust_data["environment"]["hostname"] == data["hostname"], "Rust host differs")
                expected = [{"case": case, "configuration": rust.request_configuration(case, "f64", 53, 53, "hybrid", width)} for width in args.batches]
                require(load(files["inputs"]["path"]) == expected, "Rust full input/configuration identity differs")
                require(len(rust_data["rows"]) == len(rows), "Rust family set differs")
                for row in rows:
                    width = row["batch_width"]
                    try:
                        matches = [r for r in rust_data["rows"] if r.get("case") == case and r.get("batch_width") == width]
                        require(len(matches) == 1, "missing or duplicate Rust family")
                        source = matches[0]
                        family_dir = directory / source["id"]
                        canonical_dir = directory / rust_data["rows"][0]["id"]
                        row_files = {"responses": record_file(family_dir / "responses.jsonl"),
                                     "canonical": record_file(canonical_dir / "reference-records.json")}
                        for mode in [0, 1, 2]:
                            for stream in ["stdout", "stderr"]:
                                row_files[f"canonical-mode{mode}-{stream}"] = record_file(canonical_dir / f"reference-mode{mode}.{stream}")
                        row["files"] = row_files
                        row["correctness"] = validate_rust_row(case, width, source, row_files, reference, options, rust_data["build"]["master_backend"])
                        row["rust_stages"] = source["stages"]
                        row["rust_profiled_components"] = source["profiled_components"]
                        row["madloop_stages"] = reference["samples"][str(width)]
                        row["ratio"] = independent_ratio(source["stages"]["numerical_end_to_end"]["samples_ns"], reference["samples"][str(width)]["total"]["samples_ns"])
                        row["pipeline_summaries"] = {
                            "rust": rust.summarized(source["stages"]["numerical_end_to_end"]["samples_ns"]),
                            "madloop": rust.summarized(reference["samples"][str(width)]["total"]["samples_ns"])}
                        narrow = all(summary["relative_ci_width"] <= 0.02 for summary in row["pipeline_summaries"].values())
                        qualified = bool(args.quiet_window_note) and args.repeats >= 21 and args.warmup >= 3 and args.block_ms >= 30
                        row.update(status="measured", gate=(row["ratio"]["statistical_gate"] if narrow else "inconclusive-noise") if qualified else "diagnostic-protocol",
                                   timing_protocol_qualified=qualified)
                    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
                        row.update(status="failed", gate="correctness-or-protocol-failed", error=f"{type(error).__name__}: {error}")
                    save()
            except (ValueError, KeyError, TypeError, IndexError, OSError, subprocess.TimeoutExpired) as error:
                for row in rows:
                    if row["status"] == "running":
                        row.update(status="timeout" if isinstance(error, subprocess.TimeoutExpired) else "failed",
                                   gate="unqualified", error=f"{type(error).__name__}: {error}")
                save()
        normal = True
    finally:
        finish_rows(data, normal)
        try:
            unchanged = (kernel.source_hashes() == data["producer_sha256"]
                         and rust.physical_asset_hashes(ROOT) == data["physical_assets_sha256"])
            verify_file(data["numerator_evidence"])
        except (OSError, ValueError, KeyError) as error:
            unchanged = False
            data["final_provenance_error"] = f"{type(error).__name__}: {error}"
        data.update(finished_utc=timestamp(), producer_inputs_unchanged=unchanged)
        if not unchanged:
            data["performance_parity_established"] = False
            for row in data["rows"]:
                if row["status"] == "measured":
                    row.update(gate="provenance-changed", timing_protocol_qualified=False)
        save()
    print(args.output)
    return 0 if normal and data["producer_inputs_unchanged"] and all(row["status"] == "measured" for row in data["rows"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())

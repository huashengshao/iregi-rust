"""Paired, CPU-pinned tensor-kernel measurements with full-output validation.

Only Python's standard library is required. Symbolic preparation and process
transport are not part of kernel timings. Failed cases are retained in the JSON.
"""
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import selectors
import statistics
import subprocess
import tempfile
import time

ROOT = Path.cwd()
MODE = {"Ibp": 0, "PassarinoVeltman": 1, "Hybrid": 2}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze_executable(binary, expected_digest, label):
    """Execute retained bytes, even if Cargo later replaces the selected file."""
    contents = Path(binary).read_bytes()
    if hashlib.sha256(contents).hexdigest() != expected_digest:
        raise ValueError(f"{label} executable changed before launch")
    directory = ROOT / "target/benchmark/executables"
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=label + "-", dir=directory, delete=False) as target:
        target.write(contents)
        path = Path(target.name)
    path.chmod(0o500)
    return path


def source_hashes(root=ROOT):
    files = [root / "Cargo.toml", root / "Cargo.lock"]
    files += sorted((root / "crates").rglob("*.rs"))
    files += sorted((root / "crates").rglob("Cargo.toml"))
    # Path-patched dependencies are not identified by Cargo.lock alone. Include
    # generated evaluator assets and provenance as well as their Rust sources.
    files += sorted(p for p in (root / "dependencies").rglob("*") if p.is_file()
                    and not any(part in {"target", ".git", "__pycache__"} for part in p.relative_to(root / "dependencies").parts))
    files += sorted((root / "validation/benchmark").glob("*.py"))
    files += sorted((root / "validation/benchmark").glob("*.f90"))
    return {str(p.relative_to(root)): digest(p) for p in files}


def command_output(command):
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except (OSError, subprocess.CalledProcessError) as error:
        return str(error)


def environment(cpu):
    frequency = Path(f"/sys/devices/system/cpu/cpu{cpu}/cpufreq")
    cpu_info = {}
    for block in Path("/proc/cpuinfo").read_text().split("\n\n"):
        fields = dict(line.split(":", 1) for line in block.splitlines() if ":" in line)
        fields = {k.strip(): v.strip() for k, v in fields.items()}
        if fields.get("processor") == str(cpu):
            cpu_info = fields
            break
    return {
        "platform": platform.platform(), "hostname": platform.node(), "cpu": cpu,
        "affinity": sorted(os.sched_getaffinity(0)), "cpu_info": cpu_info,
        "frequency": {p.name: p.read_text().strip() for p in frequency.glob("*") if p.is_file() and os.access(p, os.R_OK)},
        "rustc": command_output(["rustc", "--version", "--verbose"]),
        "gfortran": command_output([os.environ.get("FC", "gfortran"), "--version"]).splitlines()[0],
        "revision": command_output(["git", "rev-parse", "HEAD"]),
        "dirty": bool(command_output(["git", "status", "--porcelain"])),
        "source_sha256": source_hashes(),
    }


class Process:
    def __init__(self, binary, label, directory, timeout):
        self.binary = binary
        self.timeout = timeout
        self.log = (directory / f"{label}.stderr.log").open("a")
        self.process = subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self.log, bufsize=0)
        os.set_blocking(self.process.stdin.fileno(), False)
        os.set_blocking(self.process.stdout.fileno(), False)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)
        self.buffer = b""

    def request(self, text):
        if self.process.poll() is not None:
            raise RuntimeError(f"benchmark process already exited: {self.process.returncode}")
        deadline = time.monotonic() + self.timeout
        payload = memoryview(text.encode())
        sent = 0
        self.selector.register(self.process.stdin, selectors.EVENT_WRITE)
        try:
            while time.monotonic() < deadline:
                if sent == len(payload):
                    while b"\n" in self.buffer:
                        line, self.buffer = self.buffer.split(b"\n", 1)
                        if line.startswith(b"RESULT "):
                            return json.loads(line[7:])
                events = self.selector.select(max(0.0, deadline - time.monotonic()))
                if not events:
                    break
                for key, _ in events:
                    if key.fileobj is self.process.stdin:
                        try:
                            sent += os.write(self.process.stdin.fileno(), payload[sent:])
                        except BlockingIOError:
                            continue
                        if sent == len(payload):
                            self.selector.unregister(self.process.stdin)
                    else:
                        try:
                            chunk = os.read(self.process.stdout.fileno(), 65536)
                        except BlockingIOError:
                            continue
                        if not chunk:
                            raise RuntimeError(
                                f"benchmark process exited without RESULT: {self.process.poll()}"
                            )
                        self.buffer += chunk
            self.process.kill()
            self.process.wait()
            raise TimeoutError("benchmark request exceeded timeout; retained as failed")
        finally:
            # A timeout or early child failure can occur before all input was
            # transmitted. Keep the selector reusable and cleanup nonblocking.
            try:
                self.selector.unregister(self.process.stdin)
            except KeyError:
                pass

    def close(self):
        if self.process.poll() is None:
            try:
                os.write(self.process.stdin.fileno(), b"QUIT\n")
                self.process.wait(timeout=5)
            except (BrokenPipeError, BlockingIOError, subprocess.TimeoutExpired):
                self.process.kill()
                self.process.wait()
        self.selector.close()
        self.process.stdin.close()
        self.process.stdout.close()
        self.log.close()


def suite(ranks, mass_classes, batches):
    cases = []
    for n in (2, 3):
        shifts = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0.25, 1.25, 0]][:n]
        for rank in ranks:
            for mass_class in mass_classes:
                samples = []
                for lane in range(max(batches)):
                    # Binary-exact perturbations exercise independent samples
                    # without introducing a random near-threshold subset.
                    dilation = 1.0 + lane / 256.0
                    samples.append({
                        "shifts": [[x * dilation for x in p] for p in shifts],
                        "masses": [[0.0 if mass_class == "massless" else (i + 2) ** 2 + lane / 64.0,
                                    -(i + 1) / 8.0 if mass_class == "complex" else 0.0] for i in range(n)],
                        "mu": 3.0,
                    })
                cases.append({"id": f"n{n}-r{rank}-{mass_class}", "n": n, "rank": rank,
                              "mass_class": mass_class, "samples": samples})
    return cases


def rust_request(case, samples, algorithm, warmup, iterations, profile=False):
    return json.dumps({"id": case["id"], "n": case["n"], "rank": case["rank"],
                       "algorithm": algorithm, "samples": samples, "warmup": warmup,
                       "repeats": 1, "iterations": iterations, "profile": profile}) + "\n"


def fortran_request(case, samples, algorithm, warmup, iterations):
    mu = samples[0]["mu"]
    if any(sample["mu"] != mu for sample in samples):
        raise ValueError("Fortran benchmark currently requires one common scale per batch")
    lines = [f'BENCH {case["id"]} {MODE[algorithm]} {case["n"]} {case["rank"]} '
             f'{mu:.17g} {len(samples)} {warmup} 1 {iterations}']
    for sample in samples:
        for shift, mass in zip(sample["shifts"], sample["masses"]):
            lines.append(" ".join(f"{x:.17g}" for x in shift) + f" ({mass[0]:.17g},{mass[1]:.17g})")
    return "\n".join(lines) + "\n"


def degrees(rank):
    return [r for r in range(rank + 1) for t in range(r, -1, -1)
            for x in range(r - t, -1, -1) for _ in range(r - t - x, -1, -1)]


def validate_response(result, case, *, profile=None):
    if result.get("id") != case["id"]:
        raise ValueError("benchmark response has a mismatched case identity")
    if not isinstance(result.get("stable"), bool):
        raise ValueError("benchmark response has a missing or invalid stability flag")
    values = result.get("total_ns")
    if (not isinstance(values, list) or len(values) != 1
            or any(isinstance(value, bool) or not isinstance(value, (int, float))
                   or not math.isfinite(value) or value <= 0 for value in values)):
        raise ValueError("benchmark response has missing or invalid timing values")
    if profile is not None:
        if result.get("profiled") is not profile:
            raise ValueError("Rust response has a mismatched profiling mode")
        components = result.get("profile_ns")
        if profile:
            if not isinstance(components, dict) or set(components) != {"arguments", "masters", "reduction", "total"}:
                raise ValueError("Rust response has missing profile components")
            for values in components.values():
                if (not isinstance(values, list) or len(values) != 1
                        or any(isinstance(value, bool) or not isinstance(value, (int, float))
                               or not math.isfinite(value) or value < 0 for value in values)):
                    raise ValueError("Rust response has invalid profile timing values")
        elif components is not None:
            raise ValueError("uninstrumented Rust response contains profile timings")


def compare(rust, reference, case, samples):
    errors = []
    max_error = 0.0
    if not rust.get("stable", False) or not reference.get("stable", False):
        errors.append("at least one timed evaluation reported failure or instability")
    if len(rust.get("lanes", [])) != len(samples) or len(reference.get("lanes", [])) != len(samples):
        return {"status": "failed", "errors": ["missing output lanes"], "max_error": None}
    tensor_degrees = degrees(case["rank"])
    for lane, (actual, expected, sample) in enumerate(zip(rust["lanes"], reference["lanes"], samples)):
        if actual["status"] != "success" or expected["status"] != "success":
            errors.append(f"lane {lane}: Rust {actual['status']}, IREGI {expected['status']}")
            continue
        if len(actual["moments"]) != len(tensor_degrees) or len(expected["moments"]) != len(tensor_degrees):
            errors.append(f"lane {lane}: incomplete tensor basis")
            continue
        energy = max(1.0, sample["mu"], *(abs(x) for p in sample["shifts"] for x in p),
                     *(math.sqrt(math.hypot(*mass)) for mass in sample["masses"]))
        for moment, (a, b, degree) in enumerate(zip(actual["moments"], expected["moments"], tensor_degrees)):
            unit = energy ** (4 + degree - 2 * case["n"])
            if len(a) != 4 or len(b) != 4:
                errors.append(f"lane {lane}, moment {moment}: incomplete Laurent coefficients")
                continue
            for pole, (av, bv) in enumerate(zip(a, b)):
                if any(not isinstance(value, list) or len(value) != 2
                       or any(isinstance(part, bool) or not isinstance(part, (int, float))
                              or not math.isfinite(part) for part in value)
                       for value in (av, bv)):
                    errors.append(f"lane {lane}, moment {moment}, pole {pole}: malformed or nonfinite complex coefficient")
                    continue
                error = math.hypot(av[0] - bv[0], av[1] - bv[1]) / (unit + math.hypot(*bv))
                if not math.isfinite(error):
                    errors.append(f"lane {lane}, moment {moment}, pole {pole}: nonfinite output")
                    continue
                max_error = max(max_error, error)
                if error > 1e-10:
                    errors.append(f"lane {lane}, moment {moment}, pole {pole}: scaled error {error:.17g}")
    return {"status": "passed" if not errors else "failed", "errors": errors, "max_error": max_error,
            "tolerance": 1e-10, "normalization": "abs(a-b)/(E^(4+rank-2*n)+abs(b)); E=max(1,mu,abs(shifts),sqrt(abs(mass_squared)))"}


def quantile(values, fraction):
    values = sorted(values)
    index = fraction * (len(values) - 1)
    low = math.floor(index)
    high = math.ceil(index)
    return values[low] * (high - index) + values[high] * (index - low) if low != high else values[low]


def summarize(values, seed=173, resamples=10000):
    if not values:
        return None
    rng = random.Random(seed)
    medians = [statistics.median(rng.choices(values, k=len(values))) for _ in range(resamples)]
    median = statistics.median(values)
    return {"samples_ns": values, "unit": "ns/batch", "median_ns": median,
            "ci99_ns": [quantile(medians, 0.005), quantile(medians, 0.995)],
            "minimum_ns": min(values), "maximum_ns": max(values),
            "relative_mad": statistics.median(abs(x - median) for x in values) / median if median else None}


def ratio_summary(rust, reference, correctness):
    ratios = [a / b for a, b in zip(rust, reference)]
    data = summarize(ratios)
    if data is None:
        return None
    low, high = data["ci99_ns"]
    median = data["median_ns"]
    narrow = (high - low) / median <= 0.02
    gate = ("correctness-failed" if correctness["status"] != "passed" else
            "improvement" if narrow and high < 1 else
            "parity" if narrow and low <= 1 <= high else
            "regression" if narrow and low > 1 else "inconclusive-noise")
    return {"samples": ratios, "median": median, "ci99": [low, high], "gate": gate,
            "relative_ci_width": (high - low) / median,
            "definition": "Rust / IREGI paired block latency; 99% bootstrap median interval; CI width must be <=2% of median"}


def save(path, data):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def configuration_rows(cases, batches, algorithm, reference_algorithm):
    """Keep every requested kernel workload visible even if a run is interrupted."""
    return [{"id": case["id"], "n": case["n"], "rank": case["rank"],
             "mass_class": case["mass_class"], "precision": "binary64", "mode": algorithm,
             "reference_mode": reference_algorithm or algorithm, "batch_width": batch,
             "status": "pending", "correctness": None, "rust": None, "iregi": None, "ratio": None}
            for case in cases for batch in batches]


def finalize_rows(data, completed_normally):
    for row in data["rows"]:
        if row["status"] == "pending":
            row.update(status="not_run", error="run ended before this configuration started")
        elif row["status"] == "running":
            row.update(status="interrupted", error="run ended during this configuration")
    finished = completed_normally and bool(data["rows"]) and all(
        row["status"] in {"measured", "failed", "timeout", "unsupported", "correctness-failed"}
        for row in data["rows"]
    )
    data["status"] = "complete" if finished else "interrupted"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rust", type=Path, default=ROOT / "target/optimized/release/examples/kernel_benchmark")
    parser.add_argument("--reference", type=Path, default=ROOT / "target/benchmark/iregi-benchmark")
    parser.add_argument("--rust-build-manifest", type=Path,
                        default=ROOT / "target/benchmark/rust-build.json",
                        help="Build provenance matching the selected Rust executable")
    parser.add_argument("--reference-build-manifest", type=Path,
                        default=ROOT / "target/benchmark/reference-build.json",
                        help="Build provenance matching the selected reference executable")
    parser.add_argument("--output", type=Path, default=ROOT / "target/benchmark/results.json")
    parser.add_argument("--input", type=Path, help="JSON list of custom case objects, using the generated inputs.json schema")
    parser.add_argument("--cpu", type=int, default=min(os.sched_getaffinity(0)))
    parser.add_argument("--ranks", type=int, nargs="+", default=[0, 1, 2, 3])
    parser.add_argument("--mass-classes", nargs="+", choices=["massive", "massless", "complex"], default=["massive", "massless", "complex"])
    parser.add_argument("--batches", type=int, nargs="+", default=[1, 8, 32, 128])
    parser.add_argument("--algorithm", choices=MODE, default="Hybrid")
    parser.add_argument("--reference-algorithm", choices=MODE, help="Explicitly recorded independent-oracle override")
    parser.add_argument("--repeats", type=int, default=21)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--block-ms", type=float, default=30.0)
    parser.add_argument("--timeout", type=float, default=1200.0)
    parser.add_argument("--filter", default="", help="Case ID substring")
    parser.add_argument("--inputs-only", action="store_true")
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.rust = args.rust.resolve()
    args.reference = args.reference.resolve()
    if args.cpu not in os.sched_getaffinity(0):
        parser.error("requested CPU is outside the permitted affinity mask")
    if (min(args.batches) < 1 or args.repeats < 3 or args.warmup < 0
            or not math.isfinite(args.block_ms) or args.block_ms <= 0
            or not math.isfinite(args.timeout) or args.timeout <= 0):
        parser.error("positive batches and finite block duration/timeout, repeats>=3, and warmup>=0 required")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cases = json.loads(args.input.read_text()) if args.input else suite(args.ranks, args.mass_classes, args.batches)
    cases = [case for case in cases if args.filter in case["id"]]
    inputs_path = args.output.with_name(args.output.stem + "-inputs.json")
    save(inputs_path, cases)
    if args.inputs_only:
        print(inputs_path)
        return
    if not cases:
        parser.error("no benchmark cases match the requested filter")
    if not args.rust.is_file() or not args.reference.is_file():
        parser.error("missing executable; run validation/benchmark/build.py first")
    original_affinity = os.sched_getaffinity(0)
    os.sched_setaffinity(0, {args.cpu})
    data = {
        "schema_version": 1, "kind": "iregi-kernel-benchmark", "status": "running",
        "date": datetime.datetime.now(datetime.timezone.utc).isoformat(), "environment": environment(args.cpu),
        "input_path": str(inputs_path.relative_to(ROOT)), "input_sha256": digest(inputs_path),
        "binaries": {"rust": {"path": str(args.rust), "sha256": digest(args.rust)},
                     "reference": {"path": str(args.reference), "sha256": digest(args.reference)}},
        "protocol": {"repeats": args.repeats, "warmup": args.warmup, "target_block_ms": args.block_ms,
                     "paired_random_order_seed": 271828, "transport_timed": False,
                     "cache_policy": "structural plans/evaluators and allocation capacity reused; numerical results recomputed for every sample; original recurrence cache freed after every sample",
                     "outputs": "all Cartesian components through requested rank, all four separated native Laurent coefficients",
                     "kernel_scope": "public reduce_batch including result allocation/disposal; original tensor call plus mass-reference setup/status checking/cache disposal",
                     "stage_scope": "separate instrumented pass: argument evaluator, complete scalar-master calls, recurrence evaluator/stability checks; residual is validation/packing/routing",
                     "preparation_scope": "first Rust plan+workspace compile only; not a repeated timing distribution",
                     "numerator": "not applicable to tensor-array kernel; graph/numerator end-to-end benchmark reported separately"},
        "rows": configuration_rows(cases, args.batches, args.algorithm, args.reference_algorithm),
        "harness": {"path": str(Path(__file__).resolve()), "sha256": digest(Path(__file__))},
    }
    data["build_manifest_paths"] = {
        "rust": str(args.rust_build_manifest),
        "reference": str(args.reference_build_manifest),
    }
    for key, path in [("reference_build", args.reference_build_manifest),
                      ("rust_build", args.rust_build_manifest)]:
        data[key] = json.loads(path.read_text()) if path.exists() else None
    rust_build = data["rust_build"] or {}
    reference_build = data["reference_build"] or {}
    measured_source = Path(rust_build.get("source_root", ROOT))
    measured_source_hashes = source_hashes(measured_source)
    data["measured_source"] = {"path": str(measured_source), "revision": rust_build.get("source_revision"),
                               "sha256": measured_source_hashes, "is_current_workspace": measured_source == ROOT}
    data["build_provenance_checks"] = {
        "rust_binary_matches_manifest": rust_build.get("binary_sha256") == data["binaries"]["rust"]["sha256"],
        "reference_binary_matches_manifest": reference_build.get("binary_sha256") == data["binaries"]["reference"]["sha256"],
        "rust_sources_match_manifest": rust_build.get("source_sha256") == measured_source_hashes,
    }
    save(args.output, data)
    rng = random.Random(271828)
    rust = reference = None
    executed = {}
    rows = iter(data["rows"])
    completed_normally = False
    try:
        for case in cases:
            for batch in args.batches:
                row = next(rows)
                row["status"] = "running"
                print(f"{case['id']} batch {batch}", flush=True)
                try:
                    if len(case["samples"]) < batch:
                        raise ValueError("custom case has fewer independent samples than requested batch width")
                    samples = case["samples"][:batch]
                    if rust is None:
                        if "rust" not in executed:
                            executed["rust"] = freeze_executable(args.rust, data["binaries"]["rust"]["sha256"], "rust")
                        rust = Process(executed["rust"], "rust", args.output.parent, args.timeout)
                    if reference is None:
                        if "reference" not in executed:
                            executed["reference"] = freeze_executable(args.reference, data["binaries"]["reference"]["sha256"], "reference")
                        reference = Process(executed["reference"], "reference", args.output.parent, args.timeout)
                    ref_mode = args.reference_algorithm or args.algorithm
                    pilot_rust = rust.request(rust_request(case, samples, args.algorithm, args.warmup, 1))
                    pilot_ref = reference.request(fortran_request(case, samples, ref_mode, args.warmup, 1))
                    row["correctness"] = compare(pilot_rust, pilot_ref, case, samples)
                    if "total_ns" not in pilot_rust or "total_ns" not in pilot_ref:
                        row["engine_errors"] = {"rust": pilot_rust, "iregi": pilot_ref}
                        if "unsupported" in json.dumps(row["engine_errors"]).lower():
                            row["status"] = "unsupported"
                        raise ValueError("engine failed to produce timing output")
                    validate_response(pilot_rust, case, profile=False)
                    validate_response(pilot_ref, case)
                    rust_iterations = max(1, min(1000000, math.ceil(args.block_ms * 1e6 / max(1, pilot_rust["total_ns"][0]))))
                    ref_iterations = max(1, min(1000000, math.ceil(args.block_ms * 1e6 / max(1, pilot_ref["total_ns"][0]))))
                    row["iterations_per_block"] = {"rust": rust_iterations, "iregi": ref_iterations}
                    totals = {"rust": [], "iregi": []}
                    orders = []
                    for _ in range(args.repeats):
                        order = ["rust", "iregi"]
                        rng.shuffle(order)
                        orders.append(order)
                        block = {}
                        for name in order:
                            result = (rust.request(rust_request(case, samples, args.algorithm, 0, rust_iterations)) if name == "rust"
                                      else reference.request(fortran_request(case, samples, ref_mode, 0, ref_iterations)))
                            validate_response(result, case, profile=False if name == "rust" else None)
                            totals[name].append(result["total_ns"][0])
                            block[name] = result
                        checked = compare(block["rust"], block["iregi"], case, samples)
                        if checked["status"] != "passed":
                            row["correctness"] = checked
                    profiles = {name: [] for name in ["arguments", "masters", "reduction", "total"]}
                    for _ in range(args.repeats):
                        profiled = rust.request(rust_request(case, samples, args.algorithm, 0, rust_iterations, profile=True))
                        validate_response(profiled, case, profile=True)
                        checked = compare(profiled, pilot_ref, case, samples)
                        if checked["status"] != "passed":
                            row["correctness"] = checked
                        for name in profiles:
                            profiles[name].append(profiled["profile_ns"][name][0])
                    row["order"] = orders
                    row["rust"] = {"total": summarize(totals["rust"]), "preparation_ns": pilot_rust["preparation_ns"],
                                   "master_backend": pilot_rust.get("master_backend", rust_build.get("master_backend", "unrecorded")),
                                   "preparation_reused": pilot_rust["plan_reused"], "numerator": None,
                                   "profiled_components": {name: summarize(values) for name, values in profiles.items()},
                                   "execution": pilot_rust["execution"]}
                    row["iregi"] = {"total": summarize(totals["iregi"]), "preparation": None,
                                    "numerator": None, "arguments": None, "masters": None, "reduction": None}
                    row["ratio"] = ratio_summary(totals["rust"], totals["iregi"], row["correctness"])
                    row["status"] = "measured" if row["correctness"]["status"] == "passed" else "correctness-failed"
                except (OSError, RuntimeError, TimeoutError, ValueError, KeyError, TypeError, IndexError, ZeroDivisionError) as error:
                    if row["status"] != "unsupported":
                        row["status"] = "timeout" if isinstance(error, TimeoutError) else "failed"
                    row["error"] = str(error)
                    for process in (rust, reference):
                        if process:
                            process.close()
                    rust = reference = None
                save(args.output, data)
        completed_normally = True
    finally:
        finalize_rows(data, completed_normally)
        data["counts"] = {status: sum(row["status"] == status for row in data["rows"])
                          for status in sorted({row["status"] for row in data["rows"]})}
        # Save terminal row states before fallible cleanup/provenance checks.
        data["provenance_qualified"] = False
        data["executed_binaries"] = {name: {"path": str(path), "sha256": data["binaries"][name]["sha256"]}
                                     for name, path in executed.items()}
        save(args.output, data)
        for process in (rust, reference):
            if process:
                try:
                    process.close()
                except OSError as error:
                    data.setdefault("cleanup_errors", []).append(str(error))
        try:
            os.sched_setaffinity(0, original_affinity)
        except OSError as error:
            data.setdefault("cleanup_errors", []).append(str(error))
        checks = {
            "workspace_source_changed_during_run": lambda: source_hashes() != data["environment"]["source_sha256"],
            "source_changed_during_run": lambda: source_hashes(measured_source) != measured_source_hashes,
            "binaries_changed_during_run": lambda: len(executed) != 2 or any(
                digest(path) != data["binaries"][name]["sha256"] for name, path in executed.items()),
            "harness_changed_during_run": lambda: digest(Path(__file__)) != data["harness"]["sha256"],
        }
        for name, check in checks.items():
            try:
                data[name] = check()
            except (OSError, ValueError) as error:
                data[name] = True
                data.setdefault("finalization_errors", {})[name] = f"{type(error).__name__}: {error}"
        data["provenance_qualified"] = (all(data["build_provenance_checks"].values())
            and not data.get("finalization_errors") and not data.get("cleanup_errors")
            and not any(data[name] for name in ("source_changed_during_run", "binaries_changed_during_run", "harness_changed_during_run")))
        if data["source_changed_during_run"]:
            data["measurement_warning"] = "Sources changed during measurement; results describe hashed binaries and are stale for the current source tree"
        save(args.output, data)
    print(args.output)


if __name__ == "__main__":
    main()

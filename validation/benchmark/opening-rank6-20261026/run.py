#!/usr/bin/env python3
"""Build, supervise and summarize the opening examples; run from repository root.

Only the numerical child is pinned. This is an absolute-time observation suite,
not a paired speed gate. No credentials are read into persisted provenance.
"""
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import statistics
import subprocess
import time

ROOT = Path.cwd().resolve()
HERE = Path(__file__).resolve().parent
TARGET = ROOT / "target/opening-tensor-timings-20261026"


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    temporary.replace(path)


def capture(command):
    return subprocess.check_output(command, text=True).strip()


def source_hashes():
    # Explicit selected source context, not a claim to a hermetic build closure.
    paths = set(json.loads((HERE / "source-files.json").read_text())["paths"])
    paths.update(str((HERE / name).relative_to(ROOT)) for name in (
        "run.py", "make-inputs.py", "inputs.json", "source-files.json",
        "profiling-boundary-source-audit.json"))
    return {name: digest(ROOT / name) for name in sorted(paths)}


def supervise(command, log, cap_seconds):
    started = time.monotonic()
    record = {"command": command, "cap_seconds": cap_seconds,
              "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with log.open("wb") as output:
        process = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        record["owned_process_group"] = process.pid
        try:
            record["returncode"] = process.wait(timeout=cap_seconds)
            record["timed_out"] = False
        except subprocess.TimeoutExpired:
            record["timed_out"] = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=10)
            record["returncode"] = process.returncode
        finally:
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                record["owned_group_gone"] = True
            else:
                os.killpg(process.pid, signal.SIGKILL)
                record["owned_group_gone"] = False
    record["elapsed_seconds"] = time.monotonic() - started
    record["log_sha256"] = digest(log)
    return record


def build(args):
    TARGET.mkdir(parents=True, exist_ok=True)
    before = source_hashes()
    command = ["taskset", "-c", str(args.cpu), shutil.which("cargo"), "build", "--release",
               "--locked", "--offline", "-p", "iregi-rust", "--example", "opening_timing",
               "--message-format=json", "-j2"]
    receipt = {
        "schema_version": 1, "source_revision": capture(["git", "rev-parse", "HEAD"]),
        "source_hashes": before, "selected_context_not_complete_build_closure": True,
        "cargo": capture(["cargo", "--version"]), "rustc": capture(["rustc", "-Vv"]),
        "environment_overrides": {name: os.environ.get(name) for name in (
            "CARGO_TARGET_DIR", "CARGO_BUILD_BUILD_DIR", "CARGO_BUILD_JOBS", "RAYON_NUM_THREADS",
            "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "RUST_MIN_STACK")},
        "cpu": args.cpu, "machine": capture(["uname", "-a"]),
        "cpu_information": capture(["lscpu"]), "native_evaluation": False,
    }
    receipt["step"] = supervise(command, TARGET / "build.log", args.timeout)
    receipt["sources_unchanged"] = before == source_hashes()
    if receipt["step"]["returncode"] == 0 and receipt["sources_unchanged"]:
        events = []
        for line in (TARGET / "build.log").read_text().splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("reason") == "compiler-artifact" and event.get("executable") and event["target"]["name"] == "opening_timing":
                events.append(event)
        if len(events) != 1:
            raise RuntimeError("expected one matching Cargo executable artifact")
        artifact = events[0]
        frozen = TARGET / "opening_timing"
        shutil.copy2(artifact["executable"], frozen)
        receipt["binary_sha256"] = digest(frozen)
        receipt["binary_path"] = str(frozen.relative_to(ROOT))
        receipt["cargo_artifact"] = artifact
        receipt["status"] = "built_and_frozen"
    else:
        receipt["status"] = "build_failed"
    save(HERE / "build.json", receipt)
    print(json.dumps({"status": receipt["status"], "seconds": receipt["step"]["elapsed_seconds"]}), flush=True)
    return int(receipt["status"] != "built_and_frozen")


def run(args):
    suite = json.loads((HERE / "inputs.json").read_text())
    built = json.loads((HERE / "build.json").read_text())
    if source_hashes() != built["source_hashes"] or digest(ROOT / built["binary_path"]) != built["binary_sha256"]:
        raise RuntimeError("source or frozen executable changed since build")
    rows = []
    for case in suite["cases"]:
        if args.only and case["id"] not in args.only:
            continue
        folder = HERE / "cases" / case["id"]
        folder.mkdir(parents=True, exist_ok=True)
        result = folder / "result.json"
        if result.exists() or (folder / "supervision.json").exists():
            raise RuntimeError("refusing to overwrite a prior attempt: " + case["id"])
        request = dict(case["driver_request"])
        # Fixed in advance by topology: high-point warm kernels are expensive.
        # Counts are explicit; no observations are discarded for noise.
        if request["n"] >= 5:
            request.update(warmup=1, repeats=5, iterations=1, target_block_ns=None)
        save(folder / "request.json", request)
        command = ["taskset", "-c", str(args.cpu), str(ROOT / built["binary_path"]),
                   str(folder / "request.json"), str(result)]
        print(json.dumps({"starting": case["id"], "cpu": args.cpu}), flush=True)
        step = supervise(command, folder / "native.log", args.timeout)
        step.update(id=case["id"], cpu=args.cpu, binary_sha256=built["binary_sha256"],
                    binary_unchanged_after=digest(ROOT / built["binary_path"]) == built["binary_sha256"],
                    request_sha256=digest(folder / "request.json"),
                    source_hashes_unchanged=source_hashes() == built["source_hashes"],
                    environment_threads={k: os.environ.get(k) for k in (
                        "RAYON_NUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS")})
        if result.exists():
            step["result_sha256"] = digest(result)
            step["driver_status"] = json.loads(result.read_text())["status"]
        save(folder / "supervision.json", step)
        rows.append(step)
        print(json.dumps({"finished": case["id"], "returncode": step["returncode"],
                          "driver_status": step.get("driver_status"), "seconds": step["elapsed_seconds"]}), flush=True)
    return int(any(row["returncode"] != 0 for row in rows))


def stats(values):
    mean = statistics.mean(values)
    return {"mean": mean, "median": statistics.median(values), "minimum": min(values),
            "maximum": max(values), "stdev": statistics.stdev(values) if len(values) > 1 else None,
            "standard_error": statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else None}


def summarize(args):
    suite = json.loads((HERE / "inputs.json").read_text())
    rows = []
    for case in suite["cases"]:
        folder = HERE / "cases" / case["id"]
        row = {name: value for name, value in case.items() if name != "driver_request"}
        row.update({name: case["driver_request"][name] for name in (
            "n", "rank", "powers", "dimension_shift", "algorithm", "numeric_type", "working_bits", "requested_bits")})
        row.update(batch_size=1, moments=math.comb(row["rank"] + 4, 4), laurent_slots=4,
                   source_revision=json.loads((HERE / "build.json").read_text())["source_revision"],
                   result_source=str((folder / "result.json").relative_to(ROOT)))
        if not (folder / "supervision.json").exists():
            row["status"] = "unmeasured"
            rows.append(row)
            continue
        supervision = json.loads((folder / "supervision.json").read_text())
        result = json.loads((folder / "result.json").read_text()) if (folder / "result.json").exists() else {}
        row["status"] = result.get("status", "timeout_or_native_failure")
        row["timing_qualified"] = bool(result.get("timing_qualified")) and supervision["returncode"] == 0 and supervision["source_hashes_unchanged"] and supervision["owned_group_gone"]
        row["engine"] = result.get("workspace_engine")
        row["plan_engine"] = result.get("plan_engine")
        row["plan_ns"] = result.get("plan_ns")
        row["workspace_ns"] = result.get("workspace_ns")
        row["first_call_ns"] = result.get("first_call_ns")
        row["supervision_source"] = str((folder / "supervision.json").relative_to(ROOT))
        if row["timing_qualified"]:
            blocks = result["repeated_measurements"]
            fields = ["tirust_exclusive_ns", "scalar_masters_ns", "outer_total_ns"]
            block_means = {field: [statistics.mean(call[field] for call in block["calls"]) / 1000
                                   for block in blocks] for field in fields}
            row["timing"] = {field.removesuffix("_ns") + "_us": stats(values)
                             for field, values in block_means.items()}
            row["repeats"] = len(blocks)
            row["calls_per_repeat"] = len(blocks[0]["calls"])
            row["total_timed_calls"] = sum(len(block["calls"]) for block in blocks)
            row["maximum_additive_error_us"] = max(abs(
                call["outer_total_ns"] - call["tirust_exclusive_ns"] - call["scalar_masters_ns"])
                for block in blocks for call in block["calls"]) / 1000
            assert row["maximum_additive_error_us"] == 0
        rows.append(row)
    summary = {"schema_version": 1, "suite_id": suite["suite_id"],
               "measurement_date": "2026-10-26", "timing_contract": suite["timing_contract"],
               "input_family": suite["input_family"], "rows": rows,
               "statistics": "Arithmetic mean of equal-size block means; standard error across blocks is descriptive, not a controlled-host confidence guarantee. Additive same-call phases. Raw calls and medians/spread retained.",
               "selection_notice": "12ordinary+6generalized inputs fixed before evaluation; failures remain visible. Singleton absolute timings, mixed explicit precisions, profiled public facade, no reference-speed gate.",
               "measured_rows": sum(bool(row.get("timing_qualified")) for row in rows),
               "unqualified_rows": sum(not row.get("timing_qualified") for row in rows)}
    save(HERE / "summary.json", summary)
    print(json.dumps({"measured": summary["measured_rows"], "unqualified": summary["unqualified_rows"]}))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["build", "run", "summarize"])
    parser.add_argument("--cpu", type=int, default=18)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--only", nargs="*")
    arguments = parser.parse_args()
    raise SystemExit(globals()[arguments.mode](arguments))

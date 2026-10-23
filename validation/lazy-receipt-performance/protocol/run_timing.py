#!/usr/bin/env python3
"""Execute exactly once, only after ROOT's separate immutable quiet-window grant."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
HERE = OUT.parent
sys.path.insert(0, str(HERE))
from build import read, save, sha, verify
from protocol import parse_calibration, parse_measurements


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--quiet-manifest", type=Path, required=True)
    parser.add_argument("--quiet-sha256", required=True)
    args = parser.parse_args()
    assert args.cpu in os.sched_getaffinity(0)
    assert re.fullmatch(r"[0-9a-f]{64}", args.quiet_sha256)
    quiet = args.quiet_manifest.resolve()
    assert sha(quiet) == args.quiet_sha256
    os.sched_setaffinity(0, {args.cpu})
    ready_path = HERE / "timing-ready.json"
    ready = read(ready_path)
    assert ready["status"] == "source_reviewed_and_optimized_preflight_passed_awaiting_quiet_grant"
    assert ready["timing_started"] is False
    review_path = HERE / "review/protocol-review.json"
    review = read(review_path)
    assert review["status"] == "passed"
    assert review["protocol_manifest_sha256"] == sha(OUT / "manifest.json")
    manifest = read(OUT / "manifest.json")
    assert ready["protocol_manifest_sha256"] == sha(OUT / "manifest.json")
    assert ready["protocol_review_sha256"] == sha(review_path)
    assert ready["probe"] == manifest["probe"]
    assert all(ready["bindings"].get(path) == digest for path, digest in manifest["bindings"].items())
    build = read(HERE / "build-001/build.json")
    preflight = read(HERE / "preflight.json")
    assert build["status"] == preflight["status"] == "passed"
    assert build["inputs_unchanged"] and preflight["inputs_unchanged"]
    assert preflight["cases_passed"] == 14
    assert build["outputs"][ready["probe"]["path"]] == ready["probe"]["sha256"]
    assert preflight["inputs"][ready["probe"]["path"]] == ready["probe"]["sha256"]
    bindings = {**ready["bindings"], str(ready_path.relative_to(ROOT)): sha(ready_path)}
    verify(bindings)
    binary = ROOT / ready["probe"]["path"]
    data = binary.read_bytes()
    binary_hash = hashlib.sha256(data).hexdigest()
    assert binary_hash == ready["probe"]["sha256"]
    record_path = OUT / "performance-run.json"
    csv_path, log_path = OUT / "performance.csv", OUT / "performance.log"
    assert not any(path.exists() for path in [record_path, csv_path, log_path]), "never overwrite/repeat a retained timing cohort"
    fd, filename = tempfile.mkstemp(prefix="executed-", dir=OUT)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
    executed = Path(filename)
    executed.chmod(0o500)
    assert sha(executed) == binary_hash
    record = {
        "status": "running", "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "command": [str(executed), "--time"], "cpu_affinity": [args.cpu], "timeout_seconds": 600,
        "scope": "New paired eager-final-e23 versus lazy receipts with identical accepted shared current masters and unchanged opt3 numerical closure. Includes mixed flattened Dual; no native selection, N5 retry or IREGI reference performance claim.",
        "inputs": bindings, "binary_sha256": binary_hash,
        "quiet_manifest": str(quiet), "quiet_manifest_initial_sha256": args.quiet_sha256,
        "analysis_source_sha256": sha(OUT / "analyze.py"), "protocol_source_sha256": sha(OUT / "protocol.py"),
        "preregistration_sha256": sha(OUT / "preregistration.json"),
        "readiness_sha256": sha(ready_path), "source_review_sha256": sha(review_path),
        "performance_includes": "Entire repeated reduce_batch call, result construction/drop; preparation and snapshots outside each timed block. All14 cases, fixed41 pairs; no CI-driven stopping or omission.",
    }
    save(record_path, record)
    start = time.monotonic()
    child = None
    try:
        verify(bindings)
        assert sha(executed) == binary_hash
        assert sha(quiet) == args.quiet_sha256
        start = time.monotonic()
        record["process_started_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(csv_path, "w") as out, open(log_path, "w") as log:
            child = subprocess.Popen(record["command"], stdout=out, stderr=log, start_new_session=True)
            record["owned_process_group"] = child.pid
            save(record_path, record)
            try:
                record["exit_code"] = child.wait(timeout=600)
                record["timed_out"] = False
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
                record.update(exit_code=124, timed_out=True)
    except Exception as error:
        record.update(exit_code=1, timed_out=False, execution_error={"type": type(error).__name__, "repr": repr(error)})
    finally:
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
        record.update(status="finished_unverified", seconds=time.monotonic() - start, provenance_qualified=False)
        save(record_path, record)  # Persist terminal state before risky verification.
        for label, path in [("raw_csv_sha256", csv_path), ("log_sha256", log_path), ("executed_copy_final_sha256", executed), ("quiet_manifest_final_sha256", quiet)]:
            try:
                record[label] = sha(path)
            except Exception as error:
                record.setdefault("artifact_hash_errors", {})[str(path)] = {"type": type(error).__name__, "repr": repr(error)}
        save(record_path, record)
        try:
            verify(bindings)
            assert sha(executed) == binary_hash
            assert sha(quiet) == args.quiet_sha256
            record.update(executed_copy_final_sha256=sha(executed), quiet_manifest_final_sha256=sha(quiet), raw_csv_sha256=sha(csv_path), log_sha256=sha(log_path), provenance_qualified=True)
            log = log_path.read_text()
            passed = re.findall(r"^PASS (\d+) fixed-loop cases; mode=timing$", log, re.M)
            record["cases_passed"] = int(passed[0]) if len(passed) == 1 else 0
            assert record["exit_code"] == 0 and not record["timed_out"]
            assert record["cases_passed"] == 14
            calibration = parse_calibration(log)
            groups = parse_measurements(csv_path.read_text(), calibration)
            assert len(groups) == 14
            record.update(status="passed", measurement_rows=14 * 41 * 2, protocol_validated=True)
        except Exception as error:
            record.update(status="failed", validation_error={"type": type(error).__name__, "repr": repr(error)})
        save(record_path, record)
    print(json.dumps({key: record.get(key) for key in ["status", "exit_code", "seconds", "cases_passed", "provenance_qualified", "validation_error"]}), flush=True)
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())

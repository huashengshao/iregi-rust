#!/usr/bin/env python3
"""Bounded exact all14 optimized preflight; deliberately no timing option."""
import datetime
import os
import re
import signal
import subprocess
import sys
import time
from build import ROOT, HERE, read, save, sha, verify


def main():
    assert len(sys.argv) == 1, "correctness-only runner accepts no options"
    build = read(HERE / "build-001/build.json")
    assert build["status"] == "passed" and build["inputs_unchanged"]
    bindings = {**build["inputs"], **build["outputs"], str((HERE / "build-001/build.json").relative_to(ROOT)): sha(HERE / "build-001/build.json")}
    verify(bindings)
    out = HERE / "preflight.json"
    log_path = HERE / "preflight.log"
    assert not out.exists() and not log_path.exists(), "retain prior outcomes"
    command = ["taskset", "-c", "6,7", str(HERE / "build-001/probe")]
    record = {"status": "running", "command": command, "timeout_seconds": 120, "inputs": bindings, "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "scope": "Exact optimized paired correctness only. No --time option passed; elapsed time is not a benchmark."}
    save(out, record)
    start = time.monotonic()
    try:
        with open(log_path, "w") as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            record["owned_process_group"] = process.pid
            save(out, record)
            try:
                record["returncode"] = process.wait(timeout=120)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                record.update(returncode=process.returncode, timeout=True)
        record["status"] = "exited"
        save(out, record)
        assert record["returncode"] == 0 and not record.get("timeout"), "failure/timeout retained"
        log = log_path.read_text()
        pairs = re.findall(r"^PARITY_PASS ([\w-]+) rows=(\d+) ", log, re.M)
        families = {"bubble-ordinary", "triangle-ordinary", "bubble-zero-real", "bubble-zero-complex", "bubble-mixed-dual", "ggh-zero-real", "ggh-mixed-complex"}
        assert len(pairs) == 14 and set(pairs) == {(f, str(n)) for f in families for n in [1, 32]}
        assert len(re.findall(r"^SNAPSHOT ", log, re.M)) == 14
        assert "mode=correctness-only" in log and "CALIBRATION," not in log
        record.update(status="passed", pairs=pairs, cases_passed=14, calls_per_implementation_per_case=7)
    except Exception as error:
        record.update(status="failed", error=str(error))
    finally:
        record.update(seconds=time.monotonic() - start, finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        save(out, record)
        try:
            record["log_sha256"] = sha(log_path)
            verify(bindings)
            record["inputs_unchanged"] = True
        except Exception as error:
            record.update(status="failed", inputs_unchanged=False, provenance_error=str(error))
        save(out, record)
    print({key: record.get(key) for key in ["status", "cases_passed", "seconds", "error"]})
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())

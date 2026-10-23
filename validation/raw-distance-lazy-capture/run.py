#!/usr/bin/env python3
"""Run one bounded correctness group; no timing or performance mode."""
import datetime
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from build import ROOT, HERE, read, save, sha, verify


def main():
    attempt = HERE / ("build-" + sys.argv[1])
    group = sys.argv[2]
    assert group in {"receipts", "accounting", "snapshots"}
    build = read(attempt / "build.json")
    assert build["status"] == "passed" and build["inputs_unchanged"]
    bindings = {**build["inputs"], **build["outputs"], str((attempt / "build.json").relative_to(ROOT)): sha(attempt / "build.json")}
    verify(bindings)
    runs = attempt / "runs"
    runs.mkdir(exist_ok=True)
    output = runs / (group + ".json")
    log_path = runs / (group + ".log")
    assert not output.exists() and not log_path.exists(), "never overwrite a prior result"
    if group == "snapshots":
        command = ["taskset", "-c", "6,7", str(attempt / "snapshots")]
        expected = 14
    else:
        test_filter = "execution::proof_receipt_tests::" if group == "receipts" else "execution::accounting_followup_tests::"
        command = ["taskset", "-c", "6,7", str(attempt / "receipt-tests"), test_filter, "--test-threads=1", "--nocapture"]
        expected = 20 if group == "receipts" else 6
    record = {"status": "running", "group": group, "expected_passed": expected, "command": command, "timeout_seconds": 120, "inputs": bindings, "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "scope": "Correctness-only licensed run. No elapsed time is a benchmark."}
    save(output, record)
    started = time.monotonic()
    try:
        with open(log_path, "w") as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
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
        save(output, record)
        text = log_path.read_text()
        assert record["returncode"] == 0 and not record.get("timeout"), "nonzero exit/timeout retained"
        if group == "snapshots":
            pairs = re.findall(r"^PARITY_PASS ([\w-]+) rows=(\d+) ", text, re.M)
            families = {"bubble-ordinary", "triangle-ordinary", "bubble-zero-real", "bubble-zero-complex", "bubble-mixed-dual", "ggh-zero-real", "ggh-mixed-complex"}
            assert len(pairs) == 14 and set(pairs) == {(f, str(n)) for f in families for n in [1, 32]}
            assert len(re.findall(r"^SNAPSHOT ", text, re.M)) == 14
            record.update(pairs=pairs, tests_passed=14, tests_failed=0)
        else:
            result = re.search(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;", text)
            assert result and tuple(map(int, result.groups())) == (expected, 0, 0), "unexpected test membership/result"
            record.update(tests_passed=expected, tests_failed=0)
        record["status"] = "passed"
    except Exception as error:
        record.update(status="failed", error=str(error))
    finally:
        record.update(seconds=time.monotonic() - started, finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        save(output, record)
        try:
            record["log_sha256"] = sha(log_path)
            verify(bindings)
            record["inputs_unchanged"] = True
        except Exception as error:
            record.update(status="failed", inputs_unchanged=False, provenance_error=str(error))
        save(output, record)
    print({key: record.get(key) for key in ["status", "group", "tests_passed", "seconds", "error"]})
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())

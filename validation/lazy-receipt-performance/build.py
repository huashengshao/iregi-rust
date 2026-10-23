#!/usr/bin/env python3
"""Build only the frozen optimized paired cores/probe; no numerical runtime."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path.cwd()
HERE = ROOT / "target/raw-distance-lazy-capture-optimized"


def sha(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + "\n")


def verify(bindings):
    for path, digest in bindings.items():
        assert sha(ROOT / path) == digest, f"changed bound input: {path}"


def main():
    manifest = read(HERE / "source-manifest.json")
    review = read(HERE / "review/source-review.json")
    assert review["status"] == "passed"
    assert review["source_manifest_sha256"] == sha(HERE / "source-manifest.json")
    bindings = dict(manifest["bindings"])
    for path in [HERE / "source-manifest.json", HERE / "review/source-review.json"]:
        bindings[str(path.relative_to(ROOT))] = sha(path)
    verify(bindings)
    assert subprocess.check_output([manifest["compiler_path"], "-vV"], text=True).strip() == manifest["compiler_version"]
    attempt = HERE / "build-001"
    attempt.mkdir(exist_ok=False)
    record = {"status": "building", "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "inputs": bindings, "steps": [], "scope": "Matched current shared masters, unchanged opt3 numerical closure; eager final e23 vs private lazy receipt capture. No numeric runtime/timing in this build."}
    save(attempt / "build.json", record)
    started = time.monotonic()
    try:
        outputs = {}
        for spec in manifest["build_steps"]:
            verify({**bindings, **outputs})
            step = dict(spec)
            record["steps"].append(step)
            save(attempt / "build.json", record)
            environment = dict(os.environ, **step["environment"])
            log_path = attempt / (step["label"] + ".log")
            step_start = time.monotonic()
            print("START " + step["label"], flush=True)
            with open(log_path, "w") as log:
                process = subprocess.Popen(step["command"], env=environment, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                step["owned_process_group"] = process.pid
                save(attempt / "build.json", record)
                try:
                    step["returncode"] = process.wait(timeout=step["timeout_seconds"])
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    step.update(returncode=process.returncode, timeout=True)
            step["seconds"] = time.monotonic() - step_start
            step["status"] = "exited"
            save(attempt / "build.json", record)
            step["log_sha256"] = sha(log_path)
            verify({**bindings, **outputs})
            step["inputs_unchanged"] = True
            assert step["returncode"] == 0 and not step.get("timeout"), f"{step['label']} failed; log retained"
            outputs[step["output"]] = sha(ROOT / step["output"])
            step["status"] = "passed"
            record["outputs"] = dict(outputs)
            save(attempt / "build.json", record)
            print(f"PASS {step['label']} {step['seconds']:.3f}s", flush=True)
        record["status"] = "passed"
    except Exception as error:
        record.update(status="failed", error=str(error))
    finally:
        record.update(seconds=time.monotonic() - started, finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        save(attempt / "build.json", record)
        try:
            verify({**bindings, **record.get("outputs", {})})
            record["inputs_unchanged"] = True
        except Exception as error:
            record.update(status="failed", inputs_unchanged=False, provenance_error=str(error))
        save(attempt / "build.json", record)
    print(json.dumps({key: record.get(key) for key in ["status", "seconds", "error"]}), flush=True)
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())

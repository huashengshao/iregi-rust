"""Stdlib capture supervisor; invoke only after ROOT grants a runtime lease."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import traceback


HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("family", choices=("C0", "D0"))
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    if not args.attempt.isalnum():
        raise ValueError("Attempt name must be alphanumeric")
    config = json.loads((HERE / "inputs.json").read_text())
    manifest = json.loads((HERE / "manifest.json").read_text())
    directory = HERE / args.attempt / args.family
    directory.mkdir(parents=True, exist_ok=False)
    output = directory / "results.json"
    command = ["taskset", "-c", "0", str(REPO / manifest["venv"] / "bin/python"),
               "-I", str(HERE / "probe.py"), args.family, "--output", str(output)]
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    for key in ("IREGI_DUAL_CASE_FILTER", "IREGI_DUAL_SKIP_CASE"):
        environment.pop(key, None)
    environment.update(PYTHONNOUSERSITE="1", RAYON_NUM_THREADS="1", OMP_NUM_THREADS="1",
                       OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", RUST_MIN_STACK="67108864")
    bound = config["families"][args.family]["wall_bound_seconds"]
    record = {"command": command, "cwd": str(REPO), "wall_bound_seconds": bound,
              "kill_grace_seconds": 10, "timeout": False, "passed": False,
              "status": "running", "numerical_evidence": str(output.relative_to(REPO)),
              "manifest_sha256": hashlib.sha256((HERE / "manifest.json").read_bytes()).hexdigest(),
              "environment": {key: environment.get(key) for key in (
                  "PYTHONPATH", "PYTHONNOUSERSITE", "RAYON_NUM_THREADS", "OMP_NUM_THREADS",
                  "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "RUST_MIN_STACK",
                  "IREGI_DUAL_CASE_FILTER", "IREGI_DUAL_SKIP_CASE")}}
    summary = directory / "capture.json"
    summary.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"phase": "start", "family": args.family, "bound_seconds": bound}), flush=True)
    start = time.monotonic_ns()
    process = None

    def send_signal(signum):
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signum)
            except ProcessLookupError:
                pass  # Child exited between poll and signal; wait still reaps it.

    try:
        with (directory / "stdout.log").open("w") as stdout, (directory / "stderr.log").open("w") as stderr:
            process = subprocess.Popen(command, cwd=REPO, env=environment, stdout=stdout,
                                       stderr=stderr, start_new_session=True)
            try:
                record["returncode"] = process.wait(timeout=bound)
            except subprocess.TimeoutExpired:
                record["timeout"] = True
                send_signal(signal.SIGTERM)
                try:
                    record["returncode"] = process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    send_signal(signal.SIGKILL)
                    record["returncode"] = process.wait()
    except Exception as error:
        record["capture_error"] = {"phase": "process", "type": type(error).__name__,
                                   "message": str(error), "traceback": traceback.format_exc()}
        send_signal(signal.SIGKILL)
        if process is not None:
            record["returncode"] = process.wait()
    record["elapsed_ns"] = time.monotonic_ns() - start
    if output.exists():
        try:
            evidence = json.loads(output.read_text())
            record["probe_status"] = evidence.get("status")
            record["probe_complete"] = evidence.get("complete", False)
            record["counts"] = evidence.get("counts")
            record["passed"] = (record.get("returncode") == 0 and not record["timeout"]
                                and "capture_error" not in record
                                and evidence.get("complete") is True and evidence.get("passed") is True)
            record["last_event"] = (evidence.get("events") or [None])[-1]
        except Exception as error:
            record["passed"] = False
            record["capture_error"] = {"phase": "read_evidence", "type": type(error).__name__,
                                       "message": str(error), "traceback": traceback.format_exc()}
    record["status"] = ("capture_failed" if "capture_error" in record else
                        "passed" if record["passed"] else "timeout" if record["timeout"] else "failed")
    record["evidence_sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (output, directory / "stdout.log", directory / "stderr.log") if path.exists()
    }
    summary.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record), flush=True)
    return 0 if record["status"] == "passed" and record["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

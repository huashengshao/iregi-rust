"""Build only the public test target without debug data, then run its contracts.

Dependency profiles remain unchanged so completed current-workspace libraries
are reused. The test-target flags limit compiler scratch on the shared disk.
This is correctness validation; no build or runtime figure is a benchmark.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import signal
import subprocess
import time

ROOT = Path.cwd()
parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
OUT = args.output.resolve()
assert OUT.is_relative_to(ROOT)
OUT.mkdir(parents=True, exist_ok=False)
REPORT = OUT / "qualification.json"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


paths = subprocess.check_output(
    ["git", "ls-files", "-co", "--exclude-standard", "--", "crates", "dependencies",
     "Cargo.toml", "Cargo.lock"], text=True).splitlines()
sources = {path: sha(ROOT / path) for path in sorted(set(paths))
           if (ROOT / path).is_file() and Path(path).suffix in (".rs", ".toml", ".lock")}
environment = dict(os.environ, RAYON_NUM_THREADS="1", OMP_NUM_THREADS="1",
                   CARGO_BUILD_JOBS="2", CARGO_INCREMENTAL="0")
build = ["taskset", "-c", "22,23", "cargo", "rustc", "--locked", "--offline",
         "--message-format=json", "-p", "iregi-masters", "--test", "certified",
         "--", "-C", "debuginfo=0", "-C", "strip=debuginfo"]
record = {"status": "running", "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "parent_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
          "source_sha256": sources, "runner_sha256": sha(Path(__file__)),
          "environment_overrides": {key: environment[key] for key in
                                    ("RAYON_NUM_THREADS", "OMP_NUM_THREADS", "CARGO_BUILD_JOBS", "CARGO_INCREMENTAL")},
          "license_environment_present": bool(environment.get("SYMBOLICA_LICENSE")),
          "scope": "Actual production public API; same dependency profiles; test-target debug data disabled. Correctness only.",
          "phase_timeout_seconds": 600, "phases": []}


def save():
    temporary = REPORT.with_suffix(".tmp")
    temporary.write_text(json.dumps(record, indent=2) + "\n")
    temporary.replace(REPORT)


def run_phase(label, command):
    phase = {"label": label, "command": command, "status": "running"}
    record["phases"].append(phase)
    save()
    started = time.monotonic()
    log_path = OUT / (label + ".log")
    with log_path.open("w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                   env=environment, start_new_session=True)
        try:
            code = process.wait(timeout=600)
            status = "passed" if code == 0 else "failed"
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            code = process.wait()
            status = "timeout"
    phase.update(status=status, exit_code=code, elapsed_seconds=time.monotonic() - started,
                 log_sha256=sha(log_path))
    # Keep the actual process exit visible even if the shared disk fills again.
    print(json.dumps(phase), flush=True)
    save()
    return code == 0


save()
try:
    passed = run_phase("build", build)
    if passed:
        executables = []
        for line in (OUT / "build.log").read_text().splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("reason") == "compiler-artifact" and event.get("executable"):
                executables.append(Path(event["executable"]))
        assert len(executables) == 1, "expected exactly one public test executable"
        binary = executables[0]
        record["executable"] = {"path": str(binary.relative_to(ROOT)), "sha256": sha(binary)}
        passed = run_phase("tests", ["taskset", "-c", "22,23", str(binary), "--test-threads=1"])
        assert sha(binary) == record["executable"]["sha256"]
    changed = [path for path, digest in sources.items()
               if not (ROOT / path).is_file() or sha(ROOT / path) != digest]
    record.update(status="passed" if passed and not changed else "failed", changed_sources=changed,
                  finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
except Exception as error:
    record.update(status="supervisor-error", error=f"{type(error).__name__}: {error}")
print(json.dumps({key: record[key] for key in ("status", "phases")}), flush=True)
save()
raise SystemExit(0 if record["status"] == "passed" else 1)

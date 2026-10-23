"""Run the integrated certified-master contracts, retaining the bounded result."""
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
parser.add_argument("--output", type=Path, required=True,
                    help="A fresh evidence directory; previous attempts are retained")
args = parser.parse_args()
OUT = args.output.resolve()
assert OUT.is_relative_to(ROOT), "evidence must remain inside the project"
OUT.mkdir(parents=True, exist_ok=False)
REPORT = OUT / "public-tests.json"
LOG = OUT / "public-tests.log"
assert not REPORT.exists(), "retain the original test attempt"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


paths = subprocess.check_output(
    ["git", "ls-files", "-co", "--exclude-standard", "--", "crates", "dependencies",
     "Cargo.toml", "Cargo.lock"], text=True
).splitlines()
sources = {
    path: sha(ROOT / path) for path in sorted(set(paths))
    if (ROOT / path).is_file() and Path(path).suffix in (".rs", ".toml", ".lock")
}
command = ["taskset", "-c", "22,23", "cargo", "test", "--locked", "--offline",
           "--message-format=json", "-p", "iregi-masters", "--test", "certified",
           "--", "--test-threads=1"]
environment = dict(os.environ, RAYON_NUM_THREADS="1", OMP_NUM_THREADS="1",
                   CARGO_BUILD_JOBS="2", CARGO_INCREMENTAL="0")
record = {
    "status": "running",
    "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "parent_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    "command": command,
    "timeout_seconds": 1200,
    "source_sha256": sources,
    "runner_sha256": sha(Path(__file__)),
    "license_environment_present": bool(environment.get("SYMBOLICA_LICENSE")),
    "environment_overrides": {key: environment[key] for key in
                              ("RAYON_NUM_THREADS", "OMP_NUM_THREADS", "CARGO_BUILD_JOBS", "CARGO_INCREMENTAL")},
    "scope": "Actual production public API tests; build and test elapsed time is not a benchmark.",
}


def save():
    REPORT.write_text(json.dumps(record, indent=2) + "\n")


save()
start = time.monotonic()
with LOG.open("w") as log:
    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                               env=environment, start_new_session=True)
    try:
        code = process.wait(timeout=1200)
        record.update(status="passed" if code == 0 else "failed", exit_code=code)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
        record.update(status="timeout", exit_code=process.returncode)
record["elapsed_seconds"] = time.monotonic() - start
record["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
record["log_sha256"] = sha(LOG)
record["changed_sources"] = [path for path, digest in sources.items()
                             if not (ROOT / path).is_file() or sha(ROOT / path) != digest]
artifacts = []
for line in LOG.read_text().splitlines():
    try:
        item = json.loads(line)
    except json.JSONDecodeError:
        continue
    if item.get("reason") == "compiler-artifact" and item.get("executable"):
        binary = Path(item["executable"])
        artifacts.append({"path": str(binary.relative_to(ROOT)), "sha256": sha(binary)})
record["executables"] = artifacts
if record["changed_sources"]:
    record["original_status"] = record["status"]
    record["status"] = "source-changed"
save()
print(json.dumps({key: record[key] for key in
                 ("status", "exit_code", "elapsed_seconds", "changed_sources", "executables")}, indent=2))
raise SystemExit(0 if record["status"] == "passed" else 1)

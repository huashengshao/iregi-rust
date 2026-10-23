"""Check the production reducer against the newly exported master interface."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import signal
import subprocess
import time

ROOT = Path.cwd()
OUT = ROOT / "validation/near-vacuum-production/core-check"
OUT.mkdir(exist_ok=False)
parent = ROOT / "validation/near-vacuum-production/attempt004/qualification.json"
qualification = json.loads(parent.read_text())
assert qualification["status"] == "passed" and qualification["changed_sources"] == []


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def changed():
    return [path for path, digest in qualification["source_sha256"].items()
            if not (ROOT / path).is_file() or sha(ROOT / path) != digest]


assert changed() == []
command = ["taskset", "-c", "22,23", "cargo", "check", "--locked", "--offline",
           "--message-format=json", "-p", "iregi-rust", "--lib"]
environment = dict(os.environ, CARGO_INCREMENTAL="0", CARGO_BUILD_JOBS="2")
record = {"status": "running", "command": command, "timeout_seconds": 300,
          "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "public_test_qualification_sha256": sha(parent), "runner_sha256": sha(Path(__file__))}
path = OUT / "qualification.json"
path.write_text(json.dumps(record, indent=2) + "\n")
start = time.monotonic()
with (OUT / "check.log").open("w") as log:
    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                               env=environment, start_new_session=True)
    try:
        code = process.wait(timeout=300)
        status = "passed" if code == 0 else "failed"
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        code = process.wait()
        status = "timeout"
record.update(status=status, exit_code=code, elapsed_seconds=time.monotonic() - start,
              changed_sources=changed(), log_sha256=sha(OUT / "check.log"))
if record["changed_sources"]:
    record.update(original_status=status, status="source-changed")
print(json.dumps(record), flush=True)
temporary = path.with_suffix(".tmp")
temporary.write_text(json.dumps(record, indent=2) + "\n")
temporary.replace(path)
raise SystemExit(0 if record["status"] == "passed" else 1)

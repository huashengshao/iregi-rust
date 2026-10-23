"""Run one explicitly leased, bounded matched-preparation check."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time


parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("variant", choices=("alias", "vector"))
parser.add_argument("filter")
parser.add_argument("--kind", choices=("core", "gamma"), default="core")
parser.add_argument("--topology", type=int, choices=(6, 7))
parser.add_argument("--limit", type=int, default=90)
parser.add_argument("--exact", action="store_true")
args = parser.parse_args()
if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.name) or not 1 <= args.limit <= 600:
    parser.error("safe case name and a time limit between 1 and 600 seconds required")

root = Path(__file__).resolve().parent
output = root / "runs"
output.mkdir(exist_ok=True)
binary = root / f"{args.variant}{'-gamma' if args.kind == 'gamma' else ''}-tests"
command = [str(binary), args.filter, "--nocapture", "--test-threads=1"]
if args.exact:
    command.append("--exact")
env = os.environ.copy()
env["IREGI_PREPARATION_PROFILE"] = "1"
env["IREGI_PV_PREPARATION_PROFILE"] = "1"
env.pop("IREGI_CERTIFIED_PROFILE_N", None)
if args.topology is not None:
    env["IREGI_CERTIFIED_PROFILE_N"] = str(args.topology)
log_path = output / f"{args.name}.log"
record_path = output / f"{args.name}.json"
record = {
    "status": "running",
    "started_utc": datetime.now(timezone.utc).isoformat(),
    "variant": args.variant,
    "kind": args.kind,
    "command": command,
    "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    "timeout_seconds": args.limit,
    "topology": args.topology,
    "log": str(log_path),
    "scope": "Bounded diagnostic/correctness run; not a timing qualification.",
}
record_path.write_text(json.dumps(record, indent=2) + "\n")
started = time.monotonic()
with log_path.open("w") as log:
    try:
        code = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                              env=env, timeout=args.limit).returncode
    except subprocess.TimeoutExpired:
        code = 124
record["elapsed_seconds"] = time.monotonic() - started
content = log_path.read_text()
passed = re.search(r"test result: ok\. (\d+) passed;", content)
record["code"] = code
record["passed_tests"] = int(passed.group(1)) if passed else 0
record["status"] = ("passed" if code == 0 and record["passed_tests"] > 0 else
                    "timeout" if code == 124 else "failed")
record["log_sha256"] = hashlib.sha256(content.encode()).hexdigest()
record_path.write_text(json.dumps(record, indent=2) + "\n")
print(content[-18000:])
print(json.dumps(record, indent=2))
raise SystemExit(0 if record["status"] == "passed" else code or 1)

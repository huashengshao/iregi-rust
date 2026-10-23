"""Execute only after the root coordinator grants a quiet timing window on the explicitly selected CPU."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import signal
import subprocess
import tempfile
import time

ROOT = Path.cwd()
OUT = ROOT / "target/raw-distance-final-performance/protocol"
CLOSURE = ROOT / "target/benchmark/dependency-closures/6b24c03-complete-kinds"
sha = lambda path: hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument("--cpu", type=int, required=True)
parser.add_argument("--quiet-manifest", type=Path, required=True)
args = parser.parse_args()
assert args.cpu in os.sched_getaffinity(0), "selected CPU is unavailable"
os.sched_setaffinity(0, {args.cpu})
build = json.loads((OUT / "build.json").read_text())
preflight = json.loads((OUT / "preflight.json").read_text())
assert build["exit_code"] == 0 and preflight["status"] == "passed"
assert preflight["build_manifest_sha256"] == sha(OUT / "build.json")
assert build["source_unchanged"] and build["externs_unchanged"]
assert build["dependency_closure_manifest_sha256"] == sha(CLOSURE / "manifest.json")
assert preflight["binary_sha256"] == build["binary_sha256"]
manifest = json.loads((CLOSURE / "manifest.json").read_text())
records = manifest["files"] + manifest["native_files"]
# Bind every protocol source before execution and verify it again afterward.
protocol_paths = [OUT / name for name in ["probe.rs", "build.py", "preflight.py", "run_timing.py", "analyze.py", "protocol.py", "preregistration.json", "../lib_build.py", "../source-manifest.json", "../source-review.json"]]
protocol_hashes = {str(path.relative_to(ROOT)): sha(path) for path in protocol_paths}
quiet_manifest = args.quiet_manifest.resolve()
quiet_hash = sha(quiet_manifest)



def verify():
    assert build["cohort_bindings_unchanged"]
    for path, digest in build["cohort_bindings"].items():
        assert sha(ROOT / path) == digest, path
    for path, digest in protocol_hashes.items():
        assert sha(ROOT / path) == digest, path
    assert sha(CLOSURE / "manifest.json") == build["dependency_closure_manifest_sha256"]
    assert sha(OUT / "build.json") == preflight["build_manifest_sha256"]
    assert sha(OUT / "probe.rs") == build["source_sha256"]
    for variant in ["baseline", "candidate"]:
        library = json.loads((OUT.parent / f"{variant}-lib-build.json").read_text())
        assert library["closure_manifest_sha256"] == sha(CLOSURE / "manifest.json")
        assert sha(OUT.parent / f"libreceipt_final_{variant}.rlib") == library["binary_sha256"]
    for path, digest in build["extern_sha256"].items():
        assert sha(ROOT / path) == digest, path
    for record in records:
        path = Path(record["retained"])
        assert path.stat().st_size == record["bytes"]
        assert sha(path) == record["sha256"], str(path)


verify()
data = (OUT / "probe").read_bytes()
assert hashlib.sha256(data).hexdigest() == build["binary_sha256"]
fd, name = tempfile.mkstemp(prefix="executed-", dir=OUT)
with os.fdopen(fd, "wb") as stream:
    stream.write(data)
frozen = Path(name)
frozen.chmod(0o500)
assert sha(frozen) == build["binary_sha256"]
record_path = OUT / "performance-run.json"
assert not record_path.exists(), "retain every timing attempt separately"
record = {
    "status": "running",
    "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "command": [str(frozen), "--time"],
    "cpu_affinity": [args.cpu],
    "timeout_seconds": 600,
    "scope": "Paired warm numeric reduction: current21622+collector versus final reviewed automatic/accounting/checked receipts; preparation excluded; no IREGI reference performance claim",
    "quiet_window": "Requires explicit root-coordinator grant; all project heavy work held",
    "quiet_manifest": str(quiet_manifest),
    "quiet_manifest_initial_sha256": quiet_hash,
    "protocol_sources_sha256": protocol_hashes,
    "binary_sha256": build["binary_sha256"],
    "build_manifest_sha256": sha(OUT / "build.json"),
    "preflight_manifest_sha256": sha(OUT / "preflight.json"),
    "source_sha256": build["source_sha256"],
    "closure_manifest_sha256": sha(CLOSURE / "manifest.json"),
    "closure_files_verified_before": len(records),
    "analysis_source_sha256": sha(OUT / "analyze.py"),
    "protocol_source_sha256": sha(OUT / "protocol.py"),
    "preregistration_sha256": sha(OUT / "preregistration.json"),
}
record_path.write_text(json.dumps(record, indent=2) + "\n")
start = time.monotonic()
code = 1
child = None
try:
    with (OUT / "performance.csv").open("w") as out, (OUT / "performance.log").open("w") as err:
        child = subprocess.Popen(record["command"], cwd=ROOT, stdout=out, stderr=err, start_new_session=True)
        try:
            code = child.wait(timeout=600)
            record["timed_out"] = False
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
            code = 124
            record["timed_out"] = True
finally:
    if child is not None and child.poll() is None:
        os.killpg(child.pid, signal.SIGKILL)
        child.wait()
    record.update(exit_code=code, seconds=time.monotonic() - start, status="finished_unverified", provenance_qualified=False)
    record_path.write_text(json.dumps(record, indent=2) + "\n")
    try:
        verify()
        assert sha(frozen) == build["binary_sha256"]
        log = (OUT / "performance.log").read_text()
        passed = re.findall(r"PASS (\d+) fixed-loop cases; mode=timing", log)
        record.update(
            closure_files_verified_after=len(records),
            executed_copy_final_sha256=sha(frozen),
            raw_csv_sha256=sha(OUT / "performance.csv"),
            log_sha256=sha(OUT / "performance.log"),
            provenance_qualified=True,
            cases_passed=int(passed[0]) if len(passed) == 1 else 0,
        )
        record["status"] = "passed" if code == 0 and record["cases_passed"] == 14 else "failed"
    except (OSError, AssertionError) as error:
        record.update(status="failed", provenance_error=str(error))
    record_path.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
raise SystemExit(0 if record["status"] == "passed" else 1)

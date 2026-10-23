"""Compile one frozen final-cohort core archive; no numeric evaluation."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import time

ROOT = Path.cwd()
OUT = ROOT / "target/raw-distance-final-performance"
CLOSURE = ROOT / "target/benchmark/dependency-closures/6b24c03-complete-kinds"
sha = lambda path: hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument("variant", choices=("baseline", "candidate"))
args = parser.parse_args()
os.sched_setaffinity(0, {6, 7})
snapshot_path = OUT / "source-manifest.json"
snapshot = json.loads(snapshot_path.read_text())
review = json.loads((OUT / "source-review.json").read_text())
assert review["status"] == "source_review_passed"
assert review["source_manifest_sha256"] == sha(snapshot_path)
for path, digest in review["protocol_sources_sha256"].items():
    assert sha(OUT / path) == digest, path
closure_path = CLOSURE / "manifest.json"
closure = json.loads(closure_path.read_text())
records = closure["files"] + closure["native_files"]
events = json.loads((CLOSURE / "cargo-library-events.json").read_text())
selected, externs = {}, {}
for name in ("symbolica", "iregi_masters", "serde", "serde_json", "thiserror"):
    choices = [event for event in events if event["target"]["name"] == name
               and event["profile"]["opt_level"] == "3" and not event["profile"]["test"]]
    assert len(choices) == 1, (name, len(choices))
    selected[name] = choices[0]
    paths = [CLOSURE / "deps" / Path(value).name for value in choices[0]["filenames"] if value.endswith(".rlib")]
    assert len(paths) == 1
    externs[name] = paths[0]

source_root = OUT / args.variant
source_hashes = snapshot["compiled_source_hashes"][args.variant]
source = source_root / "crates/iregi-rust/src/lib.rs"
crate = "receipt_final_" + args.variant
binary = OUT / ("lib" + crate + ".rlib")
command = ["rustc", "--crate-name", crate, "--edition=2024", "--crate-type", "rlib",
           "-C", "opt-level=3", "-C", "codegen-units=16", "-C", "embed-bitcode=yes",
           str(source), "-L", f"dependency={CLOSURE}/deps"]
for directory in sorted({str(Path(record["retained"]).parent) for record in closure["native_files"]
                         if Path(record["retained"]).suffix in {".a", ".so"}}):
    command += ["-L", f"native={directory}"]
for name, path in externs.items():
    command += ["--extern", f"{name}={path}"]
command += ["-o", str(binary)]
bindings = {str(path.relative_to(ROOT)): sha(path) for path in
            [snapshot_path, OUT / "source-review.json", Path(__file__).resolve(), closure_path,
             CLOSURE / "workspace-completion.json", CLOSURE / "cargo-library-events.json"]}


def verify():
    for path, digest in bindings.items():
        assert sha(ROOT / path) == digest, path
    for path, digest in source_hashes.items():
        assert sha(source_root / path) == digest, path
    for record in records:
        path = Path(record["retained"])
        assert path.stat().st_size == record["bytes"] and sha(path) == record["sha256"], str(path)


verify()
record_path = OUT / (args.variant + "-lib-build.json")
assert not record_path.exists(), "preserve every build attempt separately"
record = {
    "status": "compiling", "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "command": command, "cpu_affinity": [6, 7], "selected_library_events": selected,
    "source_manifest_sha256": sha(snapshot_path), "source_hashes": source_hashes,
    "source_root": str(source_root.relative_to(ROOT)), "source_bindings": bindings,
    "closure_manifest_sha256": sha(closure_path), "closure_files_verified_before": len(records),
    "extern_sha256": {str(path.relative_to(ROOT)): sha(path) for path in externs.values()},
    "scope": "Final implementation cohort, generic core archive; no numeric runtime or performance claim",
}
record_path.write_text(json.dumps(record, indent=2) + "\n")
started = time.monotonic()
code = 1
try:
    with (OUT / (args.variant + "-lib-build.log")).open("w") as log:
        completed = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                   env=dict(os.environ, CARGO_MANIFEST_DIR=str(source.parent.parent),
                                            CARGO_CRATE_NAME=crate, CARGO_PKG_NAME="iregi-rust",
                                            CARGO_PKG_VERSION="0.1.0"))
        code = completed.returncode
finally:
    record.update(status="finished_unverified", exit_code=code, seconds=time.monotonic() - started,
                  provenance_qualified=False)
    record_path.write_text(json.dumps(record, indent=2) + "\n")
    try:
        verify()
        record.update(closure_files_verified_after=len(records), sources_unchanged=True,
                      externs_unchanged=True, provenance_qualified=True)
        if code == 0:
            record.update(status="compiled_not_run", binary_sha256=sha(binary))
        else:
            record["status"] = "compile_failed"
    except (OSError, AssertionError) as error:
        record.update(status="provenance_failed", provenance_error=str(error))
    record_path.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({key: record[key] for key in ("status", "exit_code", "seconds", "provenance_qualified")}))
raise SystemExit(0 if code == 0 and record["provenance_qualified"] else 1)

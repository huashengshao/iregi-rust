#!/usr/bin/env python3
"""Freeze private source and reconstruct the narrow test-only module mapping."""
import difflib
import hashlib
import json
from pathlib import Path
import re

ROOT = Path.cwd()
HERE = ROOT / "target/raw-distance-lazy-capture-candidate"


def sha(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


inputs = read(HERE / "input-manifest.json")
source = ROOT / "target/raw-distance-final-performance/source-manifest.json"
patch = ROOT / "validation/automatic-planar/final/adoption.patch"
assert sha(source) == inputs["input_source_manifest_sha256"]
assert sha(patch) == inputs["input_final_patch_sha256"]
baseline = HERE / "baseline"
candidate = HERE / "candidate"
test_source = HERE / "test-source"
baseline_hashes = {str(p.relative_to(baseline)): sha(p) for p in sorted(baseline.rglob("*")) if p.is_file()}
assert baseline_hashes == inputs["input_compiled_source_hashes"]
candidate_hashes = {str(p.relative_to(candidate)): sha(p) for p in sorted(candidate.rglob("*")) if p.is_file()}
changed = sorted(p for p in set(baseline_hashes) | set(candidate_hashes) if baseline_hashes.get(p) != candidate_hashes.get(p))
assert changed == sorted("crates/iregi-rust/src/" + p for p in ["execution.rs", "execution/proof_receipts.rs", "execution/proof_receipt_tests.rs", "execution/lazy_capture_tests.rs"])
diff = []
for relative in changed:
    old = (baseline / relative).read_text().splitlines(keepends=True) if (baseline / relative).exists() else []
    new = (candidate / relative).read_text().splitlines(keepends=True)
    diff.extend(difflib.unified_diff(old, new, fromfile="baseline/" + relative, tofile="candidate/" + relative))
(HERE / "candidate.patch").write_text("".join(diff))
harness = read(HERE / "test-harness-mapping.json")
disabled = []
for path in sorted(candidate.rglob("*")):
    if not path.is_file():
        continue
    relative = path.relative_to(candidate)
    target = test_source / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".rs":
        text, count = re.subn(r"#\[cfg\(test\)\](\s+mod\s+)", r"#[cfg(any())]\1", path.read_text())
        if count:
            disabled.append({"path": str(relative), "disabled_test_modules": count})
        if str(relative) == "crates/iregi-rust/src/execution.rs":
            text += harness["appended_execution_harness"]
        target.write_text(text)
    else:
        target.write_bytes(path.read_bytes())
assert disabled == harness["disabled_modules"]
assert set(p.relative_to(test_source) for p in test_source.rglob("*") if p.is_file()) == set(p.relative_to(candidate) for p in candidate.rglob("*") if p.is_file())
bindings = {}
for tree in [baseline, candidate, test_source]:
    for path in sorted(tree.rglob("*")):
        if path.is_file():
            bindings[str(path.relative_to(ROOT))] = sha(path)
for relative in ["input-manifest.json", "test-harness-mapping.json", "candidate.patch", "snapshots.rs", "build.py", "run.py", "freeze.py"]:
    path = HERE / relative
    bindings[str(path.relative_to(ROOT))] = sha(path)
for path in [source, patch, ROOT / "target/e6-direct-n2/preparation.json", ROOT / "target/core-fused-cse-census/supplemental-deps.json", ROOT / "target/core-fused-cse-census/thiserror-metadata.txt", ROOT / "target/core-fused-cse-census/thiserror-cargo-fingerprint.json"]:
    bindings[str(path.relative_to(ROOT))] = sha(path)
closure = read(ROOT / "target/e6-direct-n2/preparation.json")
supplemental = read(ROOT / "target/core-fused-cse-census/supplemental-deps.json")
for entry in closure["files"] + supplemental["files"]:
    bindings[entry["frozen"]] = entry["sha256"]
event = next(e for e in supplemental["completed_metadata_and_proc_macro_events"] if e["target"]["name"] == "thiserror")
crate = Path(event["manifest_path"]).parent
for relative, digest in supplemental["cached_crate_source_hashes"].items():
    bindings[str((crate / relative).relative_to(ROOT))] = digest
for relative, digest in bindings.items():
    assert sha(ROOT / relative) == digest, relative
save(HERE / "source-manifest.json", {
    "scope": "Private lazy outgoing receipt capture only, final qualified e23 source as eager baseline. Four changed source files including eight new test cases and test-only observation. No production changes. No timing authorized.",
    "input_final_patch_sha256": inputs["input_final_patch_sha256"],
    "baseline_files": len(baseline_hashes), "candidate_files": len(candidate_hashes),
    "changed_files": changed, "bindings": bindings,
    "test_counts": {"original_receipts": 12, "new_lazy_capture": 8, "accounting": 6, "paired_snapshots": 14},
    "expected_build": "Two opt0 generic libraries, one compact26-test executable, one all14 snapshot driver; existing frozen native dependencies. Overall180s build;120s per correctness group.",
    "snapshot_comparison": "Each cold/warm/final exact comparison includes all output and input bits, context, basis, metadata, statuses, flags, public statistics, diagnostics and four private proof-work counters; both sides assert inactive N5 certificate counters.",
})
print(sha(HERE / "source-manifest.json"))

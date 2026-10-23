"""Verify original readiness without checking out Git or using mutable postrun metadata."""
from pathlib import Path
import hashlib
import json

snapshot = Path(__file__).resolve().parent
bundle = snapshot.parent
root = snapshot.parents[2]
sha = lambda path: hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
receipt = json.loads((snapshot / "preservation.json").read_text())
assert sha(snapshot / "manifest.json") == receipt["original_manifest_sha256"]
assert sha(snapshot / "replay-qualification.json") == receipt["original_qualification_sha256"]
assert sha(bundle / "replay-qualification.json") == receipt["current_postrun_qualification_sha256"]
original = json.loads((snapshot / "manifest.json").read_text())
mapping = {item["original_path"]: item for item in receipt["resolved_files"]}
assert len(mapping) == len(receipt["resolved_files"]) == len(original["files"]) == 50
assert set(mapping) == {item["path"] for item in original["files"]}
for item in original["files"]:
    resolved = mapping[item["path"]]
    assert resolved["original_sha256"] == item["sha256"]
    path = (bundle / resolved["resolved_path"]).resolve()
    assert path.is_relative_to(bundle)
    assert sha(path) == item["sha256"], item["path"]
    assert path.stat().st_size == item["bytes"]
for path, digest in receipt["protected_records_unchanged"].items():
    assert sha(root / path) == digest, path
before = json.loads((snapshot / "replay-qualification.json").read_text())
after = json.loads((bundle / "replay-qualification.json").read_text())
assert before["status"] == "numerical-replay-qualified-timing-pending"
assert after["status"] == "numerical-replay-and-raw-timing-qualified"
assert before["binary_sha256"] == after["binary_sha256"]
assert before["qualification_records"]["initial"] == after["qualification_records"]["initial"]
print(json.dumps({"status": "passed", "source_commit": receipt["source_commit"],
                  "original_manifest_files_verified": len(mapping),
                  "protected_records_verified": len(receipt["protected_records_unchanged"]),
                  "old_qualification_sha256": receipt["original_qualification_sha256"],
                  "postrun_qualification_sha256": receipt["current_postrun_qualification_sha256"],
                  "preservation_receipt_sha256": sha(snapshot / "preservation.json")}, indent=2))

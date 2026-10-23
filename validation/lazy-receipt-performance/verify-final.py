"""Verify the reviewed payload and append-only review/finalization records."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
inventory = read(here / "final-files.json")
actual = {str(p.relative_to(here)) for p in here.rglob("*") if p.is_file() and p.name != "final-files.json"}
assert actual == set(inventory), "Missing or unbound package file"
for name, digest in inventory.items():
    assert sha(here / name) == digest, name
final = read(here / "finalization.json")
assert sha(here / "qualification.json") == final["qualification_sha256"]
assert sha(here / "files.json") == final["reviewed_payload_inventory_sha256"]
assert sha(here / "review/package-review.json") == final["package_review_sha256"]
assert read(here / "review/package-review.json")["status"] == "passed"
runpy.run_path(str(here / "verify.py"), run_name="__main__")
print(json.dumps({"status": "passed", "final_payload_files": len(inventory),
                  "reviewed_payload_inventory_preserved": True, "no_numerical_execution": True}))

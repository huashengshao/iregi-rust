#!/usr/bin/env python3
"""Append readiness after review, without numerical work or a timing grant."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
HERE = OUT.parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((OUT / "manifest.json").read_text())
review_path = HERE / "review/protocol-review.json"
review = json.loads(review_path.read_text())
assert review["status"] == "passed"
assert review["protocol_manifest_sha256"] == sha(OUT / "manifest.json")
for name, digest in manifest["protocol_files"].items():
    assert sha(OUT / name) == digest
bindings = dict(manifest["bindings"])
for path in [OUT / "manifest.json", review_path]:
    bindings[str(path.relative_to(ROOT))] = sha(path)
ready = HERE / "timing-ready.json"
assert not ready.exists(), "readiness records are immutable"
ready.write_text(json.dumps({
    "status": "source_reviewed_and_optimized_preflight_passed_awaiting_quiet_grant",
    "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "timing_started": False, "bindings": bindings, "probe": manifest["probe"],
    "protocol_manifest_sha256": sha(OUT / "manifest.json"),
    "protocol_review_sha256": sha(review_path),
    "scope": "All source and optimized correctness gates passed. Full bound-input rehash happens at launch and after exit; this append-only source record grants no timing authority.",
}, indent=2) + "\n")
print(sha(ready))

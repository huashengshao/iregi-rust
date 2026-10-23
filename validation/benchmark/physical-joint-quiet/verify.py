#!/usr/bin/env python3
"""Verify the retained physical benchmark bundle without numerical execution."""
import gzip
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "files.json").read_text())
    for record in manifest["files"]:
        stored = (root / record["stored"]).read_bytes()
        assert len(stored) == record["stored_bytes"], record["stored"]
        assert hashlib.sha256(stored).hexdigest() == record["stored_sha256"], record["stored"]
        assert record["encoding"] in {"identity", "gzip"}, record["stored"]
        original = gzip.decompress(stored) if record["encoding"] == "gzip" else stored
        assert len(original) == record["source_bytes"], record["stored"]
        assert hashlib.sha256(original).hexdigest() == record["source_sha256"], record["stored"]
    qualification = json.loads((root / "qualification.json").read_text())
    assert qualification["producer_inputs_unchanged"] is True
    assert qualification["performance_parity_established"] is False
    measured = [row for row in qualification["rows"] if row["status"] == "measured"]
    failed = [row for row in qualification["rows"] if row["status"] == "failed"]
    assert len(measured) == 6 and len(failed) == 2
    assert all(row["gate"] == "inconclusive-noise" and row["ratio"]["relative_ci_width"] > .02
               and row["correctness"]["canonical_tensors_passed"]
               and row["correctness"]["preserved_graph_passed"] for row in measured)
    assert all(row["case"] == "gghhh" and row["rust_provenance_qualified"]
               and not row["rust_stages_present"]
               and "derived distance 0" in row["engine_failure"]["error"] for row in failed)
    print(f"Verified {len(manifest['files'])} retained files; six inconclusive measured rows and two guard failures.")


if __name__ == "__main__":
    main()

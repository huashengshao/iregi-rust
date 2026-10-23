#!/usr/bin/env python3
"""Verify retained diagnosis files; do not run a numerical engine."""
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    records = json.loads((root / "files.json").read_text())["files"]
    for record in records:
        data = (root / record["stored"]).read_bytes()
        assert len(data) == record["bytes"], record["stored"]
        assert hashlib.sha256(data).hexdigest() == record["sha256"], record["stored"]
    q = json.loads((root / "qualification.json").read_text())
    assert q["guard_unchanged"] and not q["binary64_benchmark_rows_changed"]
    assert not q["performance_gate"] and not q["automatic_rescue_wrapper_tested"]
    assert [row["numerical_response_status"] for row in q["precision_rows"]] == ["error", "prepared", "prepared"]
    assert q["convergence"]["complex_tensor_slots_checked"] == 280
    assert q["convergence"]["full_tensor_convergence_passed"]
    assert q["convergence"]["graph_convergence_passed"]
    print(f"Verified {len(records)} files; 53/128-bit failures retained and 256/512-bit convergence passed.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Join the immutable COLLIER capture with its independent saved-data review.

This performs no numerical integrals. Rejected durations remain diagnostics,
never accepted reduction benchmarks. Run from the repository root.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path.cwd().resolve()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path):
    return {"source": str(path.relative_to(ROOT)), "sha256": digest(path)}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def main():
    capture_path = HERE / "capture001/results.json"
    review_path = HERE / "independent-review.json"
    original_path = ROOT / "validation/benchmark/opening-rank6-20261026/summary.json"
    capture = json.loads(capture_path.read_text())
    review = json.loads(review_path.read_text())
    original = {row["id"]: row for row in json.loads(original_path.read_text())["rows"]}
    audits = {row["id"]: row for row in review["rows"]}
    rows = []
    for raw in capture["rows"]:
        row_id = raw["id"]
        audit = audits[row_id]
        accepted = raw["timing_qualified"]
        assert accepted is audit["expected_qualified"], row_id
        assert raw["native_returncode"] == 0 and raw["binary_unchanged_after"], row_id
        original_row = original[row_id]
        response_path = (HERE / "capture001" / row_id / "timed.response.json")
        response = json.loads(response_path.read_text())
        flag = response["lanes"][0]["worst_acc_flag"]
        nonfinite = audit["nonfinite_complex_fields"]
        mismatched = audit["mismatched_finite_complex_fields"]
        failure = None
        if not accepted:
            reason = "nonfinite" if nonfinite else f"{mismatched} mismatches"
            failure = f"acc {flag} · {reason}"
        rows.append({
            "id": row_id, "n": raw["n"], "rank": raw["rank"],
            "status": raw["status"], "timing_qualified": accepted,
            "failure_label": failure, "timing_us": raw["timing_us"],
            "timing_role": "accepted absolute reduction time" if accepted else "rejected-run diagnostic duration only",
            "numeric_type": "binary64", "working_bits": 53,
            "tirust_numeric_type": original_row["numeric_type"],
            "tirust_working_bits": original_row["working_bits"],
            "batch_size": 1, "mode": "COLI", "mode_number": 1,
            "repeats": 11, "iterations_per_block": raw["iterations_per_block"],
            "distinct_complex_fields": audit["distinct_complex_fields"],
            "nonfinite_complex_fields": nonfinite,
            "mismatched_finite_complex_fields": mismatched,
            "maximum_normalized_error_over_finite_fields": audit["maximum_normalized_error_over_finite_fields"],
            "timed_response": binding(response_path),
        })
    assert len(rows) == 12 and sum(row["timing_qualified"] for row in rows) == 9
    summary = {
        "schema_version": 1, "measurement_date": "2026-10-26",
        "purpose": "Right-most COLLIER column for the existing opening ordinary table",
        "input_family": "Identical fixed massive prefix inputs and cumulative Cartesian outputs; all native Laurent slots",
        "sources": [binding(path) for path in (capture_path, review_path, original_path, HERE / "build.json", HERE / "supervision.json")],
        "mode": "COLI", "mode_number": 1, "numeric_type": "binary64",
        "cpu": capture["cpu"], "rows": rows, "accepted_rows": 9, "rejected_rows": 3,
        "timing_scope": capture["timer_scope"],
        "protocol": "Three warmups, one pilot chooses a fixed count targeting100ms (cap1e6), then11 blocks. Means and descriptive standard errors across block means. No synchronized ratio or controlled-host confidence gate.",
        "comparison_limits": "Earlier TIRust observations remain unchanged; N5/N6 use Float128. COLLIER is binary64 and includes status/finite scans inside timing. No equal-precision speed ratio is inferred.",
        "rejected_duration_policy": "Amber cells identify failed accuracy/nonfinite results. Their observed durations are diagnostic, not valid reduction benchmark times.",
        "capture_relocation": {"original_prefix": "target/collier-opening-column-20261026/capture001", "archive_prefix": "validation/benchmark/opening-collier-20261026/capture001", "raw_bytes_changed": False},
    }
    save(HERE / "summary.json", summary)
    qualification = {
        "schema_version": 1, "status": "nine_accepted_three_explicitly_rejected",
        "scope": "All twelve original ordinary rows attempted once with fixed COLI mode1; no retries or mode retuning",
        "distinct_complex_fields": sum(row["distinct_complex_fields"] for row in rows),
        "qualified_distinct_complex_fields": sum(row["distinct_complex_fields"] for row in rows if row["timing_qualified"]),
        "nonfinite_complex_fields": sum(row["nonfinite_complex_fields"] for row in rows),
        "mismatched_finite_complex_fields": sum(row["mismatched_finite_complex_fields"] for row in rows),
        "accepted_rows": [row["id"] for row in rows if row["timing_qualified"]],
        "rejected_rows": [{key: row[key] for key in ("id", "failure_label", "nonfinite_complex_fields", "mismatched_finite_complex_fields")} for row in rows if not row["timing_qualified"]],
        "independent_review": binding(review_path),
        "tolerance": "1e-10 dimensionally normalized mixed tolerance",
        "no_aggregate_speed_or_ratio_gate": True,
    }
    save(HERE / "qualification.json", qualification)
    print(json.dumps({"accepted_rows": 9, "rejected_rows": 3, "distinct_complex_fields": qualification["distinct_complex_fields"]}))


if __name__ == "__main__":
    main()

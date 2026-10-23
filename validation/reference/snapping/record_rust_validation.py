"""Attach inputs and reference provenance to an executed Rust test report."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
HERE = ROOT / "validation/reference/snapping"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=ROOT / "target/legacy-snapping-tensor-validation.json")
    parser.add_argument("--test-binary", type=Path)
    parser.add_argument("--label", default="binary64 primary reduction")
    parser.add_argument("--output", type=Path, default=HERE / "rust-validation.json")
    args = parser.parse_args()
    reference_path = HERE / "reductions.json"
    references = json.loads(reference_path.read_text())
    report = json.loads(args.report.read_text())
    by_id = {case["input"]["id"]: case for case in references["cases"]}
    for case in report["cases"]:
        reference = by_id[case["id"]]
        case["input"] = reference["input"]
        case["reference"] = reference["reference"]
        status = case.get("status", "")
        case["qualification"] = (
            "agrees_with_original_iregi" if case["passed"] else
            "requires_verified_higher_precision" if "estimated cancellation" in status else
            "exact_singular_cayley_recurrence_pending" if "nonfinite coefficients" in status else
            "unresolved_failure"
        )
    if len(report["cases"]) != len(by_id) or {case["id"] for case in report["cases"]} != set(by_id):
        raise AssertionError("Rust report does not cover every committed reference case exactly once")
    report["label"] = args.label
    report["reference_fixture_sha256"] = hashlib.sha256(reference_path.read_bytes()).hexdigest()
    report["reference_driver_sha256"] = references["driver_sha256"]
    report["reference_source_sha256"] = json.loads((HERE / "snapshot.json").read_text())["source_sha256"]
    if args.test_binary:
        report["rust_test_binary_sha256"] = hashlib.sha256(args.test_binary.read_bytes()).hexdigest()
    report["summary"] = {"total": len(report["cases"]), "passed": sum(case["passed"] for case in report["cases"])}
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Recorded all {report['summary']['total']} cases; {report['summary']['passed']} passed")


if __name__ == "__main__":
    main()

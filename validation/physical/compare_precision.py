#!/usr/bin/env python3
"""Check complete physical CLI reruns at two independent working precisions."""
import argparse
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from compare_cli import CASES, digest, kinematic_scale, normalized_error, number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lower-report", type=Path, required=True)
    parser.add_argument("--higher-report", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=1e-10)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not math.isfinite(args.tolerance) or args.tolerance <= 0:
        parser.error("tolerance must be finite and positive")
    result_paths = [path.with_suffix(".cli.json") for path in [args.lower_report, args.higher_report]]
    output = {
        "schema_version": 1,
        "passed": False,
        "tolerance": args.tolerance,
        "qualification": "Complete CLI reruns reparse the original input and reevaluate the numerator and contraction at each precision. Comparison arithmetic is binary64 and certifies no additional digits. Reference comparisons remain separately recorded.",
        "provenance": {
            "script_sha256": digest(Path(__file__)),
            "comparison_helpers_sha256": digest(Path(__file__).with_name("compare_cli.py")),
            "input_sha256": digest(args.input),
            "reports": [{"path": str(path), "sha256": digest(path)} for path in [args.lower_report, args.higher_report]],
            "cli_results": [{"path": str(path), "sha256": digest(path)} for path in result_paths],
        },
    }
    try:
        reports = [json.loads(path.read_text()) for path in [args.lower_report, args.higher_report]]
        runs = [json.loads(path.read_text()) for path in result_paths]
        sample = json.loads(args.input.read_text())
        if any(report["cli_status"]["status"] != "success" for report in reports):
            raise ValueError("both CLI invocations must succeed")
        if reports[0]["case"] != reports[1]["case"]:
            raise ValueError("physical cases differ")
        for key in ["cli_sha256", "input_sha256", "graph_sha256", "model_sha256"]:
            if reports[0]["provenance"][key] is None or reports[0]["provenance"][key] != reports[1]["provenance"][key]:
                raise ValueError(f"run provenance differs or is unavailable: {key}")
        if reports[0]["provenance"]["input_sha256"] != digest(args.input):
            raise ValueError("comparison input differs from the executed input")
        if runs[0]["precision_bits"] >= runs[1]["precision_bits"]:
            raise ValueError("higher run must use more working precision")
        for key in ["settings", "basis", "poles", "kinematics_contract"]:
            if runs[0][key] != runs[1][key]:
                raise ValueError(f"run contract differs: {key}")
        lanes = []
        for run in runs:
            if len(run["samples"]) != 1 or run["samples"][0]["status"] != "success":
                raise ValueError("each run must contain exactly one successful sample")
            if run["samples"][0]["id"] != sample["id"]:
                raise ValueError("sample identity differs from input")
            lanes.append(run["samples"][0])
        basis = runs[0]["basis"]
        if any(len(lane["moments"]) != len(basis) for lane in lanes):
            raise ValueError("tensor dimensions differ")
        scale = kinematic_scale(sample)
        maximum, worst = 0.0, None
        for index, (lower, higher) in enumerate(zip(lanes[0]["moments"], lanes[1]["moments"])):
            if len(lower) != 4 or len(higher) != 4:
                raise ValueError("tensor Laurent slots are incomplete")
            natural = scale ** (4 + sum(basis[index]) - 2 * len(sample["propagators"]))
            for pole, (a, b) in enumerate(zip(lower, higher)):
                error = normalized_error(number(a), number(b), natural)
                if error > maximum:
                    maximum, worst = error, {"moment": index, "exponents": basis[index], "pole": pole}
        if any(len(lane["integral"]) != 4 for lane in lanes):
            raise ValueError("physical Laurent slots are incomplete")
        physical_scale = scale ** CASES[reports[0]["case"]][4]
        integral_errors = [normalized_error(number(a), number(b), physical_scale)
                           for a, b in zip(lanes[0]["integral"], lanes[1]["integral"])]
        output.update(
            case=reports[0]["case"],
            working_bits=[run["precision_bits"] for run in runs],
            accuracy_bits=[run["precision_control"]["accuracy_bits"] for run in runs],
            independently_passed_reference_reports=[report["passed"] for report in reports],
            tensor_comparison={"moments": len(basis), "slots_per_moment": 4,
                               "max_normalized_error": maximum, "worst": worst},
            physical_comparison={"laurent_order": runs[0]["poles"], "errors": integral_errors},
            passed=max(maximum, *integral_errors) <= args.tolerance,
        )
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        output["failure"] = str(error)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    print(json.dumps(output, indent=2, allow_nan=False))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

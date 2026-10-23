#!/usr/bin/env python3
"""Retain disagreements between original IREGI modes at physical fixture points."""
import argparse
import json
import math
from pathlib import Path
import subprocess

import compare_cli as physical


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=physical.CASES, action="append")
    parser.add_argument("--oracle", type=Path, default=Path("target/reference/iregi-reference-original"))
    parser.add_argument("--output", type=Path, default=Path("target/physical/canonical-reference-audit.json"))
    args = parser.parse_args()
    audit = {
        "schema_version": 1, "reference_sha256": physical.digest(args.oracle),
        "script_sha256": physical.digest(Path(__file__)),
        "comparison_script_sha256": physical.digest(Path(physical.__file__)),
        "qualification": "Original IREGI modes compared at canonical physical inputs. No Rust reduction is executed. All four Laurent slots are numerically converted to OneLoop. A disagreement does not identify the correct mode.",
        "tolerance": 1e-10, "cases": [],
    }
    raw = []
    for name in args.case or physical.CASES:
        input_path = Path(f"validation/physical/{name}-cli-input.json")
        sample = json.loads(input_path.read_text())
        scale = physical.kinematic_scale(sample)
        entry = {"case": name, "input_sha256": physical.digest(input_path), "rank": sample["rank"],
                 "kinematic_scale": scale, "modes": [], "comparisons_to_ibp": []}
        results = {}
        for mode in physical.MODES:
            case = {"id": name.replace("-", "_") + f"_preflight_mode{mode}", "api": "tensor",
                    "mode": mode, "rank": sample["rank"], "dimension_shift": 0,
                    "mu": sample["mu"], "snap": False, "threshold": 1e-6,
                    "propagators": sample["propagators"]}
            capture = {"input": case}
            try:
                records, process = physical.evaluate(args.oracle.resolve(), [case], allow_stop=True)
                capture.update(results=records, stdout=process.stdout, stderr=process.stderr,
                               returncode=process.returncode)
                if process.returncode or len(records) != 1 or not records[0]["stable"]:
                    raise ValueError("original IREGI did not return one stable result")
                moments = records[0]["moments"]
                if len(moments) != math.comb(sample["rank"] + 4, 4):
                    raise ValueError("original IREGI tensor shape differs from the requested rank")
                results[mode] = moments
                entry["modes"].append({"mode": mode, "stable": True, "moments": len(moments)})
            except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
                capture["error"] = str(error)
                entry["modes"].append({"mode": mode, "stable": False, "error": str(error)})
            raw.append(capture)
        for mode in [1, 2]:
            if 0 not in results or mode not in results:
                continue
            maximum, worst, by_slot, mismatches = 0.0, None, {}, []
            for index, (actual, reference) in enumerate(zip(results[mode], results[0])):
                # Original IREGI orders Cartesian moments by increasing total rank.
                rank = next(rank for rank in range(sample["rank"] + 1)
                            if index < math.comb(rank + 4, 4))
                dimension = 4 + rank - 2 * len(sample["propagators"])
                for pole, (x, y) in enumerate(zip(physical.one_loop_slots(actual),
                                                  physical.one_loop_slots(reference))):
                    error = physical.normalized_error(x, y, scale ** dimension)
                    slot = ["uv1", "ir1", "ir2", "finite"][pole]
                    by_slot[slot] = max(by_slot.get(slot, 0.0), error)
                    if error > audit["tolerance"]:
                        mismatches.append({"moment": index, "rank": rank, "pole": slot,
                                           "error": error, "mode_value": physical.pair(x),
                                           "ibp_value": physical.pair(y)})
                    if error > maximum:
                        maximum = error
                        worst = {"moment": index, "rank": rank, "pole": pole,
                                 "mode_value": physical.pair(x), "ibp_value": physical.pair(y)}
            entry["comparisons_to_ibp"].append({"mode": mode, "max_normalized_error": maximum,
                                                "max_error_by_slot": by_slot, "mismatches": mismatches,
                                                "passed": maximum <= audit["tolerance"], "worst": worst})
        audit["cases"].append(entry)
    audit["all_modes_agree"] = all(
        all(mode["stable"] for mode in case["modes"])
        and all(comparison["passed"] for comparison in case["comparisons_to_ibp"])
        for case in audit["cases"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".oracle.json").write_text(json.dumps(raw, indent=2, allow_nan=False) + "\n")
    args.output.write_text(json.dumps(audit, indent=2, allow_nan=False) + "\n")
    print(json.dumps(audit, indent=2, allow_nan=False))
    return 0 if audit["all_modes_agree"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

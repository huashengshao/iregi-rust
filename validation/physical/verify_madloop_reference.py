#!/usr/bin/env python3
"""Verify a captured MadLoop graph against explicit original IREGI modes.

This uses MadLoop's own positive-PDEN routing, native-to-MadLoop convention,
coefficient ordering, and legacy snapping. It does not execute Rust/Symbolica.
"""
import argparse
import itertools
import json
import math
from pathlib import Path
import subprocess

import compare_cli as physical


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=physical.CASES, default="gghhh")
    parser.add_argument("--oracle", type=Path, default=Path("target/reference/iregi-reference-original"))
    parser.add_argument("--reference-mode", type=int, choices=physical.MODES, action="append")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(f"target/physical/{args.case}-madloop-reference-modes.json")
    fixture_path = Path(f"validation/physical/madloop/fixtures/{args.case}-helicity-1.json")
    fixture = json.loads(fixture_path.read_text())
    group = fixture["selected_feynkit_group"]
    record = next(record for record in fixture["records"] if record["group"] == group)
    if record["mode"] != 1:
        raise ValueError("this verifier expects MadLoop CTMODE=1 without routing reversal")
    modes = sorted(set(args.reference_mode or [1, 2]))
    report = {
        "schema_version": 1, "case": args.case, "group": group, "passed": False,
        "tolerance": 1e-10, "captured_ctmode": record["mode"],
        "input_policy": "Original MadLoop INITIREGI: legacy on-shell snapping enabled, threshold1e-6",
        "qualification": "Independent original IREGI mode replay at MadLoop's own routing. This qualifies the captured tensor/contraction reference, not Rust reduction.",
        "provenance": {"fixture_sha256": physical.digest(fixture_path),
                       "original_iregi_sha256": physical.digest(args.oracle),
                       "script_sha256": physical.digest(Path(__file__)),
                       "normalization_helper_sha256": physical.digest(Path(physical.__file__))},
        "comparisons": [],
    }
    # Native IREGI orders within each rank lexicographically in Lorentz indices;
    # MadLoop exports its different ordering explicitly in coefficient_indices.
    native_indices = [indices for rank in range(record["rank"] + 1)
                      for indices in itertools.combinations_with_replacement(range(4), rank)]
    lookup = {indices: index for index, indices in enumerate(native_indices)}
    sample = {"mu": record["mu"], "propagators": [
        {"shift": shift, "mass_squared": mass, "power": 1}
        for shift, mass in zip(record["shifts"], record["masses_squared"], strict=True)]}
    scale = physical.kinematic_scale(sample)
    report["kinematic_scale"] = scale
    captured_tensors = {(item["coefficient"], item["laurent_slot"]): physical.number(item["value"])
                        for item in record["tensors"]}
    output.parent.mkdir(parents=True, exist_ok=True)
    raw = []
    for mode in modes:
        case = {"id": args.case.replace("-", "_") + f"_madloop_mode{mode}",
                "api": "tensor", "mode": mode, "rank": record["rank"],
                "dimension_shift": 0, "mu": record["mu"], "snap": True,
                "threshold": 1e-6, "propagators": sample["propagators"]}
        comparison = {"mode": mode, "algorithm": physical.MODES[mode], "passed": False}
        capture = {"input": case}
        try:
            results, process = physical.evaluate(args.oracle.resolve(), [case], allow_stop=True)
            capture.update(results=results, returncode=process.returncode,
                           stdout=process.stdout, stderr=process.stderr)
            if process.returncode or len(results) != 1 or not results[0]["stable"]:
                raise ValueError("original IREGI did not return one stable result")
            moments = results[0]["moments"]
            if len(moments) != len(native_indices):
                raise ValueError("unexpected original IREGI moment count")
            reordered = []
            maximum, worst = 0.0, None
            for coefficient, indices in enumerate(fixture["coefficient_indices"][:len(moments)]):
                rank = len(indices)
                uv, ir, ir2, finite = physical.one_loop_slots(moments[lookup[tuple(indices)]])
                sign = -1 if rank % 2 else 1
                slots = [sign * finite, sign * (uv + ir), sign * ir2]
                reordered.append(slots)
                dimension = 4 + rank - 2 * record["propagators"]
                for pole, actual in enumerate(slots):
                    expected = captured_tensors[(coefficient, pole)]
                    error = physical.normalized_error(actual, expected, scale ** dimension)
                    if error > maximum:
                        maximum = error
                        worst = {"coefficient": coefficient, "lorentz_indices": indices,
                                 "pole": pole, "actual": physical.pair(actual),
                                 "captured": physical.pair(expected)}
            if len(reordered) != len(moments) or len(captured_tensors) != 3 * len(moments):
                raise ValueError("MadLoop and original IREGI tensor shapes differ")
            coefficients = list(map(physical.number, record["numerator"]))
            if len(coefficients) != len(reordered):
                raise ValueError("MadLoop numerator and tensor lengths differ")
            # Numeric scalar products of independently produced coefficients.
            contracted = []
            for pole in range(3):
                terms = [coefficient * slots[pole]
                         for coefficient, slots in zip(coefficients, reordered, strict=True)]
                contracted.append(complex(math.fsum(term.real for term in terms),
                                          math.fsum(term.imag for term in terms)))
            contraction_errors = [physical.normalized_error(actual, physical.number(expected),
                                   scale ** physical.CASES[args.case][4])
                                  for actual, expected in zip(contracted, record["raw_result"], strict=True)]
            passed = maximum <= report["tolerance"] and max(contraction_errors) <= report["tolerance"]
            comparison.update(status="passed" if passed else "mismatch", passed=passed,
                              tensor_max_normalized_error=maximum, worst=worst,
                              tensor_slots=len(captured_tensors),
                              contracted_raw=list(map(physical.pair, contracted)),
                              captured_raw=record["raw_result"], contraction_errors=contraction_errors)
        except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
            comparison.update(status="reference_failed", reason=str(error))
            capture["error"] = str(error)
        raw.append(capture)
        report["comparisons"].append(comparison)
    report["passed"] = all(comparison["passed"] for comparison in report["comparisons"])
    output.with_suffix(".oracle.json").write_text(json.dumps(raw, indent=2, allow_nan=False) + "\n")
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Inspect original IREGI threshold sensitivity and an exact odd-moment symmetry.

Validation only. No Rust or Symbolica runtime is called. Run from repository root:
source scripts/env.sh
python3 validation/pv-high-rank/canonical_pentagon_threshold_probe.py --write
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path.cwd() / "validation/physical"))
import compare_cli as physical


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    source = Path("validation/physical/gghhh-cli-input.json")
    sample = json.loads(source.read_text())
    symmetric = copy.deepcopy(sample)
    # Rotation in the xy plane aligns the exact symmetric reflection with y.
    # Every paired coordinate is the same decimal string up to its sign, so
    # the reflection also preserves the binary64 input exactly.
    symmetric_shifts = [
        ["0", "0", "0", "0"],
        ["375", "0", "0", "-375"],
        ["125", "-187.5", "108.253175473054824", "-375"],
        ["-125", "-187.5", "-108.253175473054824", "-375"],
        ["-375", "0", "0", "-375"],
    ]
    for propagator, shift in zip(symmetric["propagators"], symmetric_shifts, strict=True):
        propagator["shift"] = shift
    null_edge = copy.deepcopy(sample)
    null_edge["propagators"][1]["shift"][3] = "-" + sample["propagators"][1]["shift"][0]
    executable = Path("target/reference/iregi-reference-original").resolve()
    report = {
        "source": str(source),
        "source_sha256": physical.digest(source),
        "reference_sha256": physical.digest(executable),
        "script_sha256": physical.digest(Path(__file__)),
        "convention": "OneLoop, raw Cartesian tensor moments",
        "target": {"moment_index": 54, "exponents": [1, 0, 0, 3], "numerator": "q0*qz^3"},
        "symmetric_input": symmetric["propagators"],
        "canonical_p1_exact_null_input": null_edge["propagators"],
        "null_edge_change": "Only propagator1 shift[3] is set to minus its shift[0], changing it by 5.7e-14 in the supplied decimal data.",
        "source_findings": [
            "INITIREGI's supplied threshold sets ZEROTHR_IREGI; recurrence EPS is the fixed parameter 1e-10 in original src/global.f90:37. This scan does not vary recurrence EPS.",
            "Original src/si_reduce.f90:723 uses the generic invertible-R/S recurrence when their absolute determinants exceed EPS. An equal-mass near-lightlike bubble has R eigenvalues -s and s-4m^2, so this determinant test does not control conditioning.",
            "Original src/si_reduce.f90:795-799 maps the exceptional dimension divisor into a PV coefficient with IBP2PAVE. This convention alone does not explain a full Cartesian-tensor discrepancy.",
        ],
        "four_dimensional_projection": "For D-dimensional q=qbar+qperp and four-dimensional external shifts, D_j-D_0=2(p_j-p_0).(qbar+p_0)+f_j: qperp^2 cancels exactly. Inverting the four-dimensional external basis therefore determines each q0..3 component exactly, without dropping an evanescent numerator term.",
        "independent_parameter_formula": "At epsilon=0 the OneLoop target is integral over sum(x_i)=1,x_i>=0 of -(3/2)*P0*Pz/(F-i0)^2 -2*P0*Pz^3/(F-i0)^3, with P=sum(x_i*p_i), F=m^2-sum(i<j,x_i*x_j*(p_i-p_j)^2). Every UV/IR pole vanishes. F changes sign at this physical point, so real-simplex quadrature without a contour prescription is not a valid evaluation.",
        "independent_power_counting": {
            "space_time_dimension_at_epsilon_zero": 4,
            "numerator_rank": 4,
            "propagator_count": 5,
            "superficial_uv_degree": -2,
            "expected_uv_single": [0, 0],
            "expected_ir_single": [0, 0],
            "expected_ir_double": [0, 0],
            "argument": "The large-loop-momentum degree is 4+4-2*5=-2, so the one-loop integral is ultraviolet convergent. There are no UV subloops. Every internal squared mass is the positive value 29929, excluding soft and collinear infrared divergences. Physical thresholds require the Feynman prescription but do not generate dimensional-regularization poles at this generic point. Consequently every Laurent pole of this tensor moment is exactly zero, independently of reduction and finite-part quadrature.",
        },
        "symmetry": "q0->-q0, qy->-qy swaps propagators1<->4 and2<->3 and fixes0. Equal masses and measure are invariant, q0*qz^3 is odd, so its exact integral is zero in every Laurent slot.",
        "qualification": "Threshold scan of untouched original IREGI and an exact tensor symmetry. No numerical integral or Rust reduction is evaluated; variation does not independently identify the canonical answer.",
        "results": [],
    }
    for name, point in [("canonical", sample), ("symmetric_rotated", symmetric), ("canonical_p1_exact_null", null_edge)]:
        thresholds = ["1e-6"] if name == "canonical_p1_exact_null" else ["1e-6", "1e-8", "1e-10", "1e-12", "1e-15", "1e-18", "1e-21"]
        for threshold in thresholds:
            records = {}
            entries = []
            for mode in [0, 1, 2]:
                case = {
                    "id": f"{name}_eps{threshold}_mode{mode}",
                    "api": "tensor", "mode": mode, "rank": point["rank"],
                    "dimension_shift": 0, "mu": point["mu"], "snap": False,
                    "threshold": threshold, "propagators": point["propagators"],
                }
                values, process = physical.evaluate(executable, [case], allow_stop=True)
                entry = {"input": name, "threshold": threshold, "mode": mode,
                         "returncode": process.returncode}
                if process.returncode or len(values) != 1:
                    entry.update(stable=False, stdout=process.stdout, stderr=process.stderr)
                else:
                    value = values[0]
                    entry["stable"] = value["stable"]
                    entry["target"] = [physical.pair(slot) for slot in physical.one_loop_slots(value["moments"][54])]
                    entry["target_native_iregi"] = [physical.pair(physical.number(slot)) for slot in value["moments"][54]]
                    entry["full_result_sha256"] = hashlib.sha256(
                        json.dumps(value, sort_keys=True).encode()).hexdigest()
                    records[mode] = value["moments"]
                entries.append(entry)
            for entry in entries:
                if entry["mode"] != 1 and entry["mode"] in records and 1 in records:
                    target = physical.one_loop_slots(records[entry["mode"]][54])[3]
                    pv_target = physical.one_loop_slots(records[1][54])[3]
                    entry["target_finite_difference_from_pv"] = physical.pair(target - pv_target)
                report["results"].append(entry)
                print(name, threshold, entry["mode"], entry["stable"], entry.get("target", [None] * 4)[3])
    lookup = {(r["input"], r["mode"]): r for r in report["results"] if r["threshold"] == "1e-6"}
    report["observed_single_coordinate_sensitivity"] = {
        "binary64_coordinate_change": float(null_edge["propagators"][1]["shift"][3]) - float(sample["propagators"][1]["shift"][3]),
        "ibp_target_change": physical.pair(physical.number(lookup[("canonical_p1_exact_null", 0)]["target"][3]) - physical.number(lookup[("canonical", 0)]["target"][3])),
        "pv_target_change": physical.pair(physical.number(lookup[("canonical_p1_exact_null", 1)]["target"][3]) - physical.number(lookup[("canonical", 1)]["target"][3])),
        "interpretation": "Original IBP changes by about 1e-6 under a one-ulp external-coordinate change that makes a near-lightlike edge exactly lightlike; PV changes by about 1e-20 and the modes agree at the exactly lightlike variant. This supports internal IBP numerical instability. A high-precision canonical-point evaluation remains required to certify its answer.",
    }
    report["observed_uv_power_counting_violation"] = {
        "canonical_ibp_uv_oneloop": lookup[("canonical", 0)]["target"][0],
        "canonical_ibp_uv_native_iregi": lookup[("canonical", 0)]["target_native_iregi"][0],
        "canonical_pv_uv_oneloop": lookup[("canonical", 1)]["target"][0],
        "canonical_pv_uv_native_iregi": lookup[("canonical", 1)]["target_native_iregi"][0],
        "interpretation": "The original IBP result contains a spurious UV pole, contradicting independent ultraviolet power counting. This proves that result is incorrect without evaluating the physical finite part. The conversion from native IREGI finite to OneLoop finite adds (EulerGamma+ln(pi))*UV before division by i*pi^2, so the erroneous UV pole also explains why the two conventions' finite discrepancies are not related by i*pi^2 alone. The finite canonical answer still requires an independent evaluation.",
    }
    if args.write:
        Path("validation/pv-high-rank/canonical-pentagon-threshold-probe.json").write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()

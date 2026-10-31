#!/usr/bin/env python3
"""Reference array of the N7R7 row added to the opening corpus (capture 003).

Inputs: the six opening shifts (0, e_x, e_y, e_z, e_t/2, e_x + e_y) and
squared masses (1, 2, 3, 4, 2, 3) plus q_6 = (1/4, 3/8, 1/8, 5/8) with m_6^2 = 4, mu = 3
(exact dyadic values, Euclidean-like region below every threshold). The
reference is TIRust's direct engine at 256 bits (stability_driver of
validation/benchmark/stability-20261030), accepted only if quadruple-precision
original IREGI (IBP or PV) confirms it to E/A <= 1e-12 (COLLIER COLI and DD
are recorded, not required: COLI returns NaN on this point); written as exact rationals of its printed digits in the corpus format
(`first_output.lanes[0].values`, [re, im] per moment and Laurent slot), with
the checks in check.json. Run after build.py of the stability study.
"""
import importlib.util
import json
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = ROOT / "validation/benchmark/stability-20261030"
SHIFTS = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0.5, 0, 0, 0], [0, 1, 1, 0], [0.25, 0.375, 0.125, 0.625]]
MASSES = [1.0, 2.0, 3.0, 4.0, 2.0, 3.0, 4.0]
MU = 3.0


def main():
    spec = importlib.util.spec_from_file_location("study", STUDY / "run.py")
    study = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(study)
    integral = {"id": "ordinary-n7-r7", "n": 7, "rank": 7, "mu": MU, "masses_squared": MASSES,
                "points": [[[float(x) for x in s] for s in SHIFTS]]}
    points = integral["points"]
    tirust = study.tirust(points, integral)[0]
    reference = tirust["direct256"]["moments"]
    checks = {"tirust_status": tirust["direct256"]["status"]}
    for mode, name in ((0, "quad_ibp"), (1, "quad_pv")):
        checks[name] = study.exact_error(study.quad(points, integral, mode)[0], reference, 7, 7, MU)
    for mode, name in ((1, "collier_coli"), (2, "collier_dd")):
        lanes = study.collier(points, integral, mode)
        checks[name] = study.array_error(study.lane_values(lanes[0])[0] if lanes else None, reference, 7, 7, MU)
    checks["tirust_binary64_default"] = study.array_error(tirust["default"]["moments"], reference, 7, 7, MU)
    print(json.dumps(checks, indent=1))
    quad_ok = min(v for k, v in checks.items() if k.startswith("quad") and v is not None) <= 1e-12
    assert quad_ok, checks
    values = []
    for moment in reference:
        for re, im in moment:
            values.append([{"exact_rational": str(Fraction(Decimal(str(re)))), "finite": True},
                           {"exact_rational": str(Fraction(Decimal(str(im)))), "finite": True}])
    out = HERE / "n7r7"
    out.mkdir(exist_ok=True)
    (out / "result.json").write_text(json.dumps({
        "description": "N7R7 reference: TIRust direct engine at 256 bits, confirmed by quad original IREGI and COLLIER",
        "inputs": {"shifts": SHIFTS, "masses_squared": MASSES, "mu": MU},
        "first_output": {"convention": "IregiNative", "lanes": [{"values": values}]}}) + "\n")
    (out / "check.json").write_text(json.dumps(checks, indent=1) + "\n")


if __name__ == "__main__":
    main()

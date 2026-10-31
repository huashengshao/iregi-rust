#!/usr/bin/env python3
"""Derive the direct-engine campaign inputs from the fixed 18-row opening corpus.

Lane 0 of every request is the unchanged opening sample (exact dyadic strings).
Batch-32 lanes l=1..31 are binary-exact perturbations: shifts x (256+l)/256 and
squared masses + l/64, with the common scale mu kept (the IREGI driver takes one
scale per batch). They stay IR finite, below thresholds and inside COLLIER's
positive-Feynman-polynomial domain. Output: inputs.json next to this script.
"""
import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "validation/benchmark/opening-rank6-20261026/inputs.json"
LANES = 32


def text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def lane(sample: dict, index: int) -> dict:
    scale = Fraction(256 + index, 256)
    shifts = [[text(Fraction(x) * scale) for x in shift] for shift in sample["shifts"]]
    masses = [[text(Fraction(m[0]) + Fraction(index, 64)), text(Fraction(m[1]))] for m in sample["masses_squared"]]
    return {"shifts": shifts, "masses_squared": masses, "mu": sample["mu"]}


def main() -> None:
    raw = SOURCE.read_bytes()
    source = json.loads(raw)
    cases = []
    for case in source["cases"]:
        request = case["driver_request"]
        sample = request["samples"][0]
        assert lane(sample, 0) == {"shifts": sample["shifts"], "masses_squared": sample["masses_squared"], "mu": sample["mu"]}
        cases.append({
            "id": request["id"],
            "table": case["table"],
            "label": case["label"],
            "n": request["n"],
            "rank": request["rank"],
            "powers": request["powers"],
            "dimension_shift": request["dimension_shift"],
            "reference": f"validation/benchmark/opening-rank6-20261026/cases/{request['id']}/result.json",
            "lanes": [lane(sample, index) for index in range(LANES)],
        })
    # Capture 003 (inputs-003.json; inputs.json stays bound unchanged): an N7R7 row (the six opening shifts and masses plus
    # q_6 = (1/4, 3/8, 1/8, 5/8), m_6^2 = 4: the first such dyadic choices
    # (e_t/2 + e_z, ...) made six-point thin systems or null-hyperplane boxes
    # exactly singular; reference from make-n7r7-reference.py).
    seven = {"shifts": [["0", "0", "0", "0"], ["0", "1", "0", "0"], ["0", "0", "1", "0"], ["0", "0", "0", "1"],
                        ["1/2", "0", "0", "0"], ["0", "1", "1", "0"], ["1/4", "3/8", "1/8", "5/8"]],
             "masses_squared": [[m, "0"] for m in ("1", "2", "3", "4", "2", "3", "4")], "mu": "3"}
    cases.insert(next(i for i, c in enumerate(cases) if c["id"] == "ordinary-n6-r6") + 1, {
        "id": "ordinary-n7-r7", "table": "ordinary", "label": "N=7, R=7", "n": 7, "rank": 7,
        "powers": [1] * 7, "dimension_shift": 0,
        "reference": "validation/benchmark/direct-engine-20261030/n7r7/result.json",
        "lanes": [lane(seven, index) for index in range(LANES)],
    })
    document = {
        "schema_version": 1,
        "suite_id": "direct-engine-20261030",
        "source": {"path": str(SOURCE.relative_to(ROOT)), "sha256": hashlib.sha256(raw).hexdigest()},
        "lane_rule": "lane 0 = opening sample; lane l: shifts*(256+l)/256, masses^2 + l/64, common mu",
        "batch_sizes": [1, LANES],
        "cases": cases,
    }
    (HERE / "inputs-003.json").write_text(json.dumps(document, indent=1) + "\n")


if __name__ == "__main__":
    main()

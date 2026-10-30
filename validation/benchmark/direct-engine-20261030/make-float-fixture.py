#!/usr/bin/env python3
"""Write the binary64 fixture read by `cargo run --example direct_check`.

Converts the 18 opening inputs and their archived reference arrays (exact
rationals) to floats. usage: make-float-fixture.py OUTPUT.json
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "validation/benchmark/opening-rank6-20261026"

cases = []
for case in json.loads((BASE / "inputs.json").read_text())["cases"]:
    request = case["driver_request"]
    sample = request["samples"][0]
    output = json.loads((BASE / "cases" / request["id"] / "result.json").read_text())["first_output"]
    cases.append({
        "id": request["id"], "n": request["n"], "rank": request["rank"], "powers": request["powers"],
        "h": request["dimension_shift"],
        "shifts": [[float(Fraction(x)) for x in shift] for shift in sample["shifts"]],
        "masses": [[float(Fraction(m[0])), float(Fraction(m[1]))] for m in sample["masses_squared"]],
        "mu": float(Fraction(sample["mu"])), "basis": output["basis"],
        "reference": [[float(Fraction(z[0]["exact_rational"])), float(Fraction(z[1]["exact_rational"]))]
                      for z in output["lanes"][0]["values"]],
    })
Path(sys.argv[1]).write_text(json.dumps(cases))

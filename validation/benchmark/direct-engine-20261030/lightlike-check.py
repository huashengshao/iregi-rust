#!/usr/bin/env python3
"""Cross-check TIRust's public binary64 default against original IREGI on
lightlike and massless kinematics (massless external legs), complete arrays.

The old TIRust symbolic engine refuses several of these points in binary64,
so original IREGI (IBP, binary64; PV where usable) is the independent
reference. Exactly representable lightlike momenta: k1=(5,0,0,5),
k2=(5,0,0,-5), k3=-(5,3,0,4), k4=-(k1+k2+k3), all on shell.

usage: lightlike-check.py TIRUST_DRIVER IREGI_DRIVER OUTPUT.json
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("campaign_run", HERE / "run.py")
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)

K1, K2, K3 = (5, 0, 0, 5), (5, 0, 0, -5), (-5, -3, 0, -4)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


Q2 = add(K1, K2)
Q3 = add(Q2, K3)
ZERO = (0, 0, 0, 0)
CASES = [
    ("massless triangle", [ZERO, K1, Q2], [0, 0, 0], 3),
    ("massless box", [ZERO, K1, Q2, Q3], [0, 0, 0, 0], 3),
    ("massless box rank4", [ZERO, K1, Q2, Q3], [0, 0, 0, 0], 4),
    ("ggH triangle", [ZERO, K1, Q2], [3, 3, 3], 3),
    ("ggHH box", [ZERO, K1, Q2, Q3], [3, 3, 3, 3], 4),
    ("mixed box", [ZERO, K1, Q2, Q3], [0, 3, 3, 0], 3),
    ("lightlike bubble", [ZERO, K1], [1, 2], 4),
]


def case_record(label, shifts, masses, rank):
    n = len(shifts)
    lane = {"shifts": [[str(x) for x in s] for s in shifts],
            "masses_squared": [[str(m), "0"] for m in masses], "mu": "3"}
    return {"id": label.replace(" ", "-"), "table": "ordinary", "n": n, "rank": rank, "powers": [1] * n,
            "dimension_shift": 0, "lanes": [lane]}


def main():
    tirust_bin, iregi_bin, output = sys.argv[1:4]
    records = []
    for label, shifts, masses, rank in CASES:
        case = case_record(label, shifts, masses, rank)
        lanes = case["lanes"]
        tirust = run.Engine([tirust_bin], 199)
        t = tirust.request(run.tirust_wire(case, lanes, 0, 1, 1))
        tirust.close()
        entry = {"case": label, "n": case["n"], "rank": rank, "masses_squared": masses,
                 "tirust_status": t["lanes"][0]["status"] if t else "no result",
                 "tirust_engine": t.get("workspace_engine") if t else None,
                 "tirust_fallback_rows": t.get("fallback_rows") if t else None}
        tm = run.lane_moments(t, 0)
        for mode in (0, 1):
            iregi = run.Engine([iregi_bin], 199)
            r = iregi.request(run.iregi_wire(case, lanes, mode, 0, 1, 1))
            iregi.close()
            im = run.lane_moments(r, 0)
            key = run.MODES[mode]
            if im is None or tm is None:
                entry[f"iregi_{key}"] = "unavailable"
                continue
            flat = [tuple(z) for moment in im for z in moment]
            entry[f"tirust_vs_iregi_{key}"] = run.array_error(case, tm, flat)
        records.append(entry)
        print(json.dumps(entry), flush=True)
    Path(output).write_text(json.dumps({"cases": records}, indent=1) + "\n")


if __name__ == "__main__":
    main()

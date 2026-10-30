#!/usr/bin/env python3
"""Near-coplanar boxes (p3 = e_x + e_y + delta e_z, rank 4): public TIRust facade
versus original IREGI IBP/PV. usage: run from the repository root after build.py."""
import importlib.util, json, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("run", "validation/benchmark/direct-engine-20261030/run.py")
run = importlib.util.module_from_spec(spec); spec.loader.exec_module(run)
for delta in ["1/8", "1/64", "1/1024", "1/65536", "1/16777216", "0"]:
    case = {"id": "coplanar", "table": "ordinary", "n": 4, "rank": 4, "powers": [1]*4, "dimension_shift": 0,
            "lanes": [{"shifts": [["0","0","0","0"],["0","1","0","0"],["0","0","1","0"],["0","1","1",delta]],
                       "masses_squared": [["1","0"],["2","0"],["3","0"],["3","0"]], "mu": "3"}]}
    lanes = case["lanes"]
    e = run.Engine(["target/direct-engine-20261030/bin/tirust-direct-timing"], 199)
    t = e.request(run.tirust_wire(case, lanes, 0, 1, 1)); e.close()
    out = {"delta": delta, "tirust": t["lanes"][0]["status"], "fallback": t.get("fallback_rows")}
    tm = run.lane_moments(t, 0)
    ref = {}
    for mode in (0, 1):
        e = run.Engine(["target/direct-engine-20261030/bin/iregi-general"], 199)
        r = e.request(run.iregi_wire(case, lanes, mode, 0, 1, 1)); e.close()
        ref[mode] = run.lane_moments(r, 0)
        out[f"iregi_{run.MODES[mode]}"] = r["lanes"][0]["status"] if r else "STOP"
    flat = lambda m: [tuple(z) for x in m for z in x]
    if ref[0] and ref[1]:
        out["IBP_vs_PV"] = run.array_error(case, ref[1], flat(ref[0]))
    if tm and ref[0]:
        out["TIRust_vs_IBP"] = run.array_error(case, tm, flat(ref[0]))
    print(json.dumps(out), flush=True)

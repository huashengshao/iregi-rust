#!/usr/bin/env python3
"""Near-coplanar boxes against the quadruple-precision original IREGI build
(target/quad-iregi-source-audit/build-v6-001): quad IBP/PV, binary64 IREGI IBP, TIRust."""
import importlib.util, json, subprocess
spec = importlib.util.spec_from_file_location("run", "validation/benchmark/direct-engine-20261030/run.py")
run = importlib.util.module_from_spec(spec); spec.loader.exec_module(run)
QUAD = "target/quad-iregi-source-audit/build-v6-001/iregi-reference-quad"
def quad(delta, mode):
    rows = [("0","0","0","0"),("0","1","0","0"),("0","0","1","0"),("0","1","1",delta)]
    masses = ["1","2","3","3"]
    text = f"EVAL q tensor {mode} 4 4 0 3.0 0 1e-12\n" + "".join(
        " ".join(repr(float(eval(x))) for x in r) + f" {m}.0 0.0 1\n" for r, m in zip(rows, masses)) + "QUIT\n"
    out = subprocess.run([QUAD], input=text, capture_output=True, text=True, timeout=600).stdout
    res = [json.loads(l[7:]) for l in out.splitlines() if l.startswith("RESULT ")]
    m = res[0]["moments"] if res and res[0].get("moments") else None
    return [[[float(x) for x in z] for z in mom] for mom in m] if m else None
for delta in ["1/8", "1/64", "1/1024", "1/65536", "0"]:
    case = {"id": "c", "table": "ordinary", "n": 4, "rank": 4, "powers": [1]*4, "dimension_shift": 0,
            "lanes": [{"shifts": [["0","0","0","0"],["0","1","0","0"],["0","0","1","0"],["0","1","1",delta]],
                       "masses_squared": [["1","0"],["2","0"],["3","0"],["3","0"]], "mu": "3"}]}
    q_ibp, q_pv = quad(delta, 0), quad(delta, 1)
    flat = lambda m: [tuple(z) for x in m for z in x]
    out = {"delta": delta}
    if q_ibp and q_pv: out["quadIBP_vs_quadPV"] = run.array_error(case, q_pv, flat(q_ibp))
    e = run.Engine(["target/direct-engine-20261030/bin/iregi-general"], 199)
    r = e.request(run.iregi_wire(case, case["lanes"], 0, 0, 1, 1)); e.close()
    if q_ibp and run.lane_moments(r, 0): out["f64IBP_vs_quadIBP"] = run.array_error(case, run.lane_moments(r, 0), flat(q_ibp))
    e = run.Engine(["target/direct-engine-20261030/bin/tirust-direct-timing"], 199)
    t = e.request(run.tirust_wire(case, case["lanes"], 0, 1, 1)); e.close()
    if q_ibp and run.lane_moments(t, 0): out["TIRust_vs_quadIBP"] = run.array_error(case, run.lane_moments(t, 0), flat(q_ibp))
    print(json.dumps(out), flush=True)

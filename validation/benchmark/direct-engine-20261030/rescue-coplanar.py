#!/usr/bin/env python3
"""Direct-engine precision rescue on near-coplanar boxes, against the
quadruple-precision original IREGI build (target/quad-iregi-source-audit/build-v6-001).

Shifts 0, e_x, e_y, e_x+e_y+delta e_z with masses^2 (1,2,3,3) and mu = 3 at
ranks 4 and 6. Per delta: quad IBP and quad PV (their disagreement bounds the
reference), binary64 original IREGI IBP, and the TIRust public binary64 facade
(status, rescue tier, E/A against both quad modes). Read-only for the inputs;
writes one JSON line per point.

usage: rescue-coplanar.py TIRUST_DIRECT_TIMING_BINARY OUTPUT_JSONL [CPU]
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("run", HERE / "run.py")
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
QUAD = run.ROOT / "target/quad-iregi-source-audit/build-v6-001/iregi-reference-quad"
IREGI = run.ROOT / "target/direct-engine-20261030/bin/iregi-general"
DELTAS = ["1/8", "1/64", "1/256", "1/1024", "1/4096", "1/65536", "1/16777216", "0"]


def quad(delta, mode, rank, cpu):
    rows = [("0", "0", "0", "0"), ("0", "1", "0", "0"), ("0", "0", "1", "0"), ("0", "1", "1", delta)]
    masses = ["1", "2", "3", "3"]
    text = f"EVAL q tensor {mode} 4 {rank} 0 3.0 0 1e-12\n" + "".join(
        " ".join(run.decimal(x) for x in r) + f" {m}.0 0.0 1\n" for r, m in zip(rows, masses)) + "QUIT\n"
    out = subprocess.run(["taskset", "-c", str(cpu), str(QUAD)], input=text, capture_output=True, text=True,
                         timeout=3600).stdout
    res = [json.loads(line[7:]) for line in out.splitlines() if line.startswith("RESULT ")]
    moments = res[0]["moments"] if res and res[0].get("moments") else None
    return [[[float(x) for x in z] for z in moment] for moment in moments] if moments else None


def main():
    binary, output = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    cpu = int(sys.argv[3]) if len(sys.argv) > 3 else 199
    flat = lambda m: [tuple(z) for x in m for z in x]
    with output.open("w") as sink:
        sink.write(json.dumps({"tirust_binary": str(binary.relative_to(run.ROOT)),
                               "tirust_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                               "quad_sha256": hashlib.sha256(QUAD.read_bytes()).hexdigest(),
                               "iregi_sha256": hashlib.sha256(IREGI.read_bytes()).hexdigest()}) + "\n")
        for rank in (4, 6):
            for delta in DELTAS:
                case = {"id": "c", "table": "ordinary", "n": 4, "rank": rank, "powers": [1] * 4,
                        "dimension_shift": 0,
                        "lanes": [{"shifts": [["0", "0", "0", "0"], ["0", "1", "0", "0"], ["0", "0", "1", "0"],
                                              ["0", "1", "1", delta]],
                                   "masses_squared": [["1", "0"], ["2", "0"], ["3", "0"], ["3", "0"]], "mu": "3"}]}
                q_ibp, q_pv = quad(delta, 0, rank, cpu), quad(delta, 1, rank, cpu)
                out = {"rank": rank, "delta": delta}
                if q_ibp and q_pv:
                    out["quadIBP_vs_quadPV"] = run.array_error(case, q_pv, flat(q_ibp))
                engine = run.Engine([str(IREGI)], cpu)
                r = engine.request(run.iregi_wire(case, case["lanes"], 0, 0, 1, 1))
                engine.close()
                if q_ibp and run.lane_moments(r, 0):
                    out["f64IBP_vs_quadIBP"] = run.array_error(case, run.lane_moments(r, 0), flat(q_ibp))
                engine = run.Engine([str(binary)], cpu)
                t = engine.request(run.tirust_wire(case, case["lanes"], 2, 3, 3))
                engine.close()
                lane = t["lanes"][0]
                out["tirust_status"] = lane["status"]
                out["tirust_diagnostics"] = lane.get("diagnostics")
                out["tirust_precision_rescue"] = t.get("precision_rescue")
                out["tirust_symbolic_rows"] = t.get("symbolic_rows")
                out["tirust_ns_per_call"] = t["total_ns"]
                moments = run.lane_moments(t, 0)
                if q_ibp and moments:
                    out["TIRust_vs_quadIBP"] = run.array_error(case, moments, flat(q_ibp))
                if q_pv and moments:
                    out["TIRust_vs_quadPV"] = run.array_error(case, moments, flat(q_pv))
                sink.write(json.dumps(out) + "\n")
                sink.flush()
                print(json.dumps({k: v for k, v in out.items() if k != "tirust_diagnostics"}), flush=True)


if __name__ == "__main__":
    main()

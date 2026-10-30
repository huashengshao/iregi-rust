#!/usr/bin/env python3
"""Binary64 stability study: TIRust, original IREGI and COLLIER against a
quadruple-precision reference, in the style of Hirschi and Peraro,
arXiv:1604.01363, figs. 2-4.

For every point of points.json (make-points.py) and every code the complete
tensor array (all Cartesian moments, all four Laurent slots) is compared with
the reference through the report's accuracy measure E/A (dimensionally
rescaled whole-array max discrepancy, weights mu^(rank+4-2N)).

Codes (all binary64 inputs and outputs):
  tirust          public TIRust default (direct engine; lanes it refuses are
                  rerun at higher precision automatically)
  tirust-direct64 TIRust direct engine in binary64 alone (refusals reported)
  iregi-ibp/-pv   original IREGI, binary64, IBP and PV modes
  collier-coli/-dd COLLIER 1.2.10, binary64, COLI and DD branches
                  (requested accuracy 1e-10, critical 1e-3, TenRed 6); lanes
                  COLLIER flags as inaccurate still return values, which are
                  scored, and the flag is counted.
Reference: quadruple-precision original IREGI, IBP and PV modes on the same
binary64 inputs. A point's reference is the IBP array when the two quad modes
agree to E/A <= 1e-20; otherwise the quad mode that agrees with the TIRust
256-bit direct evaluation to 1e-20 is used, and points where neither agrees
are excluded (counted). Only per-point E/A values are kept (deltas.jsonl);
raw arrays stay under target/.

usage: run.py POINTS_JSON OUTPUT_DIR [--workers N] [--chunk N] [--only ID]
"""
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BIN = ROOT / "target/stability-20261030/bin"
TIRUST = BIN / "tirust-stability"
COLLIER = BIN / "collier-physical"
IREGI = ROOT / "target/direct-engine-20261030/bin/iregi-general"
QUAD = ROOT / "target/quad-iregi-source-audit/build-v6-001/iregi-reference-quad"
REFERENCE_AGREEMENT = 1e-20
COLLIER_CONFIG = {"requested_accuracy": "1e-10", "critical_accuracy": "1e-3", "direct_tensor_threshold": 6,
                  "argument_permutation": 0}


def basis(rank):
    out = []
    for r in range(rank + 1):
        for t in range(r, -1, -1):
            for x in range(r - t, -1, -1):
                for y in range(r - t - x, -1, -1):
                    out.append((t, x, y, r - t - x - y))
    return out


def array_error(moments, reference, rank, n, mu):
    """E/A over all moments and Laurent slots; NaN if any entry is nonfinite."""
    if moments is None or reference is None:
        return None
    base = 4 - 2 * n
    error = amplitude = 0.0
    for m, monomial in enumerate(basis(rank)):
        weight = mu ** (sum(monomial) + base)
        for slot in range(4):
            a, b = moments[m][slot], reference[m][slot]
            if b is None or None in b:
                return None
            if a is None or None in a:
                return float("nan")
            a = (float(a[0]), float(a[1]))
            b = (float(b[0]), float(b[1]))
            if not all(math.isfinite(x) for x in a):
                return float("nan")
            error = max(error, math.hypot(a[0] - b[0], a[1] - b[1]) / weight)
            amplitude = max(amplitude, math.hypot(b[0], b[1]) / weight)
    return error / amplitude if amplitude else (0.0 if error == 0 else float("inf"))


def results(argv, text, timeout=7200):
    out = subprocess.run(argv, input=text, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    return [json.loads(line[7:]) for line in out.stdout.splitlines() if line.startswith("RESULT ")], out


def rows(points, masses):
    return "".join(" ".join(repr(x) for x in shift) + f" ({m!r},0.0) 1\n"
                   for point in points for shift, m in zip(point, masses))


def iregi(points, integral, mode):
    n, rank, mu = integral["n"], integral["rank"], integral["mu"]
    head = f"BENCH s tensor {mode} {n} {rank} 0 {mu!r} {len(points)} 0 1 1\n"
    res, _ = results([str(IREGI)], head + rows(points, integral["masses_squared"]) + "QUIT\n")
    return res[0]["lanes"] if res else None


def collier(points, integral, mode):
    n, rank, mu = integral["n"], integral["rank"], integral["mu"]
    c = COLLIER_CONFIG
    head = (f"BENCH s {mode} {n} {rank} {mu!r} {len(points)} 0 1 1 {c['requested_accuracy']} "
            f"{c['critical_accuracy']} {c['direct_tensor_threshold']} {c['argument_permutation']}\n")
    text = head + "".join(" ".join(repr(x) for x in shift) + f" ({m!r},0.0)\n"
                          for point in points for shift, m in zip(point, integral["masses_squared"]))
    res, _ = results([str(COLLIER)], text + "QUIT\n")
    return res[0]["lanes"] if res else None


def quad(points, integral, mode):
    n, rank, mu = integral["n"], integral["rank"], integral["mu"]
    text = ""
    for point in points:
        text += f"EVAL q tensor {mode} {n} {rank} 0 {mu!r} 0 1e-12\n" + "".join(
            " ".join(repr(x) for x in shift) + f" {m!r} 0.0 1\n"
            for shift, m in zip(point, integral["masses_squared"]))
    res, _ = results([str(QUAD)], text + "QUIT\n")
    out = [r.get("moments") for r in res]
    return out + [None] * (len(points) - len(out))


def tirust(points, integral):
    with tempfile.TemporaryDirectory() as tmp:
        source, sink = Path(tmp) / "points.json", Path(tmp) / "out.jsonl"
        chunk = dict(integral, points=points)
        source.write_text(json.dumps({"integrals": [chunk]}))
        subprocess.run([str(TIRUST), str(source), str(sink)], check=True, capture_output=True, timeout=7200)
        return [json.loads(line) for line in sink.read_text().splitlines()]


def lane_values(lane):
    """Returned values (also of flagged lanes) and whether the lane was flagged."""
    if lane is None:
        return None, True
    if lane.get("status") == "success":
        return lane.get("moments"), False
    return lane.get("diagnostic_moments"), True


def chunk_job(integral, start, points):
    n, rank, mu = integral["n"], integral["rank"], integral["mu"]
    q_ibp, q_pv = quad(points, integral, 0), quad(points, integral, 1)
    t = tirust(points, integral)
    codes = {}
    for mode, name in ((0, "iregi-ibp"), (1, "iregi-pv")):
        codes[name] = iregi(points, integral, mode)
    for mode, name in ((1, "collier-coli"), (2, "collier-dd")):
        codes[name] = collier(points, integral, mode)
    records = []
    for k in range(len(points)):
        record = {"integral": integral["id"], "index": start + k}
        d256 = t[k]["direct256"]["moments"]
        e = lambda a, b: array_error(a, b, rank, n, mu)
        spread = {"quadIBP_quadPV": e(q_pv[k], q_ibp[k]), "direct256_quadIBP": e(d256, q_ibp[k]),
                  "direct256_quadPV": e(d256, q_pv[k])}
        record["reference_checks"] = spread
        ok = lambda x: x is not None and math.isfinite(x) and x <= REFERENCE_AGREEMENT
        if ok(spread["quadIBP_quadPV"]):
            reference, record["reference"] = q_ibp[k], "quad-ibp (quad modes agree)"
        elif ok(spread["direct256_quadIBP"]):
            reference, record["reference"] = q_ibp[k], "quad-ibp (agrees with 256-bit)"
        elif ok(spread["direct256_quadPV"]):
            reference, record["reference"] = q_pv[k], "quad-pv (agrees with 256-bit)"
        else:
            record["reference"] = None
            records.append(record)
            continue
        delta, flagged = {}, {}
        default = t[k]["default"]
        delta["tirust"] = e(default["moments"], reference) if default["status"] == "success" else None
        flagged["tirust"] = bool(default.get("fallback_used"))
        record["tirust_diagnostics"] = default.get("diagnostics")
        direct = t[k]["direct64"]
        delta["tirust-direct64"] = e(direct["moments"], reference) if direct["status"] == "success" else None
        flagged["tirust-direct64"] = direct["status"] != "success"
        for name, lanes in codes.items():
            values, flag = lane_values(lanes[k] if lanes else None)
            delta[name] = e(values, reference) if values is not None else None
            flagged[name] = flag
        record["delta"], record["flagged"] = delta, flagged
        records.append(record)
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("points", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--chunk", type=int, default=50)
    parser.add_argument("--only", default=None)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    data = json.loads(args.points.read_text())
    with ProcessPoolExecutor(args.workers) as pool:
        for integral in data["integrals"]:
            if args.only and integral["id"] != args.only:
                continue
            sink = args.output / f"deltas-{integral['id']}.jsonl"
            done = set()
            if sink.exists():
                done = {json.loads(line)["index"] for line in sink.read_text().splitlines()}
            points = integral["points"]
            jobs = [pool.submit(chunk_job, {k: v for k, v in integral.items() if k != "points"}, start,
                                points[start:start + args.chunk])
                    for start in range(0, len(points), args.chunk) if start not in done]
            with sink.open("a") as out:
                for future in as_completed(jobs):
                    for record in future.result():
                        out.write(json.dumps(record) + "\n")
                    out.flush()
            print(f"{integral['id']}: {len(points)} points", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()

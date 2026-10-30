#!/usr/bin/env python3
"""Condense the stability capture into the report snapshot (summary.json).

Reads deltas-*.jsonl (per-point E/A of every code against the reference) and
writes, per integral and code, the cumulative stability profile
fraction(Delta) = #{points with E/A > Delta, or no array} / #{points with a
reference} on a grid log10(Delta) = -17.0, -16.9, ..., 0.0, as in
arXiv:1604.01363 figs. 2-4; plus the fraction without an array, the fraction
flagged by the code itself, quantiles, and the reference checks.

usage: summarize.py CAPTURE_DIR POINTS_JSON BUILD_JSON OUTPUT_JSON
"""
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

CODES = [
    ("tirust", "TIRust (default: automatic precision rescue)"),
    ("tirust-direct64", "TIRust direct engine, binary64 only"),
    ("iregi-ibp", "IREGI IBP"),
    ("iregi-pv", "IREGI PV"),
    ("collier-coli", "COLLIER COLI"),
    ("collier-dd", "COLLIER DD"),
]
GRID = [round(-17 + 0.1 * k, 1) for k in range(171)]


def main():
    capture, points_path, build_path, output = map(Path, sys.argv[1:5])
    points = json.loads(points_path.read_text())
    build = json.loads(build_path.read_text())
    integrals = []
    for integral in points["integrals"]:
        records = [json.loads(line) for line in (capture / f"deltas-{integral['id']}.jsonl").read_text().splitlines()]
        records.sort(key=lambda r: r["index"])
        usable = [r for r in records if r.get("reference")]
        checks = {key: max((r["reference_checks"][key] for r in usable
                            if r["reference_checks"].get(key) is not None), default=None)
                  for key in ("quadIBP_quadPV", "direct256_quadIBP", "direct256_quadPV")}
        out = {
            "id": integral["id"], "label": integral["label"], "n": integral["n"], "rank": integral["rank"],
            "points": len(integral["points"]), "evaluated": len(records), "with_reference": len(usable),
            "reference_rules": {rule: sum(1 for r in usable if r["reference"] == rule)
                                for rule in sorted({r["reference"] for r in usable})},
            "max_reference_disagreement": checks,
            "codes": [],
        }
        for code, label in CODES:
            deltas = [r["delta"].get(code) for r in usable]
            values = sorted(d for d in deltas if d is not None and math.isfinite(d))
            missing = sum(1 for d in deltas if d is None or not math.isfinite(d))
            total = len(usable)
            curve = []
            for x in GRID:
                threshold = 10.0 ** x
                worse = missing + sum(1 for d in values if d > threshold)
                curve.append(round(worse / total, 6) if total else None)
            q = (lambda p: values[min(len(values) - 1, int(p * len(values)))] if values else None)
            entry = {"code": code, "label": label, "curve": curve, "no_array": missing,
                     "flagged": sum(1 for r in usable if r["flagged"].get(code)),
                     "median": statistics.median(values) if values else None,
                     "p99": q(0.99), "max": values[-1] if values else None,
                     "above_1e-3": missing + sum(1 for d in values if d > 1e-3)}
            if code == "tirust":
                tiers = {}
                for r in usable:
                    for note in r.get("tirust_diagnostics") or []:
                        if note.endswith(": accepted") and "bits" in note:
                            bits = note.split(" at ")[1].split(" bits")[0]
                            tiers[bits] = tiers.get(bits, 0) + 1
                entry["rescued_by_bits"] = tiers
            out["codes"].append(entry)
        integrals.append(out)
    snapshot = {
        "schema_version": 1,
        "campaign": "stability-20261030",
        "setup": {k: points[k] for k in ("seed", "sqrt_s", "mt2", "mh", "mu", "pt_min", "dr_min")},
        "points_sha256": hashlib.sha256(points_path.read_bytes()).hexdigest(),
        "binaries": {name: build[name]["sha256"] for name in ("tirust", "iregi", "collier", "quad_reference")},
        "tirust_git_head": build["tirust"]["git_head"],
        "grid_log10": GRID,
        "accuracy_metric": "E/A: dimensionally rescaled whole-array max discrepancy over all Cartesian moments and "
                           "four Laurent slots (weights mu^(rank+4-2N)) against quadruple-precision original IREGI.",
        "integrals": integrals,
    }
    output.write_text(json.dumps(snapshot, indent=1) + "\n")


if __name__ == "__main__":
    main()

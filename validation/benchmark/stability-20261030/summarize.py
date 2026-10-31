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
    ("tirust-binary64", "TIRust binary64 only (rescue disabled; refusals: no array)"),
    ("tirust-binary64-r20", "TIRust binary64 only, accuracy request 2^-20"),
    ("iregi-ibp", "IREGI IBP"),
    ("iregi-pv", "IREGI PV"),
    ("collier-coli", "COLLIER COLI"),
    ("collier-dd", "COLLIER DD"),
]
# Captures 001-004 derived "binary64 only" from the default path (its array
# unless rerun at higher precision; capture 004: sub-boxes of such lanes may
# be double-double from the partial rescue). Capture 005 on: the facade with
# the precision rescue disabled, at the requests 2^-34 and 2^-20.
LEGACY_BINARY64_LABEL = "TIRust default without a full rescue (sub-boxes may be double-double)"
GRID = [round(-17 + 0.1 * k, 1) for k in range(171)]
# Contracted dense random numerator (capture 003 on): the array codes and
# NinjaRS, which integrates the numerator directly (integrand reduction).
CONTRACTED_CODES = CODES + [("ninjars", "NinjaRS (integrand reduction, binary64 fast engine)")]


def main():
    capture, points_path, build_path, output = map(Path, sys.argv[1:5])
    points = json.loads(points_path.read_text())
    build = json.loads(build_path.read_text())
    integrals = []
    for integral in points["integrals"]:
        deltas_path = capture / f"deltas-{integral['id']}.jsonl"
        records = [json.loads(line) for line in deltas_path.read_text().splitlines()]
        records.sort(key=lambda r: r["index"])
        usable = [r for r in records if r.get("reference")]
        confirmations = [min(v for v in (r["reference_checks"]["direct256_quadIBP"],
                                         r["reference_checks"]["direct256_quadPV"]) if v is not None)
                         for r in usable if r["reference"].startswith("256-bit")]
        checks = {"confirmation_max": max(confirmations, default=None),
                  "confirmation_median": statistics.median(confirmations) if confirmations else None,
                  "quad_modes_disagree_above_1e-12": sum(
                      1 for r in records if (r["reference_checks"]["quadIBP_quadPV"] or 0) > 1e-12)}
        weak = [r for r in usable if r["reference"].startswith("256-bit")
                and min(v for v in (r["reference_checks"]["direct256_quadIBP"],
                                    r["reference_checks"]["direct256_quadPV"]) if v is not None) > 1e-12]
        checks["confirmed_above_1e-12"] = len(weak)
        checks["of_which_collier_closer_to_256bit"] = sum(
            1 for r in weak if r["arbitration"]["collier_vs_reference"] is not None
            and r["arbitration"]["collier_vs_quad"] is not None
            and r["arbitration"]["collier_vs_reference"] < r["arbitration"]["collier_vs_quad"])
        out = {
            "id": integral["id"], "label": integral["label"], "n": integral["n"], "rank": integral["rank"],
            "points": len(integral["points"]), "evaluated": len(records), "with_reference": len(usable),
            "capture_sha256": hashlib.sha256(deltas_path.read_bytes()).hexdigest(),
            "reference_rules": {rule: sum(1 for r in usable if r["reference"] == rule)
                                for rule in sorted({r["reference"] for r in usable})},
            "reference_checks": checks,
            "codes": [],
        }
        present = {code for r in usable for code in r["delta"]}
        legacy = "tirust-binary64-r20" not in present
        scored = any("binary64_best_effort" in r for r in usable)
        for code, label in CODES:
            if code not in present:
                continue
            if code == "tirust-binary64" and legacy:
                label = LEGACY_BINARY64_LABEL
            if code.startswith("tirust-binary64") and scored:
                label = label.replace("refusals: no array", "refused lanes: best-effort array")
                if code == "tirust-binary64-r20":
                    label += " (refused lanes: best-effort array)"
            deltas = [r["delta"].get(code) for r in usable]
            values = sorted(d for d in deltas if d is not None and math.isfinite(d))
            missing = sum(1 for d in deltas if d is None or not math.isfinite(d))
            total = len(usable)
            def profile(deltas):
                finite = [d for d in deltas if d is not None and math.isfinite(d)]
                absent = len(deltas) - len(finite)
                return [round((absent + sum(1 for d in finite if d > 10.0 ** x)) / total, 6) if total else None
                        for x in GRID]
            curve = profile(deltas)
            curve_quad = profile([r["delta_quad"].get(code) for r in usable])
            q = (lambda p: values[min(len(values) - 1, int(p * len(values)))] if values else None)
            difference = max((abs(a - b) for x, a, b in zip(GRID, curve, curve_quad)
                              if x >= -14 and a is not None and b is not None), default=None)
            entry = {"code": code, "label": label, "curve": curve, "no_array": missing,
                     "curve_difference_vs_quad_reference_above_1e-14": difference,
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
            if code.startswith("tirust-binary64") and scored:
                entry["best_effort"] = sum(1 for r in usable if (r.get("binary64_best_effort") or {}).get(code))
            # Lanes the checked binary64 retry kept below the a priori gate.
            notes_key = {"tirust": "tirust_diagnostics", "tirust-binary64": "tirust_binary64_diagnostics"}.get(code)
            if notes_key and not legacy:
                entry["checked_kept"] = sum(
                    1 for r in usable
                    if any(note.startswith("binary64 below the conditioning gate: kept") for note in r.get(notes_key) or []))
                entry["expansion_kept"] = sum(
                    1 for r in usable
                    if any(note.startswith("binary64 small-Gram expansion: kept") for note in r.get(notes_key) or []))
            out["codes"].append(entry)
        if any("contracted" in r for r in usable):
            out["contracted_codes"] = []
            contracted_present = {code for r in usable for code in (r.get("contracted") or {})}
            for code, label in CONTRACTED_CODES:
                if code not in contracted_present:
                    continue
                if code == "tirust-binary64" and legacy:
                    label = LEGACY_BINARY64_LABEL
                deltas = [(r.get("contracted") or {}).get(code) for r in usable]
                finite = sorted(d for d in deltas if d is not None and math.isfinite(d))
                absent = len(deltas) - len(finite)
                total = len(usable)
                curve = [round((absent + sum(1 for d in finite if d > 10.0 ** x)) / total, 6) for x in GRID]
                q = (lambda p: finite[min(len(finite) - 1, int(p * len(finite)))] if finite else None)
                out["contracted_codes"].append({
                    "code": code, "label": label, "curve": curve, "no_value": absent,
                    "median": statistics.median(finite) if finite else None, "p99": q(0.99),
                    "max": finite[-1] if finite else None,
                    "above_1e-3": absent + sum(1 for d in finite if d > 1e-3)})
        integrals.append(out)
    snapshot = {
        "schema_version": 1,
        "campaign": "stability-20261030",
        "setup": {k: points[k] for k in ("seed", "sqrt_s", "mt2", "mh", "mu", "pt_min", "dr_min")},
        "points_sha256": hashlib.sha256(points_path.read_bytes()).hexdigest(),
        "binaries": {name: build[name]["sha256"] for name in ("tirust", "iregi", "collier", "quad_reference", "ninjars")
                     if name in build},
        "tirust_git_head": build["tirust"]["git_head"],
        "grid_log10": GRID,
        "accuracy_metric": "E/A: dimensionally rescaled whole-array max discrepancy over all Cartesian moments and "
                           "four Laurent slots (weights mu^(rank+4-2N)) against quadruple-precision original IREGI.",
        "integrals": integrals,
    }
    output.write_text(json.dumps(snapshot, indent=1) + "\n")


if __name__ == "__main__":
    main()

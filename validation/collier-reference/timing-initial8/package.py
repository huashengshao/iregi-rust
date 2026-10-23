"""Reproduce the compact first COLLIER/IREGI timing evidence package.

This only packages the already completed fixed cohort. It never runs a kernel.
The exact raw response archive retains every measured component and failure.
"""
import collections
import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path.cwd()
OUTPUT = ROOT / "validation/collier-reference/timing-initial8"
RAW = ROOT / "target/collier-reference/timing-attempt001/results.json"
EXPECTED = "c5b42f2ded5cd4296f2768748eba8218c77749febe4145be7243cbed255237dd"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def main():
    contents = RAW.read_bytes()
    assert hashlib.sha256(contents).hexdigest() == EXPECTED
    data = json.loads(contents)
    assert data["status"] == "passed" and data["source_unchanged"] and data["binaries_unchanged"]
    assert len(data["rows"]) == 8 and data["protocol"]["blocks"] == 41
    OUTPUT.mkdir(exist_ok=True)
    compressed = OUTPUT / "raw-results.json.gz"
    compressed.write_bytes(gzip.compress(contents, compresslevel=9, mtime=0))
    assert gzip.decompress(compressed.read_bytes()) == contents
    rows = []
    measured_slots = prepost_slots = pairs = 0
    for source in data["rows"]:
        assert source["status"] == "measured"
        assert source["correctness"]["status"] == "passed"
        assert source["postflight"]["correctness"]["status"] == "passed"
        assert len(source["blocks"]) == 41 and len(source["warmup_blocks"]) == 5
        assert len(source["calibration"]) <= 8
        orders = collections.Counter(tuple(block["order"]) for block in source["blocks"])
        assert orders == {("collier", "iregi"): 21, ("iregi", "collier"): 20}
        assert all(block["correctness"]["status"] == "passed" for block in source["blocks"])
        batch = source["batch_width"]
        rows.append({"id": source["id"], "n": source["n"], "rank": source["rank"], "batch_width": batch,
                     "status": source["status"], "numerical_status": source["correctness"]["status"],
                     "maximum_normalized_error": source["correctness"]["max_error"],
                     "postflight_maximum_normalized_error": source["postflight"]["correctness"]["max_error"],
                     "collier_median_ns_per_batch": source["timings"]["collier"]["median_ns"],
                     "iregi_median_ns_per_batch": source["timings"]["iregi"]["median_ns"],
                     "collier_median_us_per_point": source["timings"]["collier"]["median_ns"] / 1000 / batch,
                     "iregi_median_us_per_point": source["timings"]["iregi"]["median_ns"] / 1000 / batch,
                     "ratio": source["ratio"]["median"], "ratio_ci99": source["ratio"]["ci99"],
                     "relative_ci_width": source["ratio"]["relative_ci_width"],
                     "performance_status": source["ratio"]["gate"],
                     "minimum_observed_block_ms": source["minimum_observed_block_ms"],
                     "iterations_per_block": source["iterations_per_block"],
                     "calibration_rounds": len(source["calibration"]), "paired_blocks": 41,
                     "paired_order_counts": [orders[("collier", "iregi")], orders[("iregi", "collier")]]})
        pairs += len(source["blocks"])
        for block in source["blocks"]:
            for response in block["responses"].values():
                measured_slots += sum(len(lane["moments"]) * 4 for lane in response["lanes"])
        for phase in [source["pilot"], source["postflight"]["responses"]]:
            for response in phase.values():
                prepost_slots += sum(len(lane["moments"]) * 4 for lane in response["lanes"])
    counts = dict(collections.Counter(row["performance_status"] for row in rows))
    assert counts == {"inconclusive-short-block": 1, "improvement": 7}
    summary = {"schema_version": 1, "kind": "original-iregi-vs-collier-initial-eight-families",
               "status": "complete-with-one-inconclusive-family", "elapsed_seconds": data["elapsed_seconds"],
               "comparison": "COLLIER COLI-mode1 / original IREGI Hybrid-mode2; this is not the Rust performance gate",
               "scope": "Massive Euclidean ordinary undotted N2/N3 ranks0/1, batches1/32; N4..N7 and broader shared domain remain pending",
               "normalization": "Complete native [UV single, IR single, IR double, finite] and all requested symmetric Cartesian moments",
               "ir_scope": "Positive internal squared masses; IR slots zero, checked by separate untimed delta-parameter probes for every pre/post lane",
               "units": "Raw medians are ns/batch; displayed us/point = ns/batch /1000/batch_width; batch32 is amortized throughput",
               "ratio_definition": "Median of paired COLLIER/IREGI block ratios; not ratio of the separately displayed medians",
               "cpu": 254, "cache_policy": data["protocol"]["cache_policy"],
               "compiler": "GNU Fortran15.2.0, -O3; fast-math disabled in both reference builds",
               "timing_boundary": "COLLIER invariant/momentum construction + public full tensor call + native conversion + status checks; IREGI mass setup + tensor call + status checks + cache disposal; transport and pole probes excluded",
               "protocol": data["protocol"], "counts": counts,
               "paired_blocks_total": pairs, "measured_complex_slots_both_engines": measured_slots,
               "pre_post_complex_slots_both_engines": prepost_slots,
               "maximum_normalized_array_error": max(row["maximum_normalized_error"] for row in rows),
               "source_and_binary_guards_unchanged": True,
               "quiet_window": {"path": "validation/benchmark-quiet/20261023d/collier-window.json",
                                "sha256": digest(ROOT / "validation/benchmark-quiet/20261023d/collier-window.json")},
               "quiet_completion": {"path": "validation/benchmark-quiet/20261023d/completion.json",
                                    "sha256": digest(ROOT / "validation/benchmark-quiet/20261023d/completion.json")},
               "raw": {"path": str(compressed.relative_to(ROOT)), "sha256": digest(compressed),
                       "uncompressed_sha256": EXPECTED, "uncompressed_bytes": len(contents),
                       "compression": "deterministic gzip, level9, mtime0"}, "rows": rows}
    write(OUTPUT / "summary.json", summary)
    bindings = [OUTPUT / "package.py", OUTPUT / "summary.json", compressed]
    bindings += [ROOT / path for path in [
        "validation/collier-reference/qualification-v3.json",
        "validation/collier-reference/timing-readiness-v3.json",
        "validation/checkpoint-audits/2026-10-23-collier-v3-protocol-review.json",
        "validation/benchmark-quiet/20261023d/collier-window.json",
        "validation/benchmark-quiet/20261023d/completion.json",
        "docs/research/collier-1.2.10-manifest.json",
        "docs/research/collier-1.2.10-audit.md",
        "validation/collier-reference/convention-review.md",
        "validation/collier-reference/ready-initial8-v3/build.json",
        "validation/collier-reference/ready-initial8-v3/correctness.json",
        "validation/collier-reference/ready-initial8-v3/protocol-tests.log"]]
    for name, expected in data["identity"]["source_sha256"].items():
        frozen = ROOT / "validation/collier-reference/ready-initial8-v3/producer" / name
        assert digest(frozen) == expected
        bindings.append(frozen)
    qualification = {"schema_version": 1, "status": "complete-with-one-inconclusive-family",
                     "numerical_status": "all-eight-families-passed", "performance_counts": counts,
                     "timing_attempts": 1, "repeated_or_omitted_families": False,
                     "short_block": {"id": "n2-r0-massive", "batch_width": 1,
                                     "observed_minimum_ms": rows[0]["minimum_observed_block_ms"],
                                     "required_minimum_ms": 100,
                                     "outcome": "inconclusive retained; no rerun"},
                     "paired_blocks": pairs, "source_binary_unchanged": True,
                     "files": {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(bindings))}}
    write(OUTPUT / "qualification.json", qualification)
    print(json.dumps({"summary_sha256": digest(OUTPUT / "summary.json"),
                      "qualification_sha256": digest(OUTPUT / "qualification.json"),
                      "raw_gzip_bytes": compressed.stat().st_size,
                      "measured_complex_slots_both_engines": measured_slots,
                      "pre_post_complex_slots_both_engines": prepost_slots, "counts": counts}))


if __name__ == "__main__":
    main()

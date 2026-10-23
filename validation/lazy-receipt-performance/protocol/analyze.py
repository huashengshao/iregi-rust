#!/usr/bin/env python3
"""Summarize paired diagnostic timings; never pool unlike workloads."""
import csv
import hashlib
import json
import math
import pathlib
import random
import re
import statistics

directory = pathlib.Path(__file__).resolve().parent
digest = lambda path: hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
qualification = json.loads((directory / "performance-run.json").read_text())
assert qualification["status"] == "passed" and qualification["provenance_qualified"]
assert qualification["exit_code"] == 0 and not qualification["timed_out"]
assert qualification["cases_passed"] == 14
assert digest(directory / "performance.csv") == qualification["raw_csv_sha256"]
assert digest(pathlib.Path(__file__)) == qualification["analysis_source_sha256"]
assert digest(directory / "performance.log") == qualification["log_sha256"]
assert digest(directory / "preregistration.json") == qualification["preregistration_sha256"]
assert digest(directory / "protocol.py") == qualification["protocol_source_sha256"]
from protocol import parse_calibration, parse_measurements

calibration = parse_calibration((directory / "performance.log").read_text())
groups = parse_measurements((directory / "performance.csv").read_text(), calibration)

rng = random.Random(14050301)
results = []
for (workload, rows), blocks in sorted(groups.items()):
    assert set(blocks) == set(range(41)), (workload, rows, sorted(blocks))
    assert all(set(block) == {"baseline", "candidate"} for block in blocks.values())
    old = [block["baseline"] for _, block in sorted(blocks.items())]
    new = [block["candidate"] for _, block in sorted(blocks.items())]
    logs = [math.log(a / b) for a, b in zip(old, new)]
    samples = sorted(
        math.exp(statistics.median(rng.choices(logs, k=len(logs))))
        for _ in range(20000)
    )
    interval = [samples[100], samples[19899]]
    median_speedup = math.exp(statistics.median(logs))
    latency_ratio = 1.0 / median_speedup
    latency_interval = [1.0 / interval[1], 1.0 / interval[0]]
    relative_width = (latency_interval[1] - latency_interval[0]) / latency_ratio
    narrow = relative_width <= 0.02
    results.append({
        "workload": workload,
        "rows": rows,
        "paired_blocks": len(blocks),
        "baseline_median_ns_per_batch": statistics.median(old),
        "candidate_median_ns_per_batch": statistics.median(new),
        "median_paired_speedup": median_speedup,
        "candidate_over_baseline_latency_ratio": latency_ratio,
        "latency_ratio_ci99": latency_interval,
        "relative_ci_width": relative_width,
        "ci_width_qualified": narrow,
        "classification": ("inconclusive-noise" if not narrow else "improvement" if latency_interval[1] < 1 else "regression" if latency_interval[0] > 1 else "parity"),
        "paired_bootstrap_99_percent_interval": interval,
        "direction_without_width_gate": (
            "candidate faster" if interval[0] > 1 else
            "candidate slower" if interval[1] < 1 else
            "unresolved at 99 percent"
        ),
    })
output = {
    "scope": "New optimized eager-final-e23 versus lazy-receipt f64 cohort with identical accepted current shared masters and unchanged opt3 numerical closure; includes flattened mixed Dual; N5 retry remains inactive; not an IREGI reference performance benchmark",
    "method": "41 alternating paired blocks after retained200ms calibration, median log ratio, 20000 paired bootstrap resamples, deterministic seed14050301, percentile99 interval",
    "speedup_definition": "baseline time / candidate time",
    "classification_gate": "99% bootstrap interval width <=2% of median candidate/baseline latency ratio; otherwise inconclusive-noise",
    "results": results,
}
(directory / "performance-analysis.json").write_text(json.dumps(output, indent=2) + "\n")
print(json.dumps(output, indent=2))

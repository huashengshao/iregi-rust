#!/usr/bin/env python3
"""Summarize paired diagnostic timings; never pool unlike workloads."""
import csv
import json
import math
import pathlib
import random
import statistics

directory = pathlib.Path(__file__).resolve().parent
groups = {}
with (directory / "performance.csv").open() as stream:
    for row in csv.DictReader(stream):
        key = row["workload"], int(row["rows"])
        block = groups.setdefault(key, {}).setdefault(int(row["block"]), {})
        value = float(row["ns_per_batch"])
        assert math.isfinite(value) and value > 0, row
        assert row["implementation"] not in block, "duplicate implementation/block"
        assert row["implementation"] in {"baseline", "candidate"}, row
        block[row["implementation"]] = value

assert set(groups) == {(name, rows) for name in ["n1-rank0", "n1-rank7", "n2-rank1", "n2-rank3", "n3-rank1", "n3-rank3"] for rows in [1, 32]}, "incomplete workload matrix"

rng = random.Random(14050301)
results = []
for (workload, rows), blocks in sorted(groups.items()):
    assert set(blocks) == set(range(21)), (workload, rows, sorted(blocks))
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
    "scope": "Isolated f64 lane guard-context reuse with matched direct-rustc builds and the same guards; not full reference-code acceptance benchmark",
    "method": "21 alternating paired blocks, median log ratio, 20000 paired bootstrap resamples, deterministic seed14050301, percentile99 interval",
    "speedup_definition": "baseline time / candidate time",
    "classification_gate": "99% bootstrap interval width <=2% of median candidate/baseline latency ratio; otherwise inconclusive-noise",
    "results": results,
}
(directory / "performance-analysis.json").write_text(json.dumps(output, indent=2) + "\n")
print(json.dumps(output, indent=2))

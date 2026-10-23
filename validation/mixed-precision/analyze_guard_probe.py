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
with (directory / "guard-probe.csv").open() as stream:
    for row in csv.DictReader(stream):
        key = row["workload"], int(row["rows"])
        block = groups.setdefault(key, {}).setdefault(int(row["block"]), {})
        block[row["implementation"]] = float(row["ns_per_batch"])

rng = random.Random(14050301)
results = []
for (workload, rows), blocks in sorted(groups.items()):
    assert len(blocks) == 21, (workload, rows, len(blocks))
    assert all(set(block) == {"baseline", "candidate"} for block in blocks.values())
    old = [block["baseline"] for _, block in sorted(blocks.items())]
    new = [block["candidate"] for _, block in sorted(blocks.items())]
    logs = [math.log(a / b) for a, b in zip(old, new)]
    samples = sorted(
        math.exp(statistics.median(rng.choices(logs, k=len(logs))))
        for _ in range(20000)
    )
    interval = [samples[100], samples[19899]]
    results.append({
        "workload": workload,
        "rows": rows,
        "paired_blocks": len(blocks),
        "baseline_median_ns_per_batch": statistics.median(old),
        "candidate_median_ns_per_batch": statistics.median(new),
        "median_paired_speedup": math.exp(statistics.median(logs)),
        "paired_bootstrap_99_percent_interval": interval,
        "classification": (
            "candidate faster" if interval[0] > 1 else
            "candidate slower" if interval[1] < 1 else
            "unresolved at 99 percent"
        ),
    })
output = {
    "scope": "Isolated f64 core guard overhead with matched direct-rustc builds; not full reference-code acceptance benchmark",
    "method": "21 alternating paired blocks, median log ratio, 20000 paired bootstrap resamples, deterministic seed14050301, percentile99 interval",
    "speedup_definition": "baseline time / candidate time",
    "results": results,
}
(directory / "guard-probe-analysis.json").write_text(json.dumps(output, indent=2) + "\n")
print(json.dumps(output, indent=2))

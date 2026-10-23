"""Strict parsing of the preregistered receipt follow-up; no timing operations."""
import csv
import io
import math

INITIAL_ITERATIONS = {
    "bubble-ordinary": (1024, 64),
    "triangle-ordinary": (256, 16),
    "bubble-zero-real": (512, 32),
    "bubble-zero-complex": (256, 16),
    "bubble-mixed-dual": (128, 8),
    "ggh-zero-real": (128, 8),
    "ggh-mixed-complex": (128, 8),
}
MATRIX = {(name, rows) for name in INITIAL_ITERATIONS for rows in (1, 32)}
TARGET_NS = 200_000_000
MAX_ITERATIONS = 1 << 32
FIELDS = ["workload", "rows", "block", "order", "implementation", "iterations", "ns_per_batch"]


def next_iterations(count, elapsed_ns):
    # Match Rust Duration::as_secs_f64 and the probe's left-associated f64
    # arithmetic, including its 2% calibration headroom.
    seconds = float(elapsed_ns // 1_000_000_000) + float(elapsed_ns % 1_000_000_000) / 1e9
    value = (float(count) * 0.2 / seconds) * 1.02
    assert math.isfinite(value) and value <= MAX_ITERATIONS
    return max(count + 1, math.ceil(value))


def parse_calibration(log):
    calibration = {}
    for line in log.splitlines():
        if not line.startswith("CALIBRATION,"):
            continue
        _, name, rows, trial, order, iterations, old_ns, new_ns = line.split(",")
        key = name, int(rows)
        assert key in MATRIX, f"unknown calibration case {key}"
        trials = calibration.setdefault(key, [])
        index, count = int(trial), int(iterations)
        elapsed = int(old_ns), int(new_ns)
        assert index == len(trials) and index < 12
        assert order == ("baseline-first" if index % 2 == 0 else "candidate-first")
        assert 0 < count <= MAX_ITERATIONS and min(elapsed) > 0
        if trials:
            previous = trials[-1]
            faster = min(previous[1:])
            assert faster < TARGET_NS, "continued calibration after target reached"
            assert count == next_iterations(previous[0], faster), "changed calibration rule"
        else:
            assert count == INITIAL_ITERATIONS[name][0 if key[1] == 1 else 1], "changed initial count"
        trials.append((count, *elapsed))
    assert set(calibration) == MATRIX, "incomplete calibration matrix"
    for key, trials in calibration.items():
        assert min(trials[-1][1:]) >= TARGET_NS, f"calibration below target: {key}"
    return calibration


def parse_measurements(text, calibration):
    reader = csv.DictReader(io.StringIO(text))
    assert reader.fieldnames == FIELDS, "unexpected CSV schema"
    groups = {}
    for row in reader:
        assert set(row) == set(FIELDS) and all(value is not None for value in row.values())
        key = row["workload"], int(row["rows"])
        assert key in MATRIX, f"unknown measurement case {key}"
        index = int(row["block"])
        assert 0 <= index < 41
        block = groups.setdefault(key, {}).setdefault(index, {})
        value = float(row["ns_per_batch"])
        assert math.isfinite(value) and value > 0
        assert row["order"] == ("baseline-first" if index % 2 == 0 else "candidate-first")
        assert int(row["iterations"]) == calibration[key][-1][0], "changed measured count"
        side = row["implementation"]
        assert side in {"baseline", "candidate"} and side not in block
        block[side] = value
    assert set(groups) == MATRIX, "incomplete measurement matrix"
    for key, blocks in groups.items():
        assert set(blocks) == set(range(41)), f"incomplete blocks: {key}"
        assert all(set(block) == {"baseline", "candidate"} for block in blocks.values())
    return groups

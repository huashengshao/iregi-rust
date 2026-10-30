#!/usr/bin/env python3
"""Same-session, same-core, interleaved timing of TIRust, original IREGI and COLLIER.

For every input row and batch size (1 and 32) each candidate gets a fresh
pinned process. A pilot (3 warm-ups + 1 call) fixes the per-block call count
for ~TARGET_NS; then ROUNDS rounds run one block per candidate in a seeded
random order (paired design). Arrays are validated outside the timers:
lane 0 against the archived reference tensors (independently admitted against
quadruple-precision original IREGI), other lanes against same-session TIRust
and IREGI cross-agreement. Failed, refused and STOP outcomes are kept.

usage: run.py --cpu CPU [--output DIR] [--rounds N] [--only ID-SUBSTRING]
Writes raw.jsonl (every block) and summary.json under the output directory.
"""
import argparse
import json
import math
import os
import queue
import random
import statistics
import subprocess
import threading
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BIN = ROOT / "target/direct-engine-20261030/bin"
TARGET_NS = 20_000_000
MAX_ITERATIONS = 1_000_000
MODES = {0: "IBP", 1: "PV", 2: "Hybrid"}
COLLIER_SUMMARY = ROOT / "validation/benchmark/opening-double-20261026/collier/summary.json"


class Engine:
    """A persistent driver process speaking the BENCH wire protocol.

    A reader thread moves stdout lines into a queue, so buffered reads never
    hide complete lines from the timeout logic.
    """

    def __init__(self, argv, cpu):
        self.process = subprocess.Popen(["taskset", "-c", str(cpu), *argv], cwd=ROOT, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.lines = queue.Queue()
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()
        self.tail = []
        while True:
            line = self._line(120)
            if line is None:
                raise RuntimeError(f"{argv[0]} did not start")
            if line.startswith("READY"):
                break

    def _read(self):
        for line in self.process.stdout:
            self.lines.put(line.rstrip("\n"))
        self.lines.put(None)

    def _line(self, timeout):
        try:
            return self.lines.get(timeout=max(timeout, 0))
        except queue.Empty:
            return None

    def request(self, text, timeout=1800):
        try:
            self.process.stdin.write(text)
            self.process.stdin.flush()
        except BrokenPipeError:
            return None
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            line = self._line(deadline - time.monotonic())
            if line is None:
                return None
            if line.startswith("RESULT "):
                return json.loads(line[7:])
            self.tail = (self.tail + [line])[-5:]
        return None

    def close(self):
        try:
            self.process.stdin.write("QUIT\n")
            self.process.stdin.flush()
            self.process.wait(timeout=10)
        except Exception:
            self.process.kill()
            self.process.wait()


def decimal(value: str) -> str:
    return repr(float(Fraction(value)))


def rows(case, lanes, with_power):
    out = []
    for sample in lanes:
        for shift, mass, power in zip(sample["shifts"], sample["masses_squared"], case["powers"]):
            row = " ".join(decimal(x) for x in shift) + f" ({decimal(mass[0])},{decimal(mass[1])})"
            out.append(row + (f" {power}" if with_power else ""))
    return "\n".join(out) + "\n"


def tirust_wire(case, lanes, warmup, repeats, iterations):
    mu = decimal(lanes[0]["mu"])
    head = (f"BENCH {case['id']} {case['n']} {case['rank']} {case['dimension_shift']} {mu} {len(lanes)} "
            f"{warmup} {repeats} {iterations}\n")
    return head + rows(case, lanes, True)


def iregi_wire(case, lanes, mode, warmup, repeats, iterations):
    api = "tensor" if case["table"] == "ordinary" else "general"
    mu = decimal(lanes[0]["mu"])
    head = (f"BENCH {case['id']} {api} {mode} {case['n']} {case['rank']} {2 * case['dimension_shift']} {mu} "
            f"{len(lanes)} {warmup} {repeats} {iterations}\n")
    return head + rows(case, lanes, True)


def collier_wire(case, lanes, config, warmup, repeats, iterations):
    mu = decimal(lanes[0]["mu"])
    head = (f"BENCH {case['id']} {config['mode']} {case['n']} {case['rank']} {mu} {len(lanes)} {warmup} {repeats} "
            f"{iterations} {config['requested_accuracy']} {config['critical_accuracy']} "
            f"{config['direct_tensor_threshold']} {config['argument_permutation']}\n")
    return head + rows(case, lanes, False)


def basis(rank):
    out = []
    for r in range(rank + 1):
        for t in range(r, -1, -1):
            for x in range(r - t, -1, -1):
                for y in range(r - t - x, -1, -1):
                    out.append((t, x, y, r - t - x - y))
    return out


def reference_array(case):
    data = json.loads((ROOT / case["reference"]).read_text())["first_output"]
    values = data["lanes"][0]["values"]
    return [(float(Fraction(z[0]["exact_rational"])), float(Fraction(z[1]["exact_rational"]))) for z in values]


def array_error(case, moments, reference):
    """Dimensionally rescaled whole-array E/A over all moments and Laurent slots."""
    if moments is None:
        return None
    mu = float(Fraction(case["lanes"][0]["mu"]))
    base = 4 + 2 * case["dimension_shift"] - 2 * sum(case["powers"])
    error = amplitude = 0.0
    nonfinite = 0
    for m, monomial in enumerate(basis(case["rank"])):
        weight = mu ** (sum(monomial) + base)
        for slot in range(4):
            a = moments[m][slot]
            b = reference[4 * m + slot]
            if not all(math.isfinite(x) for x in a):
                nonfinite += 1
                continue
            error = max(error, math.hypot(a[0] - b[0], a[1] - b[1]) / weight)
            amplitude = max(amplitude, math.hypot(b[0], b[1]) / weight)
    if nonfinite:
        return float("nan")
    return error / amplitude if amplitude else (0.0 if error == 0 else float("inf"))


def lane_moments(result, lane):
    if result is None:
        return None
    entry = result["lanes"][lane]
    return entry.get("moments") if entry.get("status") == "success" else None


def stats(values):
    if not values:
        return None
    mean = statistics.fmean(values)
    se = statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else None
    return {"mean": mean, "median": statistics.median(values), "standard_error": se,
            "min": min(values), "max": max(values), "blocks": len(values)}


def ratio_summary(numerator, denominator, rng):
    pairs = [a / b for a, b in zip(numerator, denominator) if b > 0]
    if not pairs:
        return None
    medians = []
    for _ in range(2000):
        sample = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        medians.append(statistics.median(sample))
    medians.sort()
    return {"median": statistics.median(pairs), "ci99": [medians[10], medians[-11]], "pairs": len(pairs)}


def cpu_busy(cpu, seconds=1.0):
    def snapshot():
        for line in Path("/proc/stat").read_text().splitlines():
            if line.startswith(f"cpu{cpu} "):
                fields = [int(x) for x in line.split()[1:]]
                return sum(fields), fields[3] + fields[4]
    total0, idle0 = snapshot()
    time.sleep(seconds)
    total1, idle1 = snapshot()
    return round(1 - (idle1 - idle0) / max(total1 - total0, 1), 4)


def candidates(case, collier_configs):
    out = [{"id": "tirust", "engine": "TIRust", "argv": [str(BIN / "tirust-direct-timing")]}]
    modes = (0, 1, 2) if case["table"] == "ordinary" else (0,)
    for mode in modes:
        out.append({"id": f"iregi-{MODES[mode].lower()}", "engine": "IREGI", "mode": MODES[mode], "mode_code": mode,
                    "argv": [str(BIN / "iregi-general")]})
    if case["table"] == "ordinary":
        out.append({"id": "collier", "engine": "COLLIER", "config": collier_configs[case["id"]],
                    "argv": [str(BIN / "collier-batch")]})
    return out


def wire(candidate, case, lanes, warmup, repeats, iterations):
    if candidate["engine"] == "TIRust":
        return tirust_wire(case, lanes, warmup, repeats, iterations)
    if candidate["engine"] == "IREGI":
        return iregi_wire(case, lanes, candidate["mode_code"], warmup, repeats, iterations)
    return collier_wire(case, lanes, candidate["config"], warmup, repeats, iterations)


def measure(case, batch, cpu, rounds, rng, raw, collier_configs):
    lanes = case["lanes"][:batch]
    reference = reference_array(case)
    runs = []
    for candidate in candidates(case, collier_configs):
        entry = {key: candidate[key] for key in candidate if key != "argv"}
        try:
            engine = Engine(candidate["argv"], cpu)
        except RuntimeError as error:
            entry.update(status="start_failure", detail=str(error))
            runs.append((entry, None))
            continue
        pilot = engine.request(wire(candidate, case, lanes, 3, 1, 1))
        if pilot is None:
            entry.update(status="no_result", detail=engine.tail)
            engine.close()
            runs.append((entry, None))
            continue
        per_call = max(pilot["total_ns"][0], 1.0)
        entry["iterations"] = max(1, min(MAX_ITERATIONS, math.ceil(TARGET_NS / per_call)))
        entry["pilot_ns"] = pilot["total_ns"][0]
        for key in ("plan_ns", "workspace_ns", "first_call_ns", "plan_engine", "workspace_engine"):
            if key in pilot:
                entry[key] = pilot[key]
        entry["blocks_ns"] = []
        entry["status"] = "measured"
        runs.append((entry, engine))
    active = [run for run in runs if run[1] is not None]
    results = {}
    for round_index in range(rounds):
        order = list(active)
        rng.shuffle(order)
        for entry, engine in order:
            if entry["status"] != "measured":
                continue
            result = engine.request(wire(next(c for c in candidates(case, collier_configs) if c["id"] == entry["id"]),
                                         case, lanes, 1, 1, entry["iterations"]))
            if result is None:
                entry.update(status="lost_during_rounds", detail=engine.tail)
                continue
            entry["blocks_ns"].append(result["total_ns"][0])
            raw.write(json.dumps({"case": case["id"], "batch": batch, "round": round_index, "candidate": entry["id"],
                                  "iterations": entry["iterations"], "ns_per_call": result["total_ns"][0]}) + "\n")
            results[entry["id"]] = result
    for entry, engine in active:
        engine.close()
    # Validation outside all timers.
    for entry, _ in runs:
        result = results.get(entry["id"])
        if result is None:
            entry.setdefault("status", "no_result")
            continue
        entry["stable_flag"] = result.get("stable")
        statuses = [lane.get("status") for lane in result["lanes"]]
        entry["lane_statuses"] = {s: statuses.count(s) for s in set(statuses)}
        entry["lane0_relative_error"] = array_error(case, lane_moments(result, 0), reference)
        if "fallback_rows" in result:
            entry["fallback_rows"] = result["fallback_rows"]
        entry["timing_ns"] = stats(entry["blocks_ns"])
    # Cross agreement of lanes 1..: TIRust versus the IREGI IBP candidate.
    tirust = results.get("tirust")
    iregi_ibp = results.get("iregi-ibp")
    cross = None
    if batch > 1 and tirust is not None and iregi_ibp is not None:
        worst = 0.0
        for lane in range(1, batch):
            a, b = lane_moments(tirust, lane), lane_moments(iregi_ibp, lane)
            if a is None or b is None:
                worst = float("nan")
                break
            flat = [tuple(z) for moment in b for z in moment]
            worst = max(worst, array_error(case, a, flat))
        cross = worst
    return [entry for entry, _ in runs], cross


def selected(entries, engine):
    usable = [e for e in entries if e["engine"] == engine and e.get("timing_ns")
              and e.get("lane_statuses", {}).get("success", 0) == sum(e.get("lane_statuses", {}).values())
              and e.get("lane0_relative_error") is not None and e["lane0_relative_error"] <= 1e-3]
    if not usable:
        return None
    return min(usable, key=lambda e: e["timing_ns"]["mean"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "target/direct-engine-20261030/capture")
    parser.add_argument("--rounds", type=int, default=11)
    parser.add_argument("--batch-rounds", type=int, default=7)
    parser.add_argument("--only", default=None)
    parser.add_argument("--seed", type=int, default=20261030)
    parser.add_argument("--build-record", default="build.json")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    inputs = json.loads((HERE / "inputs.json").read_text())
    collier_configs = {}
    for row in json.loads(COLLIER_SUMMARY.read_text())["rows"]:
        collier_configs[row["id"]] = next(a["configuration"] for a in row["all_candidate_attempts"]
                                          if a["id"] == row["selected_candidate"])
    rng = random.Random(args.seed)
    environment = {
        "cpu": args.cpu, "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "loadavg_start": Path("/proc/loadavg").read_text().split()[:3],
        "cpu_model": next(l.split(":", 1)[1].strip() for l in Path("/proc/cpuinfo").read_text().splitlines()
                          if l.startswith("model name")),
        "uname": " ".join(os.uname()), "target_ns_per_block": TARGET_NS,
        "rounds": {"batch1": args.rounds, "batch32": args.batch_rounds}, "seed": args.seed,
        "build": json.loads((HERE / args.build_record).read_text()),
    }
    rows = []
    with open(args.output / "raw.jsonl", "w") as raw:
        for case in inputs["cases"]:
            if args.only and args.only not in case["id"]:
                continue
            row = {"id": case["id"], "table": case["table"], "label": case["label"], "n": case["n"],
                   "rank": case["rank"], "powers": case["powers"], "dimension_shift": case["dimension_shift"],
                   "moments": len(basis(case["rank"]))}
            for batch in inputs["batch_sizes"]:
                busy_before = cpu_busy(args.cpu, 0.5)
                started = time.monotonic()
                entries, cross = measure(case, batch, args.cpu,
                                         args.rounds if batch == 1 else args.batch_rounds, rng, raw, collier_configs)
                key = f"batch{batch}"
                tirust = next(e for e in entries if e["id"] == "tirust")
                iregi = selected(entries, "IREGI")
                collier = next((e for e in entries if e["engine"] == "COLLIER"), None)
                ratios = {}
                for name, reference in (("tirust_over_iregi", iregi), ("tirust_over_collier", collier)):
                    if reference is not None and reference.get("blocks_ns") and tirust.get("blocks_ns"):
                        ratios[name] = ratio_summary(tirust["blocks_ns"], reference["blocks_ns"], rng)
                row[key] = {"candidates": entries, "selected_iregi": iregi["id"] if iregi else None,
                            "tirust_iregi_cross_error_lanes": cross, "ratios": ratios,
                            "cpu_busy_before": busy_before, "wall_s": round(time.monotonic() - started, 2)}
                print(json.dumps({"id": case["id"], "batch": batch,
                                  "tirust_us": (tirust.get("timing_ns") or {}).get("median", float("nan")) / 1e3,
                                  "tirust_error": tirust.get("lane0_relative_error"),
                                  "iregi": iregi["id"] if iregi else None,
                                  "iregi_us": iregi["timing_ns"]["median"] / 1e3 if iregi else None,
                                  "collier_us": ((collier or {}).get("timing_ns") or {}).get("median", float("nan")) / 1e3
                                  if collier else None,
                                  "ratios": {k: v["median"] for k, v in ratios.items() if v}}), flush=True)
            rows.append(row)
    environment["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    environment["loadavg_end"] = Path("/proc/loadavg").read_text().split()[:3]
    (args.output / "summary.json").write_text(json.dumps({"environment": environment, "rows": rows}, indent=1) + "\n")


if __name__ == "__main__":
    main()

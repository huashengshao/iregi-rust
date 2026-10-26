#!/usr/bin/env python3
"""Measure a frozen external COLLIER driver for the opening ordinary table.

Run from the project root. Compilation and the quiet-window decision belong to
root. Timing is absolute, not a synchronized TIRust/COLLIER ratio campaign.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import math
import os
import selectors
from pathlib import Path
import statistics
import time

ROOT = Path.cwd().resolve()
HERE = Path("validation/benchmark/opening-collier-20261026")
INPUT = Path("validation/benchmark/opening-rank6-20261026/inputs.json")
KERNEL = Path("validation/benchmark/run.py")
SPEC = importlib.util.spec_from_file_location("opening_collier_transport", ROOT / KERNEL)
kernel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kernel)


class CaptureProcess(kernel.Process):
    """The existing bounded wire transport, additionally retaining exact stdout."""
    def __init__(self, binary, label, directory, timeout):
        super().__init__(binary, label, directory, timeout)
        self.stdout_log = (directory / (label + ".stdout.log")).open("ab")

    def request(self, text):
        if self.process.poll() is not None:
            raise RuntimeError(f"benchmark process already exited: {self.process.returncode}")
        deadline = time.monotonic() + self.timeout
        payload = memoryview(text.encode())
        sent = 0
        self.selector.register(self.process.stdin, selectors.EVENT_WRITE)
        try:
            while time.monotonic() < deadline:
                if sent == len(payload):
                    while b"\n" in self.buffer:
                        line, self.buffer = self.buffer.split(b"\n", 1)
                        if line.startswith(b"RESULT "):
                            return json.loads(line[7:])
                events = self.selector.select(max(0.0, deadline - time.monotonic()))
                if not events:
                    break
                for key, _ in events:
                    if key.fileobj is self.process.stdin:
                        try:
                            sent += os.write(self.process.stdin.fileno(), payload[sent:])
                        except BlockingIOError:
                            continue
                        if sent == len(payload):
                            self.selector.unregister(self.process.stdin)
                    else:
                        try:
                            chunk = os.read(self.process.stdout.fileno(), 65536)
                        except BlockingIOError:
                            continue
                        if not chunk:
                            raise RuntimeError(f"benchmark process exited without RESULT: {self.process.poll()}")
                        self.stdout_log.write(chunk)
                        self.stdout_log.flush()
                        self.buffer += chunk
            self.process.kill()
            self.process.wait()
            raise TimeoutError("benchmark request exceeded timeout; retained as failed")
        finally:
            try:
                self.selector.unregister(self.process.stdin)
            except KeyError:
                pass

    def close(self):
        super().close()
        self.stdout_log.close()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def represented(value):
    q = F(value)
    v = float(q)
    if not math.isfinite(v) or F(v) != q:
        raise ValueError("fixture value is not exactly represented by binary64")
    return format(v, ".17g")


def request(case, *, check=False, repeats=1, iterations=1, warmup=0):
    req = case["driver_request"]
    if (case["table"] != "ordinary" or req["dimension_shift"] != 0
            or req["powers"] != [1] * req["n"] or len(req["samples"]) != 1):
        raise ValueError("only unchanged ordinary singleton inputs are admitted")
    s = req["samples"][0]
    lines = [f'{"CHECK" if check else "BENCH"} {case["id"]} 1 {req["n"]} {req["rank"]} '
             f'{represented(s["mu"])} 1 {warmup} {repeats} {iterations}']
    for shift, mass in zip(s["shifts"], s["masses_squared"]):
        lines.append(" ".join(represented(v) for v in shift)
                     + f" ({represented(mass[0])},{represented(mass[1])})")
    if len(lines) != req["n"] + 1:
        raise ValueError("propagator input length")
    return "\n".join(lines) + "\n"


def degrees(rank):
    return [r for r in range(rank + 1) for t in range(r, -1, -1)
            for x in range(r-t, -1, -1) for y in range(r-t-x, -1, -1)]


def decoded_tirust(case):
    path = INPUT.parent / "cases" / case["id"] / "result.json"
    value = json.loads(path.read_text())
    lane = value["first_output"]["lanes"][0]
    if value["status"] != "measured" or lane["status"] != "Success":
        raise ValueError("saved TIRust reference row is not successful")
    values = lane["values"]
    return [[tuple(F(v["exact_rational"]) for v in values[4*m+s])
             for s in range(4)] for m in range(math.comb(case["driver_request"]["rank"]+4, 4))], path


def compare(moments, expected, case):
    req = case["driver_request"]
    if not isinstance(moments, list) or len(moments) != len(expected):
        return {"passed": False, "error": "incomplete cumulative moment count"}
    maximum = F(0)
    failed = 0
    count = 0
    for degree, actual, reference in zip(degrees(req["rank"]), moments, expected):
        if not isinstance(actual, list) or len(actual) != 4:
            return {"passed": False, "error": "missing Laurent slots"}
        qpower = F(9) ** (degree + 4 - 2*req["n"])
        for a, b in zip(actual, reference):
            if (not isinstance(a, list) or len(a) != 2
                    or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in a)):
                return {"passed": False, "error": "nonfinite or missing complex field"}
            z = tuple(F(str(v)) for v in a)
            error = sum((v-w)**2 for v, w in zip(z, b)) / max(qpower, sum(v*v for v in b))
            maximum = max(maximum, error)
            failed += int(error > F(1, 10**20))
            count += 1
    return {"passed": failed == 0, "complex_fields": count, "failed_complex_fields": failed,
            "maximum_normalized_error": math.sqrt(float(maximum)),
            "maximum_squared_normalized_error_exact": str(maximum), "tolerance": "1e-10"}


def assess(response, case, expected, repeats, *, pole_check=False):
    req = case["driver_request"]
    errors = []
    n, rank = req["n"], req["rank"]
    iface = {1: "Aten_cll", 2: "Bten_cll", 3: "Cten_cll", 4: "Dten_cll"}.get(n, "TNten_cll")
    for key, value in {"id": case["id"], "stable": True, "collier_mode": 1,
                       "initialization_topology_capacity": max(n, 2),
                       "initialization_rank_capacity": max(rank, 1, n-max(n-2, 4)),
                       "interface": iface, "direct_tensor_threshold": 6}.items():
        if response.get(key) != value:
            errors.append(f"unexpected {key}: {response.get(key)!r}")
    clock_rate = response.get("clock_ticks_per_second")
    if type(clock_rate) is not int or clock_rate <= 0:
        errors.append("missing/invalid monotonic clock rate")
    times = response.get("total_ns")
    if (not isinstance(times, list) or len(times) != repeats
            or any(not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0 for v in times)):
        errors.append("missing/invalid raw timing blocks")
    lanes = response.get("lanes", [])
    checks = []
    if len(lanes) != 1:
        errors.append("missing singleton lane")
    else:
        lane = lanes[0]
        for key in ("last_err_flag", "last_acc_flag", "worst_err_flag", "worst_acc_flag"):
            if lane.get(key) != 0:
                errors.append(f"{key}={lane.get(key)!r}")
        if lane.get("status") != "success":
            errors.append("native lane is not successful")
        estimates = lane.get("maximum_rank_error_estimates")
        if (not isinstance(estimates, list) or len(estimates) != rank+1
                or any(not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0 for v in estimates)):
            errors.append("incomplete/nonfinite rank error estimates")
        checks.append(compare(lane.get("moments") or lane.get("diagnostic_moments"), expected, case))
    blocks = response.get("blocks", [])
    if len(blocks) != repeats:
        errors.append("missing per-block diagnostics/tensors")
    for block in blocks:
        block_lanes = block.get("lanes", [])
        if len(block_lanes) != 1:
            errors.append("missing per-block singleton lane")
            continue
        lane = block_lanes[0]
        if lane.get("cumulative_stable") is not True or lane.get("last_err_flag") != 0 or lane.get("last_acc_flag") != 0:
            errors.append("per-block status rejected")
        estimates = lane.get("cumulative_maximum_rank_error_estimates")
        if (not isinstance(estimates, list) or len(estimates) != rank+1
                or any(not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0 for v in estimates)):
            errors.append("incomplete/nonfinite/negative per-block rank error estimates")
        checks.append(compare(lane.get("moments"), expected, case))
    if pole_check:
        pole = response.get("pole_check_errors")
        if (not isinstance(pole, list) or len(pole) != 1 or len(pole[0]) != 3
                or any(not isinstance(v, (int, float)) or not math.isfinite(v) or not 0 <= v <= 1e-12 for v in pole[0])):
            errors.append("separate UV/IR pole probes rejected")
    return {"passed": not errors and all(v["passed"] for v in checks), "errors": errors,
            "array_comparisons": checks,
            "compared_complex_fields": sum(v.get("complex_fields", 0) for v in checks),
            "failed_complex_fields": sum(v.get("failed_complex_fields", 0) for v in checks)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--binary-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--quiet-note", required=True)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--cohort-timeout", type=float, default=300)
    args = parser.parse_args()
    if not (ROOT/"Cargo.toml").is_file() or args.cpu not in os.sched_getaffinity(0):
        parser.error("run from project root using an allowed CPU")
    if (not math.isfinite(args.timeout) or not math.isfinite(args.cohort_timeout)
            or args.timeout <= 0 or args.cohort_timeout <= 0 or not args.quiet_note.strip()):
        parser.error("positive timeouts and explicit quiet-window note required")
    binary = args.binary.resolve()
    if digest(binary) != args.binary_sha256:
        parser.error("binary hash differs")
    output = args.output.resolve()
    if not output.is_relative_to(ROOT/"target") or output.exists():
        parser.error("output must be a new target/ directory")
    output.mkdir(parents=True)
    os.sched_setaffinity(0, {args.cpu})
    sources = {str(p): digest(ROOT/p) for p in [INPUT, KERNEL, HERE/"driver.f90", HERE/"run.py", HERE/"README.md"]}
    suite = json.loads((ROOT/INPUT).read_text())
    cases = [v for v in suite["cases"] if v["table"] == "ordinary"]
    if len(cases) != 12:
        raise ValueError("expected twelve fixed ordinary rows")
    data = {"schema_version": 1, "kind": "opening-collier-absolute-timings", "status": "running",
            "started_utc": datetime.now(timezone.utc).isoformat(), "cpu": args.cpu,
            "quiet_note": args.quiet_note, "binary": {"path": str(binary.relative_to(ROOT)), "sha256": digest(binary)},
            "input_sources": sources, "mode": 1, "numeric_type": "binary64", "sample_lanes": 1,
            "repeats": 11, "warmup": 3, "target_block_ns": 100000000,
            "maximum_iterations": 1000000,
            "timer_scope": "per-root InitEvent, routing/invariants, public tensor call including masters, status/finite scans, normalization and gathering; excludes init/warmup/pole probes/snapshots/I/O",
            "ratio_campaign": False, "rows": []}
    save(output/"results.json", data)
    deadline = time.monotonic() + args.cohort_timeout
    for case in cases:
        directory = output/case["id"]
        directory.mkdir()
        row = {"id": case["id"], "n": case["driver_request"]["n"], "rank": case["driver_request"]["rank"],
               "status": "running", "timing_qualified": False, "input": case, "captures": {}}
        data["rows"].append(row)
        process = None
        try:
            expected, reference = decoded_tirust(case)
            row["tirust_array_source"] = {"path": str(reference), "sha256": digest(ROOT/reference)}
            if time.monotonic() >= deadline:
                raise TimeoutError("fixed campaign deadline exhausted before row")
            process = CaptureProcess(binary, "collier", directory, min(args.timeout, deadline-time.monotonic()))
            def capture(label, **settings):
                remaining = deadline-time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("fixed campaign deadline exhausted")
                process.timeout = min(args.timeout, remaining)
                wire = request(case, **settings)
                (directory/(label+".request.txt")).write_text(wire)
                started = time.monotonic()
                response = process.request(wire)
                save(directory/(label+".response.json"), response)
                check = assess(response, case, expected, settings.get("repeats", 1), pole_check=settings.get("check", False))
                save(directory/(label+".assessment.json"), check)
                row["captures"][label] = {"wall_seconds_including_transport": time.monotonic()-started,
                                          "response": str((directory/(label+".response.json")).relative_to(ROOT)),
                                          "response_sha256": digest(directory/(label+".response.json")), "assessment": check}
                save(output/"results.json", data)
                return response, check
            pre, precheck = capture("preflight", check=True)
            pilot, pilotcheck = capture("pilot", warmup=3)
            pilot_ns = pilot["total_ns"][0]
            iterations = max(1, min(1000000, math.ceil(100000000/pilot_ns)))
            row["iterations_per_block"] = iterations
            measured, measurecheck = capture("timed", warmup=3, repeats=11, iterations=iterations)
            post, postcheck = capture("postflight", check=True)
            values = measured["total_ns"]
            stddev = statistics.stdev(values)
            mean = statistics.mean(values)
            row["timing_ns"] = {"raw_block_means": values, "mean": mean, "median": statistics.median(values),
                                "stddev": stddev, "standard_error": stddev/math.sqrt(len(values)),
                                "confidence_95_half_width_student_t": 2.228138852*stddev/math.sqrt(len(values)),
                                "minimum": min(values), "maximum": max(values)}
            row["timing_us"] = {k: v/1000 for k, v in row["timing_ns"].items() if k != "raw_block_means"}
            row["timing_qualified"] = all(v["passed"] for v in [precheck, pilotcheck, measurecheck, postcheck])
            row["status"] = "measured" if row["timing_qualified"] else "measured_but_unqualified"
        except Exception as error:
            row.update(status="timeout" if isinstance(error, TimeoutError) else "failed", error=str(error))
        finally:
            if process is not None:
                process.close()
                row["native_returncode"] = process.process.returncode
            row["binary_unchanged_after"] = digest(binary) == args.binary_sha256
            source = row.get("tirust_array_source")
            row["reference_array_unchanged_after"] = bool(source) and digest(ROOT/source["path"]) == source["sha256"]
            if (row.get("native_returncode") != 0 or not row["binary_unchanged_after"]
                    or not row["reference_array_unchanged_after"]):
                row["timing_qualified"] = False
                if row["status"] == "measured":
                    row["status"] = "measured_but_unqualified"
            save(output/"results.json", data)
        print(json.dumps({k: row[k] for k in ["id", "status", "timing_qualified"]}), flush=True)
    data["sources_unchanged_after"] = all(digest(ROOT/p) == h for p, h in sources.items())
    data["binary_unchanged_after"] = digest(binary) == args.binary_sha256
    if not data["sources_unchanged_after"] or not data["binary_unchanged_after"]:
        for row in data["rows"]:
            row["timing_qualified"] = False
            if row["status"] == "measured":
                row["status"] = "measured_but_unqualified"
    data["completed_utc"] = datetime.now(timezone.utc).isoformat()
    data["status"] = "passed" if (all(v["timing_qualified"] for v in data["rows"])
                                         and data["sources_unchanged_after"] and data["binary_unchanged_after"]) else "retained_failures"
    save(output/"results.json", data)
    return 0 if data["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Compare original IREGI and optional COLLIER on identical tensor arrays.

Correctness is the default. Timing requires an explicit quiet-window note and
a completed matching correctness receipt; subprocess transport is never timed.
"""
import argparse
import datetime
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import statistics
import sys
import time


ROOT = Path.cwd()
HERE = ROOT / "validation/collier-reference"
SPEC = importlib.util.spec_from_file_location("iregi_kernel_benchmark_support", ROOT / "validation/benchmark/run.py")
kernel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kernel)


def load_inputs(path):
    cases = json.loads(path.read_text())
    if not isinstance(cases, list) or not cases:
        raise ValueError("the input must be a nonempty case array")
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("duplicate input case identity")
    for case in cases:
        if case["n"] not in (2, 3, 4) or case["rank"] not in (0, 1, 2, 3):
            raise ValueError("initial harness supports N2..4 ranks0..3; broader shared domain remains pending")
        if not case.get("samples"):
            raise ValueError("a case must have samples")
        for sample in case["samples"]:
            if len(sample["shifts"]) != case["n"] or len(sample["masses"]) != case["n"]:
                raise ValueError("input propagator count differs from topology")
            if (not isinstance(sample["mu"], (int, float)) or not math.isfinite(sample["mu"])
                    or sample["mu"] <= 0 or not math.isfinite(sample["mu"] ** 2) or sample["mu"] ** 2 == 0):
                raise ValueError("positive finite scale with representable positive squared scale required")
            if sample["shifts"][0] != [0, 0, 0, 0]:
                raise ValueError("initial harness requires zero-origin routing")
            if any(len(p) != 4 or any(not math.isfinite(x) for x in p) or p[0] != 0 for p in sample["shifts"]):
                raise ValueError("initial harness requires finite purely spatial real shifts")
            if any(len(m) != 2 or any(not math.isfinite(x) for x in m) or m[0] <= 0 or m[1] > 0
                   for m in sample["masses"]):
                raise ValueError("initial harness requires squared masses with Re>0 and Im<=0")
    return cases


def collier_request(case, samples, mode, warmup, iterations, *, check=False):
    text = kernel.fortran_request(case, samples, "PassarinoVeltman", warmup, iterations)
    lines = text.splitlines()
    fields = lines[0].split()
    fields[0] = "CHECK" if check else "BENCH"
    fields[2] = str(mode)
    return " ".join(fields) + "\n" + "\n".join(lines[1:]) + "\n"


def comparison(actual, expected, case, samples):
    result = kernel.compare(actual, expected, case, samples)
    result["errors"] = [error.replace("Rust", "COLLIER") for error in result["errors"]]
    return result


def validate_poles(response, samples):
    errors = response.get("pole_check_errors")
    if not isinstance(errors, list) or len(errors) != len(samples):
        raise ValueError("missing separated-pole CHECK evidence")
    for lane in errors:
        if (not isinstance(lane, list) or len(lane) != 3
                or any(isinstance(x, bool) or not isinstance(x, (int, float))
                       or not math.isfinite(x) or x < 0 or x > 1e-12 for x in lane)):
            raise ValueError("COLLIER delta-parameter pole check failed")


def uv_identities(response, case, samples):
    """Independent UV identities for the initial scalar/vector bubble/triangle rows."""
    if case["n"] == 4 and case["rank"] <= 3:
        errors = []
        worst = 0.0
        expected_count = len(kernel.degrees(case["rank"]))
        for lane, (row, sample) in enumerate(zip(response["lanes"], samples)):
            if row["status"] != "success" or len(row["moments"]) != expected_count:
                errors.append(f"lane {lane}: incomplete or unsuccessful N4 tensor array")
                continue
            energy = max(1.0, sample["mu"], *(abs(x) for p in sample["shifts"] for x in p),
                         *(math.sqrt(math.hypot(*m)) for m in sample["masses"]))
            for moment, degree in zip(row["moments"], kernel.degrees(case["rank"])):
                error = abs(complex(*moment[0])) / energy ** (4 + degree - 8)
                worst = max(worst, error)
                if not math.isfinite(error) or error > 1e-10:
                    errors.append(f"lane {lane}: superficially UV-finite N4 moment has a UV pole")
        return {"status": "passed" if not errors else "failed", "maximum_normalized_error": worst,
                "tolerance": 1e-10, "errors": errors,
                "identities": "N4 unit-power tensors through rank3 are superficially UV finite:4+rank−8<0"}
    if case["n"] not in (2, 3) or case["rank"] > 1:
        return {"status": "not_applicable", "reason": "UV identities cover N2/N3r0/1 and N4r0..3"}
    worst = 0.0
    errors = []
    for lane, (row, sample) in enumerate(zip(response["lanes"], samples)):
        if row["status"] != "success":
            errors.append(f"unsuccessful lane {lane}")
            continue
        expected = [complex(0, math.pi ** 2) if case["n"] == 2 else 0j]
        if case["rank"] == 1:
            expected += [complex(0, -math.pi ** 2 * x / 2) if case["n"] == 2 else 0j
                         for x in sample["shifts"][1]]
        energy = max(1.0, sample["mu"], *(abs(x) for p in sample["shifts"] for x in p),
                     *(math.sqrt(math.hypot(*m)) for m in sample["masses"]))
        for moment, value in enumerate(expected):
            observed = complex(*row["moments"][moment][0])
            degree = int(moment > 0)
            error = abs(observed - value) / (energy ** (4 + degree - 2 * case["n"]) + abs(value))
            worst = max(worst, error)
            if error > 1e-10:
                errors.append(f"lane {lane}, moment {moment}: independent UV identity failed")
    return {"status": "passed" if not errors else "failed", "maximum_normalized_error": worst,
            "tolerance": 1e-10, "errors": errors,
            "identities": "B UV=1, B^mu UV=−p1^mu/2; C scalar/vector UV=0, multiplied by native i*pi²"}


def source_hashes():
    files = sorted(HERE.glob("*.py")) + sorted(HERE.glob("*.f90"))
    files += sorted((HERE / "n4").glob("*.py"))
    files += [ROOT / "validation/benchmark/run.py", ROOT / "validation/benchmark/driver.f90"]
    return {str(p.relative_to(ROOT)): kernel.digest(p) for p in files}


def paired_orders(blocks, rng):
    """Randomize a fixed balanced order inventory; odd cohorts differ by one."""
    orders = [["collier", "iregi"] for _ in range((blocks + 1) // 2)]
    orders += [["iregi", "collier"] for _ in range(blocks // 2)]
    rng.shuffle(orders)
    return orders


def checked_request(processes, name, case, samples, args, warmup, iterations, expected):
    text = (collier_request(case, samples, args.collier_mode, warmup, iterations)
            if name == "collier" else kernel.fortran_request(case, samples, args.iregi_mode, warmup, iterations))
    response = bounded_request(processes[name], text, args)
    kernel.validate_response(response, case)
    if comparison(response, expected, case, samples)["status"] != "passed":
        raise ValueError("a kernel request changed complete tensor outputs")
    return response


def qualify(processes, case, samples, args):
    responses = {
        "collier": bounded_request(processes["collier"], collier_request(case, samples, args.collier_mode, 0, 1, check=True), args),
        "iregi": bounded_request(processes["iregi"], kernel.fortran_request(case, samples, args.iregi_mode, 0, 1), args),
    }
    for response in responses.values():
        kernel.validate_response(response, case)
    validate_poles(responses["collier"], samples)
    agreement = comparison(responses["collier"], responses["iregi"], case, samples)
    identities = {name: uv_identities(response, case, samples) for name, response in responses.items()}
    if agreement["status"] != "passed" or any(proof["status"] == "failed" for proof in identities.values()):
        raise ValueError("complete-array or independent UV normalization check failed")
    return {"responses": responses, "correctness": agreement, "uv_identities": identities}


def bounded_request(process, text, args):
    remaining = args.deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("fixed total cohort resource cap exhausted")
    process.timeout = min(args.timeout, remaining)
    return process.request(text)


def record_postflight_failure(row, error):
    # Preserve the original timed-stage failure if a dead process also prevents
    # the final check. A postflight error can never rehabilitate that row.
    if row["status"] in {"failed", "timeout"}:
        row["postflight_error"] = str(error)
    else:
        row.update(status="timeout" if isinstance(error, TimeoutError) else "failed", error=str(error))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", required=True, type=Path, help="COLLIER build.json")
    parser.add_argument("--baseline", type=Path,
                        default=ROOT / "validation/benchmark/baseline-6b24c03-licensed/results.json")
    parser.add_argument("--input", type=Path,
                        default=ROOT / "validation/benchmark/baseline-6b24c03-licensed/results-inputs.json")
    parser.add_argument("--output", required=True, type=Path, help="New attempt directory inside target/")
    parser.add_argument("--mode", choices=("correctness", "timing"), default="correctness")
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--batches", nargs="+", type=int, default=[1, 32])
    parser.add_argument("--collier-mode", choices=(1, 2, 3), type=int, default=1)
    parser.add_argument("--iregi-mode", choices=kernel.MODE, default="Hybrid")
    parser.add_argument("--blocks", type=int, default=41)
    parser.add_argument("--block-ms", type=float, default=100)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--cohort-timeout", type=float, default=900)
    parser.add_argument("--quiet-note", help="ROOT-granted quiet window provenance; required for timing")
    parser.add_argument("--correctness-proof", type=Path, help="Matching completed correctness receipt; required for timing")
    args = parser.parse_args()
    if (args.cpu not in os.sched_getaffinity(0) or min(args.batches) < 1
            or not math.isfinite(args.timeout) or args.timeout <= 0
            or not math.isfinite(args.cohort_timeout) or args.cohort_timeout <= 0):
        parser.error("invalid CPU, batch size or timeout")
    if args.mode == "timing" and (not args.quiet_note or not args.correctness_proof):
        parser.error("timing requires the explicit quiet-window note and a prior correctness receipt")
    if args.blocks < 3 or not math.isfinite(args.block_ms) or args.block_ms <= 0 or args.warmup < 0:
        parser.error("blocks>=3, positive block-ms and nonnegative warmup required")
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "target") or output.exists():
        parser.error("use a new attempt directory inside this project's target/")
    cases = load_inputs(args.input)
    build = json.loads(args.build.read_text())
    baseline = json.loads(args.baseline.read_text())
    binaries = {"collier": {"path": str(ROOT / build["binary"]["path"]), "sha256": build["binary"]["sha256"]},
                "iregi": baseline["binaries"]["reference"]}
    if build["status"] != "built" or baseline["reference_build"]["binary_sha256"] != binaries["iregi"]["sha256"]:
        raise ValueError("unqualified/mismatched reference build manifest")
    for info in binaries.values():
        if kernel.digest(info["path"]) != info["sha256"]:
            raise ValueError("reference binary differs from build manifest")
    sources = source_hashes()
    if build["driver_sha256"] != sources["validation/collier-reference/driver.f90"]:
        raise ValueError("COLLIER driver differs from the retained build")
    identity = {"binaries": binaries, "input_sha256": kernel.digest(args.input),
                "batches": args.batches, "iregi_mode": args.iregi_mode, "collier_mode": args.collier_mode,
                "source_sha256": sources}
    if args.mode == "timing":
        previous = json.loads(args.correctness_proof.read_text())
        if previous.get("mode") != "correctness" or previous.get("status") != "passed" or previous.get("identity") != identity:
            raise ValueError("timing requires a successful matching correctness receipt")
    output.mkdir(parents=True)
    path = output / "results.json"
    data = {"schema_version": 1, "kind": "iregi-vs-collier-shared-kernel", "mode": args.mode,
            "status": "running", "date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "identity": identity, "build_manifest": {"path": str(args.build), "sha256": kernel.digest(args.build)},
            "iregi_manifest": {"path": str(args.baseline), "sha256": kernel.digest(args.baseline)},
            "environment": kernel.environment(args.cpu), "inputs": cases,
            "protocol": {"comparison": "COLLIER / original IREGI (not Rust / IREGI)",
                         "collier_mode": args.collier_mode, "iregi_mode": args.iregi_mode,
                         "outputs": "all Cartesian components through requested rank and native [UV single, IR single, IR double, finite]",
                         "scope": "N4 massive Euclidean ordinary undotted ranks0..3 batches1/32; broader N5..N7 coverage pending",
                         "cache_policy": "within-sample recurrence memoization in both; no cross-sample/event numeric reuse",
                         "transport_timed": False, "pole_probe_timed": False,
                         "warmup": args.warmup, "warmup_blocks": 5, "blocks": args.blocks,
                         "minimum_block_ms": args.block_ms, "calibration_target_ms": 1.10 * args.block_ms,
                         "calibration": "up to eight warmed common-iteration trials, target1.10*minimum; accept only when both observed blocks reach minimum",
                         "resource_cap_seconds": args.cohort_timeout,
                         "maximum_iterations": 1_000_000,
                         "paired_order": "fixed21/20 balanced inventory shuffled with seed271828 for41 blocks",
                         "quiet_note": args.quiet_note, "statistic": "paired medians, 99% bootstrap CI; width<=2% required",
                         "correctness_tolerance": 1e-10,
                         "correctness_durations": "diagnostic only; not performance measurements"},
            "rows": [{"id": c["id"], "n": c["n"], "rank": c["rank"], "batch_width": b, "status": "pending"}
                     for c in cases for b in args.batches]}
    kernel.save(path, data)
    old_affinity = os.sched_getaffinity(0)
    os.sched_setaffinity(0, {args.cpu})
    processes = {}
    rng = random.Random(271828)
    completed = False
    started = time.monotonic()
    args.deadline = started + args.cohort_timeout
    try:
        for name, info in binaries.items():
            frozen = kernel.freeze_executable(info["path"], info["sha256"], name)
            data.setdefault("executed_binaries", {})[name] = {"path": str(frozen), "sha256": kernel.digest(frozen)}
            processes[name] = kernel.Process(frozen, name, output, args.timeout)
        work = [(case, batch, row) for (case, batch), row in zip(
            ((case, batch) for case in cases for batch in args.batches), data["rows"])]
        # Qualify the whole cohort before collecting any performance distribution.
        for case, batch, row in work:
            row["status"] = "running"
            print(f"{case['id']} batch{batch}: preflight", flush=True)
            try:
                if len(case["samples"]) < batch:
                    raise ValueError("insufficient independent input samples")
                evidence = qualify(processes, case, case["samples"][:batch], args)
                row.update(pilot=evidence["responses"], correctness=evidence["correctness"],
                           uv_identities=evidence["uv_identities"], status="qualified")
            except Exception as error:
                row.update(status="timeout" if isinstance(error, TimeoutError) else "failed", error=str(error))
            finally:
                kernel.save(path, data)
        if all(row["status"] == "qualified" for _, _, row in work):
            if args.mode == "timing":
                for case, batch, row in work:
                    samples = case["samples"][:batch]
                    pilot = row["pilot"]
                    row["status"] = "running"
                    print(f"{case['id']} batch{batch}: calibrated timing", flush=True)
                    try:
                        warmed = {name: checked_request(processes, name, case, samples, args, args.warmup, 1, pilot[name])
                                  for name in ("collier", "iregi")}
                        iterations = max(1, math.ceil(1.10 * args.block_ms * 1e6 /
                                                     min(x["total_ns"][0] for x in warmed.values())))
                        row["calibration"] = []
                        for trial in range(8):
                            if iterations > 1_000_000:
                                raise ValueError("calibrated iteration count exceeds fixed resource cap")
                            probes = {name: checked_request(processes, name, case, samples, args, 0, iterations, pilot[name])
                                      for name in ("collier", "iregi")}
                            row["calibration"].append({"iterations": iterations, "responses": probes})
                            minimum_ms = min(x["total_ns"][0] for x in probes.values()) * iterations / 1e6
                            if minimum_ms >= args.block_ms:
                                break
                            iterations = max(iterations + 1, math.ceil(iterations * 1.10 * args.block_ms / minimum_ms))
                        else:
                            raise ValueError("common calibration did not reach its target in eight trials")
                        row["iterations_per_block"] = iterations
                        row["warmup_blocks"] = []
                        for _ in range(5):
                            row["warmup_blocks"].append({name: checked_request(
                                processes, name, case, samples, args, 0, iterations, pilot[name])
                                for name in ("collier", "iregi")})
                        row["blocks"] = []
                        for block, order in enumerate(paired_orders(args.blocks, rng)):
                            entry = {"index": block, "order": order, "responses": {}}
                            row["blocks"].append(entry)
                            for name in order:
                                entry["responses"][name] = checked_request(
                                    processes, name, case, samples, args, 0, iterations, pilot[name])
                            entry["correctness"] = comparison(entry["responses"]["collier"],
                                                               entry["responses"]["iregi"], case, samples)
                            if entry["correctness"]["status"] != "passed":
                                raise ValueError("measured complete-array comparison failed")
                        times = {name: [b["responses"][name]["total_ns"][0] for b in row["blocks"]]
                                 for name in ("collier", "iregi")}
                        row["timings"] = {name: kernel.summarize(values) for name, values in times.items()}
                        row["minimum_observed_block_ms"] = min(value for values in times.values() for value in values) * iterations / 1e6
                        row["ratio"] = kernel.ratio_summary(times["collier"], times["iregi"], row["correctness"])
                        row["ratio"]["definition"] = "COLLIER / IREGI paired kernel latency; 99% bootstrap median CI, relative width<=2%"
                        if row["minimum_observed_block_ms"] < args.block_ms:
                            row["ratio"]["gate"] = "inconclusive-short-block"
                        row["status"] = "measured"
                    except Exception as error:
                        row.update(status="timeout" if isinstance(error, TimeoutError) else "failed", error=str(error))
                    finally:
                        kernel.save(path, data)
            # Recheck all cases after the whole cohort, including all pole probes.
            for case, batch, row in work:
                print(f"{case['id']} batch{batch}: postflight", flush=True)
                try:
                    row["postflight"] = qualify(processes, case, case["samples"][:batch], args)
                    for name in ("collier", "iregi"):
                        if comparison(row["postflight"]["responses"][name], row["pilot"][name],
                                      case, case["samples"][:batch])["status"] != "passed":
                            raise ValueError("postflight changed complete tensor outputs")
                    if args.mode == "correctness":
                        row["status"] = "passed"
                except Exception as error:
                    record_postflight_failure(row, error)
                finally:
                    kernel.save(path, data)
        else:
            for _, _, row in work:
                if row["status"] == "qualified":
                    row.update(status="not_run", error="cohort qualification failed; timing not started")
        completed = True
    finally:
        for process in processes.values():
            process.close()
        os.sched_setaffinity(0, old_affinity)
        for row in data["rows"]:
            if row["status"] in ("pending", "running"):
                row.update(status="not_run" if row["status"] == "pending" else "interrupted")
        data["source_unchanged"] = source_hashes() == sources
        data["elapsed_seconds"] = time.monotonic() - started
        data["binaries_unchanged"] = all(kernel.digest(v["path"]) == v["sha256"] for v in binaries.values())
        success_status = "passed" if args.mode == "correctness" else "measured"
        data["status"] = ("passed" if completed and data["source_unchanged"] and data["binaries_unchanged"]
                          and all(r["status"] == success_status for r in data["rows"]) else "failed")
        kernel.save(path, data)
    print(path)
    if data["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

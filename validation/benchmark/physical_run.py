"""CPU-pinned in-process physical-pipeline benchmark with independent correctness gates.

The JSONL Rust adapter owns every timer. Python transport, reference execution,
correctness comparisons and serialization are outside the measured intervals.
"""
import argparse
import copy
import datetime
import itertools
import json
import math
import os
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
import run as kernel
from build_physical import physical_asset_hashes

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "validation/physical"))
import compare_cli as physical

STAGES = ["graph_preparation", "evaluator_preparation", "numerator", "reduction",
          "contraction", "numerical_end_to_end", "reprepared_end_to_end"]
HOT_STAGES = ["numerator", "reduction", "contraction", "numerical_end_to_end"]
ALGORITHMS = {"ibp": "Ibp", "pv": "PassarinoVeltman", "hybrid": "Hybrid"}


def assets(case):
    return {
        "graph": Path(f"examples/graphs/{physical.CASES[case][0]}.dot"),
        "model": Path("fixtures/models/sm.json"),
        "input": Path(f"validation/physical/{case}-cli-input.json"),
        "madloop": Path(f"validation/physical/madloop/fixtures/{case}-helicity-1.json"),
    }


def request_configuration(case, precision, bits, accuracy_bits, algorithm, batch):
    paths = assets(case)
    sample = json.loads(paths["input"].read_text())
    identity = f"{case}-{precision}{bits if precision == 'float' else ''}-{algorithm}-batch{batch}"
    return {"id": identity, "model": paths["model"].read_text(), "dot": paths["graph"].read_text(),
            "component": [0] * physical.CASES[case][1],
            "input": {"samples": [copy.deepcopy(sample) for _ in range(batch)]},
            "precision": precision, "bits": bits, "accuracy_bits": accuracy_bits,
            "algorithm": ALGORITHMS[algorithm]}


def reference_records(case, oracle, directory):
    sample = json.loads(assets(case)["input"].read_text())
    records = []
    for mode in [0, 1, 2]:
        request = {"id": f"{case.replace('-', '_')}_physical_benchmark_mode{mode}",
                   "api": "tensor", "mode": mode, "rank": sample["rank"], "dimension_shift": 0,
                   "mu": sample["mu"], "snap": False, "threshold": "1e-6", "propagators": sample["propagators"]}
        record = {"mode": mode, "input": request}
        try:
            values, process = physical.evaluate(oracle, [request], allow_stop=True)
            record.update(returncode=process.returncode, results=values)
            (directory / f"reference-mode{mode}.stdout").write_text(process.stdout)
            (directory / f"reference-mode{mode}.stderr").write_text(process.stderr)
            if process.returncode or len(values) != 1 or values[0]["id"] != request["id"]:
                record["error"] = "original IREGI did not return the requested tensor array"
        except Exception as error:
            record["error"] = f"{type(error).__name__}: {error}"
        records.append(record)
    kernel.save(directory / "reference-records.json", records)
    return records


def check(output, configuration, case, references):
    sample = configuration["input"]["samples"][0]
    expected_bits = {"f64": 53, "dd": 106, "float": configuration["bits"]}[configuration["precision"]]
    if output["precision_bits"] != expected_bits:
        raise ValueError("adapter working precision differs from request")
    if output["precision_control"]["accuracy_bits"] != configuration["accuracy_bits"]:
        raise ValueError("adapter accuracy target differs from request")
    if output["algorithm_requested"] != configuration["algorithm"]:
        raise ValueError("adapter algorithm differs from request")
    settings = output["settings"]
    if (settings["convention"] != "OneLoop" or settings["tensor_weights"] != "Components"
            or settings["dimension_shift"] != 0 or settings["powers"] != [1] * len(sample["propagators"])
            or settings["propagators"] != len(sample["propagators"]) or settings["rank"] != sample["rank"]):
        raise ValueError("adapter reduction settings differ from physical fixture")
    if output["poles"] != ["uv1", "ir1", "ir2", "finite"]:
        raise ValueError("adapter pole ordering differs")
    if output["graph"]["name"] != physical.CASES[case][0]:
        raise ValueError("adapter graph identity differs")
    basis = [[indices.count(axis) for axis in range(4)]
             for rank in range(sample["rank"] + 1)
             for indices in itertools.combinations_with_replacement(range(4), rank)]
    if output["basis"] != basis:
        raise ValueError("adapter basis order or completeness differs from the canonical Cartesian basis")
    if sorted(record["mode"] for record in references) != [0, 1, 2]:
        raise ValueError("all three independent original IREGI mode records are required")
    if len(output["samples"]) != len(configuration["input"]["samples"]):
        raise ValueError("adapter returned an incomplete batch")
    madloop = json.loads(assets(case)["madloop"].read_text())
    rows = []
    # The independently established canonical original-IBP pentagon defect stays
    # visible; qualifying its PV/hybrid and MadLoop comparisons is explicit.
    required = [1, 2] if case == "gghhh" else [0, 1, 2]
    for lane, actual in enumerate(output["samples"]):
        if actual["status"] != "success" or actual["id"] != sample["id"]:
            raise ValueError(f"lane {lane} failed or returned another fixture identity")
        if len(actual["moments"]) != len(basis) or len(actual["integral"]) != 4:
            raise ValueError(f"lane {lane} returned incomplete tensors or contracted Laurent slots")
        for poles in [*actual["moments"], actual["integral"]]:
            if len(poles) != 4 or any(len(value) != 2 for value in poles):
                raise ValueError(f"lane {lane} returned malformed Laurent/complex shapes")
        single = dict(output, samples=[actual])
        comparisons = []
        for record in references:
            entry = {"mode": record["mode"], "passed": False}
            try:
                if "error" in record:
                    raise ValueError(record["error"])
                entry.update(physical.compare_tensors(single, sample, record["results"][0], 1e-10))
            except (ValueError, KeyError, TypeError, IndexError) as error:
                entry.update(status="reference_failed", reason=str(error))
            comparisons.append(entry)
        contracted = physical.compare_physical(single, sample, madloop, physical.CASES[case], 1e-10)
        passed = contracted["passed"] and all(entry["passed"] for entry in comparisons if entry["mode"] in required)
        rows.append({"lane": lane, "passed": passed, "tensor_comparisons": comparisons,
                     "physical_comparison": contracted})
    return {"passed": all(row["passed"] for row in rows), "required_original_modes": required,
            "all_original_modes_passed": all(entry["passed"] for row in rows for entry in row["tensor_comparisons"]),
            "retained_known_reference_issue": "validation/physical/canonical-reference-audit.json" if case == "gghhh" else None,
            "tolerance": 1e-10, "lanes": rows}


def summarized(values):
    result = kernel.summarize(values)
    if result is not None:
        low, high = result["ci99_ns"]
        result["relative_ci_width"] = (high - low) / result["median_ns"] if result["median_ns"] > 0 else None
        result["uncertainty"] = ("zero-observed-component" if result["relative_ci_width"] is None else
                                 "within-2-percent" if result["relative_ci_width"] <= 0.02 else "inconclusive-noise")
    return result


def validate_response(response, payload, identity):
    expected = "prepared" if payload["op"] == "prepare" else "measured"
    if response.get("id") != identity or response.get("status") != expected:
        raise ValueError("adapter failed or returned a mismatched operation/identity")
    if payload["op"] == "measure":
        for field in ["stage", "warmup", "iterations", "repeats"]:
            if response.get(field) != payload[field]:
                raise ValueError(f"adapter measurement contract differs: {field}")
        profiled = payload.get("profile", False)
        if response.get("profiled") is not profiled:
            raise ValueError("adapter profiling mode differs from measurement request")
        if len(response["total_ns"]) != payload["repeats"] or any(
                not math.isfinite(value) or value <= 0 for value in response["total_ns"]):
            raise ValueError("adapter returned missing or invalid timing values")
        if response["profile_order"] != ["arguments", "masters", "reduction", "total"]:
            raise ValueError("adapter profile component order differs")
        if len(response["profile_ns"]) != (payload["repeats"] if profiled else 0):
            raise ValueError("adapter returned missing or unexpected profiling blocks")
        for block in response["profile_ns"]:
            if len(block) != 4 or any(not math.isfinite(value) or value < 0 for value in block):
                raise ValueError("adapter returned invalid profile components")


def provenance_qualified(data):
    """Require stable identities for both the built code and live runner/checker.

    A retained revision protects the Rust source tree, but the Python harness
    still executes from the current workspace. Both must remain accounted for.
    Missing final checks fail closed, including interrupted provenance capture.
    """
    checks = data.get("build_provenance_checks", {})
    return all(checks.get(name) is True for name in [
        "successful_stable_build", "binary_matches_manifest",
        "sources_match_manifest", "assets_match_manifest",
    ]) and all(data.get(name) is False for name in [
        "source_changed_during_run", "workspace_source_changed_during_run",
        "assets_changed_during_run", "binaries_changed_during_run",
    ])


def configuration_rows(configurations):
    """Record every requested workload before any subprocess can fail."""
    return [{"id": configuration["id"], "case": case, "precision": configuration["precision"],
             "bits": configuration["bits"], "accuracy_bits": configuration["accuracy_bits"],
             "batch_width": len(configuration["input"]["samples"]),
             "status": "pending", "stages": {}, "profiled_components": {}}
            for case, configuration in configurations]


def finalize_rows(data, completed_normally):
    for row in data["rows"]:
        if row["status"] == "pending":
            row.update(status="not_run", error="run ended before this configuration started")
        elif row["status"] == "running":
            row.update(status="interrupted", error="run ended during this configuration")
    finished = completed_normally and all(
        row["status"] in {"measured", "failed", "timeout", "unsupported"}
        for row in data["rows"]
    )
    data["status"] = "complete" if finished else "interrupted"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rust", type=Path, default=Path("target/optimized/release/examples/physical_benchmark"))
    parser.add_argument("--build-manifest", type=Path, default=Path("target/benchmark/physical/physical-rust-build.json"))
    parser.add_argument("--oracle", type=Path, default=Path("target/reference/iregi-reference-original"))
    parser.add_argument("--cases", nargs="+", choices=physical.CASES, default=list(physical.CASES))
    parser.add_argument("--precision", nargs="+", choices=["f64", "dd", "float"], default=["f64"])
    parser.add_argument("--bits", nargs="+", type=int, default=[128])
    parser.add_argument("--accuracy-bits", type=int, default=53)
    parser.add_argument("--algorithm", choices=ALGORITHMS, default="hybrid")
    parser.add_argument("--batches", nargs="+", type=int, default=[1, 32])
    parser.add_argument("--stages", nargs="+", choices=STAGES, default=HOT_STAGES)
    parser.add_argument("--repeats", type=int, default=21)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--block-ms", type=float, default=30)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--cpu", type=int, default=min(os.sched_getaffinity(0)))
    parser.add_argument("--inputs-only", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("target/benchmark/physical/results.json"))
    args = parser.parse_args()
    if (min(args.batches) < 1 or min(args.bits) < 2 or args.accuracy_bits < 1 or args.repeats < 3
            or args.warmup < 0 or not math.isfinite(args.block_ms) or args.block_ms <= 0
            or not math.isfinite(args.timeout) or args.timeout <= 0):
        parser.error("positive sizes/precision/timeouts, repeats>=3 and warmup>=0 are required")
    if args.cpu not in os.sched_getaffinity(0):
        parser.error("requested CPU is outside the permitted affinity mask")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    configurations = [(case, request_configuration(case, precision, bits, args.accuracy_bits, args.algorithm, batch))
                      for case in args.cases for precision in args.precision
                      for bits in (args.bits if precision == "float" else [53 if precision == "f64" else 106])
                      for batch in args.batches]
    inputs = args.output.with_name(args.output.stem + "-inputs.json")
    kernel.save(inputs, [{"case": case, "configuration": configuration} for case, configuration in configurations])
    if args.inputs_only:
        print(inputs)
        return 0
    args.rust, args.oracle = args.rust.resolve(), args.oracle.resolve()
    if not args.rust.is_file() or not args.oracle.is_file():
        parser.error("missing benchmark/oracle executable")
    build = json.loads(args.build_manifest.read_text()) if args.build_manifest.exists() else {}
    source_root = Path(build.get("source_root", ROOT))
    sources = kernel.source_hashes(source_root)
    asset_hashes = physical_asset_hashes(ROOT)
    original_affinity = os.sched_getaffinity(0)
    thread_variables = ["RAYON_NUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"]
    original_threads = {name: os.environ.get(name) for name in thread_variables}
    for name in thread_variables:
        os.environ[name] = "1"
    os.sched_setaffinity(0, {args.cpu})
    data = {"schema_version": 1, "kind": "physical-pipeline-benchmark", "status": "running",
            "date": datetime.datetime.now(datetime.timezone.utc).isoformat(), "environment": kernel.environment(args.cpu),
            "build": build, "binary": {"path": str(args.rust), "sha256": kernel.digest(args.rust)},
            "oracle": {"path": str(args.oracle), "sha256": kernel.digest(args.oracle)},
            "assets_sha256": asset_hashes, "inputs": {"path": str(inputs), "sha256": kernel.digest(inputs)},
            "thread_environment": {name: os.environ[name] for name in thread_variables},
            "protocol": {"repeats": args.repeats, "warmup": args.warmup, "target_block_ms": args.block_ms,
                         "stage_order_seed": 271828, "transport_timed": False,
                         "batch_sampling": "each published physical fixture contains one point; batches repeat that exact point in independent lanes, not independent phase-space samples",
                         "cache_policy": "one prepared graph and numeric workspaces per configuration; numeric coefficients, masters and reduction recomputed each iteration; isolated contraction uses prepared immutable coefficients/moments; global structural caches remain warm",
                         "preparation": "first observed in persistent process, not cold-process latency; optional graph/evaluator/reprepared stages reconstruct objects with warm global caches",
                         "numerical_end_to_end": "single uninstrumented numerator+reduction+contraction call, not the sum of component medians",
                         "reference_timing": None, "performance_parity_claim": False,
                         "qualification": "stored MadLoop and original IREGI outputs establish correctness only; no physical timing ratio is inferred"},
            "rows": configuration_rows(configurations)}
    data["build_provenance_checks"] = {
        "successful_stable_build": build.get("status") == "complete" and build.get("provenance_qualified") is True,
        "binary_matches_manifest": build.get("binary_sha256") == data["binary"]["sha256"],
        "sources_match_manifest": build.get("source_sha256") == sources,
        "assets_match_manifest": build.get("assets_sha256") == asset_hashes,
    }
    kernel.save(args.output, data)
    engine = None
    reference_cache = {}
    rng = random.Random(271828)
    completed_normally = False
    try:
        for (case, configuration), row in zip(configurations, data["rows"], strict=True):
            row["status"] = "running"
            directory = args.output.parent / configuration["id"]
            directory.mkdir(parents=True, exist_ok=True)
            print(configuration["id"], flush=True)
            raw = (directory / "responses.jsonl").open("w")

            def request(payload):
                response = engine.request(json.dumps(payload) + "\n")
                raw.write(json.dumps({"request": payload if payload["op"] != "prepare" else {"op": "prepare", "id": configuration["id"]},
                                      "response": response}, allow_nan=False) + "\n")
                raw.flush()
                try:
                    validate_response(response, payload, configuration["id"])
                except (ValueError, KeyError, TypeError) as error:
                    row["engine_failure"] = response
                    raise ValueError(str(error)) from error
                checked = check(response["output"], configuration, case, reference_cache[case])
                if not checked["passed"]:
                    row["correctness"] = checked
                    raise ValueError("physical correctness gate failed; timing is not qualified")
                return response, checked

            try:
                if case not in reference_cache:
                    if kernel.digest(args.oracle) != data["oracle"]["sha256"]:
                        raise ValueError("original IREGI executable changed during benchmark")
                    reference_cache[case] = reference_records(case, args.oracle, directory)
                if engine is None:
                    if kernel.digest(args.rust) != data["binary"]["sha256"]:
                        raise ValueError("Rust benchmark executable changed before process restart")
                    engine = kernel.Process(args.rust, "physical-rust", args.output.parent, args.timeout)
                prepared, row["correctness"] = request({"op": "prepare", "configuration": configuration})
                row["first_observed_ns"] = prepared["first_observed_ns"]
                row["master_backend"] = prepared["master_backend"]
                row["execution"] = prepared["output"]["execution"]
                row["initial_output"] = prepared["output"]
                iterations = {}
                for stage in args.stages:
                    pilot, _ = request({"op": "measure", "id": configuration["id"], "stage": stage,
                                        "warmup": args.warmup, "iterations": 1, "repeats": 1})
                    iterations[stage] = max(1, min(1000000, math.ceil(args.block_ms * 1e6 / pilot["total_ns"][0])))
                    row["stages"][stage] = {"iterations_per_block": iterations[stage], "samples_ns": []}
                row["stage_orders"] = []
                for _ in range(args.repeats):
                    order = list(args.stages)
                    rng.shuffle(order)
                    row["stage_orders"].append(order)
                    for stage in order:
                        measured, _ = request({"op": "measure", "id": configuration["id"], "stage": stage,
                                              "warmup": 0, "iterations": iterations[stage], "repeats": 1})
                        row["stages"][stage]["samples_ns"].append(measured["total_ns"][0])
                        kernel.save(args.output, data)
                for stage, values in row["stages"].items():
                    values["summary"] = summarized(values["samples_ns"])
                if "reduction" in args.stages:
                    for name in ["arguments", "masters", "reduction", "total"]:
                        row["profiled_components"][name] = []
                    for _ in range(args.repeats):
                        profiled, _ = request({"op": "measure", "id": configuration["id"], "stage": "reduction",
                                              "warmup": 0, "iterations": iterations["reduction"], "repeats": 1, "profile": True})
                        for name, value in zip(profiled["profile_order"], profiled["profile_ns"][0], strict=True):
                            row["profiled_components"][name].append(value)
                    row["profiled_components"] = {name: summarized(values) for name, values in row["profiled_components"].items()}
                row["status"] = "measured"
            except (OSError, RuntimeError, TimeoutError, BrokenPipeError, ValueError, KeyError, TypeError, IndexError) as error:
                row["status"] = ("timeout" if isinstance(error, TimeoutError) else
                                 "unsupported" if "unsupported" in json.dumps(row.get("engine_failure", {})).lower() else "failed")
                row["error"] = f"{type(error).__name__}: {error}"
                if engine:
                    engine.close()
                engine = None
            finally:
                raw.close()
                kernel.save(args.output, data)
        completed_normally = True
    finally:
        if engine:
            engine.close()
        os.sched_setaffinity(0, original_affinity)
        for name, value in original_threads.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        finalize_rows(data, completed_normally)
        try:
            data["source_changed_during_run"] = kernel.source_hashes(source_root) != sources
            data["workspace_source_changed_during_run"] = kernel.source_hashes() != data["environment"]["source_sha256"]
            data["assets_changed_during_run"] = physical_asset_hashes(ROOT) != asset_hashes
            data["binaries_changed_during_run"] = (kernel.digest(args.rust) != data["binary"]["sha256"]
                                                    or kernel.digest(args.oracle) != data["oracle"]["sha256"])
            data["provenance_qualified"] = provenance_qualified(data)
        except (OSError, ValueError) as error:
            data["provenance_qualified"] = False
            data["final_provenance_error"] = f"{type(error).__name__}: {error}"
        data["counts"] = {status: sum(row["status"] == status for row in data["rows"]) for status in sorted({row["status"] for row in data["rows"]})}
        kernel.save(args.output, data)
    print(args.output)
    return 0 if data["provenance_qualified"] and all(
        row["status"] == "measured" for row in data["rows"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())

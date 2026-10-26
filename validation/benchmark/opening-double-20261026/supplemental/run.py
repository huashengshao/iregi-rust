#!/usr/bin/env python3
"""Four bounded, post-hoc denominator-order/PV candidates; no compilation.

The initial 38-candidate campaign is immutable. This supplement uses its exact
frozen binary and 215-file source guard after the N4 dotted IBP refusals. Only
the commutative denominator ordering, public algorithm and master policy vary.
"""
import argparse
import copy
import datetime
import importlib.util
import json
import os
from pathlib import Path
import statistics

ROOT = Path.cwd().resolve()
HERE = Path(__file__).resolve().parent
BASE = HERE.parent
PERMUTATION = [1, 0, 2, 3]
CASE_IDS = ("extended-n4-r6-dot2", "extended-n4-r6-dot3")
POLICIES = (("native-abc", "NativeF64Abc"), ("symbolica", "Symbolica"))

spec = importlib.util.spec_from_file_location("opening_double_producer", BASE / "run.py")
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def load(path):
    return json.loads(Path(path).read_text())


def binding(path):
    return {"path": relative(path), "sha256": producer.digest(path)}


def script_hashes():
    return {relative(HERE / name): producer.digest(HERE / name)
            for name in ("run.py", "README.md")}


def frozen():
    built = load(BASE / "build.json")
    sources = producer.source_hashes()
    if (built.get("status") != "built_and_frozen"
            or len(built["source_hashes"]) != 215
            or sources != built["source_hashes"]
            or producer.digest(ROOT / built["binary_path"]) != built["binary_sha256"]):
        raise RuntimeError("original frozen binary or 215-file source context changed")
    return built, sources


def prepared_rows():
    suite = load(BASE / "inputs.json")
    cases = {case["id"]: case for case in suite["cases"]}
    rows = []
    for case_id in CASE_IDS:
        case = cases[case_id]
        for policy_id, policy in POLICIES:
            original = copy.deepcopy(next(candidate["request"] for candidate in case["candidates"]
                                          if candidate["id"] == policy_id))
            if (original["powers"] != ([2, 1, 1, 1] if case_id.endswith("dot2") else [3, 1, 1, 1])
                    or original["algorithm"] != "Ibp" or original["numeric_type"] != "f64"
                    or original["working_bits"] != 53 or original["requested_bits"] != 53
                    or original["warmup"] != 3 or original["repeats"] != 11
                    or original["target_block_ns"] != 30_000_000
                    or original["maximum_iterations"] != 10_000):
                raise RuntimeError("original request no longer matches fixed supplemental scope")
            request = copy.deepcopy(original)
            candidate_id = "pv-permuted-" + policy_id
            request["id"] = case_id + "--" + candidate_id
            request["algorithm"] = "PassarinoVeltman"
            request["master_policy"] = policy
            request["powers"] = [original["powers"][index] for index in PERMUTATION]
            for sample, before in zip(request["samples"], original["samples"]):
                for key in ("shifts", "masses_squared"):
                    sample[key] = [before[key][index] for index in PERMUTATION]
            folder = HERE / "cases" / case_id / candidate_id
            rows.append({
                "case_id": case_id, "candidate_id": candidate_id,
                "original_request": original, "request": request,
                "permutation": PERMUTATION,
                "equivalence": "Exact denominator triple permutation; unchanged loop variable and Cartesian numerator, so no tensor transformation",
                "request_source": relative(folder / "request.json"),
                "result_source": relative(folder / "result.json"),
                "supervision_source": relative(folder / "supervision.json"),
            })
    return rows


def prepare(args):
    built, sources = frozen()
    if (HERE / "protocol.json").exists():
        raise RuntimeError("refusing to overwrite published/prepared supplemental protocol")
    rows = prepared_rows()
    for row in rows:
        path = ROOT / row["request_source"]
        if path.exists():
            raise RuntimeError("refusing to overwrite supplemental request")
        producer.save(path, row["request"])
        row["request_sha256"] = producer.digest(path)
    protocol = {
        "schema_version": 1, "supplement_id": "opening-double-permuted-pv-20261026",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "post_hoc_reason": "Added after the fixed IBP portfolio refused N4 rank-six dotted requests at binary64/request53; all original attempts remain retained",
        "fixed_additional_candidates": 4, "permutation": PERMUTATION,
        "original_inputs": binding(BASE / "inputs.json"),
        "original_build": binding(BASE / "build.json"),
        "binary_path": built["binary_path"], "binary_sha256": built["binary_sha256"],
        "source_hashes": sources, "supplemental_script_hashes": script_hashes(),
        "source_revision": built["source_revision"], "rows": rows,
    }
    producer.save(HERE / "protocol.json", protocol)
    print(json.dumps({"status": "prepared_four_fixed_candidates", "protocol": relative(HERE / "protocol.json")}))
    return 0


def checked_protocol():
    built, sources = frozen()
    protocol = load(HERE / "protocol.json")
    if (protocol["source_hashes"] != sources
            or protocol["supplemental_script_hashes"] != script_hashes()
            or protocol["original_inputs"] != binding(BASE / "inputs.json")
            or protocol["original_build"] != binding(BASE / "build.json")
            or protocol["binary_sha256"] != built["binary_sha256"]):
        raise RuntimeError("supplemental protocol/build/scripts changed")
    for expected, actual in zip(prepared_rows(), protocol["rows"]):
        if any(actual[key] != value for key, value in expected.items()):
            raise RuntimeError("supplemental candidate changed")
        if producer.digest(ROOT / actual["request_source"]) != actual["request_sha256"]:
            raise RuntimeError("supplemental request bytes changed")
    if len(protocol["rows"]) != 4:
        raise RuntimeError("supplemental candidate count differs from four")
    return built, protocol


def run(args):
    built, protocol = checked_protocol()
    outcomes = []
    for row in protocol["rows"]:
        request = ROOT / row["request_source"]
        result = ROOT / row["result_source"]
        supervision = ROOT / row["supervision_source"]
        if result.exists() or supervision.exists():
            if args.skip_existing:
                continue
            raise RuntimeError("refusing to overwrite supplemental native attempt")
        before = producer.source_hashes()
        command = ["taskset", "-c", str(args.cpu), str(ROOT / built["binary_path"]), str(request), str(result)]
        print(json.dumps({"starting": row["case_id"], "candidate": row["candidate_id"]}), flush=True)
        step = producer.supervise(command, result.parent / "native.log", args.timeout)
        after = producer.source_hashes()
        step.update({
            "case_id": row["case_id"], "candidate_id": row["candidate_id"], "cpu": args.cpu,
            "protocol": binding(HERE / "protocol.json"), "request_sha256": producer.digest(request),
            "binary_sha256": built["binary_sha256"],
            "binary_unchanged_after": producer.digest(ROOT / built["binary_path"]) == built["binary_sha256"],
            "source_hashes_before": before, "source_hashes_after": after,
            "source_hashes_unchanged": before == after == protocol["source_hashes"],
            "supplemental_script_hashes_after": script_hashes(),
            "supplemental_scripts_unchanged": script_hashes() == protocol["supplemental_script_hashes"],
            "environment_threads": {name: os.environ.get(name) for name in
                                    ("RAYON_NUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS")},
        })
        if result.exists():
            step.update(result_sha256=producer.digest(result), driver_status=load(result).get("status"))
        producer.save(supervision, step)
        outcomes.append(step)
        print(json.dumps({"finished": row["case_id"], "candidate": row["candidate_id"],
                          "status": step.get("driver_status"), "seconds": step["elapsed_seconds"]}), flush=True)
    return int(any(row["returncode"] != 0 for row in outcomes))


def summarize(args):
    built, protocol = checked_protocol()
    cases = {case["id"]: case for case in load(BASE / "inputs.json")["cases"]}
    attempts = []
    for row in protocol["rows"]:
        item = copy.deepcopy(row)
        item.update(status="unmeasured", timing_captured=False, eligible_optimistic_result=False)
        supervision_path, result_path = ROOT / row["supervision_source"], ROOT / row["result_source"]
        if supervision_path.exists():
            supervision = load(supervision_path)
            result = load(result_path) if result_path.exists() else {}
            bound = (supervision.get("request_sha256") == producer.digest(ROOT / row["request_source"])
                     and supervision.get("result_sha256") == (producer.digest(result_path) if result_path.exists() else None)
                     and supervision.get("protocol") == binding(HERE / "protocol.json")
                     and supervision.get("binary_sha256") == built["binary_sha256"]
                     and supervision.get("source_hashes_before") == protocol["source_hashes"]
                     and supervision.get("source_hashes_after") == protocol["source_hashes"])
            good = (bound and supervision.get("returncode") == 0 and not supervision.get("timed_out")
                    and supervision.get("owned_group_gone") is True
                    and supervision.get("binary_unchanged_after") is True
                    and supervision.get("source_hashes_unchanged") is True
                    and supervision.get("supplemental_scripts_unchanged") is True)
            item.update(status=result.get("status", "timeout_or_native_failure"),
                        result_sha256=producer.digest(result_path) if result_path.exists() else None,
                        supervision_sha256=producer.digest(supervision_path),
                        engine=result.get("workspace_engine"), plan_engine=result.get("plan_engine"),
                        plan_ns=result.get("plan_ns"), workspace_ns=result.get("workspace_ns"),
                        first_call_ns=result.get("first_call_ns"),
                        successful_finite_full_array=bool(result.get("all_successful_finite_full_arrays")),
                        timing_captured=bool(good and result.get("timing_qualified")),
                        first_output_statuses=[lane["status"] for lane in result.get("first_output", {}).get("lanes", [])],
                        accuracy=producer.accuracy(cases[row["case_id"]], result))
            if item["timing_captured"]:
                blocks = result["repeated_measurements"]
                fields = ("tirust_exclusive_ns", "scalar_masters_ns", "outer_total_ns")
                values = {field: [statistics.mean(call[field] for call in block["calls"]) / 1000
                                  for block in blocks] for field in fields}
                item["timing"] = {field.removesuffix("_ns") + "_us": producer.stats(data)
                                  for field, data in values.items()}
                item.update(repeats=len(blocks), calls_per_repeat=len(blocks[0]["calls"]),
                            total_timed_calls=sum(len(block["calls"]) for block in blocks),
                            maximum_additive_error_us=max(abs(call["outer_total_ns"] - call["tirust_exclusive_ns"]
                                                              - call["scalar_masters_ns"])
                                                          for block in blocks for call in block["calls"]) / 1000)
                if item["maximum_additive_error_us"] != 0:
                    raise ValueError("nonadditive supplemental timing split")
            item["eligible_optimistic_result"] = bool(item["timing_captured"]
                and item["successful_finite_full_array"] and item["accuracy"].get("relative_error_at_most_1e3"))
        attempts.append(item)
    summary = {
        "schema_version": 1, "supplement_id": protocol["supplement_id"],
        "protocol": binding(HERE / "protocol.json"), "supplemental_script_hashes": script_hashes(),
        "original_build": binding(BASE / "build.json"), "source_hashes": protocol["source_hashes"],
        "post_hoc_reason": protocol["post_hoc_reason"],
        "selection_notice": "Four additional public PV/denominator-order candidates added after original IBP refusals; preserve all initial 38 attempts. No precision or accuracy relaxation and no speed gate.",
        "attempts": attempts,
        "selected_additional_candidate_by_case": {
            case_id: min((item for item in attempts if item["case_id"] == case_id
                          and item["eligible_optimistic_result"]),
                         key=lambda item: item["timing"]["outer_total_us"]["mean"],
                         default={}).get("candidate_id") for case_id in CASE_IDS},
    }
    producer.save(HERE / "supplemental-summary.json", summary)
    print(json.dumps({"attempts": len(attempts), "eligible": sum(item["eligible_optimistic_result"] for item in attempts),
                      "selected": summary["selected_additional_candidate_by_case"]}))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run", "summarize"))
    parser.add_argument("--cpu", type=int, default=18)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()
    raise SystemExit(globals()[args.mode](args))

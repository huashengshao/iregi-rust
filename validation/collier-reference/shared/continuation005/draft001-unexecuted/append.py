"""Append only eight unexecuted reference requests; never time or rerun a case."""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time


ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
PRODUCER = ROOT / "validation/collier-reference/shared/attempt004/producer"
sys.path.insert(0, str(PRODUCER))
import support
import run_correctness as frozen


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def admit_structure(parent, inventory):
    """Validate saved data before constructing any child; used by negative tests."""
    if parent.get("status") != "capture-complete" or parent.get("guards_unchanged") is not True:
        raise ValueError("complete guarded parent capture required")
    expected_rows = {(c["id"], width) for c in parent["input_cases"] for width in (1, 32)}
    actual_rows = [(r["id"], r["batch_width"]) for r in parent["rows"]]
    if len(parent["input_cases"]) != 17 or len(actual_rows) != 34 or set(actual_rows) != expected_rows:
        raise ValueError("all17 families and34 original rows must remain visible")
    attempts = [(r, key, a) for r in parent["rows"] for key, values in r["request_attempts"].items() for a in values]
    if Counter(a["status"] for _, _, a in attempts) != {"validated-response": 239, "not_run": 8}:
        raise ValueError("exact239 completed/eight unexecuted parent requests required")
    if parent.get("isolated_request_count") != 247 or inventory.get("parent_validated_requests") != 239:
        raise ValueError("parent request count differs")
    family = "n7-r2-conditioned-cycle32"
    case = next(c for c in parent["input_cases"] if c["id"] == family)
    if (case["n"], case["rank"], inventory["family"], inventory["n"], inventory["rank"], inventory["batch_width"]) != (7, 2, family, 7, 2, 32):
        raise ValueError("different topology, rank or family")
    row = next(r for r in parent["rows"] if r["id"] == family and r["batch_width"] == 32)
    if set(row["responses"]) != {"iregi-Hybrid"} or inventory["existing_response_keys"] != ["iregi-Hybrid"]:
        raise ValueError("only previously completed Hybrid may be joined")
    samples = case["samples"]
    groups = support.scale_groups(case, samples)
    if len(samples) != 32 or {g["scale"] for g in groups} != {"3", "6"}:
        raise ValueError("unchanged32 lanes and exact scales3/6 required")
    wanted = {("iregi-PassarinoVeltman", "iregi", "PassarinoVeltman"),
              ("iregi-Ibp", "iregi", "Ibp"), ("generic-1", "generic", 1), ("generic-2", "generic", 2)}
    pending = [(r, key, a) for r, key, a in attempts if a["status"] == "not_run"]
    expected = {(key, engine, str(mode), scale) for key, engine, mode in wanted for scale in ("3", "6")}
    observed = {(key, a["engine"], str(a["mode"]), a["scale"]) for _, key, a in pending}
    supplied = inventory["remaining_group_requests"]
    if len(supplied) != 8 or observed != expected or any(r is not row for r, _, _ in pending):
        raise ValueError("pending set must contain exactly the eight unexecuted requests")
    supplied_set = {(a["response_key"], a["engine"], str(a["mode"]), a["scale"]) for a in supplied}
    if supplied_set != expected:
        raise ValueError("inventory contains duplicate, completed or different policy requests")
    for item in supplied:
        group = next(g for g in groups if g["scale"] == item["scale"])
        if item["lane_indices"] != group["lane_indices"]:
            raise ValueError("original group lane order differs")
        proof_keys = [support.proof_key(s, 7) for s in group["samples"]]
        if item["input_proof_keys"] != proof_keys:
            raise ValueError("input proof key changed")
        text = (support.original_iregi_request(case, group["samples"], item["mode"]) if item["engine"] == "iregi"
                else support.collier_request(case, group["samples"], item["mode"]))
        if item["wire_request"] != text or item["wire_request_sha256"] != hashlib.sha256(text.encode()).hexdigest():
            raise ValueError("wire request differs from exact unchanged input")
    if parent["binaries"] != inventory["binaries"] or parent["source_binary_input_guards"] != inventory["source_binary_input_guards"]:
        raise ValueError("binary/source identity differs")
    return case, row, groups


def load_admitted(inventory_path):
    inventory = json.loads(inventory_path.read_text())
    bindings = [inventory["parent_capture"], inventory["parent_qualification"]]
    for item in bindings:
        if digest(ROOT/item["path"]) != item["sha256"]:
            raise ValueError("durable parent artifact changed")
    qualification = json.loads((ROOT/inventory["parent_qualification"]["path"]).read_text())
    if qualification["artifacts"]["capture"]["sha256"] != inventory["parent_capture"]["sha256"]:
        raise ValueError("parent capture is not bound by qualification")
    parent = json.loads(gzip.decompress((ROOT/inventory["parent_capture"]["path"]).read_bytes()))
    case, row, groups = admit_structure(parent, inventory)
    for mapping in (inventory["producer_sources"], inventory["source_binary_input_guards"], qualification["producer"]):
        for path, sha in mapping.items():
            if digest(ROOT/path) != sha:
                raise ValueError("frozen source, input or binary guard changed")
    for info in inventory["binaries"].values():
        if digest(ROOT/info["path"]) != info["sha256"]:
            raise ValueError("reference binary changed")
    if digest(HERE/"PLAN.md") != inventory["proposal_sha256"]:
        raise ValueError("reviewed proposal changed")
    return inventory, parent, case, row, groups


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--cpu", type=int, default=26)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT/"target") or args.cpu not in os.sched_getaffinity(0):
        parser.error("new project target directory and available CPU required")
    review = json.loads(args.review.read_text())
    local_files = [HERE/"append.py", HERE/"test_admission.py", HERE/"inventory.json", HERE/"PLAN.md"]
    sources = {str(p.relative_to(ROOT)): digest(p) for p in local_files}
    if review.get("status") != "source_review_passed" or review.get("blockers") != [] or review.get("sources_sha256") != sources:
        raise ValueError("independent source review must bind complete append runner, tests and inventory")
    inventory, parent, case, prior_row, groups = load_admitted(HERE/"inventory.json")
    output.mkdir(parents=True)
    path = output/"results.json"
    data = {"kind": "collier-exact-eight-request-correctness-append", "status": "running", "cpu": args.cpu,
            "performance_evidence": False, "compile_performed": False, "request_cap_seconds": 20,
            "total_request_cap_seconds": 120, "parent_capture": inventory["parent_capture"],
            "parent_qualification": inventory["parent_qualification"], "sources_sha256": sources,
            "review_sha256": digest(args.review),
            "attempts": [{**item, "status": "not_run", "response": None} for item in inventory["remaining_group_requests"]],
            "all_original_rows": copy.deepcopy(parent["rows"])}
    joined = next(r for r in data["all_original_rows"] if r["id"] == case["id"] and r["batch_width"] == 32)
    joined["append005_responses"] = {"iregi-Hybrid": copy.deepcopy(prior_row["responses"]["iregi-Hybrid"])}
    started = time.monotonic()
    deadline = started+120
    previous = os.sched_getaffinity(0)
    support.kernel.save(path, data)
    try:
        os.sched_setaffinity(0, {args.cpu})
        for ordinal, (item, attempt) in enumerate(zip(inventory["remaining_group_requests"], data["attempts"])):
            attempt["status"] = "pending"
            support.kernel.save(path, data)
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                attempt.update(status="not_run", error="Fixed append deadline exhausted")
                continue
            process = None
            try:
                info = inventory["binaries"][item["engine"]]
                process = support.kernel.Process(ROOT/info["path"], f"request-{ordinal:02d}", output, min(20, remaining))
                response = process.request(item["wire_request"])
                attempt.update(status="returned", response=response)
                support.kernel.save(path, data)
                support.kernel.validate_response(response, case)
                frozen.validate_engine_header(response, case, item["engine"], item["mode"])
                if len(response.get("lanes", [])) != len(item["lane_indices"]):
                    raise ValueError("returned lane count differs")
                attempt["status"] = "validated-response"
            except Exception as error:
                attempt.update(status="timeout" if isinstance(error, TimeoutError) else "failed", error=f"{type(error).__name__}: {error}")
            finally:
                if process is not None:
                    try:
                        process.close()
                        attempt["child_exit_code"] = process.process.returncode
                        if process.process.returncode != 0:
                            attempt.update(status="failed", error="Reference child exited nonzero")
                    except Exception as error:
                        attempt.update(status="failed", close_error=f"{type(error).__name__}: {error}")
                support.kernel.save(path, data)
        for key in ("iregi-PassarinoVeltman", "iregi-Ibp", "generic-1", "generic-2"):
            values = [a for a in data["attempts"] if a["response_key"] == key]
            by_scale = {a["scale"]: a for a in values}
            if len(values) == 2 and all(a["status"] == "validated-response" for a in values):
                joined["append005_responses"][key] = support.assemble_groups(case, case["samples"], groups,
                    [by_scale[g["scale"]]["response"] for g in groups])
        reference = joined["append005_responses"]["iregi-Hybrid"]
        wire = [support.wire_sample(s, 7) for s in case["samples"]]
        joined["append005_checks"] = {}
        for key, response in joined["append005_responses"].items():
            checks = {"native_array_agreement": support.common.comparison(response, reference, case, wire),
                      "uv_identities": frozen.uv_check(response, case, wire)}
            if key.startswith("generic-"):
                try:
                    support.common.validate_poles(response, wire)
                    checks["pole_probes"] = {"status": "passed"}
                except Exception as error:
                    checks["pole_probes"] = {"status": "failed", "error": str(error)}
            joined["append005_checks"][key] = checks
        joined["append005_status"] = ("complete-rejected-or-disagrees" if len(joined["append005_responses"]) == 5
                                      else "resource-or-transport-incomplete")
        if len(joined["append005_responses"]) == 5 and all(check["status"] == "passed"
                for checks in joined["append005_checks"].values() for check in checks.values()):
            joined["append005_status"] = "all-policies-admitted"
        data["status"] = "capture-complete"
    except Exception as error:
        data.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        os.sched_setaffinity(0, previous)
        data["elapsed_seconds"] = time.monotonic()-started
        data["attempt_status_counts"] = dict(Counter(a["status"] for a in data["attempts"]))
        data["guards_unchanged"] = all(digest(ROOT/p) == sha for p, sha in inventory["source_binary_input_guards"].items())
        data["guards_unchanged"] &= all(digest(ROOT/p) == sha for p, sha in sources.items())
        data["guards_unchanged"] &= digest(args.review) == data["review_sha256"]
        data["guards_unchanged"] &= all(digest(ROOT/inventory[key]["path"]) == inventory[key]["sha256"]
                                       for key in ("parent_capture", "parent_qualification"))
        if not data["guards_unchanged"]:
            data.update(status="failed", error="source/input/binary guard changed")
        support.kernel.save(path, data)
    print(path)
    if data["status"] != "capture-complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

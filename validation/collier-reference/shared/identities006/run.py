"""One correctness-only capture of the exact46 Symbolica-prepared requests."""
from collections import Counter
import argparse
import gzip
import json
import os
from pathlib import Path
import time

import protocol


ROOT, HERE = protocol.ROOT, protocol.HERE
support = protocol.support


def source_files():
    return [HERE/"run.py", HERE/"protocol.py", HERE/"test_protocol.py", HERE/"prepared001/qualification.json",
            ROOT/"docs/research/collier-n5-identities.md"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--cpu", type=int, default=26)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT/"target") or args.cpu not in os.sched_getaffinity(0):
        parser.error("new project target directory and available CPU required")
    sources = {str(p.relative_to(ROOT)): protocol.digest(p) for p in source_files()}
    review = json.loads(args.review.read_text())
    if review.get("status") != "source_review_passed" or review.get("blockers") != [] or review.get("sources_sha256") != sources:
        raise ValueError("independent review must bind exact capture/comparator/test/preparation sources")
    prepared, parent, cases = protocol.load_prepared()
    frozen = json.loads((protocol.PARENT/"qualification.json").read_text())
    guards = {**prepared["guards"], **parent["source_binary_input_guards"], **sources,
              str(args.review.resolve().relative_to(ROOT)): protocol.digest(args.review)}
    guards.update(frozen["producer"])
    output.mkdir(parents=True)
    path = output/"results.json"
    data = {"kind": "n5-independent-pinch-trace-routing-correctness", "status": "running", "cpu": args.cpu,
            "performance_evidence": False, "build_performed": False, "extra_reduction_requests": False,
            "request_cap_seconds": 20, "request_deadline_seconds": 120, "planned_requests": 46,
            "guards": guards, "binaries": parent["binaries"], "prepared_cases": cases,
            "original34_rows": [{k: row[k] for k in ("id", "n", "rank", "batch_width", "status")} for row in parent["rows"]],
            "parent005_completion_note": "The eight resource-unexecuted parent004 requests were captured separately in shared/attempt005; this N5-only identity study does not rerun them.",
            "attempts": [{**item, "status": "not_run", "response": None} for item in prepared["reference_request_inventory"]],
            "assembled_responses": [], "identities": None}
    support.kernel.save(path, data)
    previous = os.sched_getaffinity(0)
    started = time.monotonic()
    deadline = started+120
    try:
        os.sched_setaffinity(0, {args.cpu})
        for ordinal, attempt in enumerate(data["attempts"]):
            case = next(c for c in cases if c["id"] == attempt["case"])
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                attempt["error"] = "Fixed correctness deadline exhausted; not run"
                continue
            attempt["status"] = "pending"
            child = None
            try:
                info = parent["binaries"][attempt["engine"]]
                child = support.kernel.Process(ROOT/info["path"], f"request-{ordinal:02d}", output, min(20, remaining))
                response = child.request(attempt["wire_request"])
                attempt.update(status="returned", response=response)
                support.kernel.save(path, data)
                support.kernel.validate_response(response, case)
                if attempt["engine"] == "generic":
                    support.validate_collier_header(response, case, attempt["mode"])
                if len(response.get("lanes", [])) != len(attempt["lane_indices"]):
                    raise ValueError("reference returned a different lane count")
                attempt["status"] = "validated-response"
            except Exception as error:
                attempt.update(status="timeout" if isinstance(error, TimeoutError) else "failed", error=f"{type(error).__name__}: {error}")
            finally:
                if child is not None:
                    try:
                        child.close()
                        attempt["child_exit_code"] = child.process.returncode
                        if child.process.returncode != 0:
                            attempt.update(status="failed", error="reference child exited nonzero")
                    except Exception as error:
                        attempt.update(status="failed", close_error=f"{type(error).__name__}: {error}")
                support.kernel.save(path, data)
        responses = {}
        for case in cases:
            groups = support.scale_groups(case, case["samples"])
            policies = {a["engine"]+"-"+str(a["mode"]) for a in data["attempts"] if a["case"] == case["id"]}
            for policy in sorted(policies):
                values = [a for a in data["attempts"] if a["case"] == case["id"] and a["engine"]+"-"+str(a["mode"]) == policy]
                group_values = {a["scale"]: a for a in values}
                if len(values) == len(groups) and all(a["status"] == "validated-response" for a in values):
                    response = support.assemble_groups(case, case["samples"], groups,
                        [group_values[g["scale"]]["response"] for g in groups])
                    responses[(case["id"], policy)] = response
                    data["assembled_responses"].append({"case": case["id"], "policy": policy, "response": response})
        data["identities"] = protocol.compare_identities(prepared, parent, responses)
        data["status"] = "capture-complete"
        data["qualification"] = ("identities-passed" if data["identities"]["status"] == "passed"
                                  and all(a["status"] == "validated-response" for a in data["attempts"])
                                  else "native-failure-disagreement-or-incomplete")
    except Exception as error:
        data.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        os.sched_setaffinity(0, previous)
        data["elapsed_seconds"] = time.monotonic()-started
        data["attempt_status_counts"] = dict(Counter(a["status"] for a in data["attempts"]))
        data["guards_unchanged"] = all(protocol.digest(ROOT/p) == sha for p, sha in guards.items())
        if not data["guards_unchanged"]:
            data.update(status="failed", error="source/input/binary/preparation guard changed")
        support.kernel.save(path, data)
    print(path)
    if data["status"] != "capture-complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

"""Replay durable hashes and lane gathers without executing any reference code."""
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import tarfile


ROOT = Path.cwd()
PACKAGE = ROOT/"validation/collier-reference/shared/attempt004"
sys.path.insert(0, str(PACKAGE/"producer"))
import support


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    checks, members, accepted_slots, diagnostic_nulls = 0, 0, 0, 0

    def require(condition, message):
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    qualification = json.loads((PACKAGE/"qualification.json").read_text())
    bindings = {str((PACKAGE/"qualification.json").relative_to(ROOT)): sha(PACKAGE/"qualification.json"),
                str(Path(__file__).resolve().relative_to(ROOT)): sha(__file__)}
    for name, artifact in qualification["artifacts"].items():
        path = ROOT/artifact["path"]
        require(sha(path) == artifact["sha256"], "durable artifact hash differs")
        bindings[artifact["path"]] = artifact["sha256"]
        if name.endswith("-artifacts"):
            contents = gzip.decompress(path.read_bytes())
            require(hashlib.sha256(contents).hexdigest() == artifact["uncompressed_archive_sha256"], "archive payload differs")
            observed = set()
            with tarfile.open(path, "r:gz") as archive:
                for member in archive:
                    require(member.isfile() and not Path(member.name).is_absolute() and ".." not in Path(member.name).parts,
                            "unexpected archive member type/path")
                    blob = archive.extractfile(member).read()
                    require(hashlib.sha256(blob).hexdigest() == artifact["files"][member.name], "archive member differs")
                    require(not blob.startswith((b"\x7fELF", b"!<arch>\n")), "compiled artifact in durable evidence")
                    observed.add(member.name)
                    members += 1
            require(observed == set(artifact["files"]), "archive inventory incomplete")
        elif name in ("inputs", "build", "capture"):
            blob = gzip.decompress(path.read_bytes())
            require(hashlib.sha256(blob).hexdigest() == artifact["uncompressed_sha256"], "compressed JSON differs")
    for path, expected in qualification["producer"].items():
        require(sha(ROOT/path) == expected, "frozen producer differs")
        bindings[path] = expected
    parent = json.loads(gzip.decompress((PACKAGE/"capture.json.gz").read_bytes()))
    require(parent["guards_unchanged"] is True and parent["status"] == "capture-complete", "unguarded parent")
    require(len(parent["input_cases"]) == 17 and len(parent["rows"]) == 34, "family/row omitted")
    cases = {c["id"]: c for c in parent["input_cases"]}
    require(len(cases) == 17, "duplicate case")
    require({(r["id"], r["batch_width"]) for r in parent["rows"]} == {(key, width) for key in cases for width in (1, 32)},
            "duplicate or omitted fixed row")
    attempts, assembled = [], 0
    for row in parent["rows"]:
        case = cases[row["id"]]
        samples = case["samples"][:row["batch_width"]]
        groups = support.scale_groups(case, samples)
        require(row["scale_groups"] == [{"scale": g["scale"], "lane_indices": g["lane_indices"]} for g in groups],
                "saved scale grouping differs from unchanged samples")
        if case["n"] <= 4:
            require(row["iregi_frozen_regression"]["status"] == "passed", "fixed IREGI regression changed")
            require(all(p["old_wrapper_regression"]["status"] == "passed" for p in row["collier_policies"].values()),
                    "fixed wrapper regression changed")
        for key, values in row["request_attempts"].items():
            attempts.extend(values)
            require(len(values) == len(groups), "missing planned group request")
            all_returned = all(a["status"] == "validated-response" for a in values)
            require((key in row["responses"]) == all_returned, "incomplete group promoted or complete result dropped")
            for group, attempt in zip(groups, values):
                require(attempt["scale"] == group["scale"] and attempt["lane_indices"] == group["lane_indices"], "group order changed")
                if attempt["status"] == "not_run":
                    require(attempt["response"] is None, "unexecuted request has invented response")
                    continue
                require(attempt["status"] == "validated-response" and attempt["child_exit_code"] == 0, "unexpected child failure")
                text = (support.original_iregi_request(case, group["samples"], attempt["mode"]) if attempt["engine"] == "iregi"
                        else support.collier_request(case, group["samples"], attempt["mode"]))
                require(attempt["request"] == text, "wire input changed")
                response = attempt["response"]
                require(len(response["lanes"]) == len(group["samples"]), "native lane count differs")
                if attempt["engine"] == "generic":
                    support.validate_collier_header(response, case, attempt["mode"])
                    checks += 1
                elif attempt["engine"] == "wrapped":
                    require(response.get("collier_mode") == attempt["mode"], "legacy wrapper policy differs")
                if all_returned:
                    aggregate = row["responses"][key]
                    for local, original in enumerate(group["lane_indices"]):
                        require(aggregate["lanes"][original] == response["lanes"][local], "native lane gather changed")
                        if response.get("pole_check_errors") is not None:
                            require(aggregate["pole_check_errors"][original] == response["pole_check_errors"][local], "pole gather changed")
                for lane in response["lanes"]:
                    count = math.comb(case["rank"]+4, 4)
                    if lane["status"] == "success":
                        require(len(lane["moments"]) == count, "accepted Cartesian array incomplete")
                        for moment in lane["moments"]:
                            require(len(moment) == 4, "accepted Laurent array incomplete")
                            for z in moment:
                                require(isinstance(z, list) and len(z) == 2 and all(type(x) in (int, float) and math.isfinite(x) for x in z),
                                        "accepted nonfinite/missing complex slot")
                                accepted_slots += 1
                    else:
                        require(lane["moments"] is None, "rejected lane promoted")
                        for moment in lane.get("diagnostic_moments", []) or []:
                            diagnostic_nulls += sum(z is None for z in moment)
            if all_returned:
                assembled += 1
                require(row["responses"][key]["stable"] == all(a["response"]["stable"] for a in values), "stability gather changed")
    counts = dict(Counter(a["status"] for a in attempts))
    require(counts == {"validated-response": 239, "not_run": 8}, "actual request inventory differs")
    require(assembled == 198 and parent["isolated_request_count"] == 247, "aggregate/request count differs")
    require(sum(r["status"] == "accepted-COLI" for r in parent["rows"]) == 17, "admitted row count differs")
    require(sum(r["n"] == 4 and r["status"] != "accepted-COLI" for r in parent["rows"]) == 6, "old N4 failures hidden")
    result = {"kind": "collier-attempt004-durable-and-gather-audit", "status": "passed", "assertions": checks,
              "archive_members_checked": members, "accepted_complex_pairs_checked": accepted_slots,
              "null_rejected_diagnostic_slots_retained": diagnostic_nulls,
              "family_count": 17, "row_count": 34, "assembled_responses": assembled, "group_status_counts": counts,
              "bindings": bindings, "reference_kernels_executed": False, "performance_evidence": False,
              "limits": "Hash/schema/lane-gather audit only; new numerical comparison and routing/trace identities are separate"}
    path = PACKAGE/"audit-durable-gather.json"
    if path.exists():
        raise ValueError("preserve existing audit receipt")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()

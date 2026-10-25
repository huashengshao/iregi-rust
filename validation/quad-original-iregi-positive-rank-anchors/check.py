#!/usr/bin/env python3
"""Portable source/provenance and exact saved pole replay; no native jobs."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal, localcontext
import argparse
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = "validation/quad-original-iregi-rank7-adjudication"
PRIVATE = "target/quad-iregi-source-audit"
Q = PRIVATE + "/future-positive-rank-requests"
CAPTURE = Q + "/capture-001"
HISTORICAL = "/shared/external/iregi/iregi-rust/"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {"sha256": sha(body), "bytes": len(body)}


def load(body):
    return json.loads(body, parse_float=str)


def display(squared):
    with localcontext() as context:
        context.prec = 100
        return str((Decimal(squared.numerator) / Decimal(squared.denominator)).sqrt())


def restore(manifest):
    for name, expected in manifest["capsule_files"].items():
        require(desc((HERE / name).read_bytes()) == expected, "capsule file hash")
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    require(actual == set(manifest["capsule_files"]) | {"manifest.json"}, "capsule exact file inventory")
    for name, expected in manifest["parent_files"].items():
        require(desc((ROOT / name).read_bytes()) == expected, "inherited parent file hash " + name)
    require(sha((ROOT / PARENT / "manifest.json").read_bytes()) == "7c27b1eded867c4373ee6111b54a1f88a1d944c61cd1a871c1403947c008fe07", "exact N6 source-proof capsule")
    source = ROOT / PARENT / "check.py"
    require(sha(source.read_bytes()) == "4e470143340740ff736087ca542d2ea2dc76723073ba9995b10eca3bd1880c28", "independent stdlib parent checker")
    spec = importlib.util.spec_from_file_location("preserved_quad_n6_source_saved_mechanics", source)
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    parent_manifest = load((ROOT / PARENT / "manifest.json").read_bytes())
    files = parent.restore(parent_manifest)
    inherited_receipts = parent.receipt_replay(files, parent_manifest)
    inherited_numbers = parent.numeric_replay(files)
    members = parent.read_archive((HERE / "payload.tar.gz").read_bytes(), manifest["payload_members"])
    origins = load((HERE / "payload-origins.json").read_bytes())
    require(set(origins) == set(manifest["preserved_files"]) | set(manifest["inherited_aliases"]), "exact origin inventory")
    for name, record in manifest["preserved_files"].items():
        parent.safe(name)
        body = members[record["member"]]
        require(desc(body) == {k: record[k] for k in ["sha256", "bytes"]}, "own saved alias identity")
        require(name not in files or files[name] == body, "parent/child file collision")
        require(desc(body) == {k: origins[name][k] for k in ["sha256", "bytes"]}, "own origin copy identity")
        files[name] = body
    for name, record in manifest["inherited_aliases"].items():
        parent.safe(name)
        body = files[record["inherited_source"]]
        require(desc(body) == {k: record[k] for k in ["sha256", "bytes"]} == {k: origins[name][k] for k in ["sha256", "bytes"]}, "inherited source alias identity")
        require(name not in files or files[name] == body, "inherited alias collision")
        files[name] = body
    fixture = "validation/highpoint-seven-point-current-cargo/fixture.json"
    body = (ROOT / fixture).read_bytes()
    require(sha(body) == "6c78096e83a399acd111137115505eae10da620b9dd68b6ead56eb2fa06489d2", "exact positive-F N7 fixture")
    files[fixture] = body
    return files, parent, {"N6_records_replayed": inherited_numbers["records"], "N6_old_binary64_gate": inherited_numbers["old_binary64_gate"],
                           "N6_saved_group_attestations_replayed": inherited_receipts["saved_owned_group_attestations_checked"],
                           "N6_full_rank7_or_current_cargo_or_performance_qualified": False}


def replay(files, parent, manifest):
    def read(name):
        return load(files[Q + "/" + name])
    protocol = read("protocol.json")
    proposal = read("proposal.json")
    run = read("capture-001/run.json")
    saved = read("capture-001/validation.json")
    gate = read("capture-001/pole-zero-exact.json")
    review = read("source-review.json")
    grant = read("root-execution-grant.json")
    independent = read("independent-saved-review.json")
    require(grant["status"] == "granted" and grant["grantor"] == "/root" and grant["stages"] == ["runtime"]
            and grant["recipe_sha256"] == sha(files[Q + "/protocol.json"]) and grant["review_sha256"] == sha(files[Q + "/source-review.json"]), "exact root grant")
    require(review["status"] == "passed_independent_source_runner_comparator_review" and review["findings"] == []
            and review["recipe_sha256"] == grant["recipe_sha256"], "independent source admission")
    require(independent["status"] == "passed_independent_quad_future_reference_raw_and_N7_zero_pole_review" and independent["findings"] == []
            and independent["checker_sha256"] == sha(files["target/resume-20261025-review/audit_quad_future_saved.py"]), "independent saved audit/checker")
    require(run["status"] == "passed" and run["inputs_unchanged"] is True and run["changed_inputs"] == {}
            and run["cleanup_errors"] == [] and run["cancellation"] is None, "terminal reference capture")
    require(run["bound_seconds"] == 180 and run["cleanup_reserve_seconds"] == 20 and Fraction(run["elapsed_seconds"]) < 180
            and run["executed_native_integral_requests"] == 4 and len(run["steps"]) == 4, "finite original four-request cohort")
    expected_inputs = dict(protocol["bindings"])
    for name in ["protocol.json", "source-review.json", "root-execution-grant.json"]:
        expected_inputs[HISTORICAL + Q + "/" + name] = sha(files[Q + "/" + name])
    require(run["inputs"] == expected_inputs and len(expected_inputs) == 274 and len(protocol["bindings"]) == 271, "complete exact source/product admission map")
    inherited_build = load(files[PRIVATE + "/build-v6-001/build.json"])
    require(protocol["prior_build_recipe_sha256"] == sha(files[PRIVATE + "/recipe-v6.json"])
            and run["runtime_binary_sha256"] == run["outputs"]["iregi-reference-quad"] == protocol["prior_binary_sha256"]
            == inherited_build["outputs"]["iregi-reference-quad"], "historical inherited and owned binary chain")
    require(set(run["outputs"]) == {"iregi-reference-quad"} | {f"{prefix}-{i}.{ext}" for i in range(4) for prefix, ext in [("request", "stdout"), ("request", "stderr"), ("step", "log")]}, "all raw output inventory")
    for name, expected in run["outputs"].items():
        key = CAPTURE + "/" + name
        if key in files:
            require(sha(files[key]) == expected, "preserved raw output hash")
        else:
            require(manifest["omitted_compiled_products"][key]["captured_sha256"] == expected, "omitted copied binary provenance")
    by_origin = {}
    for parent_origins in [load((ROOT / PARENT / "payload-origins.json").read_bytes()), load((HERE / "payload-origins.json").read_bytes())]:
        for name, row in parent_origins.items():
            by_origin.setdefault(row["origin"], set()).add(sha(files[name]))
    for name, body in files.items():
        if name.startswith("validation/"):
            by_origin.setdefault(HISTORICAL + name, set()).add(sha(body))
    available = historical = 0
    for path, expected in expected_inputs.items():
        if path in by_origin:
            require(expected in by_origin[path], "preserved input guard " + path)
            available += 1
        else:
            historical += 1
    fixture = load(files["validation/highpoint-seven-point-current-cargo/fixture.json"])
    conditioned = load(files["validation/highpoint-thin-n6-rank7-phase/reference/fixture-conditioned_masses.json"])
    sample = fixture["samples"][0]
    require(fixture["rank"] == 0 and proposal["source_fixture_original_rank_metadata"] == 0, "original fixture rank metadata not relabeled")
    require(sample["propagators"][:5] == conditioned["samples"][0]["propagators"][:5], "same explicit first-five N5 fixture")
    require(parent.scale2(sample, 7) == 4, "exact fixture natural scale Q=2")
    pole_records = {(r["id"], r["moment"], r["slot"]): r for r in gate["records"]}
    require(len(pole_records) == len(gate["records"]) == gate["total_pole_slots"] == 1050
            and gate["squared_threshold_exact"] == "1/100000000000000000000", "all unique exact N7 pole records")
    groups = []
    summaries = []
    total = checked_poles = 0
    for ordinal, (case, step) in enumerate(zip(protocol["runtime"]["cases"], run["steps"])):
        require((case["propagators"], case["rank"], case["moments"], case["complex_slots"], case["cap_seconds"]) == [(7, 1, 5, 20, 10), (7, 2, 15, 60, 15), (7, 7, 330, 1320, 45), (5, 7, 330, 1320, 45)][ordinal], "four exact requested shapes/caps")
        require(case["mode"] == 0 and case["algorithm"] == "original_IREGI_IBP" and case["fixture_sha256"] == "6c78096e83a399acd111137115505eae10da620b9dd68b6ead56eb2fa06489d2", "ordinary original IBP reference scope")
        props = sample["propagators"][:case["propagators"]]
        require(case["exact_propagators"] == props and Fraction(case["exact_scale"]) == Fraction(sample["mu"]), "exact fixture routing/masses/powers/scale")
        request_name = case["input"].removeprefix(HISTORICAL)
        text = files[request_name].decode()
        lines = text.splitlines()
        header = lines[0].split()
        require(header == ["EVAL", case["id"], "tensor", "0", str(case["propagators"]), str(case["rank"]), "0", "3", "0", "1e-6"]
                and len(lines) == case["propagators"] + 2 and lines[-1] == "QUIT", "explicit ordinary/unit-power/no-snap request header")
        for raw, expected in zip(lines[1:-1], props):
            row = raw.split()
            require(len(row) == 7 and [Fraction(v) for v in row[:4]] == [Fraction(v) for v in expected["shift"]]
                    and [Fraction(v) for v in row[4:6]] == [Fraction(v) for v in expected["mass_squared"]] and row[6] == "1", "exact ordered request row")
        require(sha(files[request_name]) == case["request_sha256"], "raw request provenance")
        command = [protocol["tools"]["taskset"], "-c", "26", protocol["tools"]["python"], HISTORICAL + PRIVATE + "/capture_worker.py",
                   "--binary", HISTORICAL + CAPTURE + "/iregi-reference-quad", "--input", case["input"],
                   "--stdout", HISTORICAL + CAPTURE + f"/request-{ordinal}.stdout", "--stderr", HISTORICAL + CAPTURE + f"/request-{ordinal}.stderr"]
        require(step["command"] == command and step["label"] == case["id"] and step["timeout_seconds"] == case["cap_seconds"]
                and step["status"] == "exited" and step["returncode"] == 0 and step["owned_group_gone"] is True, "exact owned request/terminal provenance")
        groups.append(step["owned_process_group"])
        transport = load(files[CAPTURE + f"/step-{ordinal}.log"])
        require(transport == {"binary_sha256": run["runtime_binary_sha256"], "input_sha256": sha(files[request_name]), "returncode": 0,
                              "stdout_sha256": run["outputs"][f"request-{ordinal}.stdout"], "stderr_sha256": run["outputs"][f"request-{ordinal}.stderr"]}, "worker exact raw transport")
        stdout = files[CAPTURE + f"/request-{ordinal}.stdout"].decode().splitlines()
        precision = [load(line[10:]) for line in stdout if line.startswith("PRECISION ")]
        require(precision == [{"dbl_kind": 16, "olo_kind": 16, "storage_bits": 128, "binary_digits": 113, "decimal_digits": 33}]
                and stdout.count("READY IREGI_REFERENCE_QP_V1") == 1, "actual quad transport precision witness")
        responses = [load(line[7:]) for line in stdout if line.startswith("RESULT ")]
        require(len(responses) == 1 and responses[0]["id"] == case["id"] and responses[0]["stable"] is True, "one stable identified response")
        response = responses[0]
        values = parent.slots(response, case["moments"], case["id"])
        require(saved["cases"][ordinal]["response"] == response and saved["cases"][ordinal]["accepted_reference"] is True, "complete raw/saved response equality")
        basis = [[t, x, y, degree - t - x - y] for degree in range(case["rank"] + 1) for t in range(degree, -1, -1)
                 for x in range(degree - t, -1, -1) for y in range(degree - t - x, -1, -1)]
        maximum = uv = Fraction(0)
        worst = None
        uv_nonzero = zeros = 0
        for moment, powers in enumerate(basis):
            unit = Fraction(2) ** (sum(powers) + 4 - 2 * case["propagators"])
            for pole, value in enumerate(values[moment]):
                norm = sum(v ** 2 for v in value)
                if pole == 0:
                    uv = max(uv, norm)
                    uv_nonzero += any(v != 0 for v in value)
                if pole < 3:
                    zeros += all(v == 0 for v in value)
                if case["propagators"] == 7 and pole < 3:
                    row = pole_records[(case["id"], moment, pole)]
                    require(row["basis"] == powers and row["represented_components"] == response["moments"][moment][pole]
                            and row["laurent"] == ["uv1", "ir1", "ir2"][pole] and Fraction(row["natural_unit"]) == unit
                            and Fraction(row["normalized_squared_residual_exact"]) == norm / unit ** 2, "all exact saved pole operands/normalization/residuals")
                    require(row["passed"] is True and norm / unit ** 2 <= Fraction(1, 10 ** 20), "unmodified N7 zero-pole identity gate")
                    if worst is None or norm / unit ** 2 > maximum:
                        worst = row
                    maximum = max(maximum, norm / unit ** 2)
                    checked_poles += 1
        require(saved["cases"][ordinal]["exact_nonzero_uv_slots"] == uv_nonzero and saved["cases"][ordinal]["exactly_zero_pole_slots"] == zeros, "zero/nonzero counts retain raw values")
        if case["propagators"] == 7:
            summary = gate["gates"][ordinal]
            require(summary["id"] == case["id"] and summary["rank"] == case["rank"] and summary["pole_slots"] == 3 * case["moments"]
                    and summary["normalization_Q_squared_exact"] == "4" and summary["passed"] is True and summary["failures"] == 0
                    and summary["offending_components"] == [] and summary["maximum_normalized_complex_residual"] == display(maximum)
                    and summary["worst"] == worst, "exact pole-gate aggregate/worst record")
        summaries.append({"id": case["id"], "n": case["propagators"], "rank": case["rank"], "complete_complex_slots": case["complex_slots"],
                          "maximum_normalized_N7_pole_residual": display(maximum) if case["propagators"] == 7 else None,
                          "nonzero_raw_uv_slots": uv_nonzero, "maximum_raw_uv_magnitude": display(uv)})
        total += case["complex_slots"]
    require(total == 2720 and checked_poles == 1050 and summaries == independent["cases"], "all complete arrays and independent exact summaries")
    require(summaries[2]["nonzero_raw_uv_slots"] == 315 and summaries[3]["nonzero_raw_uv_slots"] == 305
            and gate["N5_UV_unrestricted_and_retained"] is True, "tiny N7 and nonzero N5 UV retained without projection")
    require(saved["compared_tirust_slots"] == 0 and saved["currentCargo_qualified"] is False and saved["full_rank7_domain_qualified"] is False
            and saved["performance_qualified"] is False, "reference generation only scope")
    release = read("capture-001/numerical-release.json")
    require([r["group"] for r in release["owned_groups"]] == groups == independent["owned_groups_actually_absent"]
            and len(set(groups)) == 4 and all(r["absent"] is True for r in release["owned_groups"])
            and release["run_sha256"] == sha(files[CAPTURE + "/run.json"]) and release["all_inputs_rehashed_unchanged"] == 274, "historical release attestation; no fresh PID probe")
    return {"complete_reference_complex_slots": total, "exact_N7_pole_records": checked_poles, "cases": summaries,
            "available_source_data_guard_occurrences_checked": available, "omitted_native_external_guards_historical_only": historical,
            "historical_owned_group_attestations_checked": 4, "fresh_native_hashes_or_process_probes": False,
            "N5_UV_projected": False, "finite_TIRust_comparison_performed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct", type=Path)
    args = parser.parse_args()
    manifest = load((HERE / "manifest.json").read_bytes())
    files, parent, inherited = restore(manifest)
    result = replay(files, parent, manifest)
    qualification = load((HERE / "qualification.json").read_bytes())
    require((HERE / "qualification.json").read_bytes() == files[Q + "/qualification.json"], "exact final reference-only qualification copy")
    require(manifest["TIRust_qualified"] is False and manifest["currentCargo_qualified"] is False
            and manifest["full_rank7_domain_qualified"] is False and manifest["performance_qualified"] is False, "no scope promotion")
    require(qualification["TIRust_complex_slots_compared"] == 0 and qualification["currentCargo_qualified"] is False
            and qualification["full_rank7_domain_qualified"] is False and qualification["performance_qualified"] is False
            and qualification["finite_independent_parameter_oracle_qualified"] is False
            and qualification["precision_convergence_qualified_for_these_new_references"] is False, "final qualification remains reference generation only")
    for field, name in [("protocol_sha256", "protocol.json"), ("source_review_sha256", "source-review.json"),
                        ("independent_saved_review_sha256", "independent-saved-review.json"), ("run_sha256", "capture-001/run.json"),
                        ("validation_sha256", "capture-001/validation.json"), ("pole_zero_exact_sha256", "capture-001/pole-zero-exact.json"),
                        ("numerical_release_sha256", "capture-001/numerical-release.json")]:
        require(qualification[field] == sha(files[Q + "/" + name]), "final qualification artifact binding")
    if args.reconstruct is not None:
        require(not args.reconstruct.exists(), "reconstruction destination exists")
        args.reconstruct.mkdir(parents=True)
        for name, value in files.items():
            parent.safe(name)
            destination = args.reconstruct / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(value)
    print(json.dumps({"status": "passed_portable_source_and_saved_positive_rank_reference_replay", "manifest_sha256": sha((HERE / "manifest.json").read_bytes()),
                      "restored_files": len(files), "inherited_N6_proof": inherited, "reference_only_replay": result,
                      "new_compiler_native_integral_or_PID_work": False, "TIRust_currentCargo_fullrank7_or_performance_qualified": False}, indent=2))


if __name__ == "__main__":
    main()

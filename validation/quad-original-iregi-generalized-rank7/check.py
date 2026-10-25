#!/usr/bin/env python3
"""Portable archived-source and saved generalized-reference replay only.

Imports only the hash-pinned independent small-N parent checker. No producer,
compiler, native executable, integral, native hashing or process probe is run.
"""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = "validation/quad-original-iregi-small-n-rank7"
PRIVATE = "target/quad-generalized-rank7-anchors"
HISTORICAL = "/shared/external/iregi/iregi-rust/"
PROTOCOL_SHA = "f9da4d00dd8aa7d85377082da89e6c38dcc771f2115f15d1203699940efe8899"
PARENT_MANIFEST_SHA = "9b614c6567c28d23039053de390a7da5c665f4a57a978d54cd3148519fb3cb62"
PARENT_CHECK_SHA = "a202925e87ab6aef866563c42c3c39eda73f081b47d2ca72214013af8f12850b"
LIMIT = Q(1, 10**20)
DECIMAL = re.compile(r"\s*[+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\s*")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {"sha256": sha(body), "bytes": len(body)}


def load(body):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError("nonfinite JSON constant: " + value)

    return json.loads(body, object_pairs_hook=pairs, parse_constant=nonfinite, parse_float=str)


def norm(value):
    return sum(x*x for x in value)


def display(value):
    with localcontext() as context:
        context.prec = 100
        return str((Decimal(value.numerator) / Decimal(value.denominator)).sqrt())


def basis():
    return [[t, x, y, r-t-x-y] for r in range(8) for t in range(r, -1, -1)
            for x in range(r-t, -1, -1) for y in range(r-t-x, -1, -1)]


def parse_raw(body, identifier):
    lines = body.decode().splitlines()
    precision = [load(line[10:]) for line in lines if line.startswith("PRECISION ")]
    require(precision == [{"dbl_kind": 16, "olo_kind": 16, "storage_bits": 128,
                           "binary_digits": 113, "decimal_digits": 33}], "quad precision witness")
    require(lines.count("READY IREGI_REFERENCE_QP_V1") == 1, "one quad ready witness")
    rows = [load(line[7:]) for line in lines if line.startswith("RESULT ")]
    require(len(rows) == 1 and isinstance(rows[0], dict), "one object RESULT")
    row = rows[0]
    require(row.get("id") == identifier and type(row.get("stable")) is bool
            and row.get("error") is None and row.get("poles") == ["uv1", "ir1", "ir2", "finite"]
            and isinstance(row.get("moments"), list) and len(row["moments"]) == 330,
            "complete matching typed RESULT")
    values = []
    for moment in row["moments"]:
        require(isinstance(moment, list) and len(moment) == 4, "four native Laurent slots")
        parsed = []
        for value in moment:
            require(isinstance(value, list) and len(value) == 2
                    and all(isinstance(v, str) and DECIMAL.fullmatch(v) for v in value),
                    "two finite decimal strings per complex slot")
            parsed.append(tuple(Q(v.strip()) for v in value))
        values.append(parsed)
    return row, values


def restore(manifest):
    for name, expected in manifest["capsule_files"].items():
        require(desc((HERE/name).read_bytes()) == expected, "capsule file " + name)
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts}
    require(actual == set(manifest["capsule_files"]) | {"manifest.json"}, "exact own inventory")
    for name, expected in manifest["parent_files"].items():
        require(desc((ROOT/name).read_bytes()) == expected, "parent file " + name)
    require(sha((ROOT/PARENT/"manifest.json").read_bytes()) == PARENT_MANIFEST_SHA,
            "fixed small-N parent manifest")
    path = ROOT/PARENT/"check.py"
    require(sha(path.read_bytes()) == PARENT_CHECK_SHA, "fixed independent small-N parent checker")
    spec = importlib.util.spec_from_file_location("generalized_quad_saved_smalln_parent", path)
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    pm = load((ROOT/PARENT/"manifest.json").read_bytes())
    files, helpers, inherited = parent.restore(pm)
    summary = parent.replay(files, helpers, pm)
    members = helpers.read_archive((HERE/"payload.tar.gz").read_bytes(), manifest["payload_members"])
    origins = load((HERE/"payload-origins.json").read_bytes())
    require(set(origins) == set(manifest["preserved_files"]) | set(manifest["inherited_aliases"]),
            "exact new origin inventory")
    for name, expected in manifest["inherited_requirements"].items():
        require(name in files and desc(files[name]) == expected, "exact borrowed parent content")
    for name, row in manifest["preserved_files"].items():
        helpers.safe(name)
        body = members[row["member"]]
        expected = {k: row[k] for k in ["sha256", "bytes"]}
        require(desc(body) == expected == {k: origins[name][k] for k in expected}, "own byte identity")
        require(name not in files or files[name] == body, "no parent collision")
        files[name] = body
    for name, row in manifest["inherited_aliases"].items():
        helpers.safe(name)
        body = files[row["inherited_source"]]
        expected = {k: row[k] for k in ["sha256", "bytes"]}
        require(desc(body) == expected == {k: origins[name][k] for k in expected}, "parent alias identity")
        require(name not in files or files[name] == body, "no alias collision")
        files[name] = body
    freeze = load(files[manifest["terminal_inventory_alias"]])
    require(freeze["status"] == "terminal_inputs_frozen" and freeze["protocol_sha256"] == PROTOCOL_SHA,
            "final terminal inventory pin")
    for name, expected in freeze["files"].items():
        require(desc(files[name]) == expected, "terminal freeze descriptor")
    drafts = [("001-unexecuted-before-terminal-shape-review",
               "6739076106cfa87f718bde88c1d4c90fdb1c98fb56060295d72e692a0376b3c6"),
              ("002-unexecuted-before-canonical-propagator-powers",
               "cc2238e61975e72ab4152a4ccada4b3589728650f4d83026395e1e1aaea1cc45")]
    for directory, protocol_hash in drafts:
        prefix = PRIVATE+"/earlier-drafts/"+directory+"/"
        old = load(files[prefix+"inventory.json"])
        require(len(old) == 23 and old["protocol.json"] == protocol_hash,
                "exact superseded unexecuted source-draft identity")
        require({name.removeprefix(prefix) for name in files if name.startswith(prefix)}
                == set(old) | {"inventory.json"}, "closed old source-draft inventory")
        for name, expected_hash in old.items():
            require(sha(files[prefix+name]) == expected_hash, "preserved old unexecuted draft bytes")
    return files, helpers, {**inherited, "smallN_saved_replay": summary}


def restore_files(manifest):
    return restore(manifest)[0]


def replay(files, helpers, manifest):
    def read(name):
        return load(files[PRIVATE+"/"+name])

    p = read("protocol.json")
    require(sha(files[PRIVATE+"/protocol.json"]) == PROTOCOL_SHA and len(p["bindings"]) == 61,
            "final reviewed 61-binding protocol")
    require(p["metric"] == "+---" and p["laurent"] == ["uv1", "ir1", "ir2", "finite"]
            and p["h_to_idim"] == "idim=2*h; D=4+idim" and p["no_retry_or_budget_extension"] is True,
            "native conventions and fixed cohort")
    original = files["target/quad-iregi-source-audit/source-v2/funlib.f90"]
    repaired = files[PRIVATE+"/source/funlib.f90"]
    require(sha(original) == p["source_original_sha256"] and sha(repaired) == p["source_repaired_sha256"],
            "original/repaired source identities")
    changed, names = helpers.source_patch({"funlib.f90": original}, files[PRIVATE+"/source/factorial_pair.patch"])
    require(names == ["funlib.f90"] and changed["funlib.f90"] == repaired,
            "only exact factorial-table source patch")
    require(p["original_quad_sha256"] == "283560d64b6588e944fb641b7ed6f128f5d6667b1f334eae2acdb8bfcc7685c9",
            "retained old quad artifact attestation")

    roles = manifest["terminal_roles"]
    review, grant, audit = [load(files[roles[key]]) for key in
                            ["source_review", "root_grant", "independent_saved_review"]]
    require(review["status"] == "passed_independent_source_runner_comparator_review"
            and review["protocol_sha256"] == PROTOCOL_SHA and review["findings"] == [], "source review clear")
    for name, expected_hash in review["subject_sha256"].items():
        require(sha(files[PRIVATE+"/"+name]) == expected_hash, "exact reviewed producer source identity")
    require(grant["status"] == "granted" and grant["grantor"] == "/root"
            and grant["protocol_sha256"] == PROTOCOL_SHA
            and grant["review_sha256"] == sha(files[roles["source_review"]])
            and grant["stages"] == ["build", "runtime"], "exact finite root grant")
    require(audit["status"] == "passed_independent_saved_generalized_quad_numeric_review"
            and audit.get("findings") == [] and audit["protocol_sha256"] == PROTOCOL_SHA
            and audit["source_review_sha256"] == sha(files[roles["source_review"]])
            and audit["checker_sha256"] == sha(files[roles["independent_saved_review_source"]]),
            "independent saved audit/source exact identity")
    for name, expected_descriptor in audit["read_saved_files"].items():
        require(desc(files[name]) == expected_descriptor, "independent audit saved-input descriptor")
    expected = dict(p["bindings"])
    expected.update({HISTORICAL+PRIVATE+"/"+name: sha(files[PRIVATE+"/"+name])
                     for name in ["protocol.json", "source-review.json", "root-grant.json"]})
    build, run = read("build-001/receipt.json"), read("capture-001/receipt.json")
    for stage, receipt in [("build", build), ("runtime", run)]:
        require(receipt["stage"] == stage and receipt["status"] in ["passed", "failed"], "terminal receipt state")
        require(receipt["protocol_sha256"] == PROTOCOL_SHA and receipt["performance_measurement"] is False,
                "exact protocol, no timing promotion")
        require(receipt["bound_seconds"] == p[stage]["aggregate_seconds"]
                and receipt["cleanup_reserve_seconds"] == p[stage]["cleanup_reserve_seconds"]
                and 0 <= Q(receipt["elapsed_seconds"]) <= receipt["bound_seconds"], "fixed terminal budgets")
        require(receipt["inputs_unchanged"] is True and receipt["changed_inputs"] == {}
                and receipt["cleanup_errors"] == [] and receipt["cancellation"] is None,
                "saved guarded source/cleanup terminal attestation")
        for name, expected_hash in receipt["outputs"].items():
            key = PRIVATE+("/build-001/" if stage == "build" else "/capture-001/")+name
            if key in files:
                require(sha(files[key]) == expected_hash, "fresh preserved output digest")
            else:
                require(manifest["omitted_compiled_products"][key]["captured_sha256"] == expected_hash,
                        "explicit omitted compiled output attestation")
    require(build["inputs"] == expected and len(expected) == 64 and len(build["steps"]) == 2,
            "closed build source map and two commands")
    require(set(build["outputs"]) == set(p["build"]["products"]) | {"step-0.log", "step-1.log"},
            "closed five-product build output map")
    require(set(run["outputs"]) == {f"{prefix}-{i}.{suffix}" for i in range(12)
                                    for prefix, suffix in [("request", "stdout"), ("request", "stderr"), ("step", "log")]},
            "closed all-thirty-six raw output map")
    for step, command in zip(build["steps"], p["build"]["commands"]):
        require(step["command"] == command["command"] and step["label"] == command["label"]
                and step["timeout_seconds"] <= command["cap_seconds"], "exact build command")
    replacement = list(p["original_link_command"])
    olddir = HISTORICAL+"target/quad-iregi-source-audit/build-v6-001/"
    replacement = [p["build"]["directory"]+"/funlib.o" if v == olddir+"funlib.o"
                   else p["build"]["binary"] if v == olddir+"iregi-reference-quad" else v
                   for v in replacement]
    require(p["build"]["commands"][1]["command"] == replacement, "same link except repaired funlib/output")
    expected[HISTORICAL+PRIVATE+"/build-001/receipt.json"] = sha(files[PRIVATE+"/build-001/receipt.json"])
    for name in p["build"]["products"]:
        expected[p["build"]["directory"]+"/"+name] = build["outputs"][name]
    require(run["inputs"] == expected and len(expected) == 68, "closed runtime source/product map")
    available = historical = 0
    for name, expected_hash in expected.items():
        key = name.removeprefix(HISTORICAL)
        if key in files:
            require(sha(files[key]) == expected_hash, "available restored input content")
            available += 1
        else:
            require(manifest["historical_external_inputs"].get(name) == expected_hash
                    or manifest["omitted_compiled_products"].get(key, {}).get("captured_sha256") == expected_hash,
                    "declared historical input attestation")
            historical += 1

    cases = p["runtime"]["cases"]
    specs = [("ordinary_control", "tensor", 2, [1, 1], 0), ("general_unit_control", "general", 2, [1, 1], 0)]
    for n in [2, 3]:
        a, b, c = [1]*n, [1]*n, [1]*n
        a[0], b[-1], c[0] = 2, 2, 3
        specs.extend([(f"n{n}_first_dot2", "general", n, a, 0), (f"n{n}_last_dot2", "general", n, b, 0),
                      (f"n{n}_first_power3", "general", n, c, 0), (f"n{n}_D2", "general", n, [1]*n, -2),
                      (f"n{n}_D6", "general", n, [1]*n, 2)])
    require(len(cases) == len(run["steps"]) == 12 and len(basis()) == 330, "fixed twelve-query shape")
    anchor_key = p["ordinary_anchor"]["path"].removeprefix(HISTORICAL)
    anchor_meta, anchor = parse_raw(files[anchor_key], "n2_base_mode0")
    require(anchor_meta["stable"] is True, "stable inherited ordinary control")
    anchor_saved = load(files["target/quad-iregi-source-audit/rank7-n1-n5-corpus/capture-001/validation.json"])
    require(next(c for c in anchor_saved["cases"] if c["id"] == "n2_base_mode0")["eligible_IBP_reference_anchor"] is True,
            "ordinary anchor independently eligible in parent")
    saved, records, states = read("comparison.json"), [], []
    for ordinal, (case, spec) in enumerate(zip(cases, specs)):
        identifier, api, n, powers, idim = spec
        require((case["id"], case["api"], case["n"], case["powers"], case["idim"]) == spec
                and case["h"]*2 == idim and case["rank"] == 7 and case["mu"] == "3"
                and case["moments"] == 330 and case["complex_slots"] == 1320 and case["cap_seconds"] == 60,
                "exact generalized request metadata")
        props = case["propagators"]
        require(len(props) == n and [prop["power"] for prop in props] == powers
                and all(Q(prop["mass_squared"][0]) > 0 and Q(prop["mass_squared"][1]) == 0
                        and Q(prop["shift"][0]) == 0 for prop in props), "canonical positive-F ordered propagators")
        request = case["request"].removeprefix(HISTORICAL)
        lines = files[request].decode().splitlines()
        require(sha(files[request]) == case["request_sha256"] and len(lines) == n+2
                and lines[0].split() == ["EVAL", identifier, api, "0", str(n), "7", str(idim), "3", "0", "1e-6"]
                and lines[-1] == "QUIT", "ordered exact native request header")
        for line, prop, power in zip(lines[1:-1], props, powers):
            require(list(map(Q, line.split())) == list(map(Q, prop["shift"]+prop["mass_squared"]+[str(power)])),
                    "ordered exact rational request row")
        step = run["steps"][ordinal]
        command = [p["tools"]["taskset"], "-c", "26", p["tools"]["python"], HISTORICAL+PRIVATE+"/capture_worker.py",
                   "--binary", p["build"]["binary"], "--input", case["request"], "--stdout",
                   HISTORICAL+PRIVATE+f"/capture-001/request-{ordinal}.stdout", "--stderr",
                   HISTORICAL+PRIVATE+f"/capture-001/request-{ordinal}.stderr"]
        require(step["label"] == identifier, "ordered native transport label")
        if "command" in step:
            require(step["command"] == command and 0 < Q(step["timeout_seconds"]) <= 60, "exact runtime command/cap")
        entry = saved["cases"][ordinal]
        require(entry["id"] == identifier, "saved case ordering")
        if step.get("status") != "exited":
            require(entry["status"] == "failed_or_incomplete" and entry["eligible_reference_anchor"] is False
                    and entry["all_slots_preserved"] is False, "failed native step stays ineligible")
            states.append((False, False))
            continue
        require(step["owned_group_gone"] is True and step["returncode"] == 0, "saved terminal owned transport")
        stdout = PRIVATE+f"/capture-001/request-{ordinal}.stdout"
        stderr = PRIVATE+f"/capture-001/request-{ordinal}.stderr"
        worker = read(f"capture-001/step-{ordinal}.log")
        require(worker == {"binary_sha256": build["outputs"]["iregi-reference-quad-generalized"],
                           "input_sha256": sha(files[request]), "returncode": 0,
                           "stdout_sha256": sha(files[stdout]), "stderr_sha256": sha(files[stderr])},
                "worker artifact/request/raw chain")
        try:
            meta, values = parse_raw(files[stdout], identifier)
        except (ValueError, KeyError, TypeError, UnicodeError):
            require(entry["status"] == "failed_or_incomplete" and entry["eligible_reference_anchor"] is False,
                    "malformed raw result remains rejected")
            states.append((False, False))
            continue
        require(entry["status"] == "complete" and entry["all_slots_preserved"] is True
                and entry["native_stable"] is meta["stable"] and entry["complex_slots"] == 1320
                and entry["raw_sha256"] == sha(files[stdout]), "complete raw case binding")
        local = []

        def record(kind, moment, slot, residual, unit, denominator=None):
            denominator = unit if denominator is None else denominator
            local.append({"case": identifier, "kind": kind, "moment": moment, "powers": basis()[moment],
                          "slot": slot, "passed": residual <= LIMIT*denominator,
                          "residual_squared": str(residual), "unit_squared": str(unit),
                          "normalized_error": display(residual/denominator)})

        for moment, power in enumerate(basis()):
            delta = sum(power)+4+idim-2*sum(powers)
            unit = Q(9)**delta
            for slot in [1, 2]+([0] if delta < 0 else []):
                record("positive_mass_IR_zero" if slot else "UV_power_counting_zero", moment, slot, norm(values[moment][slot]), unit)
        absent = [axis for axis in range(4) if all(Q(prop["shift"][axis]) == 0 for prop in props)]
        for moment, power in enumerate(basis()):
            if any(power[axis] % 2 for axis in absent):
                unit = Q(9)**(sum(power)+4+idim-2*sum(powers))
                for slot in range(4):
                    record("absent_coordinate_reflection_zero", moment, slot, norm(values[moment][slot]), unit)
        if ordinal < 2:
            for moment, power in enumerate(basis()):
                unit = Q(9)**sum(power)
                for slot in range(4):
                    residual = norm(tuple(a-b for a, b in zip(values[moment][slot], anchor[moment][slot])))
                    record("ordinary_original_quad_control", moment, slot, residual, unit, max(unit, norm(anchor[moment][slot])))
        failures = sum(not row["passed"] for row in local)
        require(entry["identity_failures"] == failures, "recomputed case failures")
        states.append((True, meta["stable"] and not failures))
        records.extend(local)
    terminal_ok = (build["status"] == run["status"] == "passed"
                   and all(step.get("status") == "exited" and step.get("owned_group_gone") is True for step in build["steps"]+run["steps"]))
    require((saved["terminal_admission_errors"] == []) is terminal_ok, "saved terminal eligibility gate")
    controls = terminal_ok and all(ok for _, ok in states[:2])
    for entry, (_, eligible) in zip(saved["cases"], states):
        require(entry["eligible_reference_anchor"] is bool(controls and eligible), "exact eligibility partition")
    require(saved["records"] == records and saved["records_count"] == len(records)
            and saved["failures"] == sum(not row["passed"] for row in records), "all saved exact numerical records")
    require(saved["controls_passed"] is controls and saved["protocol_sha256"] == PROTOCOL_SHA
            and saved["run_sha256"] == sha(files[PRIVATE+"/capture-001/receipt.json"])
            and saved["all_complex_slots_requested"] == 15840
            and saved["all_cases_complete"] == sum(complete for complete, _ in states)
            and saved["no_Rust_or_currentCargo_or_performance_qualification"] is True, "scoped saved summary")
    eligible = sum(bool(controls and ok) for _, ok in states)
    require(saved["status"] == ("passed_restricted_original_quad_generalized_anchor_corpus" if eligible == 12
                                else "failed_or_partial_original_quad_generalized_anchor_corpus"), "honest corpus outcome")
    release = read("numerical-release.json")
    require(release["protocol_sha256"] == PROTOCOL_SHA
            and release["build_receipt_sha256"] == sha(files[PRIVATE+"/build-001/receipt.json"])
            and release["capture_receipt_sha256"] == sha(files[PRIVATE+"/capture-001/receipt.json"])
            and release["comparison_sha256"] == sha(files[PRIVATE+"/comparison.json"]), "terminal release data chain")
    expected_groups = [(stage, step["label"], step["owned_process_group"])
                       for stage, receipt in [("build", build), ("capture", run)] for step in receipt["steps"]]
    require([(row["stage"], row["label"], row["owned_process_group"]) for row in release["owned_groups"]]
            == expected_groups and len({group for _, _, group in expected_groups}) == 14
            and all(row["actually_absent_now"] is True for row in release["owned_groups"])
            and release["all14owned_groups_freshly_absent"] is True
            and release["all61source_input_bindings_unchanged"] is True
            and release["no_additional_integrals_or_retries"] is True
            and release["performance_measurement"] is False, "historical fourteen-group release, no new probe")
    require(eligible == 12 and len(records) == 22321 and saved["failures"] == 0,
            "frozen complete restricted twelve-anchor result")
    counts = {kind: sum(row["kind"] == kind for row in records) for kind in
              ["positive_mass_IR_zero", "UV_power_counting_zero", "absent_coordinate_reflection_zero", "ordinary_original_quad_control"]}
    require(audit["record_counts_by_kind"] == counts and audit["exact_recomputed_records"] == len(records)
            and audit["complete_arrays"] == 12 and audit["complete_complex_slots"] == 15840
            and audit["exact_archived_control_complex_slots"] == 2640
            and audit["exact_new_control_pair_complex_slots"] == 1320 and audit["numeric_failures"] == 0
            and audit["native_poles_merged_or_projected"] is False
            and audit["fresh_process_or_native_product_hash_probe"] is False,
            "independent saved audit restricted summaries")
    qualification = read("qualification.json")
    require((HERE/"qualification.json").read_bytes() == files[PRIVATE+"/qualification.json"],
            "exact final qualification copy")
    for key, name in [("source_review_sha256", "source-review.json"), ("saved_review_sha256", "saved-review.json"),
                      ("comparison_sha256", "comparison.json"), ("numerical_release_sha256", "numerical-release.json")]:
        require(qualification[key] == sha(files[PRIVATE+"/"+name]), "qualification final evidence chain")
    require(qualification["complete_arrays"] == 12 and qualification["complex_slots"] == 15840
            and qualification["independent_exact_records"] == len(records) and qualification["math_failures"] == 0
            and qualification["new_generalized_point_anchors"] == 10 and qualification["control_arrays"] == 2
            and qualification["broad_generalized_finite_correctness_proved"] is False
            and qualification["Rust_currentCargo_Dual_or_performance_qualified"] is False,
            "final qualification retains restricted scope")
    return {"requested_arrays": 12, "requested_complex_slots": 15840,
            "complete_arrays": sum(complete for complete, _ in states), "eligible_reference_arrays": eligible,
            "exact_saved_records_replayed": len(records), "failed_records": saved["failures"],
            "exact_records_by_kind": counts,
            "available_source_data_guards_checked": available, "historical_native_external_guards": historical,
            "TIRust_or_currentCargo_qualified": False, "fresh_native_hash_or_process_probe": False,
            "finite_coefficients_independently_certified": False, "performance_qualified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct", type=Path)
    args = parser.parse_args()
    manifest = load((HERE/"manifest.json").read_bytes())
    files, helpers, inherited = restore(manifest)
    result = replay(files, helpers, manifest)
    if args.reconstruct is not None:
        require(not args.reconstruct.exists(), "reconstruction destination already exists")
        args.reconstruct.mkdir(parents=True)
        for name, body in files.items():
            helpers.safe(name)
            destination = args.reconstruct/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(body)
    print(json.dumps({"status": "passed_portable_generalized_source_and_saved_reference_replay",
                      "manifest_sha256": sha((HERE/"manifest.json").read_bytes()), "restored_files": len(files),
                      "inherited": inherited, "generalized_reference_replay": result,
                      "new_native_compiler_integral_or_PID_work": False}, indent=2))


if __name__ == "__main__":
    main()

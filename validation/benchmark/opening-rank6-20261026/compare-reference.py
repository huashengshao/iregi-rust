#!/usr/bin/env python3
"""Independently compare saved opening-table tensors with admitted IREGI IBP.

This program reads JSON, exact represented values and existing reference
capsules. It never invokes a compiler, native module, integral, subprocess,
symbolic reducer or producer comparison helper. Reference requests and raw
outputs are restored directly from their pinned capsule archive members;
historical target directories are not required.

Run from the repository root after numerical captures have terminated:
  python3 -I -S -B validation/benchmark/opening-rank6-20261026/compare-reference.py
Missing captures remain explicitly unmeasured; --require-all requires all
18 first-output arrays and successful supervised terminal outcomes.
"""

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import tarfile


DIRECTORY = "validation/benchmark/opening-rank6-20261026"
AUDIT = DIRECTORY + "/independent-timing-boundary-and-fixture-review.json"
AUDIT_SHA256 = "7cb71007b1faff54d7d4b1738343aa6d3e3f33e839ff9bc76b7c9981a2f18d33"
INPUTS = DIRECTORY + "/inputs.json"
INPUTS_SHA256 = "a065511103c41ad04d14a01b3189c5180aa4d02af0c308ce2438fa3bf6cca43a"
BUILD_RECEIPT_SHA256 = "274cb167ba5ec8b3184aab184f6aff3e7736994393811048730b93b1722e87ef"
BUILD_BINARY_SHA256 = "0d3c5c37abfede1b10fb7ff99e55abc2a395bdfc9b0d4bac4ea3d966ed488c37"
REFERENCE_POLES = ["uv1", "ir1", "ir2", "finite"]
OUTPUT_POLES = ["UV single", "IR single", "IR double", "finite"]
TOLERANCE = F(1, 10**10)
SQUARED_TOLERANCE = TOLERANCE**2
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_name(name):
    require(type(name) is str and name and not name.startswith("/")
            and "\\" not in name
            and all(p not in ("", ".", "..") for p in name.split("/")),
            "unsafe project-relative name")
    return name


def document(body):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError("nonfinite JSON constant: " + value)

    return json.loads(body, object_pairs_hook=unique, parse_float=str,
                      parse_constant=reject_constant)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def descriptor(body):
    return {"sha256": digest(body), "bytes": len(body)}


def basis(maximum_rank):
    # This enumerates documented IREGI indices, not symbolic polynomials.
    return [[t, x, y, r-t-x-y]
            for r in range(maximum_rank+1)
            for t in range(r, -1, -1)
            for x in range(r-t, -1, -1)
            for y in range(r-t-x, -1, -1)]


def squared_norm(z):
    return z[0]**2 + z[1]**2


def display_sqrt(value):
    with localcontext() as context:
        context.prec = 70
        return str((Decimal(value.numerator) / Decimal(value.denominator)).sqrt())


def number(text):
    require(type(text) is str, "exact textual numeric operand required")
    q = F(text.strip().replace("D", "E").replace("d", "e"))
    return q


def native_operand(value):
    require(type(value) is dict
            and set(value) == {"exact_rational", "working_bits", "negative_sign", "finite"},
            "native represented-operand schema")
    require(value["finite"] is True and type(value["working_bits"]) is int
            and value["working_bits"] > 0 and type(value["negative_sign"]) is bool,
            "native finite precision/sign metadata")
    q = number(value["exact_rational"])
    require(q == 0 or value["negative_sign"] == (q < 0), "native represented sign")
    return q


def native_values(values, count):
    require(type(values) is list and len(values) == count, "complete native array width")
    decoded = []
    for pair in values:
        require(type(pair) is list and len(pair) == 2, "native complex pair")
        decoded.append(tuple(native_operand(v) for v in pair))
    return decoded


def reference_result(body, entry):
    lines = body.decode("utf-8").splitlines()
    result = [document(line[7:]) for line in lines if line.startswith("RESULT ")]
    require(len(result) == 1, "one native reference RESULT")
    result = result[0]
    require(result.get("id") == entry["reference_native_result_id"]
            and result.get("stable") is True
            and result.get("poles") == REFERENCE_POLES,
            "admitted original IBP id/status/native Laurent order")
    moments = result.get("moments")
    require(type(moments) is list
            and len(moments) == math.comb(entry["reference_maximum_rank"]+4, 4),
            "complete reference rank array")
    decoded = []
    for slots in moments:
        require(type(slots) is list and len(slots) == 4, "four separated reference slots")
        row = []
        for z in slots:
            require(type(z) is list and len(z) == 2, "reference complex pair")
            row.append(tuple(number(v) for v in z))
        decoded.append(row)
    return result, decoded


def check_reference_request(body, request, entry):
    lines = body.decode("utf-8").splitlines()
    header = lines[0].split()
    require(len(header) == 10 and header[:1] == ["EVAL"]
            and header[1] == entry["reference_native_result_id"]
            and header[2] in ("tensor", "general") and header[3] == "0"
            and int(header[4]) == request["n"]
            and int(header[5]) == entry["reference_maximum_rank"] >= request["rank"]
            and int(header[6]) == 2*request["dimension_shift"]
            and header[8] == "0", "unchanged original IBP request and h-to-idim mapping")
    props = [[number(v) for v in line.split()]
             for line in lines[1:1+request["n"]]]
    require(len(props) == request["n"] and all(len(p) == 7 for p in props),
            "complete original propagator request")
    require(type(request["samples"]) is list and len(request["samples"]) == 1,
            "this fixed reference suite is singleton")
    sample = request["samples"][0]
    require([p[:4] for p in props] == [[number(v) for v in p] for p in sample["shifts"]]
            and [p[4:6] for p in props] == [[number(v) for v in p] for p in sample["masses_squared"]]
            and [int(p[6]) for p in props] == request["powers"]
            and number(header[7]) == number(sample["mu"]),
            "exact original/current geometry, masses, powers and scale")
    return props


def natural_scale_squared(request):
    sample = request["samples"][0]
    shifts = [[number(v) for v in p] for p in sample["shifts"]]
    masses = [[number(v) for v in p] for p in sample["masses_squared"]]
    require(all(m[1] == 0 for m in masses), "real reference masses")
    scale = max(F(1), number(sample["mu"])**2,
                *(abs(m[0]) for m in masses))
    for a in shifts:
        for b in shifts:
            delta = [x-y for x, y in zip(a, b)]
            scale = max(scale, abs(delta[0]**2 - sum(v*v for v in delta[1:])))
    require(scale > 0, "positive dimensional normalization scale")
    return scale


def audit(read_bytes, exists, *, require_all=False):
    """All data access is an explicit saved project-relative byte callback."""
    bindings = {}
    capsule_cache = {}

    def read(name, expected=None):
        safe_name(name)
        body = read_bytes(name)
        require(type(body) is bytes, "saved byte callback")
        value = descriptor(body)
        require(expected is None or value["sha256"] == expected, "byte pin: " + name)
        require(name not in bindings or bindings[name] == value, "changed bytes: " + name)
        bindings[name] = value
        return body

    def archived(entry, name, expected):
        manifest_name = entry["reference_capsule_manifest"]
        if manifest_name not in capsule_cache:
            raw_manifest = read(manifest_name, entry["reference_manifest_sha256"])
            manifest = document(raw_manifest)
            archive_name = str(PurePosixPath(manifest_name).parent / "payload.tar.gz")
            archive_descriptor = manifest["capsule_files"]["payload.tar.gz"]
            raw_archive = read(archive_name, archive_descriptor["sha256"])
            require(descriptor(raw_archive) == archive_descriptor, "reference archive descriptor")
            members = {}
            expanded = 0
            with tarfile.open(fileobj=io.BytesIO(raw_archive), mode="r:gz") as archive:
                for item in archive:
                    safe_name(item.name)
                    require(item.isfile() and item.name not in members,
                            "reference archive ordinary unique members")
                    expanded += item.size
                    require(expanded <= MAX_ARCHIVE_BYTES, "reference archive expanded-size cap")
                    stream = archive.extractfile(item)
                    require(stream is not None, "reference archive readable member")
                    body = stream.read()
                    require(len(body) == item.size
                            and descriptor(body) == manifest["payload_members"][item.name],
                            "reference archive member descriptor")
                    members[item.name] = body
            require(set(members) == set(manifest["payload_members"]), "reference archive exact inventory")
            qualification_name = str(PurePosixPath(manifest_name).parent / "qualification.json")
            qualification_body = read(qualification_name,
                                     manifest["capsule_files"]["qualification.json"]["sha256"])
            require(descriptor(qualification_body) == manifest["capsule_files"]["qualification.json"],
                    "admitted original qualification descriptor")
            capsule_cache[manifest_name] = (manifest, members, document(qualification_body))
        manifest, members, qualification = capsule_cache[manifest_name]
        desc = manifest["preserved_files"][name]
        body = members[desc["member"]]
        require(descriptor(body) == {"sha256": desc["sha256"], "bytes": desc["bytes"]}
                and digest(body) == expected, "admitted archived alias: " + name)
        # Record restored bytes independently of any optional historical target copy.
        bindings[name] = descriptor(body)
        return body, qualification

    reviewed = document(read(AUDIT, AUDIT_SHA256))
    suite = document(read(INPUTS, INPUTS_SHA256))
    require(reviewed["all_selected_reference_request_inputs_exactly_match"] is True
            and len(reviewed["fixture_rows"]) == len(suite["cases"]) == 18,
            "fixed independently reviewed fixture inventory")
    entries = {v["id"]: v for v in reviewed["fixture_rows"]}
    require(len(entries) == 18, "unique reviewed fixture rows")
    build_name = DIRECTORY + "/build.json"
    built = document(read(build_name, BUILD_RECEIPT_SHA256)) if exists(build_name) else None
    if built is not None:
        require(built.get("status") == "built_and_frozen"
                and built.get("binary_sha256") == BUILD_BINARY_SHA256
                and built.get("source_revision") == "d2762f5547caac666866db3a383434df737007c7"
                and built.get("sources_unchanged") is True
                and built.get("step", {}).get("returncode") == 0
                and built.get("step", {}).get("owned_group_gone") is True
                and built.get("step", {}).get("timed_out") is False,
                "successful source-guarded supervised saved build")
    rows = []
    field_count = 0
    failure_count = 0
    successful_arrays = 0
    failed_native_rows = 0
    missing_rows = 0
    historical_qualifications = {}
    for case in suite["cases"]:
        ident = case["id"]
        entry = entries[ident]
        request = case["driver_request"]
        expected_basis = basis(request["rank"])
        require(len(expected_basis) == entry["moments"] == math.comb(request["rank"]+4, 4),
                "cumulative Cartesian basis count")
        request_body, qualification = archived(entry, entry["reference_request"],
                                             entry["reference_request_sha256"])
        check_reference_request(request_body, request, entry)
        raw, _ = archived(entry, entry["reference_raw_stdout"],
                          entry["reference_raw_stdout_sha256"])
        _, reference = reference_result(raw, entry)
        historical_qualifications[entry["reference_capsule_manifest"]] = {
            "source_status": qualification["status"],
            "scope": qualification.get("scope"),
            "finite_coefficients_independently_certified_by_identities": qualification.get(
                "finite_coefficients_independently_certified_by_identities", False),
            "retained_stable_but_rejected_N3_N4_PV_arrays": qualification.get(
                "stable_but_rejected_N3_N4_PV_arrays"),
            "retained_PV_vs_IBP_failing_finite_slots": qualification.get(
                "PV_vs_IBP_failing_finite_slots"),
            "reference_choice": "The admitted original IBP array; never a rejected PV/Hybrid array.",
            "full_original_qualification_snapshot": qualification,
        }
        result_name = DIRECTORY + "/cases/" + ident + "/result.json"
        row = {
            "id": ident, "n": request["n"], "rank": request["rank"],
            "powers": request["powers"], "h": request["dimension_shift"],
            "requested_algorithm": request["algorithm"],
            "working_bits": request["working_bits"],
            "reference_algorithm": "Original IREGI IBP",
            "reference_id": entry["reference_native_result_id"],
            "reference_request": entry["reference_request"],
            "reference_raw_stdout": entry["reference_raw_stdout"],
            "reference_capsule_manifest": entry["reference_capsule_manifest"],
            "requested_complex_fields": len(expected_basis)*4,
            "compared_complex_fields": 0, "compared_real_components": 0,
            "failed_complex_fields": 0, "successful_first_output_available": False,
            "saved_terminal_success": False, "numerical_agreement": False,
            "reference_rank_prefix_only": True, "result_source": result_name,
        }
        if not exists(result_name):
            row["status"] = "unmeasured_no_saved_result"
            missing_rows += 1
            rows.append(row)
            continue
        require(built is not None, "saved numerical capture requires its build association")
        result_body = read(result_name)
        result = document(result_body)
        row["result_sha256"] = digest(result_body)
        row["driver_status"] = result.get("status")
        row["actual_workspace_engine"] = result.get("workspace_engine")
        require(result.get("id") == ident, "saved timing result id")
        actual_request = result.get("request")
        require(type(actual_request) is dict, "saved actual numerical request")
        for key in ["id", "n", "rank", "powers", "dimension_shift", "algorithm",
                    "numeric_type", "working_bits", "requested_bits", "samples"]:
            require(actual_request.get(key) == request[key], "actual numeric request preserved: " + ident)
        # The runner prespecifies smaller repetition counts at high point count;
        # these do not change the mathematical input or first-output comparison.
        require(result.get("settings") == {
            "propagators": request["n"], "rank": request["rank"],
            "powers": request["powers"], "dimension_shift": request["dimension_shift"],
            "algorithm": request["algorithm"], "convention": "IregiNative",
            "tensor_weights": "Components", "invariants": "FromShifts",
            "input_policy": "Preserve"}, "actual native conventions/settings")
        supervision_name = DIRECTORY + "/cases/" + ident + "/supervision.json"
        if exists(supervision_name):
            supervision = document(read(supervision_name))
            row["supervision_source"] = supervision_name
            request_name = DIRECTORY + "/cases/" + ident + "/request.json"
            request_body = read(request_name)
            require(document(request_body) == actual_request
                    and supervision.get("request_sha256") == digest(request_body),
                    "supervised saved request matches the captured numerical request")
            row["saved_terminal_success"] = (
                supervision.get("returncode") == 0
                and supervision.get("owned_group_gone") is True
                and supervision.get("source_hashes_unchanged") is True
                and supervision.get("binary_unchanged_after") is True
                and supervision.get("binary_sha256") == built.get("binary_sha256")
                and supervision.get("timed_out") is False
                and supervision.get("result_sha256") == digest(result_body)
                and result.get("status") == "measured"
                and result.get("timing_qualified") is True
                and result.get("all_successful_finite_full_arrays") is True
                and result.get("all_outputs_exactly_reproduced") is True
                and result.get("input_preserved") is True)
            row["saved_native_returncode"] = supervision.get("returncode")
            row["saved_native_timed_out"] = supervision.get("timed_out")
        first = result.get("first_output")
        if not first or first.get("lanes", [{}])[0].get("status") != "Success":
            row["status"] = "native_failed_or_no_successful_first_array"
            row["first_lane_statuses"] = [v.get("status") for v in first.get("lanes", [])] if first else []
            row["first_diagnostics"] = result.get("first_diagnostics")
            failed_native_rows += 1
            rows.append(row)
            continue
        require(first.get("basis") == expected_basis and first.get("components") == 1
                and first.get("laurent_order") == OUTPUT_POLES
                and first.get("convention") == "IregiNative"
                and first.get("tensor_weights") == "Components"
                and type(first.get("lanes")) is list and len(first["lanes"]) == 1
                and first["lanes"][0].get("lane") == 0,
                "successful native array complete basis/convention/Laurent layout")
        lane = first["lanes"][0]
        require(type(lane.get("fallback_used")) is bool and type(lane.get("analytic_used")) is bool,
                "native route tags")
        actual = native_values(lane.get("values"), len(expected_basis)*4)
        row["successful_first_output_available"] = True
        row["fallback_used"] = lane["fallback_used"]
        row["analytic_used"] = lane["analytic_used"]
        successful_arrays += 1
        reference_basis = basis(entry["reference_maximum_rank"])
        reference_indices = {tuple(v): i for i, v in enumerate(reference_basis)}
        q2 = natural_scale_squared(request)
        require(q2 == 9, "unchanged exact family dimensional scale Q=3")
        row["normalization_scale_squared"] = str(q2)
        comparisons = []
        maximum = F(0)
        maxima_by_slot = [F(0)]*4
        for moment, monomial in enumerate(expected_basis):
            reference_index = reference_indices[tuple(monomial)]
            dimension = sum(monomial)+4+2*request["dimension_shift"]-2*sum(request["powers"])
            natural_squared = q2**dimension
            for slot in range(4):
                a = actual[4*moment+slot]
                b = reference[reference_index][slot]
                error_squared = squared_norm((a[0]-b[0], a[1]-b[1])) / max(
                    natural_squared, squared_norm(b))
                passed = error_squared <= SQUARED_TOLERANCE
                comparisons.append({
                    "moment": moment, "reference_moment": reference_index,
                    "monomial": monomial, "Laurent_slot": REFERENCE_POLES[slot],
                    "mass_dimension": dimension,
                    "actual_exact": [str(v) for v in a],
                    "reference_exact_decimal_fraction": [str(v) for v in b],
                    "squared_normalized_error": str(error_squared),
                    "passed_1e_minus_10": passed,
                })
                maximum = max(maximum, error_squared)
                maxima_by_slot[slot] = max(maxima_by_slot[slot], error_squared)
                row["compared_complex_fields"] += 1
                row["compared_real_components"] += 2
                if not passed:
                    row["failed_complex_fields"] += 1
        row["maximum_normalized_complex_error"] = display_sqrt(maximum)
        row["maximum_squared_normalized_complex_error_exact"] = str(maximum)
        row["maximum_normalized_error_by_Laurent_slot"] = {
            name: display_sqrt(v) for name, v in zip(REFERENCE_POLES, maxima_by_slot)}
        row["comparisons"] = comparisons
        row["numerical_agreement"] = row["failed_complex_fields"] == 0
        row["status"] = "passed_complete_first_array_vs_admitted_IBP" if row["numerical_agreement"] else "failed_reference_agreement"
        field_count += row["compared_complex_fields"]
        failure_count += row["failed_complex_fields"]
        rows.append(row)
    all_rows = successful_arrays == 18 and all(r["saved_terminal_success"] for r in rows)
    passed = failure_count == 0 and (not require_all or all_rows)
    return {
        "schema_version": 1,
        "status": "passed_available_saved_reference_comparisons" if passed else "failed_or_incomplete_saved_reference_comparisons",
        "available_reference_agreement_passed": failure_count == 0,
        "all_18_rows_mathematically_and_terminal_qualified": all_rows and failure_count == 0,
        "require_all": require_all, "passed_requested_replay_contract": passed,
        "expected_rows": 18, "successful_first_arrays_compared": successful_arrays,
        "unmeasured_rows": missing_rows, "native_failed_or_no_first_array_rows": failed_native_rows,
        "compared_complex_fields": field_count, "compared_real_components": 2*field_count,
        "failed_complex_fields": failure_count,
        "tolerance": "1e-10",
        "exact_acceptance_formula": "(|a_re-b_re|^2+|a_im-b_im|^2)/max((Q^2)^(rank+4+2h-2sum(powers)),|b_re|^2+|b_im|^2) <= 1e-20",
        "Q_definition": "max(1,mu,sqrt(abs(real squared mass)),sqrt(abs(pairwise Minkowski distance squared))); exact Q=3 for this selected real family",
        "basis_mapping": "Explicit monomial map from cumulative rank-R output to documented cumulative reference rank-6/7 IREGI basis; no assumption that arbitrary producer arrays share an order.",
        "Laurent_mapping": "Direct native UV single, IR single, IR double, finite. No UV/IR recombination, normalization adapter, tiny-pole projection or multinomial weights.",
        "numeric_gate": "Exact Fraction arithmetic; Decimal is used only to display square roots of squared normalized errors.",
        "reference_admission_scope": "Original IBP arrays retain their independently audited restricted admissions and approximately16-digit constants/stopping-criteria caveat despite113-bit storage. Stable flags and pole/parity identities do not certify every finite integral.",
        "known_rejected_PV_or_Hybrid_history": historical_qualifications,
        "rows": rows, "input_bindings": bindings,
        "native_or_integral_execution": False, "producer_comparator_import": False,
        "symbolic_or_production_algebra_added": False,
        "performance_or_uncertainty_qualification": False,
        "fresh_native_binary_or_process_guard_claim": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-all", action="store_true")
    parser.add_argument("--output", default=DIRECTORY + "/reference-comparison.json")
    args = parser.parse_args()
    root = Path.cwd().resolve()
    require((root/"Cargo.toml").is_file() and (root/INPUTS).is_file(), "run from repository root")

    def location(name):
        safe_name(name)
        path = (root/name).resolve()
        require(path.is_relative_to(root), "saved path escaped repository")
        return path

    try:
        report = audit(lambda name: location(name).read_bytes(),
                       lambda name: location(name).is_file(), require_all=args.require_all)
    except (ValueError, KeyError, IndexError, TypeError, OSError, tarfile.TarError) as error:
        report = {"schema_version": 1, "status": "saved_comparison_validation_error",
                  "passed_requested_replay_contract": False,
                  "error": str(error), "native_or_integral_execution": False}
    report["checker_sha256"] = digest(Path(__file__).read_bytes())
    destination = location(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({k: report[k] for k in [
        "status", "successful_first_arrays_compared", "unmeasured_rows",
        "native_failed_or_no_first_array_rows", "compared_complex_fields",
        "failed_complex_fields", "all_18_rows_mathematically_and_terminal_qualified",
        "passed_requested_replay_contract"] if k in report}))
    return 0 if report["passed_requested_replay_contract"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

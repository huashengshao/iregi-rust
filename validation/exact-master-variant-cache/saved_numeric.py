"""Portable saved-value checks for the private exact-master-cache experiment.

Only Python's standard library and supplied bytes are used.  The fixed tables
are numerical fixtures from the independent source-math review, not polynomial
or Taylor algebra.  No producer validator, native library, executable, live
process state, or omitted compiled artifact is accessed.  Manifest/source and
native provenance checks belong to the enclosing capsule checker.
"""

from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
import math
import re


OLD = "target/public-highpoint/numeric-types-dual"
FAILED = "target/public-highpoint/numeric-types-dual-shared-cache"
HERE = FAILED + "-link-closure"
AUDIT = "target/resume-20261025-review/typed-cache-link-independent-saved-audit.json"
SUPPLEMENT = "target/resume-20261025-review/typed-cache-link-independent-metadata-supplement.json"
DOMAINS = {"f64": (53, 1), "DoubleFloat": (106, 1),
           "Float128Dual": (128, 6), "Float256Dual": (256, 6)}
SHAPE = [[0, 0], [1, 0], [0, 1], [2, 0], [1, 1], [0, 2]]
SCHEDULE = [("singleton_affine", [0]), ("mixed", [0, 3, 1, 2, 0]),
            ("reordered", [2, 1, 0, 3, 0]), ("empty", []), ("singleton_again", [0])]
SETTINGS = dict(propagators=6, rank=0, powers=[1]*6, dimension_shift=0,
                algorithm="PassarinoVeltman", convention="IregiNative",
                tensor_weights="Components", invariants="FromShifts", input_policy="Preserve")
SCALE, TOL = F(1, 256), F(1, 10**10)
EXECUTION = {"analytic_rows", "argument_rows", "fallback_rows", "fallback_successes",
             "input_rows", "master_family_batches", "master_rows", "pentagon_box_rows", "reduction_rows"}
CERTIFICATE = {"evaluated_rows", "input_rows", "passes", "reduction_batches"}
PACKING = {"child_batch_calls", "packed_child_rows", "packed_parent_rows", "parent_batch_calls", "parent_input_rows"}
WORK = PACKING | {"child_execution", "parent_execution", "child_certificate_execution", "parent_certificate_execution"}


def _require(value, message):
    if not value:
        raise ValueError("saved numeric: " + message)


def _json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("saved numeric: nonfinite JSON constant: " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def _operand(value):
    _require(isinstance(value, dict) and set(value) == {"rational", "precision", "negative_sign", "finite"}, "operand metadata")
    _require(value["finite"] is True and isinstance(value["rational"], str), "nonfinite operand")
    result = F(value["rational"])
    _require(type(value["precision"]) is int and value["precision"] >= 0
             and (result == 0 or value["precision"] > 0), "operand precision")
    _require(type(value["negative_sign"]) is bool
             and (result == 0 or value["negative_sign"] == (result < 0)), "operand sign")
    return result


def _z(value):
    _require(isinstance(value, list) and len(value) == 2, "complex width")
    return tuple(_operand(part) for part in value)


def _error2(actual, expected):
    return sum((x-y)**2 for x, y in zip(actual, expected)) / max(SCALE**2, sum(x*x for x in expected))


def _decimal_error(squared):
    with localcontext() as context:
        context.prec = 100
        return str((Decimal(squared.numerator)/Decimal(squared.denominator)).sqrt())


def _stage(record, count, bound, reserve, groups):
    _require(record["status"] in ["passed", "failed"] and record["inputs_unchanged"] is True, "stage admission")
    _require(record["bound_seconds"] == bound and record["postwork_reserve_seconds"] == reserve
             and record["cleanup_errors"] == [], "stage limits/cleanup")
    elapsed = record["elapsed_seconds"]
    _require(type(elapsed) in [int, float] and math.isfinite(elapsed) and 0 <= elapsed <= bound, "aggregate bound")
    _require(len(record["steps"]) == count, "process ledger size")
    for step in record["steps"]:
        _require(step["status"] in ["exited", "failed"] and step["owned_group_gone"] is True, "saved child terminal")
        _require(0 < step["timeout_seconds"] <= bound-reserve, "work reserve")
        group = step["owned_process_group"]
        _require(type(group) is int and group > 0 and group not in groups, "owned group identity")
        groups.append(group)
        if record["status"] == "passed":
            _require(step["status"] == "exited" and step["returncode"] == 0
                     and not any(step.get(k) for k in ["timeout", "error", "cancellation"]), "failed successful child")


def _tables():
    # Fixed numeric equalities from dilation-math-source-review.json.
    a, b = F(1152921504606846977, 1152921504606846976), F(3, 2)
    linear = [[1, a, b, 0, 0, 0], [1, a, b, 0, a*b, 0], [1, 0, 0, 0, 0, 0]]
    square = [[1, 2*a, 2*b, a*a, 2*a*b, b*b], [1, 2*a, 2*b, a*a, 4*a*b, b*b], [1, 0, 0, 0, 0, 0]]
    response = [[1, -8*a, -8*b, 36*a*a, 72*a*b, 36*b*b],
                [1, -8*a, -8*b, 36*a*a, 64*a*b, 36*b*b], [1, 0, 0, 0, 0, 0]]
    return linear, square, response


def _counters(value, keys):
    _require(isinstance(value, dict) and set(value) == keys, "counter field inventory")
    _require(all(type(n) is int and n >= 0 for n in value.values()), "counter integer domain")


def _work(call):
    work, indices = call["execution"], call["profile_indices"]
    _require(set(work) == WORK, "packing inventory")
    _counters({k: work[k] for k in PACKING}, PACKING)
    active = sum(i != 3 for i in indices)
    successes = sum(lane["status"] == "Success" for lane in call["lanes"])
    _require(work["parent_input_rows"] == len(indices)
             and work["child_batch_calls"] == int(active > 0)
             and work["packed_child_rows"] == 6*active, "instruction-major child packing")
    _require(successes <= work["packed_parent_rows"] <= active
             and work["parent_batch_calls"] == int(work["packed_parent_rows"] > 0), "active/success parent packing")
    for side in ["child", "parent"]:
        execution, certificate = work[side+"_execution"], work[side+"_certificate_execution"]
        _counters(execution, EXECUTION)
        _counters(certificate, CERTIFICATE)
        _require(execution["input_rows"] == work["packed_"+side+"_rows"], "packed execution rows")
        _require(execution["fallback_successes"] <= execution["fallback_rows"] <= execution["reduction_rows"]
                 and execution["analytic_rows"] <= execution["reduction_rows"]
                 and execution["input_rows"] <= execution["reduction_rows"]
                 and execution["input_rows"] <= execution["argument_rows"]
                 and execution["master_family_batches"] <= execution["master_rows"], "execution counter bounds")
        _require(certificate["input_rows"] <= execution["input_rows"]
                 and certificate["input_rows"] <= certificate["evaluated_rows"]
                 and certificate["evaluated_rows"] <= certificate["input_rows"]*certificate["passes"]
                 and certificate["reduction_batches"] <= certificate["passes"], "certificate counter bounds")
        if certificate["input_rows"] == 0:
            _require(all(n == 0 for n in certificate.values()), "empty certificate reset")
    parent = work["parent_execution"]
    _require(parent["argument_rows"] == parent["reduction_rows"] == parent["input_rows"]
             and all(parent[k] == 0 for k in EXECUTION-{"argument_rows", "reduction_rows", "input_rows"})
             and all(n == 0 for n in work["parent_certificate_execution"].values()), "parent coefficient-only work")
    if not indices:
        _require(all(work[k] == 0 for k in PACKING)
                 and all(all(n == 0 for n in work[k].values()) for k in WORK-PACKING), "empty work reset")


def _metadata(data):
    inputs = [part for row in data["represented_input_rows"] for value in row for part in value]
    outputs, routes, completed = [], [], 0
    for call in data["calls"]:
        if call["status"] != "captured":
            continue
        completed += 1
        _work(call)
        _require(all(isinstance(x, list) and all(isinstance(s, str) and s for s in x)
                     for x in call["diagnostics"]), "diagnostic metadata")
        for row, lane in enumerate(call["lanes"]):
            _require(type(lane["fallback_used"]) is bool and type(lane["analytic_used"]) is bool, "boolean route flags")
            available = lane["values"] is not None
            _require(available == (lane["status"] == "Success"), "failure cannot return partial/zero values")
            routes.append(dict(call=call["name"], row=row, profile=lane["profile"],
                               fallback_used=lane["fallback_used"], analytic_used=lane["analytic_used"], available=available))
            if available:
                outputs.extend(part for value in lane["values"] for part in value)
    for part in inputs+outputs:
        _operand(part)
    result = dict(complete_call_work_records_checked=completed,
                  input_operand_precision_values=sorted({x["precision"] for x in inputs}),
                  output_operand_precision_values=sorted({x["precision"] for x in outputs}),
                  negative_input_zero_operands=sum(F(x["rational"]) == 0 and x["negative_sign"] for x in inputs),
                  negative_output_zero_operands=sum(F(x["rational"]) == 0 and x["negative_sign"] for x in outputs),
                  route_flags=routes)
    return result, len(inputs)+len(outputs)


def _inspect(domain, data, run, original, scalar, base):
    bits, components = DOMAINS[domain]
    report = dict(full_gate=False, available_slots=0, successful_lanes=0, invalid_rejections=0,
                  input_slots_checked=0, complete_calls=0, empty_calls=0, numerical_failures=[],
                  incomplete_or_rejected_positives=[], maxima={}, original_comparisons=0,
                  identity_comparisons=0, exact_pole_zeros=0, repeated_representation_differences=[])
    available = {}
    _require(data["domain"] == domain.removesuffix("Dual") and data["settings"] == SETTINGS
             and data["working_bits"] == bits and data["requested_bits"] == 53, "capture domain/settings")
    _require(data["status"] in ["capture_complete_not_yet_qualified", "evaluating_batch"], "saved capture status")
    report["capture_status"] = data["status"]
    _require(data["components"] == components and data["ordered_shape"] == (SHAPE if components == 6 else None), "Taylor layout")
    _require(data["basis"] == [[0, 0, 0, 0]], "scalar basis")
    linear, square, response = _tables()
    _require([[F(x) for x in row] for row in data["exact_homogeneity_multipliers"]] == response, "response fixture")
    rows = data["represented_input_rows"]
    _require(len(rows) == 4 and all(len(row) == 31*components for row in rows), "input jet inventory")
    for profile, row in enumerate(rows):
        for parameter in range(31):
            multipliers = (square if 24 <= parameter < 30 else linear)[0 if profile == 3 else profile]
            for component in range(components):
                expected = 0 if profile == 3 and parameter == 30 else base[parameter]*multipliers[component]
                _require(_z(row[parameter*components+component]) == (expected, 0), "exact beyond53 input")
                report["input_slots_checked"] += 1
    first, flags, unexpected = {}, {}, []
    def compare(actual, expected, target, location):
        squared = _error2(actual, expected)
        report["maxima"][target] = max(report["maxima"].get(target, F(0)), squared)
        if squared > TOL**2:
            report["numerical_failures"].append(dict(target=target, location=location, normalized_error=_decimal_error(squared)))
    for index, call in enumerate(data["calls"]):
        _require(index < 5 and (call["name"], call["profile_indices"]) == SCHEDULE[index], "call schedule")
        _require(call["status"] == "captured" and call["input_preserved_exactly"] is True, "complete captured-call policy")
        indices = call["profile_indices"]
        _require(call["components"] == components and call["basis"] == [[0, 0, 0, 0]], "returned shape")
        _require(call["metadata"] == dict(convention="IregiNative", tensor_weights="Components", dual_shape=SHAPE if components == 6 else None), "returned metadata")
        _require(len(call["lanes"]) == len(indices) == len(call["diagnostics"]), "lane inventory")
        report["complete_calls"] += 1
        if not indices:
            report["empty_calls"] += 1
            _require(call["diagnostics"] == [], "empty diagnostics")
        for row, (profile, lane) in enumerate(zip(indices, call["lanes"])):
            _require(lane["row"] == row and lane["profile"] == profile, "lane identity")
            values = lane["values"]
            if profile == 3:
                _require(values is None and lane["status"].startswith("InvalidInput(")
                         and not lane["fallback_used"] and not lane["analytic_used"] and call["diagnostics"][row] == [], "invalid input policy")
                report["invalid_rejections"] += 1
                continue
            if values is None or lane["status"] != "Success":
                _require(values is None and lane["status"].startswith("Unstable("), "unexpected positive failure policy")
                report["incomplete_or_rejected_positives"].append(dict(call=index, row=row, profile=profile,
                    status_prefix=lane["status"][:180], status_sha256=hashlib.sha256(lane["status"].encode()).hexdigest(),
                    values_available=values is not None))
                unexpected.append(dict(call=call["name"], profile=profile, row=row, status=lane["status"]))
                continue
            _require(len(values) == 4*components, "incomplete successful array")
            report["successful_lanes"] += 1
            old = first.setdefault(profile, values)
            route = (lane["fallback_used"], lane["analytic_used"])
            _require(profile not in flags or flags[profile] == route, "repeated profile route changed")
            flags[profile] = route
            for slot, raw in enumerate(values):
                pole, component = divmod(slot, components)
                value = _z(raw)
                where = dict(call=index, row=row, profile=profile, laurent_slot=pole, component=component)
                _require(pole == 3 or value == (0, 0), "nonzero pole")
                report["exact_pole_zeros"] += int(pole != 3)
                _require(profile != 2 or component == 0 or value == (0, 0), "nonzero constant derivative")
                target = tuple((response[profile][component] if components == 6 else 1)*x for x in scalar[pole])
                compare(value, target, "qualified_scalar_times_independent_symbolic_multiplier", where)
                report["identity_comparisons"] += 1
                if component == 0:
                    compare(value, original[pole], "untouched_original_IBP_primal", where)
                    report["original_comparisons"] += 1
                compare(value, _z(old[slot]), "same_profile_first_success", where)
                if raw != old[slot]:
                    report["repeated_representation_differences"].append(where)
                available[(index, row, profile, slot)] = raw
                report["available_slots"] += 1
    complete = data["status"] == "capture_complete_not_yet_qualified"
    _require(data.get("unexpected_outcomes", []) == unexpected, "unexpected-outcome ledger")
    if complete:
        _require(len(data["calls"]) == 5 and data["active_call"] == "singleton_again"
                 and data["successful_lanes"] == report["successful_lanes"]
                 and data["rejected_lanes"] == 12-report["successful_lanes"]
                 and data["intended_successes_available"] == (report["successful_lanes"] == 10)
                 and data["expected_invalid_rejections_confirmed"] == (report["invalid_rejections"] == 2), "complete capture ledger")
    else:
        _require(len(data["calls"]) == 1 and data["active_call"] == "mixed"
                 and run["status"] == "failed", "partial capture must remain incomplete")
    report["full_gate"] = (run["status"] == "passed" and complete
        and report["complete_calls"] == 5 and report["successful_lanes"] == 10
        and report["invalid_rejections"] == 2 and report["empty_calls"] == 1
        and report["available_slots"] == 40*components and not report["numerical_failures"]
        and not report["incomplete_or_rejected_positives"])
    report["maxima"] = {target: _decimal_error(value) for target, value in report["maxima"].items()}
    report["runtime_status"], report["runtime_seconds"] = run["status"], run["elapsed_seconds"]
    return report, available


def _log_attribution(files, load):
    saved = load(HERE+"/saved-preparation-comparison.json")
    _require(saved["status"] == "saved_existing_log_attribution_only"
             and saved["new_profiles_or_integrals_executed"] is False
             and set(saved["logs"]) == set(DOMAINS), "preparation-only attribution")
    events_checked = 0
    for domain in DOMAINS:
        for kind, root in [("original", OLD), ("shared_cache", HERE)]:
            path = root+f"/run-{domain}-001/step-0.log"
            raw, data = files[path], load(root+f"/run-{domain}-001/result.json")
            lines, events = raw.decode().splitlines(), []
            for index, line in enumerate(lines, 1):
                match = re.fullmatch(r"(iregi.*): ([0-9]+(?:\.[0-9]+)?)s", line)
                if match:
                    events.append(dict(line=index, label=match[1], seconds=match[2]))
            exact = [e for e in events if e["label"] == "iregi preparation scalar master exact evaluators"]
            expected = dict(path=path, sha256=hashlib.sha256(raw).hexdigest(),
                exact_master_event_count=len(exact), exact_master_events=exact,
                last_completed_logged_preparation=events[-1] if events else None,
                last_lines=lines[-5:], capture_status=data["status"], active_call=data["active_call"],
                completed_calls=[c["name"] for c in data["calls"]],
                available_complex_slots=sum(len(lane["values"] or []) for call in data["calls"] for lane in call["lanes"]))
            if "all_logged_preparation_events" in saved["logs"][domain][kind]:
                expected["all_logged_preparation_events"] = events
            _require(saved["logs"][domain][kind] == expected, "saved log attribution differs: "+domain+"/"+kind)
            events_checked += len(events)
    return events_checked


def check_saved(files: dict[str, bytes], read_repo: callable) -> dict:
    """Recompute saved numerical gates; raise ValueError on evidence mismatch.

    ``files`` uses original repository-relative ``target/...`` keys, including
    both independent review receipts. ``read_repo`` is used only for the three
    committed fixture/reference/scalar-baseline JSON files below. It must return
    their original bytes, without executing the original archive's scripts.
    This function neither qualifies native artifacts nor measures performance.
    """
    def load(path):
        return _json(files[path])
    def committed(path):
        return _json(read_repo(path))
    audit, supplement = load(AUDIT), load(SUPPLEMENT)
    _require(hashlib.sha256(files[AUDIT]).hexdigest() == "332772366147121e12766144f3b8ae29e18b14d174112f09637768451d4f4919", "independent audit identity")
    _require(hashlib.sha256(files[SUPPLEMENT]).hexdigest() == "3febc1494e665706b5bd25da86168298a675aadd90bdf457a5702f379d9afaff", "metadata supplement identity")
    _require(audit["status"] == "passed_independent_saved_audit" and audit["findings"] == []
             and supplement["status"] == "passed_independent_saved_work_and_operand_metadata_supplement"
             and supplement["findings"] == [], "independent review admission")
    fixture = committed("validation/public-highpoint/fixture-conditioned_masses.json")["samples"][0]
    props = fixture["propagators"][:6]
    base = [F(x) for prop in props for x in prop["shift"]] + [F(p["mass_squared"][0]) for p in props] + [F(fixture["mu"])]
    reference = committed("validation/public-highpoint/reference-conditioned_masses.json")
    reference = [c for c in reference["cases"] if c["id"] == "n6_base_mode0"]
    _require(len(reference) == 1 and reference[0]["response"]["stable"] is True, "original reference")
    original = [tuple(F(x) for x in v) for v in reference[0]["response"]["moments"][0]]
    baseline = committed("validation/highpoint-six-point-api/qualified-v2/public-rank3-256-001/result.json")
    scalar = [tuple(F(v[part]) for part in ["real", "imaginary"]) for v in baseline["lanes"][0]["moments"][0]]
    groups, reports, available, metadata, historical = [], {}, {}, {}, []
    failed, failed_q = load(FAILED+"/build-001/build.json"), load(FAILED+"/qualification.json")
    _stage(failed, 2, 90, 25, groups)
    _require(failed["status"] == "failed" and failed["steps"][0]["returncode"] == 0
             and failed["steps"][1]["returncode"] != 0
             and failed_q["status"] == "not_numerically_executed_driver_dependency_resolution_failure"
             and all(d["status"] == "not_attempted_build_prerequisite_failed" and d["numeric_result_available"] is False
                     for d in failed_q["domains"].values()), "failed-link attempt must remain visible")
    driver = load(HERE+"/build-001/build.json")
    _stage(driver, 1, 90, 25, groups)
    _require(driver["status"] == "passed", "saved driver build")
    operands = 0
    for domain in DOMAINS:
        run = load(HERE+f"/run-{domain}-001/run.json")
        _stage(run, 1, 180, 20, groups)
        _require(run["operation"] == domain, "runtime domain")
        data = load(HERE+f"/run-{domain}-001/result.json")
        report, slots = _inspect(domain, data, run, original, scalar, base)
        meta, count = _metadata(data)
        _require(report == audit["domains"][domain], "independent capture result differs: "+domain)
        _require(meta == supplement["domains"][domain], "independent work/operand metadata differs: "+domain)
        _require(load(HERE+f"/comparison-{domain}.json")["passed"] == report["full_gate"], "producer complete gate differs")
        reports[domain], available[domain], metadata[domain] = report, slots, meta
        operands += count
        old = load(OLD+f"/run-{domain}-001/result.json")
        for ci, call in enumerate(old["calls"]):
            for row, lane in enumerate(call["lanes"]):
                _require((lane["values"] is not None) == (lane["status"] == "Success"), "old null/status policy")
                if lane["values"] is None:
                    continue
                for index, previous in enumerate(lane["values"]):
                    location = (ci, row, lane["profile"], index)
                    current = slots.get(location)
                    historical.append(dict(domain=domain, location=list(location), available=current is not None,
                        within_tolerance=current is not None and _error2(_z(current), _z(previous)) <= TOL**2,
                        represented_metadata_equal=current == previous))
    paired, pair_meta, pair_errors = [], [], []
    for location, low in available["Float128Dual"].items():
        high = available["Float256Dual"].get(location)
        if high is None:
            continue
        error = _error2(_z(low), _z(high))
        pair_errors.append(error)
        paired.append(dict(location=list(location), within_tolerance=error <= F(1, 2**160)))
        slot = location[3]
        pair_meta.append(dict(laurent_slot=slot//6, component=slot%6,
            exact_real_equal=F(low[0]["rational"]) == F(high[0]["rational"]),
            exact_imaginary_equal=F(low[1]["rational"]) == F(high[1]["rational"]),
            real_sign_equal=low[0]["negative_sign"] == high[0]["negative_sign"],
            imaginary_sign_equal=low[1]["negative_sign"] == high[1]["negative_sign"],
            real_precision=[low[0]["precision"], high[0]["precision"]],
            imaginary_precision=[low[1]["precision"], high[1]["precision"]]))
    _require(historical == audit["original_slot_matches"] and len(historical) == 64
             and all(x["available"] and x["within_tolerance"] and x["represented_metadata_equal"] for x in historical), "old64 exact metadata preservation")
    _require(paired == audit["paired_comparisons"] and len(paired) == 24 and all(x["within_tolerance"] for x in paired), "available paired prefix")
    _require(pair_meta == supplement["partial_pair_component_metadata"]
             and _decimal_error(max(pair_errors)) == supplement["partial_pair_max_normalized_error"], "partial paired metadata/error")
    full_pair = (all(reports[d]["full_gate"] for d in ["Float128Dual", "Float256Dual"])
                 and len(paired) == 240 and all(x["within_tolerance"] for x in paired))
    pair_gate = load(HERE+"/comparison-paired.json")
    _require(full_pair is False and audit["complete_precision_convergence_qualified"] is False
             and supplement["complete_precision_convergence_qualified"] is False
             and pair_gate["passed"] is False and pair_gate["precision_convergence_qualified"] is False, "partial data cannot qualify full convergence")
    outputs = sum(r["available_slots"] for r in reports.values())
    inputs = sum(r["input_slots_checked"] for r in reports.values())
    calls = sum(m["complete_call_work_records_checked"] for m in metadata.values())
    _require(outputs == audit["available_output_slots_checked"] == 88
             and inputs == audit["represented_input_slots_checked"] == 1736
             and operands == supplement["finite_real_or_imaginary_operands_checked"] == 3648
             and calls == supplement["complete_call_work_records_checked"] == 12
             and groups == audit["owned_process_groups_checked_absent"], "recomputed inventory totals")
    _require(supplement["partial_paired_complex_slots_checked"] == 24
             and supplement["partial_pair_within_2_minus_80"] is True, "partial pair supplement totals")
    qualification = load(HERE+"/qualification.json")
    for domain, report in reports.items():
        q = qualification["domains"][domain]
        _require(q["full_numeric_gate_passed"] == report["full_gate"]
                 and q["coverage"]["complex_slots"] == report["available_slots"]
                 and q["coverage"]["successful_lanes"] == report["successful_lanes"], "consolidated domain gate differs")
    for key in ["complete_precision_convergence_qualified", "public_dual_qualified",
                "derivative_uncertainty_transport_qualified", "performance_qualified", "production_adoption"]:
        _require(qualification[key] is False, "unsupported qualification claim: "+key)
    _require(all(not r["numerical_failures"] for r in reports.values())
             and {d: r["full_gate"] for d, r in reports.items()} ==
             {"f64": False, "DoubleFloat": True, "Float128Dual": False, "Float256Dual": False}, "fixed domain acceptance")
    events = _log_attribution(files, load)
    return dict(status="passed_saved_numeric_checks", domains=reports,
        available_output_slots_checked=outputs, represented_input_slots_checked=inputs,
        complete_call_work_records_checked=calls, finite_real_or_imaginary_operands_checked=operands,
        historical_exact_metadata_matches=len(historical), available_partial_precision_pairs_checked=len(paired),
        logged_preparation_events_checked=events, saved_owned_group_terminal_claims_checked=len(groups),
        complete_precision_convergence_qualified=False, public_dual_qualified=False,
        derivative_uncertainty_transport_qualified=False, performance_qualified=False,
        native_artifacts_qualified_by_this_checker=False, live_process_state_checked=False,
        compiler_or_evaluator_executed=False,
        scope="Private N6 rank0 retained point and one coherent dilation; partial Dual schedules remain unqualified. Preparation log times are diagnostic observations.")

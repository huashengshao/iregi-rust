#!/usr/bin/env python3
"""Saved-only independent review of the 38 binary64 TIRust attempts.

No producer module, native library, compiler, integral or subprocess is run.
Normal replay checks saved source/binary associations; optional live flags
also rehash current source files or the frozen executable and say so explicitly.
Only run after the root-owned numerical quiet window has ended.
"""

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path


HERE = "validation/benchmark/opening-double-20261026"
OLD = "validation/benchmark/opening-rank6-20261026"
OLD_INPUT_SHA = "a065511103c41ad04d14a01b3189c5180aa4d02af0c308ce2438fa3bf6cca43a"
OLD_COMPARISON_SHA = "5d72855e1ad01690c534672d39c7a12e4e2bbbf043b4215a1b163375c95cae8e"
DRIVER = "crates/iregi-rust/examples/opening_double.rs"
HIGH_THREE = {"ordinary-n5-r5", "ordinary-n5-r6", "ordinary-n6-r6"}
POLES = ["UV single", "IR single", "IR double", "finite"]
FIELDS = ("outer_total_ns", "scalar_masters_ns", "tirust_exclusive_ns")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def safe(name):
    require(type(name) is str and name and not name.startswith("/")
            and "\\" not in name
            and all(p not in ("", ".", "..") for p in name.split("/")),
            "unsafe project-relative byte name")
    return name


def document(body):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError("nonfinite JSON number: " + value)

    return json.loads(body, object_pairs_hook=unique, parse_float=F,
                      parse_constant=nonfinite)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def describe(body):
    return {"sha256": sha(body), "bytes": len(body)}


def basis(rank):
    # Documented IREGI index enumeration, not a polynomial/algebra engine.
    return [[t, x, y, r-t-x-y] for r in range(rank+1)
            for t in range(r, -1, -1) for x in range(r-t, -1, -1)
            for y in range(r-t-x, -1, -1)]


def shown_sqrt(value):
    if value is None:
        return None
    with localcontext() as context:
        context.prec = 70
        return str((Decimal(value.numerator)/Decimal(value.denominator)).sqrt())


def operand(value, *, binary64):
    require(type(value) is dict and set(value) == {
        "exact_rational", "working_bits", "negative_sign", "finite"},
        "represented operand fields")
    require(value["finite"] is True and type(value["exact_rational"]) is str,
            "finite exact represented operand")
    require(type(value["working_bits"]) is int and value["working_bits"] > 0
            and (not binary64 or value["working_bits"] == 53),
            "ordinary binary64 represented precision")
    require(type(value["negative_sign"]) is bool, "represented sign metadata")
    q = F(value["exact_rational"])
    require(q == 0 or value["negative_sign"] == (q < 0), "represented sign")
    if binary64:
        # An exact binary64 value has a power-of-two denominator, at most53
        # significant bits, and is in the finite binary64 exponent envelope.
        denominator = q.denominator
        require(denominator & (denominator-1) == 0, "binary denominator")
        numerator = abs(q.numerator)
        if numerator:
            odd = numerator >> ((numerator & -numerator).bit_length()-1)
            require(odd.bit_length() <= 53 and abs(q) <= F(2**1024-2**971)
                    and denominator <= 2**1074, "representable finite f64 coefficient")
    return q


def complex_values(values, count, *, binary64):
    require(type(values) is list and len(values) == count, "full complex-field count")
    result = []
    for pair in values:
        require(type(pair) is list and len(pair) == 2, "complete complex pair")
        result.append(tuple(operand(v, binary64=binary64) for v in pair))
    return result


def norm2(value):
    return value[0]**2+value[1]**2


def array_check(array, reference, request):
    """Exact whole-array E/A and the separately retained old mixed metric."""
    answer = {"complete_finite_success": False, "accessible": False,
              "relative_error_at_most_1e3": False,
              "relative_error_at_most_1e6": False,
              "compared_complex_fields": 0, "errors": []}
    if array is None:
        answer["status"] = "no_array_payload"
        return answer
    try:
        expected_basis = basis(request["rank"])
        require(array.get("basis") == expected_basis and array.get("components") == 1
                and array.get("laurent_order") == POLES
                and array.get("convention") == "IregiNative"
                and array.get("tensor_weights") == "Components",
                "native cumulative basis/convention/weights/Laurent layout")
        lanes = array.get("lanes")
        require(type(lanes) is list and len(lanes) == 1 and lanes[0].get("lane") == 0,
                "one explicit sample lane")
        lane = lanes[0]
        require(type(lane.get("fallback_used")) is bool
                and type(lane.get("analytic_used")) is bool
                and type(lane.get("status")) is str, "status and actual-route flags")
        answer.update(lane_status=lane["status"], fallback_used=lane["fallback_used"],
                      analytic_used=lane["analytic_used"])
        if lane["status"] != "Success":
            require(lane.get("values") is None, "a failed guarded lane must expose null coefficients")
            answer["status"] = "honest_guarded_refusal_null_values"
            return answer
        values = complex_values(lane.get("values"), len(expected_basis)*4, binary64=True)
        require(reference.get("basis") == expected_basis and reference.get("components") == 1
                and reference.get("laurent_order") == POLES
                and reference.get("convention") == "IregiNative"
                and reference.get("tensor_weights") == "Components"
                and len(reference.get("lanes", [])) == 1
                and reference["lanes"][0].get("status") == "Success", "admitted reference layout/status")
        expected = complex_values(reference["lanes"][0]["values"], len(values), binary64=False)
        mu = F(request["samples"][0]["mu"])
        require(mu > 0, "positive dimensional weighting scale")
        error2 = F(0)
        amplitude2 = F(0)
        mixed2 = F(0)
        worst = None
        for index, (a, b) in enumerate(zip(values, expected)):
            degree = sum(expected_basis[index//4])
            dimension = degree+4+2*request["dimension_shift"]-2*sum(request["powers"])
            weight2 = mu**(2*dimension)
            delta2 = norm2((a[0]-b[0], a[1]-b[1]))
            component_error2 = delta2/weight2
            if component_error2 > error2:
                worst = {"complex_field": index, "moment": index//4,
                         "monomial": expected_basis[index//4], "Laurent": POLES[index%4]}
            error2 = max(error2, component_error2)
            amplitude2 = max(amplitude2, norm2(b)/weight2)
            mixed2 = max(mixed2, delta2/max(weight2, norm2(b)))
        relative2 = error2/amplitude2 if amplitude2 else (F(0) if error2 == 0 else None)
        answer.update(status="complete_finite_success_compared", accessible=True,
                      complete_finite_success=True, compared_complex_fields=len(values),
                      relative_error_squared_exact=str(relative2) if relative2 is not None else None,
                      relative_error=shown_sqrt(relative2),
                      maximum_scaled_absolute_error_squared_exact=str(error2),
                      maximum_scaled_reference_amplitude_squared_exact=str(amplitude2),
                      maximum_componentwise_mixed_squared_exact=str(mixed2),
                      maximum_componentwise_mixed_error=shown_sqrt(mixed2),
                      relative_error_at_most_1e3=relative2 is not None and relative2 <= F(1, 10**6),
                      relative_error_at_most_1e6=relative2 is not None and relative2 <= F(1, 10**12),
                      worst_scaled_absolute_error_field=worst)
    except (ValueError, KeyError, IndexError, TypeError, OverflowError) as error:
        answer.update(status="malformed_or_nonfinite_array", errors=[str(error)])
    return answer


def block_statistics(blocks):
    require(type(blocks) is list and blocks, "recorded timing blocks")
    exact = {name: [] for name in FIELDS}
    count = None
    for index, block in enumerate(blocks):
        require(block.get("repeat") == index
                and block.get("all_statuses_and_accessible_arrays_reproduced") is True,
                "complete repeat sequence and repeated outputs")
        calls = block.get("calls")
        require(type(calls) is list and calls, "nonempty block calls")
        if count is None:
            count = len(calls)
        require(len(calls) == count, "fixed loop count for every block")
        for call in calls:
            required = set(FIELDS) | {"profile_total_ns", "profile_arguments_ns",
                                     "profile_recurrence_and_stability_ns"}
            require(set(call) == required and all(type(call[k]) is int and call[k] >= 0
                                                for k in required), "nonnegative integer timing fields")
            require(call["outer_total_ns"] > 0
                    and call["outer_total_ns"] == call["scalar_masters_ns"]+call["tirust_exclusive_ns"],
                    "same-call exact additive master split")
            require(call["profile_arguments_ns"]+call["scalar_masters_ns"]
                    + call["profile_recurrence_and_stability_ns"] <= call["profile_total_ns"]
                    <= call["outer_total_ns"], "nonoverlapping nested stages within outer wall time")
        for field in FIELDS:
            exact[field].append(F(sum(call[field] for call in calls), len(calls)*1000))
    described = {}
    for field, values in exact.items():
        mean = sum(values)/len(values)
        variance = sum((v-mean)**2 for v in values)/(len(values)-1) if len(values) > 1 else None
        deviation = math.sqrt(float(variance)) if variance is not None else None
        described[field.removesuffix("_ns")+"_us"] = {
            "mean_exact": str(mean), "mean": float(mean),
            "median": float(sorted(values)[len(values)//2]) if len(values)%2 else float(
                (sorted(values)[len(values)//2-1]+sorted(values)[len(values)//2])/2),
            "minimum": float(min(values)), "maximum": float(max(values)),
            "stdev": deviation,
            "standard_error": deviation/math.sqrt(len(values)) if deviation is not None else None,
        }
    return {"timing": described, "repeats": len(blocks), "calls_per_repeat": count,
            "total_timed_calls": len(blocks)*count,
            "outer_mean_us_exact": sum(exact["outer_total_ns"])/len(blocks),
            "maximum_additive_error_us": 0}


def close_numeric(actual, expected, label):
    if expected is None:
        require(actual is None, label+" optional statistic")
    else:
        require(type(actual) in (int, F, float) and math.isfinite(float(actual))
                and math.isclose(float(actual), expected, rel_tol=1e-12, abs_tol=1e-9),
                "independent displayed statistic: "+label)


def audit(read_bytes, exists, *, summary_path=HERE+"/tirust-summary.json",
          verify_live_source=False, verify_live_binary=False):
    bindings = {}

    def read(name, expected=None):
        safe(name)
        body = read_bytes(name)
        require(type(body) is bytes and (expected is None or sha(body) == expected), "byte pin: "+name)
        desc = describe(body)
        require(name not in bindings or bindings[name] == desc, "changing input bytes: "+name)
        bindings[name] = desc
        return body

    def load(name, expected=None):
        return document(read(name, expected))

    suite = load(HERE+"/inputs.json")
    old_suite = load(OLD+"/inputs.json", OLD_INPUT_SHA)
    admission = load(OLD+"/reference-comparison.json", OLD_COMPARISON_SHA)
    require(admission.get("all_18_rows_mathematically_and_terminal_qualified") is True
            and admission.get("compared_complex_fields") == 8968
            and admission.get("failed_complex_fields") == 0, "previous restricted reference admission")
    built = load(HERE+"/build.json")
    require(built.get("status") == "built_and_frozen" and built.get("sources_unchanged") is True
            and built.get("features") == ["native-f64-abc"]
            and built.get("step", {}).get("returncode") == 0
            and built.get("step", {}).get("owned_group_gone") is True
            and built.get("step", {}).get("timed_out") is False,
            "feature-enabled successful source-guarded saved build")
    require(built.get("cargo_artifact", {}).get("profile", {}).get("opt_level") == "3",
            "optimized release artifact")
    source_guards = built.get("source_hashes")
    require(type(source_guards) is dict and DRIVER in source_guards
            and all(type(v) is str and len(v) == 64 for v in source_guards.values()), "selected source guards")
    old_source_names = set(load(OLD+"/source-files.json")["paths"])
    require(old_source_names.issubset(source_guards), "all previously selected core/source guards retained")
    for name in (HERE+"/inputs.json", HERE+"/make-inputs.py", HERE+"/run.py"):
        read(name, source_guards[name])
    driver = read(DRIVER, source_guards[DRIVER]).decode("utf-8")
    require('run(&request, 0.0_f64, path, &mut record)' in driver
            and 'request.numeric_type != "f64" || request.working_bits != 53' in driver
            and not any(token in driver for token in ["Float::", "DoubleFloat", "PrecisionRescue",
                                                     "TensorRescue", "rescue_workspace"]),
            "static ordinary-f64 main and no precision-rescue call")
    if verify_live_source:
        for name, expected in source_guards.items():
            read(name, expected)
    if verify_live_binary:
        read(built["binary_path"], built["binary_sha256"])
    require(len(suite.get("cases", [])) == len(old_suite["cases"]) == 18
            and sum(len(c["candidates"]) for c in suite["cases"]) == 38,
            "fixed18 rows/38 candidate attempts")
    safe(summary_path)
    summary = load(summary_path)
    summary_rows = {r["id"]: r for r in summary.get("rows", [])}
    require(len(summary_rows) == 18, "summary complete row inventory")
    output_rows = []
    checks = 0
    array_count = 0
    refused_arrays = 0
    hard_errors = []
    total_attempts = 0
    terminal_attempts = 0
    honest_failures = 0
    for case, old_case in zip(suite["cases"], old_suite["cases"]):
        ident = case["id"]
        request = case["driver_request"]
        require(ident == old_case["id"], "retained row ordering")
        for key in ("n", "rank", "powers", "dimension_shift", "samples"):
            require(request[key] == old_case["driver_request"][key], "unchanged input integral: "+ident)
        require(request["numeric_type"] == "f64" and request["working_bits"] == 53
                and request["requested_bits"] == (39 if ident in HIGH_THREE else 53),
                "working53 / requested39 only selected high3")
        require(request["algorithm"] == old_case["driver_request"]["algorithm"], "base requested method retained")
        expected_candidates = ["native-abc", "symbolica"] + (["thin-hybrid", "thin-pv"] if ident == "ordinary-n6-r6" else [])
        require([c["id"] for c in case["candidates"]] == expected_candidates, "fixed ordered candidate portfolio")
        reference_name = OLD+"/cases/"+ident+"/result.json"
        reference = load(reference_name, admission["input_bindings"][reference_name]["sha256"])["first_output"]
        item = summary_rows[ident]
        stored_attempts = {a["id"]: a for a in item.get("attempts", [])}
        require(len(stored_attempts) == len(case["candidates"]), "summary preserves every candidate")
        attempts = []
        for candidate in case["candidates"]:
            total_attempts += 1
            cid = candidate["id"]
            req = candidate["request"]
            require(req["numeric_type"] == "f64" and req["working_bits"] == 53
                    and req["requested_bits"] == request["requested_bits"], "every candidate uses f64/53")
            for key in ("n", "rank", "powers", "dimension_shift", "samples"):
                require(req[key] == request[key], "candidate preserves mathematical input")
            expected_policy = "NativeF64Abc" if cid == "native-abc" else "Symbolica"
            expected_method = "PassarinoVeltman" if cid == "thin-pv" else request["algorithm"]
            require(req["master_policy"] == expected_policy and req["algorithm"] == expected_method
                    and req.get("postconstruction_profiling") == cid.startswith("thin-"),
                    "predeclared policy, method and postconstruction profile route")
            folder = HERE+"/cases/"+ident+"/"+cid
            row = {"id": cid, "request": req, "terminal": False, "timing_captured": False,
                   "eligible": False, "finite_success": False, "array_reports": [], "warnings": []}
            if not exists(folder+"/supervision.json"):
                row["status"] = "unmeasured"
                require(stored_attempts[cid].get("status") == "unmeasured", "unrun candidate visible")
                attempts.append(row)
                continue
            step = load(folder+"/supervision.json")
            require(type(step.get("returncode")) is int
                    and type(step.get("timed_out")) is bool
                    and step.get("owned_group_gone") is True,
                    "saved terminal exit and completed owned-group cleanup")
            terminal_attempts += 1
            row["terminal"] = True
            req_body = read(folder+"/request.json", step["request_sha256"])
            require(document(req_body) == req, "exact supervised candidate request")
            require(step.get("id") == ident and step.get("candidate") == cid
                    and step.get("cpu") == 18
                    and step.get("binary_sha256") == built["binary_sha256"]
                    and step.get("binary_unchanged_after") is True
                    and step.get("source_hashes_unchanged") is True,
                    "frozen candidate/source/binary association and CPU18")
            command = step.get("command")
            require(type(command) is list and len(command) == 6 and command[:3] == ["taskset", "-c", "18"]
                    and command[3].endswith("/"+built["binary_path"])
                    and command[4].endswith("/"+folder+"/request.json")
                    and command[5].endswith("/"+folder+"/result.json"), "pinned numerical command")
            row["environment_threads"] = step.get("environment_threads")
            row["returncode"] = step.get("returncode")
            row["timed_out"] = step.get("timed_out")
            row["owned_group_gone"] = step.get("owned_group_gone")
            if not exists(folder+"/result.json"):
                row["status"] = "native_failure_without_result"
                row["warnings"].append("Saved native attempt produced no JSON result.")
                honest_failures += 1
                require(not stored_attempts[cid].get("eligible_optimistic_result"), "failed attempt not eligible")
                attempts.append(row)
                continue
            result_body = read(folder+"/result.json", step["result_sha256"])
            result = document(result_body)
            require(result.get("id") == req["id"] and result.get("request") == req, "captured request identity")
            if result.get("settings") is not None:
                require(result["settings"] == {
                    "algorithm": req["algorithm"], "convention": "IregiNative",
                    "dimension_shift": req["dimension_shift"], "input_policy": "Preserve",
                    "invariants": "FromShifts", "powers": req["powers"],
                    "propagators": req["n"], "rank": req["rank"], "tensor_weights": "Components"},
                    "captured native settings")
            require(step.get("driver_status") == result.get("status"), "supervised terminal driver status")
            stored = stored_attempts[cid]
            require(stored.get("request") == req and stored.get("status") == result.get("status")
                    and stored.get("result_source") == folder+"/result.json"
                    and stored.get("supervision_source") == folder+"/supervision.json",
                    "per-attempt displayed request/status/raw-source associations")
            for stored_key, result_key in (("engine", "workspace_engine"), ("plan_engine", "plan_engine"),
                                           ("plan_ns", "plan_ns"), ("workspace_ns", "workspace_ns"),
                                           ("first_call_ns", "first_call_ns")):
                require(stored.get(stored_key) == result.get(result_key), "per-attempt route/preparation field")
            row.update(status=result.get("status"), engine=result.get("workspace_engine"),
                       first_diagnostics=result.get("first_diagnostics"),
                       final_diagnostics=result.get("final_diagnostics"))
            for label in ("first_output", "final_output", "failure_output"):
                if label not in result:
                    continue
                checked = array_check(result[label], reference, req)
                checked["capture_field"] = label
                row["array_reports"].append(checked)
                if checked["errors"]:
                    hard_errors.append({"case": ident, "candidate": cid, "capture_field": label,
                                        "errors": checked["errors"]})
                checks += checked["compared_complex_fields"]
                if checked["complete_finite_success"]:
                    array_count += 1
                if checked.get("status") == "honest_guarded_refusal_null_values":
                    refused_arrays += 1
            first = next((a for a in row["array_reports"] if a["capture_field"] == "first_output"), None)
            row["finite_success"] = bool(first and first["complete_finite_success"]
                                         and result.get("all_successful_finite_full_arrays") is True)
            row["timing_captured"] = (result.get("timing_qualified") is True
                                     and step.get("returncode") == 0
                                     and step.get("timed_out") is False
                                     and step.get("owned_group_gone") is True)
            if row["timing_captured"]:
                times = block_statistics(result.get("repeated_measurements"))
                warmups = result.get("warmup_call_ns")
                require(type(warmups) is list and len(warmups) == req["warmup"]
                        and all(type(v) is int and v > 0 for v in warmups), "prespecified warmup observations")
                calibrated = (max(1, min(req["maximum_iterations"],
                                        (req["target_block_ns"]+max(1, warmups[-1])-1)//max(1, warmups[-1])))
                              if req["target_block_ns"] is not None else req["iterations"])
                require(times["calls_per_repeat"] == calibrated, "fixed once-calibrated loop count")
                require(times["repeats"] == req["repeats"]
                        and times["calls_per_repeat"] == result.get("realized_iterations_per_repeat"),
                        "all fixed repeats and calibrated call counts")
                row.update({key: value for key, value in times.items() if key != "outer_mean_us_exact"})
                row["outer_mean_us_exact"] = str(times["outer_mean_us_exact"])
                old_stats = stored_attempts[cid]
                require(all(old_stats.get(key) == times[key] for key in
                            ("repeats", "calls_per_repeat", "total_timed_calls", "maximum_additive_error_us")),
                        "per-attempt repeat counts and exact timing additivity")
                for field, statistics in times["timing"].items():
                    for key in ("mean", "median", "minimum", "maximum", "stdev", "standard_error"):
                        close_numeric(old_stats["timing"][field][key], statistics[key], ident+"/"+cid+"/"+field+"/"+key)
                require(result.get("all_outputs_exactly_reproduced") is True
                        and result.get("input_preserved") is True, "repeatability and input preservation")
                if row["finite_success"]:
                    require(all(a["complete_finite_success"] for a in row["array_reports"]),
                            "all available arrays from successful candidate remain finite/successful")
                else:
                    row["warnings"].append("Refused/failed coefficient output: duration is diagnostic only.")
            else:
                honest_failures += 1
                row["warnings"].append("Native or timing observation did not meet the capture protocol.")
            row["eligible"] = bool(row["timing_captured"] and row["finite_success"]
                                   and first["relative_error_at_most_1e3"])
            require(bool(stored_attempts[cid].get("timing_captured")) == row["timing_captured"]
                    and bool(stored_attempts[cid].get("eligible_optimistic_result")) == row["eligible"],
                    "summary candidate eligibility recomputed independently")
            if first and first["complete_finite_success"]:
                produced_accuracy = stored_attempts[cid]["accuracy"]
                require(produced_accuracy.get("measured") is True
                        and produced_accuracy.get("compared_complex_fields") == first["compared_complex_fields"]
                        and produced_accuracy.get("relative_error_squared_exact") == first["relative_error_squared_exact"]
                        and bool(produced_accuracy.get("relative_error_at_most_1e3")) == first["relative_error_at_most_1e3"]
                        and bool(produced_accuracy.get("relative_error_at_most_1e6")) == first["relative_error_at_most_1e6"],
                        "independent exact E/A and three/six-digit gates")
                require(produced_accuracy.get("reference_source") == reference_name
                        and produced_accuracy.get("reference_sha256") == bindings[reference_name]["sha256"]
                        and produced_accuracy.get("reference_comparison_sha256") == OLD_COMPARISON_SHA,
                        "accuracy display source pins")
                for field, exact in (("relative_error", first["relative_error_squared_exact"]),
                                     ("maximum_componentwise_mixed_error", first["maximum_componentwise_mixed_squared_exact"])):
                    expected = math.sqrt(float(F(exact))) if exact is not None else None
                    actual = produced_accuracy.get(field)
                    require((actual is None and expected is None) or
                            (expected is not None and type(actual) in (int, F, float)
                             and math.isfinite(float(actual))
                             and math.isclose(float(actual), expected, rel_tol=1e-12, abs_tol=1e-300)),
                            "independent displayed accuracy value: "+field)
            attempts.append(row)
        eligible = [a for a in attempts if a["eligible"]]
        timed = [a for a in attempts if a["timing_captured"]]
        finite = [a for a in timed if a["finite_success"] and any(
            v["capture_field"] == "first_output" and v["complete_finite_success"] for v in a["array_reports"])]
        pool = eligible or finite or timed
        chosen = min(pool, key=lambda a: F(a["outer_mean_us_exact"])) if pool else None
        require(item.get("selected_candidate") == (chosen["id"] if chosen else None)
                and bool(item.get("timing_qualified")) == bool(chosen and chosen["eligible"]),
                "fastest exact mean within the predeclared candidate-selection pool")
        require((item.get("selection_warning") is None) == bool(eligible), "diagnostic selection warning")
        if chosen:
            chosen_summary = stored_attempts[chosen["id"]]
            for key in ("timing", "accuracy", "engine", "plan_engine", "plan_ns", "workspace_ns",
                        "first_call_ns", "repeats", "calls_per_repeat", "total_timed_calls",
                        "result_source", "supervision_source", "successful_finite_full_array", "timing_captured"):
                require(item.get(key) == chosen_summary.get(key), "selected row copies verified attempt: "+key)
            require(item.get("algorithm") == chosen["request"]["algorithm"]
                    and item.get("master_policy") == chosen["request"]["master_policy"]
                    and item.get("postconstruction_profiling") == chosen["request"]["postconstruction_profiling"],
                    "selected row method/policy/profile labels")
        output_rows.append({"id": ident, "requested_bits": request["requested_bits"],
                            "selected_candidate": chosen["id"] if chosen else None,
                            "selection_pool": "finite_three_digit" if eligible else "finite_diagnostic" if finite else "timed_refusal" if timed else "unmeasured",
                            "selected_is_usable_three_digit_result": bool(chosen and chosen["eligible"]),
                            "attempts": attempts})
    return {
        "schema_version": 1,
        "status": "passed_independent_saved_binary64_review" if not hard_errors else "failed_independent_saved_binary64_review",
        "passed": not hard_errors, "summary_source": summary_path, "planned_attempts": total_attempts,
        "terminal_attempts": terminal_attempts, "all38_saved_terminal_attempts_present": terminal_attempts == 38,
        "failed_or_incomplete_timing_attempts": honest_failures,
        "honest_guarded_refusal_attempts": sum(any(v.get("capture_field") == "first_output"
            and v.get("status") == "honest_guarded_refusal_null_values" for v in a["array_reports"])
            for r in output_rows for a in r["attempts"]),
        "numerically_noneligible_attempts": sum(not a["eligible"] for r in output_rows for a in r["attempts"]),
        "successful_finite_arrays_independently_compared": array_count,
        "honest_refused_array_payloads": refused_arrays,
        "independently_compared_complex_fields": checks,
        "independently_compared_real_components": 2*checks,
        "three_digit_selected_rows": sum(r["selected_is_usable_three_digit_result"] for r in output_rows),
        "rows": output_rows, "hard_errors": hard_errors, "input_bindings": bindings,
        "precision_check": "All actual candidate input/output domains f64 at53 significant bits; only ordinaryN5R5/N5R6/N6R6 request39. Accuracy39 is a heuristic2^-20 admission target, not an achieved1e-6 certificate.",
        "relative_error_formula": "sqrt(max_j |a_j-b_j|²/mu^(2d_j) / max_j |b_j|²/mu^(2d_j)), d_j=degree_j+4+2h-2sum(powers). Gates use exact Fraction squared comparison.",
        "reference_scope": "Previous finite-precision full tensor arrays, independently admitted against originalIBP in the prior8968-field report; no exact-integral or arbitrary-kinematics claim.",
        "timing_scope": "Same-call outer minus aggregated nested master wall time; preparation/first call/warmup/checks/serialization/result destruction excluded. Exact raw-call additivity, equal-count block means and descriptive SE independently checked.",
        "selection_scope": "Fastest mean within fixed38 measured public candidate attempts, with finite complete E/A<=1e-3 eligibility; no universal fastest or controlled-host performance claim.",
        "environment_scope": "Saved taskset command and CPU18 metadata checked per candidate; recorded thread settings retained, no new process-affinity probe.",
        "live_source_guards_rehashed": verify_live_source,
        "live_frozen_binary_rehashed": verify_live_binary,
        "source_binary_association_scope": "Original saved build/source/binary/request hashes and unchanged guard flags checked. Driver source body freshly hash-matched for static f64/no-rescue inspection; optional flags separately check the entire current source list or frozen binary.",
        "native_or_integral_execution": False, "producer_imports": False,
        "fresh_process_or_environment_probe": False,
        "raw_history_preservation_publication_audit": "Separate publication audit; this replay reads old inputs/reference arrays and never writes them.",
    }


def serializable(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serializable(item) for item in value]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", default=HERE+"/tirust-summary.json",
                        help="Project-relative initial38 snapshot; supplements are audited separately")
    parser.add_argument("--verify-live-source", action="store_true")
    parser.add_argument("--verify-live-binary", action="store_true")
    args = parser.parse_args()
    root = Path.cwd().resolve()
    require((root/"Cargo.toml").is_file(), "run from project root")

    def location(name):
        path = (root/safe(name)).resolve()
        require(path.is_relative_to(root), "data path escaped project")
        return path

    try:
        result = audit(lambda name: location(name).read_bytes(), lambda name: location(name).is_file(),
                       summary_path=args.summary, verify_live_source=args.verify_live_source,
                       verify_live_binary=args.verify_live_binary)
    except (ValueError, KeyError, IndexError, TypeError, OSError, OverflowError) as error:
        result = {"schema_version": 1, "status": "failed_independent_saved_binary64_review",
                  "passed": False, "error": str(error), "native_or_integral_execution": False}
    result["checker_sha256"] = sha(Path(__file__).read_bytes())
    body = json.dumps(serializable(result), indent=2)+"\n"
    location(HERE+"/independent-review.json").write_text(body)
    qualification = {key: result[key] for key in (
        "schema_version", "status", "passed", "summary_source", "planned_attempts", "terminal_attempts",
        "all38_saved_terminal_attempts_present", "failed_or_incomplete_timing_attempts",
        "honest_guarded_refusal_attempts", "numerically_noneligible_attempts",
        "successful_finite_arrays_independently_compared", "honest_refused_array_payloads",
        "independently_compared_complex_fields", "independently_compared_real_components",
        "three_digit_selected_rows", "precision_check", "reference_scope", "timing_scope",
        "selection_scope", "environment_scope", "live_source_guards_rehashed",
        "live_frozen_binary_rehashed", "native_or_integral_execution", "producer_imports",
        "checker_sha256", "error") if key in result}
    qualification["independent_review_sha256"] = sha(body.encode())
    location(HERE+"/qualification.json").write_text(json.dumps(qualification, indent=2)+"\n")
    print(json.dumps(qualification))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

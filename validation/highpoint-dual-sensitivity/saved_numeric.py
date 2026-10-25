"""Portable checks of the saved private full-component N6 correctness cohort.

The caller supplies immutable file bytes.  This module has no filesystem reads,
producer imports, native dependencies, process inspection, or numerical engine.
All arithmetic is exact numeric comparison of retained fixtures, not Taylor or
polynomial algebra.  The fixed dilation tables originate in the independent
source-math review retained by validation/exact-master-variant-cache.  The scope
and coverage follow the reviewed comparator 22f7eefa...; that source is retained
and bound as provenance, never imported or executed here.
"""

from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
import math


PREFIX = "target/highpoint-dual-sensitivity/numerical-v1"
HISTORICAL_ROOT = "/shared/external/iregi/iregi-rust/"
FIXTURE = "validation/public-highpoint/fixture-conditioned_masses.json"
REFERENCE = "validation/public-highpoint/reference-conditioned_masses.json"
UNIT = "target/routing-rational-full-core/first-001/n6_unit-candidate.json"
DOT = "target/routing-rational-full-core/remaining-001/n6_dot0-candidate.json"
DOT_REFERENCE = "target/routing-rational-full-core/remaining-001/n6_dot0-reference.json"
DOT_AUDIT = "target/resume-20261025-review/routing-v3-dot0-independent-saved-numeric-audit.json"
MATH_REVIEW = "target/public-highpoint/numeric-types-dual/design/dilation-math-source-review.json"
PINS = {
    PREFIX + "/compare_saved.py": "22f7eefa045be9481e280c91071e4b62eabec92122d386a7416ff851fed10e24",
    PREFIX + "/source-v2.json": "dfd61c594979b41057d3ef745eab60cf96ffb5b86fbd1c8aa97828da673ca045",
    PREFIX + "/base-helpers/jet_inputs.rs": "7b35954da337f1bb2191faa5ae05cec7e7f2ce1d6f4b88e90a64b104b350041f",
    FIXTURE: "ec27f2c5774a18d3d84d2d733e634dae93e9bd4c74523d6f77e8784d13421ada",
    REFERENCE: "9bc3f10ad27615f23ddb3c2f62169575378d32e6c35c9d2a9dd51223f9b39ec4",
    UNIT: "6de57488f24af1fed40a7b9367812158943e0edd074f227cf684faabbfe7440e",
    DOT: "2a542526eacb57bc240c56f23a8b0c53abf8faeb613a4ab8b00079ba3cab28eb",
    DOT_REFERENCE: "774db2dc463925a5b2efd64f5e97e94f3bb83d06528f2ac2faa1223961c7f7f6",
    DOT_AUDIT: "ff6fb105c2526a39076c9571ffbd92a51fbb8480bae51bd24231e8d3e4a12182",
    MATH_REVIEW: "14da099580d7bd5e53f4fba3dcbf6221f365c017160189615b2ea3430d3fe7ae",
}
DOMAINS = {"Float128Mass0": (128, 2, False, 260),
           "Float256Mass0": (256, 2, False, 260),
           "Float128Scale": (128, 6, True, 550),
           "Float256Scale": (256, 6, True, 550)}
SHAPE = [[0, 0], [1, 0], [0, 1], [2, 0], [1, 1], [0, 2]]
MASS_SHAPE = [[0], [1]]
SCALE_SCHEDULE = [("singleton_affine", [0]), ("mixed", [0, 3, 1, 2, 0]),
                  ("reordered", [2, 1, 0, 3, 0]), ("empty", []), ("singleton_again", [0])]
MASS_SCHEDULE = [("singleton_mass0", [0]), ("mixed_mass0_invalid", [0, 1, 0]), ("empty", [])]
SETTINGS = dict(propagators=6, rank=0, powers=[1] * 6, dimension_shift=0,
                algorithm="PassarinoVeltman", convention="IregiNative",
                tensor_weights="Components", invariants="FromShifts", input_policy="Preserve")
OPERAND = {"rational", "precision", "negative_sign", "finite"}
ROUTES = {"Ordinary", "Analytic", "Hybrid", "CertifiedPlanar", "AutomaticPlanar", "CertifiedScalar"}
EXECUTION = {"input_rows", "argument_rows", "master_family_batches", "master_rows",
             "pentagon_box_rows", "reduction_rows", "fallback_rows", "fallback_successes", "analytic_rows"}
CERTIFICATES = {"input_rows", "evaluated_rows", "passes", "reduction_batches"}
PACKING = {"parent_input_rows", "child_batch_calls", "packed_child_rows", "parent_batch_calls", "packed_parent_rows"}


def _require(value, message):
    if not value:
        raise ValueError("saved component numeric: " + message)


def _json(raw, parse_float=float):
    def pairs(items):
        result = {}
        for name, value in items:
            _require(name not in result, "duplicate JSON key " + name)
            result[name] = value
        return result
    def invalid(value):
        raise ValueError("saved component numeric: nonfinite JSON constant " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid, parse_float=parse_float)


def _number(value):
    _require(isinstance(value, dict) and set(value) == OPERAND, "native operand field inventory")
    _require(value["finite"] is True and isinstance(value["rational"], str), "nonfinite/native rational")
    result = F(value["rational"])
    bits, sign = value["precision"], value["negative_sign"]
    _require(type(bits) is int and bits >= 0 and (result == 0 or bits > 0), "native precision")
    _require(type(sign) is bool and (result == 0 or sign == (result < 0)), "native sign")
    return result


def _z(value):
    _require(isinstance(value, list) and len(value) == 2, "complex operand width")
    return tuple(_number(part) for part in value)


def _array(values, count):
    _require(isinstance(values, list) and len(values) == count, "complex array width")
    return [_z(value) for value in values]


def _error_text(squared):
    with localcontext() as context:
        context.prec = 220
        return str((Decimal(squared.numerator) / Decimal(squared.denominator)).sqrt())


def _compare(comparisons, actual, expected, target, scale, tolerance=F(1, 10**10), **location):
    squared = sum((a - b)**2 for a, b in zip(actual, expected)) / max(scale**2, sum(x*x for x in expected))
    entry = dict(target=target, **location, actual=list(map(str, actual)), expected=list(map(str, expected)),
                 natural_scale=str(scale), normalized_error=_error_text(squared),
                 tolerance=str(tolerance), within_tolerance=squared <= tolerance**2)
    comparisons.append(entry)
    _require(entry["within_tolerance"], "complex numerical tolerance: " + str(location))


def _differences(actual, previous, components, **location):
    _require(len(actual) == len(previous) == 4 * components, "representation comparison width")
    result = []
    for index, (a, b) in enumerate(zip(actual, previous)):
        _z(a); _z(b)
        for part, (x, y) in enumerate(zip(a, b)):
            if x != y:
                result.append(dict(**location, laurent_slot=index // components, component=index % components,
                    part="real" if part == 0 else "imaginary", same_exact_value=_number(x) == _number(y),
                    same_rational_text=x["rational"] == y["rational"], same_precision=x["precision"] == y["precision"],
                    same_sign_bit=x["negative_sign"] == y["negative_sign"], current=x, previous=y))
    return result


def _base(fixture):
    sample = fixture["samples"][0]
    props = sample["propagators"][:6]
    _require(sample["id"] == "base" and len(props) == 6 and all(p["power"] == 1 for p in props), "fixed fixture")
    _require(all(len(p["shift"]) == 4 and len(p["mass_squared"]) == 2 and F(p["mass_squared"][1]) == 0 for p in props), "real fixture routing/masses")
    result = [F(x) for p in props for x in p["shift"]] + [F(p["mass_squared"][0]) for p in props] + [F(sample["mu"])]
    _require(len(result) == 31, "31 fixed parameters")
    return result


def _tables():
    # Independently reviewed fixed numeric fixture coefficients. Symbolica made
    # the original input jets and response multipliers; no AD is performed here.
    a, b = F(1152921504606846977, 1152921504606846976), F(3, 2)
    linear = [[1, a, b, 0, 0, 0], [1, a, b, 0, a*b, 0], [1, 0, 0, 0, 0, 0]]
    square = [[1, 2*a, 2*b, a*a, 2*a*b, b*b], [1, 2*a, 2*b, a*a, 4*a*b, b*b], [1, 0, 0, 0, 0, 0]]
    response = [[1, -8*a, -8*b, 36*a*a, 72*a*b, 36*b*b],
                [1, -8*a, -8*b, 36*a*a, 64*a*b, 36*b*b], [1, 0, 0, 0, 0, 0]]
    return linear, square, response


def _inputs(record, base, scale_mode, components):
    rows = record["represented_input_rows"]
    _require(isinstance(rows, list) and len(rows) == (4 if scale_mode else 2), "input profile inventory")
    decoded = [_array(row, 31 * components) for row in rows]
    if scale_mode:
        linear, square, response = _tables()
        _require(record["profiles"] == ["affine", "product", "constant", "invalid_mu_zero"], "scale profile order")
        multipliers = record["exact_homogeneity_multipliers"]
        _require(isinstance(multipliers, list) and len(multipliers) == 3
                 and all(isinstance(row, list) and len(row) == 6 and all(isinstance(v, str) for v in row) for row in multipliers), "exact multiplier inventory")
        _require([list(map(F, row)) for row in multipliers] == response, "reviewed exact homogeneity targets")
        for profile in range(3):
            for parameter, primal in enumerate(base):
                coefficients = square[profile] if 24 <= parameter < 30 else linear[profile]
                _require(decoded[profile][parameter * components:(parameter + 1) * components]
                         == [(primal * coefficient, F(0)) for coefficient in coefficients], "reviewed beyond-53-bit input jet")
        _require(decoded[3][:30 * components] == decoded[0][:30 * components]
                 and all(z == (0, 0) for z in decoded[3][30 * components:]), "invalid scale mu control")
        return response
    expected = []
    for parameter, primal in enumerate(base):
        expected.extend([(primal, F(0)), (F(parameter == 24), F(0))])
    invalid = list(expected); invalid[60] = (F(0), F(0))
    _require(decoded == [expected, invalid], "independent mass0 seed and invalid control")
    _require(record["derivative_identity"] == "d/dm0_squared I6 = + I6(powers=[2,1,1,1,1,1]); fixed routing, other masses andmu; Taylor factorial1", "mass derivative sign/factorial")
    return None


def _metadata(shape):
    return dict(convention="IregiNative", tensor_weights="Components", dual_shape=shape)


def _context(lane, bits, components, shape):
    context = lane["component_context"]
    _require(isinstance(context, dict), "component context missing")
    raw = context["raw_context"]
    _require(isinstance(raw, dict) and set(raw) == {"envelope_error", "envelope"}, "raw component envelope missing")
    if lane["status"] != "Success":
        _require(lane["values"] is None and context["status"] == "unavailable_for_failed_lane"
                 and raw == {"envelope_error": None, "envelope": None}, "failed lane retained context or values")
        return dict(status=lane["status"], context_status=context["status"], raw_context=raw)
    values = lane["values"]; _array(values, 4 * components)
    _require(context["status"] == "validated_complete_component_context" and raw["envelope_error"] is None
             and isinstance(raw["envelope"], dict), "successful context rejected/missing")
    envelope = raw["envelope"]
    keys = ["working_precision", "accuracy_bits", "components", "basis", "metadata", "route_history",
            "output_components", "component_amplitudes", "primal_operands"]
    _require(all(envelope[key] == context[key] for key in keys), "raw/validated context mismatch")
    for view in [envelope, context]:
        _require(view["working_precision"] == bits and view["accuracy_bits"] == 53 and view["components"] == components
                 and view["basis"] == [[0, 0, 0, 0]] and view["metadata"] == _metadata(shape), "context interpretation")
        routes = view["route_history"]
        _require(isinstance(routes, list) and routes and all(route in ROUTES for route in routes), "actual route history")
        _require(view["output_components"] == values, "complete value/precision/signed-zero snapshot")
        _require(all(real >= 0 and imaginary == 0 for real, imaginary in _array(view["component_amplitudes"], 4 * components)), "nonnegative full-component amplitudes")
        operands = view["primal_operands"]
        _require(isinstance(operands, list) and len(operands) == 4, "primal operand inventory")
        for index, operand in enumerate(operands):
            _require(isinstance(operand, dict) and set(operand) == {"output_index", "kind", "amplitude"}
                     and operand["output_index"] == index and operand["kind"] in {"UncancelledMasters", "NoMaster"}, "primal operand map")
            real, imaginary = _array(operand["amplitude"], 1)[0]
            _require(real >= 0 and imaginary == 0, "primal amplitude")
    _require(envelope["output_primals"] == [values[index * components] for index in range(4)]
             and context["snapshot_matches_all_values_precisions_and_signs"] is True, "complete primal/native snapshot")
    return dict(status="checked_complete_component_context", route_history=envelope["route_history"], complex_components=4 * components)


def _work(call, indices, invalid, successes):
    work = call["execution"]
    names = {"child_execution", "parent_execution", "child_certificate_execution", "parent_certificate_execution"}
    _require(set(work) == PACKING | names and all(type(work[k]) is int and work[k] >= 0 for k in PACKING), "work field inventory")
    for name in ["child_execution", "parent_execution"]:
        _require(set(work[name]) == EXECUTION and all(type(v) is int and v >= 0 for v in work[name].values()), "execution counters")
    for name in ["child_certificate_execution", "parent_certificate_execution"]:
        value = work[name]
        _require(set(value) == CERTIFICATES and all(type(v) is int and v >= 0 for v in value.values()), "certificate counters")
        _require(value["passes"] <= value["evaluated_rows"] and value["reduction_batches"] <= value["input_rows"]
                 and (value["input_rows"] != 0 or not any(value.values())), "certificate counter consistency")
    active = sum(profile != invalid for profile in indices)
    child, parent = work["child_execution"], work["parent_execution"]
    packed = work["packed_parent_rows"]
    _require(work["parent_input_rows"] == len(indices) and work["child_batch_calls"] == int(active > 0)
             and work["packed_child_rows"] == child["input_rows"] == 6 * active, "one batched child call/invalid exclusion")
    _require(successes <= packed <= active and work["parent_batch_calls"] == int(packed > 0)
             and parent["input_rows"] == packed and parent["reduction_rows"] <= packed, "packed parent counters")
    _require(not any(parent[k] for k in EXECUTION - {"input_rows", "argument_rows", "reduction_rows"})
             and not any(work["parent_certificate_execution"].values()), "parent unaccounted masters/rerouting")
    _require(work["child_certificate_execution"]["input_rows"] <= child["fallback_rows"], "child certificate attribution")
    if successes == active:
        _require(parent["argument_rows"] == packed and child["argument_rows"] >= 6 * active, "successful row counter attribution")
    if not indices:
        _require(not any(work[k] for k in PACKING) and all(not any(work[k].values()) for k in names)
                 and call["diagnostics"] == [], "empty call stale work")


def _children(call, indices, invalid, bits, components, shape):
    active = [row for row, profile in enumerate(indices) if profile != invalid]
    child = call["child_component_observation"]
    if not active:
        _require(child is None, "empty call stale child context")
        return []
    _require(isinstance(child, dict) and child["status"] == "captured_actual_child_result_before_parent_import"
             and child["rows"] == 6 * len(active) and child["components"] == components
             and child["working_bits"] == bits and child["requested_bits"] == 53
             and child["basis"] == [[0, 0, 0, 0]], "child captured layout")
    lanes = child["lanes"]
    _require(isinstance(lanes, list) and len(lanes) == 6 * len(active), "complete child rows")
    summaries = []
    for row, lane in enumerate(lanes):
        _require(lane["row"] == row and lane["status"] == "Success"
                 and all(type(lane[k]) is bool for k in ["fallback_used", "analytic_used"]), "child lane identity/status")
        summary = _context(lane, bits, components, shape)
        summary.update(child_row=row, subset=row // len(active), parent_row=active[row % len(active)])
        summaries.append(summary)
    for compact, parent_row in enumerate(active):
        for flag in ["fallback_used", "analytic_used"]:
            _require(call["lanes"][parent_row][flag] == any(lanes[subset * len(active) + compact][flag] for subset in range(6)), "actual parent/child route flags")
    return summaries


def _targets(data, name, base, powers):
    record = data[name]
    _require(record["status"] == "all_lanes_success" and record["algorithm_used"] == "Ibp"
             and record["settings"] == dict(SETTINGS, algorithm="Ibp", powers=powers)
             and record["basis"] == [[0, 0, 0, 0]] and len(record["precision_runs"]) == 2, "independent generic target")
    targets = {}
    for run in record["precision_runs"]:
        bits = run["working_bits"]
        _require(bits in [128, 256] and bits not in targets and run["requested_bits"] == 53
                 and run["workspace_bits"] == bits and run["master_policy"] == "Symbolica", "target precision/domain")
        found = []
        for batch in run["batches"]:
            _require(len(batch["lanes"]) == len(batch["statuses"]) == len(batch["input_exact_rational"]), "target lane ledger")
            for row, (lane, raw_input) in enumerate(zip(batch["lanes"], batch["input_exact_rational"])):
                _require(lane["row"] == row and lane["status"] == batch["statuses"][row] == "Success"
                         and len(lane["slots"]) == 4, "target successful Laurent array")
                decoded = []
                for slot in lane["slots"]:
                    _require(set(slot) == {"real", "imaginary", "real_precision", "imaginary_precision", "real_sign_negative", "imaginary_sign_negative"}, "target native operand inventory")
                    decoded.append(tuple(_number(dict(rational=slot[part], precision=slot[part + "_precision"],
                        negative_sign=slot[part + "_sign_negative"], finite=True)) for part in ["real", "imaginary"]))
                if raw_input["sample_index"] == 0:
                    _require(raw_input["sample_id"] == "n6_base" and [[F(v) for v in z] for z in raw_input["values"]]
                             == [[v, F(0)] for v in base], "target fixed31 primals")
                    found.append(decoded)
        _require(found and all(slots == found[0] for slots in found) and all(z == (0, 0) for z in found[0][:3]), "target repetition/pole zeros")
        targets[bits] = found[0]
    return targets


def _original_targets(data):
    reference = data[REFERENCE]
    cases = [case for case in reference["cases"] if case["id"] == "n6_base_mode0"]
    _require(reference["status"] == "complete" and len(cases) == 1, "untouched original reference")
    case = cases[0]; response = case["response"]
    _require(case["status"] == "captured" and case["exit_code"] == 0 and response["stable"] is True
             and response["poles"] == ["uv1", "ir1", "ir2", "finite"] and len(response["moments"]) == 330, "original unit stable/full")
    _require([_json(line[7:], parse_float=str) for line in case["stdout"].splitlines() if line.startswith("RESULT ")]
             == [response], "original unit raw stdout")
    unit = [tuple(map(F, z)) for z in response["moments"][0]]
    raw_dot = data[DOT_REFERENCE]
    parsed = [_json(line[7:], parse_float=str) for line in raw_dot["stdout"].splitlines() if line.startswith("RESULT ")]
    _require(raw_dot["exit_code"] == 0 and parsed == raw_dot["responses"], "original dotted raw stdout")
    dots = []
    for name in ["n6_dot0_n6_base_general", "n6_dot0_n6_base_scalar"]:
        matches = [item for item in parsed if item["id"] == name]
        _require(len(matches) == 1 and matches[0]["stable"] is True and matches[0]["poles"] == ["uv1", "ir1", "ir2", "finite"]
                 and len(matches[0]["moments"]) == 1 and len(matches[0]["moments"][0]) == 4, "original general/scalar dotted target")
        dots.append([tuple(map(F, z)) for z in matches[0]["moments"][0]])
    _require(len(unit) == 4 and all(len(z) == 2 for z in unit + dots[0] + dots[1]), "original complex widths")
    return unit, dots


def _domain(domain, record, base, unit, dot, original_unit, original_dot):
    bits, components, scale_mode, child_limit = DOMAINS[domain]
    shape, schedule, invalid = (SHAPE, SCALE_SCHEDULE, 3) if scale_mode else (MASS_SHAPE, MASS_SCHEDULE, 1)
    _require(record["schema_version"] == 1 and record["domain"] == "Float" + str(bits)
             and record["working_bits"] == bits and record["requested_bits"] == 53 and record["settings"] == SETTINGS
             and record["fixture"] in [FIXTURE, HISTORICAL_ROOT + FIXTURE] and record["components"] == components
             and record["ordered_shape"] == shape and record["basis"] == [[0, 0, 0, 0]], "capture domain/context")
    _require(record["mode"] == ("dynamic_mixed_second_dual" if scale_mode else "independent_first_squared_mass0_dual"), "capture mode")
    if scale_mode:
        _require(record["interface"] == "private exact-qualified ThinSix; capture-only helper module", "scale interface")
    multipliers = _inputs(record, base, scale_mode, components)
    calls = record["calls"]; _require(isinstance(calls, list) and len(calls) == len(schedule), "complete fixed calls")
    comparisons, contexts, outcomes, differences = [], [], [], []
    baselines, flags = {}, {}
    successes = invalids = child_rows = slots = rejected = available = 0
    for call_index, (call, (name, indices)) in enumerate(zip(calls, schedule)):
        loc = dict(call_index=call_index, call=name)
        _require(call["name"] == name and call["profile_indices"] == indices and call["status"] == "captured"
                 and call["input_preserved_exactly"] is True and call["components"] == components
                 and call["metadata"] == _metadata(shape), "captured call identity/layout")
        if scale_mode:
            _require(call["basis"] == [[0, 0, 0, 0]], "scale call basis")
        diagnostics = call["diagnostics"]
        _require(isinstance(diagnostics, list) and len(diagnostics) == len(indices)
                 and all(isinstance(row, list) and all(isinstance(note, str) for note in row) for row in diagnostics), "complete diagnostics")
        _require(isinstance(call["lanes"], list) and len(call["lanes"]) == len(indices), "complete parent rows")
        call_successes = 0
        for row, (profile, lane) in enumerate(zip(indices, call["lanes"])):
            lane_loc = dict(**loc, row=row, profile=profile)
            _require(lane["row"] == row and lane["profile"] == profile and all(type(lane[k]) is bool for k in ["fallback_used", "analytic_used"]), "parent lane identity/flags")
            values = lane["values"]
            available += int(values is not None); rejected += int(values is None)
            outcomes.append(dict(**lane_loc, status=lane["status"], values_available=values is not None,
                                 component_context_status=lane["component_context"]["status"]))
            context = _context(lane, bits, components, shape)
            contexts.append(dict(**lane_loc, level="parent", **context))
            if profile == invalid:
                _require(isinstance(lane["status"], str) and lane["status"].startswith("InvalidInput(") and values is None
                         and not lane["fallback_used"] and not lane["analytic_used"] and diagnostics[row] == [], "invalid lane null/failure policy")
                invalids += 1
                continue
            _require(lane["status"] == "Success" and values is not None, "positive parent unavailable")
            decoded = _array(values, 4 * components)
            call_successes += 1; successes += 1; slots += len(decoded)
            route_flags = lane["fallback_used"], lane["analytic_used"]
            _require(profile not in flags or flags[profile] == route_flags, "same-profile route flags")
            flags.setdefault(profile, route_flags)
            previous = baselines.setdefault(profile, values)
            differences.extend(_differences(values, previous, components, **lane_loc))
            for index, actual in enumerate(decoded):
                pole, component = divmod(index, components)
                sloc = dict(**lane_loc, laurent_slot=pole, component=component, multi_index=shape[component])
                _require(pole == 3 or actual == (0, 0), "exact pole Taylor zero")
                scale = F(1, 256) if scale_mode or component == 0 else F(1, 1024)
                if scale_mode:
                    expected = tuple(multipliers[profile][component] * x for x in unit[bits][pole])
                    _compare(comparisons, actual, expected, "generic_IBP_unit_times_Symbolica_homogeneity", scale, **sloc)
                    _require(profile != 2 or component == 0 or actual == (0, 0), "exact constant-profile derivative zero")
                else:
                    _compare(comparisons, actual, (unit if component == 0 else dot)[bits][pole],
                             "generic_IBP_unit" if component == 0 else "independent_generic_IBP_dot0", scale, **sloc)
                    if component == 1:
                        for refindex, reference in enumerate(original_dot):
                            _compare(comparisons, actual, reference[pole], "original_IREGI_dot0_" + ("general" if refindex == 0 else "scalar"), scale, **sloc)
                if component == 0:
                    _compare(comparisons, actual, original_unit[pole], "untouched_original_IBP_primal", scale, **sloc)
                _compare(comparisons, actual, _z(previous[index]), "same_profile_first_available", scale, **sloc)
        _work(call, indices, invalid, call_successes)
        children = _children(call, indices, invalid, bits, components, shape)
        child_rows += len(children)
        contexts.extend(dict(**loc, level="child", **child) for child in children)
        guard = call["sidecar_guard_probes"]
        if call_successes:
            _require(isinstance(guard, dict) and guard["status"] == "passed" and guard["failures"] == []
                     and guard["all_output_components_probed"] == 4 * components and guard["checks"] == 16 * components + 4
                     and guard["original_values_precisions_signs_preserved"] is True, "complete owned-clone mutation probes")
        else:
            _require(guard is None, "empty call stale guard")
    expected_successes, expected_invalids = (10, 2) if scale_mode else (3, 1)
    _require(successes == expected_successes and invalids == expected_invalids and slots == 4 * components * expected_successes
             and child_rows == 6 * expected_successes, "complete parent/child coverage")
    _require(record["status"] == "capture_complete_not_yet_qualified" and record["active_call"] == schedule[-1][0]
             and record["successful_lanes"] == available and record["unexpected_outcomes"] == []
             and record["intended_successes_available"] is True and record["expected_invalid_rejections_confirmed"] is True, "complete capture ledger")
    if scale_mode:
        _require(record["rejected_lanes"] == rejected, "rejected parent ledger")
    elapsed = record["elapsed_seconds"]
    _require(type(elapsed) in [int, float] and math.isfinite(elapsed) and 0 <= elapsed <= child_limit, "saved correctness alarm bound")
    coverage = dict(calls=len(calls), expected_calls=len(schedule), successful_lanes=successes,
        expected_successes=expected_successes, invalid_rejections=invalids, expected_invalid_rejections=expected_invalids,
        complex_output_slots=slots, expected_complex_output_slots=4 * components * expected_successes,
        child_rows=child_rows, expected_child_rows=6 * expected_successes, empty_calls=sum(not call["profile_indices"] for call in calls))
    _require(coverage["empty_calls"] == 1, "one empty call")
    return dict(comparisons=comparisons, context_summaries=contexts, preserved_outcomes=outcomes,
                repeated_representation_differences=differences, coverage=coverage)


def check_saved(files, borrowed):
    """Validate retained bytes only; raise ValueError on any missing/failing gate.

    Both arguments map original repository-relative paths to bytes.  The parent
    capsule checker owns safe archive loading, exact source reconstruction,
    historical artifact/lifecycle attestations, and independent-audit admission.
    """
    _require(isinstance(files, dict) and isinstance(borrowed, dict), "explicit file byte maps required")
    def raw(name):
        if name in files and name in borrowed:
            _require(files[name] == borrowed[name], "conflicting borrowed file " + name)
        body = files[name] if name in files else borrowed[name]
        _require(isinstance(body, bytes), "file is not bytes " + name)
        return body
    def load(name):
        return _json(raw(name))
    for name, expected in PINS.items():
        _require(hashlib.sha256(raw(name)).hexdigest() == expected, "anchor changed " + name)
    math_review = load(MATH_REVIEW)
    _require(math_review["source_math_review_passed"] is True and math_review["findings"] == [], "independent fixed-coefficient source-math review")
    data = {name: load(name) for name in [FIXTURE, REFERENCE, UNIT, DOT, DOT_REFERENCE, DOT_AUDIT]}
    _require(data[DOT_AUDIT]["status"] == "passed-independent-routing-v3-dot0-saved-numerical-audit", "independent dotted anchor audit")
    base = _base(data[FIXTURE])
    unit, dot = _targets(data, UNIT, base, [1] * 6), _targets(data, DOT, base, [2, 1, 1, 1, 1, 1])
    original_unit, original_dot = _original_targets(data)
    records = {domain: load(PREFIX + "/runtime-" + domain + "-001/result.json") for domain in DOMAINS}
    saved = load(PREFIX + "/saved-gate-001/comparison.json")
    summary = load(PREFIX + "/qualification-summary.json")
    _require(saved["status"] == "passed_saved_numerical_gates_only" and saved["passed"] is True
             and saved["precision_convergence_qualified"] is True and saved["failures"] == []
             and saved["anchor_errors"] == [] and saved["saved_read_errors"] == [] and set(saved["domain_reports"]) == set(DOMAINS), "saved paired gate admission")
    domains, target_max = {}, {}
    for domain, record in records.items():
        result = _domain(domain, record, base, unit, dot, original_unit, original_dot)
        prior = saved["domain_reports"][domain]
        _require(prior["passed"] is True and prior["status"] == "passed_saved_numerical_gates_only"
                 and prior["failures"] == prior["anchor_errors"] == [] and prior["captured_record"] == record, "saved full capture/domain gate " + domain)
        for key, value in result.items():
            _require(prior[key] == value, "recomputed domain " + key + " differs: " + domain)
        maximum = {}
        for entry in result["comparisons"]:
            target = entry["target"]
            maximum[target] = max(maximum.get(target, Decimal(0)), Decimal(entry["normalized_error"]))
        target_max[domain] = {target: str(error) for target, error in maximum.items()}
        _require(summary["domains"][domain]["passed"] is True and summary["domains"][domain]["coverage"] == result["coverage"]
                 and summary["domains"][domain]["target_max_normalized_error"] == target_max[domain], "saved domain summary " + domain)
        domains[domain] = result
    paired, differences, input_differences = [], [], []
    for suffix in ["Mass0", "Scale"]:
        low, high = records["Float128" + suffix], records["Float256" + suffix]
        components, shape, schedule, invalid = (6, SHAPE, SCALE_SCHEDULE, 3) if suffix == "Scale" else (2, MASS_SHAPE, MASS_SCHEDULE, 1)
        for profile, (a, b) in enumerate(zip(low["represented_input_rows"], high["represented_input_rows"])):
            _require(_array(a, 31 * components) == _array(b, 31 * components), "paired exact represented input seeds")
            for index, (x, y) in enumerate(zip(a, b)):
                if x != y:
                    input_differences.append(dict(kind=suffix, profile=profile, parameter=index // components, component=index % components, low=x, high=y))
        for call_index, (name, indices) in enumerate(schedule):
            a, b = low["calls"][call_index], high["calls"][call_index]
            for row, profile in enumerate(indices):
                if profile == invalid:
                    continue
                loc = dict(kind=suffix, call=name, row=row, profile=profile)
                x, y = a["lanes"][row]["values"], b["lanes"][row]["values"]
                differences.extend(_differences(x, y, components, **loc))
                for index, (actual, expected) in enumerate(zip(_array(x, 4 * components), _array(y, 4 * components))):
                    pole, component = divmod(index, components)
                    scale = F(1, 1024) if suffix == "Mass0" and component == 1 else F(1, 256)
                    _compare(paired, actual, expected, "Float128_vs_Float256", scale, F(1, 2**80),
                             **loc, laurent_slot=pole, component=component, multi_index=shape[component])
    _require(len(paired) == 264 and saved["comparisons"] == paired and saved["paired_representation_differences"] == differences
             and saved["input_representation_differences"] == input_differences, "complete saved precision comparison/metadata")
    parent_slots = sum(result["coverage"]["complex_output_slots"] for result in domains.values())
    child_rows = sum(result["coverage"]["child_rows"] for result in domains.values())
    paired_max = str(max(Decimal(entry["normalized_error"]) for entry in paired))
    _require(parent_slots == summary["parent_complex_laurent_taylor_slots"] == 528
             and child_rows == summary["child_rows"] == 156 and summary["paired_complex_components"] == 264
             and summary["paired_max_normalized_error"] == paired_max, "complete summary counts/precision maximum")
    for record in [saved] + list(saved["domain_reports"].values()):
        _require(all(record[name] is False for name in ["public_dual_qualified", "derivative_uncertainty_transport_qualified",
                 "performance_qualified", "runtime_provenance_checked"]), "saved numerical-only scope promoted")
    return dict(status="passed_portable_saved_full_component_numerical_check", domains=4,
                parent_complex_laurent_taylor_slots=parent_slots, child_rows=child_rows,
                paired_complex_components=len(paired), target_max_normalized_error=target_max,
                paired_max_normalized_error=paired_max, exact_anchor_files_checked=len(PINS),
                domain_comparisons=sum(len(result["comparisons"]) for result in domains.values()),
                saved_native_build_or_runtime_requalification=False, no_filesystem_or_producer_imports=True,
                no_integral_or_benchmark_executed=True, public_dual_qualified=False,
                derivative_uncertainty_transport_qualified=False, performance_qualified=False)

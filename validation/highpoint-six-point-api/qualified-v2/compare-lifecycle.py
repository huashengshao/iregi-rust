#!/usr/bin/env python3
"""Saved-data gate for the isolated public six-point lifecycle/contraction driver.

The reviewed harness validates the actual frozen build/run/prerequisite schema.
This module does no compiler, subprocess, Symbolica, master or oracle work.
Only the eleven-call Float128/request53 schedule can qualify here.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys

R = Path(__file__).resolve().parents[4]
H = Path(__file__).resolve().parent
PARENT = H.parent
CAPTURE = H / "lifecycle-001"
FIXTURE = R / "validation/public-highpoint/fixture-conditioned_masses.json"
REFERENCE = R / "validation/public-highpoint/reference-conditioned_masses.json"
SHARED = R / "validation/public-highpoint/compare_public.py"
HISTORY = R / "validation/public-highpoint/qualification.json"
REFERENCE_EXE = R / "target/reference/iregi-reference-original"
HISTORICAL_COMPARATOR = R / "target/public-highpoint/thin-n6-mask/compare-lifecycle.py"
PINS = {
    FIXTURE: "ec27f2c5774a18d3d84d2d733e634dae93e9bd4c74523d6f77e8784d13421ada",
    REFERENCE: "9bc3f10ad27615f23ddb3c2f62169575378d32e6c35c9d2a9dd51223f9b39ec4",
    SHARED: "bd7139b6f846b69706a89c6c72e426605aebd5fa4ffbb75dcf1bcfb83c04da9d",
    HISTORY: "b1d907c08cd73708404a8ee18a239f2863316b4d4fbe110ee48aa3863acd8ca1",
    REFERENCE_EXE: "8ee49ae42cb6994f4bd42ed3a3920152e767407ecdafd8986577d5496370a379",
    HISTORICAL_COMPARATOR: "785cf27d7c843df90f3fcff8e7b96bf2a6cad83c7a7d33006def25691ee376a6",
    PARENT / "public-lifecycle-driver.rs": "0866ab1e5f8eb5c24a73b8186fd7c475d15860f72aeb0858c99e67e0b6dc83f0",
    PARENT / "public-lifecycle-source.json": "2f3d65c6d77c4ae21c882e2828cc0f5b7b31383874adce28b69fa6ce8490905b",
    PARENT / "lifecycle-driver-review.json": "91247bca13f1706f29824aa43581f02318da9cb878236789de2b1b3fe22616ee",
    H / "hardening.json": "ea82c8e91e2f9427075463bf12beb0935cfc795f344356f92d1f61a1749e327f",
    H / "source-review.json": "6fc7f532bc6215a78087097f4f628b4a36775efef01b18756209a16aeec977b2",
}
SETTINGS = dict(propagators=6, rank=2, powers=[1] * 6, dimension_shift=0,
                algorithm="PassarinoVeltman", convention="IregiNative",
                tensor_weights="Components", invariants="FromShifts", input_policy="Preserve")
CERTIFICATE_KEYS = {"input_rows", "evaluated_rows", "passes", "reduction_batches"}
POLYNOMIAL = [[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1]]
COEFFICIENTS = [2, -3, 1, 4]
TOLERANCE = Decimal("1e-10")
SCHEDULE = [
    ("singleton_base", [0]), ("singleton_scaled", [1]), ("singleton_singular", [2]),
    ("empty_after_failure", []), ("mixed", [0, 2, 1, 0, 2]),
    ("reordered", [2, 0, 1, 2, 0]), ("mixed_chunk_first", [0, 2]),
    ("mixed_chunk_second", [1, 0, 2]), ("repeated_good", [0, 1, 0, 1, 0]),
    ("empty_after_repetition", []), ("base_after_empty", [0]),
]
STAT_KEYS = {"input_rows", "argument_rows", "master_family_batches", "master_rows",
             "pentagon_box_rows", "reduction_rows", "fallback_rows", "fallback_successes", "analytic_rows"}
META = dict(convention="IregiNative", tensor_weights="Components", dual_shape=None)
PARTS = ["real", "imaginary"]
SLOT_KEYS = {"real", "imaginary", "real_precision", "imaginary_precision",
             "real_negative", "imaginary_negative"}
SCOPE = ("Restricted public six-point rank2 lifecycle, Float128/request53, native Components: "
         "11 calls, 17 successful arrays of 60 complex Laurent slots plus four contraction slots, "
         "7 explicit rejection controls and 2 empty calls. No general-domain, numerical Dual, "
         "rank7, N7, performance or automatic production-adoption claim. The singular fixture "
         "is an expected rejection control; rejection alone does not localize its cause.")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def load(path, expected, name):
    require(sha(path) == expected, f"unreviewed comparator dependency: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def exact_inputs(sample):
    ps = sample["propagators"][:6]
    require(len(ps) == 6 and all(p["power"] == 1 for p in ps), "invalid fixture topology")
    row = [[str(Fraction(v)), "0"] for p in ps for v in p["shift"]]
    row += [[str(Fraction(v)) for v in p["mass_squared"]] for p in ps]
    return row + [[str(Fraction(sample["mu"])), "0"]]


def validate_slots(moments, signed=True, expected_moments=15):
    require(isinstance(moments, list) and len(moments) == expected_moments, "incomplete moment inventory")
    for index, moment in enumerate(moments):
        require(isinstance(moment, list) and len(moment) == 4, "expected four Laurent slots")
        for pole, slot in enumerate(moment):
            keys = SLOT_KEYS if signed else SLOT_KEYS - {"real_negative", "imaginary_negative"}
            require(isinstance(slot, dict) and set(slot) == keys, "incomplete coefficient metadata")
            for part in PARTS:
                require(isinstance(slot[part], str), "coefficient must be an exact rational string")
                value = Fraction(slot[part])
                bits = slot[part + "_precision"]
                require(type(bits) is int and bits >= 0 and (value == 0 or bits > 0), "invalid operand precision")
                if signed:
                    negative = slot[part + "_negative"]
                    require(type(negative) is bool and (value == 0 or negative == (value < 0)), "invalid coefficient sign metadata")
                if pole < 3:
                    require(value == 0, f"nonzero native pole at moment {index}, slot {pole}")


def normalized_error(actual, reference, sample, shared, reference_slots=False):
    q, errors = shared.scale(sample, 6), []
    for index, monomial in enumerate(shared.canonical_basis(2)):
        natural = q ** (sum(monomial) - 8)
        for pole in range(4):
            a = tuple(shared.decimal_rational(actual[index][pole][part]) / natural for part in PARTS)
            b = (tuple(Decimal(str(x)) / natural for x in reference[index][pole]) if reference_slots
                 else tuple(shared.decimal_rational(reference[index][pole][part]) / natural for part in PARTS))
            errors.append(shared.norm(tuple(x - y for x, y in zip(a, b))) / max(Decimal(1), shared.norm(b)))
    require(len(errors) == 60, "incomplete numerical coverage")
    return max(errors)


def singleton_differences(actual, baseline, expected_moments=15):
    differences = []
    for moment in range(expected_moments):
        for pole in range(4):
            a, b = actual[moment][pole], baseline[moment][pole]
            for part in PARTS:
                precision, negative = part + "_precision", part + "_negative"
                same = (a[part] == b[part], a[precision] == b[precision], a[negative] == b[negative])
                if not all(same):
                    differences.append(dict(moment=moment, laurent_slot=pole, part=part,
                        same_exact_value=same[0], same_precision=same[1], same_sign_bit=same[2],
                        current=dict(value=a[part], precision=a[precision], negative=a[negative]),
                        singleton=dict(value=b[part], precision=b[precision], negative=b[negative])))
    return differences


def check_stats(stats):
    require(isinstance(stats, dict) and set(stats) == STAT_KEYS, "execution counter inventory differs")
    require(all(type(value) is int and value >= 0 for value in stats.values()), "invalid execution counter")


def check_certificate_stats(stats):
    require(isinstance(stats, dict) and set(stats) == CERTIFICATE_KEYS,
            "certificate counter inventory differs")
    require(all(type(value) is int and value >= 0 for value in stats.values()),
            "invalid certificate counter")
    require(stats["passes"] <= stats["evaluated_rows"]
            and stats["reduction_batches"] <= stats["input_rows"],
            "inconsistent certificate pass/row accounting")
    if stats["input_rows"] == 0:
        require(all(value == 0 for value in stats.values()), "stale certificate work without input rows")


def validate_contraction_slots(slots):
    require(isinstance(slots, list) and len(slots) == 4, "incomplete contraction Laurent slots")
    # Identical native metadata and exact-zero pole checks as the moment array.
    validate_slots([slots], expected_moments=1)


def contraction_singleton_differences(actual, baseline):
    differences = singleton_differences([actual], [baseline], expected_moments=1)
    return [{key: value for key, value in item.items() if key != "moment"}
            for item in differences]


def contraction_sum(moments, shared, reference=False):
    """Independent saved-number linear sum, not an integral evaluation."""
    basis = shared.canonical_basis(2)
    positions = [basis.index(monomial) for monomial in POLYNOMIAL]
    result = []
    for pole in range(4):
        components = []
        for part_index, part in enumerate(PARTS):
            total = sum((Fraction(coefficient) * Fraction(
                str(moments[position][pole][part_index]) if reference
                else moments[position][pole][part])
                for position, coefficient in zip(positions, COEFFICIENTS)), Fraction(0))
            components.append(Decimal(total.numerator) / Decimal(total.denominator))
        result.append(tuple(components))
    return result


def compare_contraction(actual, moments, reference, singleton, sample, shared):
    q = shared.scale(sample, 6)
    natural = sum((Decimal(abs(coefficient)) * q ** (sum(monomial) - 8)
                   for coefficient, monomial in zip(COEFFICIENTS, POLYNOMIAL)), Decimal(0))
    require(natural.is_finite() and natural > 0, "invalid mixed-rank contraction scale")
    targets = {
        "captured_moment_sum": contraction_sum(moments, shared),
        "original_reference_sum": contraction_sum(reference, shared, True),
        "singleton": [tuple(shared.decimal_rational(slot[part]) for part in PARTS)
                      for slot in singleton],
    }
    errors = {name: [] for name in targets}
    for pole, slot in enumerate(actual):
        value = tuple(shared.decimal_rational(slot[part]) for part in PARTS)
        for name, values in targets.items():
            target = values[pole]
            error = shared.norm(tuple(a - b for a, b in zip(value, target))) / max(natural, shared.norm(target))
            errors[name].append(error)
    require(all(len(values) == 4 for values in errors.values()), "incomplete contraction comparison")
    require(all(value <= TOLERANCE for values in errors.values() for value in values),
            "contraction disagreement: " + str({name: str(max(values)) for name, values in errors.items()}))
    return dict(complex_slots=4, natural_scale=str(natural),
                normalized_errors={name: [str(value) for value in values] for name, values in errors.items()},
                maximum_normalized_errors={name: str(max(values)) for name, values in errors.items()})


def validate_capture(record, fixture, references, shared, settings):
    schedule = [dict(name=name, fixture_indices=ids) for name, ids in SCHEDULE]
    require(record.get("schema_version") == 1 and record.get("status") == "capture_complete_status_contract_passed"
            and record.get("active_case") is None and record.get("settings") == settings
            and record.get("working_bits") == 128 and record.get("requested_bits") == 53
            and record.get("fixture") == str(FIXTURE.relative_to(R))
            and record.get("basis") == shared.canonical_basis(2)
            and record.get("schedule") == schedule
            and record.get("interface") == "restricted public SixPointReductionPlan / SixPointWorkspace<Float>"
            and record.get("numerical_tolerance_qualification") == "pending_independent_qualifier", "lifecycle schedule, topology or completion differs")
    require([sample["id"] for sample in fixture["samples"]] == ["base", "scaled_by_two", "first_mass_squared_plus_one"],
            "fixture sample inventory differs")
    require(type(record.get("elapsed_seconds")) in (int, float)
            and math.isfinite(record["elapsed_seconds"]) and 0 <= record["elapsed_seconds"] <= 180,
            "invalid lifecycle diagnostic elapsed time")
    require(record.get("input_exact_rational") == [exact_inputs(sample) for sample in fixture["samples"]]
            and record.get("expected_successful_fixture_indices") == [0, 1]
            and record.get("expected_rejected_fixture_indices") == [2]
            and record.get("workspace_lifecycle") == "one owned workspace reused for every scheduled call",
            "lifecycle inputs or workspace policy differ")
    cases = record.get("cases")
    require(isinstance(cases, list) and len(cases) == 11, "incomplete lifecycle call inventory")
    baselines, outcomes, successes, failures, differences = {}, {}, [], [], []
    contraction_baselines, contractions, contraction_differences = {}, [], []
    counter_records = []
    for call, ((name, ids), case) in enumerate(zip(SCHEDULE, cases)):
        n = len(ids)
        require(type(case.get("diagnostic_reduction_seconds")) in (int, float)
                and math.isfinite(case["diagnostic_reduction_seconds"])
                and 0 <= case["diagnostic_reduction_seconds"] <= record["elapsed_seconds"],
                "invalid per-call diagnostic duration")
        require(case.get("name") == name and case.get("fixture_indices") == ids and case.get("rows") == n
                and case.get("components") == 1 and case.get("basis") == shared.canonical_basis(2)
                and case.get("metadata") == META and case.get("capture_status") == "captured"
                and case.get("status_shape_contract_pass") is True and case.get("input_preserved_exactly") is True
                and case.get("packing_contract_pass") is True, f"invalid lifecycle call: {name}")
        for key in ["lanes", "lane_statuses", "fallback_used", "analytic_used", "diagnostics", "singleton_comparisons"]:
            require(isinstance(case.get(key), list) and len(case[key]) == n, f"wrong {key} lane count in {name}")
        require(all(type(flag) is bool for key in ["fallback_used", "analytic_used"] for flag in case[key]), "invalid work flags")
        require(all(isinstance(notes, list) and all(isinstance(note, str) for note in notes)
                    for notes in case["diagnostics"]), "invalid lane diagnostics")
        execution = case["execution"]
        require(set(execution) == {"parent_input_rows", "child_batch_calls", "packed_child_rows",
                                  "parent_batch_calls", "packed_parent_rows", "child_execution", "parent_execution",
                                  "child_certificate_execution", "parent_certificate_execution"},
                "wrong lifecycle counter inventory")
        for key in ["parent_input_rows", "child_batch_calls", "packed_child_rows", "parent_batch_calls", "packed_parent_rows"]:
            require(type(execution[key]) is int and execution[key] >= 0, "invalid packing count")
        child, parent = execution["child_execution"], execution["parent_execution"]
        check_stats(child)
        check_stats(parent)
        child_certificate = execution["child_certificate_execution"]
        parent_certificate = execution["parent_certificate_execution"]
        check_certificate_stats(child_certificate)
        check_certificate_stats(parent_certificate)
        require(all(value == 0 for value in parent_certificate.values()),
                "master-free parent unexpectedly performed planar certificate work")
        require(child_certificate["input_rows"] <= child["fallback_rows"],
                "certificate input rows exceed counted fallback attempts")
        require(execution["parent_input_rows"] == n and execution["child_batch_calls"] == int(n > 0)
                and execution["packed_child_rows"] == 6 * n and child["input_rows"] == 6 * n,
                "child calls did not batch all six subsets")
        packed = execution["packed_parent_rows"]
        require(sum(i < 2 for i in ids) <= packed <= n and execution["parent_batch_calls"] == int(packed > 0)
                and parent["input_rows"] == packed and parent["argument_rows"] == packed
                and 0 <= parent["reduction_rows"] <= packed, "parent packing counter mismatch")
        require(all(parent[key] == 0 for key in ["master_family_batches", "master_rows", "pentagon_box_rows",
                                                 "fallback_rows", "fallback_successes", "analytic_rows"]),
                "thin parent unexpectedly performed masters or rerouting")
        if n == 0:
            require(case.get("empty_work_and_diagnostics_reset") is True
                    and all(value == 0 for value in child.values()) and all(value == 0 for value in parent.values())
                    and all(value == 0 for value in child_certificate.values())
                    and all(value == 0 for value in parent_certificate.values()),
                    "empty call retained work or diagnostics")
        else:
            require(case.get("empty_work_and_diagnostics_reset") is None and child["argument_rows"] >= 6 * n,
                    "nonempty call packing accounting differs")
        counter_records.append(dict(call=name, execution=execution))
        contracted = case.get("contraction")
        require(isinstance(contracted, dict) and set(contracted) ==
                {"monomials", "coefficients", "evaluated_rows", "lanes", "fallback_used", "analytic_used"},
                "contraction capture inventory differs")
        require(contracted["monomials"] == POLYNOMIAL and contracted["coefficients"] == COEFFICIENTS
                and type(contracted["evaluated_rows"]) is int
                and contracted["evaluated_rows"] == sum(i < 2 for i in ids)
                and contracted["fallback_used"] == case["fallback_used"]
                and contracted["analytic_used"] == case["analytic_used"]
                and isinstance(contracted["lanes"], list) and len(contracted["lanes"]) == n,
                "contraction inputs, work reset or lane flags differ")
        expected_comparisons = []
        for row, (fixture_index, lane) in enumerate(zip(ids, case["lanes"])):
            require(lane.get("row") == row and lane.get("fixture_index") == fixture_index
                    and lane.get("status") == case["lane_statuses"][row]
                    and lane.get("fallback_used") is case["fallback_used"][row]
                    and lane.get("analytic_used") is case["analytic_used"][row], "lane ordering or flags disagree")
            contraction = contracted["lanes"][row]
            require(isinstance(contraction, dict) and set(contraction) == {"row", "fixture_index", "status", "slots"}
                    and contraction["row"] == row and contraction["fixture_index"] == fixture_index
                    and contraction["status"] == lane["status"], "contraction lane/status order differs")
            flags = (lane["fallback_used"], lane["analytic_used"])
            if fixture_index in outcomes:
                require(flags == outcomes[fixture_index], "rerouting flags changed under batch order or workspace reuse")
            else:
                outcomes[fixture_index] = flags
            if fixture_index == 2:
                require(lane.get("expected_outcome") == "explicit_rejection"
                        and isinstance(lane["status"], str) and lane["status"].startswith(("Unstable(", "MasterFailure("))
                        and lane.get("moments") is None and lane.get("complete_native_array") is False
                        and contraction["slots"] is None,
                        "singular control became successful or exposed partial coefficients")
                failures.append(dict(call=name, row=row, status=lane["status"], diagnostics=case["diagnostics"][row]))
                expected_comparisons.append(dict(row=row, fixture_index=2, comparison="failure_control_not_numerical_agreement"))
                continue
            require(lane.get("expected_outcome") == "Success" and lane["status"] == "Success"
                    and lane.get("complete_native_array") is True, "expected complete successful neighbor is unavailable")
            validate_slots(lane["moments"])
            validate_contraction_slots(contraction["slots"])
            if fixture_index not in baselines:
                require(call == fixture_index, "singleton baseline was not captured first")
                baselines[fixture_index] = lane["moments"]
            delta = singleton_differences(lane["moments"], baselines[fixture_index])
            comparison = dict(row=row, fixture_index=fixture_index, comparison="complete_successful_native_arrays",
                              exact_value_precision_sign_identity=not delta, differences=delta,
                              numerical_tolerance_qualification="deferred_to_independent_normalized_1e-10_qualifier")
            expected_comparisons.append(comparison)
            sample = fixture["samples"][fixture_index]
            original_error = normalized_error(lane["moments"], references[fixture_index], sample, shared, True)
            singleton_error = normalized_error(lane["moments"], baselines[fixture_index], sample, shared)
            require(original_error <= Decimal("1e-10") and singleton_error <= Decimal("1e-10"),
                    f"numerical disagreement in {name}, row {row}: original={original_error}, singleton={singleton_error}")
            successes.append(dict(call=name, row=row, fixture_index=fixture_index, complex_slots=60,
                                  maximum_original_error=str(original_error), maximum_singleton_error=str(singleton_error)))
            differences.extend(dict(call=name, row=row, fixture_index=fixture_index, **item) for item in delta)
            if fixture_index not in contraction_baselines:
                require(call == fixture_index, "contraction singleton baseline was not captured first")
                contraction_baselines[fixture_index] = contraction["slots"]
            contraction_report = compare_contraction(contraction["slots"], lane["moments"],
                references[fixture_index], contraction_baselines[fixture_index], sample, shared)
            contractions.append(dict(call=name, row=row, fixture_index=fixture_index, **contraction_report))
            contraction_delta = contraction_singleton_differences(
                contraction["slots"], contraction_baselines[fixture_index])
            contraction_differences.extend(dict(call=name, row=row, fixture_index=fixture_index, **item)
                                           for item in contraction_delta)
        require(case["singleton_comparisons"] == expected_comparisons, "driver difference inventory is incomplete or inconsistent")
    require(len(successes) == len(contractions) == 17 and len(failures) == 7, "wrong lifecycle lane coverage")
    return dict(calls=11, empty_calls=2, successful_lanes=17, failure_controls=7,
                complex_slots=1020, real_components=2040, exact_zero_complex_poles=765,
                successes=successes, failures=failures, singleton_value_precision_sign_differences=differences,
                exact_identity_required=False, certificate_and_execution_counters=counter_records,
                contracted_complex_slots=68, contracted_real_components=136,
                contracted_exact_zero_complex_poles=51, contractions=contractions,
                contraction_singleton_value_precision_sign_differences=contraction_differences)


def bind_pinned(harness, path, inputs, expected):
    harness.bind(path, inputs, expected)


def validate_references(harness, inputs):
    for path, expected in PINS.items():
        bind_pinned(harness, path, inputs, expected)
    shared = load(SHARED, PINS[SHARED], "public_six_point_lifecycle_math")
    fixture, reference = read(FIXTURE), read(REFERENCE)
    shared.validate_reference(reference, fixture, PINS[FIXTURE])
    require(reference["executable_sha256"] == PINS[REFERENCE_EXE], "original executable binding differs")
    history = read(HISTORY)
    require(all(history["artifacts"][path.name] == PINS[path] for path in (FIXTURE, REFERENCE)),
            "untouched original capture provenance differs")
    references = {}
    for index, sample in enumerate(fixture["samples"][:2]):
        selected = [case for case in reference["cases"] if case["id"] == f'n6_{sample["id"]}_mode0']
        require(len(selected) == 1 and selected[0]["status"] == "captured"
                and selected[0]["mode"] == 0 and selected[0]["response"]["stable"] is True,
                "missing stable original IBP base/scaled reference")
        # validate_reference checked all 330 rank-seven slots and native Laurent
        # order. The canonical first 15 moments are exactly the rank-two basis.
        references[index] = selected[0]["response"]["moments"]
    return shared, fixture, references


def validate_saved_run(harness, inputs):
    validated = harness.validate_run("lifecycle")
    require(isinstance(validated, dict) and isinstance(validated.get("record"), dict)
            and isinstance(validated.get("input_sha256"), dict) and validated["input_sha256"],
            "harness did not return a validated capture and complete binding map")
    normalized = {}
    for name, digest in validated["input_sha256"].items():
        path = Path(name)
        path = path.resolve() if path.is_absolute() else (R / path).resolve()
        require(str(path) not in normalized or normalized[str(path)] == digest,
                "conflicting harness bindings")
        normalized[str(path)] = digest
        bind_pinned(harness, path, inputs, digest)
    mandatory = set(PINS) | {Path(__file__).resolve(), H / "harness_common.py",
                            CAPTURE / "run.json", CAPTURE / "result.json", CAPTURE / "step-0.log"}
    require({str(path.resolve()) for path in mandatory} <= set(normalized),
            "harness capture guard closure omits comparator, source, original reference or saved outputs")
    require(validated["record"] == read(CAPTURE / "result.json"), "harness result differs from bound saved array")
    return validated["record"]


def main():
    output = H / "lifecycle-comparison.json"
    require(not output.exists(), "existing qualification is immutable")
    inputs = {}
    report = dict(schema_version=1, status="failed", passed=False, lifecycle_qualified=False,
                  contraction_qualified=False, precision_convergence_qualified=False,
                  performance_qualified=False, scope=SCOPE)
    try:
        spec = importlib.util.spec_from_file_location("six_point_integration_harness", H / "harness_common.py")
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)
        require(Path(harness.ROOT).resolve() == R and Path(harness.HERE).resolve() == H,
                "wrong provenance harness root")
        record = validate_saved_run(harness, inputs)
        shared, fixture, references = validate_references(harness, inputs)
        with localcontext() as context:
            context.prec = 200
            coverage = validate_capture(record, fixture, references, shared, SETTINGS)
        harness.final_verify(inputs)
        report.update(status="passed", passed=True, lifecycle_qualified=True, contraction_qualified=True,
                      coverage=coverage, normalized_original_tolerance="1e-10",
                      normalized_singleton_tolerance="1e-10", normalized_contraction_tolerance="1e-10",
                      moment_normalization="Q^(4-2N+rank); complex norm / max(1, normalized reference norm)",
                      contraction_normalization="S=sum_j |c_j| Q^(rank_j-8); |actual-reference|/max(S,|reference|)",
                      contraction_comparisons=["same captured moments summed exactly as rational numbers",
                                               "untouched stable original IBP moments", "same fixture singleton"],
                      original_references=[dict(id=f'n6_{sample["id"]}_mode0', mode=0, stable=True,
                                                cumulative_rank=2, used_complex_slots=60)
                                           for sample in fixture["samples"][:2]],
                      runtime_bound_seconds=180,
                      prerequisite_scope="Harness requires the separately qualified integrated exact, ordinary-default and base128/256 gates; lifecycle itself is Float128 only.")
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
    report["input_sha256"] = inputs
    with output.open("x") as stream:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "output": str(output), "scope": SCOPE}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())


#!/usr/bin/env python3
"""Private lifecycle qualification; never executes a compiler or integral.

Requires a separately reviewed frozen protocol, guarded driver link/capture,
the unchanged full exact gate, and the prior two-precision numerical gate.
Success covers only the explicit eleven-call Float128/request53 schedule.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys

R = Path(__file__).resolve().parents[3]
H = R / "target/public-highpoint/thin-n6-mask"
BUILD = H / "lifecycle-build-001"
CAPTURE = H / "lifecycle-001"
PROTOCOL = H / "lifecycle-protocol.json"
MAIN = H / "comparison-v2-128-256.json"
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
SCOPE = ("Private thin N6 mask rank2 lifecycle, Float128/request53, native Components: "
         "11 calls, 17 successful arrays of 60 complex Laurent slots, 7 explicit failure controls, "
         "2 empty calls. No general-domain, Dual-numeric, rank7, N7, adoption or performance claim. "
         "The singular fixture is an expected rejection control; rejection alone does not localize its cause.")


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


def validate_slots(moments, signed=True):
    require(isinstance(moments, list) and len(moments) == 15, "expected all 15 moments")
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


def singleton_differences(actual, baseline):
    differences = []
    for moment in range(15):
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


def validate_capture(record, fixture, references, shared, settings):
    schedule = [dict(name=name, fixture_indices=ids) for name, ids in SCHEDULE]
    require(record.get("schema_version") == 1 and record.get("status") == "capture_complete_status_contract_passed"
            and record.get("active_case") is None and record.get("settings") == settings
            and record.get("working_bits") == 128 and record.get("requested_bits") == 53
            and record.get("fixture") == str(H.parents[2] / "validation/public-highpoint/fixture-conditioned_masses.json")
            and record.get("basis") == shared.canonical_basis(2)
            and record.get("schedule") == schedule, "lifecycle schedule, topology or completion differs")
    require([sample["id"] for sample in fixture["samples"]] == ["base", "scaled_by_two", "first_mass_squared_plus_one"],
            "fixture sample inventory differs")
    require(record.get("input_exact_rational") == [exact_inputs(sample) for sample in fixture["samples"]]
            and record.get("expected_successful_fixture_indices") == [0, 1]
            and record.get("expected_rejected_fixture_indices") == [2]
            and record.get("workspace_lifecycle") == "one owned workspace reused for every scheduled call",
            "lifecycle inputs or workspace policy differ")
    cases = record.get("cases")
    require(isinstance(cases, list) and len(cases) == 11, "incomplete lifecycle call inventory")
    baselines, outcomes, successes, failures, differences = {}, {}, [], [], []
    for call, ((name, ids), case) in enumerate(zip(SCHEDULE, cases)):
        n = len(ids)
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
                                  "parent_batch_calls", "packed_parent_rows", "child_execution", "parent_execution"},
                "wrong lifecycle counter inventory")
        for key in ["parent_input_rows", "child_batch_calls", "packed_child_rows", "parent_batch_calls", "packed_parent_rows"]:
            require(type(execution[key]) is int and execution[key] >= 0, "invalid packing count")
        child, parent = execution["child_execution"], execution["parent_execution"]
        check_stats(child)
        check_stats(parent)
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
                    and all(value == 0 for value in child.values()) and all(value == 0 for value in parent.values()),
                    "empty call retained work or diagnostics")
        else:
            require(case.get("empty_work_and_diagnostics_reset") is None and child["argument_rows"] >= 6 * n,
                    "nonempty call packing accounting differs")
        expected_comparisons = []
        for row, (fixture_index, lane) in enumerate(zip(ids, case["lanes"])):
            require(lane.get("row") == row and lane.get("fixture_index") == fixture_index
                    and lane.get("status") == case["lane_statuses"][row]
                    and lane.get("fallback_used") is case["fallback_used"][row]
                    and lane.get("analytic_used") is case["analytic_used"][row], "lane ordering or flags disagree")
            flags = (lane["fallback_used"], lane["analytic_used"])
            if fixture_index in outcomes:
                require(flags == outcomes[fixture_index], "rerouting flags changed under batch order or workspace reuse")
            else:
                outcomes[fixture_index] = flags
            if fixture_index == 2:
                require(lane.get("expected_outcome") == "explicit_rejection"
                        and isinstance(lane["status"], str) and lane["status"].startswith(("Unstable(", "MasterFailure("))
                        and lane.get("moments") is None and lane.get("complete_native_array") is False,
                        "singular control became successful or exposed partial coefficients")
                failures.append(dict(call=name, row=row, status=lane["status"], diagnostics=case["diagnostics"][row]))
                expected_comparisons.append(dict(row=row, fixture_index=2, comparison="failure_control_not_numerical_agreement"))
                continue
            require(lane.get("expected_outcome") == "Success" and lane["status"] == "Success"
                    and lane.get("complete_native_array") is True, "expected complete successful neighbor is unavailable")
            validate_slots(lane["moments"])
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
        require(case["singleton_comparisons"] == expected_comparisons, "driver difference inventory is incomplete or inconsistent")
    require(len(successes) == 17 and len(failures) == 7, "wrong lifecycle lane coverage")
    return dict(calls=11, empty_calls=2, successful_lanes=17, failure_controls=7,
                complex_slots=1020, real_components=2040, exact_zero_complex_poles=765,
                successes=successes, failures=failures, singleton_value_precision_sign_differences=differences,
                exact_identity_required=False)


def validate_protocol(v, inputs):
    v.bind(PROTOCOL, inputs)
    protocol = read(PROTOCOL)
    require(protocol.get("schema_version") == 1 and protocol.get("source_review_status") == "approved_source_only"
            and protocol.get("build_bound_seconds") == 30 and protocol.get("runtime_bound_seconds") == 180
            and protocol.get("required_main_comparison") == MAIN.name, "lifecycle protocol is not frozen/reviewed")
    names = ["lifecycle_driver.rs", "lifecycle-build.py", "lifecycle-run.py", "compare-lifecycle.py",
             "build-001/build.json", "compare-v2.py", "source-review.json"]
    expected = {str((H / name).relative_to(R)): sha(H / name) for name in names}
    v.inventory(protocol.get("artifacts"), expected, "reviewed lifecycle protocol")
    for name, digest in expected.items():
        v.bind(R / name, inputs, digest)
    require(sha(H / "lifecycle_driver.rs") == "c496497778ce15c57963ccfa167b1d6f1d6ebc001a956149248b81f0b195316c",
            "lifecycle driver differs from reviewed source")
    return protocol


def validate_main_gate(v, shared, build, fixture, references, inputs):
    v.bind(MAIN, inputs)
    main = read(MAIN)
    require(main.get("status") == "passed" and main.get("protocol_version") == 2
            and main.get("full_array_original_agreement_qualified") is True
            and main.get("precision_convergence_qualified") is True
            and main.get("normalized_original_tolerance") == "1e-10"
            and main.get("convergence_tolerance") == "2^-80"
            and [r.get("working_bits") for r in main.get("records", [])] == [128, 256],
            "required main 128/256 qualification is absent")
    require(main.get("input_sha256"), "main qualification has no provenance")
    for name, digest in main["input_sha256"].items():
        v.bind(name, inputs, digest)
    require(main["input_sha256"].get(str(H / "compare-v2.py")) == sha(H / "compare-v2.py"), "main comparator identity differs")
    v.validate_exact(build, inputs)
    arrays = []
    for bits in [128, 256]:
        directory = H / f"n6-rank2-{bits}-001"
        command = ["taskset", "-c", "14", str(v.B / "driver"), str(v.FIXTURE), "6", "2", "pv",
                   str(bits), "53", "1", str(directory / "result.json")]
        v.validate_run(directory, build, [command], {"result.json", "step-0.log"}, 180, inputs)
        result = read(directory / "result.json")
        v.validate_array(result, bits, fixture, shared)
        moments = result["lanes"][0]["moments"]
        validate_slots(moments, False)
        require(normalized_error(moments, references[0], fixture["samples"][0], shared, True) <= Decimal("1e-10"),
                "main original-reference comparison no longer passes")
        arrays.append(moments)
    require(normalized_error(arrays[0], arrays[1], fixture["samples"][0], shared) <= Decimal(2) ** -80,
            "main convergence comparison no longer passes")
    return main


def validate_capture_provenance(v, build, main, inputs):
    path = BUILD / "build.json"
    v.bind(path, inputs)
    linked = read(path)
    expected = dict(build["inputs"])
    expected.update({str(v.B / name): digest for name, digest in build["outputs"].items()})
    expected.update({str(path): sha(path) for path in [v.B / "build.json", H / "lifecycle_driver.rs", H / "lifecycle-build.py", PROTOCOL]})
    v.inventory(linked.get("inputs"), expected, "lifecycle link input")
    old = next(step["command"] for step in build["steps"] if step["name"] == "driver")
    command = [str(H / "lifecycle_driver.rs") if arg == str(H / "driver.rs") else
               str(BUILD / "driver") if arg == str(v.B / "driver") else
               "thin_n6_lifecycle_driver" if arg == "thin_n6_driver" else arg for arg in old]
    require(linked.get("status") == "passed" and linked.get("inputs_unchanged") is True
            and linked.get("bound_seconds") == 30 and linked.get("exit_code") == 0 and not linked.get("timeout")
            and linked.get("command") == command and set(linked.get("outputs", {})) == {"driver", "driver.log"},
            "lifecycle link failed or changed the frozen core/link command")
    for name, digest in linked["outputs"].items():
        v.bind(BUILD / name, inputs, digest)
    v.bind(CAPTURE / "run.json", inputs)
    run = read(CAPTURE / "run.json")
    expected = dict(linked["inputs"])
    expected.update({str(BUILD / name): digest for name, digest in linked["outputs"].items()})
    expected.update({str(path): sha(path) for path in [BUILD / "build.json", H / "lifecycle-run.py", v.FIXTURE, MAIN]})
    for name, digest in main["input_sha256"].items():
        require(name not in expected or expected[name] == digest, "conflicting prerequisite provenance")
        expected[name] = digest
    v.inventory(run.get("inputs"), expected, "lifecycle runtime input")
    command = ["taskset", "-c", "14", str(BUILD / "driver"), str(v.FIXTURE), str(CAPTURE / "result.json")]
    require(run.get("status") == "passed" and run.get("inputs_unchanged") is True
            and run.get("bound_seconds") == 180 and run.get("environment_additions") == v.ENVIRONMENT
            and len(run.get("steps", [])) == 1, "lifecycle run is incomplete or has a different bound")
    step = run["steps"][0]
    require(step.get("command") == command and step.get("exit_code") == 0 and not step.get("timeout")
            and isinstance(step.get("seconds"), (float, int)) and math.isfinite(step["seconds"])
            and 0 <= step["seconds"] <= 180, "lifecycle process failed or exceeded bound")
    require(set(run.get("outputs", {})) == {"result.json", "step-0.log"}, "lifecycle capture artifacts missing")
    for name, digest in run["outputs"].items():
        v.bind(CAPTURE / name, inputs, digest)
    return run


def main():
    output = H / "lifecycle-qualification.json"
    require(not output.exists(), "existing qualification is immutable")
    inputs, report = {}, dict(status="failed", lifecycle_qualified=False, scope=SCOPE)
    try:
        v = load(H / "compare-v2.py", "869f0e510cf459e998e6862ef3c5067b48ffa58fd6925604e5b533011fa1d915", "thin_mask_lifecycle_gate")
        v.bind(Path(__file__), inputs)
        validate_protocol(v, inputs)
        build = v.validate_build(inputs)
        shared = load(v.SHARED, v.PINS[v.SHARED], "thin_mask_lifecycle_math")
        fixture, reference = read(v.FIXTURE), read(v.REFERENCE)
        shared.validate_reference(reference, fixture, sha(v.FIXTURE))
        v.bind(R / "target/reference/iregi-reference-original", inputs, reference["executable_sha256"])
        historical = R / "validation/public-highpoint/qualification.json"
        v.bind(historical, inputs)
        history = read(historical)
        require(all(history["artifacts"][path.name] == sha(path) for path in [v.FIXTURE, v.REFERENCE]),
                "untouched reference provenance differs")
        references = {}
        for index, sample in enumerate(fixture["samples"][:2]):
            selected = [c for c in reference["cases"] if c["id"] == f'n6_{sample["id"]}_mode0']
            require(len(selected) == 1 and selected[0]["status"] == "captured" and selected[0]["mode"] == 0
                    and selected[0]["response"]["stable"] is True, "base/scaled original IBP reference is not stable")
            references[index] = selected[0]["response"]["moments"]
        with localcontext() as context:
            context.prec = 180
            prerequisite = validate_main_gate(v, shared, build, fixture, references, inputs)
            run = validate_capture_provenance(v, build, prerequisite, inputs)
            coverage = validate_capture(read(CAPTURE / "result.json"), fixture, references, shared, v.SETTINGS)
        for path, digest in inputs.items():
            require(sha(path) == digest, f"artifact changed during qualification: {path}")
        report.update(status="passed", lifecycle_qualified=True, coverage=coverage,
                      normalized_original_tolerance="1e-10", normalized_singleton_tolerance="1e-10",
                      normalization="Q^(4-2N+rank); complex norm / max(1, normalized reference norm)",
                      runtime_bound_seconds=180, elapsed_seconds=run["elapsed_seconds"],
                      precision_convergence_scope="Prerequisite base128/256 only; lifecycle itself is128 only")
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
    report["input_sha256"] = inputs
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "output": str(output), "scope": SCOPE}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())

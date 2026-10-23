#!/usr/bin/env python3
"""All-slot saved-data diagnostics; never upgrades the failed acceptance gate.

This separately versioned protocol measures128/256 convergence and reports every
retained original mode, including its stability flag. It never runs a compiler
or an integral, and its completed status is not numerical acceptance.
"""
from decimal import Decimal, localcontext
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys

R = Path(__file__).resolve().parents[3]
H = R / "target/public-highpoint/thin-n6-rank7-phase"
B = H / "build-001"
LOW = H / "n6-rank7-128-001"
HIGH = H / "n6-rank7-256-diagnostic-001"
PROTOCOL = H / "diagnostic-protocol.json"
OUTPUT = H / "diagnostic-comparison-128-256.json"
ACCEPTANCE = H / "comparison-128.json"
ACCEPTANCE_SHA = "ad2fb606dd473a901f0c13192edf02b66c2cb14155dc2592524a4cc89218eb02"
LOW_RESULT_SHA = "717ec3e0e634add1975bd969291aab0b23c640fb0d6c41cd3307d23f96b00982"
HELPER_SHA = "6e59c3964d3363191975ba13008cd8982264fcf0b969374995233094b4a2554a"
FAILURE_AUDIT_PATH = R / "target/guard-performance-review/rank7-audit/audit-128.json"
FAILURE_AUDIT_SHA = "9fd8f76748730315304c8eebfe59950f894e2a265f31d9505e8bf4b0d954f78e"
SUPPLEMENT_PATH = FAILURE_AUDIT_PATH.parent / "supplemental-diagnostics.json"
SUPPLEMENT_SHA = "04f23c398a602500fb00b115ff6bcdc1c33fd5a5138109b36b02b36f6aa63cf7"
PHASE_ZERO_PATH = FAILURE_AUDIT_PATH.parent / "phase-zero-diagnostics.json"
PHASE_ZERO_SHA = "fb1cdf7a4970bb6cf9f477aa36616704d225291caefe3174113ad369754d1746"
AUDIT_MANIFEST_PATH = FAILURE_AUDIT_PATH.parent / "manifest.json"
AUDIT_MANIFEST_SHA = "1b925a9ba411941fa198ac8bb4ab45748ad04e4604ff2f9933fd743758b5780c"
ORACLE_DIRECTORY = R / "validation/public-highpoint"
ORACLE_PAIRS = {(8, 0), (12, 0), (12, 1), (16, 0), (16, 1), (20, 0), (20, 1)}
POLES = ["uv1", "ir1", "ir2", "finite"]
SCOPE = ("Private retained base N6 rank7 diagnostic on the identical frozen candidate. "
         "All330 moments/four native Laurent slots, requested53, unchanged1e-10 original comparison "
         "and2^-80 precision convergence thresholds. Original modes0/1/2 are reported with their stability flags. "
         "This diagnostic cannot upgrade the failed acceptance result, establish original accuracy or qualify adoption.")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_binding(mapping, path, digest):
    path = Path(path)
    path = str((path if path.is_absolute() else R / path).resolve())
    require(path not in mapping or mapping[path] == digest, f"conflicting provenance: {path}")
    mapping[path] = digest


def validate_diagnostic_protocol(base, build, inputs):
    base.bind(PROTOCOL, inputs)
    protocol = read(PROTOCOL)
    require(protocol.get("status") == "approved_source_only" and "/root" in protocol.get("reviewers", [])
            and protocol.get("runtime_bound_seconds") == 300 and protocol.get("rank") == 7
            and protocol.get("complex_slots") == 1320 and protocol.get("working_bits") == 256
            and protocol.get("requested_bits") == 53 and protocol.get("acceptance_qualified") is False
            and protocol.get("prior_acceptance_sha256") == ACCEPTANCE_SHA,
            "diagnostic protocol is not independently approved or its scope differs")
    expected = dict(build["inputs"])
    add_binding(expected, B / "build.json", base.bind(B / "build.json", inputs))
    for name, digest in build["outputs"].items():
        add_binding(expected, B / name, digest)
    for path in [LOW / "run.json", LOW / "result.json", LOW / "step-0.log", ACCEPTANCE]:
        add_binding(expected, path, base.bind(path, inputs))
    base.bind(LOW / "result.json", inputs, LOW_RESULT_SHA)
    base.bind(ACCEPTANCE, inputs, ACCEPTANCE_SHA)
    acceptance = read(ACCEPTANCE)
    require(acceptance.get("status") == "failed"
            and acceptance.get("full_array_original_agreement_qualified") is False
            and acceptance.get("precision_convergence_qualified") is False
            and "original disagreement at moment" in acceptance.get("error", ""),
            "the original failed acceptance gate is not preserved")
    for name, digest in acceptance["input_sha256"].items():
        base.bind(name, inputs, digest)
    for path in [H / "compare.py", B / "build.json", LOW / "run.json", LOW / "result.json", LOW / "step-0.log"]:
        require(acceptance["input_sha256"].get(str(path)) == base.bind(path, inputs), "failed acceptance binding differs")

    audit_name, audit_files = protocol["failure_audit_path"], protocol["failure_audit_artifacts"]
    require(not Path(audit_name).is_absolute() and ".." not in Path(audit_name).parts
            and R / audit_name == FAILURE_AUDIT_PATH and isinstance(audit_files, dict)
            and set(audit_files) == {str((FAILURE_AUDIT_PATH.parent / n).relative_to(R)) for n in
                ["audit-128.json", "audit_saved.py", "all-slots.json", "audit-128.stdout", "audit-128.stderr"]},
            "failure audit inventory is absent or incomplete")
    for name, digest in audit_files.items():
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "invalid failure audit artifact path")
        add_binding(expected, R / name, base.bind(R / name, inputs, digest))
    audit = read(R / audit_name)
    base.bind(FAILURE_AUDIT_PATH, inputs, FAILURE_AUDIT_SHA)
    require(audit.get("status") == "passed_independent_saved_data_audit_of_failed_numerical_gate"
            and audit.get("numerical_agreement_qualified") is False
            and audit.get("precision_convergence_qualified") is False
            and audit["numerical"]["moments"] == 330 and audit["numerical"]["complex_slots"] == 1320
            and audit["numerical"]["exact_zero_candidate_pole_slots"] == 990
            and audit["numerical"]["failed_slots"] == 90 and audit["numerical"]["failure_counts_by_laurent"] == {"finite": 90}
            and Decimal(audit["numerical"]["threshold"]) == Decimal("1e-10"), "independent failure characterization differs")
    base.bind(FAILURE_AUDIT_PATH.parent / "audit_saved.py", inputs, audit["script_sha256"])
    base.bind(FAILURE_AUDIT_PATH.parent / "all-slots.json", inputs, audit["all_slots_sha256"])
    slots = read(FAILURE_AUDIT_PATH.parent / "all-slots.json")["records"]
    require(len(slots) == 1320 and [(r["moment"], r["slot"]) for r in slots]
            == [(i, s) for i in range(330) for s in range(4)]
            and sum(r["failed"] is True for r in slots) == 90, "failure audit omits or reorders slots")
    require(isinstance(audit.get("input_sha256"), dict) and audit["input_sha256"], "failure audit has no provenance")
    audit_inputs = {}
    for name, digest in audit["input_sha256"].items():
        path = Path(name) if Path(name).is_absolute() else R / name
        add_binding(expected, path, base.bind(path, inputs, digest))
        add_binding(audit_inputs, path, digest)
    for path in [ACCEPTANCE, LOW / "result.json", LOW / "run.json", B / "build.json"]:
        require(audit_inputs.get(str(path)) == base.bind(path, inputs), "failure audit binds different evidence")
    for name in ["diagnostic-run.py", "diagnostic-compare.py"]:
        add_binding(expected, H / name, base.bind(H / name, inputs))
    oracles = validate_saved_oracles(base, inputs)
    for path in oracles["artifacts"]:
        add_binding(expected, path, base.bind(path, inputs))
    supplemental_files = protocol["supplemental_artifacts"]
    supplemental_path = protocol["supplemental_summary_path"]
    require(isinstance(supplemental_files, dict) and supplemental_path in supplemental_files,
            "independent supplemental characterization is absent")
    for name, digest in supplemental_files.items():
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "invalid supplemental path")
        add_binding(expected, R / name, base.bind(R / name, inputs, digest))
    require(R / protocol["audit_manifest_path"] == AUDIT_MANIFEST_PATH
            and R / protocol["phase_zero_summary_path"] == PHASE_ZERO_PATH, "independent audit paths differ")
    manifest = read(AUDIT_MANIFEST_PATH)
    base.bind(AUDIT_MANIFEST_PATH, inputs, AUDIT_MANIFEST_SHA)
    require(manifest["status"] == "frozen_independent_saved_data_failure_audit"
            and manifest["primary_audit_sha256"] == FAILURE_AUDIT_SHA
            and manifest["supplemental_sha256"] == SUPPLEMENT_SHA and manifest["phase_zero_sha256"] == PHASE_ZERO_SHA
            and len(manifest["files"]) == 19
            and all(manifest[k] is False for k in ["kernel_build_test_quadrature_or_algebra_executed",
                "numerical_agreement_qualified", "precision_convergence_qualified"]), "independent audit packet differs")
    packet = {str(AUDIT_MANIFEST_PATH.relative_to(R)): AUDIT_MANIFEST_SHA}
    for name, entry in manifest["files"].items():
        require(Path(name).name == name, "unsafe audit packet member")
        path = AUDIT_MANIFEST_PATH.parent / name
        require(path.stat().st_size == entry["bytes"], "audit packet member size differs")
        packet[str(path.relative_to(R))] = entry["sha256"]
    require(supplemental_files == packet, "complete independent audit payload inventory differs")
    for name, digest in manifest["upstream_input_sha256"].items():
        path = (Path(name) if Path(name).is_absolute() else R / name).resolve()
        add_binding(expected, path, base.bind(path, inputs, digest))
    supplemental = read(R / supplemental_path)
    require(R / supplemental_path == SUPPLEMENT_PATH, "supplemental summary path differs")
    base.bind(SUPPLEMENT_PATH, inputs, SUPPLEMENT_SHA)
    require(supplemental.get("status") == "completed_saved_data_diagnostics_only"
            and supplemental.get("kernel_build_test_or_quadrature_execution") is False
            and supplemental.get("numerical_agreement_qualified") is False
            and supplemental.get("precision_convergence_qualified") is False
            and [(r["mode"], r["reference_stable"], r["complex_slots"]) for r in supplemental["mode_comparisons"]]
                == [(0, True, 1320), (1, False, 1320), (2, True, 1320)]
            and {r["moment"] for r in supplemental["quadrature_witnesses"]} == {0, 321}
            and len(supplemental["quadrature_context"]) == 7
            and supplemental["missing_historical_quadrature_files"] == ["validation/public-highpoint/simplex-n6-order8-map1.json"],
            "supplemental saved-data scope differs")
    require(isinstance(supplemental.get("input_sha256"), dict) and supplemental["input_sha256"],
            "supplemental characterization has no provenance")
    supplemental_inputs = {}
    for name, digest in supplemental["input_sha256"].items():
        path = Path(name) if Path(name).is_absolute() else R / name
        add_binding(expected, path, base.bind(path, inputs, digest))
        add_binding(supplemental_inputs, path, digest)
    require(supplemental_inputs.get(str(LOW / "result.json")) == LOW_RESULT_SHA,
            "supplemental characterization binds a different128 result")
    require(str(PHASE_ZERO_PATH.relative_to(R)) in supplemental_files, "analytic phase-zero audit is absent")
    phase_zero = read(PHASE_ZERO_PATH)
    base.bind(PHASE_ZERO_PATH, inputs, PHASE_ZERO_SHA)
    require(phase_zero["status"] == "completed_independent_analytic_phase_zero_and_saved_data_diagnostics"
            and phase_zero["phase_zero_premise_verified"] is True and phase_zero["positive_F_lower_bound"] == "15/16"
            and phase_zero["zero_identity_error_definition"] == "abs(Re output)/Q^(rank-8)"
            and phase_zero["threshold"] == "1e-10"
            and all(phase_zero[k] is False for k in ["kernel_build_test_or_algebra_execution",
                "numerical_agreement_qualified", "precision_convergence_qualified", "imaginary_accuracy_qualified",
                "causal_cache_bug_inferred"]), "phase-zero diagnostic scope differs")
    phase_zero_inputs = {}
    for name, digest in phase_zero["input_sha256"].items():
        path = (Path(name) if Path(name).is_absolute() else R / name).resolve()
        add_binding(expected, path, base.bind(path, inputs, digest))
        add_binding(phase_zero_inputs, path, digest)
    require(phase_zero_inputs.get(str(LOW / "result.json")) == LOW_RESULT_SHA
            and phase_zero_inputs.get(str(base.FIXTURE)) == base.bind(base.FIXTURE, inputs),
            "phase-zero proof binds a different input or candidate")
    base.bind(PHASE_ZERO_PATH.parent / "phase_zero_saved.py", inputs, phase_zero["script_sha256"])
    base.bind(PHASE_ZERO_PATH.parent / "phase-zero-all-slots.json", inputs, phase_zero["all_slot_residuals_sha256"])
    base.bind(SUPPLEMENT_PATH.parent / "supplement_saved_v2.py", inputs, supplemental["script_sha256"])
    keys = {str(Path(n).relative_to(R)) if Path(n).is_relative_to(R) else n: d for n, d in expected.items()}
    allowed_absolute = {build["compiler_path"], str((R / "../references/madgraph/vendor/IREGI/src/mis_warp.f90").resolve()),
                        str((R / "../references/madgraph/vendor/IREGI/src/IREGI4ML5_interface.f90").resolve())}
    require({n for n in keys if Path(n).is_absolute()} == allowed_absolute
            and all(".." not in Path(n).parts for n in keys), "diagnostic artifact key policy differs")
    require(protocol["artifacts"] == keys, "complete diagnostic protocol inventory differs")
    add_binding(expected, PROTOCOL, base.bind(PROTOCOL, inputs))
    return protocol, expected, audit_name, oracles


def validate_diagnostic_run(base, expected, inputs):
    base.bind(HIGH / "run.json", inputs)
    run = read(HIGH / "run.json")
    require(run.get("inputs") == expected, "complete diagnostic runtime inventory differs")
    for path, digest in expected.items():
        base.bind(path, inputs, digest)
    require(set(run.get("outputs", {})) <= {"result.json", "step-0.log"}, "unexpected diagnostic output")
    for name, digest in run.get("outputs", {}).items():
        base.bind(HIGH / name, inputs, digest)
    command = ["taskset", "-c", "14", str(B / "driver"), str(base.FIXTURE),
               "6", "7", "pv", "256", "53", "1", str(HIGH / "result.json")]
    require(run.get("status") == "passed" and run.get("inputs_unchanged") is True
            and run.get("acceptance_qualified") is False
            and run.get("bound_seconds") == 300 and run.get("environment_additions") == base.ENVIRONMENT
            and [s.get("command") for s in run.get("steps", [])] == [command],
            "diagnostic capture did not complete the approved command")
    step = run["steps"][0]
    require(step.get("exit_code") == 0 and not step.get("timeout")
            and type(step.get("seconds")) in {int, float} and math.isfinite(step["seconds"])
            and 0 <= step["seconds"] <= 300 and set(run["outputs"]) == {"result.json", "step-0.log"},
            "diagnostic capture is incomplete or exceeded its bound")
    return run


def validate_saved_oracles(base, inputs):
    paths = sorted(ORACLE_DIRECTORY.glob("simplex-n6-order*-map*.json"))
    expected_paths = {ORACLE_DIRECTORY / f"simplex-n6-order{o}-map{m}.json" for o, m in ORACLE_PAIRS}
    require(set(paths) == expected_paths, "saved N6 quadrature inventory differs")
    script, integrand = ORACLE_DIRECTORY / "simplex_oracle.py", R / "validation/pv-high-rank/sixpoint_simplex_oracle.py"
    artifacts, records = [script, integrand], []
    for path in paths:
        base.bind(path, inputs)
        record = json.loads(path.read_text(), parse_float=Decimal)
        pair = record["order"], record["mapping"]
        require(record["status"] == "fixed_rule_evaluated" and record["n"] == 6 and pair in ORACLE_PAIRS
                and path.name == f"simplex-n6-order{pair[0]}-map{pair[1]}.json"
                and record["fixture_sha256"] == base.bind(base.FIXTURE, inputs)
                and record["ordering"] == (list(range(6)) if pair[1] == 0 else list(reversed(range(6))))
                and record["existing_rank7_integrand_source"] == str(integrand.relative_to(R))
                and record["normalization"] == "native finite = i*pi^2 times real OneLoop integral; all poles vanish",
                "saved quadrature identity or normalization differs")
        base.bind(script, inputs, record["script_sha256"])
        base.bind(integrand, inputs, record["existing_rank7_integrand_sha256"])
        require([(r["moment_index"], r["monomial"]) for r in record["results"]]
                == [(0, [0, 0, 0, 0]), (321, [0, 1, 0, 6])]
                and all(Decimal(r["native_finite_imaginary"]).is_finite() for r in record["results"]),
                "saved quadrature component coverage differs")
        artifacts.append(path)
        records.append((path, record))
    return dict(artifacts=artifacts, records=records)


def location(index, monomial, pole):
    return dict(moment=index, monomial=monomial, rank=sum(monomial), slot_index=pole, slot=POLES[pole])


def empty_summary():
    return dict(compared_complex_slots=0, failures=0, maximum_normalized_error=Decimal(0), worst=None)


def observe(summary, error, failed, where):
    summary["compared_complex_slots"] += 1
    summary["failures"] += int(failed)
    if summary["worst"] is None or error > summary["maximum_normalized_error"]:
        summary["maximum_normalized_error"], summary["worst"] = error, where


def printable_summary(summary):
    return {**summary, "maximum_normalized_error": str(summary["maximum_normalized_error"])}


def compare_original(record, case, q, shared):
    summary, ranks, slots, failures = empty_summary(), {}, {}, []
    for index, monomial in enumerate(record["basis"]):
        natural = q ** (sum(monomial) - 8)
        for pole, slot in enumerate(record["lanes"][0]["moments"][index]):
            actual = tuple(shared.decimal_rational(slot[k]) / natural for k in ["real", "imaginary"])
            original = tuple(Decimal(str(v)) / natural for v in case["response"]["moments"][index][pole])
            error = shared.norm(tuple(a-b for a, b in zip(actual, original))) / max(Decimal(1), shared.norm(original))
            failed, where = error > Decimal("1e-10"), location(index, monomial, pole)
            observe(summary, error, failed, where)
            observe(ranks.setdefault(str(sum(monomial)), empty_summary()), error, failed, where)
            observe(slots.setdefault(POLES[pole], empty_summary()), error, failed, where)
            if failed:
                failures.append({**where, "normalized_error": str(error), "natural_scale": str(natural),
                    "actual_exact_rational": [slot["real"], slot["imaginary"]],
                    "original_decimal": [str(v) for v in case["response"]["moments"][index][pole]]})
    require(summary["compared_complex_slots"] == 1320, "original comparison omitted slots")
    return dict(working_bits=record["working_bits"], original_id=case["id"], original_mode=case["mode"],
        original_stable=case["response"]["stable"], diagnostic_only=True, tolerance="1e-10",
        observed_all_slots_within_tolerance=not failures, **printable_summary(summary),
        by_rank={k: printable_summary(v) for k, v in ranks.items()},
        by_slot={k: printable_summary(v) for k, v in slots.items()}, failure_details=failures)


def compare_precisions(low, high, q, shared):
    summary, ranks, slots, failures = empty_summary(), {}, {}, []
    for index, monomial in enumerate(low["basis"]):
        natural = q ** (sum(monomial) - 8)
        for pole in range(4):
            pair = [tuple(shared.decimal_rational(record["lanes"][0]["moments"][index][pole][k]) / natural
                          for k in ["real", "imaginary"]) for record in [low, high]]
            error = shared.norm(tuple(a-b for a, b in zip(*pair))) / max(Decimal(1), shared.norm(pair[1]))
            failed, where = error > Decimal(2) ** -80, location(index, monomial, pole)
            observe(summary, error, failed, where)
            observe(ranks.setdefault(str(sum(monomial)), empty_summary()), error, failed, where)
            observe(slots.setdefault(POLES[pole], empty_summary()), error, failed, where)
            if failed:
                failures.append({**where, "normalized_error": str(error), "natural_scale": str(natural),
                    "low_exact_rational": [low["lanes"][0]["moments"][index][pole][k] for k in ["real", "imaginary"]],
                    "high_exact_rational": [high["lanes"][0]["moments"][index][pole][k] for k in ["real", "imaginary"]]})
    require(summary["compared_complex_slots"] == 1320, "precision comparison omitted slots")
    return dict(low_working_bits=128, high_working_bits=256, tolerance="2^-80", diagnostic_only=True,
        observed_all_slots_within_tolerance=not failures, **printable_summary(summary),
        by_rank={k: printable_summary(v) for k, v in ranks.items()},
        by_slot={k: printable_summary(v) for k, v in slots.items()}, failure_details=failures)


def pole_diagnostics(record, shared):
    checked, violations = 0, []
    for index, monomial in enumerate(record["basis"]):
        for pole in range(3):
            slot = record["lanes"][0]["moments"][index][pole]
            values = tuple(shared.decimal_rational(slot[k]) for k in ["real", "imaginary"])
            checked += 1
            if values != (Decimal(0), Decimal(0)):
                violations.append({**location(index, monomial, pole), "exact_rational": [slot["real"], slot["imaginary"]]})
    require(checked == 990, "pole diagnostic omitted slots")
    return dict(working_bits=record["working_bits"], checked_complex_poles=checked,
                exact_zero_complex_poles=checked-len(violations), nonzero_poles=violations)


def compare_oracles(records, oracles, q, shared):
    comparisons, spreads = [], []
    for index, monomial in [(0, [0, 0, 0, 0]), (321, [0, 1, 0, 6])]:
        natural = q ** (sum(monomial) - 8)
        values, last_values, by_mapping = [], [], {0: [], 1: []}
        for path, oracle in oracles["records"]:
            result = next(r for r in oracle["results"] if r["moment_index"] == index)
            imaginary = Decimal(result["native_finite_imaginary"])
            values.append(imaginary)
            if oracle["order"] in {16, 20}:
                last_values.append(imaginary)
            by_mapping[oracle["mapping"]].append((oracle["order"], imaginary))
            target = Decimal(0), imaginary / natural
            for record in records:
                slot = record["lanes"][0]["moments"][index][3]
                actual = tuple(shared.decimal_rational(slot[k]) / natural for k in ["real", "imaginary"])
                error = shared.norm(tuple(a-b for a, b in zip(actual, target))) / max(Decimal(1), shared.norm(target))
                comparisons.append(dict(working_bits=record["working_bits"], moment=index, monomial=monomial,
                    rank=sum(monomial), slot="finite", oracle_path=str(path.relative_to(R)),
                    order=oracle["order"], mapping=oracle["mapping"], ordering=oracle["ordering"],
                    candidate_exact_rational=[slot["real"], slot["imaginary"]],
                    oracle_native_complex=["0", str(imaginary)], natural_scale=str(natural),
                    normalized_error=str(error), tolerance="1e-10", observed_within_tolerance=error <= Decimal("1e-10"),
                    uncertainty_scope="Successive orders/mappings estimate convergence only; no rigorous error bound or acceptance claim."))
        successive = []
        for mapping, order_values in by_mapping.items():
            order_values.sort()
            successive.extend(dict(mapping=mapping, low_order=a[0], high_order=b[0],
                native_absolute_difference=str(abs(b[1]-a[1])),
                dimensionally_normalized_absolute_difference=str(abs(b[1]-a[1])/natural))
                for a, b in zip(order_values, order_values[1:]))
        spreads.append(dict(moment=index, monomial=monomial,
            all_orders_native_spread=str(max(values)-min(values)),
            all_orders_dimensionally_normalized_absolute_spread=str((max(values)-min(values))/natural),
            last_two_orders=[16, 20], last_two_orders_native_spread=str(max(last_values)-min(last_values)),
            last_two_orders_dimensionally_normalized_absolute_spread=str((max(last_values)-min(last_values))/natural),
            successive_order_differences=successive,
            uncertainty_scope="Observed spread only; neither an interval certificate nor a replacement for the original-reference gate."))
    require(len(comparisons) == 28, "saved quadrature comparisons are incomplete")
    return dict(status="estimated_convergence_only", acceptance_qualified=False, compared_finite_components=28,
        all_retained_rule_count=7, moments=[0, 321], comparisons=comparisons, spreads=spreads,
        missing_historical_configurations=[dict(order=8, mapping=1, status="not_recorded")],
        new_quadrature_executed=False)


def real_zero_diagnostics(records, q, shared):
    rows = []
    for record in records:
        summary, ranks, failures = empty_summary(), {}, []
        for index, monomial in enumerate(record["basis"]):
            natural = q ** (sum(monomial)-8)
            for pole, slot in enumerate(record["lanes"][0]["moments"][index]):
                residual = abs(shared.decimal_rational(slot["real"])) / natural
                failed, where = residual > Decimal("1e-10"), location(index, monomial, pole)
                observe(summary, residual, failed, where)
                observe(ranks.setdefault(str(sum(monomial)), empty_summary()), residual, failed, where)
                if failed:
                    failures.append({**where, "normalized_real_residual": str(residual),
                                     "real_exact_rational": slot["real"], "natural_scale": str(natural)})
        require(summary["compared_complex_slots"] == 1320, "real-zero diagnostic omitted slots")
        rows.append(dict(working_bits=record["working_bits"], **printable_summary(summary),
            observed_all_real_parts_within_tolerance=not failures, failure_details=failures,
            by_rank={k: printable_summary(v) for k, v in ranks.items()}))
    return dict(premise_audit_path=str(PHASE_ZERO_PATH.relative_to(R)), premise_audit_sha256=PHASE_ZERO_SHA,
        positive_F_lower_bound="15/16", domain="Only the bound retained real-input, positive-F ordinary fixture",
        error_definition="abs(Re output)/Q^(moment rank-8)", tolerance="1e-10", records=rows,
        imaginary_accuracy_qualified=False, acceptance_qualified=False, causal_implementation_bug_inferred=False,
        limitation="Real-zero residuals do not establish imaginary accuracy, replace the failed complex-array acceptance gate, or identify a cause.")


def main():
    require(sys.argv[1:] == [], "usage: diagnostic-compare.py")
    require(not OUTPUT.exists(), "diagnostic output already exists; evidence is immutable")
    inputs = {}
    report = dict(schema_version=1, status="diagnostic_failed", scope=SCOPE, diagnostic_only=True,
        acceptance_qualified=False, full_array_original_agreement_qualified=False,
        precision_convergence_qualified=False, lifecycle_qualified=False, performance_qualified=False,
        prior_acceptance_sha256=ACCEPTANCE_SHA, prior_acceptance_status="failed")
    try:
        helper_path = H / "compare.py"
        require(sha(helper_path) == HELPER_SHA, "frozen provenance helper changed")
        base = load_module("rank7_frozen_acceptance_helpers", helper_path)
        base.bind(helper_path, inputs, HELPER_SHA)
        base.bind(Path(__file__), inputs)
        build, exact_gate = base.validate_build(inputs)
        base.validate_numeric(LOW, 128, build, inputs)
        protocol, expected, failure_audit, oracles = validate_diagnostic_protocol(base, build, inputs)
        run = validate_diagnostic_run(base, expected, inputs)
        shared = load_module("rank7_diagnostic_shared_math", base.SHARED)
        fixture, reference = read(base.FIXTURE), read(base.REFERENCE)
        shared.validate_reference(reference, fixture, base.bind(base.FIXTURE, inputs))
        base.bind(base.REFERENCE_EXE, inputs, reference["executable_sha256"])
        history = read(base.HISTORY)
        for path in [base.FIXTURE, base.REFERENCE]:
            require(history["artifacts"][path.name] == base.bind(path, inputs), "historical reference binding differs")
        cases = [c for c in reference["cases"] if c["sample"] == "base" and c["propagators"] == 6]
        require(len(cases) == 3 and {c["mode"] for c in cases} == {0, 1, 2}
                and all(c["status"] == "captured" for c in cases), "not every retained original base mode is available")
        cases.sort(key=lambda c: c["mode"])
        low, high = read(LOW / "result.json"), read(HIGH / "result.json")
        with localcontext() as context:
            context.prec = 200
            base.validate_array(low, 128, fixture, shared)
            base.validate_array(high, 256, fixture, shared)
            require(low["settings"] == high["settings"] and low["basis"] == high["basis"]
                    and low["input_exact_rational"] == high["input_exact_rational"], "precision captures differ in input or layout")
            q = shared.scale(fixture["samples"][0], 6)
            originals = [compare_original(record, case, q, shared) for record in [low, high] for case in cases]
            convergence = compare_precisions(low, high, q, shared)
            poles = [pole_diagnostics(record, shared) for record in [low, high]]
            oracle_comparisons = compare_oracles([low, high], oracles, q, shared)
            real_zero = real_zero_diagnostics([low, high], q, shared)
        for path, digest in inputs.items():
            require(sha(path) == digest, f"artifact changed during diagnostics: {path}")
        report.update(status="completed_diagnostic", exact_gate=exact_gate, original_mode_comparisons=originals,
            precision_comparison=convergence, pole_diagnostics=poles, failure_audit_path=failure_audit,
            saved_parameter_oracle=oracle_comparisons,
            supplemental_summary_path=protocol["supplemental_summary_path"],
            analytic_real_zero_diagnostics=real_zero, audit_manifest_path=protocol["audit_manifest_path"],
            original_complex_comparisons=sum(r["compared_complex_slots"] for r in originals),
            convergence_complex_comparisons=convergence["compared_complex_slots"],
            decimal_working_digits=200, natural_scale=str(q), normalized_original_tolerance="1e-10",
            convergence_tolerance="2^-80", declared_runtime_bound_seconds=300,
            runtime_elapsed_seconds=run["elapsed_seconds"],
            normalization="Q^(4-2N+moment rank); complex norm / max(1, normalized reference norm)",
            conclusion="Diagnostic measurements only. The unchanged original128 acceptance gate remains failed; no acceptance is upgraded.")
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
    report["input_sha256"] = inputs
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(OUTPUT), "status": report["status"], "acceptance_qualified": False}))
    return 0 if report["status"] == "completed_diagnostic" else 1


if __name__ == "__main__":
    sys.exit(main())

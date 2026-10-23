#!/usr/bin/env python3
"""Unrun v2 gate: exact-002 under 180 seconds, unchanged frozen build-001.

Accepts `128` for a first-array inspection, or `128 256` for convergence.
The separate exact-001 30-second resource timeout remains mandatory history.
Numeric captures still use the original run.py, build and 180-second protocol.
No diagnostic phase-copy result substitutes for any of the 14 exact tests.
This program never launches a numerical executable.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import sys

R = Path(__file__).resolve().parents[3]
H = R / "target/public-highpoint/thin-n6-mask"
B = H / "build-001"
C = H / "core"
FIXTURE = R / "validation/public-highpoint/fixture-conditioned_masses.json"
REFERENCE = R / "validation/public-highpoint/reference-conditioned_masses.json"
SHARED = R / "validation/public-highpoint/compare_public.py"
PINS = {
    B / "build.json": "1acf6dd8e08223f86db5cc7dbdd254f2ecccb044a84fad627393aea514525f57",
    H / "source-review.json": "7eebb1aa530557ba7638c107c979e2ae403b357317f9191d88325e01acd7d9f6",
    H / "base.json": "19221afd3f0f62fd33ec02b365127913311fe31dd8fbc4e59a94aef6cd257b94",
    H / "run.py": "676f246c4c7b6b5a87d6f41954120fe495fd3102407480c2246817b0537cfa49",
    H / "run-full-exact-v2.py": "3115f2794b46d23d85ccfcca392c330106a6d5b08d245ab074af2d21deb0a3dd",
    H / "compare.py": "ccc25d3578721688590275aaed82c5fc556bfc645d0d5eda6bbf15e5647587c3",
    H / "exact-001/run.json": "d95a1867274970208b7fa919b2678b76091864281929ee432587354aa91af634",
    H / "exact-001/step-0.log": "f71b084e80f1991552fe82b12cc4cc58e3adecc0450a771f67b49f6fe8a8998d",
    SHARED: "bd7139b6f846b69706a89c6c72e426605aebd5fa4ffbb75dcf1bcfb83c04da9d",
    FIXTURE: "ec27f2c5774a18d3d84d2d733e634dae93e9bd4c74523d6f77e8784d13421ada",
    REFERENCE: "9bc3f10ad27615f23ddb3c2f62169575378d32e6c35c9d2a9dd51223f9b39ec4",
}
ENVIRONMENT = {
    "RAYON_NUM_THREADS": "1", "RUST_TEST_THREADS": "1",
    "IREGI_PREPARATION_PROFILE": "1", "IREGI_PV_PREPARATION_PROFILE": "1",
}
SETTINGS = dict(propagators=6, rank=2, powers=[1] * 6, dimension_shift=0,
                algorithm="PassarinoVeltman", convention="IregiNative",
                tensor_weights="Components", invariants="FromShifts", input_policy="Preserve")
EXACT_TESTS = {
    "planar_mask": {
        "certified_planar::tests::planar_mask_certificates_keep_mixed_only_children_and_lane_order",
        "certified_planar::tests::planar_mask_unresolved_proof_retains_child_and_harvests_attempts",
        "certified_planar::tests::planar_mask_full_mask_and_invalid_batch_reset_fail_closed",
        "certified_planar::tests::planar_mask_plan_cache_separates_masks_charts_and_ordered_shapes",
        "pv::planar_mask_polynomial_tests::all_chart_cramer_numerators_match_existing_solve",
        "pv::planar_mask_polynomial_tests::private_mask_rejects_invalid_bits_and_omits_child_before_recursion",
        "plan::planar_mask_variant_tests::mask_identity_survives_analytic_variant_rebuild_and_cache",
    },
    "thin_n6::tests": {
        "thin_n6::tests::actual_assembly_all_slots_and_mixed_dual_sentinels",
        "thin_n6::tests::five_rhs_integrand_identities_keep_dimensionally_regulated_denominators",
    },
    "types::primal_envelope_tests": {
        "types::primal_envelope_tests::private_envelope_scatter_preserves_every_slot_and_route",
        "types::primal_envelope_tests::private_envelope_replacement_clears_missing_failed_and_quadrature_context",
        "types::primal_envelope_tests::private_envelope_rejects_equal_size_different_shape_basis_and_convention",
        "types::primal_envelope_tests::private_envelope_rejects_stale_values_sparse_maps_and_nonfinite_amplitudes",
        "types::primal_envelope_tests::private_envelope_preserves_operand_precision_and_binds_returned_precision",
    },
}
SCOPE = ("Private thin N6 rank2, retained base fixture, native Components, requested53. "
         "Every successful capture must contain 15 moments x 4 complex Laurent slots. "
         "No production adoption, broad-domain, N7, rank7, lifecycle or performance qualification. "
         "Working precision is representation precision, not proof of achieved accuracy.")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def bind(path, inputs, expected=None):
    path = Path(path).resolve()
    digest = sha(path)
    require(expected is None or digest == expected, f"changed artifact: {path}")
    require(str(path) not in inputs or inputs[str(path)] == digest, f"artifact changed during comparison: {path}")
    inputs[str(path)] = digest
    return digest


def inventory(actual, expected, label):
    require(actual == expected, f"{label} inventory or hashes differ")


def validate_build(inputs):
    for path, expected in PINS.items():
        bind(path, inputs, expected)
    build = read(B / "build.json")
    require(build.get("status") == "passed" and build.get("inputs_unchanged") is True,
            "build is incomplete or its inputs changed")
    require(build.get("bound_seconds") == 180 and set(build.get("outputs", {})) ==
            {"libiregi_rust.rlib", "tests", "driver"}, "wrong build protocol or outputs")
    require([s.get("name") for s in build.get("steps", [])] == ["core", "tests", "driver"]
            and all(s.get("exit_code") == 0 and not s.get("timeout") for s in build["steps"]),
            "missing successful build steps")
    expected = {}
    for path in [R / "target/e6-direct-n2/preparation.json",
                 R / "target/core-fused-cse-census/supplemental-deps.json"]:
        bind(path, inputs)
        expected[str(path)] = sha(path)
        for entry in read(path)["files"]:
            name = str((R / entry["frozen"]).resolve())
            require(name not in expected, "duplicate frozen dependency")
            expected[name] = entry["sha256"]
    for directory, suffixes in [(R / "target/e6-direct-n2/deps", {".rlib", ".so"}),
                                (R / "target/core-fused-cse-census/supplemental-deps", {".rlib", ".so"}),
                                (R / "target/e6-direct-n2/native", {".a", ".so"})]:
        observed = {str(p.resolve()) for p in directory.rglob("*") if p.is_file() and p.suffix in suffixes}
        retained = {name for name in expected if Path(name).parent == directory and Path(name).suffix in suffixes}
        require(observed == retained, f"dependency search-directory inventory differs: {directory}")
    for path in [p for p in C.rglob("*") if p.is_file()]:
        expected[str(path)] = sha(path)
    for name in ["base.json", "driver.rs", "build.py", "source-review.json"]:
        expected[str(H / name)] = sha(H / name)
    compiler = Path(build["compiler_path"])
    require(compiler.is_absolute(), "compiler identity is not absolute")
    expected[str(compiler)] = sha(compiler)
    for path in (R / "crates/iregi-rust/src").rglob("*.rs"):
        expected[str(path)] = sha(path)
    inventory(build["inputs"], expected, "complete build input")
    for name, expected_sha in build["inputs"].items():
        bind(name, inputs, expected_sha)
    for name, expected_sha in build["outputs"].items():
        bind(B / name, inputs, expected_sha)
    for step in build["steps"]:
        bind(B / (step["name"] + ".log"), inputs)
    base, review = read(H / "base.json"), read(H / "source-review.json")
    base_qualification = R / base["qualification"]
    bind(base_qualification, inputs, base["qualification_sha256"])
    prior = read(base_qualification)
    require(prior["status"] == "first_numerical_probe_rejected" and prior["exact_tests"] == 7
            and prior["compared_numerical_slots"] == 0, "historical failure scope changed")
    require(review["status"] == "approved_source_only_for_bounded_private_gate", "source review is missing")
    approved = {"pv.rs", "plan.rs", "certified_planar.rs", "certified_planar/mask_tests.rs"}
    require(set(review["approved_delta"]) == approved, "unreviewed source delta")
    frozen = {str(p.relative_to(C)): sha(p) for p in C.rglob("*") if p.is_file()}
    require(set(frozen) == set(base["source"]) | {"crates/iregi-rust/src/certified_planar/mask_tests.rs"},
            "frozen source inventory differs from reviewed base")
    for name, digest in base["source"].items():
        if name.removeprefix("crates/iregi-rust/src/") not in approved:
            require(frozen[name] == digest, f"unreviewed source changed: {name}")
    inventory(review["sources"], {str(p.relative_to(R)): sha(p)
              for p in (C / "crates/iregi-rust/src").rglob("*.rs")}, "source review")
    return build


def expected_run_inputs(build, runner, predecessors=()):
    expected = dict(build["inputs"])
    expected.update({str(B / name): digest for name, digest in build["outputs"].items()})
    expected.update({str(B / "build.json"): sha(B / "build.json"),
                     str(runner): sha(runner), str(FIXTURE): sha(FIXTURE)})
    expected.update({str(path): sha(path) for path in predecessors})
    return expected


def validate_run(directory, build, commands, expected_outputs, bound, inputs,
                 runner=None, predecessors=()):
    path = directory / "run.json"
    bind(path, inputs)
    run = read(path)
    require(run.get("status") == "passed" and run.get("inputs_unchanged") is True,
            f"run is incomplete, failed or timed out: {directory}")
    require(run.get("bound_seconds") == bound and run.get("environment_additions") == ENVIRONMENT,
            "run bound or environment differs from reviewed protocol")
    expected = expected_run_inputs(build, H / "run.py" if runner is None else runner, predecessors)
    inventory(run["inputs"], expected, "complete run input")
    require([s.get("command") for s in run.get("steps", [])] == commands,
            "run commands or step count differ")
    require(all(s.get("exit_code") == 0 and not s.get("timeout") and
                isinstance(s.get("seconds"), (int, float)) and 0 <= s["seconds"] <= bound
                for s in run["steps"]), "run step failed or exceeded process bound")
    require(sum(s["seconds"] for s in run["steps"]) <= bound, "combined process bound exceeded")
    require(set(run.get("outputs", {})) == expected_outputs, "run output inventory differs")
    for name, digest in run["outputs"].items():
        bind(directory / name, inputs, digest)
    return run


def validate_test_log(text, names):
    starts = re.findall(r"^running (\d+) tests?$", text, re.M)
    require(starts == [str(len(names))], "exact test count is missing or incorrect")
    completed, pending = [], None
    for line in text.splitlines():
        match = re.match(r"^test ([A-Za-z0-9_:]+) \.\.\.\s*(.*)$", line)
        if match:
            require(pending is None, "previous exact test never completed")
            pending, tail = match.groups()
            if tail == "ok":
                completed.append(pending)
                pending = None
            elif tail in {"FAILED", "ignored"}:
                raise ValueError("exact test failed or was ignored")
        elif line.strip() == "ok":
            require(pending is not None, "unbound exact test completion")
            completed.append(pending)
            pending = None
    require(pending is None and len(completed) == len(names) and set(completed) == names,
            "exact test membership is incomplete, duplicated or unexpected")
    summaries = re.findall(r"^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; \d+ filtered out;", text, re.M)
    require(summaries == [(str(len(names)), "0", "0", "0")], "exact test summary is incomplete")


def validate_predecessor(build, inputs):
    directory = H / "exact-001"
    run = read(directory / "run.json")
    require(run.get("status") == "failed" and run.get("inputs_unchanged") is True
            and run.get("bound_seconds") == 30 and run.get("environment_additions") == ENVIRONMENT,
            "original exact-001 resource timeout changed")
    inventory(run["inputs"], expected_run_inputs(build, H / "run.py"), "predecessor run input")
    expected = ["taskset", "-c", "14", str(B / "tests"), "planar_mask", "--nocapture", "--test-threads=1"]
    require(len(run.get("steps", [])) == 1 and run["steps"][0].get("command") == expected
            and run["steps"][0].get("exit_code") is None and run["steps"][0].get("timeout") is True,
            "predecessor is not the retained first-step resource timeout")
    require(set(run.get("outputs", {})) == {"step-0.log"}, "predecessor output inventory differs")
    bind(directory / "step-0.log", inputs, run["outputs"]["step-0.log"])
    log = (directory / "step-0.log").read_text()
    require("running 7 tests" in log and "test result:" not in log
            and not re.search(r"(?:^|\.\.\.\s*)ok$", log, re.M),
            "predecessor unexpectedly records a completed test")
    return {"attempt": "exact-001", "status": "resource_timeout", "completed_tests": 0,
            "declared_bound_seconds": 30, "elapsed_seconds": run["elapsed_seconds"],
            "process_seconds": run["steps"][0]["seconds"], "counts_toward_exact_gate": False}


def diagnostic_context(inputs):
    # Optional contextual evidence only. Its one instrumented test cannot
    # satisfy the unchanged-build gate, regardless of its recorded status.
    path = R / "target/public-highpoint/thin-n6-mask-phase/phase-001/diagnostic-summary.json"
    if not path.exists():
        return None
    bind(path, inputs, "07ad30a8fe3350161a23abe9a66fdff4532d27c58123559e9ff5533a12d6941c")
    summary = read(path)
    for name, digest in summary["artifacts"].items():
        bind(R / name, inputs, digest)
    return {"summary_sha256": sha(path), "recorded_status": summary["status"],
            "scope": summary["scope"], "counts_toward_exact_gate": False,
            "qualification_use": "context only; complete phase dependency closure not requalified here"}


def validate_exact(build, inputs):
    predecessor = validate_predecessor(build, inputs)
    directory = H / "exact-002"
    commands = [["taskset", "-c", "14", str(B / "tests"), name, "--nocapture", "--test-threads=1"]
                for name in EXACT_TESTS]
    predecessors = [H / "run.py", H / "exact-001/run.json", H / "exact-001/step-0.log"]
    run = validate_run(directory, build, commands, {f"step-{i}.log" for i in range(3)}, 180,
                       inputs, runner=H / "run-full-exact-v2.py", predecessors=predecessors)
    require(run.get("protocol_version") == 2, "exact run is not the separately versioned v2 protocol")
    for i, names in enumerate(EXACT_TESTS.values()):
        validate_test_log((directory / f"step-{i}.log").read_text(), names)
    return {"attempt": "exact-002", "protocol_version": 2,
            "new_mask_tests": 7, "retained_parent_tests": 2, "retained_envelope_tests": 5,
            "total_tests": 14, "declared_bound_seconds": 180, "elapsed_seconds": run["elapsed_seconds"],
            "retained_predecessor": predecessor, "phase_diagnostic_context": diagnostic_context(inputs)}


def validate_array(record, bits, fixture, shared):
    require(record.get("schema_version") == 1 and record.get("status") == "all_lanes_success"
            and record.get("settings") == SETTINGS and record.get("working_bits") == bits
            and record.get("requested_bits") == 53 and record.get("rows") == 1
            and record.get("components") == 1 and record.get("fixture") == str(FIXTURE)
            and record.get("lane_statuses") == ["Success"]
            and record.get("basis") == shared.canonical_basis(2), "unsupported or incomplete tensor result")
    require(record.get("algorithm_used") == "PassarinoVeltman", "unexpected parent algorithm")
    for key in ["fallback_used", "analytic_used"]:
        require(isinstance(record.get(key), list) and len(record[key]) == 1
                and type(record[key][0]) is bool, f"invalid {key} flags")
    sample = fixture["samples"][0]
    require(sample["id"] == "base", "retained base fixture order changed")
    ps = sample["propagators"][:6]
    expected = [[str(Fraction(v)), "0"] for p in ps for v in p["shift"]]
    expected += [[str(Fraction(v)) for v in p["mass_squared"]] for p in ps]
    expected += [[str(Fraction(sample["mu"])), "0"]]
    require(record.get("input_exact_rational") == [expected], "exact represented inputs differ")
    execution = record["execution"]
    for key, value in dict(parent_input_rows=1, child_batch_calls=1, packed_child_rows=6,
                           parent_batch_calls=1, packed_parent_rows=1).items():
        require(execution.get(key) == value, f"batch execution count differs: {key}")
    lanes = record.get("lanes")
    require(isinstance(lanes, list) and len(lanes) == 1 and lanes[0].get("row") == 0
            and lanes[0].get("status") == "Success", "lane identity differs")
    moments = lanes[0].get("moments")
    require(isinstance(moments, list) and len(moments) == 15, "expected all 15 tensor moments")
    for moment in moments:
        require(isinstance(moment, list) and len(moment) == 4, "expected four native Laurent slots")
        for slot in moment:
            require(set(slot) == {"real", "imaginary", "real_precision", "imaginary_precision"},
                    "coefficient representation or precision metadata is incomplete")
            for component in ["real", "imaginary"]:
                value = shared.decimal_rational(slot[component])
                precision = slot[component + "_precision"]
                require(value.is_finite() and type(precision) is int and precision >= 0
                        and (value == 0 or precision > 0), "nonfinite or invalid precision coefficient")


def main(arguments):
    require(arguments in [["128"], ["128", "256"]], "usage: compare-v2.py 128 [256]")
    output = H / ("comparison-v2-" + "-".join(arguments) + ".json")
    require(not output.exists(), "comparison output already exists; retained evidence is immutable")
    inputs = {}
    report = dict(status="failed", protocol_version=2, scope=SCOPE, full_array_original_agreement_qualified=False,
                  precision_convergence_qualified=False, lifecycle_qualified=False)
    try:
        bind(Path(__file__), inputs)
        build = validate_build(inputs)
        spec = importlib.util.spec_from_file_location("thin_mask_shared_comparator", SHARED)
        shared = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(shared)
        fixture, reference = read(FIXTURE), read(REFERENCE)
        shared.validate_reference(reference, fixture, sha(FIXTURE))
        bind(R / "target/reference/iregi-reference-original", inputs, reference["executable_sha256"])
        history_path = R / "validation/public-highpoint/qualification.json"
        bind(history_path, inputs)
        history = read(history_path)
        for path in [FIXTURE, REFERENCE]:
            require(history["artifacts"][path.name] == sha(path), "historical reference binding differs")
        cases = [case for case in reference["cases"] if case["id"] == "n6_base_mode0"]
        require(len(cases) == 1 and cases[0]["status"] == "captured" and cases[0]["mode"] == 0
                and cases[0]["response"]["stable"] is True, "untouched original IBP reference is not stable")
        report["exact_gate"] = validate_exact(build, inputs)
        records, arrays = [], []
        for text_bits in arguments:
            bits = int(text_bits)
            directory = H / f"n6-rank2-{bits}-001"
            commands = [["taskset", "-c", "14", str(B / "driver"), str(FIXTURE),
                         "6", "2", "pv", text_bits, "53", "1", str(directory / "result.json")]]
            run = validate_run(directory, build, commands, {"result.json", "step-0.log"}, 180, inputs)
            result = read(directory / "result.json")
            with localcontext() as context:
                context.prec = 180
                validate_array(result, bits, fixture, shared)
                q, errors, poles = shared.scale(fixture["samples"][0], 6), [], 0
                for index, monomial in enumerate(result["basis"]):
                    natural = q ** (sum(monomial) - 8)
                    for pole, slot in enumerate(result["lanes"][0]["moments"][index]):
                        actual = tuple(shared.decimal_rational(slot[k]) / natural for k in ["real", "imaginary"])
                        original = tuple(Decimal(str(x)) / natural for x in cases[0]["response"]["moments"][index][pole])
                        error = shared.norm(tuple(a - b for a, b in zip(actual, original))) / max(Decimal(1), shared.norm(original))
                        require(error <= Decimal("1e-10"), f"original disagreement at moment {index}, slot {pole}: {error}")
                        errors.append(error)
                        if pole < 3:
                            require(actual == (Decimal(0), Decimal(0)), f"nonzero pole at moment {index}, slot {pole}")
                            poles += 1
                require(len(errors) == 60 and poles == 45, "full slot coverage is incomplete")
                records.append(dict(working_bits=bits, complex_slots=60, real_components=120,
                                    exact_zero_complex_poles=45, maximum_original_error=str(max(errors)),
                                    declared_bound_seconds=180, elapsed_seconds=run["elapsed_seconds"],
                                    fallback_used=result["fallback_used"], analytic_used=result["analytic_used"]))
            arrays.append(result)
        convergence = None
        if len(arrays) == 2:
            with localcontext() as context:
                context.prec = 180
                q, errors = shared.scale(fixture["samples"][0], 6), []
                for index, monomial in enumerate(arrays[0]["basis"]):
                    natural = q ** (sum(monomial) - 8)
                    for pole in range(4):
                        pair = [tuple(shared.decimal_rational(a["lanes"][0]["moments"][index][pole][k]) / natural
                                      for k in ["real", "imaginary"]) for a in arrays]
                        errors.append(shared.norm(tuple(a - b for a, b in zip(*pair))) / max(Decimal(1), shared.norm(pair[1])))
                require(len(errors) == 60 and max(errors) <= Decimal(2) ** -80, "128/256 convergence gate failed")
                convergence = str(max(errors))
        # Recheck every bound artifact after parsing and numerical comparison.
        for path, digest in inputs.items():
            require(sha(path) == digest, f"artifact changed during comparison: {path}")
        report.update(status="passed", records=records, full_array_original_agreement_qualified=True,
                      precision_convergence_qualified=len(arrays) == 2,
                      normalized_original_tolerance="1e-10", convergence_tolerance="2^-80" if len(arrays) == 2 else None,
                      maximum_precision_difference=convergence,
                      normalization="Q^(4-2N+rank); complex norm / max(1, normalized reference norm)",
                      historical_unmasked_numeric_status="first_numerical_probe_rejected")
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
    report["input_sha256"] = inputs
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(output), "status": report["status"], "scope": SCOPE}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

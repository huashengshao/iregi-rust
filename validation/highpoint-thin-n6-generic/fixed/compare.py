#!/usr/bin/env python3
"""Source-reviewed private N6 rank3 gate; never launches a compiler or integral.

Usage: compare.py 128 [256]. Requires the reviewed numerical protocol and all
25 exact tests; the failed original generic build remains bound history.
A single successful array qualifies original agreement, never convergence.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import re
import sys

R = Path(__file__).resolve().parents[3]
H = R / "target/public-highpoint/thin-n6-generic-fixed"
B, C = H / "build-001", H / "core"
PROTOCOL = H / "numerical-protocol.json"
FIXTURE = R / "validation/public-highpoint/fixture-conditioned_masses.json"
REFERENCE = R / "validation/public-highpoint/reference-conditioned_masses.json"
SHARED = R / "validation/public-highpoint/compare_public.py"
PINS = {
    H / "proposed-protocol.json": "69cda793aa2bf9c0e7b48fa4e079c002b4ff23ad162b6ad07ce1b7fd4a414e4c",
    H / "source-review.json": "7db1c2b0db02f65af824ee585dc06920a90684ea57373017072b4b7b1f603a1b",
    H / "base.json": "b86482bd0d65c39c3b3f00fc100db1a7970e7cc6323c72416fed8749b2e50fd5",
    H / "test-fix.json": "b7a594ca5d42de886fd254d3db1bcb44a394635dd4f4d63438e031cfd1d1f331",
    SHARED: "bd7139b6f846b69706a89c6c72e426605aebd5fa4ffbb75dcf1bcfb83c04da9d",
    FIXTURE: "ec27f2c5774a18d3d84d2d733e634dae93e9bd4c74523d6f77e8784d13421ada",
    REFERENCE: "9bc3f10ad27615f23ddb3c2f62169575378d32e6c35c9d2a9dd51223f9b39ec4",
}
ENVIRONMENT = {"RAYON_NUM_THREADS": "1", "RUST_TEST_THREADS": "1",
               "IREGI_PREPARATION_PROFILE": "1", "IREGI_PV_PREPARATION_PROFILE": "1"}
SETTINGS = dict(propagators=6, rank=3, powers=[1]*6, dimension_shift=0,
                algorithm="PassarinoVeltman", convention="IregiNative",
                tensor_weights="Components", invariants="FromShifts", input_policy="Preserve")
SCOPE = ("Private generic thin N6 rank3, retained base fixture, native Components, requested53. "
         "Every successful capture contains 35 moments x 4 complex Laurent slots. "
         "No production adoption, broader-domain, N7, rank7-numerical, Dual-numerical, "
         "lifecycle or performance qualification. Working precision is not achieved accuracy.")

EXACT_TESTS = {'generic_thin': {'plan::generic_thin_variant_tests::thin_variant_rebuild_retains_imported_topology_and_native_output_context',
                  'thin_n6::generic_tests::generic_thin_all_ranks_all_native_slots_follow_dynamic_child_basis',
                  'thin_n6::generic_tests::generic_thin_borrowed_dual_preserves_ordered_shape_and_rejects_bad_metadata',
                  'thin_n6::generic_tests::generic_thin_complete_result_layout_rejects_malformed_buffers_and_shapes',
                  'thin_n6::generic_tests::generic_thin_external_amplitudes_keep_child_dimensions_and_slot_identity',
                  'thin_n6::generic_tests::generic_thin_final_uv_rule_preserves_ir_and_finite_and_the_boundary',
                  'thin_n6::generic_tests::generic_thin_integrand_identity_all_rank_seven_moments_and_routings',
                  'thin_n6::generic_tests::generic_thin_mixed_taylor_and_odd_rank_outputs_keep_raw_components',
                  'thin_n6::generic_tests::generic_thin_rejects_unsupported_callers_before_geometry',
                  'thin_n6::generic_tests::generic_thin_uv_cancellation_uses_nonzero_child_poles_all_ranks'},
 'planar_mask': {'certified_planar::tests::planar_mask_certificates_keep_mixed_only_children_and_lane_order',
                 'certified_planar::tests::planar_mask_full_mask_and_invalid_batch_reset_fail_closed',
                 'certified_planar::tests::planar_mask_plan_cache_separates_masks_charts_and_ordered_shapes',
                 'certified_planar::tests::planar_mask_unresolved_proof_retains_child_and_harvests_attempts',
                 'plan::planar_mask_variant_tests::mask_identity_survives_analytic_variant_rebuild_and_cache',
                 'pv::planar_mask_polynomial_tests::all_chart_cramer_numerators_match_existing_solve',
                 'pv::planar_mask_polynomial_tests::private_mask_rejects_invalid_bits_and_omits_child_before_recursion'},
 'thin_n6::tests': {'thin_n6::tests::actual_assembly_all_slots_and_mixed_dual_sentinels',
                    'thin_n6::tests::five_rhs_integrand_identities_keep_dimensionally_regulated_denominators'},
 'types::primal_envelope_tests': {'types::primal_envelope_tests::private_envelope_preserves_operand_precision_and_binds_returned_precision',
                                  'types::primal_envelope_tests::private_envelope_rejects_equal_size_different_shape_basis_and_convention',
                                  'types::primal_envelope_tests::private_envelope_rejects_stale_values_sparse_maps_and_nonfinite_amplitudes',
                                  'types::primal_envelope_tests::private_envelope_replacement_clears_missing_failed_and_quadrature_context',
                                  'types::primal_envelope_tests::private_envelope_scatter_preserves_every_slot_and_route'},
 'plan::tests::final_uv_power_counting_preserves_ir_and_dimension_shifted_residues': {'plan::tests::final_uv_power_counting_preserves_ir_and_dimension_shifted_residues'}}

def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def inventory(actual, expected, label):
    require(actual == expected, f"{label} inventory or hashes differ")


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


def bind(path, inputs, expected=None):
    path = Path(path).resolve()
    # Hash each distinct input once here and again at the final boundary.
    digest = inputs.get(str(path))
    if digest is None:
        digest = sha(path)
        inputs[str(path)] = digest
    require(expected is None or digest == expected, f"changed artifact: {path}")
    return digest


def protocol_artifact_paths():
    names = ["compare.py", "run-numeric.py", "build-001/build.json", "exact-001/run.json",
             *[f"exact-001/step-{i}.log" for i in range(5)], "proposed-protocol.json",
             "source-review.json", "base.json", "test-fix.json", "driver.rs", "run.py"]
    return [H / name for name in names] + [FIXTURE, REFERENCE, SHARED]


def validate_numerical_protocol(inputs):
    bind(PROTOCOL, inputs)
    protocol = read(PROTOCOL)
    require(protocol.get("schema_version") == 1
            and protocol.get("source_review_status") == "approved_source_only"
            and "/root" in protocol.get("reviewers", []), "numerical protocol lacks ROOT source review")
    required = dict(rank=3, propagators=6, working_bits=[128, 256], requested_bits=53,
                    fixture_rows=[0], moments=35, native_complex_slots=140,
                    runtime_bound_seconds=180, normalized_original_tolerance="1e-10",
                    convergence_tolerance="2^-80")
    require(all(protocol.get(k) == v for k, v in required.items()), "numerical protocol scope differs")
    expected = {str(p.relative_to(R)): bind(p, inputs) for p in protocol_artifact_paths()}
    inventory(protocol.get("artifacts"), expected, "reviewed numerical protocol")
    return protocol


def validate_build(inputs):
    for path, digest in PINS.items():
        bind(path, inputs, digest)
    proposed, review, base = [read(H / name) for name in
                              ["proposed-protocol.json", "source-review.json", "base.json"]]
    require(proposed["build_bound_seconds"] == proposed["exact_bound_seconds"] == 180
            and proposed["exact_expected_tests"] == 25, "build/exact proposal differs")
    require(review["status"] == "approved_source_only_for_reviewed_bounded_gate"
            and proposed["source_review_sha256"] == bind(H / "source-review.json", inputs),
            "frozen source review differs")
    frozen = {str(p.relative_to(H)): bind(p, inputs) for p in C.rglob("*") if p.is_file()}
    inventory(proposed["source_sha256"], frozen, "complete reviewed source")
    for name, digest in proposed["script_sha256"].items():
        bind(H / name, inputs, digest)
    require(set(proposed["script_sha256"]) == {"build.py", "run.py", "driver.rs"}, "script inventory differs")
    changed = {"crates/iregi-rust/src/plan.rs", "crates/iregi-rust/src/thin_n6.rs",
               "crates/iregi-rust/src/thin_n6/generic_tests.rs"}
    require(set(review["changed_source"]) == changed, "unreviewed generic source change")
    require(set(frozen) == {"core/" + n for n in base["source"]}
            | {"core/crates/iregi-rust/src/thin_n6/generic_tests.rs"}, "generic source inventory differs")
    for name, digest in base["source"].items():
        if name not in changed:
            require(frozen["core/" + name] == digest, f"unreviewed base source change: {name}")
    inventory(review["changed_source"], {n: frozen["core/" + n] for n in changed}, "reviewed delta")
    base_path = R / base["qualification_path"]
    bind(base_path, inputs, base["qualification_sha256"])
    require(base["qualification_sha256"] == "6ef88dfd99a32746f641b2485b2cd95b7bddfd186dc45148287874af764f4357"
            and proposed["base_qualification_sha256"] == base["qualification_sha256"], "qualified base differs")
    qualified = read(base_path)
    require(qualified["status"] == "private_retained_n6_rank2_qualified", "base is not the qualified private mask")
    for name in ["archive-manifest.json", "sources.tar.gz"]:
        bind(base_path.parent / name, inputs, qualified["files"][name])
    archive = read(base_path.parent / "archive-manifest.json")
    inventory(base["source"], {n.removeprefix("mask/"): h for n, h in archive["members"].items()
                              if n.startswith("mask/")}, "qualified base source archive")
    # Keep the rejected original compile as a different immutable attempt.
    fix = read(H / "test-fix.json")
    predecessor = R / fix["failed_build_path"]
    bind(predecessor, inputs, fix["failed_build_sha256"])
    failed = read(predecessor)
    require(failed["status"] == "failed" and [s["name"] for s in failed["steps"]] == ["core", "tests"]
            and failed["steps"][0]["exit_code"] == 0 and failed["steps"][1]["exit_code"] != 0,
            "original test-only compilation failure is not retained")
    for name in ["core.log", "tests.log"]:
        bind(predecessor.parent / name, inputs)
    bind(predecessor.parent.parent / "proposed-protocol.json", inputs, fix["frozen_parent_protocol_sha256"])
    require(review["test_fix_sha256"] == proposed["test_fix_sha256"] == bind(H / "test-fix.json", inputs),
            "test correction provenance differs")
    require(fix["after_plan_sha256"] == frozen["core/crates/iregi-rust/src/plan.rs"], "test correction source differs")
    bind(B / "build.json", inputs)
    build = read(B / "build.json")
    require(build.get("status") == "passed" and build.get("inputs_unchanged") is True
            and build.get("bound_seconds") == 180, "fixed build is not guarded and successful")
    require([s.get("name") for s in build.get("steps", [])] == ["core", "tests", "driver"]
            and all(s.get("exit_code") == 0 and not s.get("timeout") for s in build["steps"]),
            "build has incomplete or failed steps")
    require(set(build.get("outputs", {})) == {"libiregi_rust.rlib", "tests", "driver"}, "build outputs differ")
    dependency = R / "target/e6-direct-n2/deps"
    supplemental = R / "target/core-fused-cse-census/supplemental-deps"
    native = R / "target/e6-direct-n2/native"
    externs = {
        "iregi_masters": dependency / "libiregi_masters-f07797f04e91954e.rlib",
        "symbolica": dependency / "libsymbolica-06e42762cabb77d9.rlib",
        "serde": dependency / "libserde-b04ba25115fa19f8.rlib",
        "serde_json": dependency / "libserde_json-d657c5438f354a41.rlib",
        "thiserror": supplemental / "libthiserror-0527e2191ec3561c.rlib",
    }
    common = ["taskset", "-c", "14,15", "rustc", "--edition=2024", "-C", "opt-level=0",
              "-C", "debuginfo=0", "-C", "strip=debuginfo", "-L", f"dependency={dependency}",
              "-L", f"dependency={supplemental}", "-L", f"native={native}"]
    external_arguments = [arg for name, path in externs.items() for arg in ["--extern", f"{name}={path}"]]
    commands = [common + ["--crate-name", "iregi_rust", "--crate-type", "rlib",
                str(C / "crates/iregi-rust/src/lib.rs"), "-o", str(B / "libiregi_rust.rlib")] + external_arguments,
                common + ["--crate-name", "iregi_rust", "--test", str(C / "crates/iregi-rust/src/lib.rs"),
                "-o", str(B / "tests")] + external_arguments,
                common + ["--crate-name", "thin_n6_driver", str(H / "driver.rs"), "-o", str(B / "driver"),
                "--extern", f"iregi_rust={B}/libiregi_rust.rlib"] +
                [arg for name in ["symbolica", "iregi_masters", "serde_json"]
                 for arg in ["--extern", f"{name}={externs[name]}"]]]
    require([s["command"] for s in build["steps"]] == commands, "build source or link command differs")
    expected = {}
    for path in [R / "target/e6-direct-n2/preparation.json",
                 R / "target/core-fused-cse-census/supplemental-deps.json"]:
        expected[str(path)] = bind(path, inputs)
        for entry in read(path)["files"]:
            name = str((R / entry["frozen"]).resolve())
            require(name not in expected, "duplicate dependency")
            expected[name] = entry["sha256"]
    for directory, suffixes in [(R / "target/e6-direct-n2/deps", {".rlib", ".so"}),
                                (R / "target/core-fused-cse-census/supplemental-deps", {".rlib", ".so"}),
                                (R / "target/e6-direct-n2/native", {".a", ".so"})]:
        actual = {str(p.resolve()) for p in directory.rglob("*") if p.is_file() and p.suffix in suffixes}
        retained = {n for n in expected if Path(n).parent == directory and Path(n).suffix in suffixes}
        require(actual == retained, f"dependency directory differs: {directory}")
    expected.update({str(H / n): d for n, d in frozen.items()})
    for name in ["base.json", "driver.rs", "build.py", "source-review.json", "proposed-protocol.json", "test-fix.json"]:
        expected[str(H / name)] = bind(H / name, inputs)
    compiler = Path(build["compiler_path"])
    require(compiler.is_absolute(), "compiler path is not absolute")
    expected[str(compiler)] = bind(compiler, inputs)
    for path in (R / "crates/iregi-rust/src").rglob("*.rs"):
        expected[str(path)] = bind(path, inputs)
    inventory(build["inputs"], expected, "complete build input")
    for name, digest in expected.items():
        bind(name, inputs, digest)
    for name, digest in build["outputs"].items():
        bind(B / name, inputs, digest)
    for name in ["core.log", "tests.log", "driver.log"]:
        bind(B / name, inputs)
    return build


def exact_run_inputs(build):
    expected = dict(build["inputs"])
    expected.update({str(B / n): h for n, h in build["outputs"].items()})
    expected.update({str(p): sha(p) for p in [B / "build.json", H / "run.py", FIXTURE]})
    return expected


def validate_run(directory, expected, commands, outputs, inputs):
    bind(directory / "run.json", inputs)
    run = read(directory / "run.json")
    inventory(run["inputs"], expected, "complete runtime input")
    for name, digest in expected.items():
        bind(name, inputs, digest)
    require(set(run.get("outputs", {})) <= outputs, "unexpected runtime output")
    for name, digest in run.get("outputs", {}).items():
        bind(directory / name, inputs, digest)
    require(run.get("status") == "passed" and run.get("inputs_unchanged") is True
            and run.get("bound_seconds") == 180 and run.get("environment_additions") == ENVIRONMENT,
            "runtime failed, timed out or changed its guarded inputs")
    require([s.get("command") for s in run.get("steps", [])] == commands, "runtime commands differ")
    require(all(s.get("exit_code") == 0 and not s.get("timeout")
                and type(s.get("seconds")) in [int, float] and math.isfinite(s["seconds"])
                and 0 <= s["seconds"] <= 180 for s in run["steps"])
            and sum(s["seconds"] for s in run["steps"]) <= 180, "runtime process budget or completion differs")
    require(set(run["outputs"]) == outputs, "incomplete capture outputs")
    return run


def validate_exact(build, inputs):
    directory = H / "exact-001"
    commands = [["taskset", "-c", "14", str(B / "tests"), name, "--nocapture", "--test-threads=1"]
                for name in EXACT_TESTS]
    run = validate_run(directory, exact_run_inputs(build), commands,
                       {f"step-{i}.log" for i in range(5)}, inputs)
    for i, names in enumerate(EXACT_TESTS.values()):
        validate_test_log((directory / f"step-{i}.log").read_text(), names)
    return dict(attempt="exact-001", total_tests=25, generic_tests=10, mask_tests=7,
                parent_tests=2, envelope_tests=5, ordinary_uv_tests=1,
                declared_bound_seconds=180, elapsed_seconds=run["elapsed_seconds"],
                predecessor="original generic build failed at test compilation; no exact or numerical gate")


def validate_numeric(directory, bits, build, inputs):
    expected = exact_run_inputs(build)
    expected.update({str(p): sha(p) for p in [H / "exact-001/run.json",
                    *[H / f"exact-001/step-{i}.log" for i in range(5)],
                    H / "run-numeric.py", H / "compare.py", PROTOCOL, *protocol_artifact_paths()]})
    if bits == 256:
        previous_path = H / "comparison-128.json"
        bind(previous_path, inputs)
        previous = read(previous_path)
        require(previous.get("status") == "passed" and previous.get("full_array_original_agreement_qualified") is True
                and previous.get("precision_convergence_qualified") is False
                and [r.get("working_bits") for r in previous.get("records", [])] == [128]
                and previous.get("normalized_original_tolerance") == "1e-10"
                and previous.get("exact_gate", {}).get("total_tests") == 25,
                "256 run lacks successful prior128 original-reference qualification")
        require(previous.get("input_sha256"), "prior128 qualification has no provenance")
        for name, digest in previous["input_sha256"].items():
            require(name not in expected or expected[name] == digest, "prior128 provenance conflict")
            expected[name] = digest
        expected[str(previous_path)] = sha(previous_path)
    command = ["taskset", "-c", "14", str(B / "driver"), str(FIXTURE), "6", "3", "pv",
               str(bits), "53", "1", str(directory / "result.json")]
    return validate_run(directory, expected, [command], {"result.json", "step-0.log"}, inputs)

def validate_array(record, bits, fixture, shared):
    require(record.get("schema_version") == 1 and record.get("status") == "all_lanes_success"
            and record.get("settings") == SETTINGS and record.get("working_bits") == bits
            and record.get("requested_bits") == 53 and record.get("rows") == 1
            and record.get("components") == 1 and record.get("fixture") == str(FIXTURE)
            and record.get("lane_statuses") == ["Success"]
            and record.get("basis") == shared.canonical_basis(3), "unsupported or incomplete tensor result")
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
    require(isinstance(moments, list) and len(moments) == 35, "expected all 35 tensor moments")
    for moment in moments:
        require(isinstance(moment, list) and len(moment) == 4, "expected four native Laurent slots")
        for slot in moment:
            require(set(slot) == {"real", "imaginary", "real_precision", "imaginary_precision"},
                    "coefficient representation or precision metadata is incomplete")
            for component in ["real", "imaginary"]:
                require(isinstance(slot[component], str), "native output must be an exact rational string")
                value = shared.decimal_rational(slot[component])
                precision = slot[component + "_precision"]
                require(value.is_finite() and type(precision) is int and precision >= 0
                        and (value == 0 or precision > 0), "nonfinite or invalid precision coefficient")

def main(arguments):
    require(arguments in [["128"], ["128", "256"]], "usage: compare.py 128 [256]")
    output = H / ("comparison-" + "-".join(arguments) + ".json")
    require(not output.exists(), "comparison output already exists; retained evidence is immutable")
    inputs = {}
    report = dict(status="failed", protocol_version=1, scope=SCOPE, full_array_original_agreement_qualified=False,
                  precision_convergence_qualified=False, lifecycle_qualified=False)
    try:
        bind(Path(__file__), inputs)
        validate_numerical_protocol(inputs)
        build = validate_build(inputs)
        spec = importlib.util.spec_from_file_location("thin_generic_shared_comparator", SHARED)
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
            directory = H / f"n6-rank3-{bits}-001"
            run = validate_numeric(directory, bits, build, inputs)
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
                require(len(errors) == 140 and poles == 105, "full slot coverage is incomplete")
                records.append(dict(working_bits=bits, complex_slots=140, real_components=280,
                                    exact_zero_complex_poles=105, maximum_original_error=str(max(errors)),
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
                require(len(errors) == 140 and max(errors) <= Decimal(2) ** -80, "128/256 convergence gate failed")
                convergence = str(max(errors))
        # Recheck every bound artifact after parsing and numerical comparison.
        for path, digest in inputs.items():
            require(sha(path) == digest, f"artifact changed during comparison: {path}")
        report.update(status="passed", records=records, full_array_original_agreement_qualified=True,
                      precision_convergence_qualified=len(arrays) == 2,
                      normalized_original_tolerance="1e-10", convergence_tolerance="2^-80" if len(arrays) == 2 else None,
                      maximum_precision_difference=convergence,
                      normalization="Q^(4-2N+rank); complex norm / max(1, normalized reference norm)",
                      retained_rank2_base_status="private_retained_n6_rank2_qualified",
                      original_generic_build_status="test_compilation_failed")
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
    report["input_sha256"] = inputs
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(output), "status": report["status"], "scope": SCOPE}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

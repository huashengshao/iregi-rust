#!/usr/bin/env python3
"""Private rank7 full-array gate. Reads saved evidence; never launches runtime.

All 330 cumulative Cartesian moments and four native Laurent slots are required.
The existing 25 exact tests are reused only after reviewed instrumentation and
byte restoration against the durable generic source archive. No phase test run
or rank7 success is inferred from the historical rank3 qualification.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import difflib
import hashlib
import importlib.util
import json
import math
import re
import sys
import tarfile

R = Path(__file__).resolve().parents[3]
H = R / "target/public-highpoint/thin-n6-rank7-phase"
B, C = H / "build-001", H / "core"
BASE = R / "validation/highpoint-thin-n6-generic"
PROTOCOL = H / "protocol.json"
FIXTURE = R / "validation/public-highpoint/fixture-conditioned_masses.json"
REFERENCE = R / "validation/public-highpoint/reference-conditioned_masses.json"
SHARED = R / "validation/public-highpoint/compare_public.py"
REFERENCE_EXE = R / "target/reference/iregi-reference-original"
HISTORY = R / "validation/public-highpoint/qualification.json"
BASE_SHA = "79ccaaa6439fd6cc2307f0dc186b6c6fbf7ba4a1585177a6ceab360d53b74d34"
REVIEW_SHA = "94349a3b203b0a0cd9fbe56686a717da49bdb282c93b99a69073b1031c3cf158"
PINS = {
    BASE / "qualification.json": BASE_SHA,
    H / "instrumentation-independent-review.json": REVIEW_SHA,
    H / "copy-manifest.json": "c534a5af2ebf57defa6284a021ab01fc696101608f976cf47ac9c41799d5f413",
    H / "instrumentation-manifest.json": "896a4b323b459efd120332d86edf869a939c226e7cae1e1af64f1b6245c1d869",
    H / "instrumentation.patch": "214d94affa319fa59f890d3228bb80358279a479efc094eebeb71be3a637264d",
    FIXTURE: "ec27f2c5774a18d3d84d2d733e634dae93e9bd4c74523d6f77e8784d13421ada",
    REFERENCE: "9bc3f10ad27615f23ddb3c2f62169575378d32e6c35c9d2a9dd51223f9b39ec4",
    SHARED: "bd7139b6f846b69706a89c6c72e426605aebd5fa4ffbb75dcf1bcfb83c04da9d",
    REFERENCE_EXE: "8ee49ae42cb6994f4bd42ed3a3920152e767407ecdafd8986577d5496370a379",
}
ENVIRONMENT = {"RAYON_NUM_THREADS": "1", "RUST_TEST_THREADS": "1",
               "IREGI_PREPARATION_PROFILE": "1", "IREGI_PV_PREPARATION_PROFILE": "1"}
SETTINGS = dict(propagators=6, rank=7, powers=[1]*6, dimension_shift=0,
                algorithm="PassarinoVeltman", convention="IregiNative",
                tensor_weights="Components", invariants="FromShifts", input_policy="Preserve")
SCOPE = ("Private instrumented thin N6 rank7, retained base singleton, native Components, requested53. "
         "All330 moments and1320 complex Laurent slots; stable original IBP tolerance1e-10. "
         "No production adoption, performance, N7, numerical Dual/lifecycle or broader-domain qualification. "
         "Representation precision is not proof of achieved accuracy; logging timings are diagnostic.")

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


def bind(path, inputs, expected=None):
    path = Path(path).resolve()
    # Hash each distinct input once here and again at the final boundary.
    digest = inputs.get(str(path))
    if digest is None:
        digest = sha(path)
        inputs[str(path)] = digest
    require(expected is None or digest == expected, f"changed artifact: {path}")
    return digest


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


def validate_archived_baseline(inputs):
    bind(BASE / "qualification.json", inputs, BASE_SHA)
    qualified = read(BASE / "qualification.json")
    require(qualified["status"] == "private_retained_n6_rank3_qualified"
            and qualified["exact_tests"] == 25 and len(qualified["files"]) == 54,
            "durable generic prerequisite differs")
    for name, digest in qualified["files"].items():
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "unsafe package member")
        bind(BASE / name, inputs, digest)
    archive_manifest = read(BASE / "archive-manifest.json")
    require(archive_manifest["archive_sha256"] == bind(BASE / "sources.tar.gz", inputs), "source archive hash differs")
    archived = {}
    with tarfile.open(BASE / "sources.tar.gz", "r:gz") as archive:
        members = archive.getmembers()
        require(len(members) == len({m.name for m in members}) == 95
                and {m.name for m in members} == set(archive_manifest["members"]), "archive inventory differs")
        for member in members:
            require(member.isfile() and not Path(member.name).is_absolute()
                    and ".." not in Path(member.name).parts, "invalid archived source")
            data = archive.extractfile(member).read()
            require(hashlib.sha256(data).hexdigest() == archive_manifest["members"][member.name], "archived source hash differs")
            archived[member.name] = data
    build, exact = read(BASE / "fixed/build-001/build.json"), read(BASE / "fixed/exact-001/run.json")
    require(build["status"] == exact["status"] == "passed" and build["inputs_unchanged"] is True
            and exact["inputs_unchanged"] is True and exact["bound_seconds"] == 180, "retained exact prerequisite failed")
    require([s["command"][4] for s in exact["steps"]] == list(EXACT_TESTS)
            and all(s["exit_code"] == 0 and not s.get("timeout") for s in exact["steps"])
            and sum(s["seconds"] for s in exact["steps"]) <= 180, "retained exact commands/bound differ")
    for i, names in enumerate(EXACT_TESTS.values()):
        name = f"step-{i}.log"
        require(exact["outputs"][name] == bind(BASE / "fixed/exact-001" / name, inputs), "retained exact output hash differs")
        validate_test_log((BASE / "fixed/exact-001" / name).read_text(), names)
    oldroot = R / "target/public-highpoint/thin-n6-generic-fixed/core"
    sources = {n.removeprefix("fixed/"): data for n, data in archived.items() if n.startswith("fixed/")}
    require(len(sources) == 36, "baseline source inventory differs")
    for name, data in sources.items():
        digest = hashlib.sha256(data).hexdigest()
        require(build["inputs"].get(str(oldroot / name)) == exact["inputs"].get(str(oldroot / name)) == digest,
                "archive/source/exact prerequisite binding differs")
    return qualified, archived, build, exact


def expected_protocol_artifacts(protocol, inputs):
    for path, digest in PINS.items():
        bind(path, inputs, digest)
    qualified, archived, oldbuild, oldexact = validate_archived_baseline(inputs)
    expected = {str(BASE / "qualification.json"): BASE_SHA}
    expected.update({str(BASE / n): d for n, d in qualified["files"].items()})
    copy, manifest, review = [read(H / n) for n in
        ["copy-manifest.json", "instrumentation-manifest.json", "instrumentation-independent-review.json"]]
    require(review["status"] == "passed_source_only_independent_review" and review["findings"] == []
            and review["verified_file_count"] == manifest["file_count"] == 36
            and review["added_lines"] == manifest["instrumentation_line_count"] == 29
            and review["all_changed_files_restore_exact_source_bytes_after_declared_line_removal"] is True,
            "independent diagnostic-only source review is absent")
    require(review["instrumentation_manifest_sha256"] == bind(H / "instrumentation-manifest.json", inputs)
            and review["copy_manifest_sha256"] == manifest["copy_manifest_sha256"] == bind(H / "copy-manifest.json", inputs)
            and review["patch_sha256"] == manifest["patch_sha256"] == bind(H / "instrumentation.patch", inputs),
            "source-review provenance differs")
    original_sources = {n.removeprefix("fixed/"): hashlib.sha256(data).hexdigest()
                        for n, data in archived.items() if n.startswith("fixed/")}
    inventory(copy["source_files"], original_sources, "initial copied source")
    inventory(copy["production_source_guard"], {n.removeprefix("production/"): hashlib.sha256(data).hexdigest()
              for n, data in archived.items() if n.startswith("production/")}, "historical production snapshot")
    disk = {str(p.relative_to(C)): p for p in C.rglob("*") if p.is_file()}
    require(set(disk) == set(original_sources) and all(not p.is_symlink() for p in disk.values()),
            "phase source inventory differs")
    entries = {e["path"]: e for e in manifest["files"]}
    require(len(entries) == len(manifest["files"]) == 36 and set(entries) == set(disk), "instrumentation inventory differs")
    changed, line_count, patch = [], 0, []
    for name in sorted(disk):
        path, entry = disk[name], entries[name]
        data, before = path.read_bytes(), archived["fixed/" + name]
        digest = bind(path, inputs, entry["instrumented_sha256"])
        require(entry["source_sha256"] == original_sources[name], "source baseline differs")
        expected[str(path)] = digest
        lines = data.splitlines(keepends=True)
        added = [{"line": i+1, "text": line.decode().rstrip("\r\n")} for i, line in enumerate(lines)
                 if line.rstrip().endswith(b"// IREGI_PHASE_ONLY")]
        restored = b"".join(line for line in lines if not line.rstrip().endswith(b"// IREGI_PHASE_ONLY"))
        require(restored == before, "diagnostic stripping did not exactly restore the qualified source")
        require(entry["unchanged"] == (data == before), "instrumentation changed-file flag differs")
        if data != before:
            changed.append(name)
            inventory(entry["added_instrumentation_lines"], added, "added diagnostic lines")
            require(entry["stripped_matches_source"] is True
                    and entry["stripped_sha256"] == original_sources[name], "restoration provenance differs")
            patch.extend(difflib.unified_diff(before.decode().splitlines(keepends=True), data.decode().splitlines(keepends=True),
                         fromfile="a/"+name, tofile="b/"+name))
        line_count += len(added)
    require(changed == manifest["changed_files"] == review["changed_files"]
            == ["crates/iregi-rust/src/certified_planar.rs", "crates/iregi-rust/src/thin_n6.rs"]
            and line_count == 29 and "".join(patch).encode() == (H / "instrumentation.patch").read_bytes(),
            "diagnostic patch differs from independently reviewed additions")
    critical = review["critical_unchanged_uv_semantics"]
    for key, name in [("plan_source_sha256", "plan.rs"), ("thin_source_sha256", "thin_n6.rs"),
                      ("tests_source_sha256", "thin_n6/generic_tests.rs")]:
        require(critical[key] == original_sources["crates/iregi-rust/src/" + name], "raw UV source review differs")
    prior = review["prior_exact_evidence_binding"]
    require(prior["build_manifest_sha256"] == bind(BASE / "fixed/build-001/build.json", inputs)
            and prior["run_manifest_sha256"] == bind(BASE / "fixed/exact-001/run.json", inputs)
            and prior["test_executable_sha256"] == oldbuild["outputs"]["tests"]
            == oldexact["inputs"][str(R / "target/public-highpoint/thin-n6-generic-fixed/build-001/tests")],
            "retained exact executable identity differs")
    require((H / "driver.rs").read_bytes() == (BASE / "fixed/driver.rs").read_bytes(), "numerical driver changed")
    for name in ["build.py", "run.py", "compare.py", "driver.rs", "copy-manifest.json",
                 "instrumentation-manifest.json", "instrumentation.patch", "instrumentation-independent-review.json"]:
        expected[str(H / name)] = bind(H / name, inputs)
    for path in [R / "target/e6-direct-n2/preparation.json", R / "target/core-fused-cse-census/supplemental-deps.json"]:
        expected[str(path)] = bind(path, inputs)
        require(oldbuild["inputs"].get(str(path)) == expected[str(path)], "dependency manifest changed from qualified baseline")
        for entry in read(path)["files"]:
            item = (R / entry["frozen"]).resolve()
            require(str(item) not in expected and oldbuild["inputs"].get(str(item)) == entry["sha256"],
                    "unqualified or duplicated dependency")
            expected[str(item)] = bind(item, inputs, entry["sha256"])
    for directory, suffixes in [(R / "target/e6-direct-n2/deps", {".rlib", ".so"}),
                                (R / "target/core-fused-cse-census/supplemental-deps", {".rlib", ".so"}),
                                (R / "target/e6-direct-n2/native", {".a", ".so"})]:
        observed = {str(p.resolve()) for p in directory.rglob("*") if p.is_file() and p.suffix in suffixes}
        retained = {n for n in expected if Path(n).parent == directory and Path(n).suffix in suffixes}
        require(observed == retained, "dependency search directory inventory differs")
    compiler = Path(protocol["compiler_path"])
    require(compiler.is_absolute() and str(compiler) == oldbuild["compiler_path"], "compiler identity differs")
    expected[str(compiler)] = bind(compiler, inputs, oldbuild["inputs"][str(compiler)])
    for path in [FIXTURE, REFERENCE, SHARED, HISTORY, REFERENCE_EXE]:
        expected[str(path)] = bind(path, inputs)
    require(len(expected) == 225, "complete protocol artifact inventory differs")
    keys = {str(Path(n).relative_to(R)) if Path(n).is_relative_to(R) else n: digest for n, digest in expected.items()}
    inventory(protocol["artifacts"], keys, "approved protocol")
    return expected, dict(origin="durable generic exact-001", total_tests=25, rerun_on_phase_binary=False,
        source_reuse="All36 restored files match compiled/tested archive bytes; only29 independently reviewed diagnostic lines added",
        declared_bound_seconds=180, elapsed_seconds=oldexact["elapsed_seconds"],
        raw_uv_scope="N5rank6 leading UV retained; final N6rank7 UV zero follows existing degree rule; no child UV numeric claim")


def validate_build(inputs):
    bind(PROTOCOL, inputs)
    protocol = read(PROTOCOL)
    require(protocol.get("status") == "approved_source_only" and "/root" in protocol.get("reviewers", [])
            and protocol.get("build_bound_seconds") == 90 and protocol.get("runtime_bound_seconds") == 300
            and protocol.get("rank") == 7 and protocol.get("complex_slots") == 1320, "rank7 protocol not approved or scope changed")
    expected, exact_gate = expected_protocol_artifacts(protocol, inputs)
    expected[str(PROTOCOL)] = bind(PROTOCOL, inputs)
    bind(B / "build.json", inputs)
    build = read(B / "build.json")
    inventory(build["inputs"], expected, "complete build input")
    require(build.get("status") == "passed" and build.get("inputs_unchanged") is True
            and build.get("bound_seconds") == 90 and build.get("compiler_path") == protocol["compiler_path"]
            and set(build.get("outputs", {})) == {"libiregi_rust.rlib", "driver"}, "phase build did not complete")
    dependency, supplemental, native = R / "target/e6-direct-n2/deps", R / "target/core-fused-cse-census/supplemental-deps", R / "target/e6-direct-n2/native"
    externs = {"iregi_masters": dependency / "libiregi_masters-f07797f04e91954e.rlib",
               "symbolica": dependency / "libsymbolica-06e42762cabb77d9.rlib", "serde": dependency / "libserde-b04ba25115fa19f8.rlib",
               "serde_json": dependency / "libserde_json-d657c5438f354a41.rlib", "thiserror": supplemental / "libthiserror-0527e2191ec3561c.rlib"}
    common = ["taskset", "-c", "14,15", protocol["compiler_path"], "--edition=2024", "-C", "opt-level=0", "-C", "debuginfo=0",
              "-C", "strip=debuginfo", "-L", f"dependency={dependency}", "-L", f"dependency={supplemental}", "-L", f"native={native}"]
    commands = [common + ["--crate-name", "iregi_rust", "--crate-type", "rlib", str(C / "crates/iregi-rust/src/lib.rs"), "-o", str(B / "libiregi_rust.rlib")]
                + [a for n, p in externs.items() for a in ["--extern", f"{n}={p}"]],
                common + ["--crate-name", "thin_n6_driver", str(H / "driver.rs"), "-o", str(B / "driver"), "--extern", f"iregi_rust={B}/libiregi_rust.rlib"]
                + [a for n in ["symbolica", "iregi_masters", "serde_json"] for a in ["--extern", f"{n}={externs[n]}"]]]
    require([s["name"] for s in build["steps"]] == ["core", "driver"]
            and [s["command"] for s in build["steps"]] == commands, "phase build commands differ")
    require(all(s.get("exit_code") == 0 and not s.get("timeout") and type(s.get("seconds")) in [int, float]
                and math.isfinite(s["seconds"]) and 0 <= s["seconds"] <= 90 for s in build["steps"])
            and sum(s["seconds"] for s in build["steps"]) <= 90, "phase build exceeded budget or failed")
    for name, digest in build["outputs"].items():
        bind(B / name, inputs, digest)
    for name in ["core.log", "driver.log"]:
        bind(B / name, inputs)
    return build, exact_gate


def validate_numeric(directory, bits, build, inputs):
    expected = dict(build["inputs"])
    expected.update({str(B / n): d for n, d in build["outputs"].items()})
    expected[str(B / "build.json")] = bind(B / "build.json", inputs)
    if bits == 256:
        previous_path = H / "comparison-128.json"
        expected[str(previous_path)] = bind(previous_path, inputs)
        previous = read(previous_path)
        require(previous.get("status") == "passed" and previous.get("full_array_original_agreement_qualified") is True
                and previous.get("precision_convergence_qualified") is False
                and [r.get("working_bits") for r in previous.get("records", [])] == [128]
                and previous.get("normalized_original_tolerance") == "1e-10"
                and previous["records"][0]["complex_slots"] == 1320, "256 lacks prior successful rank7 128 comparison")
        require(previous.get("input_sha256"), "prior comparison lacks provenance")
        for name, digest in previous["input_sha256"].items():
            require(name not in expected or expected[name] == digest, "prior128 provenance conflict")
            expected[name] = digest
    bind(directory / "run.json", inputs)
    run = read(directory / "run.json")
    inventory(run["inputs"], expected, "complete rank7 runtime input")
    for name, digest in expected.items():
        bind(name, inputs, digest)
    require(set(run.get("outputs", {})) <= {"result.json", "step-0.log"}, "unexpected rank7 output")
    for name, digest in run.get("outputs", {}).items():
        bind(directory / name, inputs, digest)
    command = ["taskset", "-c", "14", str(B / "driver"), str(FIXTURE), "6", "7", "pv", str(bits), "53", "1", str(directory / "result.json")]
    require(run.get("status") == "passed" and run.get("inputs_unchanged") is True
            and run.get("bound_seconds") == 300 and run.get("environment_additions") == ENVIRONMENT
            and [s.get("command") for s in run.get("steps", [])] == [command], "rank7 capture failed or protocol differs")
    step = run["steps"][0]
    require(step.get("exit_code") == 0 and not step.get("timeout") and type(step.get("seconds")) in [int, float]
            and math.isfinite(step["seconds"]) and 0 <= step["seconds"] <= 300
            and set(run["outputs"]) == {"result.json", "step-0.log"}, "rank7 runtime incomplete or over bound")
    return run

def validate_array(record, bits, fixture, shared):
    require(record.get("schema_version") == 1 and record.get("status") == "all_lanes_success"
            and record.get("settings") == SETTINGS and record.get("working_bits") == bits
            and record.get("requested_bits") == 53 and record.get("rows") == 1
            and record.get("components") == 1 and record.get("fixture") == str(FIXTURE)
            and record.get("lane_statuses") == ["Success"]
            and record.get("basis") == shared.canonical_basis(7), "unsupported or incomplete tensor result")
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
    require(isinstance(moments, list) and len(moments) == 330, "expected all 330 tensor moments")
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
        build, exact_gate = validate_build(inputs)
        spec = importlib.util.spec_from_file_location("thin_rank7_shared_comparator", SHARED)
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
        report["exact_gate"] = exact_gate
        records, arrays = [], []
        for text_bits in arguments:
            bits = int(text_bits)
            directory = H / f"n6-rank7-{bits}-001"
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
                require(len(errors) == 1320 and poles == 990, "full slot coverage is incomplete")
                records.append(dict(working_bits=bits, complex_slots=1320, real_components=2640,
                                    exact_zero_complex_poles=990, maximum_original_error=str(max(errors)),
                                    declared_bound_seconds=300, elapsed_seconds=run["elapsed_seconds"],
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
                require(len(errors) == 1320 and max(errors) <= Decimal(2) ** -80, "128/256 convergence gate failed")
                convergence = str(max(errors))
        # Recheck every bound artifact after parsing and numerical comparison.
        for path, digest in inputs.items():
            require(sha(path) == digest, f"artifact changed during comparison: {path}")
        report.update(status="passed", records=records, full_array_original_agreement_qualified=True,
                      precision_convergence_qualified=len(arrays) == 2,
                      normalized_original_tolerance="1e-10", convergence_tolerance="2^-80" if len(arrays) == 2 else None,
                      maximum_precision_difference=convergence,
                      normalization="Q^(4-2N+rank); complex norm / max(1, normalized reference norm)",
                      retained_generic_base_status="private_retained_n6_rank3_qualified",
                      historical_exact_tests_reused_after_source_restoration=True)
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
    report["input_sha256"] = inputs
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(output), "status": report["status"], "scope": SCOPE}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Preserve terminal rank7 evidence; never launch or rerun a qualification gate.

Run only after both captures are terminal and packaging is authorized. This
package preserves failed128-bit acceptance and separately approved256-bit
diagnostics; it can never confer numerical acceptance, even if convergence is
observed. Native objects and executables are inventoried but not embedded.
"""
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import gzip
import hashlib
import io
import json
import math
import re
import shutil
import tarfile
import tempfile

R = Path(__file__).resolve().parents[3]
H = R / "target/public-highpoint/thin-n6-rank7-phase"
B, C = H / "build-001", H / "core"
BASE = R / "validation/highpoint-thin-n6-generic"
DESTINATION = R / "validation/highpoint-thin-n6-rank7-phase"
PROTOCOL_SHA = "289e73fc1ade605cb5642cb443843f1ae6303d97f44edce07d1fc76d420aac0a"
COMPARE_SHA = "6e59c3964d3363191975ba13008cd8982264fcf0b969374995233094b4a2554a"
BASE_SHA = "79ccaaa6439fd6cc2307f0dc186b6c6fbf7ba4a1585177a6ceab360d53b74d34"
REVIEW_SHA = "94349a3b203b0a0cd9fbe56686a717da49bdb282c93b99a69073b1031c3cf158"
ACCEPTANCE_SHA = "ad2fb606dd473a901f0c13192edf02b66c2cb14155dc2592524a4cc89218eb02"
DIAGNOSTIC_PROTOCOL_SHA = "3328f45c2e5f47eed881faea2dd1a2b9be4c66d5ed7c37debc1d5b8ed85bdaaa"
DIAGNOSTIC_COMPARE_SHA = "ed73766d8fe7243c6ef19066288bc46db24570bfea6b2456ea4a27cb88277d08"
AUDIT_SOURCE = R / "target/guard-performance-review/rank7-audit"
AUDIT_DURABLE = R / "validation/checkpoint-audits/2026-10-24-thin-n6-rank7-128"
AUDIT_COPY_RECEIPT = R / "validation/checkpoint-audits/2026-10-24-thin-n6-rank7-128-copy.json"
AUDIT_MANIFEST_SHA = "1b925a9ba411941fa198ac8bb4ab45748ad04e4604ff2f9933fd743758b5780c"
AUDIT_COPY_SHA = "d30935311c18525a22976b0dd312c8d3b9695b2cb612e7823ab6dc04e6a408bc"
AUDIT_256 = R / "target/guard-performance-review/rank7-diagnostic-256-audit"
AUDIT_256_MANIFEST_SHA = "ee9a50f7d7071f26824ad26cb479567a5990b22fb004b774692cc29a0fdfae49"
AUDIT_256_SHA = "91b28c5e547d30a51bf6c34cb02defd98322f9c9653f85675d489ec991d03b39"
ENVIRONMENT = {"RAYON_NUM_THREADS": "1", "RUST_TEST_THREADS": "1",
               "IREGI_PREPARATION_PROFILE": "1", "IREGI_PV_PREPARATION_PROFILE": "1"}
SCOPE = ("Private instrumented thin N6 rank7, unchanged retained base singleton, "
         "native Components, FromShifts/Preserve/unit powers/h0/PV, requested53. "
         "All330 cumulative moments and1320 complex Laurent slots per precision.")
LIMITATIONS = [
    "No production adoption, performance, N7, generalized-input or SuppliedG qualification.",
    "No numerical Dual, lifecycle or complex-mass qualification at rank7.",
    "The 25 exact tests are historical generic tests reused after exact source restoration; no phase test binary was built.",
    "Raw child N5 rank6 UV is retained by the existing degree rule; no numerical child-residue measurement is claimed.",
    "Existing ordinary primal sensitivity model; no rigorous compounded Taylor bound; quadrature imports unsupported.",
    "Representation precision and successful process exit do not establish achieved accuracy.",
    "Timing markers and elapsed durations are diagnostic; missing END markers do not establish a completed phase duration.",
    "Native dependencies, compiler and executables remain external and require the recorded hashes for reproduction.",
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def validate_complete_capture(record, bits, fixture):
    """Validate saved layout and identity, without claiming any agreement."""
    basis = [[t, x, y, rank-t-x-y] for rank in range(8) for t in range(rank, -1, -1)
             for x in range(rank-t, -1, -1) for y in range(rank-t-x, -1, -1)]
    settings = dict(propagators=6, rank=7, powers=[1]*6, dimension_shift=0,
                    algorithm="PassarinoVeltman", convention="IregiNative", tensor_weights="Components",
                    invariants="FromShifts", input_policy="Preserve")
    require(record.get("schema_version") == 1 and record.get("status") == "all_lanes_success"
            and record.get("settings") == settings and record.get("working_bits") == bits
            and record.get("requested_bits") == 53 and record.get("rows") == record.get("components") == 1
            and record.get("fixture") == str(R / "validation/public-highpoint/fixture-conditioned_masses.json")
            and record.get("basis") == basis and record.get("lane_statuses") == ["Success"],
            "capture identity or complete-array metadata differs")
    sample = fixture["samples"][0]
    require(sample["id"] == "base", "fixture base row differs")
    propagators = sample["propagators"][:6]
    row = [[str(Fraction(v)), "0"] for p in propagators for v in p["shift"]]
    row += [[str(Fraction(v)) for v in p["mass_squared"]] for p in propagators]
    row += [[str(Fraction(sample["mu"])), "0"]]
    require(record.get("input_exact_rational") == [row], "saved capture inputs differ")
    lanes = record.get("lanes")
    require(isinstance(lanes, list) and len(lanes) == 1 and lanes[0].get("row") == 0
            and lanes[0].get("status") == "Success", "capture lane identity differs")
    moments = lanes[0].get("moments")
    require(isinstance(moments, list) and len(moments) == 330, "capture lacks all330 moments")
    for moment in moments:
        require(isinstance(moment, list) and len(moment) == 4, "capture lacks four Laurent slots")
        for slot in moment:
            require(isinstance(slot, dict) and set(slot) == {"real", "imaginary", "real_precision", "imaginary_precision"},
                    "capture component layout differs")
            for key in ["real", "imaginary"]:
                require(isinstance(slot[key], str), "capture native component is not exact text")
                value, precision = Fraction(slot[key]), slot[key + "_precision"]
                require(type(precision) is int and precision >= 0 and (value == 0 or precision > 0),
                        "invalid capture representation precision")


def main():
    require(not DESTINATION.exists(), "package destination already exists")
    observed, payload, source_members = {}, {}, {}

    def bind(path, expected=None):
        path = Path(path).resolve()
        require(path.is_file(), f"missing artifact: {path}")
        digest = observed.get(str(path))
        if digest is None:
            digest = sha(path)
            observed[str(path)] = digest
        require(expected is None or digest == expected, f"hash differs: {path}")
        return digest

    def copy_source(path, name, expected=None):
        path = Path(path).resolve()
        require(name not in payload and not Path(name).is_absolute() and ".." not in Path(name).parts,
                "invalid or duplicated payload name")
        bind(path, expected)
        payload[name] = path

    def closure(record, directory):
        mapping = record.get("inputs", record.get("input_sha256"))
        require(isinstance(mapping, dict) and mapping, "missing evidence input inventory")
        for name, digest in mapping.items():
            bind(name, digest)
        for name, digest in record.get("outputs", {}).items():
            require(Path(name).name == name, "output escapes capture directory")
            bind(directory / name, digest)

    bind(Path(__file__))
    bind(H / "compare.py", COMPARE_SHA)
    bind(H / "protocol.json", PROTOCOL_SHA)
    bind(H / "instrumentation-independent-review.json", REVIEW_SHA)
    protocol = read(H / "protocol.json")
    require(protocol["status"] == "approved_source_only" and "/root" in protocol["reviewers"]
            and protocol["build_bound_seconds"] == 90 and protocol["runtime_bound_seconds"] == 300
            and protocol["rank"] == 7 and protocol["complex_slots"] == 1320,
            "approved rank7 protocol differs")
    artifacts = protocol["artifacts"]
    require(len(artifacts) == 225 and [n for n in artifacts if Path(n).is_absolute()] == [protocol["compiler_path"]]
            and all(".." not in Path(n).parts for n in artifacts), "protocol inventory differs")
    expected_build = {str(R / n): bind(R / n, d) for n, d in artifacts.items()}
    expected_build[str(H / "protocol.json")] = PROTOCOL_SHA

    build = read(B / "build.json")
    build_sha = bind(B / "build.json")
    require(build["status"] == "passed" and build["inputs_unchanged"] is True
            and build["bound_seconds"] == 90 and build["inputs"] == expected_build
            and build["compiler_path"] == protocol["compiler_path"]
            and set(build["outputs"]) == {"libiregi_rust.rlib", "driver"}
            and [s["name"] for s in build["steps"]] == ["core", "driver"]
            and all(s["exit_code"] == 0 and not s.get("timeout") for s in build["steps"]),
            "phase build lacks complete guarded success")
    closure(build, B)
    for name in ["build.py", "run.py", "compare.py", "driver.rs", "protocol.json", "copy-manifest.json",
                 "instrumentation-manifest.json", "instrumentation.patch", "instrumentation-independent-review.json", "package.py"]:
        copy_source(H / name, "phase/" + name)
    for name in ["build.json", "core.log", "driver.log"]:
        copy_source(B / name, "phase/build-001/" + name)

    # The baseline package is immutable. Read its archived production snapshot;
    # do not introduce a guard on today's mutable production tree.
    bind(BASE / "qualification.json", BASE_SHA)
    base = read(BASE / "qualification.json")
    require(base["status"] == "private_retained_n6_rank3_qualified" and base["exact_tests"] == 25
            and len(base["files"]) == 54, "generic prerequisite is not qualified")
    for name, digest in base["files"].items():
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "unsafe base payload name")
        bind(BASE / name, digest)
    for name in ["qualification.json", "archive-manifest.json", "README.md", "fixed/build-001/build.json",
                 "fixed/exact-001/run.json", *[f"fixed/exact-001/step-{i}.log" for i in range(5)]]:
        copy_source(BASE / name, "generic-base/" + name)
    archive_manifest = read(BASE / "archive-manifest.json")
    require(archive_manifest["archive_sha256"] == bind(BASE / "sources.tar.gz"), "generic source archive differs")
    archived = {}
    with tarfile.open(BASE / "sources.tar.gz", "r:gz") as archive:
        members = archive.getmembers()
        require(len(members) == len({m.name for m in members}) == 95
                and {m.name for m in members} == set(archive_manifest["members"]), "generic archive inventory differs")
        for member in members:
            require(member.isfile() and not Path(member.name).is_absolute() and ".." not in Path(member.name).parts,
                    "invalid generic source archive member")
            data = archive.extractfile(member).read()
            require(hashlib.sha256(data).hexdigest() == archive_manifest["members"][member.name], "generic source hash differs")
            archived[member.name] = data
            if member.name.startswith("fixed/") or member.name.startswith("production/"):
                source_members["generic-baseline/" + member.name] = data
    original_sources = {n.removeprefix("fixed/"): d for n, d in archived.items() if n.startswith("fixed/")}
    disk = {str(p.relative_to(C)): p for p in C.rglob("*") if p.is_file()}
    require(set(disk) == set(original_sources) and len(disk) == 36
            and all(not p.is_symlink() for p in disk.values()), "phase source inventory differs")
    manifest = read(H / "instrumentation-manifest.json")
    entries = {e["path"]: e for e in manifest["files"]}
    require(len(entries) == len(manifest["files"]) == 36 and set(entries) == set(disk)
            and manifest["instrumentation_line_count"] == 29, "instrumentation inventory differs")
    added = 0
    for name, path in sorted(disk.items()):
        digest = bind(path, entries[name]["instrumented_sha256"])
        require(build["inputs"].get(str(path)) == digest, "source was not bound to the build")
        data = path.read_bytes()
        lines = data.splitlines(keepends=True)
        added += sum(line.rstrip().endswith(b"// IREGI_PHASE_ONLY") for line in lines)
        restored = b"".join(line for line in lines if not line.rstrip().endswith(b"// IREGI_PHASE_ONLY"))
        require(restored == original_sources[name], "phase source does not restore the qualified baseline")
        source_members["phase/" + name] = data
    require(added == 29 and len(source_members) == 95, "expected36 phase +36 baseline +23 historical production sources")

    # This new protocol authorizes a diagnostic after failed acceptance. It is
    # distinct from the original conditional acceptance route to Float256.
    bind(H / "diagnostic-protocol.json", DIAGNOSTIC_PROTOCOL_SHA)
    bind(H / "diagnostic-compare.py", DIAGNOSTIC_COMPARE_SHA)
    diagnostic_protocol = read(H / "diagnostic-protocol.json")
    require(diagnostic_protocol["status"] == "approved_source_only"
            and "/root" in diagnostic_protocol["reviewers"]
            and diagnostic_protocol["runtime_bound_seconds"] == 300
            and diagnostic_protocol["working_bits"] == 256 and diagnostic_protocol["requested_bits"] == 53
            and diagnostic_protocol["rank"] == 7 and diagnostic_protocol["complex_slots"] == 1320
            and diagnostic_protocol["acceptance_qualified"] is False
            and diagnostic_protocol["prior_acceptance_sha256"] == ACCEPTANCE_SHA,
            "separate diagnostic protocol differs")
    expected_diagnostic = {str((R / n).resolve()): bind(R / n, d) for n, d in diagnostic_protocol["artifacts"].items()}
    require(len(expected_diagnostic) == 275, "diagnostic guard inventory differs")
    expected_diagnostic[str(H / "diagnostic-protocol.json")] = DIAGNOSTIC_PROTOCOL_SHA
    for name in ["diagnostic-run.py", "diagnostic-compare.py", "diagnostic-protocol.json",
                 "diagnostic-preflight-001.json", "diagnostic-preflight-002.json"]:
        copy_source(H / name, "phase/" + name)
    reviewed_drafts = sorted(p for p in (H / "diagnostic-reviewed-draft-001").rglob("*") if p.is_file())
    require({p.name for p in reviewed_drafts} == {"diagnostic-compare.py", "diagnostic-protocol.json",
            "protocol-schema-corrected-pending.json", "preflight-failure.json"}, "reviewed draft inventory differs")
    for path in reviewed_drafts:
        copy_source(path, "phase/" + str(path.relative_to(H)))

    # Reference the already durable audit packet instead of duplicating it.
    bind(AUDIT_SOURCE / "manifest.json", AUDIT_MANIFEST_SHA)
    bind(AUDIT_DURABLE / "manifest.json", AUDIT_MANIFEST_SHA)
    bind(AUDIT_COPY_RECEIPT, AUDIT_COPY_SHA)
    audit_manifest, receipt = read(AUDIT_DURABLE / "manifest.json"), read(AUDIT_COPY_RECEIPT)
    require(audit_manifest["status"] == "frozen_independent_saved_data_failure_audit"
            and len(audit_manifest["files"]) == 19 and audit_manifest["numerical_agreement_qualified"] is False
            and audit_manifest["precision_convergence_qualified"] is False
            and receipt["source"] == str(AUDIT_SOURCE.relative_to(R))
            and receipt["destination"] == str(AUDIT_DURABLE.relative_to(R))
            and receipt["source_manifest_sha256"] == receipt["destination_manifest_sha256"] == AUDIT_MANIFEST_SHA
            and receipt["all_source_destination_bytes_equal"] is True, "durable independent audit identity differs")
    audit_origins = {str(AUDIT_SOURCE / "manifest.json"): str(AUDIT_DURABLE / "manifest.json")}
    for name, entry in audit_manifest["files"].items():
        require(Path(name).name == name, "unsafe independent audit member")
        for directory in [AUDIT_SOURCE, AUDIT_DURABLE]:
            bind(directory / name, entry["sha256"])
            require((directory / name).stat().st_size == entry["bytes"], "independent audit member size differs")
        audit_origins[str(AUDIT_SOURCE / name)] = str(AUDIT_DURABLE / name)
    primary_audit = read(AUDIT_DURABLE / "audit-128.json")
    require(primary_audit["status"] == "passed_independent_saved_data_audit_of_failed_numerical_gate"
            and primary_audit["numerical"]["complex_slots"] == 1320 and primary_audit["numerical"]["failed_slots"] == 90
            and primary_audit["numerical"]["exact_zero_candidate_pole_slots"] == 990,
            "independent failed-acceptance characterization differs")

    attempts = sorted(p for p in H.glob("n6-rank7-*") if p.is_dir())
    require({p.name for p in attempts} == {"n6-rank7-128-001", "n6-rank7-256-diagnostic-001"},
            "expected initial128 capture and separate256 diagnostic only")
    attempt_records = []
    for directory in attempts:
        match = re.fullmatch(r"n6-rank7-(128|256)(-diagnostic)?-001", directory.name)
        require(match is not None, "unreviewed rank7 attempt path")
        bits, run = int(match[1]), read(directory / "run.json")
        require(run["status"] in {"passed", "failed"} and run.get("finished_utc")
                and run.get("inputs_unchanged") is True and run["bound_seconds"] == 300,
                f"capture is active or lacks completed input guards: {directory}")
        expected = dict(expected_build)
        expected[str(B / "build.json")] = build_sha
        expected.update({str(B / n): d for n, d in build["outputs"].items()})
        if bits == 256:
            require(match[2] == "-diagnostic" and run.get("acceptance_qualified") is False,
                    "256 attempt is not explicitly diagnostic")
            expected = expected_diagnostic
        require(run["inputs"] == expected and run["environment_additions"] == ENVIRONMENT,
                "runtime inventory or environment differs")
        command = ["taskset", "-c", "14", str(B / "driver"),
                   str(R / "validation/public-highpoint/fixture-conditioned_masses.json"),
                   "6", "7", "pv", str(bits), "53", "1", str(directory / "result.json")]
        require([s.get("command") for s in run["steps"]] == [command], "runtime command differs")
        step = run["steps"][0]
        require(type(step.get("seconds")) in {int, float} and math.isfinite(step["seconds"])
                and step["seconds"] >= 0, "runtime lacks a terminal duration")
        if run["status"] == "passed":
            require(step.get("exit_code") == 0 and not step.get("timeout") and step["seconds"] <= 300,
                    "successful runner has inconsistent process status")
        require(set(run.get("outputs", {})) <= {"result.json", "step-0.log"}
                and {p.name for p in directory.iterdir()} == set(run["outputs"]) | {"run.json"},
                "capture has unrecorded artifacts")
        closure(run, directory)
        for name in ["run.json", *run["outputs"]]:
            copy_source(directory / name, f"phase/{directory.name}/{name}")
        result, result_parse_error, complete_array, layout_error = None, None, False, None
        if "result.json" in run["outputs"]:
            try:
                result = read(directory / "result.json")
                require(isinstance(result, dict), "result ledger is not an object")
            except Exception as error:
                result = None
                result_parse_error = f"{type(error).__name__}: {error}"
        if result is not None and result.get("status") == "all_lanes_success":
            try:
                validate_complete_capture(result, bits, read(R / "validation/public-highpoint/fixture-conditioned_masses.json"))
                complete_array = True
            except Exception as error:
                layout_error = f"{type(error).__name__}: {error}"
        attempt_records.append(dict(attempt=directory.name, working_bits=bits, status=run["status"],
            diagnostic_only=bits == 256,
            result_status=None if result is None else result.get("status"), result_parse_error=result_parse_error,
            complete_saved_array=complete_array, saved_complex_slots=1320 if complete_array else 0,
            array_layout_error=layout_error,
            declared_bound_seconds=300, elapsed_seconds=run.get("elapsed_seconds"), steps=run["steps"],
            run_sha256=bind(directory / "run.json"), numerically_qualified=False))

    comparison_paths = sorted(H.glob("comparison-*.json"))
    require(comparison_paths == [H / "comparison-128.json"], "unexpected acceptance comparison")
    acceptance_path = comparison_paths[0]
    bind(acceptance_path, ACCEPTANCE_SHA)
    acceptance = read(acceptance_path)
    require(acceptance["status"] == "failed" and acceptance["full_array_original_agreement_qualified"] is False
            and acceptance["precision_convergence_qualified"] is False
            and "original disagreement at moment 126, slot 3:" in acceptance["error"],
            "original failed numerical acceptance is not preserved")
    closure(acceptance, H)
    copy_source(acceptance_path, "phase/" + acceptance_path.name)
    initial = next(a for a in attempt_records if a["working_bits"] == 128)
    require(initial["status"] == "passed" and initial["complete_saved_array"] is True,
            "original128 capture is not complete")
    for artifact in [H / "compare.py", H / "protocol.json", B / "build.json", H / "n6-rank7-128-001/run.json",
                     H / "n6-rank7-128-001/result.json", H / "n6-rank7-128-001/step-0.log"]:
        require(acceptance["input_sha256"].get(str(artifact)) == bind(artifact), "failed acceptance binding differs")
    comparison_records = [dict(name=acceptance_path.name, status="failed", sha256=ACCEPTANCE_SHA,
                               error=acceptance["error"], acceptance_qualified=False)]

    diagnostic_paths = sorted(H.glob("diagnostic-comparison-*.json"))
    require(diagnostic_paths == [H / "diagnostic-comparison-128-256.json"], "terminal diagnostic comparison is missing")
    diagnostic_path, measured_convergence, maximum_precision_difference = diagnostic_paths[0], None, None
    diagnostic = read(diagnostic_path)
    require(diagnostic["status"] in {"completed_diagnostic", "diagnostic_failed"}
            and diagnostic["diagnostic_only"] is True
            and all(diagnostic[k] is False for k in ["acceptance_qualified", "full_array_original_agreement_qualified",
                "precision_convergence_qualified", "lifecycle_qualified", "performance_qualified"])
            and diagnostic["prior_acceptance_sha256"] == ACCEPTANCE_SHA
            and diagnostic["prior_acceptance_status"] == "failed", "diagnostic output attempts to upgrade acceptance")
    closure(diagnostic, H)
    copy_source(diagnostic_path, "phase/" + diagnostic_path.name)
    if diagnostic["status"] == "completed_diagnostic":
        later = next(a for a in attempt_records if a["working_bits"] == 256)
        require(later["status"] == "passed" and later["complete_saved_array"] is True,
                "completed diagnostics lack complete256 arrays")
        for artifact, digest in expected_diagnostic.items():
            require(diagnostic["input_sha256"].get(artifact) == digest, "diagnostic prerequisite binding differs")
        for directory in attempts:
            for name in ["run.json", "result.json", "step-0.log"]:
                path = directory / name
                require(diagnostic["input_sha256"].get(str(path)) == bind(path), "diagnostic capture binding differs")
        originals, convergence = diagnostic["original_mode_comparisons"], diagnostic["precision_comparison"]
        require(diagnostic["original_complex_comparisons"] == 7920 and diagnostic["convergence_complex_comparisons"] == 1320
                and [(x["working_bits"], x["original_mode"], x["original_stable"]) for x in originals]
                    == [(bits, mode, mode != 1) for bits in [128, 256] for mode in [0, 1, 2]],
                "diagnostic original-mode coverage differs")
        for row in [*originals, convergence]:
            require(row["compared_complex_slots"] == 1320 and row["failures"] == len(row["failure_details"])
                    and row["observed_all_slots_within_tolerance"] == (row["failures"] == 0),
                    "diagnostic slot or failure counts differ")
        require(all(x["tolerance"] == "1e-10" for x in originals) and convergence["tolerance"] == "2^-80"
                and diagnostic["normalized_original_tolerance"] == "1e-10"
                and diagnostic["convergence_tolerance"] == "2^-80", "diagnostic thresholds changed")
        maximum_precision_difference = convergence["maximum_normalized_error"]
        measured_convergence = convergence["observed_all_slots_within_tolerance"]
        require(type(measured_convergence) is bool
                and measured_convergence == (Fraction(maximum_precision_difference) <= Fraction(1, 2**80)),
                "diagnostic convergence observation is inconsistent")
        require(diagnostic["saved_parameter_oracle"]["status"] == "estimated_convergence_only"
                and diagnostic["saved_parameter_oracle"]["compared_finite_components"] == 28
                and diagnostic["saved_parameter_oracle"]["all_retained_rule_count"] == 7
                and diagnostic["saved_parameter_oracle"]["new_quadrature_executed"] is False
                and diagnostic["analytic_real_zero_diagnostics"]["imaginary_accuracy_qualified"] is False,
                "limited saved-oracle/phase diagnostic scope differs")
    diagnostic_record = dict(name=diagnostic_path.name, sha256=bind(diagnostic_path), status=diagnostic["status"],
        error=diagnostic.get("error"), observed_convergence_at_2_minus_80=measured_convergence,
        maximum_precision_difference=maximum_precision_difference, acceptance_qualified=False)

    # Preserve the entire independently frozen256-bit packet, including the
    # first auditor failure and its separately recorded presentation correction.
    # Its successful audit status is diagnostic, never numerical acceptance.
    bind(AUDIT_256 / "manifest.json", AUDIT_256_MANIFEST_SHA)
    audit256_manifest = read(AUDIT_256 / "manifest.json")
    audit256_names = {"README.md", "all-slots.json", "audit-v2.stderr", "audit-v2.stdout", "audit.json",
        "audit.stderr", "audit.stdout", "audit_saved_256.py", "audit_saved_256_v2.py",
        "report-rounding-correction.json"}
    require(audit256_manifest["status"] == "frozen_independent_saved_data_diagnostic_audit"
            and set(audit256_manifest["files"]) == audit256_names
            and audit256_manifest["audit_sha256"] == AUDIT_256_SHA
            and audit256_manifest["primary_failed_acceptance_sha256"] == ACCEPTANCE_SHA
            and audit256_manifest["diagnostic_protocol_sha256"] == DIAGNOSTIC_PROTOCOL_SHA
            and audit256_manifest["precision_diagnostic_observed_passed"] is True
            and all(audit256_manifest[k] is False for k in ["acceptance_qualified",
                "precision_convergence_qualified", "imaginary_accuracy_qualified",
                "kernel_build_test_quadrature_or_algebra_execution"]),
            "independent256 audit manifest or diagnostic-only scope differs")
    audit256_inventory = sorted(AUDIT_256.iterdir())
    require({p.name for p in audit256_inventory} == audit256_names | {"manifest.json"}
            and all(p.is_file() and not p.is_symlink() for p in audit256_inventory),
            "independent256 audit packet has missing or unrecorded members")
    copy_source(AUDIT_256 / "manifest.json", "independent256audit/manifest.json", AUDIT_256_MANIFEST_SHA)
    for name, entry in audit256_manifest["files"].items():
        path = AUDIT_256 / name
        require(path.stat().st_size == entry["bytes"], "independent256 audit member size differs")
        copy_source(path, "independent256audit/" + name, entry["sha256"])
    audit256 = read(AUDIT_256 / "audit.json")
    require(audit256["status"] == "passed_independent_saved_data_diagnostic_audit"
            and bind(AUDIT_256 / "audit.json") == AUDIT_256_SHA
            and audit256["prior_failed_gate_sha256"] == ACCEPTANCE_SHA
            and audit256["protocol_sha256"] == DIAGNOSTIC_PROTOCOL_SHA
            and audit256["precision_diagnostic_observed_passed"] is True
            and all(audit256[k] is False for k in ["acceptance_qualified",
                "full_array_original_agreement_qualified", "precision_convergence_qualified",
                "imaginary_accuracy_qualified", "kernel_build_test_or_quadrature_executed_by_reviewer"]),
            "independent256 audit result or scope differs")
    audit256_inputs = {}
    for name, digest in audit256["input_sha256"].items():
        path = (R / name).resolve()
        require(str(path) not in audit256_inputs, "duplicate normalized independent256 input")
        audit256_inputs[str(path)] = bind(path, digest)
    expected_audit256 = {str((R / n).resolve()): d for n, d in diagnostic["input_sha256"].items()}
    expected_audit256[str(diagnostic_path)] = bind(diagnostic_path)
    require(len(audit256_inputs) == audit256["unique_bound_artifacts"] == 280
            and audit256_inputs == expected_audit256
            and audit256_manifest["upstream_input_sha256"] == audit256["input_sha256"]
            and audit256["script_sha256"] == bind(AUDIT_256 / "audit_saved_256_v2.py")
            and audit256["all_slots_sha256"] == bind(AUDIT_256 / "all-slots.json"),
            "independent256 audit is not bound to the complete diagnostic closure")
    require(diagnostic["status"] == "completed_diagnostic" and measured_convergence is True
            and audit256["precision"]["complex_slots"] == 1320
            and audit256["precision"]["threshold"] == "2^-80" and audit256["precision"]["failures"] == 0
            and Fraction(audit256["precision"]["maximum"]) <= Fraction(1, 2**80)
            and audit256["exact_zero_poles_by_working_bits"] == {"128": 990, "256": 990}
            and [(x["working_bits"], x["mode"], x["reference_stable"], x["slots"], x["failures"])
                 for x in audit256["original_modes"]]
                == [(bits, mode, mode != 1, 1320, count) for bits in [128, 256]
                    for mode, count in [(0, 90), (1, 151), (2, 109)]]
            and len(audit256["saved_oracle_comparisons"]) == 28
            and audit256["runtime"]["bound_seconds"] == 300
            and audit256["runtime"]["inputs_unchanged"] is True,
            "independent256 audit coverage or recorded outcome differs")
    correction = read(AUDIT_256 / "report-rounding-correction.json")
    require(correction["status"] == "saved_data_auditor_presentation_precision_correction_only"
            and correction["initial_source_sha256"] == bind(AUDIT_256 / "audit_saved_256.py")
            and correction["initial_failure_stderr_sha256"] == bind(AUDIT_256 / "audit.stderr")
            and correction["unchanged_original_tolerance"] == "1e-10"
            and correction["unchanged_precision_tolerance"] == "2^-80"
            and correction["new_kernel_build_test_execution"] is False,
            "retained initial auditor failure or correction scope differs")

    for name in ["fixture-conditioned_masses.json", "reference-conditioned_masses.json", "compare_public.py", "qualification.json"]:
        copy_source(R / "validation/public-highpoint" / name, "reference/" + name)
    for path, name in [(R / "target/e6-direct-n2/preparation.json", "dependency-preparation.json"),
                       (R / "target/core-fused-cse-census/supplemental-deps.json", "supplemental-dependencies.json")]:
        copy_source(path, "provenance/" + name)

    stage = Path(tempfile.mkdtemp(prefix=".thin-n6-rank7-phase-", dir=DESTINATION.parent))
    try:
        origins = {}
        for name, path in sorted(payload.items()):
            destination = stage / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(path.read_bytes())
            require(sha(destination) == observed[str(path)], "payload changed during copying")
            origins[name] = dict(original_path=str(path.relative_to(R)), sha256=observed[str(path)])
        source_hashes = {}
        with (stage / "sources.tar.gz").open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                with tarfile.open(mode="w", fileobj=compressed) as archive:
                    for name, data in sorted(source_members.items()):
                        info = tarfile.TarInfo(name)
                        info.size, info.mode, info.mtime = len(data), 0o644, 0
                        archive.addfile(info, io.BytesIO(data))
                        source_hashes[name] = hashlib.sha256(data).hexdigest()
        save(stage / "archive-manifest.json", dict(archive_sha256=sha(stage / "sources.tar.gz"), members=source_hashes,
             baseline_source_archive_path=str((BASE / "sources.tar.gz").relative_to(R)),
             baseline_source_archive_sha256=observed[str(BASE / "sources.tar.gz")]))
        save(stage / "payload-origins.json", origins)
        embedded = {str(p) for p in payload.values()} | {str(p.resolve()) for p in disk.values()}
        external = {p: d for p, d in observed.items() if p not in embedded}
        save(stage / "external-artifact-hashes.json", dict(scope="Verified external closure; no embedded native objects or executables.", files=external))
        save(stage / "independent-audit-reference.json", dict(
            durable_packet_path=str(AUDIT_DURABLE.relative_to(R)), manifest_sha256=AUDIT_MANIFEST_SHA,
            copy_receipt_path=str(AUDIT_COPY_RECEIPT.relative_to(R)), copy_receipt_sha256=AUDIT_COPY_SHA,
            original_runtime_binding_to_durable_copy=audit_origins,
            scope="Separate durable128-bit failure audit; unchanged bytes referenced, not duplicated. No256-bit accuracy claim."))
        status = "private_retained_n6_rank7_complete_capture_numerical_agreement_failed"
        (stage / "README.md").write_text(
            f"This package preserves a private rank7 phase experiment. Recorded outcome: `{status}`.\n\n"
            + SCOPE + "\n\n"
            "The initial128-bit process succeeded and returned all1,320 slots, but90 finite slots failed the original-reference gate. "
            "The separate256-bit attempt is diagnostic only; its process outcome, partial or complete arrays, and saved analysis are preserved. "
            f"Diagnostic status: {diagnostic['status']}; observed convergence at2^-80: {measured_convergence}. "
            "Neither numerical agreement nor precision convergence is qualified by this package. "
            "The failed acceptance remains unchanged regardless of any diagnostic observation. "
            "Original comparisons retain the1e-10 threshold with Q^(4-2N+moment rank), complex norm/max(1, normalized reference norm). "
            "All original modes retain their stability flags. Saved quadrature at only scalar/moment321 and the real-zero identity cannot certify imaginary accuracy.\n\n"
            "The reviewed draft comparator/protocol and failed preflight records are preserved alongside the narrowly corrected approved diagnostic sources. "
            "The independent20-file audit packet remains in the separately durable checkpoint-audits directory; its manifest, copy receipt, "
            "source-origin mapping and every payload hash are verified and referenced without duplicating the packet. "
            "The separate11-file independent256audit packet is copied in full, with280 upstream bindings verified. "
            "It preserves the initial auditor presentation-rounding failure and the separate correction; neither physical tolerance changed. "
            "Its observed precision agreement remains diagnostic and does not qualify imaginary accuracy or restore acceptance.\n\n"
            "The95-member source archive contains36 instrumented files,36 restored generic baseline files and23 historical production files. "
            "Removing the29 reviewed diagnostic lines restores the compiled/tested generic source bytes. "
            "The durable generic package and its original failed build remain separate immutable prerequisites; no current production file is guarded. "
            "The original25 exact tests are reused through this source restoration and the recorded independent review, without a new phase test run.\n\n"
            "Payload origins retain original paths. External hashes bind the frozen native closure, toolchain, binaries and complete durable baseline. "
            "Reproduction needs those exact dependencies and a privately supplied license. Use new attempt paths; never replace historical evidence. "
            "The packaging script only reads, hashes and copies saved evidence.\n\n"
            + "\n".join("- " + item for item in LIMITATIONS) + "\n")
        for path, digest in observed.items():
            require(sha(path) == digest, f"artifact changed during packaging: {path}")
        require(attempts == sorted(p for p in H.glob("n6-rank7-*") if p.is_dir())
                and comparison_paths == sorted(H.glob("comparison-*.json"))
                and diagnostic_paths == sorted(H.glob("diagnostic-comparison-*.json"))
                and reviewed_drafts == sorted(p for p in (H / "diagnostic-reviewed-draft-001").rglob("*") if p.is_file())
                and audit256_inventory == sorted(AUDIT_256.iterdir()),
                "new evidence appeared during packaging")
        files = {str(p.relative_to(stage)): sha(p) for p in stage.rglob("*") if p.is_file()}
        qualification = dict(schema_version=1, status=status, scope=SCOPE,
            acceptance_qualified=False, full_array_original_agreement_qualified=False, precision_convergence_qualified=False,
            complete_successful_initial_capture=True, numerical_comparison_failed=True,
            lifecycle_qualified=False, performance_qualified=False, qualified_working_bits=[],
            requested_bits=53, moments=330, complex_slots_per_precision=1320, normalized_original_tolerance="1e-10",
            diagnostic_convergence_tolerance="2^-80", observed_diagnostic_convergence=measured_convergence,
            initial_original_failure_count=90, initial_exact_zero_complex_poles=990,
            initial_maximum_original_error=primary_audit["numerical"]["maximum_error"],
            maximum_diagnostic_precision_difference=maximum_precision_difference, diagnostic=diagnostic_record,
            numerical_attempts=attempt_records, comparator_attempts=comparison_records,
            phase_build_sha256=build_sha, protocol_sha256=PROTOCOL_SHA, comparator_sha256=COMPARE_SHA,
            diagnostic_protocol_sha256=DIAGNOSTIC_PROTOCOL_SHA, diagnostic_comparator_sha256=DIAGNOSTIC_COMPARE_SHA,
            exact_tests=25, exact_tests_reused=True, phase_test_binary_built=False,
            generic_base_qualification_sha256=BASE_SHA, instrumentation_independent_review_sha256=REVIEW_SHA,
            independent_audit_packet_path=str(AUDIT_DURABLE.relative_to(R)), independent_audit_manifest_sha256=AUDIT_MANIFEST_SHA,
            independent_audit_copy_receipt_sha256=AUDIT_COPY_SHA, archive_members=len(source_hashes),
            independent256_audit_packet_path="independent256audit",
            independent256_audit_manifest_sha256=AUDIT_256_MANIFEST_SHA, independent256_audit_sha256=AUDIT_256_SHA,
            independent256_audit_files=11, independent256_audit_upstream_bindings=280,
            independent256_audit_diagnostic_only=True, imaginary_accuracy_qualified=False,
            payload_files=len(files), external_artifact_count=len(external), limitations=LIMITATIONS,
            written_utc=datetime.now(timezone.utc).isoformat(), files=files)
        save(stage / "qualification.json", qualification)
        require(not DESTINATION.exists(), "destination appeared during packaging")
        stage.rename(DESTINATION)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print(json.dumps(dict(status=status, destination=str(DESTINATION), payload_files=len(files),
        archive_members=len(source_hashes), qualification_sha256=sha(DESTINATION / "qualification.json"))))


if __name__ == "__main__":
    main()

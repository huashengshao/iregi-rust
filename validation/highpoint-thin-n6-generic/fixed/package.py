#!/usr/bin/env python3
"""Package completed private generic N6 evidence without rerunning its gates.

Run only after the chosen captures/comparisons are final and packaging is
authorized. This script never invokes a compiler, integral, or comparator.
It refuses active attempts and an existing destination. Native dependencies
and executable binaries are verified and inventoried, never copied.
"""
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import ast
import gzip
import hashlib
import io
import json
import re
import shutil
import tarfile
import tempfile

R = Path(__file__).resolve().parents[3]
H = R / "target/public-highpoint/thin-n6-generic-fixed"
OLD = R / "target/public-highpoint/thin-n6-generic"
DESTINATION = R / "validation/highpoint-thin-n6-generic"
BASE = R / "validation/highpoint-thin-n6-mask"
PROTOCOL_SHA = "6979062d32069579b5d12f3d63b6a38e10eae9e3f60a257a60df04714f4348a3"
BUILD_SHA = "0c01555ac79dc9703492a4f4288e471a50eb3d84f98411360a49b3c189ce755a"
EXACT_SHA = "a19f9624edd2a571fa4a003a56ad4387f3ae03123f94345347bdddd549d2ed6c"
COMPARE_SHA = "47a26345e851ba38aa98a52d2b6ac1ce642c170ead611b5db1630d226109f768"
FAILED_BUILD_SHA = "034a3dc4885bb28240db006a5ba8d4324ce966b844f72f5386abef203e6cc8ff"
BASE_SHA = "6ef88dfd99a32746f641b2485b2cd95b7bddfd186dc45148287874af764f4357"
AUDIT_SHA = "3660255dd4059a5442f626412c97ee7751fab068c8d113ce81a47f5dc2d459eb"
AUDIT_SCRIPT_SHA = "72036c492a45c9e93cdbc6887fcd1d6b99993ed5a908cee7bb10d339aae983a4"
SCOPE = ("Private generic thin N6, retained base fixture, rank3, native Components, "
         "FromShifts/Preserve/unit powers/h0 and requested53. Exact symbolic tests "
         "also exercise generic indexing through rank7; they are not rank7 numerical qualification.")
LIMITATIONS = [
    "No production adoption, performance, N7, generalized-input or SuppliedG qualification.",
    "No rank3 lifecycle, numerical Dual, complex-mass or rank7 numerical coverage.",
    "Existing ordinary primal sensitivity model; no rigorous compounded Taylor bound; quadrature imports unsupported.",
    "Working precision records representation precision, not proof of achieved requested accuracy.",
    "Executable/native binaries are not embedded; reproduction requires the recorded external closure and fresh attempt paths.",
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


def test_log(text, expected):
    require(re.findall(r"^running (\d+) tests?$", text, re.M) == [str(len(expected))], "test count differs")
    completed, pending = [], None
    for line in text.splitlines():
        match = re.match(r"^test ([A-Za-z0-9_:]+) \.\.\.\s*(.*)$", line)
        if match:
            require(pending is None, "unfinished test")
            pending, tail = match.groups()
            if tail == "ok":
                completed.append(pending)
                pending = None
            else:
                require(tail not in {"FAILED", "ignored"}, "failed or ignored test")
        elif line.strip() == "ok":
            require(pending is not None, "unbound test completion")
            completed.append(pending)
            pending = None
    require(pending is None and len(completed) == len(expected) and set(completed) == expected,
            "test membership differs")
    summary = re.findall(r"^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured;", text, re.M)
    require(summary == [(str(len(expected)), "0", "0", "0")], "test summary differs")


def main():
    require(not DESTINATION.exists(), "package destination already exists")
    observed, payload, source_members, attempt_records, comparison_records = {}, {}, {}, [], []

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
        require(name not in payload, f"duplicate payload: {name}")
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
    bind(H / "numerical-protocol.json", PROTOCOL_SHA)
    bind(H / "build-001/build.json", BUILD_SHA)
    bind(H / "exact-001/run.json", EXACT_SHA)
    bind(OLD / "build-001/build.json", FAILED_BUILD_SHA)
    protocol = read(H / "numerical-protocol.json")
    require(protocol["source_review_status"] == "approved_source_only" and "/root" in protocol["reviewers"],
            "numerical protocol is not ROOT-reviewed")
    for name, digest in protocol["artifacts"].items():
        bind(R / name, digest)

    # The original compile failed only in tests. Its successful core object is
    # an unqualified observation, not a retrospectively successful build.
    original = read(OLD / "build-001/build.json")
    fixed = read(H / "build-001/build.json")
    require(original["status"] == "failed" and [s["name"] for s in original["steps"]] == ["core", "tests"]
            and original["steps"][0]["exit_code"] == 0 and original["steps"][1]["exit_code"] != 0,
            "original compile failure is not preserved")
    require(fixed["status"] == "passed" and fixed["inputs_unchanged"] is True
            and fixed["bound_seconds"] == 180 and set(fixed["outputs"]) == {"libiregi_rust.rlib", "tests", "driver"},
            "fixed build is not complete")
    for label, directory, build in [("original", OLD, original), ("fixed", H, fixed)]:
        closure(build, directory / "build-001")
        for name in ["base.json", "source-review.json", "proposed-protocol.json", "build.py", "run.py", "driver.rs"]:
            copy_source(directory / name, f"{label}/{name}")
        copy_source(directory / "build-001/build.json", f"{label}/build-001/build.json")
        for step in build["steps"]:
            name = step["name"] + ".log"
            copy_source(directory / "build-001" / name, f"{label}/build-001/{name}")
        core = directory / "core"
        disk_sources = {str(p.resolve()): p for p in core.rglob("*") if p.is_file()}
        recorded_sources = {n: d for n, d in build["inputs"].items() if Path(n).is_relative_to(core)}
        require(set(disk_sources) == set(recorded_sources), f"{label} compiled source inventory differs")
        for name, digest in recorded_sources.items():
            path = disk_sources[name]
            bind(path, digest)
            source_members[f"{label}/{path.relative_to(core)}"] = path
    failed_core = OLD / "build-001/libiregi_rust.rlib"
    require(failed_core.is_file(), "original successful core output observation missing")
    failed_core_sha = bind(failed_core)
    for name in ["test-fix.json", "run-numeric.py", "compare.py", "numerical-protocol.json", "package.py"]:
        copy_source(H / name, f"fixed/{name}")

    production = R / "crates/iregi-rust/src"
    guarded = {n: d for n, d in fixed["inputs"].items() if Path(n).is_relative_to(production)}
    require(set(guarded) == {str(p.resolve()) for p in production.rglob("*.rs")}, "production guard inventory differs")
    for name, digest in guarded.items():
        require(original["inputs"].get(name) == digest, "production guards differ between attempts")
        bind(name, digest)
        source_members["production/" + str(Path(name).relative_to(R))] = Path(name)
    require(len(source_members) == 95, "expected 36 original + 36 fixed + 23 production sources")

    exact = read(H / "exact-001/run.json")
    require(exact["status"] == "passed" and exact["inputs_unchanged"] is True and exact["bound_seconds"] == 180,
            "exact gate is incomplete")
    closure(exact, H / "exact-001")
    node = next(n for n in ast.parse((H / "compare.py").read_text()).body
                if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "EXACT_TESTS" for t in n.targets))
    tests = ast.literal_eval(node.value)
    require([len(names) for names in tests.values()] == [10, 7, 2, 5, 1], "exact test scope differs")
    require([step["command"][4] for step in exact["steps"]] == list(tests)
            and all(s["exit_code"] == 0 and not s.get("timeout") for s in exact["steps"])
            and sum(s["seconds"] for s in exact["steps"]) <= 180, "exact runtime failed or exceeded bound")
    copy_source(H / "exact-001/run.json", "fixed/exact-001/run.json")
    for i, expected in enumerate(tests.values()):
        path = H / f"exact-001/step-{i}.log"
        test_log(path.read_text(), expected)
        copy_source(path, f"fixed/exact-001/step-{i}.log")

    attempts = sorted(p for p in H.glob("n6-rank3-*") if p.is_dir())
    require(attempts, "no numerical capture to preserve")
    for directory in attempts:
        match = re.fullmatch(r"n6-rank3-(128|256)-(\d{3})", directory.name)
        require(match is not None, "unrecognized numerical attempt")
        run = read(directory / "run.json")
        require(run["status"] in {"passed", "failed"}, f"active/incomplete capture: {directory}")
        require(run.get("inputs_unchanged") is True and run["bound_seconds"] == 180,
                "capture lacks completed source guards")
        require(set(run.get("outputs", {})) <= {"result.json", "step-0.log"}, "unexpected numerical artifacts")
        require({p.name for p in directory.iterdir()} == set(run["outputs"]) | {"run.json"}, "unrecorded capture artifact")
        closure(run, directory)
        for name in ["run.json", *run["outputs"]]:
            copy_source(directory / name, f"fixed/{directory.name}/{name}")
        result = read(directory / "result.json") if "result.json" in run["outputs"] else None
        attempt_records.append(dict(attempt=directory.name, working_bits=int(match[1]), status=run["status"],
            result_status=None if result is None else result.get("status"), declared_bound_seconds=180,
            elapsed_seconds=run.get("elapsed_seconds"), steps=run["steps"],
            run_sha256=bind(directory / "run.json"), numerically_qualified=False))

    qualified_bits, paired, records, maximum_precision_difference = set(), False, [], None
    for path in sorted(H.glob("comparison-*.json")):
        require(path.name in {"comparison-128.json", "comparison-128-256.json"}, "unrecognized comparator attempt")
        comparison = read(path)
        require(comparison["status"] in {"passed", "failed"}, "active/incomplete comparator output")
        closure(comparison, H)
        copy_source(path, f"fixed/{path.name}")
        comparison_records.append(dict(name=path.name, status=comparison["status"], sha256=bind(path),
                                       error=comparison.get("error")))
        if comparison["status"] == "failed":
            continue
        require(comparison["full_array_original_agreement_qualified"] is True
                and comparison["normalized_original_tolerance"] == "1e-10"
                and comparison["exact_gate"]["total_tests"] == 25, "successful comparator scope differs")
        required_bindings = {str(H / "compare.py"): COMPARE_SHA,
                             str(H / "numerical-protocol.json"): PROTOCOL_SHA,
                             str(H / "build-001/build.json"): BUILD_SHA,
                             str(H / "exact-001/run.json"): EXACT_SHA}
        require(all(comparison["input_sha256"].get(k) == v for k, v in required_bindings.items()),
                "successful comparator is bound to a different attempt")
        bits = [r["working_bits"] for r in comparison["records"]]
        expected_bits = [128] if path.name == "comparison-128.json" else [128, 256]
        require(bits == expected_bits, "precision coverage differs")
        for record in comparison["records"]:
            require(record["complex_slots"] == 140 and record["real_components"] == 280
                    and record["exact_zero_complex_poles"] == 105
                    and Decimal(0) <= Decimal(record["maximum_original_error"]) <= Decimal("1e-10"),
                    "slot coverage/tolerance differs")
            attempt = next((a for a in attempt_records if a["attempt"] == f'n6-rank3-{record["working_bits"]}-001'), None)
            require(attempt is not None and attempt["status"] == "passed" and attempt["result_status"] == "all_lanes_success",
                    "qualified precision lacks its successful capture")
            for name in ["run.json", "result.json", "step-0.log"]:
                artifact = H / attempt["attempt"] / name
                require(comparison["input_sha256"].get(str(artifact)) == bind(artifact), "capture/comparator binding differs")
            attempt["numerically_qualified"] = True
        qualified_bits.update(bits)
        if len(bits) == 2:
            require(comparison["precision_convergence_qualified"] is True
                    and comparison["convergence_tolerance"] == "2^-80"
                    and Fraction(0) <= Fraction(comparison["maximum_precision_difference"]) <= Fraction(1, 2**80),
                    "paired precision gate is not qualified")
            paired = True
            records = comparison["records"]
            maximum_precision_difference = comparison["maximum_precision_difference"]
        else:
            require(comparison["precision_convergence_qualified"] is False, "single precision claims convergence")
            if not records:
                records = comparison["records"]

    # The final qualified package additionally requires the independent saved-
    # array arithmetic and provenance review, including its reproducible script.
    audit_path = H / "independent-rank3-audit.json"
    bind(audit_path, AUDIT_SHA)
    bind(H / "independent-rank3-audit.py", AUDIT_SCRIPT_SHA)
    audit = read(audit_path)
    require(audit["status"] == "passed" and audit["full_array_original_agreement_qualified"] is True
            and audit["precision_convergence_qualified"] is True and audit["exact_tests"] == 25
            and audit["compared_original_complex_slots"] == 280 and audit["compared_convergence_complex_slots"] == 140
            and audit["original_tolerance"] == "1e-10" and audit["convergence_tolerance"] == "2^-80"
            and audit["lifecycle_qualified"] is False and audit["performance_qualified"] is False
            and audit["independent_provenance_review"]["status"] == "passed",
            "independent final array/provenance audit is incomplete")
    require([r["working_bits"] for r in audit["records"]] == [128, 256]
            and all(r["complex_slots"] == 140 and r["exact_zero_complex_poles"] == 105 for r in audit["records"]),
            "independent audit slot coverage differs")
    require(paired and qualified_bits == {128, 256}, "independent paired audit lacks its final paired gate")
    closure(audit, H)
    for path in [H / "comparison-128-256.json", H / "n6-rank3-128-001/result.json",
                 H / "n6-rank3-256-001/result.json", H / "build-001/build.json",
                 H / "exact-001/run.json", H / "numerical-protocol.json", H / "independent-rank3-audit.py"]:
        require(audit["input_sha256"].get(str(path)) == bind(path), f"independent audit binding differs: {path}")
    copy_source(audit_path, "fixed/independent-rank3-audit.json")
    copy_source(H / "independent-rank3-audit.py", "fixed/independent-rank3-audit.py")

    # Preserve base/reference provenance locally without copying native binaries
    # or duplicating the already committed rank2 source archive.
    bind(BASE / "qualification.json", BASE_SHA)
    base = read(BASE / "qualification.json")
    for name, digest in base["files"].items():
        bind(BASE / name, digest)
    for name in ["qualification.json", "archive-manifest.json", "README.md"]:
        copy_source(BASE / name, f"rank2-base/{name}")
    for name in ["fixture-conditioned_masses.json", "reference-conditioned_masses.json", "compare_public.py", "qualification.json"]:
        copy_source(R / "validation/public-highpoint" / name, f"reference/{name}")
    for path, name in [(R / "target/e6-direct-n2/preparation.json", "dependency-preparation.json"),
                       (R / "target/core-fused-cse-census/supplemental-deps.json", "supplemental-dependencies.json")]:
        copy_source(path, "provenance/" + name)

    stage = Path(tempfile.mkdtemp(prefix=".thin-n6-generic-", dir=DESTINATION.parent))
    try:
        origins = {}
        for name, path in sorted(payload.items()):
            destination = stage / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(path.read_bytes())
            require(sha(destination) == observed[str(path)], f"payload changed while copying: {path}")
            origins[name] = dict(original_path=str(path.relative_to(R)), sha256=observed[str(path)])
        archive_manifest = {}
        with (stage / "sources.tar.gz").open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                with tarfile.open(mode="w", fileobj=compressed) as archive:
                    for name, path in sorted(source_members.items()):
                        data = path.read_bytes()
                        digest = hashlib.sha256(data).hexdigest()
                        require(digest == observed[str(path.resolve())], f"source changed while archiving: {path}")
                        info = tarfile.TarInfo(name)
                        info.size, info.mode, info.mtime = len(data), 0o644, 0
                        archive.addfile(info, io.BytesIO(data))
                        archive_manifest[name] = digest
        save(stage / "archive-manifest.json", dict(archive_sha256=sha(stage / "sources.tar.gz"), members=archive_manifest))
        save(stage / "payload-origins.json", origins)
        copied_paths = {str(p) for p in payload.values()} | {str(p.resolve()) for p in source_members.values()}
        external = {p: d for p, d in observed.items() if p not in copied_paths}
        save(stage / "external-artifact-hashes.json", dict(scope="Verified external closure; not embedded binaries.",
             files=external, failed_original_core_observation=dict(path=str(failed_core.relative_to(R)), sha256=failed_core_sha,
             qualification="Core step succeeded; overall build failed. This hash was observed at packaging, not recorded as a successful build output.")))
        status = ("private_retained_n6_rank3_qualified" if paired else
                  "private_retained_n6_rank3_single_precision_agreement" if qualified_bits else
                  "private_retained_n6_rank3_unqualified_capture")
        readme = (
            f"This package preserves a **private** generic thin N6 experiment. Recorded outcome: `{status}`.\n\n"
            + SCOPE + "\n\n"
            "`original/` retains the first test-compilation failure. The `fixed/` core source differs in the settings assertion only; "
            "its successful build and all 25 exact tests are retained. The original core output remains unqualified. "
            "`base.json` describes the initial rank2 copy; the authoritative generic compiled sources are the build input hashes.\n\n"
            f"Qualified numerical precisions: {sorted(qualified_bits)}. Precision convergence qualified: {paired}. "
            "Only passed saved comparisons confer numerical agreement; successful process exit alone does not. "
            "All numerical attempts, partial ledgers, failures and comparator outputs found at packaging are retained. "
            "The main gate compares all 35 moments and four complex Laurent slots to stable untouched original IREGI IBP, "
            "using Q^(4-2N+moment rank), complex norm/max(1, normalized reference norm), and unchanged 1e-10 tolerance. "
            "Only an accepted paired comparison establishes normalized 2^-80 convergence.\n\n"
            "The mandatory independent audit recomputes all 280 original-reference comparisons and 140 precision comparisons "
            "at 200 decimal digits, and independently reviews the source/build/run chain. Its script and complete input hashes are retained.\n\n"
            "The 95-member source archive contains both complete 36-file core trees, their include_str fixtures, and 23 production files "
            "guarded during compilation. It binds historical sources without requiring mutable production files to remain frozen forever. "
            "Payload origins and external artifact hashes preserve original paths. Native dependencies, toolchain and executables are not copied. "
            "The retained rank2 package remains a separate prerequisite, with its qualification/archive manifest copied and all payload hashes verified.\n\n"
            "Reproduction requires the explicit frozen dependencies and private license environment. Restore the historical paths or prepare "
            "a separately versioned relocation; never overwrite captured attempts or substitute a rebuilt binary for its historical hash. "
            "The packager reads and hashes evidence only; it does not rerun numerical gates.\n\n"
            + "\n".join("- " + item for item in LIMITATIONS) + "\n"
        )
        (stage / "README.md").write_text(readme)
        # Verify the whole distinct observed closure after copying. This also
        # rejects a capture that resumed or changed during packaging.
        for path, digest in observed.items():
            require(sha(path) == digest, f"artifact changed during packaging: {path}")
        require(attempts == sorted(p for p in H.glob("n6-rank3-*") if p.is_dir()), "new attempt appeared during packaging")
        require({p.name for p in H.glob("comparison-*.json")} == {c["name"] for c in comparison_records},
                "new comparison appeared during packaging")
        files = {str(p.relative_to(stage)): sha(p) for p in stage.rglob("*") if p.is_file()}
        qualification = dict(schema_version=1, status=status, scope=SCOPE, exact_tests=25,
            qualified_working_bits=sorted(qualified_bits), requested_bits=53, moments=35,
            complex_slots_per_precision=140, normalized_original_tolerance="1e-10",
            precision_convergence_qualified=paired, convergence_tolerance="2^-80" if paired else None,
            maximum_original_error=str(max(Decimal(r["maximum_original_error"]) for r in records)) if records else None,
            maximum_precision_difference=maximum_precision_difference,
            records=records, numerical_attempts=attempt_records, comparator_attempts=comparison_records,
            original_failure=dict(status="test_compilation_failed", manifest_sha256=FAILED_BUILD_SHA,
                                  corrected_only="cfg(test) settings equality via serde_json::to_value"),
            fixed_build_sha256=BUILD_SHA, exact_run_sha256=EXACT_SHA, numerical_protocol_sha256=PROTOCOL_SHA,
            base_rank2_qualification_sha256=BASE_SHA, archive_members=len(archive_manifest),
            independent_audit_sha256=AUDIT_SHA, independent_audit_script_sha256=AUDIT_SCRIPT_SHA,
            payload_files=len(files), external_artifact_count=len(external), limitations=LIMITATIONS,
            written_utc=datetime.now(timezone.utc).isoformat(), files=files)
        save(stage / "qualification.json", qualification)
        require(not DESTINATION.exists(), "destination appeared during packaging")
        stage.rename(DESTINATION)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print(json.dumps(dict(status=status, destination=str(DESTINATION), payload_files=len(files),
                         archive_members=len(archive_manifest), qualification_sha256=sha(DESTINATION / "qualification.json"))))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Package already terminal evidence; no compiler, kernel or evaluator calls."""
from pathlib import Path
import datetime
import gzip
import hashlib
import io
import json
import re
import tarfile

ROOT = Path.cwd().resolve()
CAPSULE = ROOT / "validation/native-f64-sixpoint-regression"
ORIGIN = ROOT / "target/native-f64-sixpoint-port/six-regression"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def info(path):
    return dict(path=str(Path(path).relative_to(ROOT)), sha256=sha(path), bytes=Path(path).stat().st_size)


def main():
    assert (ROOT / "PLAN.md").is_file() and CAPSULE.is_dir(), "execute from project root"
    audit_root = ROOT / "target/resume-20261025-review"
    numeric_path = audit_root / "six-regression-independent-numeric-audit.json"
    provenance_path = audit_root / "six-regression-independent-provenance-audit.json"
    numeric, provenance = read(numeric_path), read(provenance_path)
    assert sha(numeric_path) == "84c4f7ea26fcead4f164458ad13fafd2e66af8e90129ee5d855d8af2ac05d953"
    assert sha(provenance_path) == "187256e843fe27c2fbf197aa8ffb76b220a979cee097835b08a150d34a65c049"
    assert numeric["status"] == "independent-retained-n6-saved-numerical-audit-passed" and not numeric["blocking_findings"]
    assert provenance["status"] == "passed-independent-retained-n6-provenance-audit" and not provenance["findings"]
    sources = {}
    omitted, bytecode = [], []
    for path in sorted(ORIGIN.rglob("*")):
        if not path.is_file():
            continue
        relative = str(path.relative_to(ORIGIN))
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            bytecode.append(info(path))
            continue
        with path.open("rb") as stream:
            magic = stream.read(8)
        if magic.startswith((b"\x7fELF", b"!<arch>\n")) or path.suffix in (".rlib", ".rmeta", ".a", ".so"):
            omitted.append(info(path))
            continue
        sources[relative] = path
    for name in ("audit_six_regression_independent.py", "six-regression-independent-numeric-audit.json",
                 "audit_six_regression_provenance.py", "six-regression-independent-provenance-audit.json"):
        sources["reviews/" + name] = audit_root / name
    assert len(omitted) == 17
    payloads = {}
    archive_path = CAPSULE / "evidence.tar.gz"
    with archive_path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for relative, path in sorted(sources.items()):
                    data = path.read_bytes()
                    assert not data.startswith((b"\x7fELF", b"!<arch>\n"))
                    assert not re.search(rb"S-130-[0-9]{4}\.[0-9]{2}\.[0-9]{2}-[A-Z0-9]{40,}", data)
                    member = tarfile.TarInfo(relative)
                    member.size, member.mtime, member.mode = len(data), 0, 0o644
                    archive.addfile(member, io.BytesIO(data))
                    payloads[relative] = dict(origin=str(path.relative_to(ROOT)), bytes=len(data),
                                             sha256=hashlib.sha256(data).hexdigest(), kind="exact-copy")
    winddown = ROOT / "validation/winddown"
    parent_archive = winddown / "native-f64-sixpoint-composition.tar.gz"
    parent_manifest = winddown / "manifest.json"
    parent_members = read(parent_manifest)["archives"]["native-f64-sixpoint-composition"]["members"]
    with tarfile.open(parent_archive, "r:gz") as archive:
        source = json.load(archive.extractfile("source-inventory.json"))
        compiled = json.load(archive.extractfile("qualification/codegen-preparation.json"))
    inherited = {}
    for category, prefix, mapping in (("base", "base/", source["base"]),
                                       ("proposed", "proposed/", source["proposed"]),
                                       ("compiled", "qualification/public-source/", compiled["compiled_source_mapping"])):
        inherited[category] = {}
        for relative, expected in mapping.items():
            member = prefix + relative
            item = parent_members[member]
            assert item["sha256"] == expected
            inherited[category][relative] = dict(member=member, sha256=expected, bytes=item["bytes"])
    reused = {}
    for relative in [
        "validation/highpoint-six-point-api/source-v1/ordinary-equivalence-driver.rs",
        "validation/highpoint-six-point-api/source-v1/public-lifecycle-driver.rs",
        "validation/highpoint-six-point-api/source-v1/public-lifecycle-source.json",
        "validation/highpoint-six-point-api/source-v1/lifecycle-driver-review.json",
        "validation/highpoint-six-point-api/qualified-v2/compare.py",
        "validation/highpoint-six-point-api/qualified-v2/compare-lifecycle.py",
        "validation/highpoint-six-point-api/qualified-v2/harness_common.py",
        "validation/highpoint-six-point-api/qualified-v2/hardening.json",
        "validation/highpoint-six-point-api/qualified-v2/source-review.json",
        "validation/public-highpoint/fixture-conditioned_masses.json",
        "validation/public-highpoint/reference-conditioned_masses.json",
        "validation/public-highpoint/compare_public.py",
        "validation/public-highpoint/qualification.json",
        "validation/highpoint-thin-n6-generic/qualification.json",
        "validation/highpoint-thin-n6-generic/fixed/n6-rank3-128-001/result.json",
        "validation/highpoint-thin-n6-generic/fixed/n6-rank3-256-001/result.json",
        "validation/highpoint-six-point-api/qualification.json",
        "validation/highpoint-six-point-current-cargo/qualification.json",
        "validation/native-f64-sixpoint-constructors/qualification.json",
        "validation/native-f64-sixpoint-constructors/reviews/root-independent-saved-audit.json",
        "validation/native-f64-sixpoint-constructors/reviews/constructor-runtime-independent-review.json",
        "validation/native-f64-sixpoint-whole/qualification.json",
    ]:
        path = ROOT / relative
        reused[relative] = dict(sha256=sha(path), bytes=path.stat().st_size)
    write(CAPSULE / "parent.json", dict(status="bound-parent-source-and-committed-reference-reuse",
        source_commit="2c1f3342e189a20fef3bbf7dd9e0baa372e2b4a2", parent_archive=info(parent_archive),
        parent_manifest=info(parent_manifest), inherited_sources=inherited, reused_committed_files=reused,
        source_deltas=[], compiled_source_files_identical_to_bound_parent=True,
        relationship="Reconstruct 80 base +85 proposed +85 exact compiled source files from the sealed parent. Reuse unchanged committed drivers, numerical gates, reference captures and prerequisite qualifications. No large generated Rust algebra is duplicated."))
    write(CAPSULE / "omitted-artifacts.json", dict(status="compiled-and-bytecode-outputs-deliberately-excluded",
        compiled_products=omitted, python_bytecode=bytecode, artifact_hash_metadata_preserved=True,
        qualification_context="Exact original executable/rlib bytes were SHA-guarded before/after execution and independently audited on the original machine. Portable validation does not claim those omitted binaries are available."))
    summary = read(ORIGIN / "stage-summary.json")
    write(CAPSULE / "qualification.json", dict(status="private-combined-native-policy-retained-n6-regression-qualified",
        created_utc=summary["created_utc"], source_context="2c1f3342e189a20fef3bbf7dd9e0baa372e2b4a2",
        private_combined_patch_sha256="70b5f94487f79d25c9bc831c0895fe2970ba8e222297ba0baf9f683d67101f9a",
        scope=summary["scope"], compiler_products=7, runtime_stages=10, saved_gates=8, failed_or_unrun_stages=[],
        independent_numeric_audit_status=numeric["status"], independent_numeric_audit_sha256=sha(numeric_path),
        independent_numeric_checks=numeric["checks"], independent_provenance_audit_status=provenance["status"],
        independent_provenance_audit_sha256=sha(provenance_path), independent_provenance_bound_files=provenance["unique_bound_files_rehashed"],
        totals=summary["totals"], working_precisions=[128, 256], requested_bits=53,
        original_tolerance="1e-10", convergence_tolerance="2^-80",
        maximum_original_error="2.425355322437416e-12", maximum_convergence_error="1.4738132606190866e-34",
        historical_rank3_exact_differences=0, lifecycle_singleton_value_precision_sign_differences=0,
        compiler_cap_seconds=180, compiler_postwork_reserve_seconds=25, ordinary_cap_seconds=120,
        highpoint_cap_seconds=180, runtime_postwork_reserve_seconds=20,
        owned_groups=17, all_owned_groups_absent=True, constructor_policies="SixPoint parent and children explicitly Symbolica; ordinary default constructors unchanged; no backend argument added to public SixPoint",
        not_qualified_by_this_capsule=dict(current_cargo_feature_forwarding=True, production_application_or_default_adoption=True,
            explicit_native_abc_execution=True, broad_native_runtime=True, public_highpoint_dual=True,
            n6_f64_or_doublefloat_accuracy=True, complex_mass_generalized_or_higher_rank_highpoint=True,
            n7_or_rank7=True, performance_or_parity=True),
        production_mutations=False, current_cargo_execution=False, benchmark_execution=False,
        source_integrity_note="Compiler environment is applied by the hash-bound runner using the frozen command recipe; no per-step env field is claimed. Original outputs lack byte-count fields where absent; actual SHA guards establish artifact identity."))
    metadata = {}
    for path in sorted(CAPSULE.iterdir()):
        if path.is_file() and path.name not in ("manifest.json", "evidence.tar.gz"):
            metadata[path.name] = dict(sha256=sha(path), bytes=path.stat().st_size)
    write(CAPSULE / "manifest.json", dict(status="portable-new-evidence-capsule-with-bound-parent-source-reuse",
        archive=dict(path="evidence.tar.gz", sha256=sha(archive_path), bytes=archive_path.stat().st_size,
                     uncompressed_bytes=sum(item["bytes"] for item in payloads.values()), members=payloads),
        metadata_files=metadata, content_audit=dict(ELF_or_ar_payloads=0, provided_license_occurrences=0,
            compiled_products_omitted=len(omitted), python_bytecode_omitted=len(bytecode),
            archived_source_context="New scripts, receipts, raw outputs, complete text logs and reviews only; 250 inherited source files remain in the bound parent archive")))
    print(json.dumps(dict(status="packaged", payloads=len(payloads), compressed_bytes=archive_path.stat().st_size,
                          qualification_sha256=sha(CAPSULE / "qualification.json"), manifest_sha256=sha(CAPSULE / "manifest.json"))))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Package frozen checked-G core test evidence; no producer/native execution."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile

ROOT = Path.cwd().resolve()
HERE = Path(__file__).resolve().parent
Q = "target/checked-g-generalized-qualification"
C = "target/checked-g-generalized-composed"
F = "target/checked-g-generalized-frontend-proposal"
INVENTORY = "target/checked-g-generalized-core-capsule-prep/source-delta-inventory.json"
PREFIX = "/shared/external/iregi/iregi-rust/"
QUAL = "1702c9f1dfb191871586de9cb248f75529bb4e10806aceb965f93ecdc4ab3f6f"
BUILD_PINS = {
    "build-001": "b8b9a289e8ec2240315e8f22311353184e5eff8b610e05678fb20f6bd85d2517",
    "build-002": "f7366af41461e7b7fb3f2f537d4c589e19d8b5b0b773d951e8ef67ba9ca10bf3",
    "build-003": "71eeca714e839be16c331ca9cf3985d9d17365be13dad04aecb6c73c6cf590cb",
    "build-004": "371dd8662f702ca0bcb4425dbbb79ae803b2069fc22ab7c95d3b58d35ba3e106",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {"sha256": sha(body), "bytes": len(body)}


def scan(name, body):
    p = Path(name)
    need(name and not p.is_absolute() and ".." not in p.parts and str(p) == name, "safe relative alias")
    need(p.suffix not in {".o", ".mod", ".smod", ".pyc", ".so", ".a", ".dll", ".dylib"}
         and "__pycache__" not in p.parts, "no compiled product/cache")
    need(not body.startswith((b"\x7fELF", b"!<arch>", b"MZ")), "no native product bytes")
    need(not re.search(rb"S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}", body), "no license literal")


def main():
    need(ROOT.name == "iregi-rust" and HERE == ROOT/"validation/checked-g-generalized-core-tests", "project cwd and designated capsule")
    existing = {p.name for p in HERE.iterdir() if p.is_file()}
    need(existing == {"package.py", "README.md", "check.py"}, "initial capsule must contain exactly package, README and completed checker")
    need(not any(p.is_dir() or p.is_symlink() for p in HERE.iterdir()), "regular flat capsule source files")
    files, contexts, omitted = {}, {}, {}

    def add(name, expected=None):
        path = ROOT/name
        need(path.is_file() and not path.is_symlink(), "regular saved source/data " + name)
        body = path.read_bytes()
        scan(name, body)
        if expected is not None:
            need(sha(body) == expected, "saved source/data hash " + name)
        need(name not in files or files[name] == body, "same-alias byte collision")
        files[name] = body
        return body

    # Controllers, protocols, selection, fixes, bridge and final qualification.
    for path in (ROOT/Q).iterdir():
        if path.is_file() and path.suffix in {".py", ".json"}:
            add(str(path.relative_to(ROOT)))
    # These two small historical receipts supplied the retained 82 test names;
    # their native products and original source closures are not dependencies.
    selection = json.loads(files[Q+"/focused-selection.json"])
    for name in selection["parent_receipts"]:
        add(name)
    need(sha(files[Q+"/focused-qualification.json"]) == QUAL, "frozen exact focused qualification")
    builds = {}
    for build, expected in BUILD_PINS.items():
        prefix = Q+"/"+build
        receipt = json.loads(add(prefix+"/receipt.json", expected))
        need(len(receipt["source_files"]) == 158, "158 selected source paths in every build")
        builds[build] = receipt
        # A frozen-* product is omitted by its recorded identity without reading it.
        for path in (ROOT/prefix).rglob("*"):
            if path.is_file() and "source-snapshot" not in path.parts and "__pycache__" not in path.parts and not path.name.startswith("frozen-"):
                add(str(path.relative_to(ROOT)))
        source_prefix = prefix+"/source-snapshot/"
        for name, digest in receipt["source_files"].items():
            add(source_prefix+name, digest)
        contexts[build] = {"source_files": receipt["source_files"], "source_alias_prefix": source_prefix,
                           "receipt_sha256": expected, "status": receipt["status"]}
        for product in receipt["products"].values():
            name = product["path"].removeprefix(PREFIX)
            need(name != product["path"] and name not in files, "omitted native product has a project-local metadata path")
            need(name not in omitted or omitted[name] == product["sha256"], "same native product metadata identity")
            omitted[name] = product["sha256"]
    anchor = builds["build-003"]["source_files"]
    for build, receipt in builds.items():
        need(set(receipt["source_files"]) == set(anchor), "same selected source paths across all builds")
    need([sum(digest != anchor[name] for name, digest in builds[build]["source_files"].items())
          for build in BUILD_PINS] == [8, 4, 0, 1], "exact source-delta cardinalities")
    versions = {(name, digest) for receipt in builds.values() for name, digest in receipt["source_files"].items()}
    need(len(versions) == 167, "158 anchor plus nine additional path/hash versions")
    for name in anchor:
        files[name] = files[Q+"/build-003/source-snapshot/"+name]
    for tag in ["tests-001", "tests-002"]:
        for path in (ROOT/Q/tag).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                add(str(path.relative_to(ROOT)))

    # Initial pre-compiler-fix source packet, rather than a later live candidate.
    for suffix in ["proposal.json", "generalized-g-mass.patch", "application.json",
                   "independent-source-review.json", "origin-paths.json"]:
        add(C+"/"+suffix)
    core = json.loads(files[C+"/proposal.json"])
    need(len(core["files"]) == 19, "original 19-file composed packet")
    for name, row in core["files"].items():
        add(C+"/candidate/"+name, row["candidate_sha256"])
    for suffix in ["proposal.json", "frontend.patch", "application.json"]:
        add(F+"/"+suffix)
    frontend = json.loads(files[F+"/proposal.json"])
    need(len(frontend["files"]) == 4, "original four-file frontend packet")
    for name, row in frontend["files"].items():
        add(F+"/"+name, row["candidate_sha256"])
    add(INVENTORY, "cfb4d3e41ea74adf5cf92c321741bc968eef9e8b779c0f5b25b9ffe81ac34932")
    need(sha(files[C+"/application.json"]) == builds["build-003"]["core_application_sha256"]
         and sha(files[F+"/application.json"]) == builds["build-003"]["frontend_application_sha256"]
         and sha(files[C+"/independent-source-review.json"]) == builds["build-003"]["independent_review_sha256"], "historical application and source-review bindings")

    members, preserved, origins = {}, {}, {}
    for name, body in sorted(files.items()):
        member = "objects/"+sha(body)
        need(member not in members or members[member] == body, "content-address collision")
        members[member] = body
        preserved[name] = {"member": member, **desc(body)}
        original = Q+"/build-003/source-snapshot/"+name if name in anchor else name
        origins[name] = {"origin": PREFIX+original, **desc(body)}
    compiled = {name: {"alias": name, "member": preserved[name]["member"],
                       "snapshot_alias": Q+"/build-003/source-snapshot/"+name, **desc(files[name])}
                for name in anchor}
    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw, filename="", mode="wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.USTAR_FORMAT) as tar:
            for name, body in sorted(members.items()):
                item = tarfile.TarInfo(name)
                item.size, item.mode, item.mtime, item.uid, item.gid = len(body), 0o644, 0, 0, 0
                item.uname = item.gname = ""
                tar.addfile(item, io.BytesIO(body))
    capsule = {"README.md": (HERE/"README.md").read_bytes(), "check.py": (HERE/"check.py").read_bytes(),
               "package.py": Path(__file__).read_bytes(), "qualification.json": files[Q+"/focused-qualification.json"],
               "payload.tar.gz": raw.getvalue(), "payload-origins.json": (json.dumps(origins, indent=2)+"\n").encode()}
    manifest = {"schema_version": 1, "status": "source_bound_120_distinct_checked_G_generalized_core_tests_saved_evidence",
                "self_contained": True, "parent_files": {}, "borrowed_files": {},
                "capsule_files": {name: desc(body) for name, body in capsule.items()},
                "payload_members": {name: desc(body) for name, body in members.items()}, "preserved_files": preserved,
                "compiled_sources": compiled, "compiled_source_count": 158, "anchor_source_context": "build-003",
                "source_contexts": contexts, "additional_source_version_count": 9, "unique_source_path_hash_pairs": 167,
                "actual_build_receipt_sha256": BUILD_PINS["build-003"], "qualification_sha256": QUAL,
                "omitted_compiled_products": omitted, "initial_composed_candidate_source_count": 19,
                "initial_frontend_candidate_source_count": 4, "qualified_distinct_test_count": 120,
                "first_context_passes": 95, "second_context_passes": 25,
                "failed_compiler_and_test_observer_attempts_preserved": True,
                "source_compilation_and_process_provenance_are_historical": True,
                "new_native_hash_or_process_probes": False, "public_Dual_qualified": False,
                "generalized_supplied_G_numerical_full_arrays_qualified": False,
                "performance_qualified": False, "achieved_precision_qualified": False,
                "native_products_license_literals_or_python_caches_included": False,
                "complete_hermetic_dependency_build_closure_claimed": False}
    for name, body in capsule.items():
        scan(name, body)
        (HERE/name).write_bytes(body)
    (HERE/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({"status": "packaged_self_contained_checked_G_core_tests_saved_evidence",
                      "manifest_sha256": sha((HERE/"manifest.json").read_bytes()), "source_context_count": 4,
                      "anchor_sources": 158, "additional_source_versions": 9, "preserved_aliases": len(preserved),
                      "payload_members": len(members), "payload_bytes": len(capsule["payload.tar.gz"]),
                      "external_parent_files": 0}, indent=2))


if __name__ == "__main__":
    main()

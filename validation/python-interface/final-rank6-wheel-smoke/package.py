"""Package finished final-wheel smoke records, never running native software.

Run from the project root only after all six stages have passed:
  python target/python-final-rank6-wheel/capsule-proposal/package.py \
    --output validation/python-interface/final-rank6-wheel-smoke
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import shutil
import tarfile

ROOT = Path.cwd().resolve()
HERE = Path(__file__).resolve().parent
RUN = ROOT / "target/python-final-rank6-wheel"
PARENTS = (
    ("validation/rank6-current-focused-core-tests", "payload.tar.gz"),
    ("validation/checked-g-zero-mass-fallback", "payload.tar.gz"),
    ("validation/checked-g-generalized-core-tests", "payload.tar.gz"),
    ("validation/python-interface/facade-wheel-004", "sources.tar.gz"),
)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {"sha256": sha(body), "bytes": len(body)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def pack(output):
    require(ROOT == Path("/shared/external/iregi/iregi-rust"), "project working directory")
    output = output.resolve()
    require(output.is_relative_to(ROOT) and not output.exists(), "fresh owned output directory under project")
    context_body = (RUN / "context.json").read_bytes()
    context = json.loads(context_body)
    require(len(context["inputs"]) == 204 and len(context["coherent_source_files"]) == 128, "expected source scope")
    stages = ("build", "install", "import", "ordinary_eight", "checked_dual_one", "n6_one")
    evidence = {"context.json": context_body}
    for stage in stages:
        directory = RUN / (stage + "-001")
        receipt_body = (directory / "receipt.json").read_bytes()
        receipt = json.loads(receipt_body)
        require(receipt["status"] == "passed", "stage must finish successfully before packaging: " + stage)
        evidence[stage + "-001/receipt.json"] = receipt_body
        for name, digest in receipt["saved_files"].items():
            require("/" not in name and name not in (".", ".."), "direct saved stage file")
            body = (directory / name).read_bytes()
            require(sha(body) == digest, "actual saved stage file: " + name)
            evidence[stage + "-001/" + name] = body
    source_bodies = {}
    for name, digest in context["inputs"].items():
        body = (RUN / "build-001/source-snapshot" / name).read_bytes()
        require(sha(body) == digest, "actual frozen selected source snapshot: " + name)
        source_bodies[name] = body
    wanted_hashes = {sha(body) for body in source_bodies.values()}
    candidates = {}
    parent_metadata = {}
    for directory, basename in PARENTS:
        folder = ROOT / directory
        manifest_body = (folder / "manifest.json").read_bytes()
        parent = json.loads(manifest_body)
        archive_body = (folder / basename).read_bytes()
        expected = parent["sources"] if basename == "sources.tar.gz" else parent["capsule_files"][basename]
        require(desc(archive_body) == {key: expected[key] for key in ("sha256", "bytes")}, "direct source archive identity")
        archive_name = directory + "/" + basename
        parent_metadata[archive_name] = {**desc(archive_body), "manifest_path": directory + "/manifest.json", "manifest": desc(manifest_body), "members": {}}
        with tarfile.open(fileobj=io.BytesIO(archive_body), mode="r:gz") as archive:
            for member in archive:
                require(member.isfile() and not member.name.startswith("/") and ".." not in Path(member.name).parts, "safe direct source member")
                body = archive.extractfile(member).read()
                if sha(body) in wanted_hashes:
                    candidates.setdefault(sha(body), (archive_name, member.name, desc(body)))
    objects = {}
    borrowed = {}

    def reference(body, allow_borrow):
        digest = sha(body)
        if allow_borrow and digest in candidates:
            archive, member, descriptor = candidates[digest]
            borrowed.setdefault(archive, {**parent_metadata[archive], "members": {}})["members"][member] = descriptor
            return {**descriptor, "archive": archive, "member": member}
        member = "objects/" + digest
        objects[member] = body
        return {**desc(body), "archive": "local", "member": member}

    selected = {name: reference(body, True) for name, body in source_bodies.items()}
    saved = {name: reference(body, False) for name, body in evidence.items()}
    # Reject binary products and private license literals before producing files.
    spec = importlib.util.spec_from_file_location("final_wheel_saved_checker", HERE / "check.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    for name, body in [*source_bodies.items(), *evidence.items()]:
        checker.text_payload(body, name)
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", filename="", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w") as archive:
            for name, body in sorted(objects.items()):
                member = tarfile.TarInfo(name)
                member.size = len(body)
                member.mode = 0o644
                member.mtime = 0
                archive.addfile(member, io.BytesIO(body))
    payload = buffer.getvalue()
    require(len(payload) < 8 * 1024 * 1024, "compact saved text capsule")
    controls = {name: (HERE / name).read_bytes() for name in ("README.md", "check.py", "package.py")}
    controls["payload.tar.gz"] = payload
    manifest = {
        "schema_version": 1,
        "status": "passed_final_rank6_wheel_exact10_saved_smoke",
        "capsule_directory": str(output.relative_to(ROOT)),
        "scope": "Final frozen core128 and selected204 frontend/scalar dependency sources. Ten already existing installed-wheel API cases only; earlier wheel004 typing and 65API+7notebooks retained separately. Not an independent integral, rank-six completeness, performance, or complete compiler/system closure claim.",
        "source_context_sha256": sha(context_body),
        "selected_source_count": 204,
        "coherent_source_count": 128,
        "selected_sources": selected,
        "evidence": saved,
        "borrowed_archives": borrowed,
        "payload_members": {name: desc(body) for name, body in sorted(objects.items())},
        "capsule_files": {name: desc(body) for name, body in controls.items()},
        "omitted_artifacts": json.loads(evidence["build-001/wheel.json"]),
        "source_compilation_native_hash_and_process_ownership_are_historical": True,
        "native_or_integral_execution_by_checker": False,
        "parent_checker_execution": False,
        "performance_qualified": False,
        "new_independent_integrals": False,
    }
    output.mkdir(parents=True)
    for name, body in controls.items():
        (output / name).write_bytes(body)
    (output / "manifest.json").write_bytes(json_bytes(manifest))
    print(json.dumps({"status": "packaged_saved_evidence", "output": str(output.relative_to(ROOT)), "selected_source_files": len(selected), "borrowed_source_files": sum(entry["archive"] != "local" for entry in selected.values()), "own_source_files": sum(entry["archive"] == "local" for entry in selected.values()), "evidence_files": len(saved), "payload_bytes": len(payload), "manifest_sha256": sha((output / "manifest.json").read_bytes())}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    pack(parser.parse_args().output)

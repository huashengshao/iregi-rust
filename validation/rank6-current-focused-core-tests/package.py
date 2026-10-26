"""Package the completed saved cohort; no compiler, evaluator or test is run."""
from pathlib import Path
import gzip
import hashlib
import importlib.util
import io
import json
import tarfile

ROOT = Path.cwd().resolve()
HERE = ROOT / "validation/rank6-current-focused-core-tests"
RUN = ROOT / "target/rank6-final-focused-core-tests"
BUILD = ROOT / "target/ordinary-gh-parent-requalification/build-001"
PARENTS = ("checked-g-generalized-core-tests", "checked-g-zero-mass-fallback")


def sha(body):
    return hashlib.sha256(body).hexdigest()


def metadata(body):
    return {"sha256": sha(body), "bytes": len(body)}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    assert ROOT == Path("/shared/external/iregi/iregi-rust")
    build_body = (BUILD / "receipt.json").read_bytes()
    assert sha(build_body) == "faa4ea0e4ea4029a8e61dbdbb02c5324f985793008e4cdc3aec1d8341fa64845"
    build = json.loads(build_body)
    runtime = (RUN / "normal-001/receipt.json").read_bytes()
    assert sha(runtime) == "fff28b069fc2976b9d7677df70e85cc482673c3b11b74f286ccfa700c9269f97"
    assert json.loads(runtime)["status"] == "passed"
    inherited = {}
    parent_manifests = {}
    for name in PARENTS:
        parent = HERE.parent / name
        parent_manifests[name] = json.loads((parent / "manifest.json").read_text())
        with tarfile.open(parent / "payload.tar.gz", "r:gz") as stream:
            for member in stream.getmembers():
                assert member.isfile() and member.name in parent_manifests[name]["payload_members"]
                body = stream.extractfile(member).read()
                info = metadata(body)
                assert parent_manifests[name]["payload_members"][member.name] == info
                inherited.setdefault(info["sha256"], (name, member.name, info))
    files = {"evidence/build-receipt.json": build_body, "evidence/normal-receipt.json": runtime}
    for name, expected in build["source_files"].items():
        body = (BUILD / "source-snapshot" / name).read_bytes()
        assert sha(body) == expected
        files["source/" + name] = body
    extras = {
        "evidence/build-cargo.log": BUILD / "cargo-0.log",
        "evidence/freeze-receipt.json": RUN / "freeze-001/receipt.json",
        "evidence/cargo-core-artifact.json": RUN / "freeze-001/cargo-core-artifact.json",
        "evidence/test-selection.json": RUN / "test-selection.json",
        "evidence/runtime-controller.py": RUN / "run.py",
        "evidence/lifecycle.py": ROOT / "target/affine-power-post-memo-current-cli/lifecycle.py",
        "evidence/listing.log": RUN / "normal-001/listing.log",
    }
    extras.update({"evidence/test-" + str(index) + ".log": RUN / "normal-001" / ("test-" + str(index) + ".log") for index in range(22)})
    files.update({name: path.read_bytes() for name, path in extras.items()})
    own = {}
    preserved = {}
    borrowed = {}
    for alias, body in sorted(files.items()):
        info = metadata(body)
        found = inherited.get(info["sha256"]) if alias.startswith("source/") else None
        if found is not None:
            owner, member, parent_info = found
            assert parent_info == info
            borrowed.setdefault(owner, {})[member] = info
        else:
            owner, member = "self", "objects/" + info["sha256"]
            own[member] = body
        preserved[alias] = {"owner": owner, "member": member, **info}
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", filename="", mtime=0, compresslevel=9) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            for name, body in sorted(own.items()):
                info = tarfile.TarInfo(name)
                info.size = len(body)
                info.mode = 0o644
                info.mtime = 0
                archive.addfile(info, io.BytesIO(body))
    (HERE / "payload.tar.gz").write_bytes(buffer.getvalue())
    parent_files = {}
    for name in borrowed:
        for filename in ("manifest.json", "payload.tar.gz"):
            parent_files[name + "/" + filename] = metadata((HERE.parent / name / filename).read_bytes())
    manifest = {
        "schema_version": 1,
        "scope": "Saved current coherent128-source actual Cargo artifact context and exact22 normal software/symbolic tests. Direct source borrowing only; no parent checker/test-count replay or entire dependency closure claim.",
        "parent_files": parent_files,
        "borrowed_members": borrowed,
        "payload_members": {name: metadata(body) for name, body in sorted(own.items())},
        "preserved_files": preserved,
        "selected_source_count": len(build["source_files"]),
        "inherited_source_count": sum(spec["owner"] != "self" for name, spec in preserved.items() if name.startswith("source/")),
        "own_source_count": sum(spec["owner"] == "self" for name, spec in preserved.items() if name.startswith("source/")),
        "omitted_native_product": {"sha256": json.loads(runtime)["actual_product_sha256"], "bytes": json.loads((RUN / "freeze-001/receipt.json").read_text())["owned_bytes"], "fresh_replay_verification": False},
    }
    spec = importlib.util.spec_from_file_location("saved_current_core_check", HERE / "check.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    qualification = checker.replay(files)
    save(HERE / "qualification.json", qualification)
    manifest["capsule_files"] = {name: metadata((HERE / name).read_bytes()) for name in ("README.md", "check.py", "package.py", "payload.tar.gz", "qualification.json")}
    save(HERE / "manifest.json", manifest)
    print(json.dumps({"status": "packaged_saved_exact22", "manifest_sha256": sha((HERE / "manifest.json").read_bytes()), "payload_bytes": (HERE / "payload.tar.gz").stat().st_size, "inherited_source_count": manifest["inherited_source_count"], "own_source_count": manifest["own_source_count"]}))


if __name__ == "__main__":
    main()

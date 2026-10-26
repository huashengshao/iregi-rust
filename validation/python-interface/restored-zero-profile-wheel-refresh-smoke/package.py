"""Package a finished wheel refresh using direct predecessor source locators.

No compiler, native extension, integral, or parent checker is invoked.
"""
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import importlib.util
import io
import json
import tarfile

ROOT = Path.cwd().resolve()
HERE = Path(__file__).resolve().parent
RUN_REL = "target/python-restored-zero-profile-wheel-refresh"
RUN = ROOT / RUN_REL
PRIOR_REL = "validation/python-interface/final-rank6-wheel-refresh-smoke"
STAGES = ("build", "install", "import", "ordinary_eight", "checked_dual_one", "n6_one")


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {"sha256": sha(body), "bytes": len(body)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def pack(output, core_receipt):
    require(ROOT == Path("/shared/external/iregi/iregi-rust"), "project working directory")
    output = output.resolve()
    require(output.is_relative_to(ROOT) and not output.exists(), "fresh owned output directory under project")
    require(str(output.relative_to(ROOT)) == "validation/python-interface/restored-zero-profile-wheel-refresh-smoke", "approved new capsule destination")
    require(not core_receipt.is_absolute() and ".." not in core_receipt.parts and str(core_receipt).startswith("target/") and str(core_receipt).endswith("/receipt.json"), "owned relative fresh core receipt")
    context_body = (RUN / "context.json").read_bytes()
    context = json.loads(context_body)
    require(len(context["inputs"]) == 205 and len(context["coherent_source_files"]) == 128 and context["coherent_build_selected_source_count"] == 210, "expected selected205/core128-of-actual210 scope")
    require(str(core_receipt) in context["inputs"] and context["inputs"][str(core_receipt)] == context["coherent_build_receipt_sha256"], "actual fresh coherent receipt is in the frozen source context")
    evidence = {"context.json": context_body}
    for stage in STAGES:
        directory = RUN / (stage + "-001")
        receipt_body = (directory / "receipt.json").read_bytes()
        receipt = json.loads(receipt_body)
        require(receipt["status"] == "passed", "all stages must finish successfully before packaging: " + stage)
        evidence[stage + "-001/receipt.json"] = receipt_body
        for name, digest in receipt["saved_files"].items():
            require("/" not in name and name not in (".", ".."), "direct saved stage file")
            body = (directory / name).read_bytes()
            require(sha(body) == digest, "actual saved stage file: " + name)
            evidence[stage + "-001/" + name] = body
    bodies = {}
    for name, digest in context["inputs"].items():
        body = (RUN / "build-001/source-snapshot" / name).read_bytes()
        require(sha(body) == digest, "actual frozen selected source snapshot: " + name)
        bodies[name] = body
    prior_manifest_path = ROOT / PRIOR_REL / "manifest.json"
    prior_manifest_body = prior_manifest_path.read_bytes()
    prior = json.loads(prior_manifest_body)
    archives = {}
    borrowed = {}

    def read_direct(entry):
        if entry["archive"] == "local":
            archive_name = PRIOR_REL + "/payload.tar.gz"
            metadata = {**prior["capsule_files"]["payload.tar.gz"], "manifest_path": PRIOR_REL + "/manifest.json", "manifest": desc(prior_manifest_body), "members": {}}
        else:
            archive_name = entry["archive"]
            metadata = copy.deepcopy(prior["borrowed_archives"][archive_name])
            metadata["members"] = {}
        if archive_name not in archives:
            archive_body = (ROOT / archive_name).read_bytes()
            require(desc(archive_body) == {key: metadata[key] for key in ("sha256", "bytes")}, "direct borrowed archive identity")
            manifest_body = (ROOT / metadata["manifest_path"]).read_bytes()
            require(desc(manifest_body) == metadata["manifest"], "direct borrowed manifest identity")
            parent = json.loads(manifest_body)
            basename = Path(archive_name).name
            declared = parent["sources"] if basename == "sources.tar.gz" else parent["capsule_files"][basename]
            require({key: declared[key] for key in ("sha256", "bytes")} == {key: metadata[key] for key in ("sha256", "bytes")}, "parent declares direct borrowed archive")
            members = {}
            seen = set()
            with tarfile.open(fileobj=io.BytesIO(archive_body), mode="r:gz") as archive:
                for member in archive:
                    require(member.isfile() and not member.name.startswith("/") and ".." not in Path(member.name).parts and member.name not in seen, "safe direct source archive")
                    seen.add(member.name)
                    members[member.name] = archive.extractfile(member).read()
            archives[archive_name] = members
        body = archives[archive_name][entry["member"]]
        expected = {key: entry[key] for key in ("sha256", "bytes")}
        require(desc(body) == expected, "actual direct source member identity")
        borrowed.setdefault(archive_name, metadata)["members"][entry["member"]] = expected
        return body, {**expected, "archive": archive_name, "member": entry["member"]}

    prior_context_body, prior_context_entry = read_direct(prior["evidence"]["context.json"])
    require(sha(prior_context_body) == prior["source_context_sha256"], "sealed predecessor context")
    previous_context = json.loads(prior_context_body)
    required_changes = {"crates/iregi-rust/src/execution.rs", "crates/iregi-rust/src/execution/quadrature_context_tests.rs"}
    old_inputs = previous_context["inputs"]
    changed_common = {name for name in old_inputs.keys() & context["inputs"].keys() if old_inputs[name] != context["inputs"][name]}
    require(changed_common == required_changes, "only the two authorized common source bodies changed")
    require(old_inputs.keys() - context["inputs"].keys() == {"target/python-final-rank6-wheel-refresh/run.py", "target/e6-dual-optional-zero-profile-qualification/build-001/receipt.json"}, "only predecessor controller and coherent core receipt removed; historical names receipt retained")
    require(context["inputs"].keys() - old_inputs.keys() == {str(core_receipt), RUN_REL + "/run.py"}, "only new controller and core receipt added")
    objects = {}

    def local_reference(body):
        member = "objects/" + sha(body)
        objects[member] = body
        return {**desc(body), "archive": "local", "member": member}

    selected = {}
    for name, body in bodies.items():
        if name in prior["selected_sources"] and sha(body) == prior["selected_sources"][name]["sha256"]:
            actual, entry = read_direct(prior["selected_sources"][name])
            require(actual == body, "unchanged predecessor source body exact bytes")
            selected[name] = entry
        else:
            selected[name] = local_reference(body)
    saved = {name: local_reference(body) for name, body in evidence.items()}
    saved["predecessor-context.json"] = prior_context_entry
    spec = importlib.util.spec_from_file_location("refreshed_wheel_saved_checker", HERE / "check.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    for name, body in [*bodies.items(), *evidence.items()]:
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
        "status": "passed_restored_zero_profile_wheel_refresh_exact10_saved_smoke",
        "capsule_directory": str(output.relative_to(ROOT)),
        "scope": "Restored-source frontend refresh following exactly two authorized core body changes removing the unsafe full-Dual quadrature zero-profile bypass and correcting its regression. Same exact ten installed-wheel API cases. Earlier final wheel and wheel004 typing/notebook qualification remain immutable. No new independent integral, rank-six completeness, performance, or full compiler/system closure claim.",
        "producer": {"run_directory": RUN_REL, "environment_directory": ".local/tirust-restored-zero-profile-wheel-refresh-env", "coherent_build_receipt_path": str(core_receipt)},
        "predecessor": {"manifest_path": PRIOR_REL + "/manifest.json", "manifest": desc(prior_manifest_body)},
        "source_refresh_bridge": {"changed_common_paths": sorted(required_changes), "predecessor_selected_source_count": 205, "current_selected_source_count": 205, "coherent_source_count": 128, "actual_core_build_selected_source_count": 210},
        "source_context_sha256": sha(context_body),
        "selected_source_count": 205,
        "coherent_source_count": 128,
        "actual_core_build_selected_source_count": 210,
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
    print(json.dumps({"status": "packaged_saved_wheel_refresh", "output": str(output.relative_to(ROOT)), "selected_source_files": len(selected), "borrowed_source_files": sum(entry["archive"] != "local" for entry in selected.values()), "own_source_files": sum(entry["archive"] == "local" for entry in selected.values()), "evidence_files": len(saved), "payload_bytes": len(payload), "manifest_sha256": sha((output / "manifest.json").read_bytes())}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--core-receipt", required=True, type=Path)
    arguments = parser.parse_args()
    pack(arguments.output, arguments.core_receipt)

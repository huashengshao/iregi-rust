#!/usr/bin/env python3
"""Portable capsule/source reconstruction and independent saved-number replay.

No producer, Rust compiler, integral evaluator, master or benchmark is executed.
The preserved independent stdlib checker is executed as reviewed Python source;
only its saved-data functions are called, never the producer-specific main.
"""
from pathlib import Path
from decimal import localcontext
import argparse
import hashlib
import json
import re
import tarfile
import tempfile
import types


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def decode(data):
    return json.loads(data)


def exact(a, b):
    return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False)


def replay(root, payload):
    audit = types.ModuleType("preserved_independent_six_regression_audit")
    audit.__file__ = str(root / "validation/native-f64-sixpoint-regression/preserved-independent-numeric.py")
    source = payload["reviews/audit_six_regression_independent.py"]
    assert digest(source) == "c0f6a3338807684192707e30bb53cf62bc0d774dbfaed69ced6223c70449b65f"
    exec(compile(source, audit.__file__, "exec"), audit.__dict__)
    expected = decode(payload["reviews/six-regression-independent-numeric-audit.json"])
    assert expected["status"] == "independent-retained-n6-saved-numerical-audit-passed"
    # Temporary files stay inside the project and contain only saved text/data.
    temporary_parent = root / "target"
    temporary_parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="six-regression-portable-", dir=temporary_parent) as directory:
        destination = Path(directory)
        for relative, data in payload.items():
            if relative.startswith(("default/", "selective/")):
                path = destination / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        audit.R = root
        audit.H = destination
        audit.FIXTURE = root / "validation/public-highpoint/fixture-conditioned_masses.json"
        audit.REFERENCE = root / "validation/public-highpoint/reference-conditioned_masses.json"
        # These are the unchanged two main-prefix checks and unchanged pure
        # functions. Rebinding H replaces legacy operational paths only.
        audit.check(True, "all producer stages are terminal in the sealed capsule")
        fixture, reference = audit.read(audit.FIXTURE), audit.read(audit.REFERENCE)
        audit.check([sample["id"] for sample in fixture["samples"]] == ["base", "scaled_by_two", "first_mass_squared_plus_one"])
        results = {}
        with localcontext() as context:
            context.prec = 220
            originals = audit.validate_reference(fixture, reference)
            for chain in ("default", "selective"):
                audit.terminal_records(chain)
                results[chain] = dict(ordinary=audit.ordinary(chain), rank3=audit.rank3(chain, fixture, originals),
                                      lifecycle=audit.lifecycle(chain, fixture, originals))
        assert exact(results, expected["chains"]), "independent saved-number replay differs"
        assert audit.CHECKS == expected["checks"] == 178352, "independent saved check inventory differs"
    return audit.CHECKS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--origins", action="store_true", help="also compare retained original-machine target files")
    args = parser.parse_args()
    capsule = Path(__file__).resolve().parent
    root = capsule.parents[1]
    assert Path.cwd().resolve() == root, "run from the project root"
    manifest = decode((capsule / "manifest.json").read_bytes())
    parent = decode((capsule / "parent.json").read_bytes())
    q = decode((capsule / "qualification.json").read_bytes())
    actual = {str(path.relative_to(capsule)) for path in capsule.rglob("*") if path.is_file()}
    assert actual == set(manifest["metadata_files"]) | {"manifest.json", "evidence.tar.gz"}, "capsule membership differs"
    for relative, item in manifest["metadata_files"].items():
        path = capsule / relative
        assert path.stat().st_size == item["bytes"] and sha(path) == item["sha256"], relative
    archive = manifest["archive"]
    assert sha(capsule / archive["path"]) == archive["sha256"]
    assert (capsule / archive["path"]).stat().st_size == archive["bytes"]
    payload = {}
    with tarfile.open(capsule / archive["path"], "r:gz") as stream:
        members = stream.getmembers()
        assert len(members) == len(archive["members"]) and {item.name for item in members} == set(archive["members"])
        for member in members:
            path = Path(member.name)
            assert member.isfile() and not path.is_absolute() and ".." not in path.parts
            data = stream.extractfile(member).read()
            item = archive["members"][member.name]
            assert member.size == item["bytes"] == len(data) and digest(data) == item["sha256"], member.name
            assert not data.startswith((b"\x7fELF", b"!<arch>\n")), member.name
            assert not re.search(rb"S-130-[0-9]{4}\.[0-9]{2}\.[0-9]{2}-[A-Z0-9]{40,}", data), member.name
            if args.origins:
                assert sha(root / item["origin"]) == item["sha256"], item["origin"]
            payload[member.name] = data
    parent_path = root / parent["parent_archive"]["path"]
    assert sha(parent_path) == parent["parent_archive"]["sha256"]
    assert sha(root / parent["parent_manifest"]["path"]) == parent["parent_manifest"]["sha256"]
    reconstructed = {}
    with tarfile.open(parent_path, "r:gz") as stream:
        for category, mapping in parent["inherited_sources"].items():
            reconstructed[category] = {}
            for relative, item in mapping.items():
                data = stream.extractfile(item["member"]).read()
                assert len(data) == item["bytes"] and digest(data) == item["sha256"], (category, relative)
                reconstructed[category][relative] = digest(data)
        private_source = decode(stream.extractfile("source-inventory.json").read())
        compiled = decode(stream.extractfile("qualification/codegen-preparation.json").read())
        assert reconstructed["base"] == private_source["base"] and len(reconstructed["base"]) == 80
        assert reconstructed["proposed"] == private_source["proposed"] and len(reconstructed["proposed"]) == 85
        assert reconstructed["compiled"] == compiled["compiled_source_mapping"] and len(reconstructed["compiled"]) == 85
    for relative, item in parent["reused_committed_files"].items():
        assert sha(root / relative) == item["sha256"], relative
    omission = decode((capsule / "omitted-artifacts.json").read_bytes())
    omitted = {item["path"]: item for item in omission["compiled_products"]}
    build = decode(payload["build-001/run.json"])
    assert build["status"] == "passed" and len(build["steps"]) == 7 and len(build["inputs"]) == 655
    assert build["bound_seconds"] == 180 and build["reserve_seconds"] == 25 and build["elapsed_seconds"] < 180
    assert build["inputs_unchanged"] is True and not build["cleanup_errors"]
    plan = decode(payload["command-plan.json"])
    assert [step["command"] for step in build["steps"]] == [step["command"] for step in plan["steps"]]
    assert len(build["outputs"]) == 7
    for label, item in build["outputs"].items():
        original = item["path"].split("/iregi-rust/", 1)[1]
        assert omitted[original]["sha256"] == item["sha256"]
        assert digest(payload["build-001/" + label + ".log"]) == build["log_sha256"][label]
    groups = [step["owned_process_group"] for step in build["steps"]]
    assert all(step["status"] == "exited" and step["returncode"] == 0 and step["owned_group_gone"] is True for step in build["steps"])
    for chain in ("default", "selective"):
        for operation in ("ordinary-baseline", "ordinary-candidate", "128", "256", "lifecycle"):
            prefix = chain + "/" + operation + "-001/"
            run = decode(payload[prefix + "run.json"])
            assert run["status"] == "passed" and run["inputs_unchanged"] is True and not run["cleanup_errors"]
            assert run["bound_seconds"] == (120 if operation.startswith("ordinary-") else 180)
            assert run["reserve_seconds"] == 20 and run["elapsed_seconds"] < run["bound_seconds"]
            step, = run["steps"]
            assert step["status"] == "exited" and step["returncode"] == 0 and step["owned_group_gone"] is True
            groups.append(step["owned_process_group"])
            for name in ("result.json", "step-0.log"):
                assert digest(payload[prefix + name]) == run["outputs"][name]
            original = "target/native-f64-sixpoint-port/six-regression/" + prefix + "frozen-executable"
            assert omitted[original]["sha256"] == run["outputs"]["frozen-executable"]
    assert len(groups) == len(set(groups)) == len(omitted) == 17
    release = decode(payload["numerical-release.json"])
    assert release["status"] == "numerical-lease-released" and release["all_owned_groups_absent"] is True
    assert {item["group"] for item in release["owned_group_checks"]} == set(groups)
    assert all(item["absent"] is True for item in release["owned_group_checks"])
    assert q["status"] == "private-combined-native-policy-retained-n6-regression-qualified"
    assert all(q["not_qualified_by_this_capsule"].values()) and q["production_mutations"] is False
    assert q["benchmark_execution"] is False and q["current_cargo_execution"] is False
    numeric = decode(payload["reviews/six-regression-independent-numeric-audit.json"])
    provenance = decode(payload["reviews/six-regression-independent-provenance-audit.json"])
    assert numeric["status"] == q["independent_numeric_audit_status"] and numeric["checks"] == 178352
    assert provenance["status"] == q["independent_provenance_audit_status"]
    assert digest(payload["reviews/six-regression-independent-numeric-audit.json"]) == q["independent_numeric_audit_sha256"]
    assert digest(payload["reviews/six-regression-independent-provenance-audit.json"]) == q["independent_provenance_audit_sha256"]
    assert not numeric["blocking_findings"] and not provenance["findings"]
    assert manifest["content_audit"]["ELF_or_ar_payloads"] == manifest["content_audit"]["provided_license_occurrences"] == 0
    checks = replay(root, payload)
    print(json.dumps(dict(status="passed", archive_payloads=len(payload), inherited_source_files=250,
                          independent_saved_checks=checks, compiled_products_omitted=len(omitted),
                          origins_checked=args.origins, no_integral_or_compiler_or_benchmark_executed=True)))


if __name__ == "__main__":
    main()

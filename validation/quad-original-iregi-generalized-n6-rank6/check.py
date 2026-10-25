#!/usr/bin/env python3
"""Restore pinned saved bytes and invoke the unchanged independent N6 audit."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = "validation/quad-original-iregi-generalized-rank7"
PRIVATE = "target/n6-rank6-generalized-quad"
PROTOCOL = "277f4652434070e9b2d20cfa6be8f044b564e6ea88df35e32b314d66565c1b26"
PARENT_MANIFEST = "ccda92bdd0be40484b2d8762d479658ada0beb98eb610df7c96b44f7f521a0b0"
PARENT_CHECKER = "8bd9efc8ee6f95f9a0387c3510f105b9bceda416aade16c2e3bee2ef445cee7e"
AUDIT = "6f7fcc3ac1fe9702c2a581c9d764f1c36b452475673da0ea74e9544390933bcc"
INDEPENDENT = "71a43fd0143294573f6c67339aa04273328291101a3753c5e30fdd4846f107c3"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return dict(sha256=sha(body), bytes=len(body))


def load(body):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(body, object_pairs_hook=pairs)


def safe(name):
    path = PurePosixPath(name)
    require(name and not path.is_absolute() and ".." not in path.parts and str(path) == name, "unsafe alias")


def imported(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def restore_files(manifest):
    expected_files = set(manifest["capsule_files"]) | {"manifest.json"}
    require({str(path.relative_to(HERE)) for path in HERE.rglob("*") if path.is_file() and "__pycache__" not in path.parts} == expected_files, "exact capsule inventory")
    for name, expected in manifest["capsule_files"].items():
        safe(name)
        require(desc((HERE/name).read_bytes()) == expected, "capsule byte identity: " + name)
    parent_bytes = {}
    for name, expected in manifest["parent_files"].items():
        safe(name)
        body = (ROOT/name).read_bytes()
        require(desc(body) == expected, "declared parent byte identity: " + name)
        parent_bytes[name] = body
    require(sha(parent_bytes[PARENT+"/manifest.json"]) == PARENT_MANIFEST and sha(parent_bytes[PARENT+"/check.py"]) == PARENT_CHECKER, "fixed generalized parent")
    parent = imported("n6_generalized_saved_parent", ROOT/PARENT/"check.py")
    files = parent.restore_files(load(parent_bytes[PARENT+"/manifest.json"]))
    for name, body in parent_bytes.items():
        require(name not in files or files[name] == body, "parent alias collision")
        files[name] = body
    for name, expected in manifest["required_parent_aliases"].items():
        require(name in files and desc(files[name]) == expected, "required inherited saved context")
    members = {}
    with tarfile.open(fileobj=io.BytesIO((HERE/"payload.tar.gz").read_bytes()), mode="r:gz") as archive:
        for item in archive:
            safe(item.name)
            require(item.isfile() and item.name not in members, "only unique regular payload members")
            body = archive.extractfile(item).read()
            require(desc(body) == manifest["payload_members"].get(item.name), "payload member identity")
            members[item.name] = body
    require(set(members) == set(manifest["payload_members"]), "exact payload member inventory")
    origins = load((HERE/"payload-origins.json").read_bytes())
    tables = [manifest["preserved_files"], manifest["inherited_aliases"], manifest["capsule_aliases"]]
    require(sum(len(table) for table in tables) == len(set().union(*map(set, tables))) and set(origins) == set().union(*map(set, tables)), "closed new alias/origin inventory")
    for table in tables:
        for name, row in table.items():
            safe(name)
            body = members[row["member"]] if "member" in row else files[row["inherited_source"]] if "inherited_source" in row else (HERE/row["capsule_file"]).read_bytes()
            expected = {key: row[key] for key in ["sha256", "bytes"]}
            require(desc(body) == expected == {key: origins[name][key] for key in expected}, "restored new alias identity")
            require(name not in files or files[name] == body, "new saved alias collision")
            files[name] = body
    for name in expected_files:
        alias = manifest["capsule_directory"]+"/"+name
        files[alias] = (HERE/name).read_bytes()
    return files


def replay(files, manifest):
    require(sha(files[PRIVATE+"/protocol.json"]) == PROTOCOL and sha(files[PRIVATE+"/independent-saved-review.json"]) == AUDIT, "fixed completed N6 evidence")
    require(files[PRIVATE+"/independent_saved_check.py"] == (HERE/"independent_saved_check.py").read_bytes() and sha((HERE/"independent_saved_check.py").read_bytes()) == INDEPENDENT, "byte-identical independent checker")
    independent = imported("n6_generalized_independent_saved_audit", HERE/"independent_saved_check.py")
    actual = independent.audit(lambda alias: files[alias])
    saved = load(files[PRIVATE+"/independent-saved-review.json"])
    require(saved.pop("checker_sha256") == INDEPENDENT, "saved independent checker attestation")
    require(actual == saved, "entire independent receipt replay; only checker_sha256 excluded")
    p = load(files[PRIVATE+"/protocol.json"])
    available = historical = 0
    prefix = "/shared/external/iregi/iregi-rust/"
    for absolute, expected in p["bindings"].items():
        alias = absolute.removeprefix(prefix) if absolute.startswith(prefix) else None
        if alias in files:
            require(sha(files[alias]) == expected, "available narrow input guard replay")
            available += 1
        else:
            require(manifest["historical_omitted_guards"].get(absolute) == expected, "explicit historical omitted native/tool guard")
            historical += 1
    old = PRIVATE+"/earlier-drafts/v1/"
    inventory = load(files[old+"inventory.json"])
    require(len(inventory) == 15 and sha(files[old+"protocol.json"]) == "1b92ea7ca4b8b126c39ba6c30de5680af4d586b2cf6a59cffedd4cc1cf6d80a7", "unexecuted v1 source packet")
    for name, expected in inventory.items():
        require(sha(files[old+name]) == expected, "preserved unexecuted v1 bytes")
    require(load(files[PRIVATE+"/source-review-001.json"])["status"] == "changes_requested_independent_source_runner_comparator_review", "initial timing finding retained")
    admission = load(files[PRIVATE+"/anchor-admission.json"])
    require((HERE/"qualification.json").read_bytes() == files[PRIVATE+"/anchor-admission.json"] and admission["independent_saved_review_sha256"] == AUDIT and admission["independent_checker_sha256"] == INDEPENDENT, "scoped admission exact evidence chain")
    require(actual["complete_arrays"] == 7 and actual["complete_complex_slots"] == 5880 and actual["exact_records"] == 5166 and actual["finite_generalized_coefficients_independently_certified"] is False and actual["Rust_Dual_physical_or_performance_qualified"] is False, "restricted seven-array scope")
    return dict(complete_arrays=7, complete_complex_slots=5880, exact_records=5166,
                gate_counts=actual["gate_counts"], exact_unit_prefix_matches=actual["exact_unit_prefix_matches"],
                negative_controls=actual["negative_controls"], maxima=actual["maxima"],
                d6_degree6_UV_slots_retained=actual["d6_degree6_UV_slots_retained"],
                available_source_guards=available, historical_native_tool_guards=historical,
                finite_generalized_coefficients_independently_certified=False,
                new_native_compiler_integral_process_or_Git_work=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct", type=Path)
    args = parser.parse_args()
    manifest = load((HERE/"manifest.json").read_bytes())
    files = restore_files(manifest)
    summary = replay(files, manifest)
    if args.reconstruct is not None:
        require(not args.reconstruct.exists(), "preserve existing reconstruction")
        args.reconstruct.mkdir(parents=True)
        for name, body in files.items():
            safe(name)
            path = args.reconstruct/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
    print(json.dumps(dict(status="passed_portable_N6_rank6_generalized_saved_replay",
                          manifest_sha256=sha((HERE/"manifest.json").read_bytes()), restored_files=len(files),
                          summary=summary), indent=2))


if __name__ == "__main__":
    main()

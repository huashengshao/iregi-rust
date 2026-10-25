#!/usr/bin/env python3
"""Restore pinned saved bytes and invoke the unchanged independent low-N dot/triple audit."""
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
PARENT = "validation/quad-original-iregi-generalized-n6-rank6"
PRIVATE = "target/quad-low-n-rank6-dot-triple"
PROTOCOL = "6c36ac2a890cb526ab9c89e2b6b11c3fa82fc4783014616695a2e648bf3506af"
PARENT_MANIFEST = "90e4ede40dbf46e537064dea0e85309b0079bfd12d245f7dc9ba658aa16d2f0e"
PARENT_CHECKER = "f13b4453ac18a2d8ab98f0c959290634d195194cb4e1dfef6bdf78a063e2a3e3"
AUDIT = "5ec162582d17f913e4a699971494d5e37789d08473d192be42eb9475526d13f1"
INDEPENDENT = "e5ff106e5ce28ca392ebb0a79fad34a1e6ac3ecf14559f54fd3cfea07ea5b1e5"


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
    parent = imported("low_n_dot_triple_saved_parent", ROOT/PARENT/"check.py")
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
    require(sha(files[PRIVATE+"/protocol.json"]) == PROTOCOL and sha(files[PRIVATE+"/independent/review.json"]) == AUDIT, "fixed completed low-N evidence")
    require(files[PRIVATE+"/independent/audit_saved.py"] == (HERE/"independent_saved_check.py").read_bytes() and sha((HERE/"independent_saved_check.py").read_bytes()) == INDEPENDENT, "byte-identical independent checker")
    independent = imported("low_n_dot_triple_independent_saved_audit", HERE/"independent_saved_check.py")
    actual = independent.audit(lambda alias: files[alias])
    saved = load(files[PRIVATE+"/independent/review.json"])
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
    admission = load(files[PRIVATE+"/anchor-admission.json"])
    index = load(files[PRIVATE+"/anchor-index.json"])
    require((HERE/"qualification.json").read_bytes() == files[PRIVATE+"/anchor-admission.json"]
            and admission["independent_saved_review_sha256"] == AUDIT
            and admission["independent_checker_sha256"] == INDEPENDENT
            and admission["anchor_index_sha256"] == sha(files[PRIVATE+"/anchor-index.json"]), "scoped admission exact evidence chain")
    require(admission["status"] == "admitted_scoped_original_quad_low_N_rank6_dot_triple_references"
            and index["status"] == "independently_audited_scoped_low_N_rank6_dot_triple_reference_index"
            and admission["records"] == index["records"] and len(index["records"]) == 6, "six-case index/admission mapping")
    prefix = "/shared/external/iregi/iregi-rust/"
    for i, (record, case) in enumerate(zip(index["records"], p["cases"])):
        require(record["index"] == i and record["id"] == case["id"] and record["n"] == case["n"]
                and record["powers"] == case["powers"] and record["h"] == record["idim"] == 0
                and record["rank"] == 6 and record["request"] == case["request"]
                and record["request_sha256"] == case["request_sha256"]
                and record["raw"] == prefix+PRIVATE+f"/capture-001/request-{i}.stdout"
                and record["raw_sha256"] == sha(files[record["raw"].removeprefix(prefix)])
                and record["complete_complex_slots"] == 840
                and record["ordinary_unit_anchor_correspondence_only"] is True
                and record["finite_coefficients_independently_certified"] is False, "exact scoped request/raw admission")
    require(actual["complete_new_complex_slots"] == 5040 and actual["identity_records_recomputed"] == 5321
            and actual["identity_failed"] == 0 and len(actual["cases"]) == 6
            and actual["finite_coefficients_independently_certified"] is False
            and actual["Rust_Dual_physical_or_performance_qualified"] is False
            and admission["finite_individual_generalized_coefficients_independently_certified"] is False,
            "restricted six-array scope")
    return dict(complete_arrays=6, complete_complex_slots=5040, exact_records=5321,
                gate_counts=actual["identity_gate_counts"],
                ordinary_unit_anchor_slots_parsed=actual["ordinary_unit_anchor_complex_slots_parsed"],
                negative_controls=actual["negative_controls_rejected"],
                independent_checks=actual["checks"], independent_checked_aliases=len(actual["checked_aliases"]),
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
    print(json.dumps(dict(status="passed_portable_low_N_rank6_dot_triple_saved_replay",
                          manifest_sha256=sha((HERE/"manifest.json").read_bytes()), restored_files=len(files),
                          summary=summary), indent=2))


if __name__ == "__main__":
    main()

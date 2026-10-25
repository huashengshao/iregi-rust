#!/usr/bin/env python3
"""Unexecuted preparation: package only final frozen saved source/data bytes.

No producer/checker import, subprocess, native hashing or process probe. The
terminal inventory is supplied by the numerical owner after independent review.
The output must not exist; final portable replay is a separate explicit step.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile

ROOT = Path.cwd().resolve()
PREP = Path(__file__).resolve().parent
PRIVATE = "target/quad-generalized-rank7-anchors"
PARENT = "validation/quad-original-iregi-small-n-rank7"
HISTORICAL = "/shared/external/iregi/iregi-rust/"
PROTOCOL_SHA = "f9da4d00dd8aa7d85377082da89e6c38dcc771f2115f15d1203699940efe8899"
PARENT_SHA = "9b614c6567c28d23039053de390a7da5c665f4a57a978d54cd3148519fb3cb62"
COMPILED_SUFFIXES = {".o", ".mod", ".smod", ".a", ".so", ".dll", ".dylib", ".pyc"}
LICENSE = re.compile(rb"S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def safe(name):
    path = Path(name)
    require(name and not path.is_absolute() and ".." not in path.parts and str(path) == name,
            "unsafe repository-relative alias")


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {"sha256": sha(body), "bytes": len(body)}


def load(body):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError("nonfinite JSON constant: " + value)

    return json.loads(body, object_pairs_hook=pairs, parse_constant=nonfinite)


def scan(name, body):
    safe(name)
    require(Path(name).suffix not in COMPILED_SUFFIXES and "__pycache__" not in Path(name).parts,
            "compiled/cache input forbidden")
    require(not body.startswith((b"\x7fELF", b"!<arch>", b"MZ")), "native product forbidden")
    require(not LICENSE.search(body), "literal Symbolica license forbidden")


def read(name):
    safe(name)
    path = ROOT/name
    require(path.is_file() and not path.is_symlink(), "missing/symlink input " + name)
    body = path.read_bytes()
    scan(name, body)
    return body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terminal-inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path,
                        default=ROOT/"validation/quad-original-iregi-generalized-rank7")
    args = parser.parse_args()
    require(ROOT.name == "iregi-rust" and (ROOT/"AGENTS.md").is_file(), "run from project root")
    require(not args.output.exists(), "preserve existing capsule")
    protocol = read(PRIVATE+"/protocol.json")
    require(sha(protocol) == PROTOCOL_SHA, "final reviewed protocol changed")
    p = load(protocol)
    inventory_path = args.terminal_inventory.resolve()
    inventory_alias = str(inventory_path.relative_to(ROOT))
    inventory_body = read(inventory_alias)
    inventory = load(inventory_body)
    require(inventory["schema_version"] == 1 and inventory["status"] == "terminal_inputs_frozen"
            and inventory["protocol_sha256"] == PROTOCOL_SHA, "accepted terminal freeze required")
    roles = inventory["roles"]
    require(set(roles) >= {"source_review", "root_grant", "independent_saved_review", "independent_saved_review_source", "numerical_release"},
            "all source/grant/audit roles required")
    require(roles["source_review"] == PRIVATE+"/source-review.json"
            and roles["root_grant"] == PRIVATE+"/root-grant.json", "producer exact reviewed role paths")
    for name in roles.values():
        require(name in inventory["files"], "every role must have a frozen descriptor")

    # Inspect immutable parent metadata only. Do not import its executable checker.
    parent_body = read(PARENT+"/manifest.json")
    require(sha(parent_body) == PARENT_SHA, "fixed small-N parent")
    pm = load(parent_body)
    parent_files = dict(pm["parent_files"])
    for name in list(pm["capsule_files"])+["manifest.json"]:
        key = PARENT+"/"+name
        parent_files[key] = desc(read(key))
    require(len(parent_files) == 37, "exact 37-file inherited closure")
    for name, expected in parent_files.items():
        # Parent compressed payloads are already hash-pinned, and not re-packed.
        safe(name)
        require(desc((ROOT/name).read_bytes()) == expected, "parent closure drift")
    registry = {}
    for package in [PARENT, "validation/quad-original-iregi-positive-rank-anchors",
                    "validation/quad-original-iregi-rank7-adjudication"]:
        m = load((ROOT/package/"manifest.json").read_bytes())
        for key in ["preserved_files", "inherited_aliases", "reconstructed_v1_files", "restored_original_files"]:
            for name, row in m.get(key, {}).items():
                expected = {k: row[k] for k in ["sha256", "bytes"]}
                require(name not in registry or registry[name] == expected, "parent metadata collision")
                registry[name] = expected

    bodies = {PRIVATE+"/protocol.json": protocol, inventory_alias: inventory_body}
    omitted, historical = {}, {}
    oldbinary = p["original_link_command"][-1]
    native_names = {oldbinary, p["build"]["binary"]}
    for absolute, expected_hash in p["bindings"].items():
        if not absolute.startswith(HISTORICAL):
            historical[absolute] = expected_hash
            continue
        name = absolute.removeprefix(HISTORICAL)
        if Path(name).suffix in COMPILED_SUFFIXES or absolute in native_names:
            omitted[name] = {"captured_sha256": expected_hash,
                             "reason": "omitted old native input; digest is captured historical provenance"}
            continue
        body = read(name)
        require(sha(body) == expected_hash, "source/data protocol guard drift")
        bodies[name] = body
    for name, expected in inventory["files"].items():
        require(set(expected) == {"sha256", "bytes"}, "exact terminal descriptor shape")
        body = read(name)
        require(desc(body) == expected, "frozen terminal file drift")
        require(name not in bodies or bodies[name] == body, "terminal source collision")
        bodies[name] = body
    required = [PRIVATE+"/build-001/receipt.json", PRIVATE+"/capture-001/receipt.json", PRIVATE+"/comparison.json"]
    require(all(name in bodies for name in required), "terminal receipts/comparison required")
    require(PRIVATE+"/qualification.json" in bodies, "final scoped qualification must be frozen")
    build, run, comparison = [load(bodies[name]) for name in required]
    require(build["status"] in ["passed", "failed"] and run["status"] in ["passed", "failed"],
            "running receipts cannot be frozen")
    for stage, receipt in [("build-001", build), ("capture-001", run)]:
        require(receipt["protocol_sha256"] == PROTOCOL_SHA, "terminal receipt source pin")
        for name, expected_hash in receipt["outputs"].items():
            key = PRIVATE+"/"+stage+"/"+name
            safe(key)
            if stage == "build-001" and name in p["build"]["products"]:
                omitted[key] = {"captured_sha256": expected_hash,
                                "reason": "omitted new native output; digest is captured historical provenance"}
            else:
                require(key in bodies and sha(bodies[key]) == expected_hash,
                        "every recorded noncompiled output must be frozen")
    require(len(build["steps"]) == 2 and len(run["steps"]) == 12, "closed two-command/twelve-request receipt shape")
    for stage, receipt in [("build-001", build), ("capture-001", run)]:
        recorded = set(receipt["outputs"])
        for name in bodies:
            prefix = PRIVATE+"/"+stage+"/"
            if name.startswith(prefix) and name != prefix+"receipt.json":
                require(name.removeprefix(prefix) in recorded or name in roles.values(),
                        "unrecorded output needs an explicit terminal review/release role")
    # Preserve every superseded unexecuted draft as explicit frozen source context.
    for directory, protocol_hash in [("001-unexecuted-before-terminal-shape-review",
                                     "6739076106cfa87f718bde88c1d4c90fdb1c98fb56060295d72e692a0376b3c6"),
                                    ("002-unexecuted-before-canonical-propagator-powers",
                                     "cc2238e61975e72ab4152a4ccada4b3589728650f4d83026395e1e1aaea1cc45")]:
        prefix = PRIVATE+"/earlier-drafts/"+directory+"/"
        require(prefix+"inventory.json" in bodies, "unexecuted source-draft inventory required")
        old = load(bodies[prefix+"inventory.json"])
        require(len(old) == 23 and old["protocol.json"] == protocol_hash, "fixed superseded draft")
        require({name.removeprefix(prefix) for name in bodies if name.startswith(prefix)} == set(old) | {"inventory.json"},
                "closed superseded draft source inventory")
        for name, expected_hash in old.items():
            require(sha(bodies[prefix+name]) == expected_hash, "superseded draft byte identity")

    members, preserved, inherited_requirements, aliases, origins = {}, {}, {}, {}, {}
    by_digest = {}
    for name, expected in registry.items():
        by_digest.setdefault((expected["sha256"], expected["bytes"]), name)
    for name, body in sorted(bodies.items()):
        expected = desc(body)
        if name in registry:
            require(registry[name] == expected, "exact parent byte match")
            inherited_requirements[name] = expected
            continue
        signature = (expected["sha256"], expected["bytes"])
        if signature in by_digest:
            source = by_digest[signature]
            aliases[name] = {"inherited_source": source, **expected}
        else:
            # Own archive aliases may share one member without executing restoration.
            member = next((key for key, value in members.items() if value == body), None)
            if member is None:
                member = name
                members[member] = body
            preserved[name] = {"member": member, **expected}
        origins[name] = {"origin": HISTORICAL+name, **expected}

    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            for name, body in sorted(members.items()):
                item = tarfile.TarInfo(name)
                item.size, item.mode, item.mtime, item.uid, item.gid = len(body), 0o644, 0, 0, 0
                item.uname = item.gname = ""
                archive.addfile(item, io.BytesIO(body))
    capsule = {"check.py": (PREP/"check.py").read_bytes(), "README.md": (PREP/"README.md").read_bytes(),
               "package.py": (PREP/"package.py").read_bytes(), "qualification.json": bodies[PRIVATE+"/qualification.json"],
               "payload.tar.gz": raw.getvalue(),
               "payload-origins.json": (json.dumps(origins, indent=2)+"\n").encode()}
    for name, body in capsule.items():
        scan(name, body)
    manifest = {"schema_version": 1, "status": "saved_restricted_generalized_reference_evidence",
                "protocol_sha256": PROTOCOL_SHA, "capsule_files": {n: desc(b) for n, b in capsule.items()},
                "payload_members": {n: desc(b) for n, b in members.items()}, "preserved_files": preserved,
                "inherited_requirements": inherited_requirements, "inherited_aliases": aliases,
                "parent_files": parent_files, "terminal_inventory_alias": inventory_alias, "terminal_roles": roles,
                "omitted_compiled_products": omitted, "historical_external_inputs": historical,
                "omitted_python_caches": [], "symbolica_license_literal_included": False,
                "upstream_COPYING_inherited": True, "requested_complex_slots": 15840,
                "saved_records": comparison["records_count"], "complete_arrays": comparison["all_cases_complete"],
                "eligible_reference_arrays": sum(c["eligible_reference_anchor"] for c in comparison["cases"]),
                "TIRust_or_currentCargo_qualified": False, "full_generalized_domain_qualified": False,
                "finite_coefficients_independently_certified_by_identities": False,
                "precision_convergence_qualified": False, "performance_qualified": False,
                "native_hash_or_process_attestations_are_not_portable_fresh_guards": True}
    # All validation above is source/data only. No existing destination is mutated.
    args.output.mkdir(parents=True)
    for name, body in capsule.items():
        (args.output/name).write_bytes(body)
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({"status": "packaged_frozen_source_and_saved_bytes_not_yet_portably_replayed",
                      "output": str(args.output), "manifest_sha256": sha((args.output/"manifest.json").read_bytes()),
                      "own_aliases": len(preserved)+len(aliases), "payload_members": len(members),
                      "parent_files": len(parent_files), "new_native_or_integral_work": False}, indent=2))


if __name__ == "__main__":
    main()

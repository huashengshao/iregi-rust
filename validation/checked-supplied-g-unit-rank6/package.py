#!/usr/bin/env python3
"""Package frozen checked-G saved evidence; no producer/native execution."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile

ROOT = Path.cwd().resolve()
HERE = Path(__file__).resolve().parent
OUT = ROOT/"validation/checked-supplied-g-unit-rank6"
Q = "target/checked-g-packed-qualification"
S = "target/checked-g-packed-source"
W = "validation/python-interface/facade-wheel-003"
N = "validation/quad-original-iregi-generalized-n6-rank6"
BUILD = "96e91d3f2a502e23c180150b7860375e524bdb4174191784a270fca9d40fe3c9"
QUAL = "90eccf70eecbe9751b0cf5eebc198556ff2cb9032799de01d890b3823de05273"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {"sha256": sha(body), "bytes": len(body)}


def safe(name):
    p = Path(name)
    need(name and not p.is_absolute() and ".." not in p.parts and str(p) == name, "unsafe path")


def scan(name, body):
    safe(name)
    need(Path(name).suffix not in {".o", ".mod", ".smod", ".pyc", ".so", ".a", ".dll", ".dylib"}
         and "__pycache__" not in Path(name).parts, "compiled/cache bytes forbidden")
    need(not body.startswith((b"\x7fELF", b"!<arch>", b"MZ")), "native product forbidden")
    need(not re.search(rb"S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}", body), "license literal forbidden")


def archive(path, expected):
    body = path.read_bytes()
    need(desc(body) == {k: expected[k] for k in ["sha256", "bytes"]}, "parent archive identity")
    files = {}
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as tar:
        for m in tar:
            need(m.isfile() and m.name not in files, "regular unique parent member")
            value = tar.extractfile(m).read()
            scan(m.name, value)
            need(desc(value) == expected["members"].get(m.name), "parent member identity")
            files[m.name] = value
    need(set(files) == set(expected["members"]), "closed parent archive inventory")
    return files


def main():
    need(ROOT.name == "iregi-rust" and not OUT.exists(), "project root and new output required")
    wm = json.loads((ROOT/W/"manifest.json").read_bytes())
    need(sha((ROOT/W/"manifest.json").read_bytes()) == "cb7a2b09282c89b17802a485d0aca6a42b36b23b110d7fe8aead0b2ea0f74a18", "fixed source parent")
    source = archive(ROOT/W/"sources.tar.gz", wm["sources"])
    evidence = archive(ROOT/W/"evidence.tar.gz", wm["evidence"])
    need(len(source) == 147 and sha(evidence["context.json"]) == "e873a0bec5cdb087caa812c6f2b1c668323f3670daed8438d3f538686da0c29c", "parent source context")
    nm = json.loads((ROOT/N/"manifest.json").read_bytes())
    need(sha((ROOT/N/"manifest.json").read_bytes()) == "90e4ede40dbf46e537064dea0e85309b0079bfd12d245f7dc9ba658aa16d2f0e", "fixed quad parent")
    need(desc((ROOT/N/"payload.tar.gz").read_bytes()) == nm["capsule_files"]["payload.tar.gz"], "quad parent payload")
    quad = {}
    with tarfile.open(ROOT/N/"payload.tar.gz", mode="r:gz") as tar:
        for item in tar:
            need(item.isfile() and item.name not in quad, "quad unique regular source/data member")
            body = tar.extractfile(item).read()
            scan(item.name, body)
            need(desc(body) == nm["payload_members"].get(item.name), "quad parent member")
            quad[item.name] = body
    need(set(quad) == set(nm["payload_members"]), "quad closed member inventory")
    parents = {W+"/"+n: desc((ROOT/W/n).read_bytes()) for n in ["manifest.json", "sources.tar.gz", "evidence.tar.gz"]}
    parents.update({N+"/"+n: desc((ROOT/N/n).read_bytes()) for n in ["manifest.json", "payload.tar.gz", "qualification.json"]})
    files, borrowed = {}, {}

    def add(name):
        safe(name)
        p = ROOT/name
        need(p.is_file() and not p.is_symlink(), "missing/symlink source/data " + name)
        body = p.read_bytes()
        scan(name, body)
        need(name not in files or files[name] == body, "duplicate alias collision")
        files[name] = body

    # All controller, raw stream, proof and source-application material; no binaries.
    for p in (ROOT/S).rglob("*"):
        if p.is_file():
            add(str(p.relative_to(ROOT)))
    for p in (ROOT/Q).rglob("*"):
        if p.is_file() and "source-snapshot" not in p.parts and not p.name.startswith("frozen-") and "__pycache__" not in p.parts:
            add(str(p.relative_to(ROOT)))
    build = json.loads(files[Q+"/build-001/receipt.json"])
    need(sha(files[Q+"/build-001/receipt.json"]) == BUILD and len(build["source_files"]) == 145, "fixed actual Cargo context")
    compiled = {}
    for name, expected in build["source_files"].items():
        alias = Q+"/build-001/source-snapshot/"+name
        body = (ROOT/alias).read_bytes()
        scan(alias, body)
        need(sha(body) == expected, "actual source snapshot changed")
        if name in source and source[name] == body:
            borrowed[alias] = {"parent_archive": W+"/sources.tar.gz", "member": name, **desc(body)}
            borrowed[name] = dict(borrowed[alias])
            compiled[name] = {"origin": "source_parent", "member": name, **desc(body)}
        else:
            files[alias] = body
            files[name] = body
            compiled[name] = {"origin": "own_delta", "alias": alias, **desc(body)}
    need(sum(row["origin"] == "source_parent" for row in compiled.values()) == 110, "fixed 110-source intersection")
    # Borrow already archived exact unit-reference bytes without importing its checker.
    for name in ["target/n6-rank6-generalized-quad/capture-001/request-0.stdout",
                 "target/n6-rank6-generalized-quad/anchor-admission.json",
                 "target/n6-rank6-generalized-quad/protocol.json",
                 "target/n6-rank6-generalized-quad/independent-saved-review.json"]:
        row = nm["preserved_files"][name]
        body = quad[row["member"]]
        borrowed[name] = {"parent_archive": N+"/payload.tar.gz", "member": row["member"], **desc(body)}
    add("target/n6-rank6-generalized-current-cli/inputs/n6_rank6_unit_control.json")
    old = "target/certified-tensor-qualification"
    for suffix in ["rank6-unit-001/receipt.json", "rank6-unit-001/result.json", "rank6-unit-001/step-0.log",
                   "rank6-unit-memory-watch.json", "rank6-unit-terminal-release.json", "watch_owned_memory.py",
                   "capture_run.py", "lifecycle.py", "compare_saved_checked.py", "build-006/receipt.json",
                   "build-006/source-inventory.json", "coordinate-002/receipt.json", "array-004/receipt.json"]:
        add(old+"/"+suffix)
    need(sha(files[Q+"/qualification.json"]) == QUAL, "frozen final qualification")
    # Deterministic content-addressed deduplication; broad native metadata stays metadata.
    members, preserved, origins = {}, {}, {}
    for name, body in sorted(files.items()):
        member = "objects/"+sha(body)
        need(member not in members or members[member] == body, "content-address collision")
        members[member] = body
        preserved[name] = {"member": member, **desc(body)}
        original = Q+"/build-001/source-snapshot/"+name if name in compiled else name
        origins[name] = {"origin": "/shared/external/iregi/iregi-rust/"+original, **desc(body)}
    for name, row in borrowed.items():
        need(name not in files, "own/borrowed alias collision")
        origins[name] = {"origin": row["parent_archive"]+":"+row["member"], **{k: row[k] for k in ["sha256", "bytes"]}}
    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw, filename="", mode="wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.USTAR_FORMAT) as tar:
            for name, body in sorted(members.items()):
                item = tarfile.TarInfo(name)
                item.size, item.mode, item.mtime, item.uid, item.gid = len(body), 0o644, 0, 0, 0
                item.uname = item.gname = ""
                tar.addfile(item, io.BytesIO(body))
    capsule = {"README.md": (HERE/"README.md").read_bytes(), "check.py": (HERE/"check.py").read_bytes(),
               "package.py": Path(__file__).read_bytes(), "qualification.json": files[Q+"/qualification.json"],
               "payload.tar.gz": raw.getvalue(), "payload-origins.json": (json.dumps(origins, indent=2)+"\n").encode()}
    manifest = {"schema_version": 1, "status": "source_bound_fixed_checked_suppliedG_unit_N6_rank6_saved_evidence",
                "capsule_files": {n: desc(b) for n, b in capsule.items()}, "parent_files": parents,
                "payload_members": {n: desc(b) for n, b in members.items()}, "preserved_files": preserved,
                "borrowed_files": borrowed, "compiled_sources": compiled, "compiled_source_count": 145,
                "source_parent_reused": 110, "own_source_delta": 35, "source_parent_context_sha256": wm["source_context_sha256"],
                "qualification_sha256": QUAL, "actual_build_receipt_sha256": BUILD,
                "omitted_compiled_products": {p["path"].removeprefix("/shared/external/iregi/iregi-rust/"): p["sha256"]
                                              for p in build["products"].values()},
                "source_compilation_provenance_is_historical": True, "new_native_or_process_probes": False,
                "quad_comparison_slots": 1680, "pair_comparison_slots": 840, "strict_pair_slots": 840,
                "generalized_suppliedG_or_numerical_Dual_qualified": False, "achieved_precision_qualified": False,
                "performance_qualified": False, "native_products_or_license_literals_included": False}
    OUT.mkdir(parents=True)
    for name, body in capsule.items():
        scan(name, body)
        (OUT/name).write_bytes(body)
    (OUT/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({"status": "packaged_saved_checked_G_source_and_data", "manifest_sha256": sha((OUT/"manifest.json").read_bytes()),
                      "own_aliases": len(preserved), "borrowed_aliases": len(borrowed), "payload_members": len(members),
                      "payload_bytes": len(capsule["payload.tar.gz"]), "parent_files": len(parents)}, indent=2))


if __name__ == "__main__":
    main()

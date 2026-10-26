#!/usr/bin/env python3
"""Package saved LegacyNoOp evidence only; no producer or native execution."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile

ROOT = Path.cwd().resolve()
HERE = Path(__file__).resolve().parent
OUT = ROOT/"validation/legacy-noop-rank6"
Q = "target/legacy-noop-qualification"
W = "validation/python-interface/facade-wheel-003"
N = "validation/quad-original-iregi-positive-rank-anchors"
SMALL = "validation/quad-original-iregi-small-n-rank7"
PREFIX = "/shared/external/iregi/iregi-rust/"


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
         and "__pycache__" not in p.parts and not body.startswith((b"\x7fELF", b"!<arch>", b"MZ")), "source/data only")
    need(not re.search(rb"S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}", body), "no license literal")


def unpack(path, expected):
    members = {}
    with tarfile.open(path, "r:gz") as tar:
        for item in tar:
            need(item.isfile() and item.name not in members, "regular unique archive member")
            body = tar.extractfile(item).read()
            scan(item.name, body)
            need(desc(body) == expected[item.name], "parent member identity")
            members[item.name] = body
    need(set(members) == set(expected), "closed parent archive inventory")
    return members


def main():
    need(ROOT.name == "iregi-rust" and not OUT.exists(), "new output from project cwd required")
    wm, nm, sm = [json.loads((ROOT/p/"manifest.json").read_bytes()) for p in [W, N, SMALL]]
    pins = {W: "cb7a2b09282c89b17802a485d0aca6a42b36b23b110d7fe8aead0b2ea0f74a18",
            N: "6fbc3465f3e2ee54a789b0ea556a51616744437e18d53bff29cec177755d9ddb",
            SMALL: "9b614c6567c28d23039053de390a7da5c665f4a57a978d54cd3148519fb3cb62"}
    for name, expected in pins.items():
        need(sha((ROOT/name/"manifest.json").read_bytes()) == expected, "fixed parent manifest")
    parents = {p+"/"+name: desc((ROOT/p/name).read_bytes()) for p, names in
               [(W, ["manifest.json", "sources.tar.gz"]), (N, ["manifest.json", "payload.tar.gz"]),
                (SMALL, ["manifest.json", "payload.tar.gz"])] for name in names}
    need(parents[W+"/sources.tar.gz"] == {k: wm["sources"][k] for k in ["sha256", "bytes"]}, "fixed source archive")
    need(parents[N+"/payload.tar.gz"] == nm["capsule_files"]["payload.tar.gz"]
         and parents[SMALL+"/payload.tar.gz"] == sm["capsule_files"]["payload.tar.gz"], "fixed reference archives")
    source = unpack(ROOT/W/"sources.tar.gz", wm["sources"]["members"])
    anchors = unpack(ROOT/N/"payload.tar.gz", nm["payload_members"])
    admission = unpack(ROOT/SMALL/"payload.tar.gz", sm["payload_members"])
    need(len(source) == 147, "147 selected parent sources")
    files, borrowed = {}, {}

    def add(name):
        p = ROOT/name
        need(p.is_file() and not p.is_symlink(), "regular existing saved source/data " + name)
        body = p.read_bytes()
        scan(name, body)
        need(name not in files or files[name] == body, "same-alias byte collision")
        files[name] = body

    # Include only the frozen qualification family, not later builds or overlays.
    for p in (ROOT/Q).iterdir():
        if p.is_file():
            add(str(p.relative_to(ROOT)))
    for suffix in ["build-001", "build-002", "tests-001", "128-001", "128-002", "256-001"]:
        for p in (ROOT/Q/suffix).rglob("*"):
            if p.is_file() and "source-snapshot" not in p.parts and not p.name.startswith("frozen-") and "__pycache__" not in p.parts:
                add(str(p.relative_to(ROOT)))
    for prefix in ["target/legacy-noop-frontstage-proposal", "target/legacy-noop-frontend-proposal", "target/legacy-n5-rank6-noop"]:
        for p in (ROOT/prefix).rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts:
                add(str(p.relative_to(ROOT)))
    built = json.loads(files[Q+"/build-002/receipt.json"])
    need(sha(files[Q+"/build-002/receipt.json"]) == "5dccfdf1207a30c78036f455e80e225d73e2bee19dea0e3241179becec87c545"
         and len(built["source_files"]) == 151, "fixed actual successful build")
    compiled = {}
    for build in ["build-001", "build-002"]:
        receipt = json.loads(files[Q+"/"+build+"/receipt.json"])
        for name, expected in receipt["source_files"].items():
            alias = Q+"/"+build+"/source-snapshot/"+name
            body = (ROOT/alias).read_bytes()
            scan(alias, body)
            need(sha(body) == expected, "frozen source snapshot byte identity")
            if source.get(name) == body:
                row = {"parent_archive": W+"/sources.tar.gz", "member": name, **desc(body)}
                borrowed[alias] = row
                if build == "build-002":
                    borrowed[name] = dict(row)
                    compiled[name] = {"origin": "source_parent", "member": name, **desc(body)}
            else:
                files[alias] = body
                if build == "build-002":
                    files[name] = body
                    compiled[name] = {"origin": "own_delta", "alias": alias, **desc(body)}
    # Inherit exact archived request, output, and historical independent admission.
    for parent, manifest, members, names in [
        (N, nm, anchors, ["target/quad-iregi-source-audit/future-positive-rank-requests/"+s for s in
                         ["capture-001/request-3.stdout", "capture-001/run.json", "protocol.json", "quad_n5_first_five_conditioned_rank7.txt"]]),
        (SMALL, sm, admission, ["target/quad-iregi-source-audit/rank7-n1-n5-corpus/"+s for s in
                               ["protocol.json", "capture-001/validation.json"]])]:
        for name in names:
            row = manifest["preserved_files"][name]
            body = members[row["member"]]
            need(desc(body) == {k: row[k] for k in ["sha256", "bytes"]}, "borrowed exact reference record")
            borrowed[name] = {"parent_archive": parent+"/payload.tar.gz", "member": row["member"], **desc(body)}
    need(sha(files[Q+"/qualification.json"]) == "63c3ea5cd84e84f0796df6573b706939c2a4debd515d74edf85842718c1896bc", "fixed final qualification")
    members, preserved, origins = {}, {}, {}
    for name, body in sorted(files.items()):
        member = "objects/"+sha(body)
        need(member not in members or members[member] == body, "content-address collision")
        members[member] = body
        preserved[name] = {"member": member, **desc(body)}
        original = Q+"/build-002/source-snapshot/"+name if name in compiled else name
        origins[name] = {"origin": PREFIX+original, **desc(body)}
    for name, row in borrowed.items():
        need(name not in files, "distinct own versus borrowed aliases")
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
    reused = sum(row["origin"] == "source_parent" for row in compiled.values())
    manifest = {"schema_version": 1, "status": "source_bound_retained_LegacyNoOp_N5_rank6_PV_unit_h0_saved_evidence",
                "capsule_files": {name: desc(body) for name, body in capsule.items()}, "parent_files": parents,
                "payload_members": {name: desc(body) for name, body in members.items()}, "preserved_files": preserved,
                "borrowed_files": borrowed, "compiled_sources": compiled, "compiled_source_count": 151,
                "source_parent_reused": reused, "own_source_delta": 151-reused,
                "actual_build_receipt_sha256": sha(files[Q+"/build-002/receipt.json"]),
                "qualification_sha256": sha(files[Q+"/qualification.json"]),
                "omitted_compiled_products": {p["path"].removeprefix(PREFIX): p["sha256"] for p in built["products"].values()},
                "source_compilation_and_process_provenance_are_historical": True,
                "new_native_or_process_probes": False, "quad_comparison_slots": 1680,
                "strict_80bit_pair_comparison_slots": 840, "failed_attempts_preserved": 3,
                "full_Legacy_dots_dimension_shifts_public_Dual_or_rescue_qualified": False,
                "current_generalized_suppliedG_MassTaylor_overlay_qualified": False,
                "achieved_precision_qualified": False, "performance_qualified": False,
                "native_products_license_literals_or_python_caches_included": False}
    OUT.mkdir(parents=True)
    for name, body in capsule.items():
        scan(name, body)
        (OUT/name).write_bytes(body)
    (OUT/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({"status": "packaged_saved_LegacyNoOp_source_and_data", "manifest_sha256": sha((OUT/"manifest.json").read_bytes()),
                      "compiled_sources": 151, "reused_sources": reused, "own_delta_sources": 151-reused,
                      "own_aliases": len(preserved), "borrowed_aliases": len(borrowed), "payload_members": len(members),
                      "payload_bytes": len(capsule["payload.tar.gz"]), "parent_files": len(parents)}, indent=2))


if __name__ == "__main__":
    main()

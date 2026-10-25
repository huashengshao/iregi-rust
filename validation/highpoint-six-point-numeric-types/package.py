#!/usr/bin/env python3
"""Freeze existing typed-N6 evidence only; never compile or evaluate integrals."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import re
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = ROOT/"target/public-highpoint/numeric-types-dual"
PARENT = "validation/winddown/n6-numeric-types-dual.tar.gz"
PARENT_SHA = "71c0f18de047a10f62e94958a6887509634f25794ab9afc790383b9a9bc5cfd7"
AUDITS = {
    "independent-numeric-audit.json": ("target/resume-20261025-review/typed-n6-independent-saved-numeric-audit.json",
        "c08655b8565c848f2749763d5f65639e798c43da1382da3634246192bc8fe0c2"),
    "independent-provenance-audit.json": ("target/resume-20261025-review/typed-n6-independent-provenance-audit.json",
        "438446e353fd66d26225c78e47ce1f65082d970078c8d1e032e9e673819e234c"),
    "independent-source-review.json": ("target/resume-20261025-review/dual-pilot-independent-source-review.json",
        "93455dfe745fc5a13fac12179e0b09f2762262db7ea8d75899e07189c6a461df"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def descriptor(body):
    return {"sha256": digest(body), "bytes": len(body)}


def saved(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    with Path(path).open("x") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True)+"\n")


def allowed(name, body):
    require(not body.startswith((b"\x7fELF", b"!<arch>")), "compiled output selected: "+name)
    require(not re.search(rb"S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}", body),
            "license literal selected: "+name)


def main():
    require(Path.cwd().resolve() == ROOT, "run from the project root")
    require(not (HERE/"manifest.json").exists(), "sealed capsule is immutable")
    parent_bytes = (ROOT/PARENT).read_bytes()
    require(digest(parent_bytes) == PARENT_SHA, "parent archive changed")
    inherited = {}
    with tarfile.open(fileobj=io.BytesIO(parent_bytes), mode="r:gz") as stream:
        for member in stream:
            require(member.isfile() and member.name not in inherited, "invalid parent member")
            inherited[member.name] = stream.extractfile(member).read()
    parent_index = saved(ROOT/"validation/winddown/manifest.json")["archives"]["n6-numeric-types-dual"]
    require({name: descriptor(body) for name, body in inherited.items()} == parent_index["members"],
            "parent member manifest differs")
    compiled = {"build-001/"+name: value for name, value in saved(PRIVATE/"build-001/build.json")["outputs"].items()}
    for domain in ["f64", "DoubleFloat", "Float128Dual", "Float256Dual"]:
        folder = "run-"+domain+"-001"
        compiled[folder+"/frozen-typed_n6"] = saved(PRIVATE/folder/"run.json")["outputs"]["frozen-typed_n6"]
    current, omitted = {}, {}
    for path in sorted(PRIVATE.rglob("*")):
        if not path.is_file():
            continue
        name = str(path.relative_to(PRIVATE))
        if name in compiled:
            omitted[name] = {"reason": "compiled product; digest retained from audited producer record",
                             "bytes": path.stat().st_size, "sha256": compiled[name]}
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            omitted[name] = {"reason": "generated Python bytecode", "bytes": path.stat().st_size}
            continue
        body = path.read_bytes()
        allowed(name, body)
        current[name] = body
    require(set(inherited) <= set(current), "an inherited source file disappeared")
    delta = {name: body for name, body in current.items() if inherited.get(name) != body}
    tar = io.BytesIO()
    with tarfile.open(fileobj=tar, mode="w", format=tarfile.PAX_FORMAT) as stream:
        for name, body in sorted(delta.items()):
            member = tarfile.TarInfo(name)
            member.size, member.mode, member.mtime = len(body), 0o644, 0
            stream.addfile(member, io.BytesIO(body))
    with (HERE/"payload.tar.gz").open("xb") as stream:
        stream.write(gzip.compress(tar.getvalue(), compresslevel=9, mtime=0))
    origins = {}
    for destination, (source, expected) in AUDITS.items():
        body = (ROOT/source).read_bytes()
        require(digest(body) == expected, "independent audit changed")
        allowed(destination, body)
        (HERE/destination).write_bytes(body)
        origins[destination] = source
    for name in ["qualification.json", "timing-attribution.md", "timing-attribution.json"]:
        body = current[name]
        (HERE/name).write_bytes(body)
        origins[name] = str((PRIVATE/name).relative_to(ROOT))
    borrowed_names = [PARENT, "validation/winddown/manifest.json",
        "validation/public-highpoint/fixture-conditioned_masses.json",
        "validation/public-highpoint/reference-conditioned_masses.json",
        "validation/highpoint-six-point-api/qualified-v2/public-rank3-256-001/result.json"]
    files = {str(p.relative_to(HERE)): descriptor(p.read_bytes())
             for p in sorted(HERE.rglob("*")) if p.is_file()}
    for name in files:
        allowed(name, (HERE/name).read_bytes())
    manifest = {
        "schema_version": 1, "status": "sealed_private_typed_scalar_n6_pilot_with_failures",
        "files": files, "payload_origins": origins,
        "parent_archive": {"path": PARENT, "sha256": PARENT_SHA, "members": parent_index["members"]},
        "delta_archive": {"path": "payload.tar.gz", "members": {name: descriptor(body) for name, body in delta.items()}},
        "borrowed_inputs": {name: descriptor((ROOT/name).read_bytes()) for name in borrowed_names},
        "reconstructed_private_tree": {name: descriptor(body) for name, body in current.items()},
        "reused_parent_members_unchanged": sum(inherited.get(name) == body for name, body in current.items()),
        "superseded_parent_members": {name: {"parent_sha256": digest(inherited[name]), "current_sha256": digest(delta[name])}
                                      for name in delta if name in inherited},
        "omitted_private_files": omitted,
        "source_reconstruction": "Parent 81-member committed archive plus exact delta; all 61 core files and three Rust helpers restored without copying the old core twice.",
        "compiled_outputs_or_license_literals_in_payload": False,
        "fresh_checkout_check": "python3 validation/highpoint-six-point-numeric-types/check.py",
        "fresh_checkout_source_reconstruction": "python3 validation/highpoint-six-point-numeric-types/check.py --reconstruct target/typed-n6-source-restored",
        "portable_checker_is_native_execution_requalification": False,
        "no_compiler_integral_reference_or_benchmark_executed_by_packaging": True,
    }
    save(HERE/"manifest.json", manifest)
    print(json.dumps({"status": manifest["status"], "manifest_sha256": digest((HERE/"manifest.json").read_bytes()),
        "files": len(files), "parent_members": len(inherited), "delta_members": len(delta),
        "reconstructed_private_files": len(current), "archive_bytes": (HERE/"payload.tar.gz").stat().st_size,
        "omitted_files": len(omitted)}))


if __name__ == "__main__":
    main()

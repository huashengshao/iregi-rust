#!/usr/bin/env python3
"""Package only pinned saved source/data; never read native/tool binaries."""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile

sys.dont_write_bytecode = True
ROOT = Path.cwd().resolve()
TEMPLATES = Path(__file__).resolve().parent
PRIVATE = "target/n6-rank6-generalized-quad"
PARENT = "validation/quad-original-iregi-generalized-rank7"
DESTINATION = "validation/quad-original-iregi-generalized-n6-rank6"
HISTORICAL = "/shared/external/iregi/iregi-rust/"
PROTOCOL = "277f4652434070e9b2d20cfa6be8f044b564e6ea88df35e32b314d66565c1b26"
AUDIT = "6f7fcc3ac1fe9702c2a581c9d764f1c36b452475673da0ea74e9544390933bcc"
CHECKER = "71a43fd0143294573f6c67339aa04273328291101a3753c5e30fdd4846f107c3"
PARENT_MANIFEST = "ccda92bdd0be40484b2d8762d479658ada0beb98eb610df7c96b44f7f521a0b0"
PARENT_CHECKER = "8bd9efc8ee6f95f9a0387c3510f105b9bceda416aade16c2e3bee2ef445cee7e"
LICENSE = re.compile(rb"S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}")
COMPILED = {".o", ".mod", ".smod", ".a", ".so", ".dll", ".dylib", ".pyc"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return dict(sha256=sha(body), bytes=len(body))


def safe(name):
    path = PurePosixPath(name)
    require(name and not path.is_absolute() and ".." not in path.parts and str(path) == name, "unsafe alias")


def scanned(name, body):
    safe(name)
    require(Path(name).suffix not in COMPILED and "__pycache__" not in Path(name).parts, "compiled/cache product forbidden")
    require(not body.startswith((b"\x7fELF", b"!<arch>", b"MZ")) and not LICENSE.search(body), "native or license bytes forbidden")
    return body


def read(name):
    safe(name)
    path = ROOT/name
    require(path.is_file() and not path.is_symlink(), "regular saved file required: " + name)
    return scanned(name, path.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/DESTINATION)
    args = parser.parse_args()
    require(not args.output.exists(), "preserve existing capsule")
    p = json.loads(read(PRIVATE+"/protocol.json"))
    require(sha(read(PRIVATE+"/protocol.json")) == PROTOCOL, "fixed runtime recipe")
    require(sha(read(PRIVATE+"/independent-saved-review.json")) == AUDIT and sha(read(PRIVATE+"/independent_saved_check.py")) == CHECKER, "fixed independent audit/source")
    pm_bytes = read(PARENT+"/manifest.json")
    require(sha(pm_bytes) == PARENT_MANIFEST and sha(read(PARENT+"/check.py")) == PARENT_CHECKER, "fixed parent capsule")
    pm = json.loads(pm_bytes)
    parent_files = dict(pm["parent_files"])
    for name in list(pm["capsule_files"]) + ["manifest.json"]:
        parent_files[PARENT+"/"+name] = desc(read(PARENT+"/"+name))
    require(len(parent_files) == 44, "exact inherited checkout closure")
    for name, expected in parent_files.items():
        require(desc((ROOT/name).read_bytes()) == expected, "parent closure drift")
    spec = importlib.util.spec_from_file_location("n6_capsule_saved_parent_packaging", ROOT/PARENT/"check.py")
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    inherited = parent.restore_files(pm)
    inherited.update({name: (ROOT/name).read_bytes() for name in parent_files})
    by_descriptor = {}
    for name, body in sorted(inherited.items()):
        by_descriptor.setdefault((sha(body), len(body)), name)
    bodies = {}
    for path in sorted((ROOT/PRIVATE).rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            name = str(path.relative_to(ROOT))
            bodies[name] = read(name)
    omitted = {}
    required_parent = {}
    for absolute, expected in p["bindings"].items():
        if absolute == p["binary"] or absolute in p["tools"].values():
            omitted[absolute] = expected
            continue
        require(absolute.startswith(HISTORICAL), "unexpected source guard outside project")
        name = absolute.removeprefix(HISTORICAL)
        if name in inherited:
            require(sha(inherited[name]) == expected, "exact inherited guard")
            required_parent[name] = desc(inherited[name])
        else:
            body = read(name)
            require(sha(body) == expected, "available narrow source guard")
            bodies[name] = body
    require(len(omitted) == 3, "one native and two tool historical guards")
    members, preserved, aliases, capsule_aliases, origins = {}, {}, {}, {}, {}
    for name, body in sorted(bodies.items()):
        expected = desc(body)
        if name == PRIVATE+"/independent_saved_check.py":
            capsule_aliases[name] = dict(capsule_file="independent_saved_check.py", **expected)
        elif (expected["sha256"], expected["bytes"]) in by_descriptor:
            source = by_descriptor[(expected["sha256"], expected["bytes"])]
            require(inherited[source] == body, "borrowed bytes exactly equal")
            aliases[name] = dict(inherited_source=source, **expected)
        else:
            member = "objects/"+expected["sha256"]
            require(member not in members or members[member] == body, "content member collision")
            members[member] = body
            preserved[name] = dict(member=member, **expected)
        origins[name] = dict(origin=HISTORICAL+name, **expected)
    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            for name, body in sorted(members.items()):
                item = tarfile.TarInfo(name)
                item.size, item.mode, item.mtime, item.uid, item.gid = len(body), 0o644, 0, 0, 0
                item.uname = item.gname = ""
                archive.addfile(item, io.BytesIO(body))
    capsule = {name: scanned(name, (TEMPLATES/name).read_bytes()) for name in ["check.py", "package.py", "README.md"]}
    capsule.update({"independent_saved_check.py": bodies[PRIVATE+"/independent_saved_check.py"],
                    "qualification.json": bodies[PRIVATE+"/anchor-admission.json"],
                    "payload.tar.gz": raw.getvalue(),
                    "payload-origins.json": (json.dumps(origins, indent=2)+"\n").encode()})
    manifest = dict(schema_version=1, status="scoped_saved_original_generalized_N6_rank6_reference_capsule",
                    capsule_directory=DESTINATION, protocol_sha256=PROTOCOL,
                    independent_audit_sha256=AUDIT, byte_identical_independent_checker_sha256=CHECKER,
                    capsule_files={name: desc(body) for name, body in capsule.items()},
                    parent_files=parent_files, required_parent_aliases=required_parent,
                    payload_members={name: desc(body) for name, body in members.items()},
                    preserved_files=preserved, inherited_aliases=aliases, capsule_aliases=capsule_aliases,
                    historical_omitted_guards=omitted, new_original_N6_arrays=7,
                    complete_complex_slots=5880, independently_replayed_records=5166,
                    finite_generalized_coefficients_independently_certified=False,
                    Rust_Dual_physical_or_performance_qualified=False,
                    native_or_license_bytes_included=False,
                    archived_initial_v1_source_timing_finding=True)
    args.output.mkdir(parents=True)
    for name, body in capsule.items():
        (args.output/name).write_bytes(body)
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps(dict(status="packaged_saved_bytes_pending_portable_replay", manifest_sha256=sha((args.output/"manifest.json").read_bytes()),
                          payload_sha256=sha(raw.getvalue()), payload_bytes=len(raw.getvalue()), payload_members=len(members),
                          own_aliases=len(bodies), inherited_parent_files=len(parent_files)), indent=2))


if __name__ == "__main__":
    main()

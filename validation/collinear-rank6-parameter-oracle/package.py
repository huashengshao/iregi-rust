#!/usr/bin/env python3
"""Build the deterministic saved-data capsule; no native or numerical work."""
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = "validation/orthogonal-rank6-current-cli"
PRIVATE = ("target/collinear-rank6-parameter-oracle",
           "target/collinear-rank6-parameter-oracle-refinement-v2",
           "target/collinear-rank6-parameter-oracle-refinement-v3")


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def desc(body):
    return {"sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")


def main():
    parent_manifest = json.loads((ROOT / PARENT / "manifest.json").read_bytes())
    require(desc((ROOT / PARENT / "manifest.json").read_bytes())["sha256"]
            == "af6a1d77de0c1ef9aeafe49833f2c140a7a75cd9b2fdca0578811cdb407be129",
            "fixed orthogonal parent")
    spec = importlib.util.spec_from_file_location("package_collinear_parent", ROOT / PARENT / "check.py")
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    inherited = parent.restore_files(parent_manifest)
    by_hash = {}
    for alias, body in sorted(inherited.items()):
        by_hash.setdefault(desc(body)["sha256"], alias)
    files = {}
    for prefix in PRIVATE:
        for path in sorted((ROOT / prefix).rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            require(path.suffix in {".py", ".json", ".md", ".log", ".patch", ".diff"},
                    "only selected source and saved evidence")
            body = path.read_bytes()
            require(len(body) < 16000000 and not body.startswith(b"\x7fELF"), "bounded noncompiled evidence")
            require(b"export SYMBOLICA_LICENSE=" not in body, "license contents forbidden")
            files[str(path.relative_to(ROOT))] = body
    members, preserved, borrowed, origins, own_by_hash = {}, {}, {}, {}, {}
    for alias, body in sorted(files.items()):
        row = desc(body)
        if row["sha256"] in by_hash:
            row["parent_source_alias"] = by_hash[row["sha256"]]
            borrowed[alias] = dict(row)
        else:
            member = own_by_hash.setdefault(row["sha256"], alias)
            members[member] = body
            row["member"] = member
            preserved[alias] = dict(row)
        origins[alias] = dict(row)
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, body in sorted(members.items()):
            item = tarfile.TarInfo(name)
            item.size, item.mode, item.mtime = len(body), 0o644, 0
            item.uid = item.gid = 0
            item.uname = item.gname = ""
            archive.addfile(item, io.BytesIO(body))
    with (HERE / "payload.tar.gz").open("wb") as stream:
        with gzip.GzipFile(fileobj=stream, mode="wb", filename="", mtime=0) as compressor:
            compressor.write(raw.getvalue())
    write("origins.json", origins)
    new = ROOT / PRIVATE[-1]
    (HERE / "qualification.json").write_bytes((new / "anchor-admission.json").read_bytes())
    (HERE / "independent_numeric_audit.py").write_bytes((new / "independent/audit_saved.py").read_bytes())
    parent_files = dict(parent_manifest["parent_files"])
    for name in set(parent_manifest["capsule_files"]) | {"manifest.json"}:
        alias = PARENT + "/" + name
        parent_files[alias] = desc((ROOT / alias).read_bytes())
    evidence = dict(inherited)
    for alias, body in files.items():
        require(alias not in evidence or evidence[alias] == body, "alias collision")
        evidence[alias] = body
    capsule_files = {str(p.relative_to(HERE)): desc(p.read_bytes()) for p in sorted(HERE.iterdir())
                     if p.is_file() and p.name != "manifest.json"}
    write("manifest.json", {
        "schema_version": 1,
        "status": "saved_independently_audited_scoped_collinear_rank6_parameter_reference",
        "capsule_files": capsule_files,
        "parent_files": dict(sorted(parent_files.items())),
        "parent_manifest_sha256": desc((ROOT / PARENT / "manifest.json").read_bytes())["sha256"],
        "parent_aliases": len(inherited),
        "preserved_files": preserved,
        "inherited_aliases": borrowed,
        "payload_members": {name: desc(body) for name, body in sorted(members.items())},
        "restored_evidence_aliases": len(evidence),
        "qualification_sha256": desc((HERE / "qualification.json").read_bytes())["sha256"],
        "independent_checker_sha256": desc((HERE / "independent_numeric_audit.py").read_bytes())["sha256"],
        "independent_numeric_receipt_sha256": desc((new / "independent/receipt.json").read_bytes())["sha256"],
        "coarse_failed_records_preserved_and_replayed": 13470,
        "refinement_records_replayed": 15150,
        "refinement_empirical_failures": 0,
        "coarse_empirical_failures_retained": 6,
        "unique_saved_grids": 8,
        "accepted_moments": 210,
        "retained_moments": 330,
        "new_native_rows": 4608,
        "new_native_batches": 18,
        "scoped_order48_identity_anchor_admitted": True,
        "TIRust_agreement_qualified": False,
        "rank7_accuracy_qualified": False,
        "rigorous_error_bounds": False,
        "Float_or_Dual_or_physical_or_performance_qualified": False,
        "native_PID_package_binary_attestations_freshly_reenacted": False,
        "license_literal_included": False,
        "compiled_or_numerical_package_contents_included": False,
        "minimal_checkout_files": len(parent_files) + len(capsule_files) + 1,
    })
    print(json.dumps({"preserved_aliases": len(preserved), "borrowed_aliases": len(borrowed),
                      "payload_members": len(members), "restored_aliases": len(evidence),
                      "payload": desc((HERE / "payload.tar.gz").read_bytes())}))


if __name__ == "__main__":
    main()

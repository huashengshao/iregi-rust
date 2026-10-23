"""Freeze the Symbolica-only preparation and its complete text provenance."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile


ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
CAPTURE = ROOT/"target/collier-reference/n5-identities-preparation-attempt006"
OUTPUT = HERE/"prepared001"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    data = json.loads((CAPTURE/"preparation.json").read_text())
    if data["status"] != "prepared-not-numerically-qualified" or data["guards_unchanged"] is not True:
        raise ValueError("complete guarded preparation required")
    if OUTPUT.exists():
        raise ValueError("preserve existing preparation package")
    OUTPUT.mkdir()
    raw = (CAPTURE/"preparation.json").read_bytes()
    (OUTPUT/"preparation.json.gz").write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    producer = OUTPUT/"producer"
    producer.mkdir()
    for name in ("prepare.py", "source-review.json", "source-readiness.json"):
        shutil.copyfile(HERE/name, producer/name)
    shutil.copyfile(ROOT/"docs/research/collier-n5-identities.md", producer/"analytic-plan.md")
    shutil.copyfile(Path(__file__), OUTPUT/"package_preparation.py")
    shutil.copyfile(CAPTURE.parent/"n5-identities-preparation-attempt006-outer.json", OUTPUT/"outer-receipt.json")
    stream, members = io.BytesIO(), {}
    with tarfile.open(fileobj=stream, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for path in sorted(CAPTURE.iterdir()):
            if not path.is_file() or path.name == "preparation.json" or path.suffix not in (".dot", ".json", ".log"):
                continue
            blob = path.read_bytes()
            member = tarfile.TarInfo(path.name)
            member.size, member.mode, member.mtime = len(blob), 0o644, 0
            archive.addfile(member, io.BytesIO(blob))
            members[path.name] = hashlib.sha256(blob).hexdigest()
    (OUTPUT/"artifacts.tar.gz").write_bytes(gzip.compress(stream.getvalue(), compresslevel=9, mtime=0))
    result = {"kind": "n5-symbolica-identity-preparation-durable", "status": "prepared-not-numerically-qualified",
        "preparation": {"path": str((OUTPUT/"preparation.json.gz").relative_to(ROOT)), "sha256": sha(OUTPUT/"preparation.json.gz"),
            "uncompressed_sha256": hashlib.sha256(raw).hexdigest(), "uncompressed_bytes": len(raw)},
        "archive": {"path": str((OUTPUT/"artifacts.tar.gz").relative_to(ROOT)), "sha256": sha(OUTPUT/"artifacts.tar.gz"),
            "uncompressed_sha256": hashlib.sha256(stream.getvalue()).hexdigest(), "members": members},
        "files": {str(p.relative_to(ROOT)): sha(p) for p in sorted(OUTPUT.rglob("*")) if p.is_file()},
        "unique_polynomials": len(data["polynomials"]), "aliases": len(data["aliases"]),
        "branches": len(data["branches"]), "planned_reference_requests": len(data["reference_request_inventory"]),
        "cli": {p: expected for p, expected in data["guards"].items() if p == "target/optimized/release/iregi-rust"},
        "reference_reduction_performed": False, "performance_evidence": False, "independent_audit": "pending"}
    (OUTPUT/"qualification.json").write_text(json.dumps(result, indent=2)+"\n")
    print(OUTPUT/"qualification.json")


if __name__ == "__main__":
    main()

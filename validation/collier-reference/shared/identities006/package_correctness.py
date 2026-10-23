"""Preserve N5 identity/reference evidence without executing calculations."""
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile


ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
CAPTURE = ROOT/"target/collier-reference/n5-identities-correctness-attempt006"
OUTPUT = HERE/"correctness001"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    capture_path = CAPTURE/"results.json"
    data = json.loads(capture_path.read_text())
    if data["status"] != "capture-complete" or data["guards_unchanged"] is not True:
        raise ValueError("complete guarded correctness capture required")
    if OUTPUT.exists():
        raise ValueError("preserve existing correctness package")
    OUTPUT.mkdir()
    raw = capture_path.read_bytes()
    (OUTPUT/"capture.json.gz").write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    producer = OUTPUT/"producer"
    producer.mkdir()
    for name in ("run.py", "protocol.py", "test_protocol.py", "correctness-source-review.json", "correctness-source-readiness.json"):
        shutil.copyfile(HERE/name, producer/name)
    shutil.copytree(HERE/"correctness-saved-data-tests", producer/"saved-data-tests")
    for path in (ROOT/"validation/collier-reference/n4/check_identities.py",
                 ROOT/"validation/pv-high-rank/compare_precision_oracle.py", ROOT/"validation/collier-reference/run.py",
                 ROOT/"validation/benchmark/run.py", ROOT/"validation/collier-reference/shared/attempt004/producer/support.py"):
        target = producer/"reused"/path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    shutil.copyfile(ROOT/"docs/research/collier-n5-identities.md", producer/"analytic-plan.md")
    shutil.copyfile(Path(__file__), OUTPUT/"package_correctness.py")
    shutil.copyfile(CAPTURE.parent/"n5-identities-correctness-attempt006-outer.json", OUTPUT/"outer-receipt.json")
    stream, members = io.BytesIO(), {}
    with tarfile.open(fileobj=stream, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for path in sorted(CAPTURE.glob("*.log")):
            blob = path.read_bytes()
            info = tarfile.TarInfo(path.name)
            info.size, info.mode, info.mtime = len(blob), 0o644, 0
            archive.addfile(info, io.BytesIO(blob))
            members[path.name] = hashlib.sha256(blob).hexdigest()
    (OUTPUT/"stderr-artifacts.tar.gz").write_bytes(gzip.compress(stream.getvalue(), compresslevel=9, mtime=0))
    groups = {}
    for name in ("prefix_rows", "routing_rows", "finiteness_rows"):
        rows = data["identities"][name]
        checks = [c for row in rows for lane in row["lanes"] for c in lane.get("checks", [])]
        groups[name] = {"rows": len(rows), "lane_status_counts": dict(Counter(lane["status"] for row in rows for lane in row["lanes"])),
            "residual_records": len(checks), "complex_slot_comparisons": sum(len(c["slots"]) for c in checks),
            "maximum_normalized_error": max((c["maximum_normalized_error"] for c in checks), default=0.)}
    rows = data["identities"]["branch_identities"]
    checks = [c for row in rows for c in row["checks"]]
    groups["branch_identities"] = {"rows": len(rows), "row_status_counts": dict(Counter(row["status"] for row in rows)),
        "residual_records": len(checks), "complex_slot_comparisons": sum(len(c["slots"]) for c in checks),
        "maximum_normalized_error": max((c["maximum_normalized_error"] for c in checks), default=0.)}
    summary = {"kind": "n5-independent-identity-correctness-summary", "status": data["qualification"],
        "attempt_status_counts": data["attempt_status_counts"], "assembled_responses": len(data["assembled_responses"]),
        "checks": groups, "original34_rows": data["original34_rows"],
        "elapsed_seconds": data["elapsed_seconds"], "source_input_binary_guards_unchanged": True,
        "independent_saved_data_audit": "pending", "performance_evidence": False,
        "scope": "Three retained massive N5 branches; r0/r1/r2 complete prefix, denominator/trace, pinched and routed arrays; no physical-process/MadLoop or performance claim"}
    (OUTPUT/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    result = {"kind": "n5-independent-identity-correctness-durable", "status": "capture-preserved-audit-pending",
        "preparation_qualification": {"path": str((HERE/"prepared001/qualification.json").relative_to(ROOT)),
            "sha256": sha(HERE/"prepared001/qualification.json")},
        "capture": {"path": str((OUTPUT/"capture.json.gz").relative_to(ROOT)), "sha256": sha(OUTPUT/"capture.json.gz"),
            "uncompressed_sha256": hashlib.sha256(raw).hexdigest(), "uncompressed_bytes": len(raw)},
        "stderr": {"path": str((OUTPUT/"stderr-artifacts.tar.gz").relative_to(ROOT)), "sha256": sha(OUTPUT/"stderr-artifacts.tar.gz"),
            "uncompressed_sha256": hashlib.sha256(stream.getvalue()).hexdigest(), "members": members},
        "files": {str(p.relative_to(ROOT)): sha(p) for p in sorted(OUTPUT.rglob("*")) if p.is_file()},
        "reference_requests": 46, "reference_build_performed": False, "performance_evidence": False,
        "independent_audit": "pending"}
    (OUTPUT/"qualification.json").write_text(json.dumps(result, indent=2)+"\n")
    print(OUTPUT/"qualification.json")


if __name__ == "__main__":
    main()

"""Preserve the exact-eight correctness append without executing references."""
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
CAPTURE = ROOT/"target/collier-reference/shared-append-attempt005"
OUTPUT = ROOT/"validation/collier-reference/shared/attempt005"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n")


def main():
    if OUTPUT.exists():
        raise ValueError("preserve existing append package")
    capture = json.loads((CAPTURE/"results.json").read_text())
    outer_path = CAPTURE.parent/"shared-append-attempt005-outer.json"
    outer = json.loads(outer_path.read_text())
    if (capture.get("status") != "capture-complete" or capture.get("guards_unchanged") is not True
            or outer["status"] != "exited" or outer["exit_code"] != 0):
        raise ValueError("complete guarded append required; native rejections remain visible")
    if len(capture["attempts"]) != 8 or len(capture["all_original_rows"]) != 34:
        raise ValueError("exact eight attempts and all34 original rows required")
    OUTPUT.mkdir(parents=True)
    raw = (CAPTURE/"results.json").read_bytes()
    (OUTPUT/"capture.json.gz").write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    producer = OUTPUT/"producer"
    producer.mkdir()
    for file in ("append.py", "test_admission.py", "inventory.json", "PLAN.md", "source-review.json", "source-readiness.json"):
        shutil.copyfile(HERE/file, producer/file)
    shutil.copytree(HERE/"saved-data-tests", producer/"saved-data-tests")
    shutil.copyfile(Path(__file__), OUTPUT/"package.py")
    shutil.copyfile(outer_path, OUTPUT/"outer-receipt.json")
    buffer, members = io.BytesIO(), {}
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for file in sorted(CAPTURE.glob("*.log")):
            blob = file.read_bytes()
            member = tarfile.TarInfo(file.name)
            member.size, member.mode, member.mtime = len(blob), 0o644, 0
            archive.addfile(member, io.BytesIO(blob))
            members[file.name] = hashlib.sha256(blob).hexdigest()
    (OUTPUT/"stderr-artifacts.tar.gz").write_bytes(gzip.compress(buffer.getvalue(), compresslevel=9, mtime=0))
    joined = next(row for row in capture["all_original_rows"] if row["id"] == "n7-r2-conditioned-cycle32" and row["batch_width"] == 32)
    policies = {}
    for key, checks in joined.get("append005_checks", {}).items():
        response = joined["append005_responses"][key]
        policies[key] = {"stable": response["stable"], "native_array_agreement": checks["native_array_agreement"],
                         "uv_identities": checks["uv_identities"], "pole_probes": checks.get("pole_probes"),
                         "lane_status_counts": dict(Counter(lane["status"] for lane in response["lanes"])),
                         "native_flags": sorted({(lane.get("worst_err_flag"), lane.get("worst_acc_flag")) for lane in response["lanes"]})}
    coverage = [{k: row[k] for k in ("id", "n", "rank", "batch_width", "status")} for row in capture["all_original_rows"]]
    for row in coverage:
        if row["id"] == joined["id"] and row["batch_width"] == 32:
            row["append005_status"] = joined.get("append005_status")
            row["append005_complete_policy_responses"] = list(joined["append005_responses"])
    summary = {"kind": "collier-shared-exact-eight-append-summary", "status": joined.get("append005_status"),
               "parent_capture": capture["parent_capture"], "parent_qualification": capture["parent_qualification"],
               "families": 17, "coverage_rows": coverage, "unchanged_parent_validated_group_requests": 239,
               "append_group_status_counts": capture["attempt_status_counts"], "append_attempts": len(capture["attempts"]),
               "joined_policies": policies, "elapsed_seconds": capture["elapsed_seconds"],
               "performance_evidence": False, "reference_build_performed": False,
               "qualification_scope": "Complete native response/failure visibility only; independent trace/routing identities and audit remain separate"}
    save(OUTPUT/"summary.json", summary)
    qualification = {"kind": "collier-shared-exact-eight-append-durable", "status": "capture-preserved-audit-pending",
        "parent_capture": capture["parent_capture"], "parent_qualification": capture["parent_qualification"],
        "artifacts": {"capture": {"path": str((OUTPUT/"capture.json.gz").relative_to(ROOT)),
            "sha256": sha(OUTPUT/"capture.json.gz"), "uncompressed_sha256": hashlib.sha256(raw).hexdigest(),
            "uncompressed_bytes": len(raw)}, "stderr": {"path": str((OUTPUT/"stderr-artifacts.tar.gz").relative_to(ROOT)),
            "sha256": sha(OUTPUT/"stderr-artifacts.tar.gz"), "uncompressed_sha256": hashlib.sha256(buffer.getvalue()).hexdigest(),
            "members": members}},
        "files": {str(file.relative_to(ROOT)): sha(file) for file in sorted(OUTPUT.rglob("*")) if file.is_file()},
        "performance_evidence": False, "reference_build_performed": False, "independent_audit": "pending"}
    save(OUTPUT/"qualification.json", qualification)
    print(OUTPUT/"qualification.json")


if __name__ == "__main__":
    main()

"""Preserve a complete or partial shared-reference capture; never run kernels."""
import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile


ROOT = Path.cwd()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+"\n")


def archive(folder, destination, raw_name):
    stream, inventory = io.BytesIO(), {}
    with tarfile.open(fileobj=stream, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for item in sorted(folder.rglob("*")):
            if not item.is_file() or item.name == raw_name or "__pycache__" in item.parts:
                continue
            relative = item.relative_to(folder)
            if not (relative.parts[0] in ("source", "sources") or item.suffix in (".dot", ".json", ".log")):
                continue
            contents = item.read_bytes()
            info = tarfile.TarInfo(relative.as_posix())
            info.size, info.mode, info.mtime = len(contents), 0o644, 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tar.addfile(info, io.BytesIO(contents))
            inventory[relative.as_posix()] = hashlib.sha256(contents).hexdigest()
    destination.write_bytes(gzip.compress(stream.getvalue(), compresslevel=9, mtime=0))
    return {"path": str(destination.relative_to(ROOT)), "sha256": sha(destination), "files": inventory,
            "uncompressed_archive_sha256": hashlib.sha256(stream.getvalue()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("input", "build", "capture", "tests", "review", "output"):
        parser.add_argument("--"+option, required=True, type=Path)
    parser.add_argument("--legacy-audit", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT/"validation/collier-reference/shared"):
        parser.error("new project shared-reference evidence directory required")
    inputs = json.loads(args.input.read_text())
    build = json.loads(args.build.read_text())
    capture = json.loads(args.capture.read_text())
    if (capture.get("status") != "capture-complete" or capture.get("guards_unchanged") is not True
            or build.get("status") != "built" or build.get("guards_unchanged") is not True
            or inputs.get("guards_unchanged") is not True):
        raise ValueError("guarded complete capture required; failed rows are retained, not removed")
    output.mkdir(parents=True)
    artifacts = {}
    for label, path in (("inputs", args.input), ("build", args.build), ("capture", args.capture)):
        raw = path.read_bytes()
        destination = output/(label+".json.gz")
        destination.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
        if gzip.decompress(destination.read_bytes()) != raw:
            raise ValueError("compressed payload differs")
        artifacts[label] = {"path": str(destination.relative_to(ROOT)), "sha256": sha(destination),
                            "uncompressed_sha256": sha(path), "uncompressed_bytes": len(raw)}
        artifacts[label+"-artifacts"] = archive(path.parent, output/(label+"-artifacts.tar.gz"), path.name)
    producer = output/"producer"
    producer.mkdir()
    for source in sorted((args.build.parent/"source").glob("*")):
        if source.is_file():
            shutil.copyfile(source, producer/source.name)
    shutil.copytree(args.tests, producer/"protocol-tests")
    shutil.copyfile(args.review, producer/"source-review.json")
    if args.legacy_audit is not None:
        audit = json.loads(args.legacy_audit.read_text())
        if (audit.get("status") != "passed" or audit.get("actual_legacy_responses") != 32
                or audit.get("fixed_rows") != 16 or audit.get("reference_kernels_executed") is not False):
            raise ValueError("passing actual32-response source-only legacy audit required")
        for path, expected in audit["bindings"].items():
            if sha(ROOT/path) != expected:
                raise ValueError("legacy-audit binding changed")
        shutil.copyfile(args.legacy_audit, producer/"legacy-header-preflight-audit.json")
        for name in ("legacy-header-preflight-audit-v1.json",):
            previous = args.legacy_audit.parent/name
            if previous.exists():
                shutil.copyfile(previous, producer/name)
        for name in ("legacy_header_audit.py", "legacy_header_audit_v1.py"):
            shutil.copyfile(ROOT/"validation/collier-reference/shared/diagnostics"/name, producer/name)
    shutil.copyfile(Path(__file__), output/"package.py")
    rows = []
    for row in capture["rows"]:
        summary = {k: row[k] for k in ("id", "n", "rank", "batch_width", "status")}
        summary.update(interface=row.get("interface"), error=row.get("error"), reason=row.get("reason"),
                       responses_retained=list(row["responses"]),
                       iregi_frozen_regression=row.get("iregi_frozen_regression"))
        attempts = [a for requests in row.get("request_attempts", {}).values() for a in requests]
        summary["resource_incomplete"] = any(a["status"] == "not_run" for a in attempts)
        summary["group_request_status_counts"] = dict(Counter(a["status"] for a in attempts))
        summary["policies"] = {}
        for mode, policy in row.get("collier_policies", {}).items():
            response = row["responses"].get("generic-"+mode, {})
            summary["policies"][mode] = {
                "status": policy["status"], "interface": policy.get("interface"),
                "native_array_agreement": policy.get("native_array_agreement"),
                "old_wrapper_regression": policy.get("old_wrapper_regression"),
                "error": policy.get("error"),
                "worst_error_flags": sorted({l["worst_err_flag"] for l in response.get("lanes", [])}),
                "worst_accuracy_flags": sorted({l["worst_acc_flag"] for l in response.get("lanes", [])})}
        rows.append(summary)
    summary = {"kind": "shared-reference-fixed-matrix-summary", "status": "incomplete-fixed-failures-retained",
               "row_status_counts": dict(Counter(row["status"] for row in rows)), "rows": rows,
               "families": len(inputs["cases"]), "planned_rows": len(rows),
               "responses_retained": sum(len(row["responses"]) for row in capture["rows"]),
               "isolated_requests_retained": capture.get("isolated_request_count"),
               "source_binary_input_guards_unchanged": capture["guards_unchanged"],
               "elapsed_seconds": capture["elapsed_seconds"], "performance_evidence": False,
               "production_changed": False, "libraries_changed": False,
               "input_preparations": len(inputs["constant_preparations"]),
               "sample_domain_proofs": len(inputs["sample_domain_proofs"])}
    write_json(output/"summary.json", summary)
    artifacts["summary"] = {"path": str((output/"summary.json").relative_to(ROOT)), "sha256": sha(output/"summary.json")}
    qualification = {"kind": "shared-reference-durable-bindings", "status": "incomplete-coverage-diagnostics-retained",
                     "artifacts": artifacts,
                     "producer": {str(p.relative_to(ROOT)): sha(p) for p in sorted(producer.rglob("*")) if p.is_file()},
                     "packager": {"path": str((output/"package.py").relative_to(ROOT)), "sha256": sha(output/"package.py")},
                     "immutable_library_sha256": build["library"]["sha256"],
                     "earlier_generic_failure": "validation/collier-reference/shared/attempt001/qualification.json",
                     "earlier_n4_failures": "validation/collier-reference/n4/diagnostics-v1/qualification.json",
                     "timing_performed": False, "independent_audit": "pending"}
    write_json(output/"qualification.json", qualification)
    print(output/"qualification.json")


if __name__ == "__main__":
    main()

"""Package retained N4 correctness failures and diagnostics; runs no kernels."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile


ROOT = Path.cwd()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+"\n")


def compress(path, destination):
    raw = path.read_bytes()
    destination.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    assert gzip.decompress(destination.read_bytes()) == raw
    return {"path": str(destination.relative_to(ROOT)), "sha256": digest(destination),
            "uncompressed_sha256": hashlib.sha256(raw).hexdigest(), "uncompressed_bytes": len(raw)}


def source_archive(directory, destination, *, identity=False):
    entries = sorted(p for p in directory.rglob("*") if p.is_file()
                     and ("sources" in p.relative_to(directory).parts
                          or (identity and p.suffix in (".dot", ".json", ".log") and p.name != "results.json")))
    buffer = io.BytesIO()
    inventory = {}
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for p in entries:
            name = p.relative_to(directory).as_posix()
            data = p.read_bytes()
            entry = tarfile.TarInfo(name)
            entry.size, entry.mtime, entry.mode = len(data), 0, 0o644
            entry.uid = entry.gid = 0
            entry.uname = entry.gname = ""
            archive.addfile(entry, io.BytesIO(data))
            inventory[name] = hashlib.sha256(data).hexdigest()
    destination.write_bytes(gzip.compress(buffer.getvalue(), compresslevel=9, mtime=0))
    return {"path": str(destination.relative_to(ROOT)), "sha256": digest(destination),
            "files": inventory, "uncompressed_archive_sha256": hashlib.sha256(buffer.getvalue()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "validation/collier-reference/n4"):
        parser.error("new directory inside validation/collier-reference/n4 required")
    diagnostic_path = ROOT / "target/collier-reference/n4-diagnostic-attempt002/results.json"
    identity_path = ROOT / "target/collier-reference/n4-identity-attempt002/results.json"
    diagnostic = json.loads(diagnostic_path.read_text())
    identities = json.loads(identity_path.read_text())
    if (diagnostic["status"] != "diagnostic_complete" or identities["status"] != "identity_checks_complete"
            or not diagnostic["guards_unchanged"] or not identities["guards_unchanged"]):
        raise ValueError("complete guarded diagnostic and identity runs required")
    output.mkdir(parents=True)
    artifacts = {}
    for name, path in (("diagnostic-complete", diagnostic_path), ("identity-complete", identity_path),
                       ("diagnostic-attempt001-failed", ROOT / "target/collier-reference/n4-diagnostic-attempt001/results.json"),
                       ("identity-attempt001-earlier-context", ROOT / "target/collier-reference/n4-identity-attempt001/results.json")):
        artifacts[name] = compress(path, output / f"{name}.json.gz")
        artifacts[name+"-artifacts"] = source_archive(path.parent, output / f"{name}-artifacts.tar.gz", identity=name.startswith("identity"))
    for name, source in (("driver-build.json", ROOT / "target/reference/collier/n4-diagnostic-build001/build.json"),
                         ("driver-build-link.log", ROOT / "target/reference/collier/n4-diagnostic-build001/link.log"),
                         ("driver-source-review.json", ROOT / "validation/collier-reference/n4/diagnostic-driver-root-review.json"),
                         ("diagnostic-link-startup-failure.json", ROOT / "validation/collier-reference/n4/diagnostic-link-startup-failure.json")):
        shutil.copyfile(source, output / name)
        artifacts[name] = {"path": str((output/name).relative_to(ROOT)), "sha256": digest(output/name)}
    rows = []
    for row in diagnostic["n4"]:
        coli = next(x for x in row["collier"] if x["mode"] == 1 and x["command"] == "CHECK")
        dd = next(x for x in row["collier"] if x["mode"] == 2 and x["command"] == "CHECK")
        proof = next(x for x in identities["rows"] if x["id"] == row["id"]
                     and x["batch_width"] == row["batch_width"] and x["engine"] == "diagnostic")
        raw_comparison = coli["diagnostic_only_array_agreement"]["raw_numeric_agreement"]
        rows.append({"id": row["id"], "rank": row["rank"], "batch_width": row["batch_width"],
                     "status": "accepted-complete-array-agreement" if coli["accepted_array_agreement"]["status"] == "passed" else "rejected-by-collier",
                     "accepted_array_agreement": coli["accepted_array_agreement"],
                     "collier_worst_error_flags": sorted({l["worst_err_flag"] for l in coli["response"]["lanes"]}),
                     "collier_worst_accuracy_flags": sorted({l["worst_acc_flag"] for l in coli["response"]["lanes"]}),
                     "raw_diagnostic_maximum_normalized_error": raw_comparison["max_error"],
                     "raw_diagnostic_qualifies": False, "independent_identity_status": proof["identity_status"],
                     "raw_diagnostic_identity_maximum_normalized_error": max(c["maximum_normalized_error"] for lane in proof["lanes"] for c in lane["checks"]),
                     "iregi_mode_agreement": row["iregi_mode_agreement"],
                     "dd_status": "rejected" if not dd["response"]["stable"] else "accepted",
                     "dd_worst_error_flags": sorted({l["worst_err_flag"] for l in dd["response"]["lanes"]}),
                     "timing": None})
    summary = {"kind": "collier-n4-bounded-correctness-summary", "status": "incomplete",
               "accepted_coli_rows": sum(r["status"] == "accepted-complete-array-agreement" for r in rows),
               "fixed_rows": len(rows), "timing_performed": False, "timing_qualified": False,
               "tolerance": 1e-10, "inputs_replaced": False, "thresholds_changed": False,
               "scope": "ordinary massive N4rank0..3 batch1/32; complete arrays/all4native Laurent slots",
               "interpretation": "COLI1 higher ranks meet external numeric/identity tolerance only as rejected diagnostics; AccFlag−1 still prevents acceptance. DD2 returns internal ErrFlag−10; its raw arrays are invalid reference evidence.",
               "initial8_successful_outputs_identical": all(r["successful_outputs_identical"] for r in diagnostic["initial8_regression"]),
               "diagnostic_elapsed_seconds": diagnostic["elapsed_seconds"], "identity_elapsed_seconds": identities["elapsed_seconds"],
               "symbolica_prepared_polynomials": len(identities["polynomials"]),
               "iregi_identity_maximum_normalized_error": max(c["maximum_normalized_error"] for r in identities["rows"] if r["engine"] == "iregi" for lane in r["lanes"] for c in lane["checks"]),
               "rows": rows}
    write_json(output / "summary.json", summary)
    artifacts["summary"] = {"path": str((output/"summary.json").relative_to(ROOT)), "sha256": digest(output/"summary.json")}
    bindings = {str(p.relative_to(ROOT)): digest(p) for p in sorted((ROOT/"validation/collier-reference/n4").glob("*.py"))}
    bindings.update({str(p.relative_to(ROOT)): digest(p) for p in
                     (ROOT/"validation/collier-reference/n4/diagnostic-driver.f90", ROOT/"docs/research/collier-n4-identities.md",
                      ROOT/"validation/collier-reference/extensions/n4-inputs.json",
                      ROOT/"validation/collier-reference/extensions/n4-inputs-provenance.json")})
    record = {"kind": "collier-n4-diagnostic-package-bindings", "status": "diagnostic-only-incomplete-qualification",
              "performance_claim": None, "artifacts": artifacts, "source_bindings": bindings,
              "earlier_rejections_retained": "validation/collier-reference/n4/history/",
              "initial8_timing_unchanged": "validation/collier-reference/timing-initial8/qualification.json",
              "library_rebuilt": False, "production_changed": False}
    write_json(output / "qualification.json", record)
    print(output / "qualification.json")


if __name__ == "__main__":
    main()

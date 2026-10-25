"""Independent compact INCOMPLETE IBP capsule audit; saved Python data only."""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
import time

sys.dont_write_bytecode = True
ROOT = Path.cwd().resolve()
HERE = Path(__file__).resolve().parent
CAPSULE = ROOT / "validation/public-rank7-ibp-owned-artifact-n1-n3"
EXPECTED = "66a60ca1a5a2c1cd1216c57885fe81250df5dc8b9e006094e40f486655294575"
PV_EXPECTED = "735a1004f379f31ec6d39916e4f4d805f845434a02a87cd016a2fbce43d8ef83"
PRIVATE = "target/public-rank7-n1-n3-ibp-owned-cargo"
COUNT = 0
STARTED = time.monotonic()


def ck(value, label):
    global COUNT
    COUNT += 1
    if not value:
        raise AssertionError(label)


def h(body):
    return hashlib.sha256(body).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return h(Path(path).read_bytes())


def desc(body):
    return {"sha256": h(body), "bytes": len(body)}


def safe(name):
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and str(path) == name


def replay(root, label):
    ck(time.monotonic() - STARTED < 145, "bounded review work")
    command = [sys.executable, "-I", "-S", "-B",
               "validation/public-rank7-ibp-owned-artifact-n1-n3/check.py"]
    before = time.monotonic()
    completed = subprocess.run(command, cwd=root,
                               env={"LC_ALL":"C", "PYTHONNOUSERSITE":"1"},
                               capture_output=True, timeout=60, check=False)
    (HERE / (label + ".stdout")).write_bytes(completed.stdout)
    (HERE / (label + ".stderr")).write_bytes(completed.stderr)
    ck(completed.returncode == 0 and not completed.stderr, "clean stdlib replay " + label)
    return {"command": command, "cwd":str(root), "timeout_seconds":60,
            "diagnostic_elapsed_seconds":time.monotonic()-before,
            "returncode":completed.returncode,
            "stdout_sha256":h(completed.stdout), "stderr_sha256":h(completed.stderr),
            "result":json.loads(completed.stdout)}


def main():
    ck(ROOT == Path("/shared/external/iregi/iregi-rust"), "project-root cwd")
    ck(not (HERE / "review.json").exists(), "fresh independent review")
    ck(sha(CAPSULE / "manifest.json") == EXPECTED, "frozen incomplete capsule identity")
    m = load(CAPSULE / "manifest.json")
    ck({str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob("*") if p.is_file()}
       == set(m["capsule_files"]) | {"manifest.json"}, "closed five-file capsule")
    for name, expected in m["capsule_files"].items():
        ck(safe(name) and desc((CAPSULE / name).read_bytes()) == expected, "capsule file " + name)
    ck(not (CAPSULE / "sources.tar.gz").exists(), "source archive inherited without duplication")
    parent = ROOT / m["parent"]["path"]
    ck(sha(parent / "manifest.json") == m["parent"]["manifest"]["sha256"] == PV_EXPECTED
       and desc((parent / "check.py").read_bytes()) == m["parent"]["checker"],
       "exact already reviewed PV parent/checker")
    pm = load(parent / "manifest.json")
    ck(sha(parent / "sources.tar.gz") == "c3ce5657ffaf0298d5962aa270a2f8b287cdb28dda0eab412096b984db164436",
       "unchanged inherited64-source archive")
    inventory = load(parent / "source-inventory.json")
    ck(inventory["source_count"] == len(inventory["members"]) == 64, "inherited64-source inventory")
    payload = {}
    with tarfile.open(fileobj=io.BytesIO((CAPSULE / "evidence.tar.gz").read_bytes()), mode="r:gz") as archive:
        for entry in archive:
            ck(safe(entry.name) and entry.isfile() and entry.name not in payload,
               "safe unique regular evidence member " + entry.name)
            body = archive.extractfile(entry).read()
            ck(not body.startswith((b"\x7fELF", b"!<arch>", b"MZ", b"\0asm"))
               and Path(entry.name).suffix not in {
                   ".o", ".a", ".mod", ".smod", ".pyc", ".rlib", ".rmeta",
                   ".so", ".dll", ".dylib", ".exe", ".wasm"}, "no native/cache product " + entry.name)
            ck(not re.search(rb"S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}", body),
               "no literal Symbolica license " + entry.name)
            ck((ROOT / entry.name).read_bytes() == body, "exact original-to-capsule copy " + entry.name)
            payload[entry.name] = body
    ck({name:desc(body) for name,body in payload.items()} == m["evidence_members"]
       and len(payload) == 36, "exact36-file evidence inventory")
    p = json.loads(payload[PRIVATE + "/protocol.json"])
    ck(len(p["bindings"]) == 86 and len(p["source_names"]) == 64,
       "preserved86-binding immutable64-source context")
    ck(not any("/shared/external/iregi/iregi-rust/" + name in p["bindings"] for name in p["source_names"]),
       "no live-main source lease introduced")
    ck(p["binary_sha256"] == "8166f6e799b241c7e09550a6e970d5e89d2386a2bda3930d97794b4560ec1f93"
       and p["source_context_sha256"] == "dc7a6297954ede6b71c668a6ff0e71d55a1b7b3e70ab9b41d1c8f1a44b41d763"
       and p["lifecycle_sha256"] == "c193cd7282d63b63a8f627612df684242a2a8941d1d0a35588514d0415ab8824",
       "old owned artifact/snapshot/helper context remains exact")
    expected_omissions = {PRIVATE + "/captures/" + c["id"] + "/highpoint_public-frozen" for c in p["cases"]}
    ck(set(m["omitted_native_products"]) == expected_omissions
       and len(expected_omissions) == 6
       and all(row["sha256"] == p["binary_sha256"] for row in m["omitted_native_products"].values()),
       "exact six owned native omissions")
    q = load(CAPSULE / "qualification.json")
    ck(m["full_requested_IBP_corpus_qualified"] is False
       and q["full_requested_IBP_corpus_qualified"] is False
       and m["portable_fresh_native_or_process_probe_claim"] is False
       and m["native_products_included"] is False and m["symbolica_license_literal_included"] is False,
       "integrity success cannot qualify incomplete corpus")
    ck(q["complete_success_cases"] == 4 and q["failed_N2_cases"] == 2
       and q["historical_N2_cleanup_failures"] == 2
       and q["later_absence_repairs_historical_cleanup_or_proves_no_overlap"] is False,
       "qualification preserves failed history")
    for bits, expected in {
        128:"b9f8e4ff957abafef1850134e1fbc978ea2761d436312ca87d0630e88e5c6003",
        256:"55ec80b2652ce5dac8c1d33f3b269a5046566993aa012e588883a3dbfc358ab3"
    }.items():
        prefix = PRIVATE + f"/captures/n2-rank7-Float{bits}-001"
        ck(h(payload[prefix + "/receipt.json"]) == expected, "exact failed N2 receipt " + str(bits))
        receipt = json.loads(payload[prefix + "/receipt.json"])
        partial = json.loads(payload[prefix + "/result.json"])
        ck(receipt["status"] == "failed_or_incomplete" and receipt["steps"][0]["owned_group_gone"] is False
           and receipt["steps"][0]["returncode"] is None and len(receipt["cleanup_errors"]) == 2
           and partial["status"] == "preparing_workspace" and "lanes" not in partial,
           "timeout/cleanup failures and missing arrays remain intact " + str(bits))
    ck(h(payload[PRIVATE + "/independent-review/terminal-review.json"])
       == "749a34697fbdaf0fb5fc856306741cf77fc25eabc435e98ee1b3a3cdf9e6de39"
       and h(payload[PRIVATE + "/independent-review/numeric-review.json"])
       == "5ef1d1f5c5438bb763abf3b26f9d1bb1b9e5a12ea636be728120598b4cd6eadb",
       "exact independent lifecycle and numerical audit retention")
    checker_paths = [CAPSULE / "check.py", parent / "check.py"] + [ROOT / "validation" / name / "check.py" for name in [
        "quad-original-iregi-small-n-rank7", "quad-original-iregi-positive-rank-anchors",
        "quad-original-iregi-rank7-adjudication"]]
    imports = set()
    for path in checker_paths:
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                ck(node.func.id not in {"exec", "eval", "compile", "__import__"},
                   "no dynamic execution builtin " + str(path.relative_to(ROOT)))
    ck(imports <= set(sys.stdlib_module_names)
       and not imports.intersection({"os", "subprocess", "ctypes", "socket"}),
       "five checker modules have process-free stdlib-only imports")
    # Assemble only the declarative validation closure: no targets, source tree,
    # Cargo/Git caches, native files, or license environment in the fresh root.
    needed = set()
    for directory, manifest in [(CAPSULE,m), (parent,pm)]:
        needed.update(str((directory / name).relative_to(ROOT)) for name in manifest["capsule_files"])
        needed.add(str((directory / "manifest.json").relative_to(ROOT)))
    reference = ROOT / pm["reference_parent"]["path"]
    rm = load(reference / "manifest.json")
    needed.update(str((reference / name).relative_to(ROOT)) for name in rm["capsule_files"])
    needed.add(str((reference / "manifest.json").relative_to(ROOT)))
    needed.update(rm["parent_files"])
    needed.update(pm["direct_parent_files"])
    minimal = HERE / "minimal-validation-only-root"
    ck(not minimal.exists(), "fresh minimal validation-only root")
    for name in sorted(needed):
        ck(safe(name) and name.startswith("validation/"), "minimal declared validation file " + name)
        path = minimal / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / name).read_bytes())
    ck(len(needed) == 49 and {str(p.relative_to(minimal)) for p in minimal.rglob("*") if p.is_file()} == needed,
       "exact49-file minimal validation closure")
    default = replay(ROOT, "default")
    fresh = replay(minimal, "minimal")
    ck(default["result"] == fresh["result"], "identical default/fresh minimal replay")
    result = default["result"]
    ck(result["capsule_manifest_sha256"] == EXPECTED and result["restored_files"] == 679,
       "correct incomplete capsule and679 restored aliases")
    evidence = result["replay"]
    ck(evidence["full_requested_IBP_corpus_qualified"] is False
       and evidence["counts"] == {
           "complete_cases":4,"failed_cases":2,"successful_lanes":12,"reference_slots":15840,
           "precision_slots":7920,"scaling_slots":5280,"mode_pair_slots":15840,
           "IR_exact_zero_slots":7920,"UV_convergent_exact_zero_slots":30},
       "all available values replay while corpus remains incomplete")
    ck(evidence["historical_N2_cleanup_failures_preserved"] is True
       and evidence["later_absence_does_not_prove_historical_cleanup_or_no_overlap"] is True
       and evidence["new_native_or_process_probe"] is False
       and evidence["later_main_source_or_full_rank7_domain_or_performance_qualified"] is False,
       "portable historical failure/scope truth retained")
    ck(sha(CAPSULE / "manifest.json") == EXPECTED and sha(parent / "manifest.json") == PV_EXPECTED,
       "sealed own and parent manifests unchanged")
    for name, expected in m["capsule_files"].items():
        ck(desc((CAPSULE / name).read_bytes()) == expected, "final capsule bytes " + name)
    review = {"schema":"iregi-rust-independent-incomplete-ibp-capsule-review-v1",
              "status":"passed_saved_copy_integrity_and_replay_of_INCOMPLETE_corpus",
              "reviewer":"/root/highpoint_generalized_research/routing_source_review",
              "manifest_sha256":EXPECTED,"parent_PV_manifest_sha256":PV_EXPECTED,
              "audit_script_sha256":sha(__file__),"checks_passed":COUNT,
              "exact_own_evidence_origin_copies":36,"inherited_source_files":64,
              "source_archive_duplicated":False,"historical_native_copies_omitted":6,
              "minimal_validation_only_file_count":49,"default_replay":default,"minimal_replay":fresh,
              "full_requested_IBP_corpus_qualified":False,
              "historical_cleanup_failure_count":2,"later_absence_repairs_history_or_proves_no_overlap":False,
              "new_native_compiler_integral_algebra_or_PID_probe":False,
              "sealed_capsule_source_or_receipt_mutation":False,
              "current_live_main_guard_or_qualification":False,"performance_qualified":False,
              "scope":"Saved portable integrity succeeds while the six-case IBP request remains incomplete. Four N1/N3 successful captures pass available gates; both original N2 workspace timeouts and FAILED historical cleanup remain preserved exactly. No native execution, no process probe, no success inferred from report-only helper exit0."}
    (HERE / "review.json").write_text(json.dumps(review,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":review["status"],"checks":COUNT,
                      "review_sha256":sha(HERE / "review.json"),"audit_script_sha256":sha(__file__),
                      "full_requested_IBP_corpus_qualified":False}))


if __name__ == "__main__":
    main()

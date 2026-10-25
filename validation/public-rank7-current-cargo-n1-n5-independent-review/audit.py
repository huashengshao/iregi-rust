"""Independent saved-only copy/source and portable capsule review.

Only Python stdlib checkers are launched. No compiler, producer, integral,
native executable, process probe, or algebra runtime is imported or invoked.
"""
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
CAPSULE = ROOT / "validation/public-rank7-current-cargo-n1-n5"
EXPECTED = "735a1004f379f31ec6d39916e4f4d805f845434a02a87cd016a2fbce43d8ef83"
SOURCE_ARCHIVE = "c3ce5657ffaf0298d5962aa270a2f8b287cdb28dda0eab412096b984db164436"
PRIVATE = "target/public-rank7-n1-n5-current-cargo"
OWNER = "target/routing-rational-cayley-adoption/current-cargo-qualification"
STARTED = time.monotonic()
CHECKS = []


def check(value, label):
    if not value:
        raise AssertionError(label)
    CHECKS.append(label)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def sha(path):
    return digest(Path(path).read_bytes())


def load(path):
    return json.loads(Path(path).read_text())


def describe(body):
    return {"sha256": digest(body), "bytes": len(body)}


def safe(name):
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and str(path) == name


def archive(path, expected):
    result = {}
    with tarfile.open(fileobj=io.BytesIO(Path(path).read_bytes()), mode="r:gz") as stream:
        for entry in stream:
            check(safe(entry.name) and entry.isfile() and entry.name not in result,
                  "safe unique regular archive member " + entry.name)
            body = stream.extractfile(entry).read()
            check(not body.startswith((b"\x7fELF", b"!<arch>", b"MZ", b"\0asm")),
                  "no native/archive/wasm product " + entry.name)
            check(Path(entry.name).suffix not in {
                ".o", ".a", ".mod", ".smod", ".pyc", ".rlib", ".rmeta",
                ".so", ".dll", ".dylib", ".exe", ".wasm"
            }, "no compiled/cache suffix " + entry.name)
            check(not re.search(rb"S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}", body),
                  "no literal Symbolica license " + entry.name)
            result[entry.name] = body
    check({name: describe(body) for name, body in result.items()} == expected,
          "exact archive member identity " + str(path.relative_to(ROOT)))
    return result


def run_checker(root, label):
    check(time.monotonic() - STARTED < 145, "remaining bounded saved-only review work")
    command = [sys.executable, "-I", "-S", "-B",
               "validation/public-rank7-current-cargo-n1-n5/check.py"]
    before = time.monotonic()
    completed = subprocess.run(command, cwd=root,
                               env={"LC_ALL": "C", "PYTHONNOUSERSITE": "1"},
                               capture_output=True, timeout=60, check=False)
    (HERE / (label + ".stdout")).write_bytes(completed.stdout)
    (HERE / (label + ".stderr")).write_bytes(completed.stderr)
    check(completed.returncode == 0 and not completed.stderr,
          "isolated stdlib checker exited cleanly " + label)
    return {"command": command, "cwd": str(root), "returncode": completed.returncode,
            "timeout_seconds": 60, "diagnostic_elapsed_seconds": time.monotonic() - before,
            "stdout_sha256": digest(completed.stdout), "stderr_sha256": digest(completed.stderr),
            "result": json.loads(completed.stdout)}


def main():
    check(ROOT == Path("/shared/external/iregi/iregi-rust"), "project-root cwd")
    check(not (HERE / "review.json").exists(), "preserve existing review")
    check(sha(CAPSULE / "manifest.json") == EXPECTED, "exact frozen capsule manifest")
    manifest = load(CAPSULE / "manifest.json")
    check({str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob("*") if p.is_file()}
          == set(manifest["capsule_files"]) | {"manifest.json"}, "closed seven-file capsule")
    for name, expected in manifest["capsule_files"].items():
        check(safe(name) and describe((CAPSULE / name).read_bytes()) == expected,
              "capsule payload " + name)
    evidence = archive(CAPSULE / "evidence.tar.gz", manifest["evidence_members"])
    check(len(evidence) == len(manifest["preserved_files"]) == 62, "62 evidence members/aliases")
    for origin, record in manifest["preserved_files"].items():
        check(safe(origin) and record["member"] in evidence, "safe preserved origin " + origin)
        body = evidence[record["member"]]
        check(describe(body) == {k: record[k] for k in ["sha256", "bytes"]},
              "preserved alias metadata " + origin)
        check((ROOT / origin).read_bytes() == body, "exact source-to-capsule copy " + origin)
    inventory = load(CAPSULE / "source-inventory.json")
    check(sha(CAPSULE / "sources.tar.gz") == inventory["archive_sha256"] == SOURCE_ARCHIVE,
          "exact source archive identity")
    sources = archive(CAPSULE / "sources.tar.gz", inventory["members"])
    check(len(sources) == inventory["source_count"] == manifest["source_archive_files"] == 64,
          "64 source members")
    context = json.loads(evidence[OWNER + "/source-context.json"])
    check(digest(evidence[OWNER + "/source-context.json"]) == inventory["source_context_sha256"],
          "source context identity")
    check({name: digest(body) for name, body in sources.items()} == context["source_files"],
          "all64 archived sources bound to actual Cargo context")
    snapshot = ROOT / OWNER / "source-snapshot"
    check({str(p.relative_to(snapshot)) for p in snapshot.rglob("*") if p.is_file()} == set(sources),
          "closed actual Cargo owner snapshot")
    for name, body in sources.items():
        check((snapshot / name).read_bytes() == body, "exact source archive/snapshot copy " + name)
    check(manifest["native_products_included"] is False
          and manifest["symbolica_license_literal_included"] is False
          and manifest["portable_fresh_native_hash_or_process_probe_claim"] is False
          and manifest["full_rank7_domain_or_performance_qualified"] is False,
          "capsule scope boundaries")
    omissions = manifest["omitted_native_products"]
    check(len(omissions) == 11
          and all(row["sha256"] == "8166f6e799b241c7e09550a6e970d5e89d2386a2bda3930d97794b4560ec1f93"
                  for row in omissions.values()), "eleven explicitly historical native omissions")
    for suffix in ["independent-saved-terminal-metadata-review.json",
                   "independent-saved-terminal-metadata-method.md",
                   "independent-saved-terminal-metadata-attempt-chronology.json",
                   "independent-saved-terminal-metadata-companion-provenance.json"]:
        check(PRIVATE + "/" + suffix in evidence, "inline metadata audit provenance retained " + suffix)
    companion = json.loads(evidence[PRIVATE + "/independent-saved-terminal-metadata-companion-provenance.json"])
    check(companion["exact_executed_program_retained"] is False
          and companion["standalone_audit_replay_script_provided"] is False,
          "honest inline-audit source retention limitation")
    # Review only these four hash-bound stdlib checker sources, not archived producers.
    checker_paths = [CAPSULE / "check.py"] + [ROOT / "validation" / name / "check.py" for name in [
        "quad-original-iregi-small-n-rank7", "quad-original-iregi-positive-rank-anchors",
        "quad-original-iregi-rank7-adjudication"]]
    imports = set()
    for path in checker_paths:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                check(node.func.id not in {"eval", "exec", "compile", "__import__"},
                      "no dynamic execution builtin " + str(path.relative_to(ROOT)))
    check(imports <= set(sys.stdlib_module_names)
          and not imports.intersection({"os", "subprocess", "ctypes", "socket"}),
          "four checker modules use only reviewed process-free stdlib imports")
    # The parent graph's declared files suffice for a validation-only fresh root.
    parent = manifest["reference_parent"]
    parent_dir = ROOT / parent["path"]
    check(describe((parent_dir / "manifest.json").read_bytes()) == parent["manifest"]
          and describe((parent_dir / "check.py").read_bytes()) == parent["checker"],
          "exact reference-parent manifest and checker")
    pm = load(parent_dir / "manifest.json")
    copied = {str((CAPSULE / name).relative_to(ROOT)) for name in manifest["capsule_files"]}
    copied.add(str((CAPSULE / "manifest.json").relative_to(ROOT)))
    copied.update(str((parent_dir / name).relative_to(ROOT)) for name in pm["capsule_files"])
    copied.add(str((parent_dir / "manifest.json").relative_to(ROOT)))
    copied.update(pm["parent_files"])
    copied.update(manifest["direct_parent_files"])
    minimal = HERE / "minimal-validation-only-root"
    check(not minimal.exists(), "fresh minimal root")
    for name in sorted(copied):
        check(safe(name) and name.startswith("validation/"), "minimal validation-only path " + name)
        destination = minimal / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / name).read_bytes())
    check(len(copied) == 44 and {str(p.relative_to(minimal)) for p in minimal.rglob("*") if p.is_file()} == copied,
          "exact minimal44-file validation closure")
    default = run_checker(ROOT, "default")
    fresh = run_checker(minimal, "minimal")
    check(default["result"] == fresh["result"], "identical default/minimal stdlib replay")
    replay = default["result"]
    check(replay["capsule_manifest_sha256"] == EXPECTED and replay["restored_files"] == 642,
          "portable manifest identity and642 restored aliases")
    check(replay["replay"]["status"] == "passed_complete_saved_numeric_and_source_replay"
          and replay["replay"]["counts"] == {
              "reference_slots": 39600, "precision_slots": 19800, "scaling_slots": 13200,
              "IR_slots": 19800, "UV_convergent_slots": 996, "exact_input_complex_arguments": 480,
              "stored_precision_fields": 79200, "owned_groups_historically_absent": 10},
          "complete portable numeric/metadata replay counts")
    check(replay["replay"]["new_native_execution"] is False
          and replay["replay"]["new_process_probe"] is False
          and replay["replay"]["full_rank7_domain_or_performance_qualified"] is False,
          "portable replay scope")
    check(sha(CAPSULE / "manifest.json") == EXPECTED, "sealed manifest unchanged after replay")
    for name, expected in manifest["capsule_files"].items():
        check(describe((CAPSULE / name).read_bytes()) == expected, "final capsule payload " + name)
    result = {"schema": "iregi-rust-independent-rank7-capsule-copy-portability-review-v1",
              "status": "passed_saved_copy_source_inventory_and_portable_replay",
              "reviewer": "/root/highpoint_generalized_research/routing_source_review",
              "manifest_sha256": EXPECTED, "audit_script_sha256": sha(__file__),
              "checks_passed": len(CHECKS), "evidence_origins_compared": 62,
              "archived_sources_compared_to_exact_snapshot": 64,
              "source_archive_sha256": SOURCE_ARCHIVE,
              "parent_manifest_sha256": parent["manifest"]["sha256"],
              "minimal_validation_only_files": len(copied),
              "minimal_root_has_git_cargo_sources_native_caches_or_license": False,
              "default_replay": default, "fresh_minimal_replay": fresh,
              "new_compiler_native_integral_or_process_probe": False,
              "capsule_or_producer_source_modified": False,
              "scope": "Restricted existing actual-Cargo PV N1-N5 rank0-through7 moments, three positive-mass rows, Float128/256 requested53. Saved data only; historical native/group identities are not fresh portable attestations. No full-rank7 or performance qualification.",
              "limits": ["The earlier terminal metadata audit used inline programs without retained exact replay source; its method/chronology companions preserve that limitation.",
                         "This audit does retain its own source before execution. Original reference-parent copy review is separately owned; its exact manifest/checker and declared closure are bound and replayed here."]}
    (HERE / "review.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": result["status"], "checks_passed": len(CHECKS),
                      "review_sha256": sha(HERE / "review.json"),
                      "audit_script_sha256": sha(__file__), "minimal_files": len(copied)}))


if __name__ == "__main__":
    main()

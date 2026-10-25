"""Saved-only sealed capsule copy/origin/portable-replay audit.

Retained before execution. Does not run any compiler, integral, original
reference, live-source equality check or process-group probe. The portable
checker's frozen comparator executes only over saved in-memory data.
"""
from collections import Counter
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile


ROOT = Path.cwd().resolve()
HERE = ROOT / "target/routing-rational-cayley-adoption/n6-rank4-7-current"
CAPSULE = ROOT / "validation/highpoint-six-point-literal-ranks4-7-current-cargo"
CHECKS = Counter()


def require(ok, why):
    CHECKS[why] += 1
    if not ok:
        raise AssertionError(why)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def archive(raw):
    result = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as stream:
        for member in stream.getmembers():
            name = PurePosixPath(member.name)
            require(member.isfile() and not member.issym() and not member.islnk()
                    and not name.is_absolute() and ".." not in name.parts
                    and member.name not in result, "safe unique regular archived file")
            result[member.name] = stream.extractfile(member).read()
    return result


def main():
    expected = {
        "manifest.json":"e3bc670c4609c4a27303689e030c1f9cde3f4646cd29e49fcfe9a04fa919d30c",
        "evidence.tar.gz":"363078bed6ac40535768316e2751cdafe9401c5d287cfb8ecc1b0e837d6d8468",
        "qualification.json":"c7dfd0d52365585609d5c93d09a33b44390bea5a31fec43de07c33ceb16d20e2",
    }
    for name, wanted in expected.items():
        require(digest((CAPSULE/name).read_bytes()) == wanted, "sealed capsule identity")
    manifest = read(CAPSULE/"manifest.json")
    before = {p.name:digest(p.read_bytes()) for p in CAPSULE.iterdir() if p.is_file()}
    for name, wanted in manifest["capsule_files"].items():
        require(digest((CAPSULE/name).read_bytes()) == wanted, "capsule-file map")
    payload = archive((CAPSULE/"evidence.tar.gz").read_bytes())
    require(len(payload) == 68 and set(payload) == set(manifest["payload_members"]), "closed68payload inventory")
    origin_paths = {}
    for name, metadata in manifest["payload_members"].items():
        raw = payload[name]
        require(len(raw) == metadata["bytes"] and digest(raw) == metadata["sha256"], "payload size and digest")
        # Only one project source file is in this payload. Its authoritative
        # origin is the immutable captured snapshot, never current live main.
        origin = HERE/"source-snapshot"/name if name in manifest["source_files"] else ROOT/name
        require(origin.read_bytes() == raw, "all68authoritative original copies")
        origin_paths[name] = str(origin.relative_to(ROOT))
    data = dict(payload)
    for name, record in manifest["external_files"].items():
        raw = (ROOT/record["path"]).read_bytes()
        require(digest(raw) == record["sha256"] and name not in data, "durable parent identity")
        data[name] = raw
    parent = archive(data[manifest["source_parent_archive"]])
    inventory = json.loads(data[manifest["source_parent_inventory"]])
    require(set(parent) == set(inventory["members"]) and len(parent) == 64, "exact64source parent")
    for name, metadata in inventory["members"].items():
        require(digest(parent[name]) == metadata["sha256"] and len(parent[name]) == metadata["bytes"],
                "parent source byte identity")
    example = "crates/iregi-rust/examples/six_point.rs"
    require(set(manifest["source_files"]) == set(parent) | {example} and example not in parent,
            "source65is64plusliteralexample")
    for name, wanted in manifest["source_files"].items():
        raw = payload[name] if name in payload else parent[name]
        require(digest(raw) == wanted, "all65captured source hashes")
        data[name] = raw
        for prefix, names in manifest["snapshot_aliases"].items():
            if name in names:
                data[prefix+name] = raw
    literal_context = json.loads(data[str(HERE.relative_to(ROOT))+"/source-context.json"])
    old_context_key = "target/routing-rational-cayley-adoption/current-cargo-qualification/source-context.json"
    old_context = json.loads(data[old_context_key])
    require(literal_context["source_files"] == manifest["source_files"], "literal65context source map")
    require(old_context["source_files"] == {name:meta["sha256"] for name,meta in inventory["members"].items()},
            "actualprior64Cargo context source map")
    require(digest(data[old_context_key]) == literal_context["actualpriorCargo64source_context_sha256"],
            "literalcontext binds actualprior64Cargo")
    original_root = manifest["original_root"]

    def canonical(path):
        return path[len(original_root)+1:] if path.startswith(original_root+"/") else path

    guards = omitted = 0
    omissions = manifest["omitted_compiled_binaries"]
    for name in manifest["receipts"]:
        record = json.loads(data[name])
        require(record["status"] == "passed" and record["inputs_unchanged"] is True
                and record["cleanup_errors"] == [] and record.get("cancellation") is None,
                "preserved passed terminal record")
        saved = record.get("saved_files", {})
        for name in set(record["inputs"]) & set(saved):
            require(record["inputs"][name] == saved[name], "overlapping guard identities")
        for path, wanted in {**record["inputs"], **saved}.items():
            key = canonical(path)
            if key in omissions:
                require(omissions[key] == wanted, "explicit omitted ELF guard identity")
                omitted += 1
            else:
                require(key in data and digest(data[key]) == wanted, "independent saved guard reconstruction")
                guards += 1
    require(guards == 1749 and omitted == 28 and len(omissions) == 10, "guard and omittedELF counts")
    for name in manifest["independent_reviews"]:
        require(str(json.loads(data[name])["status"]).startswith("passed"), "preserved independent audit")
    test_record = json.loads(data[manifest["ibp_test_receipt"]])
    test_log = data[str(PurePosixPath(manifest["ibp_test_receipt"]).parent/"step.log")].decode()
    passed = [line.split(" ... ")[0][5:] for line in test_log.splitlines()
              if line.startswith("test ibp::") and line.endswith(" ... ok")]
    require(test_record["all_51_ibp_tests_passed"] is True and len(passed) == len(set(passed)) == 51
            and passed == test_record["test_names"]
            and "test result: ok. 51 passed; 0 failed; 0 ignored;" in test_log,
            "actual51IBP named tests and strict log")
    failure_key = str(HERE.relative_to(ROOT))+"/pack-v1-failure.json"
    failure = json.loads(data[failure_key])
    old_pack_key = str(HERE.relative_to(ROOT))+"/pack-v1.py"
    require(failure["status"] == "failed-before-seal" and failure["stage"] == "capsulepackagingonly"
            and failure["native_integrals_rerun"] == failure["compiler_rerun"] == 0
            and failure["source_sha256"] == digest(data[old_pack_key])
            and "no manifest existed" in failure["error"], "preserved packaging-only initial failures")
    qualification = read(CAPSULE/"qualification.json")
    require(qualification["later_typed_Dual_reset_edit_included"] is False
            and qualification["actual_IBP_unit_tests_passed"] == 51
            and qualification["full_port_complete"] is False
            and qualification["performance_qualified"] is False, "qualification scope preserved")
    command = [sys.executable, str(CAPSULE/"check.py")]
    normal = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
    require(normal.returncode == 0 and normal.stderr == "", "default saved-only replay exit")
    normal_report = json.loads(normal.stdout)
    require(normal_report == {"status":"passed", "source_files":65, "payload_members":68,
            "replayed_guard_occurrences":1749, "omitted_compiled_binary_guard_occurrences":28,
            "ibp_tests":51, "counts":qualification["counts"], "new_integrals":0, "new_compilers":0,
            "current_host_process_absence_claim":False}, "default replay exact report")
    minimal_files = {}
    with tempfile.TemporaryDirectory(prefix="capsule-validation-only-", dir=HERE) as scratch:
        scratch = Path(scratch)
        for path in CAPSULE.iterdir():
            if path.is_file():
                target = scratch/path.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path,target)
                minimal_files[str(target.relative_to(scratch))] = digest(target.read_bytes())
        for record in manifest["external_files"].values():
            source = ROOT/record["path"]
            target = scratch/record["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source,target)
            minimal_files[str(target.relative_to(scratch))] = digest(target.read_bytes())
        require(all(name.startswith("validation/") for name in minimal_files)
                and len(minimal_files) == len(before)+len(manifest["external_files"]),
                "minimal validation-only root membership")
        minimal = subprocess.run([sys.executable,str(scratch/CAPSULE.relative_to(ROOT)/"check.py")],
                                 cwd=scratch,capture_output=True,text=True,timeout=60)
        require(minimal.returncode == 0 and minimal.stderr == "" and json.loads(minimal.stdout) == normal_report,
                "minimal validation-only replay identical")
    require({p.name:digest(p.read_bytes()) for p in CAPSULE.iterdir() if p.is_file()} == before,
            "sealed capsule unchanged")
    result = dict(schema_version=1,status="passed-independent-capsule-origin-copy-replay-review",
        reviewer="/root/highpoint_generalized_research/cayley_source_reuse",
        created_utc=datetime.now(timezone.utc).isoformat(),audit_source_sha256=digest(Path(__file__).read_bytes()),
        capsule_manifest_sha256=expected["manifest.json"],evidence_sha256=expected["evidence.tar.gz"],
        qualification_sha256=expected["qualification.json"],checks_total=sum(CHECKS.values()),
        checks_by_category=dict(CHECKS),authoritative_payload_origins=origin_paths,
        exact_sources=65,payload_original_copies=68,parent_sources=64,
        independent_reconstructed_guard_occurrences=guards,explicit_omitted_ELF_guard_occurrences=omitted,
        default_replay=normal_report,minimal_validation_only_replay=normal_report,
        minimal_root_files=minimal_files,packaging_failure_preserved=failure,
        checker_source_review="Safe regular unique tar members; closed archives anddeclared externalparents; reconstructed immutable source aliases; hashes of every non-ELF receipt guard; in-memory SavedPath/SavedTar confines frozen saved comparator input/output. No Rust,native reference,Symbolica evaluator,currentlive source equality orPGprobe is invoked.",
        independent_math_review_retained="5891fc97b86b77d19f3d75073bf9c67262c7c380da2a9a9ced415c1edac81ca7; portable producer-comparator replay is not a new independent mathematical audit.",
        findings=[],limitations=["Authoritative literalexample origin is captured immutable snapshot,not current main.",
            "Packaging-only firststatusassertion andsubsequent missingmanifest checkerfailure are preserved; these are not capture/reduction failures.",
            "Historical compiledELF/tool/native/dependency provenance andhistorical ownedcleanup remain recorded,not reconstructedbythisportable replay.",
            "No currentlive source match,PGabsence,nativejob,performance,Dual orbroaderdomain claim."],
        conclusion="PASS compact capsule byte-copy/source origin,actual51IBP history,all1749saved guardoccurrences/28explicitELF omissions,andidentical default+minimalvalidationonly saved replay. Sealedfiles remain unchanged.")
    output = HERE/"capsule-independent-review.json"
    output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"checks":result["checks_total"],
                      "review_sha256":digest(output.read_bytes()),"default_and_minimal_replay":"passed"}))


if __name__ == "__main__":
    main()

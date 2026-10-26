"""Replay saved source/artifact/test bindings using the standard library only."""
from pathlib import Path
import hashlib
import io
import json
import tarfile

HERE = Path(__file__).resolve().parent


def digest(body):
    return hashlib.sha256(body).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def archive(path, expected_members=None):
    bodies = {}
    with tarfile.open(fileobj=io.BytesIO(path.read_bytes()), mode="r:gz") as stream:
        members = stream.getmembers()
        require(len(members) == len({m.name for m in members}), "no duplicate archive members")
        require(all(m.isfile() and m.name.startswith("objects/") and len(m.name) == 72 for m in members), "plain digest objects only")
        if expected_members is not None:
            require({m.name for m in members} == set(expected_members), "closed own archive inventory")
        for member in members:
            body = stream.extractfile(member).read()
            require(digest(body) == member.name[8:], "content-addressed object: " + member.name)
            if expected_members is not None:
                spec = expected_members[member.name]
                require(len(body) == spec["bytes"] and digest(body) == spec["sha256"], "own archive member metadata")
            bodies[member.name] = body
    return bodies


def restore(manifest):
    own = archive(HERE / "payload.tar.gz", manifest["payload_members"])
    parents = {}
    for name, spec in manifest["parent_files"].items():
        path = HERE.parent / name
        body = path.read_bytes()
        require(len(body) == spec["bytes"] and digest(body) == spec["sha256"], "direct parent file: " + name)
    for name in manifest["borrowed_members"]:
        parent = HERE.parent / name
        parent_manifest = json.loads((parent / "manifest.json").read_text())
        bodies = archive(parent / "payload.tar.gz")
        for member, spec in manifest["borrowed_members"][name].items():
            require(member in parent_manifest["payload_members"], "member declared by direct source parent")
            require(parent_manifest["payload_members"][member] == spec, "parent member metadata")
            require(len(bodies[member]) == spec["bytes"] and digest(bodies[member]) == spec["sha256"], "borrowed exact source object")
        parents[name] = bodies
    restored = {}
    for alias, spec in manifest["preserved_files"].items():
        body = own[spec["member"]] if spec["owner"] == "self" else parents[spec["owner"]][spec["member"]]
        require(len(body) == spec["bytes"] and digest(body) == spec["sha256"], "saved alias: " + alias)
        require(not body.startswith((b"\x7fELF", b"!<arch>\n")), "no native product payload")
        require(b"S-130-2027.08.31-" not in body, "no license literal")
        restored[alias] = body
    return restored


def replay(files):
    read = lambda name: json.loads(files[name])
    build = read("evidence/build-receipt.json")
    frozen = read("evidence/freeze-receipt.json")
    event = read("evidence/cargo-core-artifact.json")
    selection = read("evidence/test-selection.json")
    actual = read("evidence/normal-receipt.json")
    require(build["status"] == "passed" and build["inputs_unchanged"] and not build["cleanup_errors"], "actual coherent build outcome")
    require(frozen["status"] == "passed_actual_Cargo_core_artifact_frozen_no_execution" and frozen["inputs_unchanged"], "owned artifact freeze")
    require(digest(files["evidence/build-receipt.json"]) == frozen["source_build_receipt_sha256"] == actual["actual_source_context_receipt_sha256"], "same actual build context")
    require(digest(files["evidence/cargo-core-artifact.json"]) == frozen["actual_cargo_artifact_event_sha256"], "actual Cargo artifact event binding")
    require(digest(files["evidence/build-cargo.log"]) == frozen["source_log_sha256"], "actual Cargo output binding")
    events = []
    for line in files["evidence/build-cargo.log"].decode().splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("reason") == "compiler-artifact" and item.get("executable") and item.get("target", {}).get("name") == "iregi_rust" and item.get("target", {}).get("kind") == ["lib"] and item.get("profile", {}).get("test"):
            events.append(item)
    require(events == [event], "exact actual core Cargo event")
    require(event["executable"] == frozen["actual_cargo_executable"], "emitted executable path")
    require(event["fresh"] is True, "historical Cargo freshness preserved")
    require(frozen["actual_cargo_product_sha256"] == frozen["owned_product_sha256"] == actual["actual_product_sha256"], "actual frozen runtime product digest")
    require(build["source_files"] == frozen["source_files"] == actual["source_files"] and len(build["source_files"]) == 128, "same selected128 source context")
    for name, expected in build["source_files"].items():
        require(digest(files["source/" + name]) == expected, "actual selected source: " + name)
    names = selection["exact_tests"]
    require(len(names) == len(set(names)) == 22 and names == actual["selected_tests"] == actual["passed_tests"] and actual["unrun_tests"] == [], "same exact22 tests, no missing cases")
    require(actual["status"] == "passed" and actual["inputs_unchanged"] and not actual["cleanup_errors"] and not actual["cancellation"] and not actual["post_cancellation"], "actual cohort success and guards")
    require(actual["bounds"] == selection["bounds"] == {"total_seconds": 240, "cleanup_reserve_seconds": 30, "per_test_seconds": 60, "cpu": 22}, "approved finite execution bounds")
    require(0 < actual["elapsed_seconds"] <= 240 and len(actual["steps"]) == 23, "actual duration and stages")
    require(actual["strict_listing_passed"] and actual["Cargo_executed"] is False and actual["ignored_drivers_executed"] is False and actual["new_integral_qualification"] is False, "normal cohort scope retained")
    listed = [line.removesuffix(": test") for line in files["evidence/listing.log"].decode().splitlines() if line.endswith(": test")]
    require(all(listed.count(name) == 1 for name in names), "strict selected listing")
    for index, step in enumerate(actual["steps"]):
        require(step["status"] == "exited" and step["returncode"] == 0 and step["owned_group_gone"], "saved owned process outcome")
        command = step["command"]
        if index == 0:
            require(command[-3:] == ["--list", "--format", "terse"], "listing command")
            continue
        name = names[index - 1]
        body = files["evidence/test-" + str(index - 1) + ".log"].decode()
        require("test " + name + " ... ok" in body and "1 passed; 0 failed; 0 ignored;" in body, "strict one normal pass: " + name)
        require(command[-4:] == ["--exact", name, "--nocapture", "--test-threads=1"], "exact named command")
        require("--ignored" not in command and step["strict_exact_gate"] == "passed", "no ignored driver")
        require(digest(files["evidence/test-" + str(index - 1) + ".log"]) == actual["outputs"]["test-" + str(index - 1) + ".log"], "actual raw test output binding")
    for original, body in [(frozen["source_build_receipt"], files["evidence/build-receipt.json"]), (str(Path(frozen["test_selection"])), files["evidence/test-selection.json"])]:
        require(actual["inputs"][original] == digest(body), "runtime input receipt binding")
    return {
        "status": "passed_saved_current_core_exact22",
        "selected_source_bodies": 128,
        "passed_tests": 22,
        "failed_tests": 0,
        "ignored_tests": 0,
        "unrun_tests": 0,
        "elapsed_seconds": actual["elapsed_seconds"],
        "actual_build_receipt_sha256": digest(files["evidence/build-receipt.json"]),
        "actual_tests_receipt_sha256": digest(files["evidence/normal-receipt.json"]),
        "actual_product_sha256": actual["actual_product_sha256"],
        "Cargo_fresh_true_preserved": True,
        "source_and_artifact_guards_unchanged": True,
        "native_products_or_license_literals_included": False,
        "native_products_or_processes_freshly_probed_by_replay": False,
        "complete_dependency_build_closure_claimed": False,
        "new_integral_or_full_Dual_quadrature_qualification": False,
        "performance_qualified": False,
    }


def main():
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, spec in manifest["capsule_files"].items():
        body = (HERE / name).read_bytes()
        require(len(body) == spec["bytes"] and digest(body) == spec["sha256"], "capsule file: " + name)
    result = replay(restore(manifest))
    require(result == json.loads((HERE / "qualification.json").read_text()), "same saved qualification")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

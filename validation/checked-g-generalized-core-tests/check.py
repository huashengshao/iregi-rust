#!/usr/bin/env python3
"""Replay source identities and saved Cargo/libtest evidence using stdlib only.

This checker never loads a producer, native artifact, compiler, or evaluator.
"""
import argparse
import hashlib
import io
import json
from fractions import Fraction as F
from pathlib import Path
import re
import sys
import tarfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
Q = "target/checked-g-generalized-qualification"
CORE = "target/checked-g-generalized-composed"
FRONT = "target/checked-g-generalized-frontend-proposal"
PREFIX = "/shared/external/iregi/iregi-rust/"
QUAL = "1702c9f1dfb191871586de9cb248f75529bb4e10806aceb965f93ecdc4ab3f6f"
BUILD_PINS = {
    "build-001": "b8b9a289e8ec2240315e8f22311353184e5eff8b610e05678fb20f6bd85d2517",
    "build-002": "f7366af41461e7b7fb3f2f537d4c589e19d8b5b0b773d951e8ef67ba9ca10bf3",
    "build-003": "71eeca714e839be16c331ca9cf3985d9d17365be13dad04aecb6c73c6cf590cb",
    "build-004": "371dd8662f702ca0bcb4425dbbb79ae803b2069fc22ab7c95d3b58d35ba3e106",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def desc(body):
    return {"sha256": sha(body), "bytes": len(body)}


def load(body):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError("nonfinite JSON constant: " + value)

    return json.loads(body, object_pairs_hook=pairs, parse_constant=nonfinite, parse_float=str)


def safe(name):
    path = Path(name)
    need(name and not path.is_absolute() and ".." not in path.parts and str(path) == name,
         "unsafe relative alias")


def scan(name, body):
    safe(name)
    need(Path(name).suffix not in {".o", ".mod", ".smod", ".pyc", ".so", ".a", ".dll", ".dylib"}
         and "__pycache__" not in Path(name).parts, "compiled/cache payload")
    need(not body.startswith((b"\x7fELF", b"!<arch>", b"MZ")), "native payload")
    need(not re.search(rb"S-\d{3}-\d{4}\.\d{2}\.\d{2}-[A-Z2-7]{20,}", body), "license literal")


def unpack(body, expected):
    members = {}
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as archive:
        for entry in archive:
            need(entry.isfile() and entry.name not in members, "unique regular archive member")
            value = archive.extractfile(entry).read()
            scan(entry.name, value)
            need(desc(value) == expected.get(entry.name), "closed exact member identity")
            members[entry.name] = value
    need(set(members) == set(expected), "closed payload inventory")
    return members


def restore(manifest):
    actual = {str(path.relative_to(HERE)) for path in HERE.rglob("*") if path.is_file()}
    need(actual == set(manifest["capsule_files"]) | {"manifest.json"} and len(actual) == 7,
         "closed seven-file capsule")
    need(manifest["parent_files"] == {} and manifest["self_contained"] is True,
         "self-contained source and saved-test capsule")
    for name, expected in manifest["capsule_files"].items():
        body = (HERE / name).read_bytes()
        scan(name, body)
        need(desc(body) == expected, "capsule file " + name)
    members = unpack((HERE / "payload.tar.gz").read_bytes(), manifest["payload_members"])
    origins = load((HERE / "payload-origins.json").read_bytes())
    need(set(origins) == set(manifest["preserved_files"]), "exact source-origin alias inventory")
    files = {}
    for name, row in manifest["preserved_files"].items():
        safe(name)
        value = members[row["member"]]
        need(desc(value) == {key: row[key] for key in ["sha256", "bytes"]}
             == {key: origins[name][key] for key in ["sha256", "bytes"]}, "preserved alias " + name)
        files[name] = value
    need(files[Q + "/focused-qualification.json"] == (HERE / "qualification.json").read_bytes()
         and sha(files[Q + "/focused-qualification.json"]) == QUAL, "original aggregate qualification")
    return files


def restore_files(manifest):
    """Return exact project-relative aliases for downstream source inheritance."""
    return restore(manifest)


def replay(files, manifest):
    read = lambda name: load(files[Q + "/" + name])
    builds = {name: read(name + "/receipt.json") for name in BUILD_PINS}
    need(set(manifest["source_contexts"]) == set(builds), "four actual source contexts")
    source_hashes = {}
    cargo_errors = []
    for name, built in builds.items():
        need(sha(files[Q + "/" + name + "/receipt.json"]) == BUILD_PINS[name], "fixed actual build receipt")
        need(built["cleanup_errors"] == [], "historical build cleanup")
        if name == "build-001":
            need("inputs_unchanged" not in built, "preserved initial compile receipt lacks a postguard-success flag")
        else:
            need(built["inputs_unchanged"] is True, "successful build postguards")
        context = manifest["source_contexts"][name]
        need(context["source_files"] == built["source_files"] and len(context["source_files"]) == 158,
             "158 exact source bodies per context")
        prefix = context["source_alias_prefix"].rstrip("/") + "/"
        need(prefix == Q + "/" + name + "/source-snapshot/", "actual owned source snapshot aliases")
        source_hashes[name] = {}
        for canonical, expected in built["source_files"].items():
            source_hashes[name][canonical] = sha(files[prefix + canonical])
            need(source_hashes[name][canonical] == expected, "compiled source version " + name + "/" + canonical)
        events = []
        for index, step in enumerate(built["steps"]):
            need(step["owned_group_gone"] is True and F(step["elapsed_seconds"]) <= F(step["timeout_seconds"]),
                 "historical finite owned Cargo stage")
            raw = files[Q + "/" + name + "/cargo-" + str(index) + ".log"].decode()
            current = [load(line) for line in raw.splitlines() if line.startswith("{")]
            events.extend(current)
            need(any(event.get("reason") == "build-finished" and event.get("success") is (name != "build-001")
                     for event in current), "actual Cargo completion event")
            if name == "build-001":
                cargo_errors.extend(event["message"]["code"]["code"] for event in current
                                    if event.get("reason") == "compiler-message" and event["message"]["level"] == "error")
                need(step["returncode"] == 101 and step["status"] == "failed", "preserved initial compile failure")
            else:
                need(step["returncode"] == 0 and step["status"] == "exited", "successful actual Cargo stage")
        need(built["status"] == ("failed" if name == "build-001" else "passed"), "unmodified actual build outcome")
        for product in built.get("products", {}).values():
            event = load(files[Q + "/" + name + "/" + product["cargo_event"]])
            need(event in events and event["reason"] == "compiler-artifact"
                 and event["executable"] == product["cargo_executable"], "actual selected Cargo artifact event")
            need(manifest["omitted_compiled_products"][product["path"].removeprefix(PREFIX)] == product["sha256"],
                 "historical omitted product identity only")
        for output, expected in built["outputs"].items():
            alias = Q + "/" + name + "/" + output
            if output.startswith("frozen-"):
                need(manifest["omitted_compiled_products"][alias] == expected, "omitted native output metadata")
            else:
                need(sha(files[alias]) == expected, "saved raw Cargo output identity")
        for absolute, expected in built["inputs"].items():
            alias = absolute.removeprefix(PREFIX)
            if alias in built["source_files"]:
                value = files[prefix + alias]
            elif alias in files:
                value = files[alias]
            else:
                need(manifest["omitted_compiled_products"].get(alias) == expected, "only native build inputs omitted")
                continue
            need(sha(value) == expected, "actual build input context " + alias)
    need(cargo_errors == ["E0599"] * 4 + ["E0618", "E0283"], "all six original test compiler errors retained")
    anchor = source_hashes["build-003"]
    need(len(manifest["compiled_sources"]) == 158 and set(manifest["compiled_sources"]) == set(anchor), "shared canonical source surface")
    for canonical, row in manifest["compiled_sources"].items():
        need(sha(files[canonical]) == anchor[canonical] and row["alias"] == canonical
             and {key: row[key] for key in ["sha256", "bytes"]} == desc(files[canonical])
             and row["member"] == manifest["preserved_files"][canonical]["member"], "canonical build003 body owned once")
    overrides = {name: {path: digest for path, digest in values.items() if anchor[path] != digest}
                 for name, values in source_hashes.items()}
    need({name: len(rows) for name, rows in overrides.items()} == {"build-001": 8, "build-002": 4, "build-003": 0, "build-004": 1},
         "exact compiler/admission/test-only source versions")
    additional = {(path, digest) for rows in overrides.values() for path, digest in rows.items()}
    need(len(additional) == 9, "nine additional source versions, 167 distinct path/hash pairs")
    changed_test = "crates/iregi-rust/src/dispatch/mass_taylor_tests.rs"
    need(set(overrides["build-004"]) == {changed_test}, "sole build004 cfg(test) delta")
    before, after = [files[Q + "/" + name + "/source-snapshot/" + changed_test].decode()
                     for name in ["build-003", "build-004"]]
    need(before.replace("    assert_eq!(ordinary_kind(&legacy), TensorEngineKind::Generic);",
                        "    // The separate no-op proof stage preserves requested Legacy semantics.\n"
                        "    assert_eq!(ordinary_kind(&legacy), TensorEngineKind::LegacyNoOp);") == after,
         "byte-exact stale engine-observer correction")
    dispatch = files["crates/iregi-rust/src/dispatch.rs"].decode()
    need('#[cfg(test)]\n#[path = "dispatch/mass_taylor_tests.rs"]\nmod mass_taylor_tests;' in dispatch,
         "changed source included only under cfg(test)")
    bridge = read("test-selection-bridge.json")
    need(bridge["all_other_source_files_byte_identical"] is True and bridge["cli003_production_unchanged"] is True
         and bridge["build003_sha256"] == BUILD_PINS["build-003"], "source bridge to actual CLI003")
    tests = [read("tests-001/receipt.json"), read("tests-002/receipt.json")]
    need(tests[0]["status"] == "failed" and tests[1]["status"] == "passed", "initial observer failure retained")
    successes, failed_names = [], []
    for tag, receipt, count in zip(["tests-001", "tests-002"], tests, [95, 25]):
        need(receipt["inputs_unchanged"] is True and receipt["cleanup_errors"] == []
             and receipt["cpu_affinity"] == [18] and F(receipt["elapsed_seconds"]) <= F(receipt["total_seconds"]),
             "finite test stages and historical postguards")
        expected_product = builds["build-003" if tag == "tests-001" else "build-004"]["products"]["tests"]
        need(receipt["inputs"][expected_product["path"]] == expected_product["sha256"],
             "actual libtest context bound to selected frozen product")
        for absolute, expected in receipt["inputs"].items():
            alias = absolute.removeprefix(PREFIX)
            if alias in files:
                need(sha(files[alias]) == expected, "saved libtest input identity " + alias)
            else:
                need(manifest["omitted_compiled_products"].get(alias) == expected,
                     "only historical native libtest inputs omitted")
        stage_successes = []
        for index, step in enumerate(receipt["steps"]):
            need(step["owned_group_gone"] is True, "historical libtest group cleanup")
            need(step["command"][0] == expected_product["path"], "same selected actual libtest executable")
            if step["name"] == "listing":
                need(step["returncode"] == 0, "actual saved owned test listing")
                continue
            raw = files[Q + "/" + tag + "/step-" + str(index) + ".log"].decode()
            if step.get("strict_exact_gate") == "passed":
                summaries = [line for line in raw.splitlines() if line.startswith("test result:")]
                need(len(summaries) == 1 and re.fullmatch(
                    r"test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; [0-9]+ filtered out; finished in [^\n]+", summaries[0]),
                     "strict one-success raw libtest result")
                need(step["returncode"] == 0 and "test " + step["name"] + " ..." in raw,
                     "exact selected successful test")
                stage_successes.append(step["name"])
                successes.append((step["name"], tag + "/step-" + str(index) + ".log"))
            else:
                failed_names.append(step["name"])
                need("LegacyNoOp" in raw and "Generic" in raw and "test result: FAILED." in raw,
                     "actual stale Legacy tag failure raw log")
        need(len(stage_successes) == count, "95 then 25 strict successes")
        for output, expected in receipt["outputs"].items():
            need(sha(files[Q + "/" + tag + "/" + output]) == expected, "raw test output hash")
    need(len(successes) == len({name for name, log in successes}) == 120, "120 unique named passes without repeating 95")
    need([name for name, log in successes] == tests[0]["selected_tests"], "complete original120 inventory")
    need(tests[0]["unrun_tests"] == tests[1]["selected_tests"] and not tests[1]["unrun_tests"]
         and failed_names == tests[1]["selected_tests"][:1], "complete25 remainder, one preserved failed observer")
    selection = read("focused-selection.json")
    need(len(selection["existing_exact_tests"]) == 82 and len(selection["new_suffixes"]) == 38,
         "56 retained Power +26 Legacy +38 new focused cases")
    need(tests[0]["selected_tests"][:82] == selection["existing_exact_tests"], "original retained test names")
    for suffix, actual in zip(selection["new_suffixes"], tests[0]["selected_tests"][82:]):
        need(actual.endswith(suffix), "new exact names resolved from owned listing")
    qualification = read("focused-qualification.json")
    need(qualification["qualified_exact_test_count"] == 120 and qualification["first_context_passes"] == 95
         and qualification["second_context_passes"] == 25 and qualification["earlier95_repeated"] is False,
         "fixed aggregate test scope")
    for actual, saved in zip(successes, qualification["tests"]):
        need(saved["name"] == actual[0] and saved["log"] == actual[1]
             and saved["log_sha256"] == sha(files[Q + "/" + actual[1]]), "aggregate raw success binding")
    for name, expected in qualification["references"].items():
        need(sha(files[Q + "/" + name]) == expected, "aggregate reference identity")
    need(sum(F(t["elapsed_seconds"]) for t in tests) < 600
         and qualification["generalized_supplied_g_numeric_arrays_qualified"] is False
         and qualification["public_Dual_qualified"] is False and qualification["performance_qualified"] is False,
         "normal-test-only scope and aggregate finite bound")
    proposal = load(files[CORE + "/proposal.json"])
    review = load(files[CORE + "/independent-source-review.json"])
    need(review["proposal_sha256"] == sha(files[CORE + "/proposal.json"])
         and review["numerically_qualified"] is False, "original independent source review scope")
    for canonical, row in proposal["files"].items():
        need(sha(files[CORE + "/candidate/" + canonical]) == row["candidate_sha256"]
             == review["packet_bindings"][canonical], "reviewed original candidate body")
    need(sha(files[CORE + "/application.json"]) == builds["build-003"]["core_application_sha256"]
         and sha(files[FRONT + "/application.json"]) == builds["build-003"]["frontend_application_sha256"],
         "actual source application records")
    return {"status": "passed_saved_source_and_120_test_replay", "compiled_source_count": 158,
            "source_context_count": 4, "additional_source_versions": 9, "strict_named_passes": 120,
            "first_context_passes": 95, "second_context_passes": 25, "preserved_compile_errors": 6,
            "preserved_failed_observers": 1, "initial_failed_build_postguard_success_recorded": False,
            "generalized_G_array_qualification": False,
            "native_execution": False, "performance_qualification": False,
            "scope": "Four actual compile contexts and saved normal tests; no generalized-G integral array qualification."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconstruct", type=Path, help="Write exact project-relative aliases to a new directory.")
    args = parser.parse_args()
    manifest = load((HERE / "manifest.json").read_bytes())
    files = restore(manifest)
    result = replay(files, manifest)
    if args.reconstruct is not None:
        target = args.reconstruct.resolve()
        need(not target.exists(), "reconstruction destination must not exist")
        target.mkdir(parents=True)
        for name, body in files.items():
            output = target / name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(body)
        result["reconstructed_aliases"] = len(files)
    result["manifest_sha256"] = sha((HERE / "manifest.json").read_bytes())
    result["restored_aliases"] = len(files)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

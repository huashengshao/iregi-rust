"""Replay saved final-wheel smoke evidence using Python's standard library only.

This verifies historical records and source bytes. It does not load a wheel,
probe a process, invoke a compiler, or evaluate an integral.
"""
from pathlib import Path
import hashlib
import io
import json
import re
import tarfile
import xml.etree.ElementTree as ET

ROOT_PREFIX = "/shared/external/iregi/iregi-rust/"
RUN_PREFIX = ROOT_PREFIX + "target/python-restored-zero-profile-wheel-refresh/"
ENV_PREFIX = ROOT_PREFIX + ".local/tirust-restored-zero-profile-wheel-refresh-env/"
STAGES = ("build", "install", "import", "ordinary_eight", "checked_dual_one", "n6_one")
COUNTS = {"ordinary_eight": 8, "checked_dual_one": 1, "n6_one": 1}
BOUNDS = {"build": (1800, 60), "install": (180, 30), "import": (60, 20), "ordinary_eight": (180, 30), "checked_dual_one": (240, 30), "n6_one": (300, 30)}
ALIASES = ("Expression", "Float", "ComplexFloat", "Dual", "Model", "FeynmanDiagram", "TensorExpression", "ReductionPlan", "Workspace")
EXPECTED_TESTS = [
    "tests/python/test_tirust_interop.py::test_standalone_aliases_are_owner_classes_with_owner_metadata",
    "tests/python/test_tirust_interop.py::test_native_operations_work_with_canonical_symbolica_imports_blocked",
    "tests/python/test_tirust_numerics.py::test_batch_metadata_lane_failure_and_empty[f64-53-40]",
    "tests/python/test_tirust_numerics.py::test_batch_metadata_lane_failure_and_empty[double-double-106-70]",
    "tests/python/test_tirust_numerics.py::test_batch_metadata_lane_failure_and_empty[float-128-70]",
    "tests/python/test_tirust_numerics.py::test_dotted_propagator_matches_dual_mass_derivative_all_laurent_slots",
    "tests/python/test_tirust_numerics.py::test_float_inputs_beyond_binary64_remain_distinct",
    "tests/python/test_tirust_numerics.py::test_parameter_coefficient_duals_keep_mixed_components",
    "tests/python/test_tirust_dispatch.py::test_checked_scalar_products_cannot_bypass_certificates[options2]",
    "tests/python/test_tirust_dispatch.py::test_eligible_highpoint_batch_contraction_failure_and_recovery[6-1-six_point-6]",
]
PLAN = "target/rank6-final-focused-core-tests/final-wheel-smoke-plan.json"
CONTROLLER = "target/python-restored-zero-profile-wheel-refresh/run.py"
checks = 0


def require(condition, why):
    global checks
    checks += 1
    if not condition:
        raise ValueError(why)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def descriptor(body):
    return {"sha256": sha(body), "bytes": len(body)}


def safe_name(name):
    return bool(name) and not name.startswith("/") and ".." not in Path(name).parts


def text_payload(body, why):
    require(not body.startswith((b"\x7fELF", b"!<arch>", b"PK\x03\x04")), "no native/wheel/archive product: " + why)
    require(re.search(rb"S-[0-9]{3}-[0-9]{4}\.[0-9]{2}\.[0-9]{2}-[A-Z2-7]{30,}", body) is None, "no license literal: " + why)


def unpack_selected(path, archive_descriptor, selected, exact_inventory=False):
    body = path.read_bytes()
    require(descriptor(body) == {key: archive_descriptor[key] for key in ("sha256", "bytes")}, "archive byte binding: " + str(path))
    output = {}
    seen = set()
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as archive:
        for member in archive:
            require(member.isfile() and safe_name(member.name) and member.name not in seen, "safe distinct regular archive member")
            seen.add(member.name)
            if member.name in selected:
                require(member.size <= 32 * 1024 * 1024, "bounded selected member")
                content = archive.extractfile(member).read()
                require(descriptor(content) == selected[member.name], "selected archive member identity")
                text_payload(content, member.name)
                output[member.name] = content
    require(set(output) == set(selected), "all selected archive members exist")
    if exact_inventory:
        require(seen == set(selected), "exact local archive member inventory")
    return output


def repository_root(here, manifest):
    suffix = Path(manifest["capsule_directory"])
    require(tuple(here.parts[-len(suffix.parts):]) == suffix.parts, "capsule repository location")
    return here.parents[len(suffix.parts) - 1]


def verify(here):
    here = Path(here).resolve()
    manifest_body = (here / "manifest.json").read_bytes()
    manifest = json.loads(manifest_body)
    require(manifest["schema_version"] == 1 and manifest["status"] == "passed_restored_zero_profile_wheel_refresh_exact10_saved_smoke", "capsule schema and terminal status")
    root = repository_root(here, manifest)
    CORE = manifest["producer"]["coherent_build_receipt_path"]
    require(safe_name(CORE) and CORE.startswith("target/") and CORE.endswith("/receipt.json"), "owned fresh coherent receipt path")
    require(manifest["producer"]["run_directory"] == "target/python-restored-zero-profile-wheel-refresh" and manifest["producer"]["environment_directory"] == ".local/tirust-restored-zero-profile-wheel-refresh-env", "exact new producer paths")
    prior_path = "validation/python-interface/final-rank6-wheel-refresh-smoke/manifest.json"
    require(manifest["predecessor"]["manifest_path"] == prior_path, "immutable predecessor path")
    prior_body = (root / prior_path).read_bytes()
    require(descriptor(prior_body) == manifest["predecessor"]["manifest"], "immutable predecessor manifest byte binding")
    prior = json.loads(prior_body)
    for name, expected in manifest["capsule_files"].items():
        require(safe_name(name) and descriptor((here / name).read_bytes()) == expected, "capsule control byte binding: " + name)
    local = unpack_selected(here / "payload.tar.gz", manifest["capsule_files"]["payload.tar.gz"], manifest["payload_members"], True)
    require(set(local) == set(manifest["payload_members"]), "exact local object inventory")
    archives = {"local": local}
    for archive_name, entry in manifest["borrowed_archives"].items():
        require(safe_name(archive_name) and safe_name(entry["manifest_path"]), "relative direct parent paths")
        parent_body = (root / entry["manifest_path"]).read_bytes()
        require(descriptor(parent_body) == entry["manifest"], "direct parent manifest byte binding")
        parent = json.loads(parent_body)
        basename = Path(archive_name).name
        declared = parent["sources"] if basename == "sources.tar.gz" else parent["capsule_files"][basename]
        require({key: declared[key] for key in ("sha256", "bytes")} == {key: entry[key] for key in ("sha256", "bytes")}, "direct parent declares the borrowed archive identity")
        archives[archive_name] = unpack_selected(root / archive_name, entry, entry["members"])

    def materialize(entry):
        require(entry["archive"] in archives and entry["member"] in archives[entry["archive"]], "resolved direct object reference")
        body = archives[entry["archive"]][entry["member"]]
        require(descriptor(body) == {key: entry[key] for key in ("sha256", "bytes")}, "resolved alias identity")
        return body

    sources = {name: materialize(entry) for name, entry in manifest["selected_sources"].items()}
    evidence = {name: materialize(entry) for name, entry in manifest["evidence"].items()}
    context_body = evidence["context.json"]
    context = json.loads(context_body)
    context_sha = sha(context_body)
    require(context_sha == manifest["source_context_sha256"], "original frozen source context")
    require(len(sources) == len(context["inputs"]) == manifest["selected_source_count"] == 205, "exact selected205 source bodies")
    require(set(sources) == set(context["inputs"]), "exact selected source names")
    previous_context_body = evidence["predecessor-context.json"]
    require(sha(previous_context_body) == prior["source_context_sha256"], "immutable predecessor source context")
    previous_context = json.loads(previous_context_body)
    old_sources = previous_context["inputs"]
    require(len(old_sources) == len(prior["selected_sources"]) == 205 and set(old_sources) == set(prior["selected_sources"]), "exact predecessor source inventory")
    require(all(old_sources[name] == entry["sha256"] for name, entry in prior["selected_sources"].items()), "predecessor source map matches sealed locators")
    changed = {name for name in old_sources.keys() & context["inputs"].keys() if old_sources[name] != context["inputs"][name]}
    required_changes = {"crates/iregi-rust/src/execution.rs", "crates/iregi-rust/src/execution/quadrature_context_tests.rs"}
    require(changed == required_changes, "only the two authorized core bodies changed among common source paths")
    require(old_sources.keys() - context["inputs"].keys() == {"target/python-final-rank6-wheel-refresh/run.py", "target/e6-dual-optional-zero-profile-qualification/build-001/receipt.json"}, "only predecessor controller and coherent core receipt removed; historical core names receipt retained")
    require(context["inputs"].keys() - old_sources.keys() == {CORE, CONTROLLER}, "only fresh core receipt/controller added")
    old_coherent = previous_context["coherent_source_files"]
    require(len(old_coherent) == 128 and set(old_coherent) == set(context["coherent_source_files"]), "identical coherent128 source names")
    require({name for name in old_coherent if old_coherent[name] != context["coherent_source_files"][name]} == required_changes, "coherent core refresh has exactly the authorized two changed bodies")
    require(manifest["source_refresh_bridge"] == {"changed_common_paths": sorted(required_changes), "predecessor_selected_source_count": 205, "current_selected_source_count": 205, "coherent_source_count": 128, "actual_core_build_selected_source_count": 210}, "exact source-refresh bridge declaration")
    for name, digest in context["inputs"].items():
        require(safe_name(name) and sha(sources[name]) == digest, "frozen selected source body: " + name)
    require(len(context["coherent_source_files"]) == manifest["coherent_source_count"] == 128, "coherent current128 source scope")
    require(('CORE = ROOT / "' + CORE + '"').encode() in sources[CONTROLLER], "frozen new controller selects the fresh coherent core receipt")
    core = json.loads(sources[CORE])
    require(sha(sources[CORE]) == context["coherent_build_receipt_sha256"], "frozen coherent core build receipt")
    require(core["status"] == "passed_fresh_core_libtest_build_and_freeze" and core["inputs_unchanged"], "actual fresh core build and input ownership")
    require(len(core["sources"]) == context["coherent_build_selected_source_count"] == manifest["actual_core_build_selected_source_count"] == 210, "actual fresh core build selected210 source inventory")
    names_path = "target/ordinary-gh-parent-requalification/build-001/receipt.json"
    require(sha(sources[names_path]) == context["coherent_subset_names_receipt_sha256"] == "faa4ea0e4ea4029a8e61dbdbb02c5324f985793008e4cdc3aec1d8341fa64845", "historical receipt supplies exactly the selected subset names")
    names_receipt = json.loads(sources[names_path])
    require(set(names_receipt["source_files"]) == set(previous_context["coherent_source_files"]), "historical core128 names agree with predecessor context")
    require(set(names_receipt["source_files"]) == set(context["coherent_source_files"]) <= set(core["sources"]), "selected coherent128 names are a subset of actual fresh210")
    require({name: core["sources"][name] for name in context["coherent_source_files"]} == context["coherent_source_files"], "all coherent128 values come from actual fresh210 build")
    for name, digest in context["coherent_source_files"].items():
        require(name in sources and sha(sources[name]) == digest, "all coherent current128 bodies present")
    plan = json.loads(sources[PLAN])
    require(sha(sources[PLAN]) == context["smoke_plan_sha256"], "frozen exact10 plan bytes")
    require(plan["exact_existing_pytest_node_ids"] == context["exact_tests"] == EXPECTED_TESTS, "strict exact10 test IDs")
    controller = sources[CONTROLLER]
    for phrase in (
        b'require(sha(native) == read(HERE / "build-001/wheel.json")["native_sha256"], "exact installed native hash")',
        b'require(native.is_relative_to(ENV), "native loaded from fresh installed environment")',
        b'assert not any(k==\'symbolica\' or k.startswith(\'symbolica.\') for k in sys.modules)',
        b'require(archive.read("tirust/_tirust.pyi") == (ROOT / "python/tirust/_tirust.pyi").read_bytes(), "unchanged current stub bytes included")',
    ):
        require(phrase in controller, "historical native ownership/stub guard in actual frozen controller")
    wheel = json.loads(evidence["build-001/wheel.json"])
    require(wheel == manifest["omitted_artifacts"], "recorded omitted wheel/native identity")
    require(wheel["wheel"] == RUN_PREFIX + "wheels/tirust-0.1.0-cp310-abi3-linux_x86_64.whl", "actual owned wheel location")
    require(wheel["native_member"] == "tirust/_tirust.abi3.so", "one recorded native owner member")
    require(all(re.fullmatch(r"[0-9a-f]{64}", wheel[key]) for key in ("wheel_sha256", "native_sha256")), "recorded artifact SHA identities")
    require(all(isinstance(wheel[key], int) and wheel[key] > 0 for key in ("wheel_bytes", "native_bytes")), "positive recorded artifact sizes")
    identity = json.loads(evidence["import-001/identity.json"])
    require(identity["native"].startswith(ENV_PREFIX) and identity["native"].endswith("/" + wheel["native_member"]), "historical native owner imported from fresh environment")
    require(identity["package"].startswith(ENV_PREFIX) and identity["package"].endswith("/tirust/__init__.py"), "historical package in same fresh environment")
    require(Path(identity["native"]).parent == Path(identity["package"]).parent, "one exact installed package directory owns native module")
    require(identity["shared_aliases"] == list(ALIASES), "all nine exact shared owner classes")
    require(json.loads(evidence["import-001/step-0.log"].decode().splitlines()[-1]) == identity, "actual import log identity")
    groups = 0
    actual_tests = []
    for stage in STAGES:
        prefix = stage + "-001/"
        receipt = json.loads(evidence[prefix + "receipt.json"])
        require(receipt["stage"] == stage and receipt["status"] == "passed", "actual successful stage: " + stage)
        require(receipt["source_context_sha256"] == context_sha and receipt["source_file_count"] == 205, "stage frozen source context")
        require(receipt["coherent_build_receipt_sha256"] == context["coherent_build_receipt_sha256"] and receipt["toolchain"] == context["toolchain"], "stage coherent build and pinned toolchain")
        require(not receipt["cleanup_errors"] and receipt["cancellation"] is None and receipt["inputs_unchanged"], "historical successful cleanup and owned-input guards")
        require(receipt["performance_qualified"] is False and receipt["new_independent_integrals"] is False, "frontend smoke scope only")
        require(0 <= receipt["elapsed_seconds"] <= receipt["seconds"] and 0 < receipt["cleanup_reserve_seconds"] < receipt["seconds"], "actual finite bounded stage")
        require((receipt["seconds"], receipt["cleanup_reserve_seconds"]) == BOUNDS[stage], "exact approved stage and cleanup budgets")
        require(receipt["main_source_Cargo_lease"] == (stage == "build"), "stage source/Cargo lease scope")
        if stage == "build":
            for key, suffix in (("CARGO_TARGET_DIR", "target"), ("CARGO_BUILD_BUILD_DIR", "target/cargo-build")):
                require(receipt["environment_overrides"][key] == ROOT_PREFIX + suffix, "explicit safely reused compiler cache: " + key)
            require(receipt["environment_overrides"]["CARGO_BUILD_JOBS"] == "2", "bounded Cargo jobs")
            build_command = receipt["steps"][0]["command"]
            for option, value in (("--features", "standalone,native"), ("--profile", "dev"), ("--jobs", "2")):
                require(build_command[build_command.index(option) + 1] == value, "actual selected wheel build option: " + option)
            require("--locked" in build_command and "--offline" in build_command, "actual locked offline build")
        expected_guards = {(ROOT_PREFIX if stage == "build" else RUN_PREFIX + "build-001/source-snapshot/") + name: digest for name, digest in context["inputs"].items()}
        expected_guards[RUN_PREFIX + "context.json"] = context_sha
        if stage != "build":
            expected_guards[wheel["wheel"]] = wheel["wheel_sha256"]
        require(receipt["inputs"] == expected_guards, "complete exact historical source/product guards")
        require(len(receipt["steps"]) == (2 if stage == "install" else 1), "exact stage process count")
        for step in receipt["steps"]:
            require(step["status"] == "exited" and step["returncode"] == 0 and step["owned_group_gone"] is True, "historical successful owned process group terminal")
            require(step["timeout_seconds"] > 0 and step["elapsed_seconds"] <= receipt["seconds"], "finite owned child time")
            groups += 1
        require(receipt["cpu"] == ("20,21" if stage == "build" else "22"), "pinned stage CPU scope")
        for name, digest in receipt["saved_files"].items():
            require(safe_name(name) and "/" not in name and prefix + name in evidence, "all saved stage outputs retained")
            require(sha(evidence[prefix + name]) == digest, "saved stage output exact bytes")
        expected_output = {prefix + "receipt.json", *(prefix + name for name in receipt["saved_files"])}
        require({name for name in evidence if name.startswith(prefix)} == expected_output, "exact retained stage output inventory")
        if stage in COUNTS:
            chosen = {"ordinary_eight": EXPECTED_TESTS[:8], "checked_dual_one": EXPECTED_TESTS[8:9], "n6_one": EXPECTED_TESTS[9:10]}[stage]
            cases = list(ET.fromstring(evidence[prefix + "tests.xml"]).iter("testcase"))
            require(receipt["expected_test_count"] == len(chosen) == len(cases) == COUNTS[stage], "strict exact successful XML count")
            require(all(not list(case) for case in cases), "no skipped, failed, xfailed, or error cases")
            names = [case.attrib["name"] for case in cases]
            ids = [case.attrib["classname"].replace(".", "/") + ".py::" + case.attrib["name"] for case in cases]
            require(ids == chosen and names == receipt["test_names"], "actual complete XML node IDs and saved names")
            command = receipt["steps"][0]["command"]
            require(command[-len(chosen):] == [RUN_PREFIX + "build-001/source-snapshot/" + name for name in chosen], "actual exact selected pytest commands")
            require("--rootdir=" + RUN_PREFIX + "build-001/source-snapshot" in command, "tests actually use frozen source snapshot")
            actual_tests.extend(ids)
        else:
            require(receipt["expected_test_count"] is None, "non-test stage count")
    require(actual_tests == EXPECTED_TESTS and groups == 7, "exact ten tests and seven successful historical process groups")
    require(manifest["native_or_integral_execution_by_checker"] is False and manifest["performance_qualified"] is False, "saved-only replay and qualification scope")
    result = {
        "status": "passed_saved_restored_zero_profile_wheel_refresh_exact10_replay",
        "checks": checks,
        "selected_source_files": len(sources),
        "coherent_source_files": 128,
        "actual_core_build_selected_source_files": 210,
        "authorized_changed_core_source_files": 2,
        "exact_existing_api_tests": len(actual_tests),
        "successful_historical_process_groups": groups,
        "native_or_integral_execution": False,
        "new_independent_integrals": False,
        "performance_qualified": False,
        "manifest_sha256": sha(manifest_body),
    }
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    verify(Path(__file__).resolve().parent)

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
RUN_PREFIX = ROOT_PREFIX + "target/python-final-rank6-wheel/"
ENV_PREFIX = ROOT_PREFIX + ".local/tirust-final-rank6-wheel-env/"
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
CORE = "target/ordinary-gh-parent-requalification/build-001/receipt.json"
PLAN = "target/rank6-final-focused-core-tests/final-wheel-smoke-plan.json"
CONTROLLER = "target/python-final-rank6-wheel/run.py"
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
    require(manifest["schema_version"] == 1 and manifest["status"] == "passed_final_rank6_wheel_exact10_saved_smoke", "capsule schema and terminal status")
    root = repository_root(here, manifest)
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
    require(len(sources) == len(context["inputs"]) == manifest["selected_source_count"] == 204, "exact selected204 source bodies")
    require(set(sources) == set(context["inputs"]), "exact selected source names")
    for name, digest in context["inputs"].items():
        require(safe_name(name) and sha(sources[name]) == digest, "frozen selected source body: " + name)
    require(len(context["coherent_source_files"]) == manifest["coherent_source_count"] == 128, "coherent current128 source scope")
    core = json.loads(sources[CORE])
    require(sha(sources[CORE]) == context["coherent_build_receipt_sha256"], "frozen coherent core build receipt")
    require(core["status"] == "passed" and core["source_files"] == context["coherent_source_files"], "actual coherent core128 build source inventory")
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
        require(receipt["source_context_sha256"] == context_sha and receipt["source_file_count"] == 204, "stage frozen source context")
        require(receipt["coherent_build_receipt_sha256"] == context["coherent_build_receipt_sha256"] and receipt["toolchain"] == context["toolchain"], "stage coherent build and pinned toolchain")
        require(not receipt["cleanup_errors"] and receipt["cancellation"] is None and receipt["inputs_unchanged"], "historical successful cleanup and owned-input guards")
        require(receipt["performance_qualified"] is False and receipt["new_independent_integrals"] is False, "frontend smoke scope only")
        require(0 <= receipt["elapsed_seconds"] <= receipt["seconds"] and 0 < receipt["cleanup_reserve_seconds"] < receipt["seconds"], "actual finite bounded stage")
        require((receipt["seconds"], receipt["cleanup_reserve_seconds"]) == BOUNDS[stage], "exact approved stage and cleanup budgets")
        require(receipt["main_source_Cargo_lease"] == (stage == "build"), "stage source/Cargo lease scope")
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
        require(receipt["cpu"] == ("18,19" if stage == "build" else "22"), "pinned stage CPU scope")
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
        "status": "passed_saved_final_rank6_wheel_exact10_replay",
        "checks": checks,
        "selected_source_files": len(sources),
        "coherent_source_files": 128,
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

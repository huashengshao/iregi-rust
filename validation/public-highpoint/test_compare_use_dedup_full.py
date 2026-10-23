"""Python-only rejection tests; synthetic success arrays are never qualifications."""
from decimal import localcontext
from fractions import Fraction
from pathlib import Path
import copy
import json
import tempfile
import unittest

import compare_use_dedup_full as compare


class ArrayInspectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path("validation/public-highpoint")
        cls.fixture = compare.read(here / "fixture-conditioned_masses.json")
        cls.reference = compare.read(here / "reference-conditioned_masses.json")
        cls.fixture_hash = compare.digest(here / "fixture-conditioned_masses.json")

    def setUp(self):
        self.context = localcontext()
        self.context.__enter__().prec = 160
        self.addCleanup(self.context.__exit__, None, None, None)
        sample = self.fixture["samples"][0]
        case = next(case for case in self.reference["cases"] if case["id"] == "n6_base_mode0")
        inputs = [[str(Fraction(v)), "0"] for p in sample["propagators"][:6] for v in p["shift"]]
        inputs += [[str(Fraction(v)) for v in p["mass_squared"]] for p in sample["propagators"][:6]]
        inputs += [[str(Fraction(sample["mu"])), "0"]]
        self.record = {"status": "all_lanes_success", "working_bits": 128, "requested_bits": 53,
                       "settings": {"propagators": 6, "rank": 7, "powers": [1]*6, "dimension_shift": 0,
                                    "convention": "IregiNative", "tensor_weights": "Components",
                                    "invariants": "FromShifts", "input_policy": "Preserve",
                                    "algorithm": "PassarinoVeltman"},
                       "components": 1, "rows": 1, "basis": compare.public.canonical_basis(7),
                       "input_exact_rational": [inputs], "lane_statuses": ["Success"],
                       "lanes": [{"row": 0, "status": "Success", "moments": [
                           [{"real": str(Fraction(pair[0])), "imaginary": str(Fraction(pair[1]))}
                            for pair in moment] for moment in case["response"]["moments"]]}]}

    def inspect(self, record=None, reference=None):
        return compare.inspect_single(record or self.record, reference or self.reference,
                                      self.fixture, self.fixture_hash)

    def test_single_complete_array_has_no_convergence_claim(self):
        result = self.inspect()
        self.assertTrue(result["passed"])
        self.assertFalse(result["precision_convergence_checked"])
        self.assertEqual(result["compared_complex_slots"], 1320)
        self.assertNotIn("convergence_tolerance", result)

    def test_failed_lane_and_partial_array_cannot_be_inspected(self):
        for mutation in [lambda r: r.update(status="lanes_rejected"),
                         lambda r: r["lanes"][0]["moments"].pop(),
                         lambda r: r["lanes"][0]["moments"][0].pop()]:
            changed = copy.deepcopy(self.record)
            mutation(changed)
            with self.assertRaises(ValueError):
                self.inspect(changed)

    def test_reordered_basis_and_wrong_exact_input_are_rejected(self):
        changed = copy.deepcopy(self.record)
        changed["basis"][1], changed["basis"][2] = changed["basis"][2], changed["basis"][1]
        with self.assertRaises(ValueError):
            self.inspect(changed)
        changed = copy.deepcopy(self.record)
        changed["input_exact_rational"][0][0][0] = "123"
        with self.assertRaises(ValueError):
            self.inspect(changed)

    def test_last_finite_imaginary_slot_is_compared(self):
        self.record["lanes"][0]["moments"][-1][3]["imaginary"] = "1"
        result = self.inspect()
        self.assertFalse(result["passed"])
        self.assertTrue(any(item["moment"] == 329 and item["slot"] == 3 for item in result["reference_failures"]))

    def test_dimensional_pole_threshold_is_not_relaxed(self):
        # N6 scalar normalization is Q^-8 = 1/256 for this fixture.
        self.record["lanes"][0]["moments"][0][0] = {"real": "1/2560000000000", "imaginary": "0"}
        self.assertFalse(self.inspect()["pole_failures"])
        self.record["lanes"][0]["moments"][0][0]["real"] = "1/1280000000000"
        self.assertTrue(self.inspect()["pole_failures"])

    def test_reference_stability_and_transport_are_mandatory(self):
        changed = copy.deepcopy(self.reference)
        changed["cases"][0]["response"]["stable"] = False
        with self.assertRaisesRegex(ValueError, "transport"):
            self.inspect(reference=changed)
        changed["cases"][0]["stdout"] = "RESULT " + json.dumps(changed["cases"][0]["response"]) + "\n"
        with self.assertRaisesRegex(ValueError, "stable"):
            self.inspect(reference=changed)

    def test_matching_wrong_reference_pole_still_fails_zero_constraint(self):
        changed = copy.deepcopy(self.reference)
        changed["cases"][0]["response"]["moments"][0][0] = ["1", "0"]
        changed["cases"][0]["stdout"] = "RESULT " + json.dumps(changed["cases"][0]["response"]) + "\n"
        self.record["lanes"][0]["moments"][0][0] = {"real": "1", "imaginary": "0"}
        result = self.inspect(reference=changed)
        self.assertFalse(result["reference_failures"])
        self.assertTrue(result["pole_failures"] and result["reference_pole_failures"])
        self.assertFalse(result["passed"])

    def test_two_precisions_require_increase_and_detect_disagreement(self):
        high = copy.deepcopy(self.record)
        with self.assertRaisesRegex(ValueError, "increasing"):
            compare.compare_arrays(self.record, high, self.reference, self.fixture, self.fixture_hash)
        high["working_bits"] = 256
        result = compare.compare_arrays(self.record, high, self.reference, self.fixture, self.fixture_hash)
        self.assertTrue(result["passed"] and result["precision_convergence_checked"])
        high["lanes"][0]["moments"][-1][3]["real"] = "1/1000000000000000000"
        result = compare.compare_arrays(self.record, high, self.reference, self.fixture, self.fixture_hash)
        self.assertTrue(result["convergence_failures"])
        self.assertFalse(result["passed"])


class ProvenanceTests(unittest.TestCase):
    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if not isinstance(value, str) else value)
        return compare.digest(path)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="dedup-comparator-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.here = self.root / "validation/public-highpoint"
        self.frozen = self.root / "target/public-highpoint/use-dedup-full/source"
        self.fixture = self.here / "fixture-conditioned_masses.json"
        self.write(self.fixture, {})
        self.result = self.here / "sample.json"
        self.record = {"fixture": str(self.fixture.relative_to(self.root)), "settings": {
            "propagators": 6, "rank": 7, "algorithm": "PassarinoVeltman"},
            "working_bits": 128, "requested_bits": 53, "rows": 1}
        self.write(self.result, self.record)
        sources = {name: self.write(self.frozen / name, "test-only frozen source") for name in [
            "crates/iregi-rust/src/lib.rs", "crates/iregi-rust/examples/highpoint_public.rs"]}
        originals = {name: self.write(self.frozen.parent / "original" / name, "test-only original") for name in sources}
        self.binary = self.frozen.parent / "highpoint_public"
        binary_hash = self.write(self.binary, "test-only binary identity")
        test_binary = self.frozen.parent / "core_tests"
        test_hash = self.write(test_binary, "test-only test binary identity")
        dependencies = {}; baseline = []
        for name in ["iregi_masters", "symbolica", "oneloop"]:
            path = self.root / f"target/stack-reuse-current-workspace/deps/lib{name}-test.rlib"
            value = self.write(path, "test-only archive " + name)
            dependencies[str(path.relative_to(self.root))] = value
            baseline.append({"preserved_path": str(path.relative_to(self.root)), "sha256": value})
        self.write(self.here / "build.json", {"library_artifacts": baseline})
        hook = self.here / "use_dedup_full_hooks.py"
        protected = {str(hook.relative_to(self.root)): self.write(hook, "test-only hook")}
        patch_hash = self.write(self.here / "use-dedup-full-instrumentation.patch", "test-only patch")
        self.build = {"status": "passed", "exit_codes": [0, 0, 0], "changed_inputs": {}, "sources_unchanged": True,
                      "source_revision": compare.EXPECTED_REVISION, "frozen_source_root": str(self.frozen.relative_to(self.root)),
                      "frozen_source_hashes": sources, "original_source_hashes": originals,
                      "protected_input_hashes": protected, "dependency_hashes": dependencies,
                      "instrumentation_patch_sha256": patch_hash, "binary_path": str(self.binary.relative_to(self.root)),
                      "binary_sha256": binary_hash, "test_binary_path": str(test_binary.relative_to(self.root)),
                      "test_binary_sha256": test_hash}
        self.build_path = self.here / "use-dedup-full-build.json"
        build_hash = self.write(self.build_path, self.build)
        semantic_path = self.here / "use-dedup-full-tests-run.json"
        self.write(semantic_path, {"status": "passed", "changed_inputs": {}, "build_manifest_sha256": build_hash,
                                   "protected_input_hashes": {str(test_binary.relative_to(self.root)): test_hash}})
        artifacts = {str(path.relative_to(self.root)): compare.digest(path) for path in [self.build_path, semantic_path]}
        for name in ["use-dedup-full-tests-list.txt", "qualify_use_dedup_full_tests.py",
                     "use-dedup-full-tests-stability.log", "use-dedup-full-tests-execution.log"]:
            path = self.here / name
            artifacts[str(path.relative_to(self.root))] = self.write(path, "test-only qualified artifact")
        self.qualification_path = self.here / "use-dedup-full-tests-qualification.json"
        self.qualification = {"status": "passed", "build_manifest_sha256": build_hash,
                              "exact_complete_module_counts": compare.MODULE_COUNTS, "total_passed": 73,
                              "artifacts": artifacts}
        qualification_hash = self.write(self.qualification_path, self.qualification)
        runner_hash = self.write(self.here / "run_use_dedup_full.py", "test-only runner")
        log_hash = self.write(self.result.with_suffix(".log"), "test-only log")
        self.run = {"variant": "use-dedup-full", "status": "completed", "exit_code": 0,
                    "last_public_stage": "all_lanes_success", "numerical_reduction_entered": True,
                    "result_sha256": compare.digest(self.result), "fixture_sha256": compare.digest(self.fixture),
                    "build_manifest_sha256": build_hash, "frozen_source_files_unchanged": len(sources),
                    "binary_sha256": binary_hash, "probe_source_sha256": sources["crates/iregi-rust/examples/highpoint_public.rs"],
                    "runner_source_sha256": runner_hash, "log_sha256": log_hash,
                    "environment_additions": {"IREGI_PV_PREPARATION_PROFILE": "1", "RAYON_NUM_THREADS": "1", "IREGI_PREPARATION_PROFILE": "1"},
                    "environment_removals": ["IREGI_ALIAS_USE_VERIFY", "IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE", "IREGI_MASTER_AMPLITUDE_MODE"],
                    "timeout_seconds": 600, "semantic_qualification_sha256": qualification_hash,
                    "command": ["taskset", "-c", "14", str(self.binary), self.record["fixture"], "6", "7", "pv", "128", "53", "1", str(self.result.relative_to(self.root))]}

    def check(self):
        self.write(self.here / "sample-run.json", self.run)
        return compare.validate_provenance(self.record, self.result, self.fixture, self.root)

    def test_matching_frozen_full_build_chain_is_accepted(self):
        self.assertEqual(self.check()["variant"], "use-dedup-full")

    def test_timeout_and_false_success_result_cannot_qualify(self):
        self.run.update(status="timeout", exit_code=-9)
        with self.assertRaisesRegex(ValueError, "unsuccessful"):
            self.check()

    def test_changed_result_build_and_frozen_source_are_rejected(self):
        self.result.write_text(self.result.read_text()+"\n")
        with self.assertRaisesRegex(ValueError, "mismatched"):
            self.check()
        self.run["result_sha256"] = compare.digest(self.result)
        self.build_path.write_text(self.build_path.read_text()+"\n")
        with self.assertRaisesRegex(ValueError, "mismatched"):
            self.check()
        self.run["build_manifest_sha256"] = compare.digest(self.build_path)
        self.write(self.frozen / "crates/iregi-rust/src/lib.rs", "changed")
        with self.assertRaisesRegex(ValueError, "frozen source"):
            self.check()

    def test_wrong_command_precision_and_missing_source_count_are_rejected(self):
        self.run["command"][8] = "256"
        with self.assertRaisesRegex(ValueError, "command"):
            self.check()
        self.run["command"][8] = "128"
        self.run["frozen_source_files_unchanged"] = 0
        with self.assertRaisesRegex(ValueError, "every frozen source"):
            self.check()

    def test_changed_dependency_and_semantic_logs_are_rejected(self):
        dependency = self.root / next(iter(self.build["dependency_hashes"]))
        previous = dependency.read_text()
        dependency.write_text("changed archive")
        with self.assertRaisesRegex(ValueError, "dependency"):
            self.check()
        dependency.write_text(previous)
        self.write(self.here / "use-dedup-full-tests-stability.log", "0 tests")
        with self.assertRaisesRegex(ValueError, "Semantic qualification"):
            self.check()

    def test_incomplete_module_qualification_is_rejected(self):
        self.qualification["total_passed"] = 0
        self.run["semantic_qualification_sha256"] = self.write(self.qualification_path, self.qualification)
        with self.assertRaisesRegex(ValueError, "complete semantic"):
            self.check()

    def test_different_build_cannot_supply_the_higher_precision(self):
        low = self.check(); high = copy.deepcopy(low)
        high["build_manifest_sha256"] = "different frozen build"
        with self.assertRaisesRegex(ValueError, "same frozen build"):
            compare.require_same_build({"low": low, "high": high})


class OriginalCaptureProvenanceTests(unittest.TestCase):
    def test_original_executable_and_fixture_path_are_bound(self):
        with tempfile.TemporaryDirectory(prefix="dedup-reference-") as temporary:
            root = Path(temporary)
            here = root / "validation/public-highpoint"
            here.mkdir(parents=True)
            source = Path("validation/public-highpoint")
            fixture_path = here / "fixture-conditioned_masses.json"
            fixture_path.write_bytes((source / fixture_path.name).read_bytes())
            fixture = compare.read(fixture_path)
            reference = compare.read(source / "reference-conditioned_masses.json")
            executable = root / "target/reference/iregi-reference-original"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"test-only original executable identity")
            reference["executable_sha256"] = compare.digest(executable)
            reference_path = here / "reference-conditioned_masses.json"
            reference_path.write_text(json.dumps(reference))
            provenance = compare.validate_reference_capture(reference, reference_path, fixture_path, fixture, root)
            self.assertEqual(provenance["reference_sha256"], compare.digest(reference_path))
            reference["fixture"] = "different-fixture.json"
            with self.assertRaisesRegex(ValueError, "provenance"):
                compare.validate_reference_capture(reference, reference_path, fixture_path, fixture, root)
            reference["fixture"] = str(fixture_path.relative_to(root))
            executable.write_bytes(b"changed executable")
            with self.assertRaisesRegex(ValueError, "provenance"):
                compare.validate_reference_capture(reference, reference_path, fixture_path, fixture, root)


if __name__ == "__main__":
    unittest.main()

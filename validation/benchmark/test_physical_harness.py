"""Protocol/gate regression tests; no Rust, Fortran, or Symbolica execution."""
import copy
import itertools
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import physical_run as benchmark


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "build_provenance_checks": {
                "successful_stable_build": True, "binary_matches_manifest": True,
                "sources_match_manifest": True, "assets_match_manifest": True,
            },
            "source_changed_during_run": False,
            "workspace_source_changed_during_run": False,
            "assets_changed_during_run": False,
            "binaries_changed_during_run": False,
        }

    def test_stable_retained_sources_do_not_hide_a_changed_live_harness(self):
        self.assertTrue(benchmark.provenance_qualified(self.data))
        # The Rust build snapshot is unchanged, but physical_run.py and its
        # checker execute from the workspace even with --revision.
        self.data["workspace_source_changed_during_run"] = True
        self.assertFalse(benchmark.provenance_qualified(self.data))

    def test_missing_or_failed_final_checks_cannot_qualify(self):
        for name in ["source_changed_during_run", "workspace_source_changed_during_run",
                     "assets_changed_during_run", "binaries_changed_during_run"]:
            with self.subTest(name=name):
                changed = dict(self.data, **{name: True})
                self.assertFalse(benchmark.provenance_qualified(changed))
                missing = dict(self.data)
                del missing[name]
                self.assertFalse(benchmark.provenance_qualified(missing))
        for name in self.data["build_provenance_checks"]:
            with self.subTest(build_check=name):
                failed = copy.deepcopy(self.data)
                failed["build_provenance_checks"][name] = False
                self.assertFalse(benchmark.provenance_qualified(failed))
                del failed["build_provenance_checks"][name]
                self.assertFalse(benchmark.provenance_qualified(failed))


class InterruptedRunTests(unittest.TestCase):
    def setUp(self):
        self.configurations = [(case, {"id": case, "precision": "f64", "bits": 53,
                                      "accuracy_bits": 53, "input": {"samples": [{}]}})
                               for case in ["ggh", "gghh", "gghhh"]]
        self.data = {"status": "running", "rows": benchmark.configuration_rows(self.configurations)}

    def test_interrupt_between_rows_retains_every_requested_configuration(self):
        self.data["rows"][0]["status"] = "measured"
        benchmark.finalize_rows(self.data, completed_normally=False)
        self.assertEqual(self.data["status"], "interrupted")
        self.assertEqual([row["id"] for row in self.data["rows"]], ["ggh", "gghh", "gghhh"])
        self.assertEqual([row["status"] for row in self.data["rows"]],
                         ["measured", "not_run", "not_run"])

    def test_interrupt_during_a_row_keeps_completed_work_and_pending_failures_visible(self):
        self.data["rows"][0]["status"] = "failed"
        self.data["rows"][1]["status"] = "running"
        benchmark.finalize_rows(self.data, completed_normally=False)
        self.assertEqual([row["status"] for row in self.data["rows"]],
                         ["failed", "interrupted", "not_run"])
        self.assertEqual(self.data["status"], "interrupted")

    def test_completion_requires_all_configurations_to_finish(self):
        benchmark.finalize_rows(self.data, completed_normally=True)
        self.assertEqual(self.data["status"], "interrupted")
        for row, status in zip(self.data["rows"], ["measured", "failed", "timeout"], strict=True):
            row["status"] = status
        benchmark.finalize_rows(self.data, completed_normally=True)
        self.assertEqual(self.data["status"], "complete")


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.request = {"op": "measure", "id": "fixture", "stage": "reduction",
                        "warmup": 0, "iterations": 7, "repeats": 1}
        self.response = {"id": "fixture", "status": "measured", "stage": "reduction",
                         "warmup": 0, "iterations": 7, "repeats": 1, "profiled": False,
                         "total_ns": [500.0], "profile_ns": [],
                         "profile_order": ["arguments", "masters", "reduction", "total"]}

    def test_valid_uninstrumented_and_instrumented_replies(self):
        benchmark.validate_response(self.response, self.request, "fixture")
        self.request["profile"] = self.response["profiled"] = True
        self.response["profile_ns"] = [[50., 300., 100., 480.]]
        benchmark.validate_response(self.response, self.request, "fixture")

    def test_wrong_stage_counts_and_profiling_are_rejected(self):
        for key, value in [("stage", "numerator"), ("iterations", 6), ("repeats", 2),
                           ("warmup", 1), ("profiled", True), ("status", "prepared"),
                           ("id", "another-fixture"), ("total_ns", []),
                           ("total_ns", [float("nan")]), ("profile_ns", [[0., 0., 0., 0.]])]:
            with self.subTest(key=key, value=value):
                response = dict(self.response, **{key: value})
                with self.assertRaises(ValueError):
                    benchmark.validate_response(response, self.request, "fixture")

    def test_zero_profile_components_remain_defined(self):
        summary = benchmark.summarized([0., 0., 0.])
        self.assertEqual(summary["uncertainty"], "zero-observed-component")
        self.assertIsNone(summary["relative_ci_width"])


class CorrectnessContractTests(unittest.TestCase):
    def setUp(self):
        self.case = "gghhh"
        sample = json.loads(Path("validation/physical/gghhh-cli-input.json").read_text())
        self.configuration = {"input": {"samples": [sample, copy.deepcopy(sample)]},
                              "precision": "float", "bits": 128, "accuracy_bits": 53,
                              "algorithm": "Hybrid"}
        basis = [[indices.count(axis) for axis in range(4)] for rank in range(sample["rank"] + 1)
                 for indices in itertools.combinations_with_replacement(range(4), rank)]
        lane = {"id": sample["id"], "status": "success", "moments": [[["0", "0"] for _ in range(4)] for _ in basis],
                "integral": [["0", "0"] for _ in range(4)]}
        self.output = {"precision_bits": 128, "precision_control": {"accuracy_bits": 53},
                       "algorithm_requested": "Hybrid", "settings": {"convention": "OneLoop",
                           "tensor_weights": "Components", "dimension_shift": 0, "powers": [1] * 5,
                           "propagators": 5, "rank": sample["rank"]},
                       "poles": ["uv1", "ir1", "ir2", "finite"], "basis": basis,
                       "graph": {"name": "gghhh_top_pentagon"}, "samples": [lane, copy.deepcopy(lane)]}
        self.references = [{"mode": mode, "results": [{"mode": mode}]} for mode in [0, 1, 2]]
        # These tests cover boundary metadata and fail-closed gating. Actual
        # numerical reference comparison remains in compare_cli.py and fixtures.
        self.tensor = patch.object(benchmark.physical, "compare_tensors",
                                   side_effect=lambda result, sample, expected, tolerance:
                                   {"passed": expected["mode"] != 0})
        self.integral = patch.object(benchmark.physical, "compare_physical", return_value={"passed": True})
        self.tensor.start()
        self.integral.start()
        self.addCleanup(self.tensor.stop)
        self.addCleanup(self.integral.stop)

    def test_known_reference_exception_stays_visible_for_all_lanes(self):
        checked = benchmark.check(self.output, self.configuration, self.case, self.references)
        self.assertTrue(checked["passed"])
        self.assertFalse(checked["all_original_modes_passed"])
        self.assertEqual(checked["required_original_modes"], [1, 2])
        self.assertEqual(len(checked["lanes"]), 2)

    def test_same_rank_reordered_basis_is_rejected(self):
        self.output["basis"][1], self.output["basis"][2] = self.output["basis"][2], self.output["basis"][1]
        with self.assertRaisesRegex(ValueError, "basis"):
            benchmark.check(self.output, self.configuration, self.case, self.references)

    def test_missing_reference_mode_cannot_pass_vacuously(self):
        with self.assertRaisesRegex(ValueError, "mode records"):
            benchmark.check(self.output, self.configuration, self.case, self.references[:1])

    def test_last_lane_malformed_output_is_rejected(self):
        for shape in [[], [["0", "0", "0"] for _ in range(4)]]:
            with self.subTest(shape=shape):
                output = copy.deepcopy(self.output)
                output["samples"][-1]["moments"][-1] = shape
                with self.assertRaisesRegex(ValueError, "malformed"):
                    benchmark.check(output, self.configuration, self.case, self.references)


if __name__ == "__main__":
    unittest.main()

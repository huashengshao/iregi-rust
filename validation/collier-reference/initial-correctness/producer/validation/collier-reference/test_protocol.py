"""Fail-closed checks for the optional external-reference comparison harness."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest


ROOT = Path.cwd()
SPEC = importlib.util.spec_from_file_location("collier_reference_run", ROOT / "validation/collier-reference/run.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.case = runner.kernel.suite([1], ["massive"], [1])[0]
        self.sample = self.case["samples"][0]

    def load(self, case):
        directory = ROOT / "target/collier-reference-tests"
        directory.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as temporary:
            path = Path(temporary) / "inputs.json"
            path.write_text(json.dumps([case]))
            return runner.load_inputs(path)

    def response(self):
        moments = [[[0.0, 0.0] for _ in range(4)] for _ in range(5)]
        moments[0][0] = [0.0, math.pi ** 2]
        for mu, shift in enumerate(self.sample["shifts"][1]):
            moments[mu + 1][0] = [0.0, -math.pi ** 2 * shift / 2]
        return {"id": self.case["id"], "stable": True, "total_ns": [1.0],
                "lanes": [{"status": "success", "moments": moments}],
                "pole_check_errors": [[0.0, 0.0, 0.0]]}

    def test_initial_inputs_are_accepted_without_rewriting(self):
        before = copy.deepcopy(self.case)
        self.assertEqual(self.load(self.case), [self.case])
        self.assertEqual(self.case, before)

    def test_domain_rejects_massless_timelike_translated_and_wrong_mass_branch(self):
        variants = []
        for target, value in [("origin", 1), ("time", 1), ("mass", 0), ("width", 1)]:
            case = copy.deepcopy(self.case)
            sample = case["samples"][0]
            if target == "origin":
                sample["shifts"][0][1] = value
            elif target == "time":
                sample["shifts"][1][0] = value
            elif target == "mass":
                sample["masses"][0][0] = value
            else:
                sample["masses"][0][1] = value
            variants.append(case)
        for case in variants:
            with self.subTest(case=case), self.assertRaises(ValueError):
                self.load(case)

    def test_scale_square_underflow_and_nonfinite_are_rejected(self):
        for value in (0.0, 1e-200, float("nan"), float("inf")):
            case = copy.deepcopy(self.case)
            case["samples"][0]["mu"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.load(case)

    def test_check_request_does_not_change_inputs_or_iregi_mode_mapping(self):
        before = copy.deepcopy(self.case)
        text = runner.collier_request(self.case, [self.sample], 3, 0, 1, check=True)
        self.assertEqual(text.splitlines()[0].split()[:3], ["CHECK", self.case["id"], "3"])
        self.assertEqual(self.case, before)
        original = runner.kernel.fortran_request(self.case, [self.sample], "Hybrid", 0, 1)
        self.assertEqual(original.splitlines()[0].split()[2], "2")

    def test_independent_uv_identities_expose_an_odd_rank_sign_error(self):
        response = self.response()
        self.assertEqual(runner.uv_identities(response, self.case, [self.sample])["status"], "passed")
        response["lanes"][0]["moments"][2][0][1] *= -1
        self.assertEqual(runner.uv_identities(response, self.case, [self.sample])["status"], "failed")

    def test_complete_array_comparison_rejects_missing_native_slots(self):
        expected = self.response()
        actual = copy.deepcopy(expected)
        actual["lanes"][0]["moments"][0].pop()
        self.assertEqual(runner.comparison(actual, expected, self.case, [self.sample])["status"], "failed")

    def test_pole_probes_reject_missing_nonfinite_and_nonzero_ir(self):
        response = self.response()
        runner.validate_poles(response, [self.sample])
        for value in (None, [], [[0, 0]], [[0, float("nan"), 0]], [[0, 1e-9, 0]]):
            response["pole_check_errors"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                runner.validate_poles(response, [self.sample])

    def test_failed_lane_cannot_validate_as_successful_zero(self):
        expected = self.response()
        actual = copy.deepcopy(expected)
        actual["stable"] = False
        actual["lanes"][0] = {"status": "unstable", "moments": None}
        self.assertEqual(runner.comparison(actual, expected, self.case, [self.sample])["status"], "failed")


if __name__ == "__main__":
    unittest.main()

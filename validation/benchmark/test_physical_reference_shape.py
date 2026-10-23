"""MadLoop comparison boundary tests; no Rust, Fortran, or Symbolica execution."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path.cwd() / "validation/physical"))
import compare_cli as physical  # noqa: E402


class PhysicalReferenceShapeTests(unittest.TestCase):
    def setUp(self):
        self.sample = json.loads(Path("validation/physical/ggh-cli-input.json").read_text())
        self.case = physical.CASES["ggh"]
        # Distinct exact values exercise the finite/UV+IR/double-pole map and
        # the graph's -1/2 factor independently of a tensor-reduction result.
        self.output = {"samples": [{"integral": [[1, 2], [3, 4], [5, 6], [7, 8]]}]}
        self.reference = {
            "selected_feynkit_group": 41,
            "records": [
                {"group": 40, "stable": False, "raw_result": []},
                {"group": 41, "stable": True,
                 "raw_result": [[-14, -16], [-8, -12], [-10, -12]]},
            ],
        }

    def compare(self, reference=None):
        return physical.compare_physical(
            self.output, self.sample,
            self.reference if reference is None else reference, self.case, 1e-10,
        )

    def test_selected_group_factor_and_all_laurent_slots_correspond(self):
        result = self.compare()
        self.assertTrue(result["passed"])
        self.assertEqual(result["group"], 41)
        self.assertEqual(result["factor"], "-1/2")
        self.assertEqual(result["laurent_order"], ["finite", "single_pole", "double_pole"])
        self.assertEqual(result["actual_raw"], [[7, 8], [4, 6], [5, 6]])
        self.assertEqual(result["expected_raw"], result["actual_raw"])
        self.assertEqual(result["errors"], [0, 0, 0])

    def test_each_reference_laurent_slot_is_compared(self):
        for slot in range(3):
            with self.subTest(slot=slot):
                reference = copy.deepcopy(self.reference)
                reference["records"][1]["raw_result"][slot][0] += 1
                self.assertFalse(self.compare(reference)["passed"])

    def test_missing_short_long_and_nonarray_results_are_rejected(self):
        valid = self.reference["records"][1]["raw_result"]
        for raw_result in [None, {}, "123", [], valid[:1], valid[:2], valid + [[0, 0]]]:
            with self.subTest(raw_result=raw_result):
                reference = copy.deepcopy(self.reference)
                reference["records"][1]["raw_result"] = raw_result
                with self.assertRaisesRegex(ValueError, "exactly three Laurent"):
                    self.compare(reference)
        reference = copy.deepcopy(self.reference)
        del reference["records"][1]["raw_result"]
        with self.assertRaisesRegex(ValueError, "exactly three Laurent"):
            self.compare(reference)

    def test_malformed_complex_pairs_are_rejected_in_every_slot(self):
        for slot in range(3):
            for value in [None, 0, "12", {}, [], [0], [0, 0, 0],
                          [None, 0], [{}, 0], ["not-a-number", 0], [True, 0]]:
                with self.subTest(slot=slot, value=value):
                    reference = copy.deepcopy(self.reference)
                    reference["records"][1]["raw_result"][slot] = value
                    with self.assertRaisesRegex(ValueError, "MadLoop Laurent coefficients"):
                        self.compare(reference)

    def test_nonfinite_real_and_imaginary_components_are_rejected(self):
        for slot in range(3):
            for component in range(2):
                for value in [float("nan"), float("inf"), float("-inf"),
                              "NaN", "Infinity", "-Infinity", "1e10000"]:
                    with self.subTest(slot=slot, component=component, value=value):
                        reference = copy.deepcopy(self.reference)
                        reference["records"][1]["raw_result"][slot][component] = value
                        with self.assertRaisesRegex(ValueError, "finite complex values"):
                            self.compare(reference)

    def test_all_retained_physical_fixtures_keep_their_valid_shape(self):
        # This checks acceptance of the actual retained reference assets and
        # normalization, not independent numerical agreement with Rust.
        for name, case in physical.CASES.items():
            with self.subTest(case=name):
                reference = json.loads(Path(
                    f"validation/physical/madloop/fixtures/{name}-helicity-1.json"
                ).read_text())
                sample = json.loads(Path(f"validation/physical/{name}-cli-input.json").read_text())
                record = next(record for record in reference["records"]
                              if record["group"] == reference["selected_feynkit_group"])
                finite, single, double = [case[2] * physical.number(value)
                                          for value in record["raw_result"]]
                output = {"samples": [{"integral": [
                    [0, 0], physical.pair(single), physical.pair(double), physical.pair(finite),
                ]}]}
                result = physical.compare_physical(output, sample, reference, case, 1e-10)
                self.assertTrue(result["passed"])
                self.assertEqual(result["errors"], [0, 0, 0])


if __name__ == "__main__":
    unittest.main()

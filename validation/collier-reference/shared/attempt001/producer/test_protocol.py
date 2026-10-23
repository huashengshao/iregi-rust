"""Meaningful input, routing, status and complete-output protocol regressions."""
import copy
from fractions import Fraction
import json
import math
from pathlib import Path
import tempfile
import unittest

import support
import run_correctness as runner


ROOT = Path.cwd()


class SharedProtocolTests(unittest.TestCase):
    def setUp(self):
        self.case = {"id": "n7-r2-test", "n": 7, "rank": 2, "powers": [1]*7, "dimension_shift": 0}
        self.sample = {"mu": "3", "shifts": [["0"]*4 for _ in range(7)], "masses": [["2", "0"] for _ in range(7)]}
        self.sample["shifts"][4][0] = "1/2"

    def response(self, *, accepted=True):
        moments = [[[0., 0.] for _ in range(4)] for _ in range(15)]
        lane = {"status": "success" if accepted else "unstable", "moments": moments if accepted else None,
                "last_err_flag": 0, "last_acc_flag": 0 if accepted else -1,
                "worst_err_flag": 0, "worst_acc_flag": 0 if accepted else -1}
        if not accepted:
            lane["diagnostic_moments"] = moments
        return {"id": self.case["id"], "stable": accepted, "lanes": [lane], "total_ns": [1.]}

    def test_even_and_odd_invariant_order_reproduces_old_wrappers(self):
        self.assertEqual(support.invariant_pairs(2), [(0, 1)])
        self.assertEqual(support.invariant_pairs(3), [(0, 1), (1, 2), (2, 0)])
        self.assertEqual(support.invariant_pairs(4), [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)])
        self.assertEqual(support.invariant_pairs(5), [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
                                                   (0, 2), (1, 3), (2, 4), (3, 0), (4, 1)])

    def test_higher_invariant_series_covers_each_unordered_pair_once(self):
        for n in (5, 6, 7):
            pairs = support.invariant_pairs(n)
            self.assertEqual(len(pairs), n*(n-1)//2)
            self.assertEqual({tuple(sorted(p)) for p in pairs}, {(a, b) for a in range(n) for b in range(a+1, n)})

    def test_frozen_initial_and_n4_inputs_transport_without_numeric_change(self):
        for path in (ROOT/"validation/benchmark/baseline-6b24c03-licensed/results-inputs.json",
                     ROOT/"validation/collier-reference/extensions/n4-inputs.json"):
            cases = json.loads(path.read_text())
            before = copy.deepcopy(cases)
            for case in cases:
                for sample in case["samples"]:
                    self.assertEqual(support.wire_sample(sample, case["n"]), sample)
            self.assertEqual(cases, before)

    def test_distinguishable_beyond53bit_input_cannot_silently_round(self):
        self.assertEqual(support.binary64("9007199254740992"), 9007199254740992.)
        with self.assertRaises(ValueError):
            support.binary64("9007199254740993")

    def test_nondyadic_and_nonfinite_reference_inputs_are_explicitly_rejected(self):
        for value in ("1/3", "1e1000", "nan", float("inf"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                support.binary64(value)

    def test_nonzero_time_is_preserved_and_sample_is_immutable(self):
        before = copy.deepcopy(self.sample)
        wire = support.wire_sample(self.sample, 7)
        self.assertEqual(wire["shifts"][4][0], .5)
        self.assertEqual(self.sample, before)

    def test_unsupported_mass_routing_scale_and_extra_fields_are_rejected(self):
        variants = []
        sample = copy.deepcopy(self.sample); sample["shifts"][0][0] = "1"; variants.append(sample)
        sample = copy.deepcopy(self.sample); sample["masses"][0][0] = "0"; variants.append(sample)
        sample = copy.deepcopy(self.sample); sample["masses"][0][1] = "-1"; variants.append(sample)
        sample = copy.deepcopy(self.sample); sample["mu"] = "1e-200"; variants.append(sample)
        sample = copy.deepcopy(self.sample); sample["powers"] = [1]*7; variants.append(sample)
        for sample in variants:
            with self.subTest(sample=sample), self.assertRaises(ValueError):
                support.exact_sample(sample, 7)

    def test_powers_dimension_and_interface_limits_are_not_silently_ignored(self):
        variants = []
        for key, value in (("powers", [1]*6+[2]), ("powers", [1]*6), ("dimension_shift", 2),
                           ("dimension_shift", False), ("n", 8), ("rank", -1)):
            case = copy.deepcopy(self.case); case[key] = value; variants.append(case)
        for case in variants:
            with self.subTest(case=case), self.assertRaises(ValueError):
                support.original_iregi_request(case, [self.sample], "Hybrid")

    def test_requests_preserve_native_mode_numbering_and_explicit_policies(self):
        before = copy.deepcopy(self.sample)
        original = support.original_iregi_request(self.case, [self.sample], "Hybrid")
        self.assertEqual(original.splitlines()[0].split()[:5], ["BENCH", self.case["id"], "2", "7", "2"])
        collier = support.collier_request(self.case, [self.sample], 1)
        self.assertEqual(collier.splitlines()[0].split()[:5], ["CHECK", self.case["id"], "1", "7", "2"])
        with self.assertRaises(ValueError):
            support.collier_request(self.case, [self.sample], 3)
        self.assertEqual(self.sample, before)

    def test_uv_finiteness_checks_every_requested_component(self):
        response = self.response()
        wire = [support.wire_sample(self.sample, 7)]
        self.assertEqual(runner.uv_check(response, self.case, wire)["status"], "passed")
        response["lanes"][0]["moments"][-1][0] = [1., 0.]
        self.assertEqual(runner.uv_check(response, self.case, wire)["status"], "failed")

    def test_incomplete_laurent_arrays_cannot_compare_successfully(self):
        expected = self.response()
        actual = copy.deepcopy(expected)
        actual["lanes"][0]["moments"][-1].pop()
        self.assertEqual(support.common.comparison(actual, expected, self.case,
                                                  [support.wire_sample(self.sample, 7)])["status"], "failed")

    def test_rejected_raw_agreement_is_not_native_acceptance(self):
        response = self.response(accepted=False)
        expected = self.response()
        wire = [support.wire_sample(self.sample, 7)]
        raw = runner.diagnose.diagnostic_comparison(response, expected, self.case, wire)
        self.assertEqual(raw["raw_numeric_agreement"]["status"], "passed")
        self.assertIs(raw["qualifies"], False)
        self.assertEqual(support.common.comparison(response, expected, self.case, wire)["status"], "failed")
        self.assertIsNone(response["lanes"][0]["moments"])

    def test_wrapper_regression_preserves_rejection_and_compares_flags(self):
        generic = self.response(accepted=False)
        wrapped = copy.deepcopy(generic)
        wire = [support.wire_sample(self.sample, 7)]
        result = runner.interface_agreement(generic, wrapped, self.case, wire)
        self.assertEqual(result["status"], "passed")
        self.assertIs(result["raw_array_comparison"]["qualifies"], False)
        generic["lanes"][0]["worst_acc_flag"] = -2
        self.assertEqual(runner.interface_agreement(generic, wrapped, self.case, wire)["status"], "failed")
        fixed = [{"n": 4, "iregi_frozen_regression": {"status": "passed"},
                  "collier_policies": {str(mode): {"old_wrapper_regression": {"status": "passed"}}
                                       for mode in (1, 2)}} for _ in range(16)]
        self.assertTrue(runner.fixed_interfaces_ready(fixed))
        self.assertFalse(runner.fixed_interfaces_ready(fixed[:-1]))
        fixed[0]["collier_policies"]["1"]["old_wrapper_regression"]["status"] = "failed"
        self.assertFalse(runner.fixed_interfaces_ready(fixed))

    def test_missing_exact_domain_witness_is_rejected_before_execution(self):
        document = {"status": "prepared-not-numerically-qualified", "guards_unchanged": True,
                    "cases": [{**self.case, "samples": [self.sample]*32}], "sample_domain_proofs": {}}
        directory = ROOT/"target/collier-shared-protocol-tests"
        directory.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as temporary:
            path = Path(temporary)/"inputs.json"
            path.write_text(json.dumps(document))
            with self.assertRaisesRegex(ValueError, "missing positive exact"):
                support.load_document(path)


if __name__ == "__main__":
    unittest.main()

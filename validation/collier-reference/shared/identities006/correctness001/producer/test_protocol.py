"""Actual prepared/saved-data admission tests; no CLI or reference processes."""
import copy
import gzip
import json
import unittest

import protocol


class IdentityProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = protocol.HERE/"prepared001/preparation.json.gz"
        cls.prepared = json.loads(gzip.decompress(path.read_bytes()))
        cls.parent = json.loads(gzip.decompress((protocol.PARENT/"capture.json.gz").read_bytes()))

    def test_actual_symbolica_preparation_admits_exact46_requests(self):
        cases = protocol.admit(copy.deepcopy(self.prepared))
        self.assertEqual(len(cases), 7)
        loaded, parent, loaded_cases = protocol.load_prepared()
        self.assertEqual(len(loaded["reference_request_inventory"]), 46)
        self.assertEqual(len(parent["rows"]), 34)

    def test_actual_symbolica_metric_and_all_cancellation_witnesses(self):
        trace = protocol.polynomial(self.prepared, self.prepared["aliases"]["metric-trace-rank2"])
        observed = {tuple(t["exponents"]): protocol.support.exact_number(t["coefficient"]) for t in trace["terms"]}
        self.assertEqual(observed, {(2, 0, 0, 0): 1, (0, 2, 0, 0): -1, (0, 0, 2, 0): -1, (0, 0, 0, 2): -1})
        for label, expression in self.prepared["aliases"].items():
            if "cancellation" in label:
                self.assertEqual(protocol.polynomial(self.prepared, expression)["terms"], [])

    def test_omitted_duplicate_or_changed_wire_request_is_rejected(self):
        mutations = [lambda d: d["reference_request_inventory"].pop(),
                     lambda d: d["reference_request_inventory"].__setitem__(1, copy.deepcopy(d["reference_request_inventory"][0])),
                     lambda d: d["reference_request_inventory"][0].__setitem__("wire_request", "different input\n")]
        for mutate in mutations:
            changed = copy.deepcopy(self.prepared)
            mutate(changed)
            with self.assertRaises(ValueError):
                protocol.admit(changed)

    def test_changed_branch_domain_or_original_lane_order_is_rejected(self):
        mutations = [lambda d: d["original32_proof_keys"].reverse(),
                     lambda d: d["branches"][0]["parent_domain_proof"].__setitem__("positive_mass_polynomial_lower_bound", "0"),
                     lambda d: d["branches"][0].__setitem__("proof_key", "different-branch")]
        for mutate in mutations:
            changed = copy.deepcopy(self.prepared)
            mutate(changed)
            with self.assertRaises(ValueError):
                protocol.admit(changed)

    def test_pinch_translation_mass_scale_and_rank_are_bound(self):
        mutations = [lambda d: d["pinched_cases"][0]["samples"][0]["shifts"][0].__setitem__(0, "1"),
                     lambda d: d["pinched_cases"][0]["samples"][0]["masses"].reverse(),
                     lambda d: d["pinched_cases"][0]["samples"][0].__setitem__("mu", "12"),
                     lambda d: d["pinched_cases"][0].__setitem__("rank", 2)]
        for mutate in mutations:
            changed = copy.deepcopy(self.prepared)
            mutate(changed)
            with self.assertRaises(ValueError):
                protocol.admit(changed)

    def test_routing_order_and_missing_family_cannot_pass(self):
        for mutate in (lambda d: d["routing_cases"][0]["denominator_order"].reverse(),
                       lambda d: d["routing_cases"].pop()):
            changed = copy.deepcopy(self.prepared)
            mutate(changed)
            with self.assertRaises(ValueError):
                protocol.admit(changed)

    def test_real_native_rejection_diagnostics_cannot_be_used_as_accepted_moments(self):
        actual = next(r for r in self.parent["rows"] if r["n"] == 6 and r["rank"] == 1 and r["batch_width"] == 1)
        response = actual["responses"]["generic-1"]
        self.assertIsNotNone(response["lanes"][0]["diagnostic_moments"])
        self.assertIsNone(response["lanes"][0]["moments"])
        with self.assertRaisesRegex(ValueError, "native lane rejected"):
            protocol.accepted_moments(response, 0, 1)

    def test_complete_arrays_flags_and_poles_required_for_every_accepted_lane(self):
        actual = next(r for r in self.parent["rows"] if r["n"] == 5 and r["rank"] == 2 and r["batch_width"] == 1)
        response = actual["responses"]["generic-1"]
        self.assertEqual(len(protocol.accepted_moments(response, 0, 2)), 15)
        mutations = [lambda r: r["lanes"][0]["moments"][-1].pop(),
                     lambda r: r["lanes"][0]["moments"][-1].__setitem__(3, None),
                     lambda r: r["lanes"][0].__setitem__("worst_acc_flag", -1),
                     lambda r: r["lanes"][0].pop("last_err_flag"),
                     lambda r: r["pole_check_errors"][0].__setitem__(0, 1.),
                     lambda r: r["lanes"][0]["moments"][-1][3].__setitem__(0, float("nan"))]
        for mutate in mutations:
            changed = copy.deepcopy(response)
            mutate(changed)
            with self.assertRaises(ValueError):
                protocol.accepted_moments(changed, 0, 2)


if __name__ == "__main__":
    unittest.main()

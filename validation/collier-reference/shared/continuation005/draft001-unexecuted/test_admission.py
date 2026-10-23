"""Saved-data admission tests; these tests never construct a reference child."""
import copy
import gzip
import json
from pathlib import Path
import unittest

import append


class SavedAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads((append.HERE/"inventory.json").read_text())
        cls.parent = json.loads(gzip.decompress((append.ROOT/cls.inventory["parent_capture"]["path"]).read_bytes()))

    def inputs(self):
        return copy.deepcopy(self.parent), copy.deepcopy(self.inventory)

    def test_actual_saved_parent_admits_exact_pending_set_and_all34_rows(self):
        parent, inventory = self.inputs()
        before = copy.deepcopy(parent)
        case, row, groups = append.admit_structure(parent, inventory)
        self.assertEqual(case["n"], 7)
        self.assertEqual(case["rank"], 2)
        self.assertEqual(row["batch_width"], 32)
        self.assertEqual([len(g["samples"]) for g in groups], [22, 10])
        self.assertEqual(parent, before)

    def test_actual_durable_bindings_and_frozen_sources_are_verified_without_children(self):
        inventory, parent, case, row, groups = append.load_admitted(append.HERE/"inventory.json")
        self.assertEqual(len(inventory["remaining_group_requests"]), 8)
        self.assertEqual(len(parent["rows"]), 34)

    def test_completed_request_cannot_be_reclassified_for_retry(self):
        parent, inventory = self.inputs()
        attempt = next(a for r in parent["rows"] for values in r["request_attempts"].values()
                       for a in values if a["status"] == "validated-response")
        attempt["status"] = "not_run"
        with self.assertRaisesRegex(ValueError, "239 completed/eight"):
            append.admit_structure(parent, inventory)

    def test_duplicate_or_completed_policy_inventory_is_rejected(self):
        for replacement in (copy.deepcopy(self.inventory["remaining_group_requests"][0]),
                            {**self.inventory["remaining_group_requests"][0], "response_key": "iregi-Hybrid", "mode": "Hybrid"}):
            parent, inventory = self.inputs()
            inventory["remaining_group_requests"][1] = replacement
            with self.assertRaises(ValueError):
                append.admit_structure(parent, inventory)

    def test_omitted_or_replaced_family_row_cannot_hide_a_failure(self):
        for mutate in (lambda rows: rows.pop(0), lambda rows: rows.__setitem__(0, copy.deepcopy(rows[1]))):
            parent, inventory = self.inputs()
            mutate(parent["rows"])
            with self.assertRaisesRegex(ValueError, "all17 families"):
                append.admit_structure(parent, inventory)

    def test_lane_order_scale_proof_and_wire_are_bound(self):
        mutations = [lambda a: a["lane_indices"].reverse(), lambda a: a.__setitem__("scale", "4"),
                     lambda a: a["input_proof_keys"].__setitem__(0, "different-input"),
                     lambda a: a.__setitem__("wire_request", a["wire_request"].replace(" 7 2 ", " 7 3 "))]
        for mutate in mutations:
            parent, inventory = self.inputs()
            mutate(inventory["remaining_group_requests"][0])
            with self.assertRaises((ValueError, StopIteration)):
                append.admit_structure(parent, inventory)

    def test_parent_binary_source_and_rank_cannot_change(self):
        mutations = [lambda p, i: i["binaries"]["generic"].__setitem__("sha256", "0"*64),
                     lambda p, i: i["source_binary_input_guards"].clear(),
                     lambda p, i: i.__setitem__("rank", 3)]
        for mutate in mutations:
            parent, inventory = self.inputs()
            mutate(parent, inventory)
            with self.assertRaises(ValueError):
                append.admit_structure(parent, inventory)

    def test_changed_existing_hybrid_or_parent_guard_is_rejected(self):
        parent, inventory = self.inputs()
        row = next(r for r in parent["rows"] if r["id"] == inventory["family"] and r["batch_width"] == 32)
        row["responses"]["generic-1"] = row["responses"]["iregi-Hybrid"]
        with self.assertRaisesRegex(ValueError, "Hybrid"):
            append.admit_structure(parent, inventory)
        parent, inventory = self.inputs()
        parent["guards_unchanged"] = False
        with self.assertRaisesRegex(ValueError, "guarded parent"):
            append.admit_structure(parent, inventory)


if __name__ == "__main__":
    unittest.main()

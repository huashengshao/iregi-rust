"""Admission controls only; synthetic timings are never benchmark measurements."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from replay_parser import FIRST_VARIANTS, validate_rows


def fixtures():
    capture = json.loads((Path(__file__).parent / "capture-results.json").read_text())
    rows = []
    for original in capture["rows"]:
        groups = []
        outputs = []
        for expected in original["capture"]["master_captures"]:
            groups.append({"family": expected["family"], "rows": expected["rows"],
                           "complex_outputs": 6 * expected["rows"], "max_normalized_error": 0.,
                           "represented_component_differences": 0, "signed_zero_differences": 0,
                           "symbolica_matches_public_capture_exactly": True, "native_cells": 0})
            outputs.append([[[0, 0] for _ in range(6 * expected["rows"])] for _ in range(2)])
        timing = {"protocol": "actual-master-replay-fixed-loop-v1", "pilot_target_ns": 2_000_000,
                  "block_target_ns": 30_000_000, "pair_order_seed": 173,
                  "pair_order_algorithm": "Python random.Random(seed).shuffle([0]*11+[1]*10)",
                  "pilots": [[8, 2_000_000], [8, 2_000_000]], "iterations": 120,
                  "blocks": [{"block": index, "order": [first, 1 - first], "iterations": 120,
                              "elapsed_ns": [30_000_000, 30_000_000]}
                             for index, first in enumerate(FIRST_VARIANTS)], "postcheck": deepcopy(groups)}
        rows.append({"id": original["id"], "outer_batch": original["outer_batch"], "status": "passed",
                     "mode": "timing", "native_context_preparation_ns": 0,
                     "result": {"preparation_ns": 0, "groups": groups,
                                "represented_outputs": outputs, "timing": timing}})
    return rows, capture


class Admission(unittest.TestCase):
    def test_complete_protocol(self):
        rows, capture = fixtures()
        validate_rows(rows, capture, True)
        for row in rows:
            row["mode"] = "qualification"
            row["result"]["timing"] = None
        validate_rows(rows, capture, False)

    def test_malformed_controls(self):
        # Each mutation must be rejected independently, even when all other rows pass.
        changes = [
            ("pilot boolean", ["result", "timing", "pilots", 0, 0], True),
            ("pilot float", ["result", "timing", "pilots", 0, 0], 8.),
            ("pilot too small", ["result", "timing", "pilots", 0, 0], 4),
            ("pilot too big", ["result", "timing", "pilots", 0, 0], 1 << 27),
            ("pilot nonpower", ["result", "timing", "pilots", 0, 0], 12),
            ("pilot premature", ["result", "timing", "pilots", 0, 1], 1_999_999),
            ("pilot elapsed boolean", ["result", "timing", "pilots", 0, 1], True),
            ("exact truthy", ["result", "groups", 0, "symbolica_matches_public_capture_exactly"], "true"),
            ("difference boolean", ["result", "groups", 0, "represented_component_differences"], False),
            ("difference fractional", ["result", "groups", 0, "represented_component_differences"], .5),
            ("difference exceeds bound", ["result", "groups", 0, "represented_component_differences"], 10**9),
            ("sign exceeds changes", ["result", "groups", 0, "signed_zero_differences"], 1),
            ("error nan", ["result", "groups", 0, "max_normalized_error"], float("nan")),
            ("error infinity", ["result", "groups", 0, "max_normalized_error"], float("inf")),
            ("error boolean", ["result", "groups", 0, "max_normalized_error"], False),
            ("iteration float", ["result", "timing", "iterations"], 120.),
            ("wrong shared iterations", ["result", "timing", "iterations"], 121),
            ("elapsed boolean", ["result", "timing", "blocks", 0, "elapsed_ns", 0], True),
            ("elapsed zero", ["result", "timing", "blocks", 0, "elapsed_ns", 0], 0),
            ("block index boolean", ["result", "timing", "blocks", 0, "block"], False),
            ("order boolean", ["result", "timing", "blocks", 0, "order", 0], False),
            ("wrong order", ["result", "timing", "blocks", 0, "order"], [1, 0]),
            ("wrong seed", ["result", "timing", "pair_order_seed"], 172),
            ("nonfinite output", ["result", "represented_outputs", 0, 0, 0, 0], 0x7ff0000000000000),
            ("boolean output", ["result", "represented_outputs", 0, 0, 0, 0], False),
            ("postcheck truthy", ["result", "timing", "postcheck", 0, "symbolica_matches_public_capture_exactly"], 1),
            ("postcheck boolean count", ["result", "timing", "postcheck", 0, "represented_component_differences"], False),
            ("failed row", ["status"], "failed"),
            ("wrong row coordinate", ["outer_batch"], 33),
        ]
        for label, path, value in changes:
            rows, capture = fixtures()
            item = rows[0]
            for key in path[:-1]:
                item = item[key]
            item[path[-1]] = value
            with self.subTest(label=label), self.assertRaises(AssertionError):
                validate_rows(rows, capture, True)
        for mutation in [lambda rows: rows.pop(), lambda rows: rows.__setitem__(1, deepcopy(rows[0]))]:
            rows, capture = fixtures()
            mutation(rows)
            with self.assertRaises(AssertionError):
                validate_rows(rows, capture, True)


if __name__ == "__main__":
    unittest.main()

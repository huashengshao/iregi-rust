"""Synthetic admission regressions only; no kernels or benchmark measurements.

Every analysis runs in a disposable directory below this file's directory.
The statistics helper deliberately fails if admission reaches measurement.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
from replay_parser import FIRST_VARIANTS, validate_rows

BASE = Path(__file__).resolve().parent
LABEL = "SYNTHETIC ADMISSION FIXTURE; NOT BENCHMARK MEASUREMENTS"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def synthetic_records():
    capture = {"fixture_kind": LABEL, "rows": []}
    rows = []
    for n in (2, 3):
        for rank in (0, 1):
            for width in (1, 32):
                families = {
                    (2, 0): [("B0", width)],
                    (2, 1): [("B0", width), ("A0", 2 * width)],
                    (3, 0): [("C0", width)],
                    (3, 1): [("C0", width), ("B0", 3 * width)],
                }[(n, rank)]
                identity = {"id": f"n{n}-r{rank}-massive", "outer_batch": width}
                expected = [{"family": family, "rows": count} for family, count in families]
                capture["rows"].append(identity | {"capture": {"master_captures": expected}})
                groups = [group | {
                    "complex_outputs": 6 * group["rows"], "max_normalized_error": 0.0,
                    "represented_component_differences": 0, "signed_zero_differences": 0,
                    "symbolica_matches_public_capture_exactly": True, "native_cells": 0,
                } for group in expected]
                outputs = [[[[0, 0] for _ in range(6 * group["rows"])] for _ in range(2)]
                           for group in expected]
                timing = {
                    "protocol": "actual-master-replay-fixed-loop-v1",
                    "pilot_target_ns": 2_000_000, "block_target_ns": 30_000_000,
                    "pair_order_seed": 173,
                    "pair_order_algorithm": "Python random.Random(seed).shuffle([0]*11+[1]*10)",
                    "pilots": [[8, 2_000_000], [8, 2_000_000]], "iterations": 120,
                    "blocks": [{"block": index, "order": [first, 1 - first],
                                "iterations": 120, "elapsed_ns": [30_000_000, 30_000_000]}
                               for index, first in enumerate(FIRST_VARIANTS)],
                    "postcheck": deepcopy(groups),
                }
                rows.append(identity | {
                    "fixture_kind": LABEL, "status": "passed", "mode": "timing",
                    "native_context_preparation_ns": 0,
                    "result": {"preparation_ns": 0, "groups": groups,
                               "represented_outputs": outputs, "timing": timing},
                })
    # This inexpensive positive control runs admission only, never statistics.
    validate_rows(rows, capture, True)
    return rows, capture


class AnalyzerAdmission(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="synthetic-analyzer-admission-", dir=BASE)
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        for name in ("analyze_replay.py", "replay_parser.py", "run_replay.py"):
            shutil.copyfile(BASE / name, self.directory / name)
        helper = self.directory / "benchmark_helper.py"
        helper.write_text(
            '"""Synthetic admission sentinel; never computes benchmark statistics."""\n'
            'def forbidden(*args, **kwargs):\n'
            '    raise AssertionError("SYNTHETIC FIXTURE reached statistics")\n'
            'summarize = ratio_summary = forbidden\n'
        )
        write_json(self.directory / "statistics-source.json",
                   {"scope": LABEL, "sha256": digest(helper)})
        self.rows, self.capture = synthetic_records()
        write_json(self.directory / "capture-results.json", self.capture)
        (self.directory / "replay-timing.jsonl").write_text(
            "".join(json.dumps(row, allow_nan=False) + "\n" for row in self.rows)
        )
        write_json(self.directory / "replay-qualification-initial.json", {"fixture_kind": LABEL})
        self.run = {
            "fixture_kind": LABEL, "status": "passed", "initial_outputs_bitwise_unchanged": True,
            "jsonl_sha256": digest(self.directory / "replay-timing.jsonl"),
            "capture_sha256": digest(self.directory / "capture-results.json"),
            "parser_sha256": digest(self.directory / "replay_parser.py"),
            "runner_sha256": digest(self.directory / "run_replay.py"),
            "initial_qualification_sha256": digest(self.directory / "replay-qualification-initial.json"),
        }
        write_json(self.directory / "replay-timing.json", self.run)

    def assert_unqualified(self):
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, "-B", str(self.directory / "analyze_replay.py")],
            cwd=BASE.parent.parent, env=environment, text=True, capture_output=True, timeout=15,
        )
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        path = self.directory / "replay-timing-summary.json"
        self.assertTrue(path.is_file(), completed.stdout + completed.stderr)
        summary = json.loads(path.read_text())
        self.assertEqual(summary["status"], "unqualified")
        self.assertEqual(summary["gates"], {"unqualified": 8})
        self.assertEqual(len(summary["rows"]), 8)
        self.assertEqual(
            [(row["id"], row["outer_batch"]) for row in summary["rows"]],
            [(row["id"], row["outer_batch"]) for row in self.capture["rows"]],
        )
        for row in summary["rows"]:
            self.assertEqual(row["status"], "unqualified")
            self.assertIsNone(row["ratio"])
            self.assertIn("error", row)
            self.assertNotIn("order_strata", row)
        self.assertNotIn("SYNTHETIC FIXTURE reached statistics", completed.stderr)
        return summary

    def test_truncated_jsonl_retains_every_case(self):
        path = self.directory / "replay-timing.jsonl"
        path.write_text(json.dumps(self.rows[0]) + '\n{"id":')
        # Keep the raw hash valid: this must exercise JSON parsing, not a stale hash.
        self.run["jsonl_sha256"] = digest(path)
        write_json(self.directory / "replay-timing.json", self.run)
        summary = self.assert_unqualified()
        self.assertTrue(all("Expecting" in row["error"] for row in summary["rows"]))

    def test_changed_capture_hash_retains_every_case(self):
        self.capture["synthetic_metadata_changed_after_run"] = True
        write_json(self.directory / "capture-results.json", self.capture)
        self.assert_unqualified()

    def test_changed_parser_hash_retains_every_case(self):
        with (self.directory / "replay_parser.py").open("a") as stream:
            stream.write("\n# SYNTHETIC harmless source change after recorded run.\n")
        self.assert_unqualified()


if __name__ == "__main__":
    print(LABEL, flush=True)
    unittest.main(verbosity=2)

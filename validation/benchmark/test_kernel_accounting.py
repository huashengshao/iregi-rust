"""Kernel benchmark interruption accounting; no numerical subprocesses."""
import sys
import unittest

sys.dont_write_bytecode = True
import run as kernel


class KernelAccountingTests(unittest.TestCase):
    def rows(self):
        cases = [{"id": "bubble", "n": 2, "rank": 1, "mass_class": "massive"},
                 {"id": "triangle", "n": 3, "rank": 2, "mass_class": "complex"}]
        return kernel.configuration_rows(cases, [1, 32], "Hybrid", "PassarinoVeltman")

    def test_interrupt_between_rows_preserves_all_requested_workloads(self):
        data = {"rows": self.rows()}
        data["rows"][0]["status"] = "measured"
        kernel.finalize_rows(data, False)
        self.assertEqual(data["status"], "interrupted")
        self.assertEqual([row["status"] for row in data["rows"]],
                         ["measured", "not_run", "not_run", "not_run"])
        self.assertEqual([(row["id"], row["batch_width"]) for row in data["rows"]],
                         [("bubble", 1), ("bubble", 32), ("triangle", 1), ("triangle", 32)])
        self.assertTrue(all(row["reference_mode"] == "PassarinoVeltman" for row in data["rows"]))

    def test_interrupted_running_row_retains_partial_evidence(self):
        data = {"rows": self.rows()}
        data["rows"][0].update(status="running", correctness={"status": "passed"})
        kernel.finalize_rows(data, False)
        self.assertEqual(data["rows"][0]["status"], "interrupted")
        self.assertEqual(data["rows"][0]["correctness"], {"status": "passed"})
        self.assertEqual(data["status"], "interrupted")

    def test_completion_requires_nonempty_fully_attempted_work(self):
        for rows in [[], self.rows()]:
            with self.subTest(rows=rows):
                data = {"rows": rows}
                kernel.finalize_rows(data, True)
                self.assertEqual(data["status"], "interrupted")
        data = {"rows": self.rows()}
        for row, status in zip(data["rows"], ["measured", "timeout", "unsupported", "correctness-failed"]):
            row["status"] = status
        kernel.finalize_rows(data, True)
        self.assertEqual(data["status"], "complete")
        self.assertEqual([row["status"] for row in data["rows"]],
                         ["measured", "timeout", "unsupported", "correctness-failed"])


if __name__ == "__main__":
    unittest.main()

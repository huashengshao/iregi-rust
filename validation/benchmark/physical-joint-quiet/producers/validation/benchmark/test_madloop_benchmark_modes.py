"""Verify benchmark algorithm provenance without executing the numerical tools."""
import argparse
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


folder = Path.cwd() / "validation/physical/madloop"
capture = load("madloop_mode_capture", folder / "run.py")
with patch.dict(sys.modules, {"run": capture}):
    benchmark = load("madloop_mode_benchmark", folder / "benchmark.py")


class MadLoopBenchmarkModeTests(unittest.TestCase):
    def test_actual_call_modes_identify_hybrid_without_reversal(self):
        result = benchmark.observed_modes(
            "unrelated output\n IREGI_BENCH_MODES           1           2\n"
        )
        self.assertEqual(result, {"ctmode": 1, "iregimode": 2, "algorithm": "Hybrid"})

    def test_missing_duplicate_and_malformed_records_fail(self):
        for text in ["", "IREGI_BENCH_MODES\n", "IREGI_BENCH_MODES 1\n",
                     "IREGI_BENCH_MODES 1 2 3\n", "IREGI_BENCH_MODES a b\n",
                     "IREGI_BENCH_MODES 1 2\nIREGI_BENCH_MODES 1 2\n"]:
            with self.subTest(text=text), self.assertRaises(RuntimeError):
                benchmark.observed_modes(text)

    def test_other_algorithms_and_reversed_routing_cannot_be_labeled_hybrid(self):
        for ctmode, iregimode in [(1, 0), (1, 1), (2, 2), (4, 2), (1, 9)]:
            with self.subTest(ctmode=ctmode, iregimode=iregimode):
                with self.assertRaisesRegex(RuntimeError, "unexpected benchmark call modes"):
                    benchmark.observed_modes(f"IREGI_BENCH_MODES {ctmode} {iregimode}\n")

    def test_generated_timer_exports_and_checks_the_actual_arguments(self):
        args = argparse.Namespace(batch_widths=[1, 3], n_groups=2, repeats=3,
                                  warmup=0, target_ms=0.1)
        source = benchmark.timer_source("ML5_0_", 1, args)
        emission = source.index("'IREGI_BENCH_MODES',CTMODE,IMODE")
        check = source.index("IF(CTMODE.NE.1.OR.IMODE.NE.2) STOP 26")
        timer = source.index("CALL SYSTEM_CLOCK")
        self.assertLess(emission, check)
        self.assertLess(check, timer)
        self.assertTrue(all(len(line) <= 132 for line in source.splitlines()))


if __name__ == "__main__":
    unittest.main()

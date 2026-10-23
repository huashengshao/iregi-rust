"""Run the actual evidence-only marimo app; import no numerical extension."""

from collections import Counter
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/python"))
sys.path.insert(0, str(ROOT / "examples/notebooks"))

import marimo as mo
from _presentation import COHORT_CHOICES, load_benchmark_cohort
from test_gallery_runtime import BenchmarkGalleryTests, load_app


def main():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BenchmarkGalleryTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError("Actual benchmark app integration tests failed.")
    selections = []
    for label, choice in COHORT_CHOICES.items():
        _, definitions = load_app("03_benchmark_explorer.py").run(defs={
            "cohort_choice": mo.ui.dropdown({label: choice}, value=label),
        })
        _, expected = load_benchmark_cohort(ROOT, choice)
        rows = definitions["selected_rows"]
        assert rows == expected, choice
        assert len(rows) == 8, choice
        selections.append({"choice": choice, "rows": len(rows),
                           "gates": dict(Counter(row.timing_status for row in rows)),
                           "numerator": rows[0].tirust_label,
                           "denominator": rows[0].reference_label})
    assert "tirust" not in sys.modules, "Benchmark explorer imported the numerical extension."
    print(json.dumps({"status": "PASS", "actual_marimo_app": True,
                      "runtime_tests": result.testsRun, "cohort_selections": selections,
                      "native_extension_imported": False}, indent=2))


if __name__ == "__main__":
    main()

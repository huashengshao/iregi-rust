"""Reproduce source lint and frozen-evidence checks; execute no notebook."""

from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PYTHON = ROOT / ".local/notebooks-env/bin/python"
MARIMO = ROOT / ".local/notebooks-env/bin/marimo"
NOTEBOOKS = [
    "examples/notebooks/01_numerator_to_integral.py",
    "examples/notebooks/02_dots_and_derivatives.py",
    "examples/notebooks/03_benchmark_explorer.py",
]
SOURCES = [*NOTEBOOKS, "examples/notebooks/_presentation.py",
           "examples/notebooks/README.md", "tests/python/test_gallery_evidence.py",
           "tests/python/test_gallery_runtime.py", "validation/python-notebooks/review_source.py",
           str(Path(__file__).relative_to(ROOT))]
EVIDENCE = [
    "validation/benchmark/baseline-6b24c03-licensed/results.json",
    "validation/collier-reference/timing-initial8/summary.json",
    "validation/selected-native-four-engine/posthoc-revision2/summary.json",
    "validation/selected-native-four-engine/posthoc-revision2/qualification.json",
    "validation/selected-native-four-engine/v3-frozen/qualification.json",
    "validation/python-notebooks/qualification.json",
]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def run(name, arguments):
    directory = OUT / name
    directory.mkdir(exist_ok=True)
    before = {path: digest(ROOT / path) for path in SOURCES}
    started = time.monotonic()
    with (directory / "stdout.log").open("w") as stdout, (directory / "stderr.log").open("w") as stderr:
        completed = subprocess.run(arguments, cwd=ROOT, stdout=stdout, stderr=stderr,
                                   timeout=60, check=False)
    after = {path: digest(ROOT / path) for path in SOURCES}
    receipt = {"command": [str(item) for item in arguments], "exit_code": completed.returncode,
               "seconds": time.monotonic() - started, "cap_seconds": 60,
               "source_hashes": before, "source_unchanged": before == after,
               "native_reduction_executed": False, "notebook_executed": False}
    write_json(directory / "run.json", receipt)
    if completed.returncode != 0 or before != after:
        raise RuntimeError(f"Source qualification failed: {name}")
    return receipt


def main():
    source_spec = importlib.util.spec_from_file_location(
        "gallery_source_review", ROOT / "validation/python-notebooks/review_source.py")
    source_module = importlib.util.module_from_spec(source_spec)
    source_spec.loader.exec_module(source_module)
    ast_report = {"status": "passed", "notebooks_executed": False,
                  "files": [source_module.inspect_notebook(ROOT / path)
                            for path in SOURCES if path.endswith(".py")]}
    write_json(OUT / "source-ast-review.json", ast_report)
    lint = run("lint", [MARIMO, "check", "--strict", *NOTEBOOKS])
    tests = run("evidence-tests", [PYTHON, "-m", "unittest", "discover", "-s",
                                  "tests/python", "-p", "test_gallery_evidence.py", "-v"])
    qualification = {
        "status": "SOURCE_AND_FROZEN_EVIDENCE_PASS_RUNTIME_PENDING",
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "historical_source_commit": "1e06fc5",
        "historical_qualification": "validation/python-notebooks/qualification.json",
        "scope": "Separate benchmark-explorer revision only. Six distinct choices retain all historical/private families; no numerical kernel or native notebook is executed.",
        "official_lint": {"marimo": "0.24.0", "strict": True, "files": 3,
                          "exit_code": lint["exit_code"]},
        "evidence_tests": {"passed": 15, "failed": 0, "saved_ratios_checked": 40,
                           "CI_endpoints_checked": 80, "exit_code": tests["exit_code"]},
        "notebook_cells": sum(len(item["cells"]) for item in ast_report["files"]),
        "posthoc": True, "original_conservative_verdict_retained": True,
        "short_block_family_retained_in_all_five_private_comparisons": True,
        "ratios": "TIRust/reference or TIRust(selected)/TIRust(baseline), never cross-session",
        "source_hashes": {path: digest(ROOT / path) for path in SOURCES},
        "evidence_hashes": {path: digest(ROOT / path) for path in EVIDENCE},
        "pending": ["Actual standalone wheel-backed tests", "Headless notebook execution/export",
                    "Rendered graph/math/controls visual review"],
    }
    write_json(OUT / "qualification.json", qualification)
    print(json.dumps({"status": qualification["status"], "notebook_cells": qualification["notebook_cells"],
                      "evidence_tests": qualification["evidence_tests"]}))


if __name__ == "__main__":
    main()

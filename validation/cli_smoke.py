#!/usr/bin/env python3
"""Small end-to-end CLI checks; run serially with other Symbolica users."""
import argparse
import copy
import json
import math
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, default=Path("target/debug/iregi-rust"))
    parser.add_argument("--output", type=Path, default=Path("target/cli-smoke"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    checks = []
    report_path = args.output / "report.json"
    report_path.write_text(json.dumps({"schema_version": 1, "passed": False,
                           "status": "running", "checks": checks}, indent=2) + "\n")

    def run(name, arguments, code=0, json_output=True):
        process = subprocess.run([str(args.cli.resolve()), *arguments], text=True,
                                 capture_output=True, cwd=Path.cwd(), timeout=180)
        (args.output / f"{name}.stdout").write_text(process.stdout)
        (args.output / f"{name}.stderr").write_text(process.stderr)
        if process.returncode != code:
            report_path.write_text(json.dumps({"schema_version": 1, "passed": False,
                "status": "failed", "checks": checks, "failed_check": name,
                "returncode": process.returncode, "expected_returncode": code,
                "diagnostic": process.stderr}, indent=2) + "\n")
            raise AssertionError(f"{name}: exit {process.returncode}, expected {code}: {process.stderr}")
        checks.append(name)
        return json.loads(process.stdout) if json_output else process

    def close(actual, expected, tolerance=1e-11):
        actual, expected = complex(*map(float, actual)), complex(*map(float, expected))
        error = abs(actual - expected) / max(1, abs(expected))
        if not math.isfinite(error) or error > tolerance:
            raise AssertionError(f"complex comparison failed: {actual} vs {expected}")

    def write(name, value):
        path = args.output / name
        path.write_text(json.dumps(value, indent=2) + "\n")
        return str(path)

    run("help", ["--help"], json_output=False)
    graph = ["examples/graphs/bubble.dot", "--model", "fixtures/models/phi3.json"]
    prepared = run("prepare-bubble", ["prepare", *graph])
    assert prepared["rank"] == 2 and len(prepared["terms"]) == 6
    assert len(prepared["propagators"]) == 2
    comparison = run("compare-bubble-rank2", ["compare", "--fixtures", "validation/reference/fixtures.json",
                     "--case", "bubble_rank2_mode1"])
    assert comparison["passed"] == 1 and comparison["failed"] == 0
    assert comparison["cases"][0]["id"] == "bubble_rank2_mode1"
    assert comparison["cases"][0]["status"] == "passed"
    expected = next(case["expected"]["moments"][0] for case in
                    json.loads(Path("validation/reference/fixtures.json").read_text())["cases"]
                    if case["input"]["id"] == "B0")
    base = None
    for precision in ["f64", "dd", "float"]:
        result = run(f"reduce-bubble-{precision}", ["reduce", "--input", "examples/inputs/bubble.json",
                     "--algorithm", "pv", "--precision", precision, "--bits", "160"])
        assert len(result["samples"]) == 2 and len(result["basis"]) == 15
        assert all(sample["status"] == "success" for sample in result["samples"])
        for actual, reference in zip(result["samples"][0]["moments"][0], expected):
            close(actual, reference)
        if precision == "f64":
            base = result["samples"][0]["moments"]
    result = run("run-bubble", ["run", *graph, "--input", "examples/inputs/bubble.json", "--algorithm", "pv"])
    assert all(len(sample["integral"]) == 4 for sample in result["samples"])
    result = run("run-triangle", ["run", "examples/graphs/triangle.dot", "--model", "fixtures/models/phi3.json",
                 "--input", "examples/inputs/triangle.json", "--algorithm", "pv"])
    assert result["samples"][0]["status"] == "success"
    result = run("supplied-invariants", ["reduce", "--input", "examples/inputs/bubble-scalar-products.json", "--algorithm", "pv"])
    assert result["settings"]["invariants"] == "SuppliedScalarProducts"
    for actual, reference in zip(result["samples"][0]["moments"], base):
        for x, y in zip(actual, reference):
            close(x, y)
    inputs = json.loads(Path("examples/inputs/bubble.json").read_text())
    invalid = copy.deepcopy(inputs)
    invalid["samples"][1]["mu"] = "0"
    result = run("invalid-lane", ["reduce", "--input", write("invalid-lane.json", invalid), "--algorithm", "pv"], code=1)
    assert [sample["status"] for sample in result["samples"]] == ["success", "failed"]
    for actual, reference in zip(result["samples"][0]["moments"], base):
        for x, y in zip(actual, reference):
            close(x, y)
    ranks = copy.deepcopy(inputs)
    ranks["samples"][1]["rank"] = 3
    run("mixed-ranks", ["reduce", "--input", write("mixed-ranks.json", ranks)], code=2, json_output=False)
    singular_graph = args.output / "singular-coefficient.dot"
    singular_graph.write_text('''digraph bubble {
    graph [num="1/iregi::a", overall_factor="1"];
    edge [particle="phi"];
    ext [style=invis];
    ext -> a;
    a -> b [lmb_id=0];
    a -> b;
    b -> ext;
}
''')
    coefficients = copy.deepcopy(inputs)
    for sample, value in zip(coefficients["samples"], ["1", "0"]):
        sample["parameters"] = {"iregi::a": value}
    result = run("singular-coefficient-lane", ["run", str(singular_graph), "--model", "fixtures/models/phi3.json",
                 "--input", write("singular-coefficient.json", coefficients), "--algorithm", "pv", "--rank", "2"], code=1)
    assert [sample["status"] for sample in result["samples"]] == ["success", "failed"]
    for actual, reference in zip(result["samples"][0]["integral"], expected):
        close(actual, reference)
    report = {"schema_version": 1, "passed": True, "status": "passed", "checks": checks,
              "qualification": "Small CLI integration suite; full tensor oracle comparisons and physical MadLoop comparison run separately."}
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

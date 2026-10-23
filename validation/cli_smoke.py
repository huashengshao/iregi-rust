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
    current_check = None
    report_path = args.output / "report.json"
    report_path.write_text(json.dumps({"schema_version": 1, "passed": False,
                           "status": "running", "checks": checks}, indent=2) + "\n")

    def run(name, arguments, code=0, json_output=True):
        nonlocal current_check
        current_check = name
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

    try:
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
        comparison = run("compare-legacy-bubble", ["compare", "--fixtures", "validation/reference/snapping/reductions.json",
                         "--case", "bubble_near_mass_mode1"])
        assert comparison["passed"] == 2 and comparison["failed"] == 0
        assert {case["id"] for case in comparison["cases"]} == {
            "bubble_near_mass_mode1", "bubble_near_mass_mode1_translated_complex"}
        assert all("LegacyOnShell" in case["input_policy"] for case in comparison["cases"])
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
        result = run("float-accuracy", ["reduce", "--input", "examples/inputs/bubble.json", "--algorithm", "pv",
                     "--precision", "float", "--bits", "128", "--accuracy-bits", "53"])
        assert result["precision_control"]["output_bits"] == 128
        assert result["precision_control"]["accuracy_bits"] == 53
        assert result["precision_control"]["verification_scope"] == "none"
        assert all(sample["status"] == "success" for sample in result["samples"])
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
        supplied = json.loads(Path("examples/inputs/bubble-scalar-products.json").read_text())
        supplied.update(snap=True, threshold="1e-1000")
        result = run("legacy-supplied-invariants", ["reduce", "--input", write("legacy-supplied.json", supplied), "--algorithm", "pv"])
        assert result["input_policy"] == {"LegacyOnShell": {"threshold": "1e-1000"}}
        assert any("bypass" in note.lower() for note in result["preparation_notes"])
        for actual, reference in zip(result["samples"][0]["moments"], base):
            for x, y in zip(actual, reference):
                close(x, y)
        inputs = json.loads(Path("examples/inputs/bubble.json").read_text())
        diagonal = copy.deepcopy(inputs)
        for sample in diagonal["samples"]:
            sample.update(snap=True, threshold="0", rank=0, mu="3")
        diagonal["samples"][0]["propagators"][0]["mass_squared"] = ["-4", "0"]
        result = run("legacy-negative-zero-diagonal", ["reduce", "--input", write("legacy-diagonal.json", diagonal), "--algorithm", "ibp"], code=1)
        assert [sample["status"] for sample in result["samples"]] == ["failed", "success"]
        assert "nonphysical Cayley-diagonal domain is unsupported" in result["samples"][0]["reason"]
        assert "moments" not in result["samples"][0]
        for actual, reference in zip(result["samples"][1]["moments"][0], expected):
            close(actual, reference)
        pentagon = copy.deepcopy(inputs["samples"][0])
        pentagon.update(snap=True, rank=0)
        pentagon["propagators"] = pentagon["propagators"] + [copy.deepcopy(pentagon["propagators"][0]) for _ in range(3)]
        unsupported = run("legacy-higher-point-rejected", ["reduce", "--input", write("legacy-pentagon.json", pentagon)], code=2, json_output=False)
        assert "five or more propagators" in unsupported.stderr
        invalid = copy.deepcopy(inputs)
        invalid["samples"][1]["mu"] = "0"
        result = run("verified-invalid-lane", ["reduce", "--input", write("invalid-lane.json", invalid),
                     "--algorithm", "pv", "--rescue"], code=1)
        assert [sample["status"] for sample in result["samples"]] == ["success", "failed"]
        assert [sample["precision_rescue"]["status"] for sample in result["samples"]] == ["converged", "not_requested"]
        assert result["rescue_execution"]["requested_rows"] == result["rescue_execution"]["accepted_rows"] == 1
        assert result["precision_control"]["verification_scope"] == "tensor_moments"
        for actual, reference in zip(result["samples"][0]["moments"], base):
            for x, y in zip(actual, reference):
                close(x, y)
        comparison = run("verified-generalized-triangle", ["compare", "--case", "C0_power2_1_1_rank2",
                         "--algorithm", "ibp", "--rescue", "--accuracy-bits", "53"])
        assert comparison["passed"] == 1 and comparison["failed"] == 0
        assert comparison["cases"][0]["precision_rescue"]["status"] == "converged"
        assert comparison["cases"][0]["rescue_execution"]["accepted_rows"] == 1
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
                     "--input", write("singular-coefficient.json", coefficients), "--algorithm", "pv", "--rank", "2", "--rescue"], code=1)
        assert [sample["status"] for sample in result["samples"]] == ["success", "failed"]
        assert all(sample["precision_rescue"]["status"] == "converged" for sample in result["samples"])
        for actual, reference in zip(result["samples"][0]["integral"], expected):
            close(actual, reference)
        report = {"schema_version": 1, "passed": True, "status": "passed", "checks": checks,
                  "qualification": "Small CLI integration suite; full tensor oracle comparisons and physical MadLoop comparison run separately."}
        report_path.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 0
    except Exception as error:
        completed = checks[:-1] if checks and checks[-1] == current_check else checks
        report_path.write_text(json.dumps({"schema_version": 1, "passed": False,
            "status": "failed", "checks": completed, "failed_check": current_check,
            "exception": type(error).__name__, "diagnostic": str(error)}, indent=2) + "\n")
        raise


if __name__ == "__main__":
    sys.exit(main())

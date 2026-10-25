#!/usr/bin/env python3
"""Focused CLI facade integration smoke against retained, committed captures.

Run phases independently under a bounded owned-process runner. This script does
not create a new numerical oracle, rebuild libraries, or retry failed commands.
"""
import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ("input_rows", "argument_rows", "master_family_batches", "master_rows",
          "pentagon_box_rows", "reduction_rows", "fallback_rows", "fallback_successes", "analytic_rows")
CERTIFICATE = {"input_rows", "evaluated_rows", "passes", "reduction_batches"}
POLES = ["uv1", "ir1", "ir2", "finite"]
BASIS2 = [[0,0,0,0], [1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1],
          [2,0,0,0], [1,1,0,0], [1,0,1,0], [1,0,0,1], [0,2,0,0],
          [0,1,1,0], [0,1,0,1], [0,0,2,0], [0,0,1,1], [0,0,0,2]]


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def pair(value):
    assert len(value) == 2 and all(isinstance(x, str) for x in value)
    return tuple(Fraction(x) for x in value)


def compare_complex(actual, expected, scale=Fraction(1)):
    got = pair(actual)
    error = sum(abs(a - b) for a, b in zip(got, expected)) / (scale + sum(map(abs, expected)))
    assert error <= Fraction(1, 10**10), f"saved complex mismatch: {error}"
    return error


def check_execution(output, engine, rows, packed=None):
    summary = output["execution"]
    detail = output["engine_execution"]
    assert set(summary) == set(FIELDS) and detail["engine"] == engine
    assert all(type(value) is int and value >= 0 for value in summary.values())
    assert summary["input_rows"] == rows
    if engine == "Generic":
        assert summary == detail["execution"]
        if detail["certificate_execution"] is not None:
            assert set(detail["certificate_execution"]) == CERTIFICATE
    else:
        assert detail["parent_input_rows"] == rows
        assert detail["child_batch_calls"] == detail["parent_batch_calls"] == 1
        assert detail["packed_child_rows"] == packed
        assert detail["packed_parent_rows"] == 1
        for name in FIELDS[1:]:
            assert summary[name] == detail["child_execution"][name] + detail["parent_execution"][name]
        assert detail["child_execution"]["input_rows"] == packed
        assert detail["parent_execution"]["input_rows"] == 1
        for name in ["child_certificate_execution", "parent_certificate_execution"]:
            assert set(detail[name]) == CERTIFICATE
    assert summary["master_rows"] > 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--phase", choices=["low", "n6", "n7"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cli = args.cli.resolve()
    directory = args.output.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    cli_hash = sha(cli)
    report = {"status": "running", "phase": args.phase, "binary": str(cli),
              "binary_sha256": cli_hash, "checks": [], "inputs": {},
              "scope": "CLI integration against committed captures, not new mathematical or performance qualification"}
    report_path = directory / "report.json"
    save(report_path, report)
    started = time.monotonic()

    def source(relative):
        path = ROOT / relative
        report["inputs"][relative] = sha(path)
        save(report_path, report)
        return json.loads(path.read_text())

    def run(name, arguments, expected_code=0, timeout=25):
        assert sha(cli) == cli_hash
        report["active_command"] = {"name": name, "arguments": arguments,
                                     "timeout_seconds": timeout, "expected_code": expected_code}
        save(report_path, report)
        try:
            process = subprocess.run([str(cli), *arguments], cwd=ROOT, capture_output=True,
                                     text=True, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            for suffix, content in [("stdout", error.stdout), ("stderr", error.stderr)]:
                data = content or b""
                (directory / (name + "." + suffix)).write_bytes(data if isinstance(data, bytes) else data.encode())
            raise
        (directory / (name + ".stdout")).write_text(process.stdout)
        (directory / (name + ".stderr")).write_text(process.stderr)
        assert process.returncode == expected_code, (name, process.returncode, process.stderr)
        value = json.loads(process.stdout)
        report["checks"].append(name)
        assert sha(cli) == cli_hash
        save(report_path, report)
        return value

    def input_file(name, value):
        path = directory / (name + ".json")
        save(path, value)
        report["inputs"][str(path)] = sha(path)
        return str(path)

    def check_rank2(value, statuses):
        assert value["basis"] == BASIS2 and value["poles"] == POLES
        assert len(value["samples"]) == len(statuses) == 2
        assert [row["status"] for row in value["samples"]] == statuses
        for row in value["samples"]:
            if row["status"] == "success":
                assert len(row["moments"]) == 15
                for moment in row["moments"]:
                    assert len(moment) == 4
                    for pole in moment: pair(pole)
            else:
                assert row.get("moments") is None

    try:
        if args.phase == "low":
            fixture = source("validation/reference/fixtures.json")
            report["inputs"]["examples/graphs/bubble.dot"] = sha(ROOT / "examples/graphs/bubble.dot")
            report["inputs"]["fixtures/models/phi3.json"] = sha(ROOT / "fixtures/models/phi3.json")
            inputs = source("examples/inputs/bubble.json")
            result = run("compare-bubble", ["compare", "--fixtures", "validation/reference/fixtures.json",
                         "--case", "bubble_rank2_mode1"])
            assert result["passed"] == 1 and result["failed"] == 0
            case = result["cases"][0]
            assert case["engine_execution"]["engine"] == "Generic"
            assert case["execution"] == case["engine_execution"]["execution"]
            assert case["execution_batch_ids"] == ["bubble_rank2_mode1"]
            assert isinstance(case["diagnostics"], list)
            run_result = run("run-default-hybrid", ["run", "examples/graphs/bubble.dot", "--model",
                "fixtures/models/phi3.json", "--input", "examples/inputs/bubble.json"])
            assert run_result["algorithm_requested"] == "Hybrid"
            check_execution(run_result, "Generic", 2)
            check_rank2(run_result, ["success", "success"])
            assert all(row["status"] == "success" and len(row["integral"]) == 4
                       for row in run_result["samples"])
            dd = run("doublefloat-bubble", ["reduce", "--input", "examples/inputs/bubble.json",
                                            "--algorithm", "pv", "--precision", "dd"])
            check_execution(dd, "Generic", 2)
            check_rank2(dd, ["success", "success"])
            assert dd["precision_bits"] > 53
            for row, reference in zip(dd["samples"], run_result["samples"]):
                assert row["status"] == "success"
                assert len(row["moments"]) == len(reference["moments"]) == 15
                for moment, prior in zip(row["moments"], reference["moments"]):
                    for got, old in zip(moment, prior): compare_complex(got, pair(old))
            invalid = copy.deepcopy(inputs)
            invalid["samples"][1]["mu"] = "0"
            verified = run("rescue-invalid-neighbor", ["reduce", "--input", input_file("invalid", invalid),
                "--algorithm", "pv", "--rescue", "--accuracy-bits", "53"], expected_code=1, timeout=45)
            check_execution(verified, "Generic", 2)
            check_rank2(verified, ["success", "failed"])
            assert verified["engine_execution"]["certificate_execution"] is None
            assert verified["diagnostics"] is None
            assert [row["status"] for row in verified["samples"]] == ["success", "failed"]
            assert [row["precision_rescue"]["status"] for row in verified["samples"]] == ["converged", "not_requested"]
            assert verified["samples"][1].get("moments") is None
            assert verified["rescue_execution"]["accepted_rows"] == 1
            for moment, reference in zip(verified["samples"][0]["moments"], dd["samples"][0]["moments"]):
                for got, old in zip(moment, reference): compare_complex(got, pair(old))
            expected = next(case["expected"]["moments"][0] for case in fixture["cases"] if case["input"]["id"] == "B0")
            for got, old in zip(verified["samples"][0]["moments"][0], expected):
                # Existing reference values are intentionally captured binary64.
                compare_complex(got, tuple(Fraction(value) for value in old))
        else:
            n = 6 if args.phase == "n6" else 7
            rank = 3 if n == 6 else 0
            if n == 6:
                fixture = source("validation/public-highpoint/fixture-conditioned_masses.json")
                sample = copy.deepcopy(fixture["samples"][0]); sample["propagators"] = sample["propagators"][:6]
                saved = source("validation/highpoint-six-point-rank7-current/rank7-128/result.json")
            else:
                fixture = source("validation/highpoint-seven-point-current-cargo/fixture.json")
                sample = copy.deepcopy(fixture["samples"][0])
                saved = source("validation/highpoint-seven-point-current-cargo/captures/capture128.json")
            exact = [[Fraction(component), Fraction(0)] for p in sample["propagators"] for component in p["shift"]]
            exact += [[Fraction(p["mass_squared"][0]), Fraction(p["mass_squared"][1])] for p in sample["propagators"]]
            exact += [[Fraction(sample["mu"]), Fraction(0)]]
            assert saved["working_bits"] == 128 and saved["requested_bits"] == 53
            assert saved["lanes"][0]["status"] == "Success" and saved["lane_statuses"] == ["Success"]
            assert exact == [[Fraction(a), Fraction(b)] for a, b in saved["input_exact_rational"][0]]
            assert saved["settings"]["propagators"] == n and saved["settings"]["powers"] == [1]*n
            assert saved["settings"]["dimension_shift"] == 0 and saved["settings"]["convention"] == "IregiNative"
            assert saved["settings"]["tensor_weights"] == "Components"
            sample["rank"] = rank
            invalid = copy.deepcopy(sample); invalid["id"] = "invalid-scale"; invalid["mu"] = "0"
            value = run(args.phase, ["reduce", "--input", input_file("input", {"samples": [sample, invalid]}),
                "--rank", str(rank), "--algorithm", "pv", "--precision", "float", "--bits", "128",
                "--accuracy-bits", "53"], expected_code=1, timeout=130 if n == 6 else 250)
            check_execution(value, "SixPoint" if n == 6 else "SevenPoint", 2, packed=6 if n == 6 else 21)
            expected_settings = copy.deepcopy(saved["settings"]); expected_settings["rank"] = rank
            assert value["settings"] == expected_settings and value["poles"] == POLES
            if n == 7:
                detail = value["engine_execution"]
                assert detail["child_execution"]["master_family_batches"] == 1
                assert detail["child_execution"]["master_rows"] == 105
                assert detail["parent_execution"]["master_rows"] == 0
            assert value["precision_bits"] == 128 and value["precision_control"]["accuracy_bits"] == 53
            assert value["algorithm_requested"] == value["algorithm_used"] == "PassarinoVeltman"
            assert [row["status"] for row in value["samples"]] == ["success", "failed"]
            assert value["samples"][1].get("moments") is None
            assert len(value["diagnostics"]) == 2
            basis = value["basis"]
            assert len(basis) == (35 if n == 6 else 1)
            assert basis == saved["basis"][:len(basis)]
            assert len(value["samples"][0]["moments"]) == len(basis)
            maximum = Fraction(0); count = 0
            for powers, moment, reference in zip(basis, value["samples"][0]["moments"], saved["lanes"][0]["moments"]):
                assert len(moment) == len(reference) == 4
                scale = Fraction(sample["mu"])**(sum(powers)+4-2*n)
                for got, old in zip(moment, reference):
                    maximum = max(maximum, compare_complex(got, (Fraction(old["real"]), Fraction(old["imaginary"])), scale))
                    count += 1
            assert count == (140 if n == 6 else 4)
            report["saved_comparison"] = {"complex_slots": count, "maximum_error_exact": str(maximum),
                "tolerance": "1e-10", "reference_scope": "prefix of existing qualified committed full array at exactly matched inputs"}
        for name, value in report["inputs"].items():
            assert sha(ROOT / name if not Path(name).is_absolute() else Path(name)) == value
        assert sha(cli) == cli_hash
        report["status"] = "passed"
        report["elapsed_seconds"] = time.monotonic() - started
        save(report_path, report)
        print(json.dumps({"status": "passed", "phase": args.phase, "checks": report["checks"],
                          "elapsed_seconds": report["elapsed_seconds"]}))
        return 0
    except BaseException as error:
        report["status"] = "failed"; report["error"] = repr(error)
        report["elapsed_seconds"] = time.monotonic() - started
        save(report_path, report)
        raise


if __name__ == "__main__":
    raise SystemExit(main())

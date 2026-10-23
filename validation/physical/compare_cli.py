#!/usr/bin/env python3
"""Compare FeynKit physical graphs, full Rust tensor output, and MadLoop.

Original IREGI is reevaluated at FeynKit's canonical routing in every requested
mode. MadLoop uses another loop variable: only its mapped graph contraction is
compared directly. Failed modes and unsuccessful CLI calls remain in reports.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "validation/reference"))
from capture import evaluate  # noqa: E402

CASES = {
    "ggh": ("ggh_top_triangle", 2, -0.5, "-1/2", 1),
    "gghh": ("gghh_top_box", 2, -0.5, "-1/2", 0),
    "gghhh": ("gghhh_top_pentagon", 2, -0.5, "-1/2", -1),
    "gggg-up": ("gggg_up_box", 4, -0.125, "-1/8", 0),
}
MODES = {0: "ibp", 1: "pv", 2: "hybrid"}


def digest(path):
    if not path.is_file():
        return None
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def number(pair):
    value = complex(float(pair[0]), float(pair[1]))
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise ValueError("nonfinite numerical result")
    return value


def pair(value):
    return [value.real, value.imag]


def normalized_error(actual, expected, scale=1):
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("invalid comparison normalization")
    error = abs(actual / scale - expected / scale) / max(1, abs(expected / scale))
    if not math.isfinite(error):
        raise ValueError("nonfinite comparison error")
    return error


def kinematic_scale(sample):
    scale = float(sample["mu"])
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("renormalization scale must be positive and finite")
    for propagator in sample["propagators"]:
        for component in propagator["shift"]:
            value = abs(float(component))
            if not math.isfinite(value):
                raise ValueError("nonfinite propagator shift")
            scale = max(scale, value)
        scale = max(scale, math.sqrt(abs(number(propagator["mass_squared"]))))
    return scale


def one_loop_slots(native_poles):
    """Numerical conversion of independently computed native Laurent slots."""
    uv, ir, ir2, finite = map(number, native_poles)
    a = 0.5772156649015328606 + math.log(math.pi)
    b = a * a / 2 + math.pi ** 2 / 12
    normalization = 1 / complex(0, math.pi ** 2)
    return [normalization * uv, normalization * (ir + a * ir2), normalization * ir2,
            normalization * (finite + a * (uv + ir) + b * ir2)]


def compare_tensors(result, sample, expected, tolerance):
    lane = result["samples"][0]
    if not expected.get("stable"):
        raise ValueError("original IREGI reports unstable tensor coefficients")
    if len(expected["moments"]) != len(lane["moments"]):
        raise ValueError("original IREGI and CLI tensor shapes differ")
    if len(result["basis"]) != len(lane["moments"]):
        raise ValueError("CLI basis and tensor shapes differ")
    maximum, worst, by_rank = 0.0, None, {}
    for index, (actual_poles, native_poles) in enumerate(zip(lane["moments"], expected["moments"])):
        if len(actual_poles) != 4 or len(native_poles) != 4:
            raise ValueError("each tensor moment must retain all four Laurent slots")
        rank = sum(result["basis"][index])
        dimension = 4 + rank - 2 * len(sample["propagators"])
        scale = kinematic_scale(sample) ** dimension
        for pole, (actual, reference) in enumerate(zip(map(number, actual_poles), one_loop_slots(native_poles))):
            error = normalized_error(actual, reference, scale)
            by_rank[str(rank)] = max(by_rank.get(str(rank), 0.0), error)
            if error > maximum:
                maximum = error
                worst = {"moment": index, "exponents": result["basis"][index], "pole": pole,
                         "actual": pair(actual), "expected": pair(reference)}
    return {"status": "passed" if maximum <= tolerance else "mismatch", "passed": maximum <= tolerance,
            "reference": "original IREGI at the FeynKit canonical shifts, converted to OneLoop",
            "moments": len(lane["moments"]), "slots_per_moment": 4,
            "max_normalized_error": maximum, "max_error_by_rank": by_rank, "worst": worst}


def compare_physical(result, sample, madloop, case, tolerance):
    group = madloop["selected_feynkit_group"]
    record = next(record for record in madloop["records"] if record["group"] == group)
    if not record["stable"]:
        raise ValueError("selected MadLoop graph reports unstable reduction")
    raw_reference = [case[2] * number(value) for value in record["raw_result"]]
    uv, ir, ir2, finite = map(number, result["samples"][0]["integral"])
    raw_actual = [finite, uv + ir, ir2]
    scale = kinematic_scale(sample) ** case[4]
    errors = [normalized_error(actual, reference, scale) for actual, reference in zip(raw_actual, raw_reference)]
    passed = max(errors) <= tolerance
    return {"status": "passed" if passed else "mismatch", "passed": passed,
            "reference": "MadLoop selected graph, fixed equal gluon colors",
            "group": group, "factor": case[3], "laurent_order": ["finite", "single_pole", "double_pole"],
            "mass_dimension": case[4], "normalization_scale": scale,
            "actual_raw": list(map(pair, raw_actual)), "expected_raw": list(map(pair, raw_reference)),
            "errors": errors,
            "actual_normalized": [pair(value / (16 * math.pi ** 2)) for value in raw_actual],
            "expected_normalized": [pair(value / (16 * math.pi ** 2)) for value in raw_reference],
            "excludes": ["R2", "UV counterterms"], "includes": ["bare UV and IR poles", "R1"],
            "momentum_source": "MadLoop evaluated external momenta at the numerator seam"}


def text(value):
    return value.decode(errors="replace") if isinstance(value, bytes) else (value or "")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, default="ggh")
    parser.add_argument("--cli", type=Path, default=Path("target/optimized/release/iregi-rust"))
    parser.add_argument("--input", type=Path)
    parser.add_argument("--madloop", type=Path)
    parser.add_argument("--oracle", type=Path, default=Path("target/reference/iregi-reference-original"))
    parser.add_argument("--reference-mode", type=int, choices=MODES, action="append",
                        help="repeat to select original IREGI modes; defaults to IBP, PV and hybrid")
    parser.add_argument("--cli-result", type=Path,
                        help="audit existing CLI JSON without running Symbolica; producer identity is not inferred")
    parser.add_argument("--precision", choices=["f64", "dd", "float"], default="f64")
    parser.add_argument("--bits", type=int, default=128)
    parser.add_argument("--algorithm", choices=["ibp", "pv", "hybrid"], default="hybrid")
    parser.add_argument("--tolerance", type=float, default=1e-10)
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not math.isfinite(args.tolerance) or args.tolerance <= 0:
        parser.error("tolerance must be positive and finite")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("timeout must be positive and finite")
    case = CASES[args.case]
    args.input = args.input or Path(f"validation/physical/{args.case}-cli-input.json")
    args.madloop = args.madloop or Path(f"validation/physical/madloop/fixtures/{args.case}-helicity-1.json")
    args.output = args.output or Path(f"target/physical/{args.case}-cli-{args.algorithm}-{args.precision}-comparison.json")
    modes = sorted(set(args.reference_mode if args.reference_mode is not None else MODES))
    graph = Path(f"examples/graphs/{case[0]}.dot")
    model = Path("fixtures/models/sm.json")
    command = [str(args.cli.resolve()), "run", str(graph), "--model", str(model),
               "--input", str(args.input), "--feynman-rules", "--external-wavefunctions",
               "--component", ",".join(["0"] * case[1]), "--convention", "oneloop",
               "--algorithm", args.algorithm, "--precision", args.precision, "--bits", str(args.bits)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 2, "case": args.case, "passed": False, "tolerance": args.tolerance,
        "precision": args.precision, "algorithm": args.algorithm,
        "error_metric": "abs((actual-expected)/Q^dimension) / max(1, abs(expected/Q^dimension)); Q=max(mu, abs(shift components), sqrt(abs(mass_squared)))",
        "cli_status": {"status": "not_started", "executed": args.cli_result is None},
        "tensor_comparisons": [], "physical_comparison": {"status": "not_run", "passed": False},
        "provenance": {"cli_sha256": digest(args.cli) if args.cli_result is None else None,
                       "replayed_cli_result_sha256": digest(args.cli_result) if args.cli_result else None,
                       "input_sha256": digest(args.input), "madloop_fixture_sha256": digest(args.madloop),
                       "original_iregi_sha256": digest(args.oracle), "graph_sha256": digest(graph),
                       "model_sha256": digest(model), "script_sha256": digest(Path(__file__)),
                       "command": command if args.cli_result is None else None},
        "qualification": "Reference data and comparison arithmetic are binary64; higher working precision does not certify additional digits. Failed modes remain visible and are not attributed to either implementation without an independent check.",
    }
    oracle_records = []
    try:
        sample = json.loads(args.input.read_text())
        report["kinematic_scale"] = kinematic_scale(sample)
        madloop = json.loads(args.madloop.read_text())
        report["provenance"]["madgraph_revision"] = madloop["source_revision"]
        if args.cli_result:
            stdout, stderr, returncode = args.cli_result.read_text(), "", 0
        else:
            try:
                process = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=args.timeout)
                stdout, stderr, returncode = process.stdout, process.stderr, process.returncode
            except subprocess.TimeoutExpired as error:
                stdout, stderr, returncode = text(error.stdout), text(error.stderr), None
                report["cli_status"] = {"status": "timeout", "executed": True, "timeout_seconds": args.timeout}
        args.output.with_suffix(".cli.stdout.txt").write_text(stdout)
        args.output.with_suffix(".cli.stderr.txt").write_text(stderr)
        if returncode != 0:
            if returncode is not None:
                report["cli_status"] = {"status": "failed", "executed": True, "returncode": returncode}
            raise ValueError("CLI did not complete successfully; retained stdout/stderr accompany this report")
        result = json.loads(stdout)
        args.output.with_suffix(".cli.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        report["precision_bits"] = result["precision_bits"]
        report["algorithm_requested"] = result.get("algorithm_requested")
        report["algorithm_used"] = result.get("algorithm_used")
        if len(result["samples"]) != 1 or result["samples"][0]["status"] != "success":
            report["cli_status"] = {"status": "failed_lane", "executed": args.cli_result is None,
                                    "samples": result.get("samples")}
            raise ValueError("expected exactly one successful physical sample")
        if result["samples"][0]["id"] != sample["id"]:
            raise ValueError("CLI result sample identity differs from the selected physical input")
        if result["graph"]["name"] != case[0]:
            raise ValueError("CLI result graph differs from the selected physical topology")
        settings = result["settings"]
        if (settings["convention"] != "OneLoop" or settings["tensor_weights"] != "Components"
                or settings["dimension_shift"] != 0
                or settings["powers"] != [1] * len(sample["propagators"])
                or settings["propagators"] != len(sample["propagators"])
                or settings["rank"] != sample["rank"]):
            raise ValueError("CLI tensor settings differ from the selected physical comparison contract")
        if result["poles"] != ["uv1", "ir1", "ir2", "finite"]:
            raise ValueError("CLI Laurent slot order differs from the comparison contract")
        report["cli_status"] = {"status": "success", "executed": args.cli_result is None, "returncode": returncode}
        for mode in modes:
            reference_case = {"id": f"{args.case.replace('-', '_')}_canonical_mode{mode}", "api": "tensor", "mode": mode,
                              "rank": result["settings"]["rank"], "dimension_shift": 0,
                              "mu": sample["mu"], "snap": False, "threshold": 1e-6,
                              "propagators": sample["propagators"]}
            comparison = {"mode": mode, "algorithm": MODES[mode], "passed": False}
            capture = {"mode": mode, "input": reference_case}
            try:
                expected, process = evaluate(args.oracle.resolve(), [reference_case], allow_stop=True)
                capture.update(returncode=process.returncode, results=expected)
                args.output.with_suffix(f".oracle-mode{mode}.stdout.txt").write_text(process.stdout)
                args.output.with_suffix(f".oracle-mode{mode}.stderr.txt").write_text(process.stderr)
                if process.returncode or len(expected) != 1 or expected[0]["id"] != reference_case["id"]:
                    raise ValueError("original IREGI did not return the requested record")
                comparison.update(compare_tensors(result, sample, expected[0], args.tolerance))
            except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
                comparison.update(status="reference_failed", reason=str(error))
                capture["error"] = str(error)
                if isinstance(error, subprocess.TimeoutExpired):
                    args.output.with_suffix(f".oracle-mode{mode}.stdout.txt").write_text(text(error.stdout))
                    args.output.with_suffix(f".oracle-mode{mode}.stderr.txt").write_text(text(error.stderr))
            oracle_records.append(capture)
            report["tensor_comparisons"].append(comparison)
        try:
            report["physical_comparison"] = compare_physical(result, sample, madloop, case, args.tolerance)
        except (ValueError, KeyError, TypeError, StopIteration) as error:
            report["physical_comparison"] = {"status": "failed", "passed": False, "reason": str(error)}
        # Preserve the familiar single-comparison field; independent IBP is primary.
        primary = next((entry for entry in report["tensor_comparisons"] if entry["mode"] == 0), report["tensor_comparisons"][0])
        report["tensor_comparison"] = primary
        report["all_reference_modes_passed"] = all(entry["passed"] for entry in report["tensor_comparisons"])
        report["reference_modes_disagree_on_rust_match"] = len({entry["passed"] for entry in report["tensor_comparisons"]}) > 1
        report["passed"] = report["physical_comparison"]["passed"] and report["all_reference_modes_passed"]
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        report["failure"] = str(error)
        if report["cli_status"]["status"] == "not_started":
            report["cli_status"]["status"] = "failed_to_start_or_parse"
    args.output.with_suffix(".oracle.json").write_text(json.dumps(oracle_records, indent=2, allow_nan=False) + "\n")
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

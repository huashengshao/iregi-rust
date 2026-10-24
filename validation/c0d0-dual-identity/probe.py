"""Frozen, bounded-runner-only C0/D0 mass-derivative identity qualification.

This file has not been numerically executed when initially prepared. All number
arithmetic is delegated to the wheel's Symbolica/Numerica Float/ComplexFloat.
Python implements transport, explicit fixture selection, and evidence capture.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback


HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, document):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("family", choices=("C0", "D0"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError("Refusing to overwrite prior numerical evidence")
    config = json.loads((HERE / "inputs.json").read_text())
    manifest = json.loads((HERE / "manifest.json").read_text())
    family = config["families"][args.family]
    report = {
        "schema_version": 1,
        "family": args.family,
        "configuration": config,
        "manifest_sha256": digest(HERE / "manifest.json"),
        "status": "running",
        "complete": False,
        "passed": False,
        "events": [],
        "evaluations": [],
        "identities": [],
        "precision_comparisons": [],
        "exceptions": [],
    }
    started = time.monotonic_ns()

    def event(phase, **fields):
        entry = {"elapsed_ns": time.monotonic_ns() - started, "phase": phase, **fields}
        report["events"].append(entry)
        save(output, report)
        print(json.dumps(entry), flush=True)

    try:
        for name, expected in manifest["guarded_files_sha256"].items():
            actual = digest(REPO / name)
            if actual != expected:
                raise RuntimeError(f"Frozen input changed: {name}: {actual} != {expected}")
        installed = REPO / manifest["installed_native"]
        if digest(installed) != manifest["installed_native_sha256"]:
            raise RuntimeError("Installed native library does not match qualified wheel004")
        if Path(sys.prefix).resolve() != (REPO / manifest["venv"]).resolve():
            raise RuntimeError("Wrong Python environment; use the frozen wheel004 interpreter")
        report["provenance"] = {
            "native_path": str(installed),
            "native_sha256": digest(installed),
            "interpreter": sys.executable,
            "python": sys.version,
        }
        event("provenance_verified")

        # No native import occurs before the provenance checks above.
        from tirust import ComplexFloat, Dual, Float, ReductionPlan
        import tirust._tirust as native

        if Path(native.__file__).resolve() != installed.resolve():
            raise RuntimeError("Python loaded a native module other than frozen wheel004")
        event("native_imported")
        shape = config["shape"]
        n = family["propagators"]

        def real_record(value):
            if not isinstance(value, Float) or not value.is_finite():
                raise ValueError("Successful output must have finite upstream Float components")
            numerator, denominator = value.as_integer_ratio()
            return {
                "numerator": str(numerator),
                "denominator": str(denominator),
                "precision_bits": value.precision,
                "display": str(value),
            }

        def number_record(value):
            if not isinstance(value, ComplexFloat):
                raise TypeError("Expected direct ComplexFloat output; no binary64 conversion allowed")
            return {"real": real_record(value.real), "imag": real_record(value.imag)}

        def lifted(value, bits):
            # Exact represented values are transferred through arbitrary-sized
            # integers. No input or result passes through Python float/complex.
            return ComplexFloat(
                Float.from_ratio(*value.real.as_integer_ratio(), precision=bits),
                Float.from_ratio(*value.imag.as_integer_ratio(), precision=bits),
            )

        def compare(actual, expected, component, pole):
            bits = max(512, actual.real.precision, actual.imag.precision,
                       expected.real.precision, expected.imag.precision)
            left, right = lifted(actual, bits), lifted(expected, bits)
            degree = sum(shape[component])
            dimension = 4 - 2 * n - 2 * degree
            scale = Float(family["characteristic_scale"], precision=bits) ** dimension
            tolerance = Float(config["tolerance"], precision=bits)
            error = abs(left - right) / (scale + abs(right))
            # These strictly massive, spacelike D=4 integrals and all their
            # dotted versions are UV and IR finite. Check all three poles
            # independently, so an identical spurious pole cannot pass.
            poles_zero = pole == 3 or (left == 0 and right == 0)
            return {
                "component": shape[component],
                "laurent": config["laurent_names"][pole],
                "mass_dimension": dimension,
                "actual": number_record(actual),
                "expected": number_record(expected),
                "normalization_scale": real_record(scale),
                "normalized_error": real_record(error),
                "exact_poles_zero": poles_zero,
                "passed": bool(error <= tolerance and poles_zero),
            }

        def prepare(powers, algorithm, label):
            event("plan_start", label=label, powers=powers, algorithm=algorithm)
            try:
                plan = ReductionPlan(
                    n, config["rank"], powers=powers,
                    dimension_shift=config["dimension_shift"], algorithm=algorithm,
                    convention=config["convention"], input_policy=config["input_policy"],
                )
                event("plan_end", label=label, notes=plan.preparation_notes)
                return plan
            except Exception as error:
                report["exceptions"].append({"label": label, "phase": "plan",
                    "type": type(error).__name__, "message": str(error),
                    "traceback": traceback.format_exc()})
                event("plan_failed", label=label)
                return None

        def evaluate(plan, bits, label, dual):
            record = {"label": label, "precision_bits": bits, "dual": dual,
                      "success": False, "complete": False}
            report["evaluations"].append(record)
            if plan is None:
                record["status"] = "plan_failed"
                event("evaluation_unavailable", label=label, precision_bits=bits)
                return None
            try:
                event("workspace_start", label=label, precision_bits=bits)
                workspace = plan.workspace(
                    dtype="float", precision=bits, accuracy_bits=config["accuracy_bits"],
                    dual_shape=shape if dual else None,
                )
                event("workspace_end", label=label, precision_bits=bits)
                masses = list(family["masses_squared"])
                if dual:
                    masses[:2] = [Dual(shape=shape, values=values)
                                  for values in config["mass_seed_values"]]
                batch = plan.pack(shifts=[family["shifts"]], masses_squared=[masses],
                                  mu=[family["mu"]])
                event("reduction_start", label=label, precision_bits=bits)
                result = workspace.reduce_batch(batch)
                record.update({"statuses": result.statuses,
                               "lane_success": result.success,
                               "diagnostics": result.diagnostics,
                               "fallback_used": result.fallback_used,
                               "analytic_used": result.analytic_used,
                               "execution_stats": result.execution_stats,
                               "stats": result.stats})
                if tuple(result.laurent_names) != tuple(config["laurent_names"]):
                    raise ValueError("Laurent ordering changed")
                if result.rows != 1 or result.success != (True,):
                    record.update(status="lane_failed", complete=True)
                    event("reduction_failed", label=label, precision_bits=bits)
                    return None
                lane = result.lane(0)
                if len(lane) != 1 or len(lane[0]) != 4:
                    raise ValueError("Rank-zero output dimensions changed")
                if dual:
                    if any(not isinstance(value, Dual) or value.shape != shape
                           or len(value.values) != 6 for value in lane[0]):
                        raise ValueError("Dual shape/order changed")
                    # Component-major local view; no numerical operations.
                    values = [[pole.values[component] for pole in lane[0]]
                              for component in range(6)]
                else:
                    values = [list(lane[0])]
                record["values"] = [[number_record(value) for value in row] for row in values]
                record.update(status="success", success=True, complete=True)
                event("reduction_end", label=label, precision_bits=bits)
                return values
            except Exception as error:
                record.update(status="exception", exception_type=type(error).__name__,
                              exception=str(error), traceback=traceback.format_exc())
                event("evaluation_exception", label=label, precision_bits=bits)
                return None

        dual_plan = prepare([1] * n, config["base_algorithm"], "dual_unit")
        dual_results = {bits: evaluate(dual_plan, bits, "dual_unit", True)
                        for bits in config["precisions"]}
        ordinary_results = {}
        for component, prefix in enumerate(config["component_powers_prefix"]):
            powers = prefix + [1] * (n - 2)
            label = f"ordinary_{component}"
            plan = prepare(powers, config["oracle_algorithm"], label)
            for bits in config["precisions"]:
                values = evaluate(plan, bits, label, False)
                ordinary_results[bits, component] = values
                for pole in range(4):
                    if dual_results[bits] is None or values is None:
                        check = {"component": shape[component],
                                 "laurent": config["laurent_names"][pole],
                                 "passed": False, "status": "missing_failed_evaluation"}
                    else:
                        # All six normalized Taylor weights are exactly one
                        # for this explicitly fixed unit-power base integral.
                        check = compare(dual_results[bits][component][pole],
                                        values[0][pole], component, pole)
                    check.update(precision_bits=bits, powers=powers)
                    report["identities"].append(check)
                event("identity_compared", component=shape[component], precision_bits=bits)

        low, high = config["precisions"]
        for component in range(6):
            for source in ("dual", "ordinary"):
                lower = dual_results[low] if source == "dual" else ordinary_results[low, component]
                upper = dual_results[high] if source == "dual" else ordinary_results[high, component]
                index = component if source == "dual" else 0
                for pole in range(4):
                    if lower is None or upper is None:
                        check = {"component": shape[component],
                                 "laurent": config["laurent_names"][pole],
                                 "passed": False, "status": "missing_failed_evaluation"}
                    else:
                        check = compare(lower[index][pole], upper[index][pole], component, pole)
                    check.update(source=source, lower_precision=low, higher_precision=high)
                    report["precision_comparisons"].append(check)
        report["counts"] = {
            "evaluations": len(report["evaluations"]),
            "successful_evaluations": sum(record["success"] for record in report["evaluations"]),
            "identities": len(report["identities"]),
            "identities_passed": sum(check["passed"] for check in report["identities"]),
            "precision_comparisons": len(report["precision_comparisons"]),
            "precision_comparisons_passed": sum(check["passed"] for check in report["precision_comparisons"]),
        }
        expected_counts = (14, 14, 48, 48, 48, 48)
        observed_counts = tuple(report["counts"].values())
        report["passed"] = observed_counts == expected_counts and not report["exceptions"]
        report["complete"] = True
        report["status"] = "passed" if report["passed"] else "failed"
        event("complete", passed=report["passed"], counts=report["counts"])
    except Exception as error:
        report["exceptions"].append({"phase": "harness", "type": type(error).__name__,
                                      "message": str(error), "traceback": traceback.format_exc()})
        report["status"] = "exception"
        event("harness_exception")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

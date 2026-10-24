"""Independent audit of already-emitted C0 JSON; no numerical library imports.

Fraction/Decimal operations here only check stored numeric receipts. They do not
differentiate, reduce, integrate, evaluate special functions, or run a backend.
"""
import datetime
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import traceback

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
BASE = ROOT / "target/c0d0-dual-identity"
OUTPUT = HERE / "saved-data-gate002.json"
EXPECTED_FILES = {
    "capture.json": "52435655929f89d33dac73f33bcbc96606fa2b4edf5a8191b567e7a2879bd3d5",
    "process-terminal.json": "913d9f591727317085a335d9b761b74dafe94211a44cfcfee2dd1bcccb3b738c",
    "results.json": "c3e947d64295ede1a3cd86c5e920d7d33e450fcab2b24ff7ca850e4c2e046920",
    "runtime.log": "462ac90721748e50e2d5037ee54180c6bc2218f212fb61cf43daf471eb889887",
}
MANIFEST_SHA = "24d5dc7992e67371df6a2a248cb1f0211b3f5fbf15a6257089fd5d14183b7243"
HELPER_SHA = "c193cd7282d63b63a8f627612df684242a2a8941d1d0a35588514d0415ab8824"
SHAPE = [[0, 0], [1, 0], [0, 1], [2, 0], [1, 1], [0, 2]]
POLES = ["uv_single", "ir_single", "ir_double", "finite"]
PREFIXES = [[1, 1], [2, 1], [1, 2], [3, 1], [2, 2], [1, 3]]
TOLERANCE = Fraction(1, 10**10)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    if OUTPUT.exists():
        raise RuntimeError("Refusing to overwrite the independent gate receipt")
    receipt = {
        "schema_version": 1, "scope": "Independent saved-data C0 receipt arithmetic and evidence closure only",
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "native_imports": False, "native_or_symbolica_runtime": False,
        "new_integral_evaluations": 0, "frozen_files_modified": False,
        "supervisor_exit": {"value": 0, "source": "Parent terminal notice after collecting session 74574; not inferred from child returncode"},
        "gate_source_sha256": digest(Path(__file__)),
        "prior_gate": {"receipt": "saved-data-gate.json", "sha256": digest(HERE / "saved-data-gate.json"), "scope_failure": "The first audit incorrectly assumed finite values had exactly zero real component. This revision uses general complex norms; the runtime data and 1e-10 threshold are unchanged."},
        "interpreter": sys.executable, "checks": 0, "failures": [], "exceptions": [],
    }

    def check(condition, label):
        receipt["checks"] += 1
        if not condition:
            receipt["failures"].append(label)

    def ratio(item, label):
        check(isinstance(item["numerator"], str) and isinstance(item["denominator"], str), label + ": integer strings")
        numerator, denominator = int(item["numerator"]), int(item["denominator"])
        check(denominator > 0 and denominator & (denominator - 1) == 0, label + ": binary denominator")
        check(math.gcd(numerator, denominator) == 1, label + ": reduced exact ratio")
        precision = item["precision_bits"]
        check(type(precision) is int and precision > 0, label + ": positive precision")
        if numerator:
            mantissa = abs(numerator)
            mantissa //= mantissa & -mantissa
            check(mantissa.bit_length() <= precision, label + ": represented mantissa fits recorded precision")
        return Fraction(numerator, denominator)

    def complex_ratio(item, label):
        return ratio(item["real"], label + ".real"), ratio(item["imag"], label + ".imag")

    def decimal(value):
        return Decimal(value.numerator) / Decimal(value.denominator)

    def fraction_record(value):
        with localcontext() as ctx:
            ctx.prec = 40
            display = format(decimal(value), ".16E")
        return {"numerator": str(value.numerator), "denominator": str(value.denominator), "display": display}

    try:
        check(ROOT == Path("/shared/external/iregi/iregi-rust"), "project cwd")
        hashes = {name: digest(HERE / name) for name in EXPECTED_FILES}
        receipt["artifact_sha256"] = hashes
        check(hashes == EXPECTED_FILES, "all four artifacts match independently supplied terminal hashes")
        manifest = read(BASE / "manifest.json")
        inputs = read(BASE / "inputs.json")
        capture = read(HERE / "capture.json")
        terminal = read(HERE / "process-terminal.json")
        results = read(HERE / "results.json")
        check(digest(BASE / "manifest.json") == MANIFEST_SHA, "frozen manifest hash")
        bindings = dict(manifest["guarded_files_sha256"])
        check(len(bindings) == 19, "nineteen frozen source guards")
        bindings[manifest["installed_native"]] = manifest["installed_native_sha256"]
        bindings["target/c0d0-dual-identity/manifest.json"] = MANIFEST_SHA
        check(len(bindings) == 21 and capture["guarded_inputs"] == bindings, "complete 21-input guard binding")
        current = {name: digest(ROOT / name) for name in bindings}
        receipt["current_guard_hashes"] = current
        check(current == bindings, "all 21 guarded files remain unchanged at independent audit")
        for stage in ("guards_before", "guards_after"):
            checks = capture[stage]
            check(set(checks) == set(bindings), stage + ": no missing or extra guards")
            for name, expected in bindings.items():
                check(checks[name] == {"actual": expected, "expected": expected, "match": True}, stage + ": " + name)
        check(capture["lifecycle_sha256"] == HELPER_SHA == digest(BASE / "lifecycle.py"), "reviewed lifecycle hash")
        check(digest(ROOT / "target/native-f64-opt-in/qualification/lifecycle.py") == HELPER_SHA, "helper matches reviewed original")
        check(capture["manifest_sha256"] == results["manifest_sha256"] == MANIFEST_SHA, "manifest crosslinks")
        check(results["configuration"] == inputs, "full exact input/configuration crosslink")
        check(inputs["shape"] == SHAPE and inputs["laurent_names"] == POLES, "ordered six-component/four-slot shape")
        check(inputs["precisions"] == [128, 256] and inputs["accuracy_bits"] == 53, "working/requested precisions")
        check(inputs["component_powers_prefix"] == PREFIXES and inputs["component_weights"] == ["1"] * 6, "fixed Taylor-to-raised-power map")
        check(inputs["rank"] == inputs["dimension_shift"] == 0 and inputs["convention"] == "iregi", "rank/dimension/native convention")
        check(inputs["families"]["C0"]["propagators"] == 3 and inputs["families"]["C0"]["characteristic_scale"] == "4", "fixed triangle dimensional scale")
        check(capture["status"] == "passed" and capture["passed"] is True, "supervisor recorded pass")
        check(results["family"] == capture["family"] == "C0", "C0 family only")
        check(results["status"] == "passed" and results["passed"] is True and results["complete"] is True, "complete probe pass")
        check(results["exceptions"] == [] and capture["cleanup_errors"] == [], "no suppressed probe/cleanup exceptions")
        check(not any(key in capture for key in ("capture_error", "final_accounting_error")), "no capture/accounting error")
        check(capture["pre_run_unchanged"] is True and capture["post_run_unchanged"] is True, "before/after admission gates")
        check(capture["cancellation"] is None and capture["pending_admission_signals"] == [] and capture["deadline_exceeded"] is False, "no cancellation/deadline excess")
        check((capture["work_bound_seconds"], capture["total_bound_seconds"], capture["cleanup_and_bookkeeping_reserve_seconds"]) == (180, 200, 20), "frozen work/total/reserve bounds")
        process = capture["process"]
        check(process == terminal["process"] and terminal["cleanup_errors"] == [], "durable terminal agrees with capture")
        check(process["status"] == "exited" and process["returncode"] == 0 and process["owned_group_gone"] is True, "child exit and cleanup success")
        check(not process.get("timeout", False) and "error" not in process and "cancellation" not in process, "no child timeout/error/cancellation")
        check(0 < process["elapsed_seconds"] < terminal["elapsed_seconds"] < capture["elapsed_seconds"] < 200, "ordered terminal/total timings within bound")
        check(0 < process["timeout_seconds"] <= 180, "preflight charged against work deadline")
        group = process["owned_process_group"]
        check(group == 346829, "owned process group matches terminal notice")
        try:
            os.killpg(group, 0)
            gone = False
        except ProcessLookupError:
            gone = True
        check(gone, "independent current owned-process-group absence")
        receipt["owned_process_group"] = {"id": group, "absent_at_gate": gone}
        expected_command = ["taskset", "-c", "0", str(ROOT / manifest["venv"] / "bin/python"), "-I", str(BASE / "probe.py"), "C0", "--output", str(HERE / "results.json")]
        check(capture["command"] == process["command"] == expected_command, "isolated CPU0 historical interpreter command")
        check(capture["environment"] == {"PYTHONPATH": None, "PYTHONNOUSERSITE": "1", "RAYON_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "RUST_MIN_STACK": "67108864", "IREGI_DUAL_CASE_FILTER": None, "IREGI_DUAL_SKIP_CASE": None}, "fixed environment and no case filters")
        check(capture["evidence_sha256"] == {name: hashes[name] for name in ("results.json", "runtime.log", "process-terminal.json")}, "capture evidence hash closure")
        check(results["provenance"]["native_sha256"] == manifest["installed_native_sha256"], "historical wheel004 native crosslink")
        events = results["events"]
        check(all(a["elapsed_ns"] <= b["elapsed_ns"] for a, b in zip(events, events[1:])), "monotonic saved events")
        check(events[-1]["phase"] == "complete" and events[-1]["passed"] is True and capture["last_event"] == events[-1], "complete terminal event crosslink")
        log_events = []
        for line in (HERE / "runtime.log").read_text().splitlines():
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict) and "elapsed_ns" in item and "phase" in item:
                log_events.append(item)
        check(log_events == events, "all probe events independently present in retained log")
        evaluations = results["evaluations"]
        keys = [("dual_unit", bits) for bits in (128, 256)] + [(f"ordinary_{component}", bits) for component in range(6) for bits in (128, 256)]
        check([(row["label"], row["precision_bits"]) for row in evaluations] == keys, "all fourteen evaluations in prescribed order")
        by_key = {}
        evaluated_slots = 0
        for record in evaluations:
            key = (record["label"], record["precision_bits"])
            by_key[key] = record
            is_dual = key[0] == "dual_unit"
            check(record["dual"] is is_dual and record["success"] is True and record["complete"] is True and record["status"] == "success", str(key) + ": complete success")
            check(record["statuses"] == ["success"] and record["lane_success"] == [True], str(key) + ": successful single lane")
            check(len(record["values"]) == (6 if is_dual else 1), str(key) + ": full Taylor layout")
            check(record["stats"] == record["execution_stats"] and record["stats"]["input_rows"] == 1, str(key) + ": stats crosslink")
            check(record["diagnostics"] == [[]], str(key) + ": no hidden diagnostics")
            for component, values in enumerate(record["values"]):
                check(len(values) == 4, str(key) + ": all four Laurent slots")
                for pole, value in enumerate(values):
                    re, im = complex_ratio(value, f"evaluation {key} component {component} pole {pole}")
                    if pole < 3:
                        check(re == im == 0, str(key) + ": exact vanishing UV/IR poles")
                    else:
                        check(re != 0 or im != 0, str(key) + ": nontrivial finite value")
                    evaluated_slots += 1

        maximum = {"identities": Fraction(0), "precision_comparisons": Fraction(0)}
        rounding_max = Fraction(0)
        comparisons = 0

        def compare_saved(record, actual, expected, component, pole, section):
            nonlocal comparisons, rounding_max
            check(record["component"] == SHAPE[component] and record["laurent"] == POLES[pole], section + ": ordered component/pole")
            check(record["actual"] == actual and record["expected"] == expected, section + ": exact full-precision evaluation crosslinks")
            ar, ai = complex_ratio(actual, section + ": actual")
            er, ei = complex_ratio(expected, section + ": expected")
            dimension = -2 - 2 * sum(SHAPE[component])
            check(record["mass_dimension"] == dimension, section + ": squared-mass derivative dimension")
            scale = ratio(record["normalization_scale"], section + ": scale")
            check(scale == Fraction(4) ** dimension, section + ": exact dimensionful natural scale")
            stored = ratio(record["normalized_error"], section + ": stored error")
            delta_squared = (ar - er) ** 2 + (ai - ei) ** 2
            expected_squared = er ** 2 + ei ** 2
            # Exact rational threshold gate: sqrt(A) <= t*(s+sqrt(B)).
            # Once squared, x=A/t^2-s^2-B is either nonpositive or must
            # satisfy x^2 <= 4*s^2*B. This only audits saved numeric ratios.
            x = delta_squared / TOLERANCE ** 2 - scale ** 2 - expected_squared
            threshold_ok = x <= 0 or x ** 2 <= 4 * scale ** 2 * expected_squared
            check(threshold_ok, section + ": exact saved-ratio complex-norm threshold")
            # Decimal is used only to independently reproduce the already
            # emitted normalized residual, at more than 700 binary bits.
            residuals = []
            for decimal_precision in (220, 260):
                with localcontext() as ctx:
                    ctx.prec = decimal_precision
                    value = decimal(delta_squared).sqrt() / (decimal(scale) + decimal(expected_squared).sqrt())
                    residuals.append(Fraction(value))
            independent = residuals[1]
            check(abs(residuals[0] - independent) <= Fraction(1, 10**210), section + ": independent decimal recomputation convergence")
            check(0 <= independent <= TOLERANCE, section + ": independently recomputed threshold")
            check(0 <= stored <= TOLERANCE, section + ": stored threshold")
            rounding_error = abs(stored - independent)
            error_precision = record["normalized_error"]["precision_bits"]
            rounding_bound = Fraction(2) ** (10 - error_precision) * max(Fraction(1), independent)
            check(rounding_error <= rounding_bound, section + ": emitted error consistent with exact saved-ratio arithmetic")
            zero = pole == 3 or ar == ai == er == ei == 0
            check(record["exact_poles_zero"] is True and zero and record["passed"] is True, section + ": explicit pole and pass claims")
            maximum[section] = max(maximum[section], independent)
            rounding_max = max(rounding_max, rounding_error)
            comparisons += 1

        identities = results["identities"]
        check(len(identities) == 48, "48 complete identities")
        for index, (component, bits, pole) in enumerate((component, bits, pole) for component in range(6) for bits in (128, 256) for pole in range(4)):
            item = identities[index]
            check(item["precision_bits"] == bits and item["powers"] == PREFIXES[component] + [1], "identity precision/raised-power request")
            compare_saved(item, by_key["dual_unit", bits]["values"][component][pole], by_key[f"ordinary_{component}", bits]["values"][0][pole], component, pole, "identities")
        convergence = results["precision_comparisons"]
        check(len(convergence) == 48, "48 complete precision comparisons")
        for index, (component, source, pole) in enumerate((component, source, pole) for component in range(6) for source in ("dual", "ordinary") for pole in range(4)):
            item = convergence[index]
            check((item["source"], item["lower_precision"], item["higher_precision"]) == (source, 128, 256), "precision comparison source/precision order")
            label = "dual_unit" if source == "dual" else f"ordinary_{component}"
            local = component if source == "dual" else 0
            compare_saved(item, by_key[label, 128]["values"][local][pole], by_key[label, 256]["values"][local][pole], component, pole, "precision_comparisons")
        counts = {"evaluations": 14, "successful_evaluations": 14, "identities": 48, "identities_passed": 48, "precision_comparisons": 48, "precision_comparisons_passed": 48}
        check(results["counts"] == capture["counts"] == events[-1]["counts"] == counts, "independently enumerated counts match all claims")
        receipt["verified"] = {"guarded_files": 21, "before_guard_records": 21, "after_guard_records": 21, "evaluations": len(evaluations), "evaluated_complex_laurent_slots": evaluated_slots, "identity_checks": len(identities), "precision_checks": len(convergence), "exact_numeric_comparisons": comparisons, "all_three_poles_exact_zero": True, "maximum_recomputed_normalized_errors": {key: fraction_record(value) for key, value in maximum.items()}, "maximum_emitted_error_rounding_difference": fraction_record(rounding_max), "numeric_audit_method": "Exact Fraction arithmetic independently proves each saved complex-norm threshold inequality. Decimal square roots at220 and260 digits independently reproduce the emitted errors; precision-consistent roundoff and convergence are checked. No differentiation, polynomial manipulation, reduction, integration, special functions, or native library runtime."}
        check(all(digest(HERE / name) == expected for name, expected in EXPECTED_FILES.items()), "original artifacts unchanged after gate")
        check(digest(BASE / "manifest.json") == MANIFEST_SHA, "frozen manifest unchanged after gate")
    except Exception as error:
        receipt["exceptions"].append({"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()})
    receipt["passed"] = not receipt["failures"] and not receipt["exceptions"]
    receipt["status"] = "saved_data_gate_passed" if receipt["passed"] else "saved_data_gate_failed"
    with OUTPUT.open("x") as stream:
        stream.write(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": receipt["status"], "checks": receipt["checks"], "failures": receipt["failures"], "exceptions": receipt["exceptions"], "verified": receipt.get("verified"), "receipt_sha256": digest(OUTPUT)}, indent=2))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

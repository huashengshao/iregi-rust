"""Bounded shared-domain correctness capture; this runner cannot time cohorts."""
import argparse
import datetime
import gzip
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import time

import support


ROOT = Path.cwd()
SPEC = importlib.util.spec_from_file_location("existing_rejected_numeric_diagnostic", ROOT/"validation/collier-reference/n4/diagnose.py")
diagnose = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diagnose)


def uv_check(response, case, samples):
    if case["n"] < 4:
        return support.common.uv_identities(response, case, samples)
    errors, worst = [], 0.
    for lane, (row, sample) in enumerate(zip(response["lanes"], samples)):
        if row["status"] != "success":
            errors.append(f"lane{lane} is rejected")
            continue
        energy = max(1., sample["mu"], *(abs(x) for p in sample["shifts"] for x in p),
                     *(math.sqrt(math.hypot(*m)) for m in sample["masses"]))
        for index, (moment, degree) in enumerate(zip(row["moments"], support.kernel.degrees(case["rank"]))):
            error = abs(complex(*moment[0]))/energy**(4+degree-2*case["n"])
            worst = max(worst, error)
            if not math.isfinite(error) or error > 1e-10:
                errors.append(f"lane{lane},moment{index} violates UV-finiteness")
    return {"status": "passed" if not errors else "failed", "maximum_normalized_error": worst,
            "errors": errors, "tolerance": 1e-10,
            "identity": "N>=4 rank<=3 ordinary massive tensors are UV finite; every UV slot checked"}


def interface_agreement(generic, wrapped, case, samples):
    raw = diagnose.diagnostic_comparison(generic, wrapped, case, samples)
    # For rejected old wrappers retain their labelled raw values as the expected
    # numerical diagnostic; this comparison never accepts either rejected lane.
    if not wrapped["stable"]:
        import copy
        expected = copy.deepcopy(wrapped)
        expected["stable"] = True
        for row in expected["lanes"]:
            if row["status"] != "success":
                row["moments"] = row.get("diagnostic_moments")
            row["status"] = "success"
        raw = diagnose.diagnostic_comparison(generic, expected, case, samples)
    keys = ("status", "last_err_flag", "last_acc_flag", "worst_err_flag", "worst_acc_flag")
    flags_match = (generic["stable"] == wrapped["stable"]
                   and len(generic["lanes"]) == len(wrapped["lanes"]) == len(samples)
                   and all(all(a.get(k) == b.get(k) for k in keys)
                           for a, b in zip(generic["lanes"], wrapped["lanes"])))
    accepted_exact = (len(generic["lanes"]) == len(wrapped["lanes"])
                      and all(a["moments"] == b["moments"] for a, b in zip(generic["lanes"], wrapped["lanes"])))
    pole_probes_exact = generic.get("pole_check_errors") == wrapped.get("pole_check_errors")
    return {"status": "passed" if flags_match and accepted_exact and pole_probes_exact else "failed",
            "native_statuses_match": flags_match, "raw_array_comparison": raw,
            "accepted_outputs_exact": accepted_exact, "pole_probes_exact": pole_probes_exact,
            "scope": "Interface regression only; rejected outputs remain rejected"}


def accepted_outputs_equal(actual, expected):
    return (actual.get("stable") == expected.get("stable")
            and len(actual.get("lanes", [])) == len(expected.get("lanes", []))
            and all(a.get("status") == b.get("status") and a.get("moments") == b.get("moments")
                    for a, b in zip(actual.get("lanes", []), expected.get("lanes", []))))


def fixed_interfaces_ready(rows):
    fixed = [r for r in rows if r["n"] <= 4]
    return (len(fixed) == 16
            and all(r.get("iregi_frozen_regression", {}).get("status") == "passed"
                    and set(r.get("collier_policies", {})) == {"1", "2"}
                    and all(p.get("old_wrapper_regression", {}).get("status") == "passed"
                            for p in r["collier_policies"].values()) for r in fixed))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--build", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cpu", type=int, default=26)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT/"target"):
        parser.error("new project target/ attempt directory required")
    document = support.load_document(args.input)
    build = json.loads(args.build.read_text())
    original_path = ROOT/"validation/benchmark/baseline-6b24c03-licensed/results.json"
    original = json.loads(original_path.read_text())
    wrapped_path = ROOT/"validation/collier-reference/n4/diagnostics-v1/driver-build.json"
    wrapped_build = json.loads(wrapped_path.read_text())
    old_initial_path = ROOT/"validation/collier-reference/ready-initial8-v3/correctness.json"
    old_n4_path = ROOT/"validation/collier-reference/n4/diagnostics-v1/diagnostic-complete.json.gz"
    old_initial = json.loads(old_initial_path.read_text())
    old_n4 = json.loads(gzip.decompress(old_n4_path.read_bytes()))
    binaries = {"generic": build["binary"], "wrapped": wrapped_build["binary"],
                "iregi": original["binaries"]["reference"]}
    if build.get("status") != "built" or not build.get("guards_unchanged"):
        raise ValueError("reviewed immutable-library driver build required")
    source_paths = sorted((ROOT/"validation/collier-reference/shared").glob("*.py"))
    source_paths += [ROOT/"validation/collier-reference/shared/driver.f90",
                     ROOT/"validation/collier-reference/run.py", ROOT/"validation/benchmark/run.py",
                     ROOT/"validation/benchmark/driver.f90", ROOT/"validation/collier-reference/n4/diagnose.py",
                     args.input.resolve(), args.build.resolve(), original_path, wrapped_path, old_initial_path, old_n4_path,
                     *(ROOT/info["path"] for info in binaries.values()), ROOT/build["library"]["path"]]
    guards = {str(p.relative_to(ROOT)): support.kernel.digest(p) for p in source_paths}
    for name, info in binaries.items():
        if support.kernel.digest(ROOT/info["path"]) != info["sha256"]:
            raise ValueError(f"{name} binary changed")
    for p, sha in build["source_sha256"].items():
        if guards.get(p) != sha:
            raise ValueError("source changed since reviewed build")
    output.mkdir(parents=True)
    for p in source_paths:
        if p.suffix in (".py", ".f90", ".json"):
            destination = output/"sources"/p.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, destination)
    data = {"kind": "collier-shared-bounded-correctness", "status": "running",
            "date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "cpu": args.cpu,
            "timeout_seconds": 120, "performance_evidence": False,
            "source_binary_input_guards": guards, "binaries": binaries, "input_cases": document["cases"],
            "protocol": {"collier_policies": {"1": "COLI", "2": "Denner-Dittmaier"},
                         "direct_tensor_threshold": 6, "original_iregi_modes": ["Hybrid", "PassarinoVeltman", "Ibp"],
                         "request_accuracy": 1e-12, "critical_accuracy": 1e-10, "tolerance": 1e-10,
                         "batch_widths": [1, 32], "request_cap_seconds": 20,
                         "cache": "local recurrence memoization; no cross-sample/event reuse",
                         "n4_failures_preserved": "validation/collier-reference/n4/diagnostics-v1/qualification.json"},
            "rows": [{"id": case["id"], "n": case["n"], "rank": case["rank"], "batch_width": width,
                      "status": "pending", "responses": {}}
                     for case in document["cases"] for width in (1, 32)]}
    path = output/"results.json"
    support.kernel.save(path, data)
    previous = os.sched_getaffinity(0)
    started = time.monotonic()
    deadline = started+120
    processes = {}
    try:
        os.sched_setaffinity(0, {args.cpu})
        processes = {name: support.kernel.Process(ROOT/info["path"], name, output, 20)
                     for name, info in binaries.items()}
        for row in data["rows"]:
            if row["n"] >= 5 and not fixed_interfaces_ready(data["rows"]):
                row.update(status="not_run", reason="Exact fixed N2/N3/N4 per-engine output/status/pole-probe regression gate is not satisfied")
                support.kernel.save(path, data)
                continue
            case = next(c for c in document["cases"] if c["id"] == row["id"])
            exact = case["samples"][:row["batch_width"]]
            wire = [support.wire_sample(sample, case["n"]) for sample in exact]
            try:
                def request(name, key, text):
                    remaining = deadline-time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError("fixed total correctness cap exhausted")
                    processes[name].timeout = min(20, remaining)
                    response = processes[name].request(text)
                    row["responses"][key] = response
                    support.kernel.save(path, data)
                    support.kernel.validate_response(response, case)
                    return response
                reference = request("iregi", "iregi-Hybrid", support.original_iregi_request(case, exact, "Hybrid"))
                if case["n"] <= 4:
                    if case["n"] == 4:
                        retained = next(r for r in old_n4["n4"] if r["id"] == row["id"] and r["batch_width"] == row["batch_width"])
                        old_reference = retained["iregi"]["Hybrid"]
                    else:
                        retained = next(r for r in old_initial["rows"] if r["id"] == row["id"] and r["batch_width"] == row["batch_width"])
                        old_reference = retained["pilot"]["iregi"]
                    row["iregi_frozen_regression"] = {"status": "passed" if accepted_outputs_equal(reference, old_reference) else "failed",
                                                       "scope": "Exact complete Hybrid native outputs/status against retained per-engine fixed-input capture; timing fields excluded"}
                row["iregi_mode_agreement"] = {}
                for mode in ("PassarinoVeltman", "Ibp"):
                    other = request("iregi", "iregi-"+mode, support.original_iregi_request(case, exact, mode))
                    row["iregi_mode_agreement"][mode] = support.common.comparison(other, reference, case, wire)
                    if case["n"] == 4 and not accepted_outputs_equal(other, retained["iregi"][mode]):
                        row["iregi_frozen_regression"] = {"status": "failed", "reason": "Exact retained N4 mode output/status changed", "mode": mode}
                row["collier_policies"] = {}
                for mode in (1, 2):
                    generic = request("generic", f"generic-{mode}", support.collier_request(case, exact, mode))
                    policy = {"native_array_agreement": support.common.comparison(generic, reference, case, wire),
                              "raw_rejected_diagnostic": diagnose.diagnostic_comparison(generic, reference, case, wire),
                              "uv_identities": uv_check(generic, case, wire)}
                    row["collier_policies"][str(mode)] = policy
                    try:
                        support.common.validate_poles(generic, wire)
                        policy["pole_probes"] = {"status": "passed"}
                    except Exception as error:
                        policy["pole_probes"] = {"status": "failed", "error": str(error)}
                    if case["n"] <= 4:
                        wrapped = request("wrapped", f"wrapped-{mode}", support.collier_request(case, exact, mode))
                        policy["old_wrapper_regression"] = interface_agreement(generic, wrapped, case, wire)
                    policy["status"] = "accepted" if all(value["status"] == "passed" for key, value in policy.items()
                                                                      if key != "raw_rejected_diagnostic") else "rejected-or-disagrees"
                    support.kernel.save(path, data)
                row["status"] = "accepted-COLI" if (row["collier_policies"]["1"]["status"] == "accepted"
                                                      and all(x["status"] == "passed" for x in row["iregi_mode_agreement"].values())) else "failed-or-rejected"
            except Exception as error:
                row.update(status="timeout" if isinstance(error, TimeoutError) else "failed", error=f"{type(error).__name__}: {error}")
            support.kernel.save(path, data)
        data["status"] = "capture-complete"
        data["qualification"] = "complete" if all(r["status"] == "accepted-COLI" for r in data["rows"]) else "incomplete-fixed-failures-retained"
    except Exception as error:
        data.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        for process in processes.values():
            process.close()
        os.sched_setaffinity(0, previous)
        data["elapsed_seconds"] = time.monotonic()-started
        data["guards_unchanged"] = all(support.kernel.digest(ROOT/p) == sha for p, sha in guards.items())
        if not data["guards_unchanged"]:
            data.update(status="failed", error="source/binary/input guard changed")
        support.kernel.save(path, data)
    print(path)
    if data["status"] != "capture-complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

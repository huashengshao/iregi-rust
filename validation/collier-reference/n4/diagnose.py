"""Capture fixed-input, untimed diagnostics without promoting rejected outputs."""
import argparse
import copy
import datetime
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import time


ROOT = Path.cwd()
SPEC = importlib.util.spec_from_file_location("collier_frozen_common", ROOT / "validation/collier-reference/run.py")
common = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(common)
kernel = common.kernel


def diagnostic_comparison(response, expected, case, samples):
    """Compare available raw numbers; this does not change acceptance status."""
    numerical = copy.deepcopy(response)
    for lane in numerical.get("lanes", []):
        if lane.get("status") != "success":
            lane["moments"] = lane.get("diagnostic_moments")
        if lane.get("moments") is None:
            return {"status": "unavailable", "reason": "raw moments absent", "qualifies": False}
        lane["status"] = "success"
    numerical["stable"] = True
    result = common.comparison(numerical, expected, case, samples)
    return {"raw_numeric_agreement": result, "qualifies": False,
            "scope": "Diagnostic-only numeric comparison; original rejected status is preserved and cannot qualify the lane"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cpu", type=int, default=26)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "target"):
        parser.error("use a new project target/ attempt directory")
    if args.cpu not in os.sched_getaffinity(0):
        parser.error("CPU unavailable")
    build_path = args.build.resolve()
    build = json.loads(build_path.read_text())
    original_path = ROOT / "validation/collier-reference/ready-initial8-v3/build.json"
    original = json.loads(original_path.read_text())
    baseline_path = ROOT / "validation/benchmark/baseline-6b24c03-licensed/results.json"
    baseline = json.loads(baseline_path.read_text())
    input_paths = {
        "initial8": ROOT / "validation/benchmark/baseline-6b24c03-licensed/results-inputs.json",
        "n4": ROOT / "validation/collier-reference/extensions/n4-inputs.json",
    }
    cases = {name: common.load_inputs(path) for name, path in input_paths.items()}
    binaries = {"original": original["binary"], "diagnostic": build["binary"],
                "iregi": baseline["binaries"]["reference"]}
    paths = [Path(__file__).resolve(), ROOT / "validation/collier-reference/run.py",
             ROOT / "validation/benchmark/run.py", build_path, original_path, baseline_path,
             ROOT / "validation/collier-reference/n4/diagnostic-driver.f90",
             ROOT / "validation/collier-reference/n4/build_diagnostic.py",
             ROOT / build["review"]["path"], ROOT / original["library"]["path"],
             *input_paths.values(), *(ROOT / info["path"] for info in binaries.values())]
    guards = {str(p.relative_to(ROOT)): kernel.digest(p) for p in paths}
    for info in binaries.values():
        if kernel.digest(ROOT / info["path"]) != info["sha256"]:
            raise ValueError("binary does not match build receipt")
    if guards[original["library"]["path"]] != original["library"]["sha256"]:
        raise ValueError("immutable library changed")
    if build.get("status") != "built" or not build.get("library_unchanged"):
        raise ValueError("diagnostic build not successful")
    output.mkdir(parents=True)
    for p in paths:
        if p.suffix in (".py", ".f90", ".json"):
            snapshot = output / "sources" / p.relative_to(ROOT)
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, snapshot)
    data = {"kind": "collier-n4-rejection-diagnostic", "status": "running",
            "date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "performance_evidence": False, "timeout_seconds": 120, "cpu": args.cpu,
            "source_binary_input_guards": guards, "binaries": binaries,
            "acceptance_policy_changed": False, "tolerance": 1e-10,
            "initial8_regression": [], "n4": []}
    result_path = output / "results.json"
    kernel.save(result_path, data)
    deadline = time.monotonic() + 120
    previous_affinity = os.sched_getaffinity(0)
    processes = {}
    started = time.monotonic()
    try:
        os.sched_setaffinity(0, {args.cpu})
        processes = {name: kernel.Process(ROOT / info["path"], name, output, 20)
                     for name, info in binaries.items()}

        def request(name, text):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("diagnostic total cap exhausted")
            processes[name].timeout = min(20, remaining)
            return processes[name].request(text)

        for case in cases["initial8"]:
            for width in (1, 32):
                samples = case["samples"][:width]
                row = {"id": case["id"], "batch_width": width, "responses": {}}
                data["initial8_regression"].append(row)
                text = common.collier_request(case, samples, 1, 0, 1, check=True)
                for name in ("original", "diagnostic"):
                    row["responses"][name] = request(name, text)
                    kernel.save(result_path, data)
                original_response, diagnostic = row["responses"]["original"], row["responses"]["diagnostic"]
                row["successful_outputs_identical"] = (
                    original_response["stable"] is True and diagnostic["stable"] is True
                    and all(a["status"] == b["status"] == "success" and a["moments"] == b["moments"]
                            for a, b in zip(original_response["lanes"], diagnostic["lanes"]))
                    and len(original_response["lanes"]) == len(diagnostic["lanes"]) == width
                    and original_response["pole_check_errors"] == diagnostic["pole_check_errors"])
                if not row["successful_outputs_identical"]:
                    raise ValueError("initial-eight diagnostic instrumentation changed successful outputs")
                kernel.save(result_path, data)
        for case in cases["n4"]:
            for width in (1, 32):
                samples = case["samples"][:width]
                row = {"id": case["id"], "rank": case["rank"], "batch_width": width,
                       "iregi": {}, "collier": []}
                data["n4"].append(row)
                for mode in ("Hybrid", "PassarinoVeltman", "Ibp"):
                    row["iregi"][mode] = request("iregi", kernel.fortran_request(case, samples, mode, 0, 1))
                    kernel.save(result_path, data)
                row["iregi_mode_agreement"] = {
                    mode: common.comparison(response, row["iregi"]["Hybrid"], case, samples)
                    for mode, response in row["iregi"].items()}
                for mode in (1, 2):
                    for check in (False, True):
                        item = {"mode": mode, "command": "CHECK" if check else "BENCH"}
                        row["collier"].append(item)
                        item["response"] = request("diagnostic", common.collier_request(case, samples, mode, 0, 1, check=check))
                        kernel.save(result_path, data)
                        item["accepted_array_agreement"] = common.comparison(item["response"], row["iregi"]["Hybrid"], case, samples)
                        item["diagnostic_only_array_agreement"] = diagnostic_comparison(item["response"], row["iregi"]["Hybrid"], case, samples)
                        kernel.save(result_path, data)
        data["status"] = "diagnostic_complete"
    except Exception as error:
        data.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        for process in processes.values():
            process.close()
        os.sched_setaffinity(0, previous_affinity)
        data["elapsed_seconds"] = time.monotonic() - started
        data["guards_unchanged"] = all(kernel.digest(ROOT / p) == sha for p, sha in guards.items())
        if not data["guards_unchanged"]:
            data.update(status="failed", guard_error="source/binary/input changed during diagnostic")
        kernel.save(result_path, data)
    print(result_path)
    if data["status"] != "diagnostic_complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

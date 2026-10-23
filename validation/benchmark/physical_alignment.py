#!/usr/bin/env python3
"""Capture and validate equivalent physical pipelines; never infer timing parity."""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


physical = load("alignment_physical_comparison", ROOT / "validation/physical/compare_cli.py")
capture = load("alignment_madloop_capture", ROOT / "validation/physical/madloop/run.py")
previous_run = sys.modules.get("run")
try:
    sys.modules["run"] = capture
    madloop = load("alignment_madloop_benchmark", ROOT / "validation/physical/madloop/benchmark.py")
finally:
    if previous_run is None:
        del sys.modules["run"]
    else:
        sys.modules["run"] = previous_run


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finite_pair(value):
    if (not isinstance(value, (list, tuple)) or len(value) != 2
            or any(isinstance(component, bool) for component in value)):
        raise ValueError("expected one finite real/imaginary pair")
    return physical.number(value)


def fixture_and_input(case):
    fixture = ROOT / f"validation/physical/madloop/fixtures/{case}-helicity-1.json"
    sample = ROOT / f"validation/physical/{case}-cli-input.json"
    return json.loads(fixture.read_text()), json.loads(sample.read_text())


def contract(case):
    """Bind known physical equivalence to unchanged, already qualified assets."""
    info = physical.CASES[case]
    fixture, sample = fixture_and_input(case)
    group = fixture["selected_feynkit_group"]
    graph = next(graph for graph in fixture["graph_correspondence"] if graph["group"] == group)
    evidence_path = ROOT / "validation/physical/numerator-evidence.json"
    evidence = json.loads(evidence_path.read_text())
    assets = [f"examples/graphs/{info[0]}.dot", "fixtures/models/sm.json",
              f"validation/physical/{case}-cli-input.json",
              f"validation/physical/madloop/fixtures/{case}-helicity-1.json"]
    hashes = {name: digest(ROOT / name) for name in assets}
    if any(evidence["sha256"].get(name) != sha for name, sha in hashes.items()):
        raise ValueError("physical assets changed since the independent numerator correspondence")
    matches = [row for row in evidence["physical_numerator_tests"]["cases"] if row["id"] == case]
    if (len(matches) != 1 or matches[0]["selected_group"] != group
            or matches[0]["reference_factor"] != info[3]
            or evidence["physical_numerator_tests"]["failed"] != 0):
        raise ValueError("missing independently qualified oriented-graph correspondence")
    if (sample.get("snap", False) or sample.get("dimension_shift", 0) != 0
            or any(prop.get("power", 1) != 1 for prop in sample["propagators"])):
        raise ValueError("physical pipeline requires preserved unit-power D=4 inputs")
    if fixture["grouping"] or graph["symmetry_factor"] != 1 or graph["multiplier"] != 1:
        raise ValueError("unexpected graph grouping or graph factor")
    return {
        "kind": "equivalent-full-graph-numerical-pipelines-v1", "case": case,
        "graph": info[0], "madloop_graph": graph, "precision": "binary64",
        "working_bits": 53, "accuracy_bits": 53, "algorithm": "Hybrid",
        "input_policy": "Preserve", "helicity_index": fixture["helicity_index"],
        "helicities": fixture["metadata"]["helicity"], "color_components": [0] * info[1],
        "rust_rank": sample["rank"], "madloop_rank": graph["rank"],
        "routing_relation": fixture["feynkit_routing_relation"],
        "matched_tensor_workload": False,
        "rank_and_routing_policy": "Declared algorithmic choices; no tensor-stage timing ratio is valid",
        "common_output": ["finite", "UV+IR single pole", "IR double pole"],
        "untimed_output_adapters": {
            "rust": "[uv,ir,ir2,finite] -> [finite,uv+ir,ir2]; graph/color/fermion factors are already in the prepared numerator",
            "madloop": f"multiply stripped [finite,single,double] by {info[3]}",
            "optional_common_normalization": "divide by16*pi^2 outside both timers",
        },
        "timed_stages": {"rust": "numerical_end_to_end", "madloop": "total"},
        "timed_contract": "numerical coefficient construction, full requested reduction, native Laurent/tensor conversion where required, contraction, status checking and returned-buffer/cache cleanup",
        "excluded_from_both_timers": ["graph/Feynman-rule preparation", "external wavefunction preparation",
            "parameter parsing/packing", "final comparison adapters", "file and process transport"],
        "batch_policy": "Repeated identical captured point in separate lanes; reference loops over lanes and Rust propagates the batch",
        "cache_policy": "Structural plans/evaluators and scratch capacity may persist; numerical values recomputed per invocation; original IREGI numerical caches cleared after each sample",
        "physical_terms": {"excluded": fixture["excluded"], "included": ["bare UV/IR poles", "R1"]},
        "asset_sha256": hashes, "numerator_evidence_sha256": digest(evidence_path),
        "numerator_evidence": "validation/physical/numerator-evidence.json",
        "timing_parity_established": False,
    }


def validate_reference(case, reference):
    expected = contract(case)
    fixture, _ = fixture_and_input(case)
    graph = expected["madloop_graph"]
    group = graph["group"]
    if (reference.get("status") != "measured" or reference.get("precision") != "binary64"
            or reference.get("mode") != "Hybrid"
            or reference.get("workload_contract") != "madloop-selected-generated-graph-v1"
            or reference.get("graph") != graph or reference.get("helicity_index") != 1):
        raise ValueError("reference does not describe the selected binary64 graph pipeline")
    policy = reference.get("observed_input_policy", {})
    desired = {"onshell_iregi": False, "check": False, "threshold": 1e-6}
    graphs = policy.get("ordinary_graphs", {})
    ordinary = graphs.get(str(group), graphs.get(group))
    if (policy.get("name") != "preserve" or policy.get("timer") != desired
            or ordinary != desired or policy.get("checked_before_every_timed_step") is not True):
        raise ValueError("reference input preservation was not observed in both paths")
    if reference.get("observed_call_modes") != {"ctmode": 1, "iregimode": 2, "algorithm": "Hybrid"}:
        raise ValueError("reference call modes were not observed")
    correctness = reference.get("correctness", {})
    error = correctness.get("max_error")
    if (correctness.get("status") != "passed" or correctness.get("committed_fixture_input_identity_passed") is not True
            or isinstance(error, bool) or not isinstance(error, (int, float))
            or not math.isfinite(error) or not 0 <= error <= 1e-10):
        raise ValueError("ordinary preserved-path tensor/final-pole replay was not validated")
    recorded = reference["reference_record"]
    original = next(record for record in fixture["records"] if record["group"] == group)
    if (recorded.get("group") != group or recorded.get("rank") != graph["rank"]
            or recorded.get("propagators") != capture.CASES[case]["nloop"] or recorded.get("mode") != 1
            or recorded.get("stable") is not True or len(recorded.get("raw_result", [])) != 3
            or len(recorded.get("tensors", [])) != len(original["tensors"])
            or len(recorded.get("numerator", [])) != len(original["numerator"])):
        raise ValueError("reference graph output is incomplete or unstable")
    if [(entry["coefficient"], entry["laurent_slot"]) for entry in recorded["tensors"]] != [
            (entry["coefficient"], entry["laurent_slot"]) for entry in original["tensors"]]:
        raise ValueError("reference tensor ordering or completeness differs")
    for field in ["parameters", "couplings", "helicity", "evaluated_external_momenta",
                  "coefficient_construction_momenta", "wavefunctions", "wavefunction_momenta"]:
        madloop.exact_numeric_identity(reference["metadata"][field], fixture["metadata"][field], field)
    for field in ["shifts", "masses_squared", "mu"]:
        madloop.exact_numeric_identity(recorded[field], original[field], field)
    for value in [*recorded["raw_result"], *recorded["numerator"], recorded["probe_value"],
                  *(tensor["value"] for tensor in recorded["tensors"])]:
        finite_pair(value)
    if reference.get("provenance", {}).get("fixture_sha256") != expected["asset_sha256"][
            f"validation/physical/madloop/fixtures/{case}-helicity-1.json"]:
        raise ValueError("reference is not bound to the qualified fixture")
    return expected


def preserved_fixture(case, reference):
    validate_reference(case, reference)
    fixture, _ = fixture_and_input(case)
    fixture = copy.deepcopy(fixture)
    fixture["metadata"] = reference["metadata"]
    fixture["records"] = [reference["reference_record"]]
    fixture["graph_correspondence"] = [reference["graph"]]
    fixture["input_policy"] = "Preserve"
    fixture["qualification"] = "Selected ordinary preserved-input path, independently checked against timed replay; other graph records omitted"
    fixture["matched_reference_provenance"] = reference["provenance"]
    return fixture


def compare_rust_output(case, reference, output):
    expected = validate_reference(case, reference)
    settings = output.get("settings", {})
    if (output.get("precision_bits") != 53 or output.get("algorithm_requested") != "Hybrid"
            or output.get("precision_control", {}).get("accuracy_bits") != 53
            or settings.get("input_policy") != "Preserve" or settings.get("convention") != "OneLoop"
            or settings.get("rank") != expected["rust_rank"] or settings.get("dimension_shift") != 0
            or settings.get("propagators") != capture.CASES[case]["nloop"]
            or settings.get("tensor_weights") != "Components"
            or settings.get("powers") != [1] * capture.CASES[case]["nloop"]
            or output.get("poles") != ["uv1", "ir1", "ir2", "finite"]
            or output.get("graph", {}).get("name") != expected["graph"]):
        raise ValueError("Rust output does not meet the matched pipeline settings")
    fixture = preserved_fixture(case, reference)
    _, sample = fixture_and_input(case)
    rows = output.get("samples", [])
    if not rows or any(row.get("status") != "success" or row.get("id") != sample["id"] for row in rows):
        raise ValueError("failed, missing, or unexpected Rust sample")
    for row in rows:
        if not isinstance(row.get("integral"), list) or len(row["integral"]) != 4:
            raise ValueError("Rust graph contraction must retain all four native slots")
        for value in row["integral"]:
            finite_pair(value)
    comparisons = [physical.compare_physical(dict(output, samples=[row]), sample, fixture,
                                             physical.CASES[case], 1e-10) for row in rows]
    return dict(passed=all(row["passed"] for row in comparisons), lanes=comparisons,
                scope="All three graph Laurent coefficients; canonical full-tensor checks remain a separate required gate",
                timing_parity_established=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", choices=list(physical.CASES), default=list(physical.CASES))
    parser.add_argument("--capture", action="store_true", help="Build/run the original Fortran preserved-input timer")
    parser.add_argument("--cpu", type=int, default=16)
    parser.add_argument("--build-cpus", default="16,17")
    parser.add_argument("--batches", nargs="+", type=int, default=[1, 32])
    parser.add_argument("--repeats", type=int, default=21)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--target-ms", type=float, default=30)
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--output", type=Path, default=Path("target/physical-alignment/results.json"))
    args = parser.parse_args()
    if Path.cwd().resolve() != ROOT:
        parser.error(f"run from {ROOT}")
    cpus = {int(cpu) for cpu in args.build_cpus.split(",")}
    if (not cpus or not cpus.issubset(os.sched_getaffinity(0)) or args.cpu not in cpus
            or min(args.batches) < 1 or args.repeats < 3 or args.warmup < 0
            or not math.isfinite(args.timeout) or args.timeout <= 0
            or not math.isfinite(args.target_ms) or args.target_ms <= 0):
        parser.error("valid permitted CPUs, positive batches/timeout, repeats>=3 and warmup>=0 are required")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = dict(kind="physical-pipeline-alignment", rows=[dict(case=case, status="pending") for case in args.cases],
                  performance_qualified=False, timing_parity_established=False,
                  note="This helper establishes workload/reference contracts. Rust runtime correctness and quiet timing qualification remain separate.")
    def save():
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    save()
    for row in result["rows"]:
        case = row["case"]
        try:
            row["contract"] = contract(case)
            if args.capture:
                command = ["taskset", "--cpu-list", args.build_cpus, sys.executable,
                           "validation/physical/madloop/benchmark.py", "--case", case,
                           "--input-policy", "preserve", "--cpu", str(args.cpu), "--repeats", str(args.repeats),
                           "--warmup", str(args.warmup), "--target-ms", str(args.target_ms),
                           "--batch-widths", *map(str, args.batches)]
                row["command"] = command
                with (args.output.parent / f"{case}-capture.log").open("w") as log:
                    process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                    try:
                        exit_code = process.wait(timeout=args.timeout)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                        raise
                row["capture_exit_code"] = exit_code
                if exit_code:
                    raise RuntimeError("preserved reference build/run failed; see capture log and retained attempt")
            path = ROOT / f"target/physical/{case}-benchmark-preserve.json"
            if not path.exists():
                row["status"] = "needs-preserved-reference"
            else:
                reference = json.loads(path.read_text())
                validate_reference(case, reference)
                row.update(status="reference-aligned", reference_path=str(path.relative_to(ROOT)),
                           reference_sha256=digest(path), reference=reference)
                fixture_path = args.output.parent / f"{case}-preserved-reference.json"
                fixture_path.write_text(json.dumps(preserved_fixture(case, reference), indent=2) + "\n")
                row["preserved_fixture"] = str(fixture_path)
        except Exception as error:
            row.update(status="failed", error=f"{type(error).__name__}: {error}")
        save()
    print(args.output)
    return 1 if any(row["status"] == "failed" for row in result["rows"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())

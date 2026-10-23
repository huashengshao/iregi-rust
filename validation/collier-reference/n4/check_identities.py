"""Check N4 identities using polynomial coefficients prepared by Symbolica.

Rejected COLLIER moments remain diagnostics; independent identity agreement
cannot turn them into accepted results. No performance measurements are made.
"""
import argparse
import datetime
from fractions import Fraction
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import time


ROOT = Path.cwd()
SPEC = importlib.util.spec_from_file_location("collier_common", ROOT / "validation/collier-reference/run.py")
common = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(common)
kernel = common.kernel
BSPEC = importlib.util.spec_from_file_location("existing_tensor_index_enumeration", ROOT / "validation/pv-high-rank/compare_precision_oracle.py")
basis_module = importlib.util.module_from_spec(BSPEC)
BSPEC.loader.exec_module(basis_module)


def scalar_text(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"({value.numerator}/{value.denominator})"


def array(response, lane):
    row = response["lanes"][lane]
    return row["moments"] if row["status"] == "success" else row.get("diagnostic_moments")


def contract(polynomial, moments, rank):
    """Numerical dot product of Symbolica coefficients and existing moments."""
    indices = {tuple(exp): i for i, exp in enumerate(basis_module.tensor_basis(rank))}
    result = [0j] * 4
    for term in polynomial["terms"]:
        coefficient = float(Fraction(term["coefficient"]))
        moment = moments[indices[tuple(term["exponents"])]]
        for pole in range(4):
            result[pole] += coefficient * complex(*moment[pole])
    return result


def residual(lhs, rhs, unit):
    values = [{"pole": pole, "lhs": [a.real, a.imag], "rhs": [b.real, b.imag],
               "residual": [(a-b).real, (a-b).imag], "normalized_error": abs(a-b)/(unit+abs(b))}
              for pole, (a, b) in enumerate(zip(lhs, rhs))]
    worst = max(v["normalized_error"] for v in values)
    return {"status": "passed" if worst <= 1e-10 else "failed", "slots": values,
            "maximum_normalized_error": worst, "absolute_unit": unit, "tolerance": 1e-10}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagnostic", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cpu", type=int, default=26)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "target"):
        parser.error("new project target/ directory required")
    diagnostic = json.loads(args.diagnostic.read_text())
    if diagnostic.get("status") != "diagnostic_complete" or not diagnostic.get("guards_unchanged"):
        raise ValueError("complete guarded diagnostic receipt required")
    input_path = ROOT / "validation/collier-reference/extensions/n4-inputs.json"
    cases = common.load_inputs(input_path)
    cli = ROOT / "target/optimized/release/iregi-rust"
    model = ROOT / "fixtures/models/phi3.json"
    binaries = {name: diagnostic["binaries"][name] for name in ("diagnostic", "iregi")}
    guard_paths = [Path(__file__).resolve(), args.diagnostic.resolve(), input_path, cli, model,
                   ROOT / "validation/collier-reference/run.py", ROOT / "validation/benchmark/run.py",
                   ROOT / "validation/pv-high-rank/compare_precision_oracle.py",
                   ROOT / "docs/research/collier-n4-identities.md",
                   *(ROOT / info["path"] for info in binaries.values()),
                   *sorted((ROOT / "crates/iregi-prepare").rglob("*.rs")),
                   ROOT / "crates/iregi-cli/src/main.rs"]
    guards = {str(p.relative_to(ROOT)): kernel.digest(p) for p in guard_paths}
    for info in binaries.values():
        if kernel.digest(ROOT / info["path"]) != info["sha256"]:
            raise ValueError("reference binary changed")
    output.mkdir(parents=True)
    for p in guard_paths:
        if p.suffix in (".py", ".rs", ".md"):
            dest = output / "sources" / p.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest)
    data = {"kind": "collier-n4-symbolica-identity-checks", "status": "running",
            "date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "cpu": args.cpu,
            "performance_evidence": False, "timeout_seconds": 120, "tolerance": 1e-10,
            "cli_provenance": "Existing executable hash pinned; current CLI/preparation source inventory is contextual, not a claim of a new source-matched build",
            "source_binary_input_guards": guards,
            "scope": "All8 fixed N4rank0..3 batch1/32 rows; accepted IREGI and separately labelled raw rejected COLLIER diagnostics",
            "dimensional_caveat": "Trace defect is epsilon times UV/IR-finite D6 box scalar/vector, so no finite correction at ranks2/3 on this massive Euclidean domain; rank4 excluded",
            "polynomials": {}, "pinched_triangle_inputs": [], "pinched_triangle_responses": {}, "rows": []}
    path = output / "results.json"
    kernel.save(path, data)
    deadline = time.monotonic() + 120
    started = time.monotonic()
    previous_affinity = os.sched_getaffinity(0)
    processes = {}
    try:
        os.sched_setaffinity(0, {args.cpu})

        def prepare(name, numerator):
            graph = output / f"{name}.dot"
            graph.write_text('digraph box { graph [num="' + numerator + '", overall_factor="1"]; '
                             'edge [particle="phi"]; ext [style=invis]; ext -> a; b -> ext; c -> ext; d -> ext; '
                             'a -> b [lmb_id=0]; b -> c; c -> d; d -> a; }\n')
            command = [str(cli), "prepare", str(graph), "--model", str(model)]
            completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                       timeout=min(20, max(.001, deadline-time.monotonic())))
            (output / f"{name}.stderr.log").write_text(completed.stderr)
            (output / f"{name}.prepared.json").write_text(completed.stdout)
            if completed.returncode != 0:
                raise ValueError(f"Symbolica preparation failed for {name}")
            prepared = json.loads(completed.stdout)
            data["polynomials"][name] = {"input": numerator, "prepared": prepared,
                                         "dot_sha256": kernel.digest(graph), "command": command}
            return prepared

        trace_text = "(iregi::q0^2-iregi::q1^2-iregi::q2^2-iregi::q3^2)"
        trace = prepare("trace", trace_text)
        vectors = [prepare(f"vector-{nu}", f"iregi::q{nu}") for nu in range(4)]
        trace_vectors = [prepare(f"trace-vector-{nu}", trace_text+f"*iregi::q{nu}") for nu in range(4)]
        zero_text = f"({trace_text}-(({trace_text}+iregi::qperp2-iregi::m0sq)+iregi::m0sq-iregi::qperp2))"
        zeros = [prepare("denominator-cancellation", zero_text)]
        zeros += [prepare(f"denominator-cancellation-{nu}", zero_text+f"*iregi::q{nu}") for nu in range(4)]
        if any(p["terms"] or p["numerator"] != "0" for p in zeros):
            raise ValueError("Symbolica did not establish the exact integrand cancellation")
        translations = []
        differences = []
        samples = cases[0]["samples"]
        for lane, sample in enumerate(samples):
            translations.append([prepare(f"pinch0-l{lane}-q{nu}",
                                         f"iregi::q{nu}-({scalar_text(sample['shifts'][1][nu])})")
                                 for nu in range(4)])
            differences.append([prepare(f"difference-l{lane}-p{i}",
                                        "2*("+"+".join(f"({scalar_text(p[nu] if nu == 0 else -p[nu])})*iregi::q{nu}"
                                                       for nu in range(4))+")")
                                for i, p in enumerate(sample["shifts"][1:], 1)])
        processes = {name: kernel.Process(ROOT / info["path"], name, output, 20)
                     for name, info in binaries.items()}
        for pinch in range(4):
            triangle_samples = []
            for sample in samples:
                kept = [i for i in range(4) if i != pinch]
                origin = sample["shifts"][kept[0]]
                triangle_samples.append({"mu": sample["mu"], "masses": [sample["masses"][i] for i in kept],
                                         "shifts": [[p-o for p, o in zip(sample["shifts"][i], origin)] for i in kept]})
            case = {"id": f"n4-pinch{pinch}-translated", "n": 3, "rank": 1, "samples": triangle_samples}
            data["pinched_triangle_inputs"].append(case)
            data["pinched_triangle_responses"][str(pinch)] = {}
            for name in processes:
                text = (common.collier_request(case, triangle_samples, 1, 0, 1, check=True) if name == "diagnostic"
                        else kernel.fortran_request(case, triangle_samples, "Hybrid", 0, 1))
                processes[name].timeout = min(20, max(.001, deadline-time.monotonic()))
                data["pinched_triangle_responses"][str(pinch)][name] = processes[name].request(text)
                kernel.save(path, data)
        for source_row in diagnostic["n4"]:
            case = next(c for c in cases if c["id"] == source_row["id"])
            width = source_row["batch_width"]
            collier = next(x["response"] for x in source_row["collier"] if x["mode"] == 1 and x["command"] == "CHECK")
            responses = {"iregi": source_row["iregi"]["Hybrid"], "diagnostic": collier}
            for name, response in responses.items():
                row = {"id": case["id"], "batch_width": width, "engine": name,
                       "accepted": response["stable"], "qualifies": name == "iregi" and response["stable"],
                       "scope": "accepted reference" if name == "iregi" else "raw diagnostic, never promotes rejected COLLIER status", "lanes": []}
                data["rows"].append(row)
                for lane, sample in enumerate(samples[:width]):
                    moments = array(response, lane)
                    if moments is None:
                        row["lanes"].append({"status": "unavailable"})
                        continue
                    Q = max(1., sample["mu"], *(abs(x) for p in sample["shifts"] for x in p),
                            *(math.sqrt(math.hypot(*m)) for m in sample["masses"]))
                    checks = []
                    triangle = {i: array(data["pinched_triangle_responses"][str(i)][name], lane) for i in range(4)}
                    if any(v is None for v in triangle.values()):
                        row["lanes"].append({"status": "unavailable", "reason": "pinched triangle raw moments absent"})
                        continue
                    c0 = [complex(*v) for v in triangle[0][0]]
                    d0 = [complex(*v) for v in moments[0]]
                    if case["rank"] >= 1:
                        for i, p in enumerate(sample["shifts"][1:], 1):
                            lhs = contract(differences[lane][i-1], moments, case["rank"])
                            f = p[0]*p[0]-sum(x*x for x in p[1:])-sample["masses"][i][0]+sample["masses"][0][0]
                            rhs = [complex(*triangle[i][0][pole])-c0[pole]-f*d0[pole] for pole in range(4)]
                            checks.append({"identity": f"denominator-difference-p{i}", **residual(lhs, rhs, Q**-2)})
                    if case["rank"] >= 2:
                        lhs = contract(trace, moments, case["rank"])
                        rhs = [c0[pole]+sample["masses"][0][0]*d0[pole] for pole in range(4)]
                        checks.append({"identity": "rank2-metric-trace", **residual(lhs, rhs, Q**-2)})
                    if case["rank"] >= 3:
                        for nu in range(4):
                            lhs = contract(trace_vectors[nu], moments, case["rank"])
                            cvec = contract(translations[lane][nu], triangle[0], 1)
                            dvec = contract(vectors[nu], moments, case["rank"])
                            rhs = [cvec[pole]+sample["masses"][0][0]*dvec[pole] for pole in range(4)]
                            checks.append({"identity": f"rank3-metric-trace-q{nu}", **residual(lhs, rhs, Q**-1)})
                    for index, exp in enumerate(basis_module.tensor_basis(case["rank"])):
                        if exp[0] % 2:
                            checks.append({"identity": f"time-reflection-moment{index}",
                                           **residual([complex(*v) for v in moments[index]], [0j]*4,
                                                      Q**(4+sum(exp)-8))})
                        checks.append({"identity": f"UV-finiteness-moment{index}",
                                       **residual([complex(*moments[index][0])], [0j], Q**(4+sum(exp)-8))})
                    row["lanes"].append({"status": "passed" if all(c["status"] == "passed" for c in checks) else "failed",
                                         "input_status": response["lanes"][lane]["status"], "checks": checks})
                row["identity_status"] = "passed" if all(l["status"] == "passed" for l in row["lanes"]) else "failed"
                kernel.save(path, data)
        data["status"] = "identity_checks_complete" if all(r["identity_status"] == "passed" for r in data["rows"]) else "failed"
    except Exception as error:
        data.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        for process in processes.values():
            process.close()
        os.sched_setaffinity(0, previous_affinity)
        data["elapsed_seconds"] = time.monotonic()-started
        data["guards_unchanged"] = all(kernel.digest(ROOT/p) == sha for p, sha in guards.items())
        if not data["guards_unchanged"]:
            data.update(status="failed", guard_error="source/binary/input changed during identity checks")
        kernel.save(path, data)
    print(path)
    if data["status"] != "identity_checks_complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

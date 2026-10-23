"""Prepare N5 identity witnesses with the existing Symbolica CLI; no reduction.

This source candidate has not been executed.  Index enumeration and input
transport are Python; every polynomial, invariant and shift is prepared by
Symbolica through the existing Rust CLI.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
PARENT = ROOT/"validation/collier-reference/shared/attempt004"
sys.path.insert(0, str(PARENT/"producer"))
import support
SPEC = importlib.util.spec_from_file_location("existing_tensor_basis", ROOT/"validation/pv-high-rank/compare_precision_oracle.py")
basis_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(basis_module)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def square_text(vector):
    """Construct input syntax only; Symbolica evaluates the expression."""
    return "+".join(("" if nu == 0 else "-")+f"({value})^2" for nu, value in enumerate(vector))


def dot_text(vector):
    return "+".join(("" if nu == 0 else "-")+f"({value})*iregi::q{nu}" for nu, value in enumerate(vector))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--cpu", type=int, default=26)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT/"target") or args.cpu not in os.sched_getaffinity(0):
        parser.error("new project target directory and available CPU required")
    document = ROOT/"docs/research/collier-n5-identities.md"
    local = {str(p.relative_to(ROOT)): digest(p) for p in [Path(__file__).resolve(), document]}
    review = json.loads(args.review.read_text())
    if review.get("status") != "source_review_passed" or review.get("blockers") != [] or review.get("sources_sha256") != local:
        raise ValueError("independent source review must bind producer and analytic plan")
    qualification = json.loads((PARENT/"qualification.json").read_text())
    for name in ("capture", "inputs"):
        entry = qualification["artifacts"][name]
        if digest(ROOT/entry["path"]) != entry["sha256"]:
            raise ValueError("parent durable artifact changed")
    parent = json.loads(gzip.decompress((PARENT/"capture.json.gz").read_bytes()))
    inputs = json.loads(gzip.decompress((PARENT/"inputs.json.gz").read_bytes()))
    if parent.get("guards_unchanged") is not True:
        raise ValueError("guarded parent required")
    n5_rows = [r for r in parent["rows"] if r["n"] == 5]
    if len(n5_rows) != 6 or any(r["status"] != "accepted-COLI" for r in n5_rows):
        raise ValueError("this proposal targets exactly the six admitted N5 rows")
    cases = [c for c in parent["input_cases"] if c["n"] == 5]
    case = next(c for c in cases if c["rank"] == 2)
    original_keys = [support.proof_key(s, 5) for s in case["samples"]]
    if any([support.proof_key(s, 5) for s in c["samples"]] != original_keys for c in cases):
        raise ValueError("N5 rank families do not share unchanged input lanes")
    unique = list({support.proof_key(s, 5): s for s in case["samples"]}.items())
    if len(unique) != 3:
        raise ValueError("exactly three existing kinematic branches required")
    cli, model = ROOT/"target/optimized/release/iregi-rust", ROOT/"fixtures/models/phi3.json"
    guarded = [Path(__file__).resolve(), document, PARENT/"capture.json.gz", PARENT/"inputs.json.gz",
               PARENT/"qualification.json", PARENT/"producer/support.py", cli, model,
               ROOT/"validation/pv-high-rank/compare_precision_oracle.py", args.review.resolve()]
    guards = {str(p.relative_to(ROOT)): digest(p) for p in guarded}
    output.mkdir(parents=True)
    data = {"kind": "n5-symbolica-independent-identity-preparation", "status": "running",
            "performance_evidence": False, "reference_reduction_performed": False, "cpu": args.cpu,
            "cap_seconds": 60, "request_cap_seconds": 20, "guards": guards,
            "cli_provenance": "Existing executable hash pinned; no new source-matched CLI build claimed",
            "parent_n5_rows": [{k: r[k] for k in ("id", "rank", "batch_width", "status")} for r in n5_rows],
            "original32_proof_keys": original_keys, "polynomials": {}, "aliases": {}, "branches": [],
            "pinched_cases": [], "routing_cases": [], "reference_request_inventory": [],
            "dimensional_scope": "Positive Feynman polynomial, real positive masses; epsilon times UV/IR-finite D6 N5 scalar has no Laurent contribution through finite"}
    path = output/"preparation.json"
    support.kernel.save(path, data)
    started = time.monotonic()
    deadline = started+60
    previous = os.sched_getaffinity(0)
    try:
        os.sched_setaffinity(0, {args.cpu})

        def prepare(label, expression):
            data["aliases"][label] = expression
            if expression in data["polynomials"]:
                return data["polynomials"][expression]["prepared"]
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                raise TimeoutError("fixed Symbolica-preparation deadline exhausted")
            ordinal = len(data["polynomials"])
            dot = output/f"polynomial-{ordinal:04d}.dot"
            dot.write_text('digraph witness { graph [num="'+expression+'", overall_factor="1"]; '
                           'edge [particle="phi"]; ext [style=invis]; ext -> a; a -> b [lmb_id=0]; '
                           'a -> b; b -> ext; }\n')
            command = [str(cli), "prepare", str(dot), "--model", str(model)]
            try:
                child = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                       timeout=min(20, remaining))
            except subprocess.TimeoutExpired as error:
                def decoded(value):
                    return value.decode(errors="replace") if isinstance(value, bytes) else (value or "")
                (output/f"polynomial-{ordinal:04d}.prepared.json").write_text(decoded(error.stdout))
                (output/f"polynomial-{ordinal:04d}.stderr.log").write_text(decoded(error.stderr))
                raise TimeoutError(f"Symbolica preparation timed out for {label}; partial output retained") from error
            (output/f"polynomial-{ordinal:04d}.prepared.json").write_text(child.stdout)
            (output/f"polynomial-{ordinal:04d}.stderr.log").write_text(child.stderr)
            if child.returncode != 0:
                raise ValueError(f"Symbolica preparation failed for {label}")
            prepared = json.loads(child.stdout)
            data["polynomials"][expression] = {"prepared": prepared, "command": command,
                "dot_sha256": digest(dot), "exit_code": child.returncode}
            support.kernel.save(path, data)
            return prepared

        def constant(label, expression):
            prepared = prepare(label, expression)
            if not prepared["terms"]:
                return "0"
            if len(prepared["terms"]) != 1 or prepared["terms"][0]["exponents"] != [0]*4:
                raise ValueError("Symbolica did not produce an exact rational constant")
            return support.scalar_text(prepared["terms"][0]["coefficient"])

        trace = "(iregi::q0^2-iregi::q1^2-iregi::q2^2-iregi::q3^2)"
        prepare("metric-trace-rank2", trace)
        for nu in range(4):
            prepare(f"vector-{nu}", f"iregi::q{nu}")
        for branch, (proof_key, sample) in enumerate(unique):
            proof = inputs["sample_domain_proofs"][proof_key]
            if support.exact_number(proof["positive_mass_polynomial_lower_bound"]) <= 0:
                raise ValueError("positive Feynman-polynomial domain required")
            branch_data = {"id": branch, "sample": sample, "proof_key": proof_key, "parent_domain_proof": proof,
                           "denominator_differences": [], "translation_monomials": {}}
            data["branches"].append(branch_data)
            d0 = f"({trace}+iregi::qperp2-({sample['masses'][0][0]}))"
            cancellation = prepare(f"trace-cancellation-{branch}",
                f"({trace})-(({d0})+({sample['masses'][0][0]})-iregi::qperp2)")
            if cancellation["terms"]:
                raise ValueError("Symbolica trace cancellation is nonzero")
            for i in range(1, 5):
                p = sample["shifts"][i]
                f_expr = f"({square_text(p)})-({sample['masses'][i][0]})+({sample['masses'][0][0]})"
                f = constant(f"f-{branch}-{i}", f_expr)
                linear = f"2*({dot_text(p)})"
                prepare(f"difference-{branch}-{i}", linear)
                for nu in range(4):
                    prepare(f"difference-{branch}-{i}-q{nu}", f"({linear})*iregi::q{nu}")
                di = f"({trace}+iregi::qperp2+({linear})+({square_text(p)})-({sample['masses'][i][0]}))"
                zero = prepare(f"difference-cancellation-{branch}-{i}", f"({di})-({d0})-({linear})-({f})")
                if zero["terms"]:
                    raise ValueError("Symbolica denominator-difference cancellation is nonzero")
                branch_data["denominator_differences"].append({"i": i, "f": f,
                    "linear_polynomial": linear, "exact_cancellation": zero})
            origin = sample["shifts"][1]
            for alpha in basis_module.tensor_basis(2):
                expression = "*".join(f"(iregi::q{nu}-({origin[nu]}))^{power}"
                                      for nu, power in enumerate(alpha) if power) or "1"
                label = f"translation-{branch}-"+"-".join(map(str, alpha))
                prepare(label, expression)
                branch_data["translation_monomials"]["-".join(map(str, alpha))] = expression
        originals = [sample for _, sample in unique]
        for pinch in range(5):
            samples = []
            for branch, sample in enumerate(originals):
                kept = [i for i in range(5) if i != pinch]
                origin = sample["shifts"][kept[0]]
                shifts = [[constant(f"pinch-{pinch}-{branch}-{i}-{nu}", f"({sample['shifts'][i][nu]})-({origin[nu]})")
                           for nu in range(4)] for i in kept]
                samples.append(support.exact_sample({"mu": sample["mu"], "shifts": shifts,
                    "masses": [sample["masses"][i] for i in kept]}, 4))
            data["pinched_cases"].append({"id": f"n5-pinch{pinch}-rank1", "n": 4, "rank": 1, "samples": samples,
                "domain": "Inherited parent positive lower bound; deleting a denominator and translating routing preserves all retained pair distances"})
        for name, order in (("cyclic-origin1", [1, 2, 3, 4, 0]), ("reversed-nonzero", [0, 4, 3, 2, 1])):
            samples = []
            for branch, sample in enumerate(originals):
                origin = sample["shifts"][order[0]]
                shifts = [[constant(f"route-{name}-{branch}-{i}-{nu}", f"({sample['shifts'][i][nu]})-({origin[nu]})")
                           for nu in range(4)] for i in order]
                samples.append(support.exact_sample({"mu": sample["mu"], "shifts": shifts,
                    "masses": [sample["masses"][i] for i in order]}, 5))
            data["routing_cases"].append({"id": "n5-"+name, "n": 5, "rank": 2, "samples": samples,
                "denominator_order": order, "numerator_map": "q_original=q_local-p1" if order[0] == 1 else "q_original=q_local"})
        for verification_case in [*data["pinched_cases"], *data["routing_cases"]]:
            groups = support.scale_groups(verification_case, verification_case["samples"])
            policies = [("iregi", mode) for mode in ("Hybrid", "PassarinoVeltman", "Ibp")]
            if verification_case["n"] == 5:
                policies.append(("generic", 1))
            for engine, mode in policies:
                for group in groups:
                    text = (support.original_iregi_request(verification_case, group["samples"], mode) if engine == "iregi"
                            else support.collier_request(verification_case, group["samples"], mode))
                    data["reference_request_inventory"].append({"case": verification_case["id"], "engine": engine,
                        "mode": mode, "scale": group["scale"], "lane_indices": group["lane_indices"], "wire_request": text,
                        "wire_request_sha256": hashlib.sha256(text.encode()).hexdigest()})
        if len(data["reference_request_inventory"]) != 46:
            raise ValueError("exact46-request identity/routing proposal changed")
        data["status"] = "prepared-not-numerically-qualified"
    except Exception as error:
        data.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        os.sched_setaffinity(0, previous)
        data["elapsed_seconds"] = time.monotonic()-started
        data["guards_unchanged"] = all(digest(ROOT/p) == sha for p, sha in guards.items())
        if not data["guards_unchanged"]:
            data.update(status="failed", error="source/input/CLI guard changed")
        support.kernel.save(path, data)
    print(path)
    if data["status"] != "prepared-not-numerically-qualified":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

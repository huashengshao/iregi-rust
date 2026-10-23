"""Prepare exact shared-domain families and Symbolica mass-domain witnesses.

Source candidate. This performs input preparation only, never a reduction.
"""
import argparse
import copy
from fractions import Fraction
import json
import os
from pathlib import Path
import subprocess
import time

import support


ROOT = Path.cwd()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cpu", type=int, default=26)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "target"):
        parser.error("new project target/ directory required")
    source_paths = {
        "initial8": ROOT / "validation/benchmark/baseline-6b24c03-licensed/results-inputs.json",
        "n4": ROOT / "validation/collier-reference/extensions/n4-inputs.json",
        "conditioned": ROOT / "validation/public-highpoint/fixture-conditioned_masses.json",
    }
    cli = ROOT / "target/optimized/release/iregi-rust"
    model = ROOT / "fixtures/models/phi3.json"
    guard_paths = [Path(__file__).resolve(), ROOT / "validation/collier-reference/shared/support.py",
                   cli, model, *source_paths.values()]
    guards = {str(p.relative_to(ROOT)): support.kernel.digest(p) for p in guard_paths}
    output.mkdir(parents=True)
    data = {"kind": "collier-shared-source-defined-inputs", "status": "running",
            "dimension": "D=4-2epsilon denominators, four-dimensional Cartesian numerator moments",
            "cli_provenance": "Existing executable hash pinned; no new source-matched CLI build claimed",
            "source_binary_guards": guards, "cases": [], "sample_domain_proofs": {}, "constant_preparations": {}}
    path = output / "inputs.json"
    support.kernel.save(path, data)
    deadline = time.monotonic()+120
    started = time.monotonic()
    previous = os.sched_getaffinity(0)
    try:
        os.sched_setaffinity(0, {args.cpu})
        for label in ("initial8", "n4"):
            for source_case in json.loads(source_paths[label].read_text()):
                case = copy.deepcopy(source_case)
                case["samples"] = [support.exact_sample(s, case["n"]) for s in case["samples"]]
                case.update(dimension_shift=0, powers=[1]*case["n"], family_source=label,
                            unique_kinematics=32, lane_policy="unchanged original32 lanes")
                data["cases"].append(case)
        fixture = json.loads(source_paths["conditioned"].read_text())
        if len(fixture["samples"]) != 3:
            raise ValueError("retained conditioned fixture changed its three-row envelope")
        for n in (5, 6, 7):
            unique = []
            for source in fixture["samples"]:
                props = source["propagators"][:n]
                if len(props) != n or any(p.get("power", 1) != 1 for p in props):
                    raise ValueError("retained ordinary conditioned topology changed")
                unique.append(support.exact_sample({"id": source["id"], "mu": source["mu"],
                                                     "shifts": [p["shift"] for p in props],
                                                     "masses": [p["mass_squared"] for p in props]}, n))
            for rank in (0, 1, 2):
                data["cases"].append({"id": f"n{n}-r{rank}-conditioned-cycle32", "n": n, "rank": rank,
                                      "dimension_shift": 0, "powers": [1]*n,
                                      "family_source": "retained conditioned-mass prefixes; explicit three-row cycle",
                                      "unique_kinematics": 3,
                                      "lane_policy": "base/scaled-by-two/mass-deformed in source order repeated cyclically to32 lanes; no claim of32 distinct branches",
                                      "samples": [copy.deepcopy(unique[lane % 3]) for lane in range(32)]})

        def constant(expression):
            cache = data["constant_preparations"]
            if expression in cache:
                return cache[expression]["value"]
            index = len(cache)
            dot = output / f"constant-{index:04d}.dot"
            dot.write_text('digraph witness { graph [num="'+expression+'", overall_factor="1"]; '
                           'edge [particle="phi"]; ext [style=invis]; ext -> a; a -> b [lmb_id=0]; '
                           'a -> b; b -> ext; }\n')
            completed = subprocess.run([str(cli), "prepare", str(dot), "--model", str(model)],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                       timeout=min(20, max(.001, deadline-time.monotonic())))
            (output/f"constant-{index:04d}.stderr.log").write_text(completed.stderr)
            (output/f"constant-{index:04d}.prepared.json").write_text(completed.stdout)
            if completed.returncode != 0:
                raise ValueError("Symbolica constant preparation failed")
            prepared = json.loads(completed.stdout)
            if not prepared["terms"]:
                value = "0"
            elif (len(prepared["terms"]) == 1 and prepared["terms"][0]["exponents"] == [0]*4):
                value = support.scalar_text(prepared["terms"][0]["coefficient"])
            else:
                raise ValueError("domain witness did not simplify to a rational scalar")
            cache[expression] = {"value": value, "prepared": prepared, "dot_sha256": support.kernel.digest(dot)}
            return value

        for case in data["cases"]:
            for sample in case["samples"]:
                key = support.proof_key(sample, case["n"])
                if key in data["sample_domain_proofs"]:
                    continue
                invariants = []
                for a, b in support.invariant_pairs(case["n"]):
                    expression = "+".join(("" if nu == 0 else "-")+
                                          f"(({sample['shifts'][a][nu]})-({sample['shifts'][b][nu]}))^2"
                                          for nu in range(4))
                    invariants.append(constant(expression))
                minimum_mass = min((m[0] for m in sample["masses"]), key=Fraction)
                maximum_positive = max(["0", *invariants], key=Fraction)
                bound = constant(f"({minimum_mass})-({maximum_positive})/2")
                if Fraction(bound) <= 0:
                    raise ValueError("fixed input has no positive conservative finite-domain witness")
                data["sample_domain_proofs"][key] = {
                    "algebra_provider": "Symbolica via existing iregi-rust prepare CLI",
                    "invariant_pairs": support.invariant_pairs(case["n"]), "exact_invariants": invariants,
                    "minimum_squared_mass": minimum_mass, "maximum_positive_interval": maximum_positive,
                    "positive_mass_polynomial_lower_bound": bound,
                    "bound": "F(x)>=min(m_i²)-max(0,s_ij)/2>0; sum pair weights<=1/2",
                    "dimension_shift": 0, "powers": [1]*case["n"]}
            support.kernel.save(path, data)
        data["status"] = "prepared-not-numerically-qualified"
    except Exception as error:
        data.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        os.sched_setaffinity(0, previous)
        data["elapsed_seconds"] = time.monotonic()-started
        data["guards_unchanged"] = all(support.kernel.digest(ROOT/p) == sha for p, sha in guards.items())
        if not data["guards_unchanged"]:
            data.update(status="failed", error="source/binary guard changed")
        support.kernel.save(path, data)
    print(path)
    if data["status"] != "prepared-not-numerically-qualified":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

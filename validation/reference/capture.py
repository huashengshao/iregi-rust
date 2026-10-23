"""Regenerate independently sourced oracle fixtures and validate the copy-only repair."""
import argparse
import cmath
import copy
import json
import math
from pathlib import Path
import subprocess

ROOT = Path.cwd()
OUT = ROOT / "target/reference"
HERE = ROOT / "validation/reference"

def sample(name, topology, rank=0, mode=2, api="tensor", powers=None, idim=0):
    shifts = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0.2, 1.1, 0], [0, -0.3, 0.4, 1.2]]
    masses = [4, 9, 16, 25]
    return {"id": name, "api": api, "mode": mode, "rank": rank,
            "dimension_shift": idim, "mu": 3, "snap": False, "threshold": 1e-6,
            "propagators": [{"shift": shifts[i], "mass_squared": [masses[i], 0],
                              "power": powers[i] if powers else 1} for i in range(topology)]}

def encode(case):
    header = (f"EVAL {case['id']} {case['api']} {case['mode']} {len(case['propagators'])} "
              f"{case['rank']} {case['dimension_shift']} {case['mu']} {int(case['snap'])} {case['threshold']}")
    rows = [" ".join(map(str, p["shift"] + p["mass_squared"] + [p["power"]]))
            for p in case["propagators"]]
    return "\n".join([header, *rows]) + "\n"

def evaluate(executable, cases, allow_stop=False):
    process = subprocess.run([str(executable)], input="".join(map(encode, cases)) + "QUIT\n",
                             capture_output=True, text=True, cwd=ROOT, timeout=120)
    results = [json.loads(line[7:]) for line in process.stdout.splitlines() if line.startswith("RESULT ")]
    if not allow_stop and (process.returncode or len(results) != len(cases)):
        raise RuntimeError(f"Reference failed ({process.returncode}): {process.stdout}\n{process.stderr}")
    return results, process

def close(actual, expected, tolerance=1e-10):
    if abs(actual - expected) > tolerance * max(1, abs(expected)):
        raise AssertionError(f"{actual} != {expected}")

def values(result):
    return [[complex(*x) for x in moment] for moment in result["moments"]]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-fixtures", action="store_true")
    args = parser.parse_args()
    ordinary = [sample(name, n) for n, name in enumerate(["A0", "B0", "C0", "D0"], 1)]
    for n, topology in [(2, "bubble"), (3, "triangle")]:
        for rank in [1, 2, 3]:
            for mode in [0, 1, 2]:
                ordinary.append(sample(f"{topology}_rank{rank}_mode{mode}", n, rank=rank, mode=mode))
    scaleless = sample("scaleless_B0", 2)
    for p in scaleless["propagators"]:
        p["shift"] = [0, 0, 0, 0]
        p["mass_squared"] = [0, 0]
    ordinary.append(scaleless)
    complex_case = sample("complex_triangle_rank2", 3, rank=2)
    for p in complex_case["propagators"]:
        p["mass_squared"][1] = -0.01 * p["mass_squared"][0]
    ordinary.append(complex_case)
    untouched, _ = evaluate(OUT / "iregi-reference-original", ordinary)
    repaired, _ = evaluate(OUT / "iregi-reference", ordinary)
    if untouched != repaired:
        raise AssertionError("Repair changed ordinary tensor outputs")
    if not all(r["stable"] for r in repaired):
        raise AssertionError("Ordinary fixture unexpectedly unstable")
    # Analytic scalar normalizations, without consulting any Rust implementation.
    ipi2 = complex(0, math.pi ** 2)
    a = 0.5772156649015328606 + math.log(math.pi)
    av = values(repaired[0])[0]
    close(av[0], 4 * ipi2)
    close(av[3], 4 * ipi2 * (1 + math.log(9 / 4) - a))
    sv = values(repaired[-2])[0]
    close(sv[0], ipi2)
    close(sv[1], -ipi2)
    close(sv[2], 0)
    close(sv[3], 0)
    # Every entry of the repaired table equals its exact binomial coefficient.
    table = subprocess.check_output([str(OUT / "factorial-table-check")], text=True, cwd=ROOT)
    for row in table.splitlines():
        i, j, value = row.split()
        close(float(value), math.comb(int(i) + int(j) - 1, int(j)), 0)
    reproduction = sample("general_initialization_stop", 1, api="general")
    failed, stop = evaluate(OUT / "iregi-reference-original", [reproduction], allow_stop=True)
    if failed or "i > 12" not in stop.stdout:
        raise AssertionError("Original generalized-interface initialization failure was not reproduced")
    general = [sample("general_unit_bubble_rank2", 2, rank=2, api="general"),
               sample("general_unit_triangle_rank3", 3, rank=3, api="general"),
               sample("A0_power2", 1, api="general", powers=[2]),
               sample("B0_power2_1", 2, api="general", powers=[2, 1]),
               sample("C0_power2_1_1_rank2", 3, rank=2, api="general", powers=[2, 1, 1]),
               sample("A0_dim6_power2", 1, api="general", powers=[2], idim=2),
               sample("C0_dim6", 3, api="general", idim=2)]
    generalized, _ = evaluate(OUT / "iregi-reference", general)
    if not all(r["stable"] for r in generalized):
        raise AssertionError("Generalized fixture unexpectedly unstable")
    by_id = {r["id"]: r for r in repaired}
    for result, key in [(generalized[0], "bubble_rank2_mode2"),
                        (generalized[1], "triangle_rank3_mode2")]:
        for got, expected in zip(values(result), values(by_id[key])):
            for x, y in zip(got, expected):
                close(x, y)
    derivative = values(generalized[2])[0]
    close(derivative[0], ipi2)
    close(derivative[3], ipi2 * (math.log(9 / 4) - a))
    for x, y in zip(values(generalized[5])[0], av):
        close(x, -math.pi * y)
    # d/d(m_1^2) B0 = B0 with the first propagator squared.
    plus, minus = copy.deepcopy(ordinary[1]), copy.deepcopy(ordinary[1])
    plus["id"], minus["id"] = "mass_plus", "mass_minus"
    h = 1e-3
    plus["propagators"][0]["mass_squared"][0] += h
    minus["propagators"][0]["mass_squared"][0] -= h
    differentiated, _ = evaluate(OUT / "iregi-reference-original", [plus, minus])
    for x, y, expected in zip(values(differentiated[0])[0], values(differentiated[1])[0],
                              values(generalized[3])[0]):
        close((x-y)/(2*h), expected, 2e-8)
    scalar_real = sample("scalar_B0_power2_1", 2, api="scalar", powers=[2, 1])
    scalar_complex = sample("scalar_complex_A0_power2", 1, api="scalar", powers=[2])
    scalar_complex["propagators"][0]["mass_squared"][1] = -0.04
    scalars, _ = evaluate(OUT / "iregi-reference-original", [scalar_real, scalar_complex])
    for x, y in zip(values(scalars[0])[0], values(generalized[3])[0]):
        close(x, y)
    close(values(scalars[1])[0][0], ipi2)
    close(values(scalars[1])[0][3], ipi2 * (cmath.log(9 / complex(4, -0.04)) - a))
    # Changing scale and request order cannot leak cached numerical values.
    changed_scale = copy.deepcopy(ordinary[1])
    changed_scale["id"], changed_scale["mu"] = "B0_scale17", 17
    mixed_scale, _ = evaluate(OUT / "iregi-reference", [ordinary[1], changed_scale, ordinary[1]])
    isolated_scale, _ = evaluate(OUT / "iregi-reference", [changed_scale])
    if mixed_scale[0] != mixed_scale[2] or mixed_scale[1] != isolated_scale[0]:
        raise AssertionError("Scale changes leaked between cached requests")
    reordered, _ = evaluate(OUT / "iregi-reference", list(reversed(ordinary)))
    if reordered != list(reversed(repaired)):
        raise AssertionError("Request order changed the result")
    validation = {"ordinary_cases_unchanged": len(ordinary), "generalized_cases": len(general),
                  "factorial_table_entries": len(table.splitlines()),
                  "checks": ["original initialization STOP reproduced", "ordinary results unchanged exactly",
                             "factorial table equals exact binomial coefficients", "analytic A0 normalization",
                             "scaleless UV/IR cancellation", "general unit powers equal ordinary tensor API",
                             "analytic A0 mass derivative", "tadpole dimension-shift identity",
                             "B0 mass derivative finite difference", "lower-level scalar power parity",
                             "complex A0 mass derivative", "request-order and scale-cache isolation"],
                  "original_stop_stdout": stop.stdout, "original_stop_stderr": stop.stderr}
    (OUT / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")
    if args.write_fixtures:
        provenance = json.loads((OUT / "provenance.json").read_text())
        data = {"schema_version": 1, "normalization": "native_iregi", "basis": "unweighted_cartesian_monomials",
                "source_commit": provenance["madgraph_commit"], "compiler": provenance["compiler"],
                "driver_sha256": provenance["driver_sha256"], "repair_sha256": provenance["patch_sha256"],
                "cases": [{"input": case, "expected": result, "reference_repaired": False}
                          for case, result in zip(ordinary, untouched)] +
                         [{"input": case, "expected": result, "reference_repaired": True}
                          for case, result in zip(general, generalized)]}
        (HERE / "fixtures.json").write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({k: v for k, v in validation.items() if not k.startswith("original_stop")}, indent=2))

if __name__ == "__main__":
    main()

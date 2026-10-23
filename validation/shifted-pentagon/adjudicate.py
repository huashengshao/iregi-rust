"""Independent finite D6 pentagon audit, using only validation dependencies.

The oracle is the defining Dirichlet/Feynman-parameter integral, evaluated by
mpmath's Gauss-Legendre quadrature. Neither a Rust reduction nor a tensor
reduction formula contributes to that oracle. Run from the repository root.
"""

import argparse
import glob
import hashlib
import importlib
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
try:
    import mpmath as mp
except ImportError:
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    candidates = glob.glob(
        f"/nix/store/*-python{version}-mpmath-*/lib/python{version}/site-packages"
    )
    if not candidates:
        raise SystemExit("Install mpmath in the validation Python environment")
    sys.path.insert(0, candidates[0])
    mp = importlib.import_module("mpmath")

sys.path.insert(0, str(Path("validation/reference").resolve()))
from capture import OUT, evaluate


SHIFTS = [[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0],
          [0, 0, 1, 0], [0, 0, 0, 1]]
MASSES = [10, 12, 15, 18, 22]


def case(name, dimension_shift=2, mode=0, api="scalar", shift=0):
    return {"id": name, "api": api, "mode": mode, "rank": 0,
            "dimension_shift": dimension_shift, "mu": 1, "snap": False,
            "threshold": 1e-12,
            "propagators": [{"shift": p, "mass_squared": [m + shift, 0], "power": 1}
                            for p, m in zip(SHIFTS, MASSES)]}


def unit_rule(order):
    nodes, weights = mp.gauss_quadrature(order, "legendre")
    return [((x + 1) / 2, w / 2) for x, w in zip(nodes, weights)]


def parameter_integrals(order, digits, tail_start=20):
    mp.mp.dps = digits
    rule = unit_rule(order)
    d4 = mp.mpf(0)
    d6 = mp.mpf(0)
    tail = mp.mpf(0)
    for u, wu in rule:
        a = 1 - u
        for v, wv in rule:
            b = 1 - v
            for w, ww in rule:
                c = 1 - w
                prefactor = wu * wv * ww * a**3 * b**2 * c
                for z, wz in rule:
                    xs = [u, a * v, a * b * w, a * b * c * z,
                          a * b * c * (1 - z)]
                    # sum x_i p_i² - (sum x_i p_i)², with metric (+---).
                    quadratic = (xs[1] - xs[2] - xs[3] - xs[4] - xs[1]**2
                                 + xs[2]**2 + xs[3]**2 + xs[4]**2)
                    f = sum(x * m for x, m in zip(xs, MASSES)) - quadratic
                    weight = prefactor * wz
                    d4 -= 2 * weight / f**3
                    d6 -= weight / f**2
                    tail -= weight / (f + tail_start)**2
    return {"order_per_axis": order, "working_digits": digits,
            "D4": mp.nstr(d4, digits - 5), "D6": mp.nstr(d6, digits - 5),
            "shifted_D6_tail": mp.nstr(tail, digits - 5)}


def finite_mass_shift(order, upper):
    cases = []
    weights = []
    for i, (x, w) in enumerate(unit_rule(order)):
        cases.append(case(f"massshift_{order}_{i}", dimension_shift=0,
                          shift=float(upper * x)))
        weights.append(float(upper * w))
    results, _ = evaluate(OUT / "iregi-reference", cases)
    if not all(result["stable"] for result in results):
        raise AssertionError("An ordinary D4 mass-shift sample reports instability")
    finite = sum(w * complex(*r["moments"][0][3]) / (1j * math.pi**2)
                 for w, r in zip(weights, results))
    return {"order": order, "interval": [0, upper],
            "D4_integral": [finite.real, finite.imag], "all_reference_stable": True}


def box_mass_shift(order):
    # R b=1 at the exact integer input gives b=[25,1,-6,-9,-13]/325.
    # The production implementation obtains these coefficients with Symbolica.
    b = [mp.mpf(value) / 325 for value in [25, 1, -6, -9, -13]]
    total = sum(b)
    cases, factors = [], []
    for node, (x, w) in enumerate(unit_rule(order)):
        t = 10 * x / (1 - x)
        jacobian = 10 / (1 - x)**2
        for pinch in range(5):
            point = case(f"boxshift_{order}_{node}_{pinch}", dimension_shift=0,
                         shift=float(t))
            point["propagators"].pop(pinch)
            cases.append(point)
            factors.append(float(w * jacobian * b[pinch] / (1 - 2 * t * total)))
    results, _ = evaluate(OUT / "iregi-reference", cases)
    assert all(result["stable"] for result in results)
    finite = sum(factor * complex(*result["moments"][0][3]) / (1j * math.pi**2)
                 for factor, result in zip(factors, results))
    return {"order": order, "interval": [0, "infinity"], "scale": 10,
            "D6": [finite.real, finite.imag], "box_rows": 5 * order,
            "all_reference_stable": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    tail_start = 20
    quadratures = [parameter_integrals(n, digits, tail_start)
                   for n, digits in [(14, 40), (18, 50), (22, 70)]]
    d6 = mp.mpf(quadratures[-1]["D6"])
    d4 = mp.mpf(quadratures[-1]["D4"])
    tail = mp.mpf(quadratures[-1]["shifted_D6_tail"])
    assert abs(d6 - mp.mpf(quadratures[-2]["D6"])) < mp.mpf("1e-25")
    assert abs(d4 - mp.mpf(quadratures[-2]["D4"])) < mp.mpf("1e-25")

    inputs = [case(f"{api}_mode{mode}", mode=mode, api=api)
              for api in ["scalar", "general"] for mode in [0, 1, 2]]
    inputs.append(case("ordinary_D4", dimension_shift=0))
    for h in [0, 2]:
        coalesced = case(f"coalesced_{h}", dimension_shift=h)
        for propagator in coalesced["propagators"]:
            propagator.update(shift=[0, 0, 0, 0], mass_squared=[10, 0])
        inputs.append(coalesced)
    reference, _ = evaluate(OUT / "iregi-reference", inputs)
    untouched, _ = evaluate(OUT / "iregi-reference-original", [inputs[0]])
    assert untouched[0] == reference[0], "The factorial repair changed scalar D6 output"
    if not all(result["stable"] for result in reference):
        raise AssertionError("Reference unexpectedly reports an unstable case")
    normalized = []
    for inp, result in zip(inputs, reference):
        denominator = 1j * math.pi ** (2 + inp["dimension_shift"] // 2)
        slots = [complex(*value) / denominator for value in result["moments"][0]]
        normalized.append({"id": inp["id"], "stable": result["stable"],
                           "slots": [[z.real, z.imag] for z in slots]})
    assert abs(complex(*normalized[6]["slots"][3]) - float(d4)) < 1e-13
    assert abs(complex(*normalized[7]["slots"][3]) + 1 / 12000) < 1e-18
    assert abs(complex(*normalized[8]["slots"][3]) + 1 / 2400) < 1e-18
    for result in normalized[:6]:
        assert abs(complex(*result["slots"][3]) - float(d6)) > 2e-5

    mass_shift = [finite_mass_shift(n, tail_start) for n in [12, 20, 28]]
    for entry in mass_shift:
        combined = complex(*entry["D4_integral"]) + float(tail)
        entry["plus_parameter_tail"] = [combined.real, combined.imag]
        entry["absolute_error_to_direct_D6"] = abs(combined - float(d6))
        assert entry["absolute_error_to_direct_D6"] < 2e-12

    derivative_checks = []
    for step in [0.01, 0.003, 0.001]:
        shifted, _ = evaluate(OUT / "iregi-reference", [
            case("derivative_plus", shift=step), case("derivative_minus", shift=-step)])
        vals = [complex(*result["moments"][0][3]) / (1j * math.pi**3)
                for result in shifted]
        derivative = (vals[0] - vals[1]) / (2 * step)
        derivative_checks.append({"common_mass_step": step,
                                  "reference_D6_derivative": [derivative.real, derivative.imag],
                                  "expected_minus_D4": mp.nstr(-d4, 60)})
        assert all(result["stable"] for result in shifted)
        assert abs(derivative + float(d4)) > 1e-6

    box_mass_shift_checks = [box_mass_shift(n) for n in [12, 20, 32, 48, 64]]
    for entry in box_mass_shift_checks:
        entry["absolute_error_to_direct_D6"] = abs(complex(*entry["D6"]) - float(d6))
        assert entry["absolute_error_to_direct_D6"] < 2e-14

    # Independent numerical determinant checks; production matrix algebra is
    # delegated to Symbolica. These integer entries are exact in mpmath here.
    metric = [1, -1, -1, -1]
    distances = [[sum(g * (a-b)**2 for g, a, b in zip(metric, p, q))
                  for q in SHIFTS] for p in SHIFTS]
    cayley = mp.matrix([[distances[i][j] - MASSES[i] - MASSES[j]
                        for j in range(5)] for i in range(5)])
    report = {
        "schema_version": 1, "qualification": "Independent shifted-scalar definition audit; no performance claim",
        "convention": "J_h = native IREGI / (i*pi^(2+h)); finite UV/IR-free points",
        "input": inputs[0], "F_lower_bound": "39/4: m_min²=10, positive distance contribution <=1/4",
        "det_R": mp.nstr(mp.det(cayley), 30), "det_external_Gram": -16,
        "mpmath_version": mp.__version__, "parameter_quadrature": quadratures,
        "repaired_reference_sha256": hashlib.sha256((OUT / "iregi-reference").read_bytes()).hexdigest(),
        "untouched_reference_sha256": hashlib.sha256((OUT / "iregi-reference-original").read_bytes()).hexdigest(),
        "untouched_scalar_equals_repaired": True,
        "reference_results": normalized, "mass_shift_checks": mass_shift,
        "reference_mass_derivative_checks": derivative_checks,
        "box_halfline_mass_shift_checks": box_mass_shift_checks,
        "conclusion": "The reference standalone D6 pentagon disagrees with its defining parameter integral in this nondegenerate finite case. All original modes share the same shifted-scalar fallback. Ordinary D4 and coalesced D4/D6 normalization checks pass. Finite-interval ordinary-D4 mass-shift integration plus an independently integrated tail agrees with direct D6 integration.",
        "limits": "The direct 4D parameter oracle converges at increasing quadrature order and precision. The 1D mass-shift check uses binary64 Fortran D4 samples and is qualified only at its recorded absolute error; it does not establish a production quadrature implementation or performance parity.",
    }
    encoded = json.dumps(report, indent=2) + "\n"
    if args.write:
        Path("validation/shifted-pentagon/evidence.json").write_text(encoded)
    print(encoded)


if __name__ == "__main__":
    main()

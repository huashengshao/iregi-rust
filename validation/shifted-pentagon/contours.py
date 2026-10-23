"""Independent complex-mass and deformed-contour D6 validation fixtures."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
from adjudicate import mp, unit_rule, evaluate, OUT

SHIFTS = [[0, 0, 0, 0], [4, 0, 0, 0], [0, 1, 0, 0],
          [0, 0, 1, 0], [0, 0, 0, 1]]
MASSES = [1, 2, 3, 4, 5]
WIDTH = -5
DISTANCES = [[sum(g * (x-y)**2 for g, x, y in zip([1, -1, -1, -1], p, q))
              for q in SHIFTS] for p in SHIFTS]


def parameter_integral(order, digits):
    mp.mp.dps = digits
    rule = unit_rule(order)
    total = mp.mpc(0)
    for u, wu in rule:
        a = 1 - u
        for v, wv in rule:
            b = 1 - v
            for w, ww in rule:
                c = 1 - w
                prefactor = wu * wv * ww * a**3 * b**2 * c
                for z, wz in rule:
                    xs = [u, a*v, a*b*w, a*b*c*z, a*b*c*(1-z)]
                    quadratic = (16 * (xs[1] - xs[1]**2) - xs[2] - xs[3] - xs[4]
                                 + xs[2]**2 + xs[3]**2 + xs[4]**2)
                    f = mp.mpc(sum(x*m for x, m in zip(xs, MASSES)) - quadratic, WIDTH)
                    total -= prefactor * wz / f**2
    return {"order_per_axis": order, "working_digits": digits,
            "D6": [mp.nstr(total.real, digits-5), mp.nstr(total.imag, digits-5)]}


def box_contour(order, slope):
    r = mp.matrix([[mp.mpc(DISTANCES[i][j] - MASSES[i] - MASSES[j], -2*WIDTH)
                    for j in range(5)] for i in range(5)])
    b = mp.lu_solve(r, mp.matrix([1] * 5))
    total_b = sum(b)
    ray = mp.mpc(16, -16*slope)
    inputs, factors = [], []
    for node, (x, w) in enumerate(unit_rule(order)):
        t = ray * x / (1-x)
        jacobian = ray / (1-x)**2
        for pinch in range(5):
            inputs.append({"id": f"contour{order}_{slope}_{node}_{pinch}",
                           "api": "scalar", "mode": 0, "rank": 0,
                           "dimension_shift": 0, "mu": 1, "snap": False,
                           "threshold": 1e-12,
                           "propagators": [{"shift": p,
                                            "mass_squared": [float(m+t.real), float(WIDTH+t.imag)],
                                            "power": 1}
                                           for i, (p, m) in enumerate(zip(SHIFTS, MASSES))
                                           if i != pinch]})
            factors.append(complex(w * jacobian * b[pinch] / (1 - 2*t*total_b)))
    results, _ = evaluate(OUT / "iregi-reference", inputs)
    assert all(result["stable"] for result in results)
    value = sum(factor * complex(*result["moments"][0][3]) / (1j * math.pi**2)
                for factor, result in zip(factors, results))
    return {"order": order, "contour_slope": slope, "scale": 16,
            "D6": [value.real, value.imag], "box_rows": len(inputs)}


def pinched_box(order, digits, pinch):
    """Independent defining D4 simplex integral; no reduction formulas."""
    mp.mp.dps = digits
    active = [i for i in range(5) if i != pinch]
    rule = unit_rule(order)
    total = mp.mpc(0)
    for u, wu in rule:
        for v, wv in rule:
            for w, ww in rule:
                xs = [u, (1-u)*v, (1-u)*(1-v)*w, (1-u)*(1-v)*(1-w)]
                f = sum(x * mp.mpc(MASSES[i], WIDTH) for x, i in zip(xs, active))
                f -= sum(xs[i]*xs[j]*DISTANCES[active[i]][active[j]]
                         for i in range(4) for j in range(i+1, 4))
                total += wu*wv*ww*(1-u)**2*(1-v)/f**2
    case = {"id": f"complex_box_{pinch}", "api": "scalar", "mode": 0, "rank": 0,
            "dimension_shift": 0, "mu": 1, "snap": False, "threshold": 1e-12,
            "propagators": [{"shift": SHIFTS[i], "mass_squared": [MASSES[i], WIDTH],
                             "power": 1} for i in active]}
    result = evaluate(OUT / "iregi-reference", [case])[0][0]
    actual = complex(*result["moments"][0][3])/(1j*math.pi**2)
    return {"pinch": pinch, "active": active, "order_per_axis": order,
            "working_digits": digits,
            "parameter_D4": [mp.nstr(total.real, digits-5), mp.nstr(total.imag, digits-5)],
            "reference": result, "reference_D4": [actual.real, actual.imag],
            "absolute_error": float(abs(actual-complex(total)))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    values = []
    for n, digits in [(14, 40), (18, 50), (22, 70), (26, 90)]:
        values.append(parameter_integral(n, digits))
        print(f"Parameter order {n} complete", file=sys.stderr, flush=True)
    expected = mp.mpc(*values[-1]["D6"])
    difference = abs(expected - mp.mpc(*values[-2]["D6"]))
    assert difference < mp.mpf("1e-15"), difference
    contours = [box_contour(n, slope) for n in [32, 64] for slope in [1, 2]]
    for contour in contours:
        error = abs(complex(*contour["D6"]) - complex(expected))
        contour["absolute_error_to_parameter_integral"] = error
    boxes = [pinched_box(18, 50, pinch) for pinch in range(5)]
    # This direct scalar-master probe deliberately bypasses IREGI's reducer.
    probe = subprocess.run([str(OUT / "box-probe")], check=True, text=True,
                           capture_output=True).stdout
    agreement = (all(contour["absolute_error_to_parameter_integral"] < 1e-12
                     for contour in contours)
                 and all(box["absolute_error"] < 1e-12 for box in boxes))
    report = {
        "schema_version": 1,
        "qualification": "Reference counterexample retained: complex box contour fails against independent parameter integration",
        "status": "pass" if agreement else "reference_failure",
        "input": {"shifts": SHIFTS, "mass_squared": [[m, WIDTH] for m in MASSES], "mu_squared": 1},
        "invariant_s01": 16,
        "zero_width_threshold_s01": "(sqrt(1)+sqrt(2))² < 16",
        "parameter_quadrature": values,
        "last_parameter_difference": mp.nstr(difference, 30),
        "box_contours": contours,
        "independent_pinched_boxes": boxes,
        "direct_oneloop_probe_stdout": probe,
        "direct_oneloop_probe_source": "validation/shifted-pentagon/box_probe.f90",
        "failed_box_external_discriminants": [-4, -12, -4, -4],
        "failed_box_nonzero_proof": "F=A-5i with A>0 throughout the simplex; Im(F^-2)=10A/(A²+25)²>0",
        "mpmath_version": mp.__version__,
        "reference_sha256": hashlib.sha256((OUT / "iregi-reference").read_bytes()).hexdigest(),
        "conclusion": "The original complex box routine returns zero for pinch 1 because every tested external triangle discriminant is nonpositive. Its explicit 'no positive lambda, returning 0' branch invalidates this reference contour. The independent parameter value remains a Rust qualification fixture; this report does not establish Rust complex-contour agreement.",
    }
    encoded = json.dumps(report, indent=2) + "\n"
    if args.write:
        Path("validation/shifted-pentagon/contours.json").write_text(encoded)
    print(encoded)


if __name__ == "__main__":
    main()

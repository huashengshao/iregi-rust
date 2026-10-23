"""Independent lightlike-bubble Cartesian moments from Feynman parameters.

Validation only: mpmath performs all numerical quadrature and differentiation.
Neither Rust reduction, original IREGI, nor a symbolic runtime is called.
Run from the repository root: source scripts/env.sh
python3 validation/pv-high-rank/lightlike_feynman_parameters.py --write
"""

import argparse
import glob
import importlib
import json
from pathlib import Path
import sys

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


def evaluate(digits):
    mp.mp.dps = digits
    mu_squared = mp.mpf(9)
    rows = []
    for mass0, mass1 in [(4, 9), (4, 4)]:
        for rank in range(4):
            def f(x, invariant=0):
                return mass0 * (1 - x) + mass1 * x - invariant * x * (1 - x)

            # epsilon*I/(i*pi^2), evaluated directly in native IREGI
            # normalization. k=q+xp, p=(1,1,0,0), hence qx=kx-x.
            # For ranks <=3 the only even Gaussian moments are 1 and kx^2.
            # g_xx=-1 gives the latter's factor F/[2(epsilon-1)].
            def regulated_residue(epsilon, invariant=0):
                def integrand(x):
                    polynomial = (-x) ** rank
                    if rank >= 2:
                        polynomial += (
                            mp.binomial(rank, 2)
                            * (-x) ** (rank - 2)
                            * f(x, invariant)
                            / (2 * (epsilon - 1))
                        )
                    return f(x, invariant) ** (-epsilon) * polynomial

                return (
                    (mu_squared / mp.pi) ** epsilon
                    * mp.gamma(1 + epsilon)
                    * mp.quad(integrand, [0, 1])
                )

            native_uv = mp.pi**2 * regulated_residue(0)
            native_finite = mp.pi**2 * mp.diff(regulated_residue, 0)

            # Independently evaluate the explicit residue and finite
            # parameter integrands, with OneLoop normalization.
            def uv_integrand(x, invariant=0):
                value = (-x) ** rank
                if rank >= 2:
                    value -= mp.binomial(rank, 2) * (-x) ** (rank - 2) * f(x, invariant) / 2
                return value

            def finite_integrand(x, invariant=0):
                logarithm = mp.log(f(x, invariant) / mu_squared)
                value = -(-x) ** rank * logarithm
                if rank >= 2:
                    value -= (
                        mp.binomial(rank, 2)
                        * (-x) ** (rank - 2)
                        * f(x, invariant)
                        / 2
                        * (1 - logarithm)
                    )
                return value

            uv = mp.quad(uv_integrand, [0, 1])
            finite = mp.quad(finite_integrand, [0, 1])
            expected_uv = [
                mp.mpf(1),
                -mp.mpf(1) / 2,
                mp.mpf(1) / 3 - mp.mpf(mass0 + mass1) / 4,
                -mp.mpf(1) / 4 + mp.mpf(mass0 + 2 * mass1) / 4,
            ][rank]
            tolerance = mp.mpf(10) ** (-digits + 10)
            assert abs(uv - expected_uv) < tolerance
            assert abs(native_uv - mp.pi**2 * uv) < tolerance
            assert abs(
                native_finite
                - mp.pi**2 * (finite - (mp.euler + mp.log(mp.pi)) * uv)
            ) < tolerance

            # The supplied invariant s is an independent numerical argument:
            # hold p_x=1 and all routing components fixed while differentiating.
            # mpmath differentiates the quadratures; no derivative recurrence
            # from the reduction implementation enters these expected values.
            uv_s = mp.diff(
                lambda invariant: mp.quad(lambda x: uv_integrand(x, invariant), [0, 1]), 0
            )
            finite_s = mp.diff(
                lambda invariant: mp.quad(lambda x: finite_integrand(x, invariant), [0, 1]), 0
            )
            native_uv_s = mp.pi**2 * mp.diff(lambda invariant: regulated_residue(0, invariant), 0)
            native_finite_s = mp.pi**2 * mp.diff(
                lambda invariant: mp.diff(lambda epsilon: regulated_residue(epsilon, invariant), 0),
                0,
            )
            expected_uv_s = [mp.mpf(0), mp.mpf(0), mp.mpf(1) / 12, -mp.mpf(1) / 8][rank]
            assert abs(uv_s - expected_uv_s) < tolerance
            assert abs(native_uv_s - mp.pi**2 * uv_s) < tolerance
            assert abs(
                native_finite_s
                - mp.pi**2 * (finite_s - (mp.euler + mp.log(mp.pi)) * uv_s)
            ) < tolerance

            text = lambda value: mp.nstr(value, digits - 10)
            rows.append(
                {
                    "mass_squared": [mass0, mass1],
                    "rank": rank,
                    "oneloop": {
                        "uv": text(uv),
                        "ir": "0",
                        "ir2": "0",
                        "finite": text(finite),
                    },
                    "native_iregi_imaginary": {
                        "uv": text(native_uv),
                        "ir": "0",
                        "ir2": "0",
                        "finite": text(native_finite),
                    },
                    "derivative_invariant_s": {
                        "oneloop": {
                            "uv": text(uv_s),
                            "ir": "0",
                            "ir2": "0",
                            "finite": text(finite_s),
                        },
                        "native_iregi_imaginary": {
                            "uv": text(native_uv_s),
                            "ir": "0",
                            "ir2": "0",
                            "finite": text(native_finite_s),
                        },
                    },
                }
            )
    return {"decimal_digits": digits, "results": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    checks = [evaluate(digits) for digits in [60, 100]]
    tolerance = mp.mpf("1e-48")
    for low, high in zip(checks[0]["results"], checks[1]["results"], strict=True):
        for low_values, high_values in [(low, high), (low["derivative_invariant_s"], high["derivative_invariant_s"])]:
            for convention in ["oneloop", "native_iregi_imaginary"]:
                for slot in ["uv", "ir", "ir2", "finite"]:
                    assert abs(mp.mpf(low_values[convention][slot]) - mp.mpf(high_values[convention][slot])) < tolerance
    report = {
        "input": {
            "shifts": [[0, 0, 0, 0], [1, 1, 0, 0]],
            "mass_squared_cases": [[4, 9], [4, 4]],
            "mu": 3,
            "numerators": ["1", "qx", "qx^2", "qx^3"],
            "derivative": "d/ds at supplied squared invariant s=0, holding shift components and masses fixed",
        },
        "metric": "+---",
        "tensor_weights": "raw Cartesian monomial, no multinomial factor",
        "method": "mpmath quadrature and differentiation of the regulated Gaussian/Feynman-parameter integral",
        "normalization": {
            "oneloop": "real coefficients; UV/IR1/IR2/finite",
            "native_iregi_imaginary": "coefficient of i; native finite=i*pi^2*(OneLoop finite-(EulerGamma+log(pi))*UV)",
        },
        "checks": "Exact UV residues and invariant derivatives; direct regulated gamma differentiation versus explicit finite integrand; primal and first-invariant-derivative 60/100-digit agreement below 1e-48",
        "mpmath_version": mp.__version__,
        "precision_checks": checks,
        "implementation_comparison": "Not performed by this script; these are independent expected values.",
    }
    encoded = json.dumps(report, indent=2) + "\n"
    if args.write:
        Path("validation/pv-high-rank/lightlike-feynman-parameters.json").write_text(encoded)
    print(encoded)


if __name__ == "__main__":
    main()

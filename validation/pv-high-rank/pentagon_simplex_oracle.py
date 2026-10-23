"""Independent smooth-simplex oracle for the preserved rank-six pentagon case.

Validation only. SciPy supplies the quadrature rules and adaptive subdivision;
this script defines the Gaussian/Feynman-parameter integrand and coordinates.
It does not execute IREGI, Rust reduction, scalar-master code, or Symbolica.

Run from the repository root:
source scripts/env.sh
python3 validation/pv-high-rank/pentagon_simplex_oracle.py --write
"""

import argparse
import glob
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time


def dependency(name):
    try:
        return importlib.import_module(name)
    except ImportError:
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        candidates = glob.glob(f"/nix/store/*-python{version}-{name}-*/lib/python{version}/site-packages")
        if not candidates:
            raise SystemExit(f"Install {name} in the optional validation environment")
        sys.path.insert(0, candidates[0])
        return importlib.import_module(name)


np = dependency("numpy")
scipy = dependency("scipy")
from scipy.integrate import cubature


class SimplexIntegrand:
    def __init__(self, ordering):
        self.ordering = ordering
        self.points_evaluated = 0
        self.minimum_observed_f = float("inf")

    def __call__(self, points):
        self.points_evaluated += len(points)
        # Standard stick-breaking map of [0,1]^4 onto sum(x_i)=1.
        remaining = np.ones(len(points))
        jacobian = np.ones(len(points))
        x = np.empty((len(points), 5))
        for axis in range(4):
            x[:, self.ordering[axis]] = remaining * points[:, axis]
            jacobian *= (1 - points[:, axis]) ** (3 - axis)
            remaining *= 1 - points[:, axis]
        x[:, self.ordering[4]] = remaining
        x0, x1, x2, x3, x4 = x.T
        # For the fixed fixture, P=(x4,x1,x2,x3) and
        # F=sum(x_i*m_i^2)-sum(x_i*p_i^2)+P^2.
        f = (
            4*x0 + 9*x1 + 16*x2 + 25*x3 + 36*x4
            + x1 + x2 + x3 - x4 + x4*x4 - x1*x1 - x2*x2 - x3*x3
        )
        self.minimum_observed_f = min(self.minimum_observed_f, float(f.min()))
        if np.any(f < 3.75):
            raise ValueError("The fixture's analytic positive-F bound was violated")
        value = -2*x4**5*x3/f**3 + 5*x4**3*x3/f**2 - (15/4)*x4*x3/f
        return jacobian * value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    source = Path("validation/pv-high-rank/precision-probe.json")
    reference = json.loads(source.read_text())
    expected = {
        "shifts": [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0]],
        "mass_squared": [4, 9, 16, 25, 36], "mu": 3, "monomial": [5, 0, 0, 1],
    }
    if reference["input"] != expected:
        raise ValueError("This independent integrand applies only to the recorded fixture")
    report = {
        "input": expected,
        "input_source": str(source),
        "input_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        "method": "SciPy adaptive cubature after a standard simplex-to-cube coordinate change",
        "integrand_oneloop": "-2*P0^5*Pz/F^3 +5*P0^3*Pz/F^2 -(15/4)*P0*Pz/F",
        "derivation": "Shift k=q+P. The kz term integrates to zero because g0z=0. The surviving -Pz times k0^0,k0^2,k0^4 terms have Gamma(5)-weighted Gaussian integrals -2/F^3,+1/(2F^2),-3/(4F), respectively. Binomial coefficients give the displayed integrand.",
        "pole_argument": "The only rank-six UV term is k0^5*kz, whose angular integral vanishes. Lower Gaussian moments are UV finite; positive F excludes IR singularities. All UV/IR Laurent slots vanish for this monomial.",
        "positive_f_bound": "F>=min(m_i^2)-x4*(1-x4)>=4-1/4=3.75; the spatial variance terms are nonnegative.",
        "native_conversion": "Native finite coefficient is i*pi^2 times the real OneLoop integral; no pole normalization terms occur.",
        "qualification": "Independent numerical quadrature with estimated errors and convergence checks, not an interval-certified bound or a performance benchmark.",
        "runs": [],
    }
    output = Path("validation/pv-high-rank/pentagon-simplex-oracle.json")
    configurations = [
        ("genz-malik", 1e-10, [1, 2, 3, 4, 0]),
        ("gk21", 1e-13, [1, 2, 3, 4, 0]),
        ("gk21", 1e-15, [1, 2, 3, 4, 0]),
        ("gk21", 1e-15, [4, 3, 2, 1, 0]),
    ]
    for rule, tolerance, ordering in configurations:
        integrand = SimplexIntegrand(ordering)
        started = time.monotonic()
        result = cubature(
            integrand, np.zeros(4), np.ones(4), rule=rule,
            atol=tolerance, rtol=0, max_subdivisions=10000,
        )
        row = {
            "rule": rule, "absolute_tolerance_oneloop": tolerance,
            "simplex_ordering": ordering, "status": result.status,
            "oneloop_finite": float(result.estimate),
            "native_finite_imaginary": float(np.pi**2 * result.estimate),
            "estimated_absolute_error_oneloop": float(result.error),
            "estimated_absolute_error_native": float(np.pi**2 * result.error),
            "subdivisions": result.subdivisions,
            "points_evaluated": integrand.points_evaluated,
            "minimum_observed_f": integrand.minimum_observed_f,
            "elapsed_seconds_validation_only": time.monotonic() - started,
        }
        report["runs"].append(row)
        print(json.dumps(row), flush=True)
        if args.write:
            output.write_text(json.dumps(report, indent=2) + "\n")
    tight = report["runs"][-2:]
    difference = abs(tight[0]["native_finite_imaginary"] - tight[1]["native_finite_imaginary"])
    uncertainty = max(difference, *(run["estimated_absolute_error_native"] for run in tight))
    high_precision_value = float(reference["precision"]["binary256"])
    report["comparison"] = {
        "tight_mapping_difference_native": difference,
        "estimated_native_uncertainty_including_mapping_difference": uncertainty,
        "previous_pv_binary256_native_imaginary": reference["precision"]["binary256"],
        "difference_from_previous_pv_binary256": abs(tight[-1]["native_finite_imaginary"] - high_precision_value),
        "passed_1e_minus_12_native": all(run["status"] == "converged" for run in tight)
            and uncertainty < 1e-12
            and abs(tight[-1]["native_finite_imaginary"] - high_precision_value) < 1e-12,
    }
    if args.write:
        output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["comparison"], indent=2), flush=True)
    if not report["comparison"]["passed_1e_minus_12_native"]:
        raise SystemExit("Independent quadrature did not qualify the requested accuracy")


if __name__ == "__main__":
    main()

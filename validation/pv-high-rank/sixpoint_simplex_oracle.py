"""Independent smooth-simplex oracle for the preserved rank-seven six-point case.

Validation only. SciPy supplies the quadrature and adaptive subdivision. This
script defines a Feynman-parameter integrand and a coordinate map; it does not
execute Rust reduction, IREGI, scalar masters, or Symbolica.

Run from the project root:
source scripts/env.sh
python3 validation/pv-high-rank/sixpoint_simplex_oracle.py --write
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
        # Cubature owns its tensor rule. Bound temporary integrand arrays while
        # preserving the exact rule and all supplied evaluation points.
        if len(points) > 131072:
            return np.concatenate([self.evaluate(points[start:start+131072]) for start in range(0, len(points), 131072)])
        return self.evaluate(points)

    def evaluate(self, points):
        self.points_evaluated += len(points)
        remaining = np.ones(len(points))
        jacobian = np.ones(len(points))
        x = np.empty((len(points), 6))
        for axis in range(5):
            x[:, self.ordering[axis]] = remaining * points[:, axis]
            jacobian *= (1 - points[:, axis]) ** (4 - axis)
            remaining *= 1 - points[:, axis]
        x[:, self.ordering[5]] = remaining
        x0, x1, x2, x3, x4, x5 = x.T
        p0 = x4 + 2*x5
        px = x1 + 3*x5
        py = x2 + 5*x5
        pz = x3 + 7*x5
        f = (
            4*x0 + 9*x1 + 16*x2 + 25*x3 + 36*x4 + 49*x5
            + x1 + x2 + x3 - x4 + 79*x5
            + p0*p0 - px*px - py*py - pz*pz
        )
        self.minimum_observed_f = min(self.minimum_observed_f, float(f.min()))
        if np.any(f < 3):
            raise ValueError("The analytic positive-F bound was violated")
        value = -px*(6*pz**6/f**4 + 15*pz**4/f**3 + (45/4)*pz**2/f**2 + (15/8)/f)
        return jacobian * value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--report-only", action="store_true", help="Rebuild comparisons from saved quadrature runs")
    parser.add_argument("--max-subdivisions", type=int, help="Override the per-rule subdivision limit")
    parser.add_argument("--run", type=int, help="Execute one zero-indexed configuration and retain existing others")
    args = parser.parse_args()
    source = Path("validation/pv-high-rank/oracle-runs/n6-base-rank7.json")
    reference = json.loads(source.read_text())
    expected = {
        "shifts": [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [2, 3, 5, 7]],
        "mass_squared": [4, 9, 16, 25, 36, 49], "mu": 3, "monomial": [0, 1, 0, 6],
    }
    if any(reference[key] != expected[key] for key in ("shifts", "mass_squared", "mu")):
        raise ValueError("This independent integrand applies only to the recorded fixture")
    report = {
        "input": expected,
        "input_source": str(source),
        "input_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        "method": "SciPy adaptive cubature after a simplex-to-cube coordinate change",
        "integrand_oneloop": "-Px*(6*Pz^6/F^4 +15*Pz^4/F^3 +(45/4)*Pz^2/F^2 +(15/8)/F)",
        "derivation": "Shift k=q+P. Every kx term in (kx-Px)*(kz-Pz)^6 vanishes: kx has no partner and gxz=0. Gamma(6)-weighted Gaussian integrals of kz^(2r), r=0,1,2,3, are respectively 6/F^4, 1/F^3, 3/(4F^2), 15/(8F). The Minkowski Gaussian sign and (gzz)^r cancel. Multiplication by -Px*binomial(6,2r)*Pz^(6-2r) yields the displayed integrand.",
        "pole_argument": "The original N=6 rank=7 integral is ultraviolet convergent (superficial degree -1), as are all surviving shifted terms. Positive F excludes IR singularities. All UV/IR Laurent slots vanish.",
        "positive_f_bound": "F=sum(x_i*m_i^2)-Var(p0)+Var(px)+Var(py)+Var(pz). With p0 in [0,2], Var(p0)<=1, so F>=4-1=3 throughout the simplex.",
        "native_conversion": "Native finite coefficient is i*pi^2 times the real OneLoop integral; no pole normalization terms occur.",
        "qualification": "Independent numerical quadrature with estimated errors and mapping convergence, not an interval-certified bound or a performance benchmark.",
        "runs": [],
    }
    output = Path("validation/pv-high-rank/sixpoint-simplex-oracle.json")
    if (args.run is not None or args.report_only) and output.exists():
        previous = json.loads(output.read_text())
        if previous["input_source_sha256"] == report["input_source_sha256"] and previous["input"] == report["input"]:
            report["runs"] = previous["runs"]
            for row in report["runs"]:
                row.setdefault("script_sha256", previous["script_sha256"])
    configurations = [
        ("genz-malik", 1e-10, [5, 4, 3, 2, 1, 0], 50000),
        ("gk15", 1e-13, [5, 4, 3, 2, 1, 0], 2),
        ("gk15", 1e-13, [1, 2, 3, 4, 5, 0], 2),
        ("gk21", 1e-13, [1, 2, 3, 4, 5, 0], 0),
        ("gk21", 1e-13, [2, 1, 3, 4, 5, 0], 0),
        ("gk21", 1e-13, [1, 2, 3, 4, 5, 0], 2),
        ("gk21", 1e-13, [2, 1, 3, 4, 5, 0], 3),
    ]
    for index, (rule, tolerance, ordering, default_limit) in enumerate(configurations):
        if args.report_only or (args.run is not None and args.run != index):
            continue
        integrand = SimplexIntegrand(ordering)
        started = time.monotonic()
        subdivision_limit = args.max_subdivisions if args.max_subdivisions is not None else default_limit
        result = cubature(
            integrand, np.zeros(5), np.ones(5), rule=rule,
            atol=tolerance, rtol=0, max_subdivisions=subdivision_limit,
        )
        row = {
            "configuration": index, "rule": rule,
            "script_sha256": report["script_sha256"],
            "absolute_tolerance_oneloop": tolerance,
            "simplex_ordering": ordering, "status": result.status,
            "oneloop_finite": float(result.estimate),
            "native_finite_imaginary": float(np.pi**2 * result.estimate),
            "estimated_absolute_error_oneloop": float(result.error),
            "estimated_absolute_error_native": float(np.pi**2 * result.error),
            "subdivisions": result.subdivisions,
            "max_subdivisions": subdivision_limit,
            "points_evaluated": integrand.points_evaluated,
            "minimum_observed_f": integrand.minimum_observed_f,
            "elapsed_seconds_validation_only": time.monotonic() - started,
        }
        report["runs"] = sorted([r for r in report["runs"] if r["configuration"] != index] + [row], key=lambda r: r["configuration"])
        print(json.dumps(row), flush=True)
        if args.write:
            output.write_text(json.dumps(report, indent=2) + "\n")
    tight = [row for row in report["runs"] if row["configuration"] in [5, 6]]
    if len(tight) == 2:
        difference = abs(tight[0]["native_finite_imaginary"] - tight[1]["native_finite_imaginary"])
        uncertainty = max(difference, *(row["estimated_absolute_error_native"] for row in tight))
        p = np.asarray(expected["shifts"])
        differences = p[:, None, :] - p[None, :, :]
        q_squared = max(1, *expected["mass_squared"], float(np.max(np.abs(differences[:,:,0]**2 - np.sum(differences[:,:,1:]**2, axis=2)))))
        normalized = tight[-1]["native_finite_imaginary"] * np.sqrt(q_squared)
        discrepant = next(row for row in reference["discrepancies"] if row["monomial"] == expected["monomial"] and row["slot"] == 3 and row["component"] == 1)
        report["comparison"] = {
            "tight_mapping_difference_native": difference,
            "estimated_native_uncertainty_including_mapping_difference": uncertainty,
            "normalization_scale_squared": q_squared,
            "independent_native_finite_imaginary_normalized": normalized,
            "previous_rust_with_original_f64_masters_normalized": discrepant["actual_normalized"],
            "previous_original_ibp_f64_normalized": discrepant["expected_normalized"],
            "difference_from_previous_rust_normalized": abs(normalized - float(discrepant["actual_normalized"])),
            "difference_from_previous_original_ibp_normalized": abs(normalized - float(discrepant["expected_normalized"])),
            "all_library_runs_report_converged": all(row["status"] == "converged" for row in tight),
            "all_requested_tolerances_met_by_error_estimate": all(row["estimated_absolute_error_oneloop"] <= row["absolute_tolerance_oneloop"] for row in tight),
            "estimated_error_and_mapping_gate_1e_minus_12_native": uncertainty < 1e-12,
            "library_status_note": "SciPy 1.17 checks the subdivision cap immediately after a subdivision, before checking the updated error again. Configuration 5 reaches its cap on the same step that its error estimate falls below the requested tolerance; its unmodified library status remains not_converged. Configuration 6 stops after the same number of subdivisions with a larger cap and reports converged. The numerical accuracy gate uses both reported error estimates and their independent mapping difference, and is not a rigorous interval bound.",
        }
        if args.write:
            output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report["comparison"], indent=2), flush=True)
        if not report["comparison"]["estimated_error_and_mapping_gate_1e_minus_12_native"]:
            raise SystemExit("Independent quadrature did not qualify the requested accuracy")


if __name__ == "__main__":
    main()

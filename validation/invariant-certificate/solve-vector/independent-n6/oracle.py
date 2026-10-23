"""Independent finite scalar N6 simplex integral; validation only.

SciPy supplies the Gauss-Jacobi rules and optional adaptive cubature. The script
only evaluates a fixed Feynman-parameter integrand and combines library rule
nodes/weights. No Rust reduction, scalar masters, IREGI, or Symbolica is used.
Numerical execution requires the parent's coordinated runtime window.
"""

import argparse
import glob
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dependency(name):
    try:
        return importlib.import_module(name)
    except ImportError:
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        candidates = sorted(glob.glob(
            f"/nix/store/*-python{version}-{name}-*/lib/python{version}/site-packages"
        ))
        if not candidates:
            raise SystemExit(f"Install {name} in the optional validation environment")
        sys.path.insert(0, candidates[0])
        return importlib.import_module(name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", type=int, help="Run one Gauss-Jacobi order")
    parser.add_argument("--mapping", type=int, choices=(0, 1), default=0)
    parser.add_argument("--cubature", action="store_true")
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    if not args.report_only and not args.cubature and args.order is None:
        parser.error("choose --order, --cubature, or --report-only explicitly")
    if args.order is not None and not 2 <= args.order <= 32:
        parser.error("validation orders must be between 2 and 32")
    if args.order is not None and args.cubature:
        parser.error("choose one quadrature method per bounded process")

    # Avoid BLAS thread contention; every quadrature call itself is serial.
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    np = dependency("numpy")
    scipy = dependency("scipy")
    from scipy.special import roots_jacobi

    fixture_path = ROOT / "input.json"
    fixture = json.loads(fixture_path.read_text())
    expected_shifts = [[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0],
                       [0, 0, 1, 0], [0, 0, 0, 1], [1, 1, 1, 1]]
    if (fixture["shifts"] != expected_shifts
            or fixture["mass_squared"] != list(range(30, 36))
            or fixture["powers"] != [1] * 6
            or fixture["dimension_shift"] != 0 or fixture["rank"] != 0):
        raise ValueError("The integrand is specialized to the exact retained fixture")
    provenance = {
        "input_sha256": digest(fixture_path), "script_sha256": digest(__file__),
        "fixture_source_sha256": digest(fixture["source"]),
        "python": sys.version, "numpy_version": np.__version__,
        "numpy_path": np.__file__, "scipy_version": scipy.__version__,
        "scipy_path": scipy.__file__,
    }
    output = ROOT / "result.json"
    report = {
        "status": "incomplete", "input": fixture, "provenance": provenance,
        "integrand_oneloop": "6/F^4",
        "f_definition": "sum(x_i*m_i^2)-sum(x_i*p_i^2)+(sum(x_i*p_i))^2",
        "pole_argument": "UV degree 4-12=-8; F>=30-Var(pt)>=29.75 excludes infrared singularities. All three pole slots are exactly zero.",
        "native_conversion": "Native finite = i*pi^2*OneLoop finite; no pole-dependent conversion terms survive.",
        "uncertainty_kind": "Successive library rules and independent mappings, optionally embedded cubature error; not an interval-certified bound.",
        "runs": [],
    }
    if output.exists():
        previous = json.loads(output.read_text())
        if previous["provenance"]["input_sha256"] != provenance["input_sha256"]:
            raise ValueError("Existing result belongs to a different fixture")
        report["runs"] = previous["runs"]

    def write_report():
        temporary = output.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        temporary.replace(output)

    ordering = ([0, 1, 2, 3, 4, 5], [5, 3, 1, 4, 2, 0])[args.mapping]
    points_evaluated = 0
    minimum_f = float("inf")
    maximum_f = float("-inf")

    def integrand(points, include_jacobian):
        nonlocal points_evaluated, minimum_f, maximum_f
        points_evaluated += len(points)
        remaining = np.ones(len(points))
        jacobian = np.ones(len(points))
        x = np.empty((len(points), 6))
        for axis in range(5):
            x[:, ordering[axis]] = remaining * points[:, axis]
            remaining *= 1 - points[:, axis]
            if include_jacobian:
                jacobian *= (1 - points[:, axis]) ** (4 - axis)
        x[:, ordering[5]] = remaining
        x0, x1, x2, x3, x4, x5 = x.T
        pt, px, py, pz = x1 + x5, x2 + x5, x3 + x5, x4 + x5
        f = (30*x0 + 31*x1 + 32*x2 + 33*x3 + 34*x4 + 35*x5
             - x1 + x2 + x3 + x4 + 2*x5
             + pt*pt - px*px - py*py - pz*pz)
        minimum_f = min(minimum_f, float(f.min()))
        maximum_f = max(maximum_f, float(f.max()))
        if np.any(f < 29.75 - 1e-12) or np.any(f > 35.75 + 1e-12):
            raise ValueError("The analytic F variance bounds were violated")
        return 6 * jacobian / f**4

    if not args.report_only:
        # Write incomplete before work so a killed run cannot leave a stale pass.
        write_report()
        started = time.monotonic()
        row = {"provenance": provenance, "mapping": args.mapping,
               "ordering": ordering, "started_unix": time.time()}
        if args.cubature:
            from scipy.integrate import cubature

            def chunked(points):
                return np.concatenate([
                    integrand(points[start:start+131072], True)
                    for start in range(0, len(points), 131072)
                ])

            result = cubature(chunked, np.zeros(5), np.ones(5), rule="gk15",
                              atol=1e-19, rtol=0, max_subdivisions=1)
            estimate = float(result.estimate)
            row.update(method="scipy.integrate.cubature:gk15",
                       library_status=result.status, subdivisions=result.subdivisions,
                       requested_absolute_error=1e-19,
                       estimated_absolute_error=float(result.error))
            run_id = f"gk15-map{args.mapping}"
        else:
            nodes, weights = [], []
            for axis in range(5):
                alpha = 4 - axis
                z, w = roots_jacobi(args.order, alpha, 0)
                nodes.append((z + 1) / 2)
                weights.append(w / 2**(alpha + 1))
            volume = float(np.prod([np.sum(w) for w in weights]))
            if abs(volume - 1/120) > 1e-16:
                raise ValueError("Gauss-Jacobi rule does not reproduce the simplex volume")
            partials = []
            total_points = args.order**5
            shape = (args.order,) * 5
            for start in range(0, total_points, 131072):
                indices = np.unravel_index(
                    np.arange(start, min(start + 131072, total_points)), shape
                )
                points = np.column_stack([nodes[axis][indices[axis]] for axis in range(5)])
                weight = np.ones(len(points))
                for axis in range(5):
                    weight *= weights[axis][indices[axis]]
                partials.append(float(np.sum(weight * integrand(points, False))))
            import math
            estimate = math.fsum(partials)
            row.update(method="scipy.special.roots_jacobi:tensor-product",
                       order=args.order, library_status="fixed_rule_evaluated",
                       estimated_absolute_error=None, simplex_volume_from_rule=volume)
            run_id = f"jacobi{args.order}-map{args.mapping}"
        row.update(run_id=run_id, oneloop_finite=estimate,
                   native_finite_imaginary=float(np.pi**2 * estimate),
                   normalized_oneloop_finite=1500625 * estimate,
                   points_evaluated=points_evaluated, minimum_observed_f=minimum_f,
                   maximum_observed_f=maximum_f,
                   validation_wall_seconds=time.monotonic()-started)
        report["runs"] = [r for r in report["runs"] if r["run_id"] != run_id] + [row]
        print(json.dumps(row), flush=True)

    # Keep historical runs visible, but only current exact provenance can
    # qualify this report. Changed code or library context must be rerun.
    current_runs = [r for r in report["runs"] if r.get("provenance") == provenance]
    report["excluded_stale_run_ids"] = [
        r["run_id"] for r in report["runs"] if r.get("provenance") != provenance
    ]
    jacobi = {(r["order"], r["mapping"]): r for r in current_runs if "order" in r}
    required = [(order, mapping) for order in (8, 12, 16) for mapping in (0, 1)]
    if all(key in jacobi for key in required):
        estimates = [jacobi[key]["oneloop_finite"] for key in required]
        estimate = jacobi[(16, 1)]["oneloop_finite"]
        differences = [abs(jacobi[(16, m)]["oneloop_finite"]
                           - jacobi[(12, m)]["oneloop_finite"]) for m in (0, 1)]
        differences.append(abs(jacobi[(16, 0)]["oneloop_finite"] - estimate))
        cubature_runs = [r for r in current_runs if r["method"].startswith("scipy.integrate.cubature")]
        for row in cubature_runs:
            differences.extend([abs(row["oneloop_finite"]-estimate), row["estimated_absolute_error"]])
        # Include a conservative floating-point reporting floor, explicitly
        # estimated rather than a proof of the quadrature's error.
        uncertainty = max(*differences, 64*np.finfo(float).eps*abs(estimate))
        report["comparison"] = {
            "oneloop_finite": estimate, "native_finite_imaginary": float(np.pi**2*estimate),
            "all_order_values": estimates, "tight_order_and_mapping_differences": differences,
            "estimated_uncertainty_oneloop": uncertainty,
            "estimated_uncertainty_normalized_oneloop": 1500625*uncertainty,
            "normalized_oneloop_finite": 1500625*estimate,
            "absolute_error_target_oneloop": 1e-19,
            "cubature_crosscheck_run_ids": [r["run_id"] for r in cubature_runs],
            "all_cubature_runs_report_converged": all(
                r["library_status"] == "converged" for r in cubature_runs
            ) if cubature_runs else None,
        }
        report["status"] = "estimated_converged" if uncertainty <= 1e-19 else "not_converged"
    write_report()
    print(json.dumps({"status": report["status"], "comparison": report.get("comparison")}), flush=True)


if __name__ == "__main__":
    main()

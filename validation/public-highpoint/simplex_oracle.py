"""Independent SciPy finite-integral witnesses for the conditioned family.

Scalar integrands use the standard Feynman-parameter formula. The N6 qx*qz^6
integrand is reused verbatim from the independently derived existing
validation/pv-high-rank/sixpoint_simplex_oracle.py; no polynomial manipulation
or tensor reduction is implemented here. SciPy supplies the quadrature rules.
"""
import argparse
import glob
import hashlib
import importlib
import json
import math
import os
from fractions import Fraction
from pathlib import Path
import sys
import time

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"


def dependency(name):
    try:
        return importlib.import_module(name)
    except ImportError:
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        candidates = sorted(glob.glob(f"/nix/store/*-python{version}-{name}-*/lib/python{version}/site-packages"))
        if not candidates:
            raise SystemExit(f"Install optional validation dependency {name}")
        sys.path.insert(0, candidates[0])
        return importlib.import_module(name)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int, choices=[6, 7])
    parser.add_argument("--order", type=int, required=True, choices=range(4, 25))
    parser.add_argument("--mapping", type=int, required=True, choices=[0, 1])
    args = parser.parse_args()
    np = dependency("numpy")
    scipy = dependency("scipy")
    from scipy.special import roots_jacobi
    here = Path("validation/public-highpoint")
    fixture_path = here / "fixture-conditioned_masses.json"
    sample = json.loads(fixture_path.read_text())["samples"][0]
    propagators = sample["propagators"][:args.n]
    p = np.asarray([[float(Fraction(v)) for v in item["shift"]] for item in propagators])
    masses = np.asarray([float(Fraction(item["mass_squared"][0])) for item in propagators])
    assert all(item["mass_squared"][1] == "0" and item["power"] == 1 for item in propagators)
    # Fixed inputs are dyadic, so this optional binary64 reference evaluates
    # exactly the same input point without an initial decimal truncation.
    assert p.tolist() == [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0],
                          [0, 0, 0, 1], [0.5, 0, 0, 0], [0, 1, 1, 0],
                          [0, 0, 1, 1]][:args.n]
    assert masses.tolist() == [1, 2, 3, 4, 2, 3, 4][:args.n]
    orderings = [list(range(args.n)), list(reversed(range(args.n)))]
    ordering = orderings[args.mapping]
    output = here / f"simplex-n{args.n}-order{args.order}-map{args.mapping}.json"
    assert not output.exists(), "Retain earlier runs; use another quadrature configuration"
    record = {
        "status": "started", "n": args.n, "order": args.order, "mapping": args.mapping,
        "ordering": ordering, "fixture_sha256": digest(fixture_path), "script_sha256": digest(__file__),
        "existing_rank7_integrand_source": "validation/pv-high-rank/sixpoint_simplex_oracle.py",
        "existing_rank7_integrand_sha256": digest("validation/pv-high-rank/sixpoint_simplex_oracle.py"),
        "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        "method": "SciPy roots_jacobi tensor-product rule with simplex stick-breaking map",
        "scalar_integrand_oneloop": "(-1)^N Gamma(N-2) F^(2-N)",
        "n6_rank7_integrand_oneloop": "-Px*(6*Pz^6/F^4 +15*Pz^4/F^3 +(45/4)*Pz^2/F^2 +(15/8)/F)",
        "positive_F_bound": "F=sum(x_i m_i^2)-Var(pt)+Var(px)+Var(py)+Var(pz)>=1-(1/2)^2/4=15/16",
        "normalization": "native finite = i*pi^2 times real OneLoop integral; all poles vanish",
        "qualification": "Independent fixed-rule quadrature. Successive orders and mappings provide estimated uncertainty only, not a rigorous interval certificate or performance measurement.",
    }
    output.write_text(json.dumps(record, indent=2) + "\n")
    start = time.monotonic()
    dimensions = args.n-1
    nodes, weights = [], []
    for axis in range(dimensions):
        alpha = dimensions-1-axis
        z, w = roots_jacobi(args.order, alpha, 0)
        nodes.append((z+1)/2)
        weights.append(w/2**(alpha+1))
    volume = float(np.prod([np.sum(w) for w in weights]))
    assert abs(volume - 1/math.factorial(dimensions)) < 1e-16
    p_squared = p[:, 0]**2-np.sum(p[:, 1:]**2, axis=1)
    scalar_parts, rank7_parts = [], []
    min_f = math.inf
    total = args.order**dimensions
    for offset in range(0, total, 65536):
        indices = np.unravel_index(np.arange(offset, min(offset+65536, total)), (args.order,)*dimensions)
        remaining = np.ones(len(indices[0]))
        weight = np.ones(len(remaining))
        x = np.empty((len(remaining), args.n))
        for axis in range(dimensions):
            point = nodes[axis][indices[axis]]
            x[:, ordering[axis]] = remaining*point
            remaining *= 1-point
            weight *= weights[axis][indices[axis]]
        x[:, ordering[-1]] = remaining
        P = x @ p
        f = x @ (masses-p_squared) + P[:, 0]**2-np.sum(P[:, 1:]**2, axis=1)
        min_f = min(min_f, float(f.min()))
        assert np.all(f >= 15/16-1e-14)
        scalar_parts.append(float(np.sum(weight*((-1)**args.n)*math.factorial(args.n-3)/f**(args.n-2))))
        if args.n == 6:
            px, pz = P[:, 1], P[:, 3]
            # Existing independent Gaussian-moment integrand, unchanged.
            value = -px*(6*pz**6/f**4 + 15*pz**4/f**3 + (45/4)*pz**2/f**2 + (15/8)/f)
            rank7_parts.append(float(np.sum(weight*value)))
    results = [{"monomial": [0, 0, 0, 0], "moment_index": 0,
                "oneloop_finite": math.fsum(scalar_parts), "native_finite_imaginary": math.pi**2*math.fsum(scalar_parts)}]
    if args.n == 6:
        results.append({"monomial": [0, 1, 0, 6], "moment_index": 321,
                        "oneloop_finite": math.fsum(rank7_parts), "native_finite_imaginary": math.pi**2*math.fsum(rank7_parts)})
    record.update(status="fixed_rule_evaluated", points_evaluated=total, simplex_volume_from_rule=volume,
                  minimum_observed_F=min_f, results=results, diagnostic_seconds=time.monotonic()-start)
    output.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({key: record[key] for key in ["n", "order", "mapping", "results", "diagnostic_seconds"]}), flush=True)


if __name__ == "__main__":
    main()

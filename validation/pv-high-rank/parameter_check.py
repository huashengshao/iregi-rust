"""Independent gamma/Feynman-parameter adjudication of original rank-four Bxxxx.

Validation only. Numerical quadrature and differentiation use mpmath; no
integration algorithm, polynomial engine or Laurent-series engine is provided.
Run from the repository root after scripts/build-reference.sh.
"""
import argparse
import glob
import importlib
import json
from pathlib import Path
import subprocess
import sys

try:
    import mpmath as mp
except ImportError:
    # Offline development-shell fallback, matching the active Python version.
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    candidates = glob.glob(f"/nix/store/*-python{version}-mpmath-*/lib/python{version}/site-packages")
    if not candidates:
        raise SystemExit("Install mpmath in the validation Python environment")
    sys.path.insert(0, candidates[0])
    mp = importlib.import_module("mpmath")


def evaluate_parameter_integral(digits):
    mp.mp.dps = digits
    def f(x):
        return 4 * (1 - x) + 9 * x + x * (1 - x)
    # Multiplying by epsilon exposes a smooth function at epsilon=0.
    # The value and derivative are the UV residue and finite coefficient.
    def residue_series(eps):
        return (mp.mpf(9) / mp.pi) ** eps * mp.gamma(1 + eps) * mp.quad(
            lambda x: f(x) ** (-eps) * (
                3 * f(x) ** 2 / (4 * (eps - 1) * (eps - 2))
                + 3 * x ** 2 * f(x) / (eps - 1) + x ** 4), [0, 1])
    return {"uv_imaginary": mp.nstr(mp.pi ** 2 * residue_series(0), digits - 10),
            "finite_imaginary": mp.nstr(mp.pi ** 2 * mp.diff(residue_series, 0), digits - 10)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    queries = "".join(
        f"EVAL mode{mode} tensor {mode} 2 4 0 3 0 1e-6\n0 0 0 0 4 0 1\n0 1 0 0 9 0 1\n"
        for mode in [0, 1, 2]) + "QUIT\n"
    run = subprocess.run([str(Path.cwd() / "target/reference/iregi-reference-original")],
                         input=queries, text=True, capture_output=True, check=True)
    results = [json.loads(line[7:]) for line in run.stdout.splitlines() if line.startswith("RESULT ")]
    if len(results) != 3 or not all(r["stable"] for r in results):
        raise RuntimeError("Reference did not return three stable results")
    # IREGI's packed ordering places q_x^4 at index 55 (rank four).
    oracle = [{"mode": i, "stable": r["stable"], "qx4": r["moments"][55]}
              for i, r in enumerate(results)]
    checks = [evaluate_parameter_integral(digits) for digits in [50, 80]]
    assert abs(mp.mpf(checks[0]["finite_imaginary"]) - mp.mpf(checks[1]["finite_imaginary"])) < mp.mpf("1e-38")
    expected = mp.mpf(checks[1]["finite_imaginary"])
    assert abs(mp.mpf(oracle[0]["qx4"][3][1]) - expected) < mp.mpf("1e-10")
    assert abs(mp.mpf(oracle[1]["qx4"][3][1]) - expected) > mp.mpf("0.6")
    report = {"input": {"shifts": [[0, 0, 0, 0], [0, 1, 0, 0]],
                         "mass_squared": [4, 9], "mu": 3, "numerator": "qx^4"},
              "convention": "native IREGI, raw Cartesian moment, (+---)",
              "method": "mpmath gamma/Feynman-parameter quadrature and differentiation",
              "mpmath_version": mp.__version__, "precision_checks": checks,
              "untouched_iregi": oracle,
              "conclusion": "Original IBP agrees; original PV and hybrid finite coefficients disagree."}
    encoded = json.dumps(report, indent=2) + "\n"
    if args.write:
        Path("validation/pv-high-rank/evidence.json").write_text(encoded)
    print(encoded)


if __name__ == "__main__":
    main()

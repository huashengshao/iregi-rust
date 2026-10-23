# Independent six-point parameter integral

This check addresses the largest original-IREGI comparison discrepancy in
`oracle-runs/n6-base-rank7.json`: the moment `qx*qz^6` (index 321). It uses SciPy
quadrature and a direct Feynman-parameter integral, independently of the Rust
recurrences, original IREGI, and scalar-master implementations. It is validation,
not a performance benchmark.

For the recorded shifts and masses, let `P = sum_i x_i p_i` and
`F = sum_i x_i m_i^2 - sum_i x_i p_i^2 + P^2`, with `x_i >= 0` and
`sum_i x_i = 1`. Shifting `k = q + P` makes every `kx` term vanish because
`gxz = 0`. The four surviving `kz^(2r)` Gaussian moments, including the
Feynman-parameter factor `Gamma(6)`, are

```
r = 0: 6/F^4
r = 1: 1/F^3
r = 2: 3/(4F^2)
r = 3: 15/(8F)
```

The Minkowski Gaussian sign and `(gzz)^r` cancel. Expanding the numerator with
the binomial factors gives the real OneLoop-normalized parameter integrand

```
-Px * (6*Pz^6/F^4 + 15*Pz^4/F^3 + (45/4)*Pz^2/F^2 + (15/8)/F).
```

Here `F >= 3`: the timelike shift components lie in `[0,2]`, so their variance
is at most 1, the minimum squared mass is 4, and the spatial variance terms
are nonnegative. Thus there are no thresholds or IR poles. The original
integral has superficial UV degree `7+4-12 = -1`, so it has no UV pole either.
Its native finite result is `i*pi^2` times the parameter integral.

The two final GK21 runs use different stick-breaking mappings, with orders
`[1,2,3,4,5,0]` and `[2,1,3,4,5,0]`. Their native imaginary values are
`-0.004930291971105481` and `-0.004930291971105485`. The mapping difference is
`4.34e-18`; the larger reported absolute quadrature error is `6.07e-14`.
These are estimated errors, not certified interval bounds.

With the oracle normalization `Q^2 = 82`, the independent value is
`-0.04464569264182684`, with estimated uncertainty `5.50e-13`.
The previous Rust expression evaluated with original binary64 masters differs
by `2.04e-10` in normalized absolute units (`1.95e-10` mixed error), while the
original binary64 IBP result differs by `1.17e-6` (`1.12e-6` mixed error).
Consequently, both previous binary64 paths fail the unchanged `1e-10` mixed
accuracy gate for this component. This check does not characterize a later
higher-precision or rescue implementation.

All original SciPy statuses remain in `sixpoint-simplex-oracle.json`.
Configuration 5 reaches its iteration cap on the same step that its estimated
error falls below tolerance, so SciPy 1.17 reports `not_converged`; configuration
6 allows one extra subdivision, stops after the same two subdivisions, and
reports `converged`. The report distinguishes those library statuses from the
error-estimate and independent-mapping accuracy gate. Earlier less accurate
runs remain visible.

To reproduce the final pair from the repository root:

```sh
source scripts/env.sh
timeout 120s python3 validation/pv-high-rank/sixpoint_simplex_oracle.py --write --run 5
timeout 120s python3 validation/pv-high-rank/sixpoint_simplex_oracle.py --write --run 6
```

Run the script without `--run` to repeat the exploratory rules as well. The
optional validation script finds the installed Nix SciPy/NumPy packages if
they are not on Python's default import path. Integrand temporary arrays are
chunked to limit memory; the SciPy quadrature rule and its points are unchanged.

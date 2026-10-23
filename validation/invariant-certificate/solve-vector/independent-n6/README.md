# Independent scalar N6 oracle preparation

`result.json` records six completed Gauss-Jacobi runs (orders 8,12,16 under
both mappings), each executed under a 45-second bound on CPU 12. All launcher
exit codes are zero; `runner.json` and separate logs retain their commands.

The independent OneLoop finite result is `4.298607666927012e-8`. Its native
IREGI value is `+4.242555714805930e-7 i`, with all pole coefficients zero.
The largest tight order/mapping difference is `3.97e-23` in OneLoop units.
Including the explicit binary64 reporting floor gives estimated uncertainty
`6.11e-22`, or `9.17e-16` after normalization by `35^4`. These are convergence
estimates, not certified bounds. The retained status is `estimated_converged`.
The optional adaptive GK15 cross-check has not been executed.

This oracle integrates the original scalar integral directly over its Feynman
parameters. For unit powers, N=6 and D=4-2ε, the finite OneLoop value is
`(+1) Γ(6-2) ∫ F^-4 = 6 ∫ F^-4`. The simplex volume is `1/120`.
Its UV degree is -8. Timelike components of every shift lie in [0,1], so
`F = Σx m² - Var(pt) + Var(px) + Var(py) + Var(pz) >= 29.75`.
There are no UV or IR poles. Native IREGI finite is `i π²` times this result.

The primary method uses SciPy's public `roots_jacobi` for all nodes and weights.
Under the stick-breaking simplex map, each cube axis has weight
`(1-t)^(4-axis)`. The Jacobi exponents are therefore `(alpha,beta)=(4-axis,0)`;
mapping the library's [-1,1] rule to [0,1] divides its weights by
`2^(alpha+1)`. Independent mappings and orders 8,12,16 check convergence.
SciPy adaptive GK15 cubature is an optional second quadrature method with its
own error estimate. No reduction recurrence, scalar-master code, or Symbolica
runtime enters this oracle.

The required raw OneLoop uncertainty is 1e-19, corresponding to 1.500625e-13
after dimensional normalization by `35^4`. Reported errors are estimates,
including a conservative binary64 reporting floor, not certified bounds.
Input, source and script hashes and library paths/versions are retained per run.

The wrapper input is `mu=3`, hence its scalar backend receives `mu²=9`.
An initial oracle request described `mu²=3`; the present pole-free finite
coefficient is scale independent, so this distinction does not alter it.

After obtaining the coordinated CPU window, run from the project directory:

```sh
source scripts/env.sh
timeout 45s python3 target/certified-scalar-matched/independent-n6/oracle.py --order 8 --mapping 0
```

Repeat separately for order 8/map1, order 12/maps0,1, and order 16/maps0,1.
The optional cross-check is `--cubature --mapping 0`, also under an external
timeout. Use `--report-only` to rebuild the summary without numerical integration.

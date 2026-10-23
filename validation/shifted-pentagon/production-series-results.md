# Exact-oracle production comparison: initial two cases

Both authorized precision pairs completed and were rejected by production.
Neither returned a successful value, so neither establishes oracle agreement or
disagreement. The source, original inputs, and acceptance thresholds were
unchanged. The exact independent oracle remains valid with enclosing radius
below `2^-321`.

| Working / requested bits | Public status | Process wall | Reduction call | Scalar masters |
| --- | --- | ---: | ---: | ---: |
| 128 / 128 | Unstable: recorded box failure `NonFiniteOutput` | 94.525 s | 89.585 s | 88.778 s |
| 256 / 128 | Unstable: `NonConvergent` | 156.392 s | 148.881 s | 148.099 s |

These durations are diagnostic observations from the frozen executable built
before the default stack-allocation optimization. They are not performance
benchmarks of the current working tree. Both processes completed within their
120/180-second bounds. The 384/128, 256/256 and 384/256 pairs remain unrun.

Each public call first attempted its exact-zero structural profile, then the
ordinary plan after rejection. Each attempt reached order 128 and evaluated
1,240 boxes; the public total is 2,480 boxes. An `analytic_rows` count of one
records the profile attempt, not a successful analytic result.

At 128 working bits the last recorded failure was pinch zero, but the error
field can be overwritten while scanning boxes, so this does not identify every
failing node or pinch. Its `2.5387e25` refinement estimate was retained from the
last completed successful rule; the failed order-128 box evaluation did not
compute a new estimate. At 256 working bits the order-128 assessment completed;
`6.346e21` is its final numerical difference from order 64. Increasing working
precision alone has therefore not qualified this fixture.

## Why this is more than insufficient quadrature order

Let `eta=2^-64` and `Fmin=1-eta`. The independent Symanzik construction gives
`F >= Fmin > 0`. The parameter representation documented in
`docs/research/shifted-pentagon.md` gives the four-dimensional pentagon along
the integration contour as

```text
J0(t) = -2 integral_simplex (F(z)+t)^(-3) dz,
simplex volume = 1/24.
```

For this fixture the production contour has scale and slope one:
`t=(1-i)u`, `u>=0`. Consequently

```text
|J0(t)| <= 1/[12(Fmin+u)^3].
```

With `u=x/(1-x)`, the mapped integrand is
`g(x)=(1-i)J0(t)/(1-x)^2`, and

```text
|g(x)| <= sqrt(2)*(1-x)/[12(Fmin*(1-x)+x)^3]
       <= B = sqrt(2)/[12*Fmin^3] ~= 0.117851.
```

An exact Gauss-Legendre sum has positive weights summing to one, so its modulus
is at most `B`; two exact quadrature orders differ by at most `2B ~= 0.235702`.
The observed differences of order `1e21` and `1e25` therefore reflect arithmetic
or branch-evaluation breakdown, not ordinary quadrature truncation. This bound
does not validate the implemented floating nodes, weights or master values, nor
does it isolate the failing operation. The near-degenerate DNS box formulas and
mass/invariant cancellation remain source-supported candidates.

The implementation details are in `crates/iregi-masters/src/pentagon6.rs`:
contour construction, order bookkeeping, box failures and convergence assessment
are deliberately retained unchanged. The next useful experiment isolates one
scalar box on this contour against an independent parameter-series formula.

## Evidence and review

`production-series-qualification.json` indexes the six per-case result, log and
run-manifest files. Each run manifest embeds frozen dependency hashes and the
qualified core source manifest, explicitly distinguishing its binary from later
production changes. Rejected lanes serialize `values: null` and exit with code
two. An independent agent reviewed both cases, the 12 recorded hashes per case,
classification, diagnostic interpretation and the contour bound; no actionable
defect was found. No production source changed during this qualification.

# Public precision comparison against the rational E6 oracle

The optional example `crates/iregi-rust/examples/e6_series_compare.rs` runs one
working/requested precision pair against `series-oracle.json`. It uses the
public `ReductionPlan` and `Workspace<Float>` APIs, singleton batching, IBP,
dimension shift one, rank zero, unit powers and OneLoop convention. It feeds
the original `delta=2^-32` routing, squared masses one and `mu=1` directly;
snapping, rescaling, automatic precision rescue and threshold changes are not
enabled. It checks every constructed input against its original exact rational.

Planned pairs are `(128,128)`, `(256,128)`, `(384,128)`, `(256,256)` and
`(384,256)`, written as `(working bits, requested bits)`. The impossible request
`(128,256)` is rejected by the harness. Initial process budgets are 120 seconds
at 128 working bits, 180 seconds at 256 and 240 seconds at 384. These are
diagnostic limits, not estimated benchmark latencies. Every invocation logs
plan, workspace and reduction stages; its output records core timing counters,
quadrature diagnostics and tracked precision for successful components.

## Exact comparison and classification

The independently generated reference is an exact center `c` with exact radius
`r < 2^-321`. A successful production value is converted to its exact represented
rational real and imaginary components `a,b`; no binary64 comparison is used.
The true squared complex error is enclosed by

```
max(abs(a-c)-r,0)^2 + b^2
    <= error^2 <=
(abs(a-c)+r)^2 + b^2.
```

The original fixture's kinematic scale is exactly one. The unchanged core
mixed error target is therefore `2^(19-requested_bits)*max(abs(output),1)`.
The example compares squared quantities exactly. An upper bound below this
target certifies agreement; a lower bound above it proves a violation. If the
target lies inside the enclosure, the result is explicitly unclassified rather
than a claimed disagreement. All three finite-domain pole slots must also be
exactly zero. A stricter pure-relative `2^-requested_bits` check using the L1
error upper bound is recorded separately and does not change the production
acceptance target.

Exit statuses distinguish agreement (0), harness/preparation error (1), a
production-rejected lane (2), proven disagreement/nonzero poles/successful
nonfinite output (3), and an inconclusive enclosure (4). Rejected lanes expose
no initialized scratch values. A failed stronger certificate alone is never
reported as a production false success.

## Structural conditioning audit

Write `eta=delta^2=2^-64`. The doubled external Gram matrix is
`Z=2*eta*diag(1,-1,-1,-1)`. Its spectral condition number is one, despite the
small determinant `-16*eta^4=-2^-252`. A small determinant alone therefore does
not diagnose a numerical failure here. The unscaled Cayley matrix approaches a
rank-one matrix; its determinant is `16*eta^4*(2+eta)` and its condition number
grows as `eta^-1`.

The geometry used by the E6 backend instead solves the Gram system. Its exact
quantities are

```
f = (eta,-eta,-eta,-eta),
v = (1/2,1/2,1/2,1/2),
B = -1/(2+eta),
b0 = 1/(2+eta),
b1 = b2 = b3 = b4 = -1/(4+2*eta).
```

These coefficients are moderate. Two source-supported loss mechanisms still
need numerical investigation:

- `Pentagon6Plan` forms `f_i=s0i-mi^2+m0^2` without explicitly preserving a
  mass-first grouping. Numerica's multiprecision addition/subtraction reduces
  tracked precision after exponent cancellation, even when the particular
  dyadic represented result is exact. The routing/mass combination can thus
  consume about 64 tracked bits. This is a possible propagation issue, not a
  measured error of the E6 implementation.
- At every quadrature node the five boxes share a complex mass `M=1+t`.
  Pinches zero and one select the complex-mass DNS fallback; pinches two,
  three and four permute into the `zero_external` contour branch. For pinch
  zero, exact DNS coefficients `a,c` scale as `(eta/M)^(3/2)`, about `2^-96`
  near `M=1`, although the general formulas form them from terms of order one.
  The exact equal-mass pseudothreshold `k=2` also passes through products of
  complex square roots, which can introduce a residual before taking another
  square root. Existing factored discriminants and Vieta formulas help but do
  not prove the residual is absent.

Relevant source locations are `crates/iregi-masters/src/pentagon6.rs`,
`dependencies/symbolica/lib/numerica/src/domains/float/multiprecision.rs`, and
oneloopmaster's `expressions.rs`, `box_integral.rs` and `box_complex.rs`.
The contour implementation already documents and protects some mass-first
sums with `in_order`/`coefficient_sum`. This audit proposes no production
regrouping or algebra changes.

Finally, the current maximum quadrature order remains 128 and acceptance
requires two consecutive successful differences. A 256-bit request may be
unable to qualify within that cap even at adequate working precision. The
comparison retains `NonConvergent`, the final order and its error estimate.
Working precision, tracked precision and independently certified agreement
remain separate observations.

## Reproduction

With the single Symbolica runtime lease available, from the project root:

```sh
source scripts/env.sh
RUST_MIN_STACK=67108864 IREGI_PREPARATION_PROFILE=1 \
  cargo run -p iregi-rust --example e6_series_compare -- \
  validation/shifted-pentagon/series-oracle.json 256 128 \
  target/e6-series-256-128.json
```

The prepared isolated executable uses private copies of the qualified core,
master, Symbolica, oneloopmaster and JSON archives. Their hashes, source
qualification manifest and eventual executable identity are recorded under
`target/e6-series-compare/`; a runtime qualification must retain them with its
results. Merely compiling this example establishes no production agreement or
precision-convergence claim.

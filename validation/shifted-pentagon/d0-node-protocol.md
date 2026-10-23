# Isolated finite-box diagnostic

The initial exact-oracle E6 runs reject the tiny-routing fixture at 128 and
256 working bits. This diagnostic removes E6 geometry and quadrature and tests
one scalar D0 point. It compares an unchanged source snapshot with a private
six-call substitution using an existing upstream helper. Production remains
unchanged.

## Specific point and independent oracle

Take the first pinch of the original pentagon, with `eta=2^-64` and D0 ordering

```text
p = eta * [0,-2,-2,0,0,-2],
m1_squared = m2_squared = m3_squared = m4_squared = M = 2-i,
mu_squared = 1.
```

This is the rational contour point `x=1/2`, `t=1-i`, corresponding to the
production ray. It is a representative point, not an abscissa of the even-order
Gauss rules. A passing result here does not reproduce or resolve a failure at a
different quadrature node.

Constructing the Symanzik polynomial independently from the four retained
Cartesian shifts gives, on the three-dimensional simplex,

```text
F = M + eta*P,
P = 2*(x1*x2+x1*x3+x2*x3),
D0 = M^(-2) * integral_simplex (1+eta*P/M)^(-2).
```

Since all parameters are nonnegative and sum to one,
`0<=P<=2*sum_(i<j) xi*xj<=1`. The simplex volume is `1/6`.
`d0_contour_node.rs` uses Symbolica to calculate the squared distances, series,
stick-breaking Jacobian, polynomial antiderivatives, and endpoint values. It
retains terms through order four in `z=eta/M`, then uses Symbolica's polynomial
evaluation over exact `Complex<Rational>` values. Sanity checks are

```text
D0 = 1/(6*M^2) - eta/(10*M^3) + O(eta^2).
```

In particular, snapping the invariants to zero would omit a correction much
larger than the target accuracy. No snapping is permitted in this experiment.

As `|M|^2=5` and `|M|>=2`, let `r=eta/2`. The complex remainder is enclosed by

```text
R = r^5*(6-5*r)/(30*(1-r)^2) < 2^-327.
```

Symbolica verifies the underlying generating-function tail identity. For a
returned finite output, its exact rational distance squared `d2` from the
series center is compared with `(tau-R)^2` and `(tau+R)^2`, where
`tau=2^-109`. This certifies agreement, proves a violation, or leaves an
explicitly inconclusive interval. Both pole slots must vanish exactly.
The absolute node target is a diagnostic target; it is not a claim about the
public E6 mixed tolerance. Nonfinite outputs and evaluator errors remain
separate failures.

## Narrow source hypothesis

Every opposite-channel product is zero for this routing, so no relabelling can
provide the two nonzero channels required by
`box_complex::supported_kinematics`. Complex masses therefore select
`box_four_masses_dns`. The existing equal-mass vacuum branch applies only when
all six invariants vanish. There is no existing small-momentum neighborhood
branch covering this point.

DNS constructs `k12=k13=k14=2` through `(M+M)/(sqrt(M)*sqrt(M))`.
Finite-precision complex square-root products can leave a residual before the
next square root at the pseudothreshold. Its generic coefficient formulas also
form `a,c=O(eta^(3/2))` from order-one terms, and the exact `b=0` can be lost if
the pseudothreshold roots acquire a residual. DNS uses the direct
`negative_quadratic_roots` function, not the later Vieta root helper.

The existing `triangle.rs::r_function_of` returns exactly `(r,d)=(1,0)` for
zero invariant and equal masses while retaining the upstream branch rules for
other inputs. The private candidate changes only the six DNS `r_function(k)`
calls to `r_function_of(p,mi,mj,sqrti,sqrtj)`; the exact patch is
`dns-r-function-of.patch`. No coefficient, quadratic-root, sheet or
divided-difference formula changes. This isolates the pseudothreshold helper
hypothesis; it does not address every remaining cancellation mechanism.

Existing facilities were checked in three places before choosing the oracle:

1. Symbolica `AtomCore::series`, `MultivariatePolynomial::integrate`, endpoint
   replacement and exact polynomial evaluation already provide all algebra.
2. Symbolica `examples/series.rs`, oneloopmaster's series-based removable-limit
   tests and the accepted `e6_parameter_series.rs` demonstrate those operations.
3. FeynKit `IntegralFamily::symanzik` provides equivalent parametric preparation;
   its integral-family module does not provide a small-momentum D0 evaluator.
   The oneloopmaster tiny-invariant D0 regression covers a different,
   contour-admissible family and uses existing mass-first coefficient grouping.

## Frozen builds and bounded execution

The source and private dependencies are inventoried in
`target/d0-node-probe/source-inputs.json`. Two independent oneloop archives are
compiled from the private snapshots with identical flags and no optional
features. The example explicitly selects the expression backend, so the
candidate cannot accidentally evaluate a stale generated or prebuilt formula.
The executables are `target/d0-node-probe/d0_node_baseline` and
`target/d0-node-probe/d0_node_candidate`.

Run one process at a time under ROOT's Symbolica lease, initially bounded to
30 seconds each. Record oracle preparation, evaluator preparation and one-row
evaluation separately; a preparation timeout is not a numerical failure. Each
process writes its exact inputs, independent oracle, every Laurent slot,
tracked precision and comparison status. Preserve binary/source hashes and
logs with each result. Diagnostic durations do not qualify performance.

If the baseline does not reproduce the loss, the next experiment must use a
specific failing production quadrature abscissa. If both fail, inspect the
remaining DNS coefficient/divided-difference cancellations. If only the private
candidate passes, this supports the helper hypothesis for this node; adoption
still requires broader mass, branch, permutation, precision and Dual checks.

# Exact rational small-momentum D6 oracle

The optional Rust example `crates/iregi-rust/examples/e6_parameter_series.rs`
constructs an independent parameter-integral oracle. It calls neither the
reduction library nor oneloopmaster. Production code is unchanged. The oracle
is for one special positive-F family; it does not improve the established
digits of the generic fixture in `evidence.json`.

Take squared masses equal to one, metric `(+---)`, `q0=0`, and
`q1,...,q4=delta*e0,...,delta*e3`, with `delta=2^-32` and `eta=delta^2=2^-64`.
The doubled external Gram matrix is
`2*eta*diag(1,-1,-1,-1)`. Its determinant is `-16*eta^4=-2^-252`, so the
external span has rank four. Three timelike–spacelike pair distances vanish
exactly. Equal masses and these exact lightlike differences make this a
special family despite the nonsingular Gram matrix.

The one-loop Symanzik polynomials are

```
U = sum_i x_i,
F = U*sum_i x_i*m_i^2 - sum_(i<j) x_i*x_j*(q_i-q_j)^2.
```

On the simplex `sum_i x_i=1`, `x_i>=0`, the example verifies with Symbolica
that `F=1-eta*Q`, where

```
Q = x1*(1-x1) - x2*(1-x2) - x3*(1-x3) - x4*(1-x4).
```

Every `xi*(1-xi)` is nonnegative and at most `xi`. The triangle inequality
therefore gives `|Q| <= sum_(i=1..4) xi <= 1`, and `F >= 1-eta > 0`.
The parameter integral is consequently finite, with zero UV/IR poles and
unambiguous real analytic branch. The tighter range `-2/3 <= Q <= 1/4` is
unnecessary for this bound.

In the project's OneLoop normalization,

```
J1 = -Gamma(2) * integral_simplex F^-2 dx = -integral_simplex F^-2 dx.
```

Symbolica expands this integrand in `eta` through order `N`, inclusive. It
also differentiates the stick-breaking parameter map to obtain its Jacobian.
Its multivariate polynomial `integrate` and exact `replace` methods evaluate
the four unit-interval integrals over the rational field. No polynomial,
Dirichlet-moment, coefficient-expansion, or antiderivative algorithm is
implemented by the example. The first two exact coefficients are checked
against `-1/24` and `+1/45`.

For `eta<1`, the uniformly convergent generating function bounds the omitted
terms pointwise:

```
|sum_(k=N+1..infinity) (k+1)*(eta*Q)^k|
  <= eta^(N+1)*((N+2)-(N+1)*eta)/(1-eta)^2.
```

Symbolica verifies this closed form by subtracting its generated finite
series from `(1-eta)^-2`. Multiplying by simplex volume `1/24` gives the
absolute remainder bound returned by the example. Thus its exact rational
center, minus/plus that exact rational radius, encloses the defining integral.
For `N=4` the radius is

```
eta^5*(6-5*eta)/(24*(1-eta)^2) < 2^-321.
```

The example verifies this final rational inequality exactly. This is an
analytic enclosure, rather than an inference from agreement of successive
numerical quadratures. A future production comparison should first convert
the represented output to an exact rational using `NativeFloat::exact_rational`
and require `abs(actual-center)+radius < tolerance`. Converting the oracle
through binary64 would discard the property this fixture is intended to test.

## Existing facilities checked

1. Symbolica source: `AtomCore::series` includes the requested order;
   `src/poly/polynomial.rs` supplies `integrate`, `replace`, and `replace_all`;
   `Matrix::det` supplies both Jacobian and Gram determinants.
2. Symbolica usage/tests: the `AtomCore::series` example explicitly includes
   order four, and `src/poly/univariate/tests.rs::derivative_and_integral_are_inverses`
   verifies exact integration. The existing pentagon master likewise delegates
   quadrature polynomial differentiation and root operations to Symbolica.
3. FeynKit: `IntegralFamily::symanzik` in
   `references/gammaloop_feynkit/crates/feynkit-graph/src/integrals/parametric.rs`
   uses this sign convention. Its `massive_bubble_symanzik_and_shift_invariance`
   test checks `F=(x+y)*(x*m1^2+y*m2^2)-s*x*y`. The optional oracle assembles the
   documented one-loop formula directly using Symbolica, avoiding any reduction
   recurrence or production master as an oracle input.

## Reproduction and scope

From the project directory, with the single Symbolica runtime lease available:

```sh
source scripts/env.sh
cargo run -p iregi-rust --example e6_parameter_series -- \
  validation/shifted-pentagon/series-oracle.json
```

The output records exact centers and enclosing radii for orders zero through
four. Executable/source hashes and the independent review belong in a separate
qualification record. Generating this oracle does not qualify production
agreement, requested-precision convergence, generic or complex-mass E6
kinematics, Dual components, or runtime performance. Production failures at
the tiny invariants must remain visible and must not be removed by snapping.

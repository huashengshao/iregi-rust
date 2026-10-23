# Exact supplied-invariant certificate

This is an implementation proposal and an unconnected prototype. The public
six/seven-point supplied-G guard remains in place until integration and numerical
validation pass. The first restoration targets rank-zero IBP requests with a
regular rank-four primal Gram chart.

## Input meaning

The certificate uses the exact represented value of every input coefficient.
It constructs the relative Gram matrix

`K_ij = G_ij - G_i0 - G_0j + G_00`, for `i,j > 0`.

This is invariant under translations of the common momentum origin. Scalar
integrals admit analytic continuation to complex external vectors, so the
certificate imposes no real-Minkowski inertia restriction. For a Cartesian
tensor interface, a later extension must additionally compare this relative
Gram matrix against the supplied relative coordinate shifts, coefficient by
coefficient. Rank-zero scalar inputs need no coordinate witness.

For each four-element principal chart `A`, Symbolica constructs `det(A)` and
the bordered minors

`E_uv = det([[A, K_Av], [K_uA, K_uv]])`.

If the primal determinant is nonzero, every coefficient of every `E_uv` must
vanish in the caller's Taylor algebra. This is equivalent to the full Schur
complement constraint in that chart, without dividing by its determinant.
There are five charts with one residual each for six propagators, and fifteen
charts with three residuals each for seven. Off-diagonal residuals are essential;
principal minors alone do not establish the seven-point rank constraint.

The prototype prepares rational polynomial instructions and Taylor coefficients
using Symbolica's Dualizer. Its existing batch evaluator requires `Real`, so
`Complex<Rational>` cannot execute through that interface: exact ring execution
currently exists only in the scalar evaluator. Instead, the prototype maps exact
inputs and coefficients to Symbolica's certified `ComplexBall` domain and runs
the polynomial instructions across all active lanes. Increasing precision either
certifies a nonzero residual or produces an exact zero enclosure, whose center
and radius are both zero in both complex components. Only the latter can pass.
A zero-containing ball with positive radius remains unresolved, never accepted.
All represented input coefficients are dyadic; the polynomial operations can
therefore become exact at sufficient precision. A bounded precision budget
leaves an explicit unresolved diagnostic when they do not.

The prototype never accepts a small nonzero residual as zero. Rounded scalar products
may therefore receive an incompatibility diagnostic even when they were intended
to approximate a physical rank-four matrix. Higher arithmetic precision cannot
restore information already lost from the supplied input. No input is projected
or modified.

`f64` is converted through an exact 53-bit Symbolica `Float`; `DoubleFloat` is
the exact rational sum of its two represented limbs; arbitrary `Float` uses
Symbolica's `try_to_rational`. These conversions introduce no binary64 detour
for higher-precision values. Derivative coefficients remain distinct from sample
lanes.

No invertible primal chart produces an explicit `NoRegularChart` diagnostic.
This is not evidence that the input is invalid: lower-rank and rank-changing
Taylor strata require separate analytic profiles. All current public guards
remain until those profiles or explicitly qualified subdomains are available.

## Reduction integration

In a certified chart, use Symbolica's matrix solve for
`c = A^-1 K_Aw`. Set `f_i=K_ii-m_i²+m_0²` and
`C=f_w-sum(c_a f_a)`. Then

`D_w - sum(c_a D_a) + (sum(c_a)-1) D_0 = C`.

A nonzero `C` gives an inhomogeneous pinching identity. A zero `C` gives a
homogeneous power-transfer relation. The existing scalar compiler's routing
relation engine already distinguishes these cases and supports generalized
powers and dimensions. Integration must reuse that engine and its termination
rules, rather than implement a second recurrence. A particularly small integration
can supply that existing engine with four linear coordinates `r_i=(K_ai)`, one
for each member of the certified chart, and `r_0=0`. These covector projections
are an invertible linear coordinate system on the external span. Their linear
dependencies are therefore the physical momentum dependencies; they are not
time/spatial components and must never be used to reconstruct squared distances.
The original Cayley matrix still supplies the denominator constants. The
prototype exposes this construction as `certified_relation_coordinates`; the
scalar compiler should name its internal setter to reflect that contract.

Numeric cancellation in a
valid chart remains the responsibility of stability diagnostics and precision
rescue; exact compatibility alone is not a conditioning certificate.

## Existing facilities checked

All checks use the project's pinned Symbolica/Numerica revision
`9cdc2949cdb153478c1eca0d40690dc0abfc616e`, rather than the newer convenience
checkout in `references/symbolica`.

1. Symbolica/Numerica APIs and source: `Matrix::det`, `inv`, `solve`, `solve_any`,
   `rank`, and `row_reduce` in `lib/numerica/src/tensors/matrix.rs`; exact rational
   preparation and certified-ball domains in `src/evaluate/domain.rs`; the
   `Real` bound in `src/evaluate/batch.rs` and exact scalar `evaluate_in_ring`
   in `src/evaluate/evaluator.rs`; directed interval
   arithmetic in `lib/numerica/src/domains/float/interval.rs`; exact float
   conversion in the multiprecision float implementation.
2. Existing usage/tests: Numerica's matrix determinant and solve tests; this
   project's PV denominator charts, E6 geometry preparation, and precision-rescue
   exact DoubleFloat promotion. Symbolica already owns both determinant
   construction and Taylor expansion.
3. FeynKit equivalents: `IntegralFamily::affine_system`, its partial-fraction
   dependence search, and orbit-projector matrix solves use the same Symbolica
   matrix facilities. No higher-level full-Taylor supplied-Gram compatibility
   certificate was found in these implementations.

The prototype adds chart enumeration, input conversion and diagnostics only.
It adds no determinant, elimination, polynomial, or Dual arithmetic algorithm.

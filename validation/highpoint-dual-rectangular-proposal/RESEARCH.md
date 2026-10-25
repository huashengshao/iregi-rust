# Rectangular mass0/dilation helper: source-only proposal

This is an isolated new helper. It does not modify numerical-v1, production,
Cargo, or the previously frozen comparator. No compiler, test, evaluator,
integral, benchmark, or dependency bulk hash has been run for this helper.
The six Rust tests are source proposals and have **not** passed execution.

## Interface and exact directions

`prepare(base: &[Rational]) -> Result<PreparedJets, String>` accepts exactly 31
real parameters: 24 Cartesian shifts, 6 squared masses, and mu. It returns 124 exact
input coefficients in parameter-major order, a 4-by-2 exact expected multiplier
matrix, and the explicit ordered shape `[[0,0],[1,0],[0,1],[1,1]]`.
The matrix columns multiply independent unit-power and first-dotted scalar
Laurent arrays, respectively. It performs no scalar-integral evaluation.

The mass variable `a` adds directly to the first squared mass, while `b` sets
`lambda=1+b`. Thus shifts and mu become `lambda` times their base values; squared
masses become `lambda^2` times their base values, with `+a` on mass0 only. Both
independent direction seeds are 1. Every primal is checked against the supplied
exact base. This API does not alter or replace the retained physical fixture.

This is an ancestor-closed rectangular jet, with multiplication modulo
`a^2=b^2=0`. It includes the mixed derivative while excluding both pure second
derivatives. Symbolica constructs the multiplication table. The helper checks
that its reported order is unchanged, both `a*b` and `b*a` reach the mixed
component, and no pure-square component is represented; it implements no
multiplication table or algebra itself. All four Taylor factorials are 1.

## Expected response and independence

For the retained finite native D=4 scalar N6, rescaling the integration variable
and all dimensional inputs gives

`F(a,b) = lambda^-8 I6(m0_base^2 + a/lambda^2, other base inputs)`.

Modulo `a^2`, this is `lambda^-8*unit + a*lambda^-10*dot0`, since
`dI6/dm0_squared = +I6(powers=[2,1,1,1,1,1])` with the native denominator
`(k+q)^2-m^2+i0`. The expected ordered outputs are therefore unit, dot0,
minus 8 times unit, and minus 10 times dot0. These are a mathematical derivation, not
a numerical result or a claim of runtime accuracy.

The implementation constructs that response with abstract Symbolica unit/dot
variables. It derives the four a/b derivatives using ordinary
`AtomCore::derivative`, then differentiates the abstract variables to extract
the two matrix columns and evaluates overQ at zero. It never installs a fixed
coefficient matrix. Input jets instead come from `ExpressionEvaluator` and
`Dualizer`, independently of the expected ordinary derivative route.

The last mixed coefficient distinguishes independent additive mass from the
different co-scaled perturbation `lambda^2*(m0_base^2+a)`, whose dot0 response
would carry dimension minus 8 rather than minus 10. A source test constructs and
symbolically differentiates this negative control. No second mass derivative
is needed by this rectangular domain. There are two independent physical
directions here, unlike the earlier six-component pure-dilation pilot.

## Three actual reuse checks

1. **Symbolica APIs and source.** Inspected
   `dependencies/symbolica/lib/numerica/src/domains/dual.rs`:
   `HyperDual::from_values` checks ancestor closure and generates its own
   multiplication table; `DualNumberStructure::{get_shape,get_len,
   get_multiplication_table}` exposes existing metadata. Inspected
   `dependencies/symbolica/src/evaluate/dual.rs` and used existing evaluator
   vectorization rather than creating component algebra. Exact conversion and
   arithmetic use Symbolica `Rational`/Q throughout.
2. **Existing Symbolica usage/tests and qualified project helper.** Inspected
   `dependencies/symbolica/examples/dual.rs`, Numerica dual examples/tests,
   and the earlier
   `target/highpoint-dual-sensitivity/numerical-v1/base-helpers/jet_inputs.rs`
   (original helper SHA256
   `7b35954da337f1bb2191faa5ae05cec7e7f2ce1d6f4b88e90a64b104b350041f`).
   This helper follows its actual `Atom::evaluator_multiple`,
   `vectorize(&Dualizer::new(...))`, `map_to_ring(&Q)`, and
   `evaluate_in_ring` sequence, and its separate ordinary symbolic derivative
   route. The rectangular shape and physical directions are new inputs to
   those existing facilities, not missing algebra operations.
3. **FeynKit/gammaloop equivalents.** Inspected
   `../references/gammaloop_feynkit/crates/gammalooprs/src/integrands/process/evaluators.rs`
   around the existing HyperDual/Dualizer vectorization, and
   `../references/gammaloop_feynkit/crates/feynkit-cff/src/algebra.rs` around
   ordinary derivatives and Taylor factorial normalization. Both already
   delegate this work to Symbolica. No separate FeynKit numerical Taylor
   implementation is needed, and none is added.

## Proposed source tests and boundaries

Six source tests cover exact shape/order and omitted pure-second components;
independent input seeds and zero mixed input; all eight symbolic matrix
entries; distinction from co-scaled mass; rational base values distinguishable
only beyond 53 bits; and invalid parameter counts. The beyond 53-bit case changes
test base values only, preserving unit mass/dilation seeds and expected target
normalization. It does not change the future retained fixture or scalar targets.

Future qualification still needs an independently reviewed capture overlay,
finite lifecycle protocol, actual compiler/tests, complete parent/child
full-component contexts, all four native Laurent slots, exact fixture maps,
128/256 convergence, independent unit/dot reference agreement, batch/invalid/
empty controls and precision/sign snapshot checks. The mixed result tests one
mass-direction/dilation cross derivative; it does not qualify arbitrary mixed
mass/momentum derivatives, finite differences, public Dual constructors,
rigorous error enclosures, or performance parity. E6 backend uncertainty
transport remains unsupported by the private thin parent.

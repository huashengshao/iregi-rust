# Local OneLOop integration

Origin: https://github.com/alphal00p/oneloopmaster

Baseline revision: `8ec256fc26cb361b20e10f59c19beb35717ef32c`.

This directory contains the baseline package manifest, README, Rust sources and
prebuilt expression assets. It retains the upstream manifest's licensing status.
The parent workspace supplies the exact Symbolica/Numerica/Graphica patch pins.

## Analytic grouping in Dual compilation

`src/definitions.rs` and `src/expressions.rs` replace the exact identity
`if(z,z,0)` with a transparent Symbolica identity function only when preparing a
Dual evaluator. The original identity is an intentional arithmetic grouping
barrier. Its scalar zero arm, however, erases every nonconstant Taylor component
when the primal of `z` is zero. Independent equal-mass derivatives need those
components.

The mapped identity stays opaque during Atom normalization. The existing direct
translation path evaluates its argument once into the caller's instruction
scope, then inlines the identity body by returning that slot. This keeps the
rounding/grouping needed by complex-axis tests, preserves every component, and
introduces neither a runtime callback nor an extra conditional branch. A guard
with identical nonzero/zero branches was avoided because Symbolica deliberately
uses separate expression caches for the two branch scopes.

All transformations use Symbolica's `replace_map_bottom_up`; only structurally
identical condition/true arguments with a literal zero false argument match.
The ordinary scalar evaluator, generated Rust scalar kernels, and non-identity
conditionals remain unchanged. Regression and physical finite-difference tests
are in `../../crates/iregi-masters/tests/physical_derivatives.rs`.

## Bounded helper inlining before Dual compilation

The same Dual-only map rebuild asks Symbolica to inline leaf helper bodies of at
most 256 encoded bytes, and pure forwarding aliases whose arguments are only
variables or numbers. Symbolica's existing symbol inspection and function
registration options perform this transformation; no algebra is implemented
locally. Helpers containing other registered helper calls stay outlined unless
they are pure aliases, bounding expansion of nested expression graphs.

This targets redundant helper-component evaluation after Dualizer retains all
arguments of an outlined helper. Scalar interpretation and generated scalar Rust
remain unchanged. Qualification compares the same physical high-precision finite
differences and legacy Dual tests with the mapped-identity baseline; measured
results are recorded in the master's validation evidence once available.

## Euler–Mascheroni constant in reusable Rust emission

The exact constant metadata and native constant table recognize Symbolica's
`euler_gamma()` constant, which appears in IREGI's normalization. Generated code
initializes it with Symbolica's `Real::euler` at the requested numeric precision;
there is no binary64 intermediary or local approximation. This extends the
existing constant export used for pi and dilogarithms, allowing the same Rust
batch emitter to accept normalized reduction graphs.

The two compile-time unit-test fixtures in `tests/data/` are unchanged copies
from the baseline revision above. They are retained so the dependency's own
unit-test target can compile when qualifying emitter/runtime modifications.

## Exact represented-value access for certified zero predicates

`NativeFloat::exact_rational` exposes exact represented input values without a
binary64 detour. Binary64 uses Symbolica's 53-bit float conversion, DoubleFloat
adds its two exact limb rationals (including sparse limbs), and arbitrary Float
uses its existing exact conversion. Nonfinite inputs return `None`. A default
`None` preserves custom numeric implementations while allowing callers to report
that a required certificate is unavailable. IREGI uses this before treating a
rounded scalar invariant as exactly zero; no scalar-master arithmetic changes.

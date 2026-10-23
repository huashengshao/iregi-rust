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

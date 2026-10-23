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

## Opt-in ordinary-root stack-allocation experiment

`OneLoopExpressions::evaluator_with_stack_reuse` builds the same exact ordinary
graph as `evaluator`, then calls Symbolica's existing `optimize_stack` once.
Default compilation, Dual compilation, prebuilt assets and generated production
kernels remain unchanged. The allocator only reassigns temporary storage; it
does not simplify expressions or reorder arithmetic. This is an experimental
entry point whose correctness and performance evidence must be recorded before
any default adoption.

Reuse checks: Symbolica's `src/evaluate/tree.rs` returns fresh root SSA directly
from `linearize_multiple` for direct translation with zero Horner iterations;
`src/evaluate/optimize.rs` provides the existing lifetime allocator. Its branch
test `nested_multi_result_branches_keep_common_operations_in_scope`, and the
shared-function tests in `src/evaluate.rs`, exercise allocation with lazy
branches. FeynKit's `soft-ct-evaluator-memory` reproduction programs likewise
apply it to freshly compiled zero-Horner graphs. No alternative algebra or
allocator is implemented here. Already allocated graphs must not be allocated
again: Dualizer and shared-body compilation already perform this step.

`examples/stack_reuse_probe.rs` qualifies the opt-in in an explicit artifact
directory. It records original exact represented inputs, Laurent output order,
scale/normalization conventions, root and deduplicated helper slot counts,
ordered instruction provenance, and numerical batch parity. Its C0/D0 inputs
are copied from the recorded `validation/native-policy` experiment. It checks
empty, singleton, odd, batch-32, reordered and reused batches, plus DoubleFloat
and Float256. `--emit` exports paired baseline/candidate Rust batch modules and
one exact constant table to that artifact directory only. These modules retain
the Whole batch policy. The probe reports no timing measurements; compiled
native parity and controlled timing remain separate qualification steps.

The transparent C0/D0 root probe passed 40 batch/domain configurations per
family, comparing 672 complex outputs each with identical represented values,
precision metadata and signed zeros. Root temporary counts changed from 132 to
7 for C0 and from 24,777 to 24 for D0; shared helpers were unchanged. Exact
instruction provenance also agreed. The evidence in
`../../validation/stack-reuse/qualification.json` explicitly separates these
three Laurent outputs from the complete IREGI scalar adapter and records the
initial three-call wrapper probe, which showed no root allocation reduction.
These are correctness and storage results, not runtime measurements.

The complete six-output IREGI scalar factory also passed the paired C0/D0
probe: 40 configurations and 1,440 complex outputs per family, including
massless and scaleless controls. The actual factory root uses 220 to 8
slots for C0 and 25,010 to 25 for D0; shared helpers are unchanged. This
candidate changes only the ordinary factory call in an isolated source
snapshot. The default remains unchanged. Exact source, binary and dependency
hashes, inputs, instruction provenance and parity records are in
`../../validation/stack-reuse/production-factory/qualification.json`.
Core/E6 qualification and compiled-native parity remain separate checks.

# C0/D0 production Dual mass identities: source protocol

Status at preparation: **source only; no native import, build, numerical run, or qualification claim**. ROOT must grant a serialized runtime separately. The target is installed wheel004, not whatever a later workspace rebuild produces. The manifest freezes the harness, inputs, owner API evidence, and wheel004 native library hash. A runtime mismatch is a failed attempt.

## Fixed scope and inputs

One massive spacelike scalar triangle and one massive spacelike scalar box, one lane each, rank zero, D=4-2ε, unit base propagator powers. Time-first shifts, masses squared, and μ=3 are exact integer strings in `inputs.json`; no input is a Python float. The geometry comes from accepted generalized cases `n3_p123_h4_mode0` and `n4_unit_h1_mode0` in `validation/generalized-pv/reference-capture.json`. Their original dimensions/powers differ: only geometry is reused. This is an independent identity comparison, not a new Fortran agreement claim.

For each family, evaluate the same six-component mass jet at 128 and 256 working bits, both requesting 53 accuracy bits, through the public Python `ReductionPlan` → `Workspace` → `reduce_batch` API. Base method: hybrid; independent raised-power reductions: IBP. All plans use native IREGI normalization and input preservation. The finite native IREGI result can be imaginary: no projection onto its real part is made.

One lane is deliberate: historical six-component D0 evaluator preparation/full finite-difference validation took 224.83 seconds for five cases at 384 bits. This small experiment qualifies the new core/transport identity gap without expanding to additional geometries. It makes no new throughput or multi-lane isolation claim. Existing C0/D0 master finite-difference evidence remains separately scoped in `audit.md`.

## Taylor weights, signs, and four Laurent slots

The shape is `[00,10,01,20,11,02]`, in that exact order. Seed squared mass 0 with `[4,1,0,0,0,0]`, squared mass 1 with `[9,0,1,0,0,0]`; all other inputs have zero derivative components. These are Taylor coefficients, not raw derivatives. This convention is explicit in `dependencies/symbolica/src/evaluate/dual.rs` around lines 843–846 and in Numerica's factorial-normalized transcendental series in `dependencies/symbolica/lib/numerica/src/domains/dual.rs` around lines 1160–1188. The existing `physical_derivatives.rs::stencil` solves exact Symbolica matrix weights with a unit right-hand side at the requested degree, also selecting normalized Taylor coefficients. Existing wheel regression `test_dotted_propagator_matches_dual_mass_derivative_all_laurent_slots` checks the first-order sign for B0.

For the denominator `(q+p_i)^2-m_i^2+i0`, differentiation with respect to `m_i^2` raises its power with positive coefficient ν_i. Repeating twice at unit initial power gives coefficient 2, divided by the Taylor 2!; a mixed derivative gets coefficient 1. Thus the explicit fixed comparison is:

| Dual component | Raised powers on propagators 0,1 | Other powers | Taylor weight |
| --- | --- | --- | --- |
| 00 | 1,1 | 1 | 1 |
| 10 | 2,1 | 1 | 1 |
| 01 | 1,2 | 1 | 1 |
| 20 | 3,1 | 1 | 1 |
| 11 | 2,2 | 1 | 1 |
| 02 | 1,3 | 1 | 1 |

No symbolic manipulation, finite-difference stencil, differentiation engine, or polynomial algebra is implemented in this harness. It selects these six fixed existing-API requests. Symbolica supplies all Dual propagation and all Float/ComplexFloat comparison arithmetic.

Check every `[UV single, IR single, IR double, finite]` entry for all six components. Since all masses are positive and the chosen spacelike C0/D0 integrals and their dotted versions are UV/IR finite, additionally require exact zero for all three pole entries on both sides. An identical spurious pole is a failure.

## Precision and dimension normalization

The production Python conversion is `crates/iregi-python/src/scalar.rs::output_components`, which invokes `PythonNumber::output` for each component. The `Float` implementation directly wraps a clone of `Complex<Float>` in the owner `PythonComplexFloat`; it does not call `to_f64`. The installed owner stub documents `Dual.values` and `ComplexFloat.real/imag` as full-precision objects. The harness checks their actual types and finite values.

Evidence serializes each real/imaginary component as `Float.as_integer_ratio()` arbitrary-sized integer strings plus its precision; the display string is supplementary. Comparison copies those exact represented values via `Float.from_ratio` to at least 512 bits, preserving every stored bit. This does not manufacture missing digits or imply 512-bit integral evaluation. No result uses Python `float`, Python `complex`, a decimal→float bridge, NumPy, or JSON floating-point serialization.

For component α=(a,b), the mass dimension is `d=4-2N-2(a+b)`. Use fixed Q=4 for C0 and Q=5 for D0, the maximum of μ, shift magnitude, and square-root mass at the fixed input. Compare

`abs(actual-expected) / (Q**d + abs(expected)) <= 1e-10`.

The normalization is dimensionally consistent because each derivative is with respect to a squared mass and each seed is one unit of squared mass. Q and the tolerance are constructed as owner Floats from strings; exponentiation and norms use owner operations. Retain the exact ratio of each error and normalization scale. At each precision there are 24 identity checks; each family totals 48. Separately compare 128-bit versus 256-bit Dual results and independent raised-power results, 24 each, using the same criterion. This establishes agreement across increased precision at a fixed requested accuracy; it does **not** establish 128- or 256-bit achieved accuracy.

## Failure visibility and bounded capture

There are 14 evaluations per family (two Dual plus six ordinary requests at two precisions). Each plan/workspace/reduction phase is checkpointed to JSON and stdout before it starts. Failed lanes retain their status, diagnostics, fallbacks, and execution statistics. Their corresponding identity/convergence comparisons are explicit failures; no failed lane is replaced with zero or dropped. Exceptions and incomplete/timed-out processes cannot pass. Every output attempt directory must be new.

The capture supervisor pins its child to CPU 0 and sets Rayon/OpenMP/OpenBLAS/MKL thread counts to one, with the existing historical master-validation Rust worker stack setting of 64 MiB. Bounds are **180 seconds C0, 360 seconds D0**, including import/provenance checks/plan preparation/evaluation/comparison; then SIGTERM with a ten-second grace and SIGKILL if needed. These are validation safety bounds, not timing/performance gates. Launch/termination/evidence-parse failures are retained as `capture_failed` instead of leaving an apparent running capture. No concurrent Symbolica runtime is authorized by this protocol.

After ROOT grants the corresponding family lease, from `/shared/external/iregi/iregi-rust`:

```bash
source scripts/env.sh
.local/tirust-wheel-004-env/bin/python -I target/c0d0-dual-identity/run_bounded.py C0 --attempt attempt001
```

Only under a separate/continued explicit D0 lease:

```bash
source scripts/env.sh
.local/tirust-wheel-004-env/bin/python -I target/c0d0-dual-identity/run_bounded.py D0 --attempt attempt001
```

Do not rerun an attempt path. Preserve every failure before any source revision. Successful evidence requires exit zero, no timeout, all 14 successful evaluations, 48/48 identities, 48/48 precision comparisons, matching frozen hashes, and no exception. Native inputs/results remain accessible in each family's `results.json`; `capture.json` records bounds, exit/timeout, commands, and output hashes.

Not included: general static Dual/DoubleFloat coverage, thresholds or massless/Gram boundaries, physical numerator/MadLoop checks, new finite differences, performance qualification, or any change to production implementation.

# C0/D0 production Dual mass identities: source protocol

Status at preparation: **source only; no native import, build, numerical run, or qualification claim**. ROOT must grant a serialized runtime separately. The target is installed wheel004, not whatever a later workspace rebuild produces. The manifest freezes the harness, inputs, owner API evidence, and wheel004 native library hash. Every guarded source and that same historical installed native library are checked before and after the run; a mismatch or an incomplete guard set fails the attempt. The earlier runner/protocol/manifest/commands/review draft is preserved under `draft001/`. Subsequent project checkpoint 4fe1a1e does not replace the wheel004 native/source identity.

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

The capture supervisor pins its child to CPU 0 and sets Rayon/OpenMP/OpenBLAS/MKL thread counts to one, with the existing historical master-validation Rust worker stack setting of 64 MiB. **C0 has a 200-second total bound: at most 180 seconds of work plus a 20-second reserve for cleanup and final accounting. D0 is a separate future 380-second proposal: 360 seconds of work plus the same 20-second reserve.** The work deadline includes pre-run guards, native import, preparation, evaluation, and comparison; post-run guards and evidence hashing consume the reserved final accounting allowance. The existing `inputs.json` bounds of 180/360 therefore remain unchanged and mean work bounds. These are validation safety bounds, not performance gates.

Process lifecycle is delegated to the exact reviewed helper copied from `target/native-f64-opt-in/qualification/lifecycle.py`, SHA256 `c193cd7282d63b63a8f627612df684242a2a8941d1d0a35588514d0415ab8824`. Its bytes remain unchanged. The caller adjusts its public work-deadline attribute to reserve 20 rather than eight seconds. `execute` owns a new process group, cleans it in `finally`, and checks the entire group even if its original leader already exited. Cleanup defers signals, sends TERM, waits up to one second before KILL, reaps the leader, and checks that the group is gone. KeyboardInterrupt/SIGINT/SIGTERM/work-deadline cancellation cannot leave a successful capture or skip owned-group cleanup.

The helper's terminal callback persists `process-terminal.json` and the summary **before** any post-run evidence read or hash. A failed preflight also receives a terminal no-launch record. After cleanup, the supervisor checks every frozen source, the manifest itself, and the installed historical wheel004 native library again, including after failed/cancelled work when time allows. Missing/incomplete post-run guards fail admission. An aggregate timer bounds final accounting; TERM/INT during final accounting are recorded and deferred. Both streams are preserved in `runtime.log`. Signal cancellation, launch/cleanup/read/hash failure, a remaining owned process group, a changed input, or deadline excess fails the attempt. No concurrent Symbolica runtime is authorized by this protocol.

Final admission has an explicit protected completion boundary. The aggregate alarm stays armed through the final summary save. TERM/INT/ALRM are blocked only across that atomic save and a subsequent pending-signal/cancellation/deadline check; a cancellation or deadline crossed during the write revokes the provisional pass and writes failure. The qualification completes at that final check after the durable save, with no further successful-path evidence processing or reporting. Restoring handlers and returning the process exit code follow the boundary. A nonzero supervisor exit cannot be admitted as success even if an earlier provisional record exists.

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

Do not rerun an attempt path. Preserve every failure before any source revision. Successful evidence requires exit zero, no timeout/cancellation, the whole owned process group gone, all 14 successful evaluations, 48/48 identities, 48/48 precision comparisons, complete matching guards before and after, total deadline respected, and no exception. Native inputs/results remain accessible in each family's `results.json`; `process-terminal.json` preserves process exit/cleanup independently of later bookkeeping, and `capture.json` records all bounds, guards, commands, terminal state, and output hashes.

Not included: general static Dual/DoubleFloat coverage, thresholds or massless/Gram boundaries, physical numerator/MadLoop checks, new finite differences, performance qualification, or any change to production implementation.

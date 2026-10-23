# One bounded ordinary fused-evaluator CSE trial

Source-only proposal, 2026-10-23. No candidate code, compilation, numerical run,
timing, production change, or adoption is included. CLI coefficient timing
remains separately frozen and unrun. This proposal follows
`target/core-cse0-audit/design.md`; it proposes one candidate, not a search over
Horner/CPE settings.

## Target and possible benefit

The retained `validation/benchmark/baseline-6b24c03-licensed/results.json`
bubble rank-one batch-32 row reports 143.942 us unprofiled Rust latency against
97.462 us for the original IREGI kernel. Its separate instrumented run reports
143.043 us total, 10.053 us arguments, 25.751 us masters, and 100.946 us reduction
plus inspection. Therefore the measured non-master total is 117.292 us, of
which about 6.292 us lies outside the three recorded stages. These are historical
6b24 observations, not measurements of the current final implementation.

The 100.946 us stage contains both Symbolica execution and Rust finite checks,
precision checks, guard/envelope comparisons and result copies. There is no
evidence yet that duplicate evaluator instructions dominate it. CSE cannot
remove these inspection costs, argument certification, scalar masters, lane
compaction or allocations. The experiment must separately observe evaluator
execution and inspection while continuing to time the complete unchanged call.
Do not subtract medians from different profiled/unprofiled runs to claim a
recoverable speedup. A smaller instruction count alone is not acceptance.

## Exact seam and exclusion boundary

Change only the ordinary invocation that builds `PreparedExecution::reduction`
in `crates/iregi-rust/src/execution.rs`, currently near line 758. Its output tuple
is, in order: every requested tensor moment and all four Laurent slots; local
stability outputs; then fused primal-envelope outputs when present. The input
tuple is the complete ordered kinematic parameters followed by every leaf's
native Laurent slots. Preserve both tuples and all existing symbolic expressions,
aliases, monitor operation counts, thresholds, masks and inspection functions.

Keep the shared `compile_exact` behavior unchanged for every other call site:
master arguments, raw-distance polynomials and positive envelopes, exact-zero
certificates, snapping probes, activation predicates, quadrature coefficient and
convolution graphs, and the separate Dual primal monitor. Do not change scalar
master factories, contraction, CLI numerator preparation or master batch policy.

The narrow candidate helper uses the same fresh direct0 builder as today. When
the requested layout is ordinary, replace its one `optimize_stack()` call with
the existing public Symbolica operation:

```rust
// Typed empty output slice, EXACT same ordered parameter slice, no aliases/map.
let empty: ExpressionEvaluator<Complex<Rational>> =
    Atom::evaluator_multiple(&Vec::<Atom>::new(), parameters)
        .direct_translation(true).horner_iterations(0).cores(1).build()?;
exact.merge(empty, Some(0))?;
```

Use the real evaluator as `self`. Export and assert the empty program has the
same input count and zero outputs, instructions, constants, constant functions
and subevaluators. Merge itself restores SSA, removes common instructions and
allocates; do not add another allocation pass. Build metadata must retain the
actual ordered parameters because merge checks only their count. No realness
annotation is currently applied here; any future annotation belongs after merge.

For a Dual layout, call the existing unmodified builder/Dualizer path. Do not
merge before or after Dualizer. This also leaves the separate ordinary primal
monitor of a Dual workspace untouched. Validate its exact exported program and
ordered shape remain identical. Ordinary children of an ordinary parent may use
the same seam; record their individual graphs and routes. A private experiment
must use separate plans/caches per mode or pass the candidate mode explicitly in
its private cache key. Never toggle an environment mode on an already cached
plan and interpret cache reuse as a candidate measurement.

## Semantics that cannot be assumed

`merge(empty, Some(0))` avoids the builder's indeterminate counting, coefficient
collection and function-map Horner rewriting. It still sorts remapped Add/Mul
operands and may coalesce Pow/Powf/builtin/pure external calls. Floating-point
association, signed zero and tracked Float precision can therefore change even
when no instruction is deleted. It is not a storage-only transformation.

Preserve all lazy control and guard semantics; do not exclude the monitors from
the tuple, change their predicates, or simplify the branch tests. Symbolica CSE
tracks conditional ancestry and reuses only an enclosing-scope definition. A
qualified candidate must also demonstrate that singular operations remain
inactive on their original paths. Never obtain a faster result by marking more
lanes failed, skipping outputs, weakening guards or suppressing diagnostics.

Core expressions use registered constants such as pi/Euler gamma. Compare their
full symbolic definitions, tags, fixed arguments and positions, not their exact
evaluator's placeholder rationals. All existing helper signatures, bodies and
capture metadata must remain identical. Unexpected stateful callbacks are an
admission failure. Pure builtins must be inventoried explicitly; the empty
program adds no callbacks or helper bodies. No new handwritten optimizer,
polynomial manipulation, rational simplifier or branch-rewriting algorithm is
permitted.

## One implementation sequence and stopping points

1. **Exact-only census and proof, external bound 120 s per topology.** One copied
   current core and one driver, using the completed current Cargo debug native
   object closure. Prepare direct0 once per graph, clone the exact evaluator,
   merge the clone with the checked empty program, and retain both exports.
   Start with N2 ranks 0/1, N3 ranks 0/1, and an N4 rank-2 lazy-branch control;
   include native and OneLoop conventions. Record parent/child identity, ordered
   parameters, basis, output offsets, constants, helper metadata, operation and
   instruction counts, temporary slots, allocation and CSE preparation times.
   If there are no useful duplicates or preparation becomes excessive, stop
   instead of adding another mode or optimizing other graphs.

2. **Exact all-output equivalence.** Reuse the existing export/provenance tooling
   from the allocator and CLI proof experiments. The old allocator's ordered
   primitive identity proof is insufficient because this pass reorders operands.
   Every arithmetic expression used for a proof must be constructed and
   normalized through Symbolica. For straight-line ring-supported portions,
   prefer `map_to_ring`/`AtomField`. That existing API rejects builtin functions
   and cannot symbolically evaluate both conditional arms, so it alone does not
   prove the fused guard graph. A bounded extension of the validation-only
   exported-program decoder may reconstruct Symbolica expressions for pure
   functions and structured IF joins, retaining branch predicates and execution
   paths. It must read complete RHS values before an aliased write, compare every
   output (including all guard outputs), and prove zero differences with Symbolica
   exact normalization, not sampled evaluations. Compare normalized control paths
   as an additional check, while explicitly relying on Symbolica's structured SSA
   and CSE dominance implementation. Atom identities and normalized controls are
   not an independent proof of branch-local definedness: an incorrect reuse of a
   value defined only in the then arm can reconstruct an equal Atom while reading
   stale storage in the else arm. They also do not independently establish that
   an inactive singular operation stays unevaluated. Keep this trusted-compiler
   limitation in the proof artifact and require the numerical lazy-branch,
   mixed-lane, alias and signed-zero regression witnesses before qualification.
   Reject unhandled exported instructions, callbacks or ambiguous branch layouts;
   do not treat a partially proved program as qualified. Existing Symbolica CSE
   branch/dependent-duplicate regressions supplement this program proof.

3. **Full unchanged acceptance path.** In one paired driver, instantiate the
   baseline and candidate exact preparations with independent numerical buffers.
   Exercise f64, DoubleFloat, Float128/256, mixed input precision and beyond-53-bit
   inputs. Compare all native Laurent slots and tensor components before any
   contraction. Require the existing dimensionally normalized 1e-10 reference
   criterion in binary64 and higher-precision convergence; record exact represented
   values, precision and signed-zero metadata separately, since arithmetic
   reordering is not guaranteed bitwise-neutral. Any changed status, flags,
   branch outcome, diagnostic or public execution counter is an investigation
   failure until independently explained. Include lightlike equal/unequal bubbles,
   a scaleless UV/IR cancellation, complex widths, a near-Gram rejection, false-zero
   and nonzero derived-invariant cancellation, signed-zero branch controls,
   subnormal and mixed-precision failures, invalid-lane isolation, empty/odd/reordered
   batches and reuse. Existing Dual cases and their exported graphs must stay
   unchanged, including all ordered mixed Taylor components. Keep failed cases
   visible. Do not use process exit0 or a contracted amplitude as the only check.

4. **One coordinated timing, only after correctness.** Use the same two frozen
   preparations/binaries for all declared families and widths1/32. Retain complete
   warm-call timing with identical allocation/cache policy, paired fixed blocks,
   calibration, every output/status check, and separate plan/preparation cost.
   Add private timers immediately around `reduction.evaluate_batch` and around the
   subsequent unchanged inspection loop to diagnose the target; these instrumented
   observations are separate from uninstrumented acceptance. A regression or noisy
   row remains visible. Current debug objects qualify semantics/census only; any
   performance claim needs a later matched optimized build and quiet grant. No
   inference about IREGI parity follows from this private diagnostic alone.

## Fast build reuse and provenance

Reuse `target/master-cse-census/preparation.json`, bound to
`validation/near-vacuum-production/attempt004/build.log` and its qualification.
It records actual completed Cargo events, source hashes, profiles/features and
native ELF archive members. Current selected artifacts include Symbolica
`libsymbolica-06e42762cabb77d9.rlib` (opt2), masters
`libiregi_masters-f07797f04e91954e.rlib` (opt0/default), and serde_json
`libserde_json-d657c5438f354a41.rlib`. GMP's recorded native link directory is
`target/cargo-build/debug/build/gmp-mpfr-sys-c4459d582ef76f89/out/lib`.

Before an authorized build, extend the same event-based inventory for the copied
core's serde/thiserror and all transitive/native dependencies. Verify/freeze or
pre/post-hash the coherent set; do not guess hashes from filenames or borrow an
optimized directory. Link native objects without ThinLTO or Cargo feature changes.
A small non-test copied core with a validation-only accessor plus one driver avoids
instantiating the full workspace test suite and permits baseline/candidate exact
graphs in one process. Do not build two huge independently optimized workspaces
for this first decision. No dependency recompilation is part of the proposal.

## Existing facilities checked

- Symbolica `evaluate/optimize.rs::merge`, stack restoration/allocation, scoped
  instruction CSE, `evaluate/instruction.rs` complete export, and
  `evaluate/evaluator.rs::map_to_ring`/ring evaluation were inspected.
- Symbolica tests cover dependent duplicate collapse, branch ancestry and nested
  conditional CSE; current project CLI/allocator proofs were inspected. This is
  source review, not a claim those tests were rerun here.
- FeynKit/gammaloop's evaluator tests export instructions/helpers and use
  `map_to_ring(&Q)`; Idenso test support uses ring evaluation. No existing full
  symbolic conditional reconstruction API was found in these inspected paths.
  This establishes the three checks before any limited validation decoder is
  extended; all actual expression algebra still belongs to Symbolica.

The next deliverable after ROOT's scheduling grant is only this bounded private
census/proof candidate. No production switch, wider optimizer policy, alternate
Horner mode or new algebra layer is proposed.

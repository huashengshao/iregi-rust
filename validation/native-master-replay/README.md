# Actual core master-request capture and native replay

This private experiment addresses scalar-master cost in the eight existing massive N2/N3 rank0/1 benchmark families at outer batches1/32. It is separate from the rejected shared, dense-span and allocated native kernels. Production is unchanged.

The current committed core is pinned at `21622ec`; the reviewed but uncommitted collector change in `stability.rs` is excluded. Scalar-master sources match the frozen optimized `6b24c03` default dependency closure exactly. A private observational hook records the inputs and results of each original public master call, without changing arithmetic, branch order or reduction decisions. Source and archive hashes are preserved; no native feature or D0 code is compiled.

All eight complete tensor/Laurent outputs agree with original IREGI at the existing dimensionally normalized1e-10 tolerance. Every captured master row is finite and publicly valid, components=1, with no fallback or analytic-profile recursion. Inputs retain exact represented rational values, precision and signed-zero signs; the final scale argument is already `mu²`. Request coordinates and original sample mapping are retained. Actual group order is:

| Outer family | Ordered master groups for width b |
|---|---|
| N2 rank0 | B0(b) |
| N2 rank1 | B0(b), A0(2b) |
| N3 rank0 | C0(b) |
| N3 rank1 | C0(b), B0(3b) |

This gives297 master rows across twelve groups and1,584 final complex Laurent outputs. The captured data, reference arrays and source/build provenance are in `capture-results.json`, `capture-qualification.json`, and the source archive. Capture itself is untimed. The reference protocol executes one evaluation only for correctness; its returned kernel timing is discarded.

The initial preparation guard rejected a pre-existing working-tree difference before any compilation. The successful retry uses a committed Git snapshot and records the excluded difference. This was not a compiler or numerical failure. Both successful private compile stages and their costs are retained separately.

Replay preparation imports only unchanged generated A0/B0/C0 and exact constant tables. It must use the actual captured group order and sizes, and compare all six raw outputs before any timing. Public scalar output provides the first five; ordinary output six is the identically-zero derivative-domain field. Raw replay excludes adapter validation/result allocation and cannot establish whole-reduction or IREGI performance parity. The selected replay build was released after shared disk capacity became available. Its initial missing-trait-import failure is retained separately from numerical failures; the corrected compile completed in423.07s. All eight replay bundles passed the untimed qualification in1.77s. The single predeclared replay timing cohort has now completed; no repeat was selected from its confidence intervals.

The frozen protocol uses ten warm-up invocations per backend, two2ms pilots, one shared integer iteration count, and twenty-one fixed-loop paired30ms blocks. The pair order is a balanced shuffle with seed173. Own-backend outputs must remain bitwise identical after every pair and across separate qualification/timing processes. Preparation, validation and public result allocation are excluded from kernel timing. The strict parser admits all eight cases and all blocks;31 malformed controls are rejected. Three analyzer controls verify truncated JSONL or changed capture/parser provenance remains visible as eight unqualified rows. Synthetic test timings are explicitly separated from measurements.

Run commands from `/shared/external/iregi/iregi-rust`, sourcing `scripts/env.sh` and the private license environment for numerical execution. `prepare.py` pins a committed core and the dependency closure; `build_capture.py` builds only the private core/capture driver; `run_capture.py` executes the eight cases and validates every final Laurent component against the reference. Preserve existing attempts before rerunning. Never copy or publish a license value.

The completed quiet cohort on CPU254 is bound by `quiet-window.json` and `quiet-completion.json`. All eight actual master bundles improve under the declared paired99% bootstrap and<=2% interval-width gate. Native/Symbolica median ratios for singleton/batch32 are N2r0:0.143351/0.702008; N2r1:0.267635/0.737225; N3r0:0.174592/0.808725; N3r1:0.236815/0.783823. Every one of168 pairs favors native; both order strata agree. The full intervals, raw blocks, absolute kernel times, all represented output arrays and provenance checks remain available. External host activity was uncontrolled. These are raw master-kernel results, not IREGI or whole-reduction comparisons.

`capture-qualification.json` is the immutable earlier capture-only checkpoint, whose replay-unrun status describes that historical stage. The current complete status is `replay-qualification.json`; `decision.json` records the scope and limits of the diagnostic recommendation. Prior rejected allocator/dense/shared-kernel candidates are separate experiments and remain rejected.

The original pre-timing readiness qualification and manifest from commit `bdb55c9516e2c8f5700dcfb3d2c48fa87e6697a0` are preserved byte-for-byte under `initial-qualification/`. Its preservation receipt resolves all50 original manifest entries: the three files changed after readiness are retained locally and the other47 still use identical shared bytes. Run `python validation/native-master-replay/initial-qualification/verify.py` to verify the original4553f2 readiness statement, the separate current445350 postrun statement, and the untouched quiet window/completion/earlierc904 audit. No checkout or mutable readiness lookup is required.

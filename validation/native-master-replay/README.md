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

Replay preparation imports only unchanged generated A0/B0/C0 and exact constant tables. It must use the actual captured group order and sizes, and compare all six raw outputs before any timing. Public scalar output provides the first five; ordinary output six is the identically-zero derivative-domain field. Raw replay excludes adapter validation/result allocation and cannot establish whole-reduction or IREGI performance parity. The selected replay build was released after shared disk capacity became available. Its initial missing-trait-import failure is retained separately from numerical failures; the corrected compile completed in423.07s. All eight replay bundles passed the untimed qualification in1.77s. No replay timing has been run.

The frozen protocol uses ten warm-up invocations per backend, two2ms pilots, one shared integer iteration count, and twenty-one fixed-loop paired30ms blocks. The pair order is a balanced shuffle with seed173. Own-backend outputs must remain bitwise identical after every pair and across separate qualification/timing processes. Preparation, validation and public result allocation are excluded from kernel timing. The strict parser admits all eight cases and all blocks;31 malformed controls are rejected. Three analyzer controls verify truncated JSONL or changed capture/parser provenance remains visible as eight unqualified rows. Synthetic test timings are explicitly separated from measurements.

Run commands from `/shared/external/iregi/iregi-rust`, sourcing `scripts/env.sh` and the private license environment for numerical execution. `prepare.py` pins a committed core and the dependency closure; `build_capture.py` builds only the private core/capture driver; `run_capture.py` executes the eight cases and validates every final Laurent component against the reference. Preserve existing attempts before rerunning. Never copy or publish a license value.

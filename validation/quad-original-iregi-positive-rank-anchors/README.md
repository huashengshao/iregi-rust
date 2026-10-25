# Original quadruple IBP positive-rank reference anchors

This companion preserves **reference generation only**: four original-IREGI IBP captures using the exact seven-line `6c780…` fixture at ranks 1, 2 and 7, plus its explicit shared first five lines at N5 rank 7. All four reported native stability and complete arrays: 20 + 60 + 1,320 + 1,320 = **2,720 complex Laurent slots**. No TIRust output was compared in this cohort.

The N7 UV/IR zero-pole identities pass for all **1,050 pole slots**, using exact `Fraction` residuals and the unchanged dimensionally normalized `1e-10` threshold. This does not mean every represented pole is exactly zero. N7 ranks 1/2 have exactly zero 15/45 pole slots. N7 rank 7 retains 315 tiny nonzero UV slots and 675 exactly zero poles; its maximum normalized pole residual is approximately `6.39390e-26`. The raw coefficients are never snapped or projected.

N5 rank-seven UV coefficients are retained without imposing a zero-UV identity: 305 UV slots are nonzero. Its maximum **raw UV magnitude** is approximately `1.07948798137`; the saved maximum **dimensionally normalized pole norm** is approximately `0.771062843835`. These are different quantities. Native stability and successful N7 pole identities do not independently certify the finite coefficients, achieved 33-digit accuracy, or convergence of these new reference arrays.

The exact fixture has seventh shift `[1/4,0,1,1]`. It differs from the older conditioned N7 routing `[0,0,1,1]`. Its original rank-zero metadata remains unchanged; the new ranks are explicitly named by this cohort's own requests. N5 uses the first five common conditioned lines. Ordered shifts, squared masses, unit powers, unshifted dimension, scale 3, no on-shell snapping, original IBP mode and native Laurent/component ordering are preserved.

The capsule inherits the immutable canonical 22-file original-IREGI/OneLOop source, precision canaries, full complex matrix implementation, upstream COPYING text, failed earlier builds and independently adjudicated N6 point from `validation/quad-original-iregi-rank7-adjudication` (manifest `7c27b1…`). The previous N6 binary64 failure and unsuccessful quadruple PV/hybrid outputs stay visible in that parent. This companion does not duplicate source or compiled products. It stores the four request texts, preparation/protocol/runner/validator sources, source review and exact root grant, stdout/stderr/worker logs, all captured arrays, exact pole records, diagnostics, release receipt, independent checker and audit, and final reference-only qualification. Historical source-only status strings in the original proposal remain unmodified.

Run the Python-standard-library-only replay with both capsules and their listed parent files present:

```sh
python validation/quad-original-iregi-positive-rank-anchors/check.py
python validation/quad-original-iregi-positive-rank-anchors/check.py --reconstruct target/quad-reference-anchors-restored-new
```

The destination must not exist. The checker imports only the hash-pinned independent parent checker, replays its source restoration and saved N6 proof, validates available source/data guards and exact ordered requests, and independently reads all 2,720 complex outputs and recomputes every exact N7 pole gate. It preserves raw strings/signs/nonzero UV components and reproduces the independent summaries. It does not import a producer comparator or execute the preserved independent audit's native hash/PID checks. Original native hashes and process absence are historical attestations, not fresh portable guards.

The four captures used CPU 26 with child caps 10/15/45/45 seconds inside an aggregate 180-second budget and a 20-second cleanup reserve. Recorded elapsed time is diagnostic, not a kernel benchmark. The copied native binary and Python caches are excluded; the literal Symbolica license value is excluded while the upstream source COPYING text remains inherited from the parent.

No current-main/Cargo, TIRust, full N≤7/rank≤7 domain, dotted/dimension-shifted, complex-mass numerical, public interface, physical graph, Dual, finite parameter oracle, precision convergence or performance qualification follows. The capsule checker performs no new compilation, integral evaluation, native-product hashing, or process probing.

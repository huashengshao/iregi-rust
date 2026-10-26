# N6 rank-six D2: Float128 pass and Float256 stability failure

This capsule preserves a **partial qualification**, with both outcomes visible.
For the fixed real EC27 N6/rank-six unit-power h=-1 request, Float128 passed all
840 native complex Laurent comparisons against the scoped original IREGI quad
array at dimensionally normalized 1e-10. Float256 failed the E6 quadrature
stability guard and returned no moments. Its 840 reference comparisons and
the 840 precision-pair comparisons are **unrun**, with no maximum error.

The failed terminal is terminal 1, leaf 30: order 128, 1,240 box rows,
reported error estimate 2.499e-4. The other three child terminals converged.
The actual counters retain three completed child rows, 3,040 total box rows,
and no parent reduction. No retry, successful coefficient, pair agreement or
zero-valued replacement is inferred from this failure.

The immutable source epoch is **CLI003, 158 selected source bodies, before the
later G_h repair**, with binary identity
`0b28ce2428f7719da1acf9eee9584365d2a6bf62f83ee63db950d30b2b0bc58d`.
The source bodies and build/test history are inherited once from the adjacent
`validation/checked-g-generalized-core-tests`, manifest
`ee4bc172dd8b87e3242158afacab425e6b13376f72dd3fbb6678feb701a97417`.
This is historical evidence; it does not establish equality with current main
or qualify later production changes. Native executables are omitted with
their exact hashes. No duplicate source archive is stored here.

The own content-addressed payload retains both controllers, protocols,
source reviews and releases, the prior-pin-hardening finding, frozen controller
snapshots, raw results, receipts, logs and every resource observation:
70 samples for Float128 and 78 for Float256. The unexecuted passing-pair
packaging draft is retained only as source history. The finalized independent
failure audit preserves the failed reason, absent owned processes, unchanged
329 guarded inputs, and both sets of 840 unrun comparisons.

From a checkout containing this folder and its adjacent parent, run:

```
python3 -I -S -B validation/public-n6-rank6-d2-partial-evidence/check.py
```

The checker restores saved bytes and independently recomputes the Float128
840 comparisons using standard-library Fractions. It validates exact inputs,
tensor ordering, normalization `9^(degree-10)` for squared errors, native
UV/IR zeros, the failed Float256 lane without moments, actual counters,
diagnostics, historical postguards, and the separately pinned independent
failure audit. `--reconstruct FRESH_PATH` writes restored byte aliases.
Replay invokes no producer, compiler, integral or numerical dependency, and
performs no current PID probe or omitted-executable rehash. Saved input maps
attest the historical runtime context, not a complete hermetic dependency
closure. Resource samples are diagnostics, not benchmark measurements.

Original quad agreement is empirical and does not independently certify every
finite coefficient or establish achieved 128-bit accuracy. Float256 and the
precision pair remain unqualified. D6 remains HOLD. This capsule establishes
no broad generalized-domain, Dual, physical-graph or performance claim.

# Ordinary core evaluator stack allocation experiment

The candidate adds one `Symbolica::ExpressionEvaluator::optimize_stack()` call
to each fresh ordinary SSA factory in `execution.rs` and `contraction.rs`.
`ordinary-root-allocation.patch` is the complete proposed production change.
It was applied to production after the paired qualification and quiet diagnostic.
The uninstrumented current-source checks in `adoption/` passed 67 tests. The
separately retained optimized 80949db benchmark binaries exclude this change.

The proof builds start from commit
`80949dbc4711947971a702643f75d639ef217e82` and use identical retained dependency
archives. Their only behavioral difference is whether the two ordinary factory
hooks allocate temporary slots. Dualized arithmetic is unchanged. Primal-only
monitors prepared inside Dual workspaces are ordinary graphs and are affected.
The independent source review found no semantic defect in these insertion
points. `preparation.json` and the compile manifests identify the exact source,
compiler commands, dependencies and binaries; the core proof builds use opt2.

Both variants passed all 30 execution tests and all 8 contraction tests: 76 tests
in total, with no failures or ignored tests. A separate 12-case paired corpus
covers f64, DoubleFloat and Float128, ordinary and second-order Dual values,
regular/lightlike/complex-mass inputs, catastrophic-cancellation neighbors and
invalid scales. All successful coefficients and contractions agree exactly in
represented rational value, precision and signed zero. Result metadata, basis,
statuses, diagnostics, routing flags and repeated calls also agree. Every corpus
case requires a successful physical lane and the expected invalid-scale lane;
identical failure alone cannot qualify a case.

Every observed ordinary graph is exported before and after the candidate call.
The probe asserts identical instruction dataflow, arithmetic order, branch
labels, exact constants and constant registrations, output bindings, and shared
helper graphs. It reads all operands before assigning a destination, including
slots reused by that same instruction. Each process has its own proof directory.
There are 760 graph observations across the tests and capture, including 380
candidate observations; 252 candidate graphs use fewer temporaries. One large
execution graph shrinks from 333,585 temporary slots to 156. These are structural
storage counts, not measured speedups. Deduplicated instruction provenance is
stored in `semantics.tar.gz`; `semantics-sha256.json` maps each observed graph to
its content-addressed entry. Preparation-time and peak-memory claims are invalid
for these instrumented proof binaries.

The optional warm diagnostic in `warm/` made 92 further exact full-output
comparisons around 21 alternating timing blocks per family, on CPU 18. The
candidate/baseline median ratios and bootstrap 99% intervals were:

| Rank-one massive family | Batch | Ratio | 99% interval |
|---|---:|---:|---:|
| Bubble | 1 | 1.010 | 0.993–1.022 |
| Bubble | 32 | 0.972 | 0.953–0.980 |
| Triangle | 1 | 1.031 | 0.998–1.041 |
| Triangle | 32 | 1.005 | 0.975–1.027 |

Other work was active and the raw samples show load variation. This diagnostic
uses matched opt2 experimental libraries with preparation excluded, rather than
the optimized whole-workspace benchmark configuration. Only the bubble batch-32
case shows a modest local gain; the other intervals include parity. These data
establish neither a performance gate nor a broad speedup. The earlier diagnostic alone was inconclusive for singleton behavior.

A fresh rerun in `warm-quiet/` used the same binaries and inputs, with all other
project computations held. It made 92 exact full-output comparisons around 21
alternating 30 ms blocks per family on CPU 18:

| Rank-one massive family | Batch | Ratio | 99% interval |
|---|---:|---:|---:|
| Bubble | 1 | 1.0007 | 0.9883–1.0082 |
| Bubble | 32 | 0.9873 | 0.9802–0.9996 |
| Triangle | 1 | 0.9886 | 0.9767–1.0114 |
| Triangle | 32 | 0.9802 | 0.9701–0.9930 |

Both singleton intervals include parity, while both batch-32 cases show modest
local gains. Raw samples still contain outliers: workload elsewhere on the host
was not controlled. These are opt2 warm-core diagnostics, not an opt3 workspace
acceptance gate or an IREGI comparison. Production adoption followed these diagnostics and passed the focused checks
recorded in `adoption/qualification.json`; a fresh opt3 performance gate remains
separate. `warm-quiet/qualification.json` records the raw-data and artifact hashes; the
previous concurrent-load run is retained unchanged.

The local retained qualification can be replayed from the repository root:

```sh
source scripts/env.sh
python3 -B target/core-stack-reuse/run.py baseline execution::tests:: 180
python3 -B target/core-stack-reuse/run.py candidate execution::tests:: 180
python3 -B target/core-stack-reuse/run.py baseline contraction::tests:: 180
python3 -B target/core-stack-reuse/run.py candidate contraction::tests:: 180
python3 -B target/core-stack-reuse/run.py capture corpus 180
```

The target directory retains the exact source snapshots and matched binaries.
For reconstruction, apply the baseline/candidate instrumentation patches to
separate copies of the stated commit, retain the dependency archives identified
in `preparation.json`, and use the recorded direct-rustc commands. A rebuild with
different dependency bytes is a new qualification, even if filenames match.
The committed scripts and raw logs explain the protocol; runtime work must
respect the available Symbolica license and the shared benchmark schedule.

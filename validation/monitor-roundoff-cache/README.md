# Isolated local monitor estimate-cache experiment

This experiment is not enabled in production. It reuses successful numerical
`OperandRoundoff::complex` estimates for repeated local-monitor expression
indices within one lane. It does not change Symbolica expressions, accuracy
budgets, norm formulas, error messages, branch selection, accumulation order,
or the precision of inputs and outputs.

The baseline core sources match commit `80949db`. `source-manifest.json` retains
both source snapshots; `prepare.py` reconstructs them from that commit without
modifying the working tree. Both archives use the same compiler flags and
frozen Symbolica/master dependencies. `review.json` records independent review;
build success is not a numerical or performance qualification.

The cache owns one numerical slot per repeated expression and Taylor component,
with generation stamps invalidated for every inspected lane. Single-use terms
call the original estimator. Plans without repeated terms use the original
uncached checker. The primal and output monitors have separate namespaces and
are unchanged. The first candidate deliberately caches estimates only, not
intermediate magnitudes.

Observed local reuse is modest: the N4 rank-2 diagnostic has 4,072 term uses and
3,710 unique indices; the N5 rank-2 diagnostic has 19,853 uses and 18,227 unique
indices. These counts justify measuring the candidate; they do not establish a
speedup. The earlier f64 box guard rejection is retained by this experiment.

From the repository root, after sourcing `scripts/env.sh`:

```sh
python3 validation/monitor-roundoff-cache/prepare.py
python3 validation/monitor-roundoff-cache/build.py
python3 validation/monitor-roundoff-cache/prepare_probes.py
python3 validation/monitor-roundoff-cache/build_probes.py
python3 validation/monitor-roundoff-cache/build_tests.py
```

Preparation scripts refuse to overwrite source snapshots. Compiler jobs use
CPUs 10 and 11. Unit tests add eight candidate-only regressions covering mixed
precision, subnormals, errors, generation changes/wrap, Taylor indexing, and
first-diagnostic order. `protocol` compares the same 120 sequential public
Workspace snapshots between independent core archives, including every
successful coefficient as an exact rational, precision metadata, signed zeros,
lane statuses, result metadata and execution counts. It uses the committed
concurrency corpus only sequentially: actual concurrent execution remains
outside this paired protocol; a separate licensed two-thread control is now qualified in validation/concurrent-workspaces/.

Run numerical checks serially under the root agent's runtime lease:

```sh
target/monitor-roundoff-cache/baseline-unit stability::tests --test-threads=1
target/monitor-roundoff-cache/candidate-unit stability::tests --test-threads=1
target/monitor-roundoff-cache/protocol
```

Only after correctness qualification, run `performance` under a quiet CPU-0
lease. It checks all output bit patterns before and after paired timings, uses
21 alternating paired blocks for each workload, and includes singleton and
32-lane batches. Preparation and calibration are excluded. The analysis must
report each workload separately with paired 99% bootstrap intervals. This
isolated experiment does not replace the optimized IREGI comparison pipeline.

`paused-handoff.json` records the earlier user-requested pause; subsequent build
records supersede its interrupted-build status. The separate
`validation/mixed-precision/guard_probe.rs` experiment measures the earlier
accuracy-guard change and is not this cache experiment.

Current numerical qualification: 29 baseline stability tests, 37 candidate
tests (the same 29 plus eight cache regressions), and all 120 public sequential
snapshots pass. The initial `stability::tests` filter ran 19/27 local tests; a
second run covered five argument and five quadrature tests per variant. See
`qualification-all.json` and `qualification-remaining.json` for exact run
scopes and binary/log hashes. Performance was measured in a centrally granted quiet window on CPU0. The
cache is rejected for production: no qualified improvement, two regressions,
and ten inconclusive-noise rows under the 99% interval/2% width gate. See
`decision.json` for every workload, source/binary/log provenance and the separate
earlier accuracy-guard cost experiment. Production remains unchanged.

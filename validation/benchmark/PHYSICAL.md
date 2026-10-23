# Physical-pipeline benchmark

The `iregi-cli` example `physical_benchmark` calls the production Rust APIs in
one persistent process. It shares exact input parsing and compiled polynomial
coefficient evaluation with the CLI through `iregi_cli::input` and
`iregi_cli::numerator`. FeynKit/Spenso/Idenso prepare the graph and Symbolica owns
all polynomial operations. The reduction crate remains independent of this
preparation layer.

The four inputs are the independently checked ggH triangle, ggHH box, massless
up-quark box and ggHHH pentagon in `validation/physical`. Each published fixture
contains one phase-space point. Batch widths above one repeat that exact point
in separate lanes; they measure repeated-point throughput, not independent
phase-space sampling. Input momentum, mass, parameter and wavefunction strings
are parsed directly at the requested precision.

Build and run from the project root, after obtaining the shared runtime and
quiet CPU slot:

```sh
source scripts/env.sh
python3 validation/benchmark/build_physical.py
python3 validation/benchmark/physical_run.py
```

The builder accepts `--revision COMMIT` for a retained committed snapshot and
`--native-batch` for the optional generated Rust scalar backend. It uses the
same optimized build policy as the tensor benchmark. The default benchmark
requests binary64, singleton latency and batch-32 throughput. Higher precision
must be reported separately:

```sh
python3 validation/benchmark/physical_run.py --precision float --bits 128 256 \
  --accuracy-bits 53 --batches 1 32
```

`--precision dd` selects Symbolica DoubleFloat. `--accuracy-bits` controls the
existing core tolerance independently of working precision. The adapter uses
ordinary workspaces and does not silently rescue failed precision cases.
Failures at binary64 remain rows even when a later high-precision run succeeds.
Use `--inputs-only` to inspect the complete requests without executing Rust or
Fortran. `--timeout` bounds each adapter request, including preparation.

## Stage definitions

| Stage | Timed work |
| --- | --- |
| `graph_preparation` | Model/DOT parsing, Feynman rules, external wavefunctions, component projection, exact polynomial extraction and object disposal |
| `evaluator_preparation` | Prepared-graph clone, parameter parsing/packing, exact coefficient evaluator, precision mapping, reduction and contraction plans/workspaces and disposal |
| `numerator` | Batched numerical parameter-to-polynomial-coefficient evaluation, finite-value inspection and returned-buffer disposal |
| `reduction` | Full `Workspace::reduce_batch`, including scalar masters, statuses, result allocation and disposal |
| `contraction` | Prepared coefficient/moment contraction, statuses and returned-result disposal |
| `numerical_end_to_end` | One complete uninstrumented coefficient evaluation, reduction and contraction call |
| `reprepared_end_to_end` | Fresh graph preparation, evaluator/workspace preparation and one complete numerical pipeline, including disposal |

The default repeated stages are numerator, reduction, contraction and numerical
end-to-end. `--stages` selects any combination from the table. Preparation is
also recorded on every configuration as separate **first-observed** durations,
including a directly measured first end-to-end interval. Symbolica and core
structural caches may already be warm in this persistent process. Neither
first-observed nor repeated fresh-object measurements are called cold-process
latencies. No file I/O, JSON transport or output serialization is timed.

Coefficient, master and reduction values are recomputed on every numerical
iteration. Symbolic plans, compiled evaluators and scratch capacity are reused.
The isolated contraction stage uses immutable coefficients and tensor moments
prepared before its timer. The measured numerical end-to-end stage recomputes
them; its duration is not a sum of isolated component medians.

Profiling runs separately after the ordinary timings and uses the core's
existing argument, master, recurrence and total counters. These instrumented
components never replace uninstrumented reduction or end-to-end timings.

## Correctness and uncertainty

Before warmup or calibrated timing, every tensor component and all four Laurent
slots are checked against original IREGI at the canonical FeynKit routing. The
contracted finite, single and double poles are checked against graph-isolated
MadLoop with the established color/fermion factors. R2 and UV counterterms are
excluded; bare poles and R1 remain. Every subsequent measurement block returns
complete untimed output for the same checks. Every warmup and timed numerical
invocation inspects statuses; failures retain completed durations and explicit
diagnostics.

All three original IREGI modes stay visible. For ggHHH, the separately audited
canonical original-IBP rank-four defect remains a mismatch; PV/hybrid plus
MadLoop are the required independent checks. This exception is identified in
each correctness record and never changes the `1e-10` numerical tolerance.
For the other graphs, all three original modes must agree. A correctness failure
prevents that row from receiving qualified timing results.

The runner uses the existing CPU-affinity/environment collector, per-stage
calibration, raw nanoseconds per complete batch, 21 repeated blocks, and a
deterministic 10,000-resample 99% bootstrap interval. Stage order is randomized
with a recorded seed. An interval wider than 2% of its median is labeled
`inconclusive-noise`. CPU frequency settings are recorded but not changed.

The physical runner does not yet time a matching MadLoop or original-IREGI
physical pipeline. Reference results establish correctness only. These data
cannot establish physical performance parity; reference timing and ratios remain
absent. The separate tensor-kernel benchmark supplies its own matched reference
timings.

The existing MadLoop timer requires additional workload alignment before a
physical timing ratio can be formed. Its generated ggH tensor rank is three,
while the prepared polynomial has degree two; ggHHH allocates rank five while
the prepared polynomial has degree four. Matched tensor timings must request
the same rank and complete moment array. MadLoop also uses the mapped variable
`x=p1-q` and legacy snapping at `1e-6`, whereas these canonical Rust inputs
preserve their shifts. Both engines must receive the same routing, snapping
policy, scale and coefficient arrays for a matched reduction comparison.
MadLoop's `numerator_assembly` corresponds to numerical coefficient preparation;
its `numerator` is a separate polynomial probe. Its `reduction` includes ordering
conversion, contraction and cache cleanup, so it cannot be compared directly
with the isolated Rust reduction stage or with a sum of stage medians.
The generated MadLoop timer exports the actual `CTMODE` and `IREGIMODE`
arguments before timing. Both the Fortran timer and the Python reader require
`CTMODE=1` (unchanged propagator direction) and `IREGIMODE=2` (hybrid); an absent,
duplicate or unexpected record fails the run. Parser tests and generated-source
compilation are recorded in `madloop-mode-qualification/`; they do not qualify
numerical timing results.

Each row retains precision, accuracy target, actual scalar backend, full initial
output, references, raw response log, execution counters and stage samples.
The artifact records binary/build identity, source and asset hashes, CPU details,
thread settings and source changes during measurement. Missing manifests,
changing sources or mismatched hashes make provenance unqualified. Failed,
unsupported, timed-out and interrupted rows remain in the output; there is no
aggregate score that benefits from excluding them.

Python boundary qualification is recorded in `harness-qualification/`. It checks
large-input pipe backpressure within the request timeout, persistent responses,
interrupted configuration accounting and strict three-slot MadLoop references.
Those tests do not execute Rust, Fortran or Symbolica and do not qualify physical
timings. The subsequent bounded ggH smoke in `physical-smoke/` completed
singleton and batch-three inputs, all seven stages and a separate profiling
pass. Every tensor and graph comparison passed. Its identified debug executable,
short intervals and changing live source snapshot remain explicitly unqualified
for performance; these results cannot establish performance parity.

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

The Rust-only `physical_run.py` runner does not time a matching MadLoop or
original-IREGI physical pipeline. Reference results establish correctness only. These data
cannot establish physical performance parity; reference timing and ratios remain
absent. The separate tensor-kernel benchmark supplies its own matched reference
timings.

The historical MadLoop timer measurements require workload alignment before a
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

## Equivalent physical numerical pipelines

`physical_alignment.py` establishes a separate full-graph comparison contract
for the four qualified oriented graphs. It compares the Rust
`numerical_end_to_end` workload with MadLoop's `total`: numerical coefficient
construction, reduction, native result conversion where needed, contraction,
status checks, and numerical-cache/result cleanup. Both exclude graph and
wavefunction preparation, parameter parsing, file I/O, and process transport.

This is an equivalent full-graph workload. Each engine keeps its established
loop routing and algorithmic tensor rank: Rust/MadLoop request ranks 2/3 for
ggH, 4/4 for ggHH and the up-quark box, and 4/5 for ggHHH. Those differences
must remain in every result. The existing three-probe numerator qualification
establishes the relation `x=p1-q`; the helper checks its graph/model/input and
fixture hashes without introducing a polynomial transformation. A matched
tensor-stage comparison would additionally require identical routing, rank,
coefficient arrays and requested moment outputs, and is a separate benchmark.

The shared pipeline contract uses binary64, Hybrid reduction, the exact
captured evaluated external point, identical model parameters and HELAS
wavefunctions, helicity 1, and fixed adjoint-color components zero. It preserves
input kinematics in both engines. Repeated-point batches remain declared as
such. Structural evaluators and scratch capacity may persist, but numerical
coefficients and integrals are recomputed each invocation; the original
IREGI numerical cache is cleared after each sample within its timer.

The code-native outputs are converted outside both timers to the common
three-slot graph result `[finite, UV+IR single pole, IR double pole]`. Rust's
four slots are combined as `[finite,uv+ir,ir2]`; its prepared numerator already
contains the graph/color/fermion factors. MadLoop's stripped three slots receive
the previously established factor `-1/2` for the top loops or `-1/8` for the
up-quark box. Optional division by `16*pi^2` is also outside both timers.
These comparison adapters do not enter either stage measurement.

Run the reference alignment from the project root, choosing permitted CPUs:

```sh
source scripts/env.sh
python3 validation/benchmark/physical_alignment.py --capture \
  --cpu 16 --build-cpus 16,17 --batches 1 32
```

The MadLoop timer defaults to its unchanged legacy snapping policy. Its explicit
`--input-policy preserve` option disables `ONSHELL_IREGI` after both ordinary
and replay initialization, checks the effective `CHECK`/`ONSHELL_IREGI`/threshold
state before every timed step, and exports observed policy records. It checks
replayed coefficients, every tensor slot and final poles against the ordinary
preserved-input path before timing. The earlier legacy fixture supplies an
exact identity check for evaluated momenta, model values, wavefunctions and
routing, plus coefficient/probe agreement; its tensor results are retained
only as a different-policy diagnostic.

The helper retains failed cases and emits preserved selected-graph fixtures
for subsequent Rust checks. It computes no timing ratio and does not qualify
performance. Rust binary64 failures remain failures; higher-precision runs
must be reported separately. The Rust-only `physical_run.py` measurements and
these reference measurements still require joint correctness, provenance,
quiet-CPU and uncertainty qualification before a full-pipeline ratio is valid.

## Joint full-graph runner

`physical_joint.py` orchestrates the Rust numerical pipeline and the preserved
MadLoop pipeline for each graph. Without `--execute` it writes a planned ledger
and starts no numerical process. Use a fresh output directory for every attempt:

```sh
python3 validation/benchmark/physical_joint.py --execute \
  --rust target/optimized/release/examples/physical_benchmark \
  --build-manifest target/benchmark/physical/physical-rust-build.json \
  --cpu 0 --batches 1 32 --repeats 21 --warmup 5 --block-ms 30 \
  --quiet-window-note "Coordinated runtime slot; competing project builds paused" \
  --output target/benchmark/physical-joint/attempt-01/results.json
```

The note records the coordinated quiet-window context; it does not prove that
the host was free of interference. Missing quiet context, fewer than 21 blocks,
fewer than 3 warmups or blocks targeted below 30 ms remain diagnostic. The runner
retains a row for every requested graph/batch, even when preparation, reference
execution, correctness, or provenance fails. A timeout kills only the process
group launched for that phase. Completed raw responses and phase logs survive
interruption, and a new attempt cannot overwrite them.

Before comparing timings, the runner joins every Rust prepare, calibration,
timed and profiling response to its requested batch and rechecks full canonical
tensor arrays plus all three preserved graph coefficients. It parses the
MadLoop trace again, checks effective policy and call modes, and requires its
raw block sequence to match the published stage samples. Both executable
identities, raw logs, producer sources, generated reference inputs, cards and
linked archives are retained or hashed. The original canonical-IBP pentagon
exception remains explicitly visible under the established PV/hybrid gate.

Immutable Rust build sources and their build-time assets must match the build
manifest. Numerical model, graph, point, fixture and audit data must also match
the live inputs. Python validation producers can evolve independently of that
compiled snapshot; their live hashes are recorded and must remain unchanged
throughout the run. This distinction permits updated reference capture without
rewriting an older build manifest or treating changed numerical inputs as the
same benchmark.

The two timer processes run sequentially per graph. Their samples are independent,
so the estimator is `median(Rust numerical_end_to_end) / median(MadLoop total)`.
Each of 10,000 bootstrap resamples draws independently from both sample arrays;
block indices are never paired. The per-family 99% interval and each pipeline's
own median interval must have relative width at most 2%. A narrow ratio interval
below 1 is an improvement, one containing 1 is operational parity, and one above 1
is a regression. Wider intervals are inconclusive. These are per-family
operational intervals, not simultaneous-family confidence or a formal statistical
equivalence test. Separate runs remain sensitive to drift between engines;
within-run bootstrap uncertainty does not measure that drift.

The runner preserves all component timings and the independent profiling pass,
but forms a ratio only from the two complete numerical pipeline stages. No
physical parity result is established merely by adding this runner or by the
earlier reference-only smoke captures.

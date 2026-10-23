# Reproducible kernel benchmarks

The benchmark uses the production Rust `Workspace::reduce_batch` API and a
separate original-IREGI Fortran timing executable. Both return every Cartesian
moment through the requested rank and its four native Laurent coefficients.
The default corpus covers bubble/triangle ranks 0–3 with massive, massless, and
complex masses. Each family has independent binary-exact perturbed samples.
All timing artifacts remain under `target/benchmark` until validated results
are copied into the committed report data.

From the repository root:

```sh
source scripts/env.sh
bash scripts/build-reference.sh                 # once, unless sources change
python3 validation/benchmark/build.py
python3 validation/benchmark/run.py
```

The build uses `--offline --locked --release`, the workspace's thin LTO and one
code-generation unit, and the independently audited `-O3` reference objects.
Compiler commands, versions, binary hashes, source hashes, reference revisions,
and local reference repair provenance are saved with the measurements. Build
while sources are stable: the build script rejects a changing source snapshot.
Use `python3 validation/benchmark/build.py --native-batch` to measure the
opt-in generated Rust scalar kernels. Each row identifies the actual compiled
backend. Preserve the manifest alongside measurements when comparing builds.
`provenance_qualified` requires both measured binaries to match their build
manifests and the Rust source snapshot to remain unchanged; a timing verdict
without this provenance is diagnostic only.
Use `--revision COMMIT` to build a retained Git snapshot below
`target/benchmark/sources/` while development continues. Commands still run
from the project root. Measurements identify that exact revision and snapshot;
they qualify that implementation, not subsequent working-tree edits. The
runner separately tracks measured-source and current-workspace changes.

A smaller qualification run, after obtaining the shared Symbolica runtime
slot, is:

```sh
python3 validation/benchmark/run.py --ranks 0 1 --mass-classes massive \
  --batches 1 32 --repeats 21 --block-ms 30 --output target/benchmark/smoke.json
```

`--cpu N` selects a permitted CPU. The default selects the lowest CPU in the
process affinity mask. The runner pins itself and both children to that CPU,
restores its original affinity afterward, and records CPU/frequency settings.
It does not alter governor or turbo settings. Other workloads on the same CPU
can still cause uncertainty; noisy families cannot pass the timing gate.

`--input cases.json` accepts custom topologies through seven propagators and
rank seven. `--inputs-only` writes the default input schema without launching
either engine. Use `--filter ID_SUBSTRING` to select families. All samples of a
Fortran batch currently share `mu`; every other input is supplied independently.
The current executable benchmarks binary64 ordinary unit-power tensor inputs.
Generalized inputs, higher precision, Dual, and graph preparation need separate
benchmark adapters and must not be described as measured by this executable.

## Timing contract

Numerical results are cold on every sample. Rust reuses its structural plan,
compiled evaluators, and scratch capacity; it recomputes every numerical master
and recurrence result. Original IREGI reuses initialization and uses recycling
within one sample, then frees its numerical recurrence caches after each sample.
The independent Fortran scalar backend may maintain its own constant tables.
The original IREGI API is scalar, so its batch timing is the sum of successive
scalar reductions on exactly the same input rows.

Rust kernel timing surrounds complete `reduce_batch` calls, result status checks,
and returned-result disposal. Fortran timing surrounds its tensor call, input
mass-reference setup, status/finiteness checks, and `IREGI_FREE_PS`. Both retain
all requested outputs. Parsing, transport, output serialization, initial setup,
and symbolic plan/workspace preparation are excluded from kernel timing.
Rust preparation is recorded separately as a single observed duration, not a
statistically qualified latency distribution.

The runner performs warmup, then calibrates each engine independently to target
30 ms per measurement block. It collects 21 paired blocks, randomizing which
engine goes first using a recorded seed. Both engines evaluate the same complete
input batch on every iteration; iterations per block may differ. Every paired
block is checked against the reference over all moments and Laurent slots.
The mixed absolute/relative `1e-10` tolerance is dimensionally normalized using
the documented per-input energy scale; it is not relaxed for difficult cases.

Profiling is a separate Rust pass. Production kernel timing has profiling
disabled. Its components are:

- `arguments`: Symbolica's argument evaluator only;
- `masters`: complete batched scalar-master calls;
- `reduction`: recurrence evaluation and stability inspection;
- `total`: the complete instrumented reduction call.

The difference between the instrumented total and these components is input
validation, packing, lane routing, result construction, and other overhead.
Child fallback/profile components are included once. Instrumented timings are
never substituted into the uninstrumented speed comparison. Numerator evaluation
is not applicable to this tensor-array kernel; graph/numerator end-to-end timing
is a separate benchmark family. Missing Fortran stage splits are `null`, never
estimated by subtracting unrelated measurements.

## Data and gates

`target/benchmark/results.json` contains rows keyed by `id`, `n`, `rank`,
`mass_class`, `precision`, `mode`, `reference_mode`, and `batch_width`.
Each engine's `total` has the raw `samples_ns` in **ns per complete batch**,
median, 99% percentile-bootstrap confidence interval, extrema, and relative
median absolute deviation. Divide by `1000 * batch_width` for microseconds per
point. `rust.profiled_components` has the corresponding independent instrumented
measurements; `rust.preparation_ns` is present only when a new structural plan was
compiled. `rust.execution` records active-lane and master-batch counts, providing
evidence that the new implementation propagates batches internally.

The paired Rust/IREGI latency ratios use a deterministic 10,000-resample
bootstrap. A timing verdict requires a 99% confidence interval no wider than
2% of its median. An interval wholly below one is `improvement`; a narrow
interval containing one is `parity`; a narrow interval wholly above one is
`regression`. Wider intervals are `inconclusive-noise`. These classifications
are per family and batch width. Failed correctness cannot pass performance.
This is an operational uncertainty gate, not a guarantee that machine noise is
independent or that every system-level systematic error has been eliminated.

Crashes, missing results (including an original Fortran `STOP` with exit code
zero), unstable lanes, unsupported input, and disagreement remain explicit rows.
There is no aggregate speed score that can improve by dropping these rows. The
runner saves after each family and retains partial results if interrupted. If
sources change during a run, the artifact identifies the data as stale for the
current tree; binary hashes still identify the measured implementation.

`results-inputs.json` stores every input. `rust.stderr.log` and
`reference.stderr.log` retain diagnostic output. `reference-build.json` and
`rust-build.json` record the build provenance. The report ingester must check
the source/binary identity and correctness before promoting measurements into
`docs/data/results.json` and rebuilding `docs/benchmark.pdf`.

## Protocols

The Rust example reads one JSON object per input line (fields are shown in
`run.py::rust_request`), writes `RESULT {json}`, and exits on `QUIT`.

The Fortran driver accepts:

```text
BENCH id mode n rank mu batch warmup repeats iterations
p0 p1 p2 p3 (mass_squared_real,mass_squared_imaginary)
... n rows per sample, batch samples ...
```

Modes are 0 = IBP, 1 = PV, 2 = hybrid. Input shifts are time-first, the metric is
`(+---)`, and the result has no multinomial weights. A single `RESULT` JSON line
contains raw batch durations and complete final tensor arrays. The transport
protocol is intentionally outside the timer. `driver.f90` is separate from the
proven correctness-oracle driver in `validation/reference`.

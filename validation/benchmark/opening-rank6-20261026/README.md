# Opening rank-six timing suite

This suite records representative **absolute** TIRust timings through six points
and rank six. It makes no speed-parity claim. The first table uses ordinary
unit-power, unshifted integrals; the second uses repeated propagators or an
independent dimension shift, outside COLLIER's ordinary tensor interface.

`make-inputs.py` generates `inputs.json` from the first sample of the committed
conditioned Cartesian fixture. Prefixes retain their original shifts, squared
masses and renormalization scale. All input strings are exactly representable
dyadic rationals. The Rust driver rejects rounding of this cohort's inputs.
Working precision is explicit for every row. It is not an achieved-precision
claim, and timings at different precisions are not directly comparable.

The executable is the example `crates/iregi-rust/examples/opening_timing.rs`.
The following is the capture workflow in a separate output copy; first preserve
the published observations as described below:

```sh
source scripts/env.sh
python3 validation/benchmark/opening-rank6-20261026/make-inputs.py
python3 validation/benchmark/opening-rank6-20261026/run.py build --cpu 18
python3 validation/benchmark/opening-rank6-20261026/run.py run --cpu 18
python3 validation/benchmark/opening-rank6-20261026/run.py summarize
```

Use the project toolchain environment and an authorized Symbolica license for
native execution. The root runner records the actual command, CPU, optimized
build, source/dependency hashes, resource supervision and exit status. No
license value belongs in the measurement artifacts. Execute one producer at a
time, after builds have finished; report failed and unmeasured rows explicitly.

Each call requests **all cumulative Cartesian moments through the stated rank**,
including all four native Laurent slots. This is more work than one monomial
integral or a precontracted numerator. Preparation, the first numerical call
(including lazy specialization), warmup, output validation and JSON I/O have
separate records and are excluded from the warm call measurements.

Profiling is explicitly enabled at construction, using the public facade and
the Symbolica master policy. Its actual engine is recorded. For eligible
high-point requests, this can select the existing AffinePower workspace instead
of the unprofiled thin SixPoint workspace. The table must not claim to measure
the latter or imply that this is the fastest available route.

Every timed call retains its outer wall duration and the existing profiler's
aggregate scalar-master duration. The latter includes master calls in nested
reduction children and hybrid retries; an E6 master includes its internal D0
evaluations. The displayed TIRust-exclusive duration is their difference. It
includes routing, invariant arguments, recurrence, error transport, diagnostics,
buffer packing and result construction. Arithmetic means taken over the same
calls give an additive split. Repeated blocks and all individual observations
remain available for uncertainty/spread inspection. Instrumentation overhead
remains present.

For N≤4 the protocol uses three warm-up calls followed by eleven equal-size
blocks, targeting 100 ms per block with at most 10,000 calls. The loop count is
chosen once from the last warm-up. N≥5 uses one warm-up and five single-call
blocks, fixed before measurement. Means are additive across the same calls;
displayed standard errors describe variation across blocks, without a claim
to control other users' host activity. Result destruction is outside the timer.

The runner refuses to overwrite existing attempts. A fresh checkout also
contains the published `cases/` observations. Before a new capture, use a
separate checkout and preserve/move `cases/`, `build.json` and `summary.json`
under its `target/` directory. The original committed observations remain in Git.
The committed `source-files.json` defines the portable selected source context;
neither it nor the receipt claims a hermetic build closure. Set the project
toolchain overrides and an authorized license before native execution. The
reported build uses Rust 1.99.0, release optimization, and one numerical thread.

The first and last full tensor arrays are retained as exact represented values.
Every warmup and timed result is checked, **outside its timed region**, for
successful lane statuses, complete finite arrays and exact equality to the
first result as represented numbers (not signed-zero bit patterns). Inputs
must remain unchanged. A failed call is retained, never
qualified as a successful zero or silently omitted. Repetition checks are not
an independent mathematical oracle; reference-validation evidence remains
separate.

Source inspection of the timing boundary is recorded in
`profiling-boundary-source-audit.json`. In particular, the affine parent's
`ImportedAffineQuadrature::evaluate` propagates previously computed uncertainty
using Symbolica evaluators; it does not evaluate additional scalar masters.
Its time therefore correctly belongs to the TIRust-exclusive region.

All 18 published arrays pass the independent saved-reference comparison in
`reference-comparison.json`: 8,968 complex coefficients, all four native
Laurent slots, with unchanged dimensionally normalized mixed tolerance `1e-10`.
The largest normalized difference is below `2.714e-13`. Original IREGI IBP
reference admission and rejected PV/Hybrid history remain explicit. This
comparison uses saved results, without executing reference integrals again.

Audit the published arrays without remeasuring:

```sh
python3 validation/benchmark/opening-rank6-20261026/compare-reference.py \
  --require-all --output target/opening-tensor-timings-20261026/reference-replay.json
```

This saved-evidence checker pins the published build, request and terminal
receipt bindings. A new timing campaign generates new receipts and requires
its own bindings and review; it must not overwrite or masquerade as this cohort.

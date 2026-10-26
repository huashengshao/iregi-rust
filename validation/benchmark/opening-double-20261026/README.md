# Optimistic binary64 opening-table timings

This new campaign retains the exact 18 tensor inputs from
`../opening-rank6-20261026/inputs.json`. All numerical inputs, recurrences,
masters and outputs use ordinary Rust `f64` with 53 significant bits. No
higher-precision fallback or promotion is requested. The three ordinary
high-point inputs N5R5, N5R6 and N6R6 set the public accuracy parameter to 39,
whose existing 19-bit safety margin gives target `2^-20`, approximately `1e-6`.
Other inputs retain parameter 53. These parameters do not certify accuracy.

Each row has a predeclared explicit Symbolica and NativeF64Abc master-policy
candidate. Ordinary N6R6 additionally tries the existing Symbolica thin Hybrid
and PV public routes, enabling profiling after workspace construction to
preserve their numerical dispatch. The native policy specializes supported
A/B/C masters and retains the existing supported backend for other families.
No mathematical strategy is patched. All candidate attempts are retained.

The opening table selects the fastest mean among complete finite arrays whose
measured array-relative discrepancy is at most `1e-3`. Accuracy is displayed
independently from timing; a missed old `1e-10` gate does not suppress a usable
three-digit result. If every attempt fails this boundary, diagnostic timing
remains visible with its failure. Public guarded failed lanes stay null: the
harness never accesses private buffers or presents zero tensors as results.

Reference arrays are the previously captured full TIRust outputs, independently
checked against admitted original IREGI arrays for all 18 inputs at `1e-10`.
The comparison measures dimensionless full-array relative discrepancy E/A:
E is the maximum absolute complex error after dividing by
`mu^(tensor_degree+4+2h-2sum(powers))`; A is the corresponding maximum reference
amplitude. This avoids exaggerating relative errors of zero/tiny components.
The previous per-component mixed normalized metric is also retained. This
saved finite-precision reference comparison is not an exact-integral oracle.

Preparation, first call, warmup, output comparisons, serialization and process
startup are excluded from warm timings. Every timed call includes the complete
public numerical reduction. Nested scalar-master durations come from that
same call, and TIRust-exclusive equals outer duration minus masters. Refused
calls may be timed diagnostically but cannot qualify a numerical result.

From the repository root, root supervises compilation and the quiet window:

```sh
source .local/tirust-current-toolchain-roots/env.sh
source scripts/env.sh
source .local/symbolica-license.env
ulimit -s 65536
export CARGO_TARGET_DIR="$PWD/target/optimized-build"
export CARGO_BUILD_BUILD_DIR="$PWD/target/optimized-build"
export CARGO_BUILD_JOBS=2
export RAYON_NUM_THREADS=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export RUST_MIN_STACK=67108864
python3 -I -S -B validation/benchmark/opening-double-20261026/make-inputs.py
python3 -I -S -B validation/benchmark/opening-double-20261026/run.py build --cpu 18
python3 -I -S -B validation/benchmark/opening-double-20261026/run.py run --cpu 18
python3 -I -S -B validation/benchmark/opening-double-20261026/run.py summarize
```

The runner freezes the feature-enabled release binary under `target/`, records
selected source hashes/toolchain/CPU, pins every numerical child, bounds each
process group, checks cleanup and refuses to overwrite prior attempts. To
resume an interrupted suite use `run --skip-existing`; an existing completed or
failed attempt is retained. A fresh rerun requires a new destination/suite ID.
The separate `collier/` subtree belongs to the independent COLLIER runner.

The initial38 candidates produce complete finite outputs for16 of18 inputs.
The two N4 rank-six dotted requests hit the retained cancellation guard at
request53. Four explicitly post-hoc PV trials under `supplemental/` reorder
whole denominator triples by `[1,0,2,3]`, preserving the integral and all
requested precisions. They also refuse. Their raw attempts are retained and
their fastest diagnostic durations are eligible for display, with *Refused
output · diagnostic timing* and *accuracy unavailable*. These are not successful
tensor results. The initial saved audit checks32,512 complex fields across68
successful arrays, plus eight null refusal payloads; the supplemental audit
separately checks its four refused attempts. No higher-precision result is
substituted in a binary64 timing cell.

After capture, retain `run.py summarize` as `tirust-summary.json`, run COLLIER's
saved-data checker/summarizer, then use `combine.py` for the report's joined
`summary.json` (including the audited supplement). The TIRust `independent_check.py` rechecks all request/result
hashes against supervision receipts, complete tensor metadata, exact rational
binary64 values, every raw call's additive/nonoverlapping timing stages, and
the selected mean independently. It accepts `--verify-live-source` and
`--verify-live-binary` for the current checkout; ordinary saved-data replay
does not require retained native executables. The COLLIER checker is likewise
artifact-only, using an independent Decimal100 norm computation. No reference
code is executed by either checker.

The two COLLIER pentagon rows are finite and no longer marked rejected. The
six-point/rank-six fixture still produces nonfinite coefficients for every
tested public configuration; its observed duration is a diagnostic, with the
finite-subset error and nonfinite count shown explicitly. Native warning flags
are archived separately from the achieved-error classification. "DD" means
Denner–Dittmaier reduction, still binary64.

`AUDIT-MANIFEST.md` documents the append-only report binding/sealing procedure.
Earlier captures and strict classifications remain historical evidence. These
selected optimistic means are absolute observations, with descriptive repeat
uncertainty; they do not establish a controlled-host speed-parity gate.

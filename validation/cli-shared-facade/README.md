# Shared tensor facade in the CLI

The CLI now constructs TensorReductionPlan/TensorWorkspace, so the library
selects generic, six-point or seven-point execution. Graph import and Symbolica
numerator preparation remain separate. Contraction uses the facade's contraction
plan. Default Hybrid, requested accuracy, precision rescue and existing master
policy are preserved. Output includes tagged nested execution counters and
per-lane diagnostics; unavailable rescue observations are explicitly null.

The locked/offline actual-Cargo build produced the CLI, its focused test binary
and the existing public tensor-array example in 1,010.83 seconds. A subsequent
one-assertion test-only correction rebuilt just the test product in 40.95 seconds.
All thirteen exact CLI tests passed in 21.82 seconds. Four low-point smoke calls
cover retained reference comparison, DOT numerator preparation/contraction,
DoubleFloat and precision rescue with an invalid neighboring lane. The six-point
rank-three smoke checks all 140 complex Laurent slots against a retained full
array. The seven-point scalar smoke checks all four slots, all 21 packed children,
105 scalar-master requests in one family batch and the failed neighbor.

The initial zero-command preflight alias failure, test-only diagnostic-wording
failure and resource-bound seven-point timeout remain in the evidence. The one
separately authorized seven-point retry passed in 235.14 seconds on a free CPU,
with the same executable, fixture and numerical gates. All terminal owned process
groups were cleaned and all captured input guards passed. These are bounded
correctness observations; none of these wall times are performance benchmarks.

Run python3 validation/cli-shared-facade/check.py from the project directory.
The checker restores exact saved bytes and replays the numerical comparisons with
stdlib rational arithmetic, without invoking Rust, Symbolica, Fortran or an
integral backend. This compact payload inherits the already sealed 77-file source
snapshot from ../public-rank7-ibp-n2-postfix and adds the corrected test source,
runners, raw JSON, logs and receipts. Compiled executables are omitted with their
exact hashes retained. The selected source/artifact context is not a complete
dependency or operating-system closure, and this frontend cohort does not extend
the library's mathematical qualification or public high-point Dual coverage.

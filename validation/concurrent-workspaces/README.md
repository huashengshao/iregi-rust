# Concurrent workspace and preparation qualification

The retained integration test first prepares and warms independent Workspaces
serially, then compares every successful Laurent/Taylor coefficient, retained
precision, signed zero, lane status, result metadata, fallback/analytic flag,
and execution count against sequential references. Its corpus covers A0/B0/C0/D0,
a rank-2 tensor triangle, a second-order Dual bubble, mixed Float input precision,
complex/physical branches, exact scaleless lanes, and an explicitly unstable lane.
Workers change both job and lane ordering and exercise batches and singletons.

Qualification is tied to the source, dependency, and binary hashes in
`build.json`, `sequential-control.json`, and `concurrent-control.json`:

- The sequential control passes.
- The actual two-thread numerical control passes all 360 batch comparisons
  across 12 rounds per worker using the retained SymbolicaBatch backend.
- A separate four-worker cold-specialization test passes, confirming that
  concurrent requests initialize one shared analytic-jet plan and release its
  ownership correctly. Its frozen 80949db core build is recorded in
  `cold-specialization.json`.

The original restricted-license run allowed one Symbolica thread, so concurrent
execution initially remained unqualified. After the user supplied a license,
`license-capabilities.json` records the public capability check and the two
ignored tests were explicitly run. No license key is stored in this directory.
These tests remain ignored by default so users with a restricted license do not
accidentally exceed their allowance.

The original rank-1 f64 box fixture had no successful lane under the existing
stability gate. Its failed run is retained in `rank1-fixture-*`; the concurrency
corpus uses a scalar D0 positive control while retaining tensor/derivative
coverage elsewhere. No production guard or tolerance was changed.

From the repository root, with an appropriate license configured:

```sh
source scripts/env.sh
cargo test -p iregi-rust --test concurrent_workspaces \
  independent_warmed_numeric_workspaces_match_sequential_results \
  -- --ignored --test-threads=1 --nocapture
cargo test -p iregi-rust --lib \
  plan::tests::cold_specializations_are_initialized_once_across_threads \
  -- --exact --ignored --test-threads=1 --nocapture
```

This qualifies the retained implementations and corpus. Generated native-master
kernels and future source changes need their own concurrency qualification.

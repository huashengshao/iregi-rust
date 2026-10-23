# Paused at user request

Paused 2026-10-23 18:55 UTC. No owned compiler or runtime remains. Production was not changed.

## Frozen candidate

- Base: production standalone checkpoint `21622ec`.
- Private source: `target/planar-automatic/source-snapshot`.
- Separate accounting repair: `accounting-source`, `accounting.patch`.
- Automatic dispatch relative to accounting: `automatic.patch`.
- Build: `build.json`, `build.log`, `build.py`; binary `core-tests` SHA256 `eb52303483e511267ba38ed1839329723b5fdb67446f673c797196708f4dd3cd`.
- Build exit 0. Elapsed 631.212 s includes 273.737 s logged compiler pause; this is not a performance result.
- Failed initial build preserved in `failed-build-initializer/`; corrected initializer placement and unused test import only.
- Owned compiler1896058 pause/resume provenance in `compiler-pause.json`.

## Qualification so far

- `runs/accounting.json`: 6 passed, 1.730 s; nested retries, analytic attempts, child work on global errors, preserved flags.
- `runs/eligibility.json`: 1 passed, 26.620 s; completed18:55:39.709UTC before termination scan. Source/binary unchanged.
- `user-pause.json`: no remaining owned test processes found. No numerical run was suspended.
- Independent child source review found no concrete blocker in dispatch/accounting. Runtime qualification is incomplete.

## Resume next steps

1. Run frozen named groups `binary64`, `hybrid`, `mixed`, `auxiliary` using `run.py` with bounded caps (mixed at most600s), CPUs16/17, subject to ROOT scheduling. Preserve all outcomes.
2. Run ordinary41, PV14 (+1ignored), standalone9 (+3ignored) regression groups if dispatch tests pass. Do not indiscriminately run all197 tests.
3. Package source/build/dependency/test/review provenance, keeping accounting and automatic patches separately reviewable. No production adoption without ROOT approval.
4. Combine certificate-reuse receipts only in a new snapshot after this frozen qualification. Receipt patch: `validation/raw-distance-receipts-performance/adoption/adoption.patch` (unapplied). Its execution.rs generic fallback (~2151) and dispatch_profile (~2335) must aggregate private `proof_work` before propagating captured child errors, matching new public child-work accounting. Receipt tests: `execution/proof_receipt_tests.rs` (10tests). Coordinate numeric_batch_audit; do not overwrite this candidate.

## Commands after explicit resume

Run from `/shared/external/iregi/iregi-rust`:

```sh
source scripts/env.sh
source .local/symbolica-license.env
taskset --cpu-list 16,17 python3 target/planar-automatic/run.py binary64 --timeout 300
```

Choose each named group separately; runner refuses overwriting previous results. No automatic rank7 qualification or production claim yet.

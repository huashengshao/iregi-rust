# Propagated full-Dual joint-budget core tests

This capsule preserves the functional source change that combines each component's
propagated quadrature estimate with its returned-result operand-roundoff estimate.
Component zero uses the larger of the legacy primal and dense component-zero
roundoff estimates once; higher components use their own dense roundoff estimates.
The change reuses the existing stability heuristic, normalization, precision and
signed snapshot checks. It adds no interval-error claim or new algebra.

The final owned Cargo build passed and all 15 selected, individually named libtests
passed in 15.112 seconds. These are software and symbolic microtests, not a
full-Dual integral qualification. D6 native evaluation remains **on hold** because
the ordinary finite reference is unresolved. No new numerical result, convergence,
performance, benchmark-report or public high-point precision claim is admitted.

All three build receipts and both test cohorts are retained. The first test cohort
passed six tests, then exposed a test fixture whose synthetic fallback injection
was lost when `new_dual` rebuilt its analytic order. Preparing the fixture at order
two fixed that setup error; the following build exposed an `Arc` ownership error.
Cloning the pointed-to plan fixed that test-only compile error. The final build
and all 15 tests passed. Both failures, both narrow patches, all raw logs and the
unchanged original 11-file production/source patch remain visible. No production
guard or numerical tolerance was changed for either test repair.

There are three declared source contexts, each with 132 paths, and 134 distinct
path/hash versions in total. Of those, 119 are inherited by exact content hash from
the sibling `checked-g-generalized-core-tests` archive; only 15 new source versions
are stored here. The wider captured source context includes two files outside the
11-file patch; their presence is not additional test coverage. Cargo event records
and receipt hashes identify the two successful frozen libtest products. Compiled
products, license literals and a hermetic dependency closure are deliberately
absent. This checker does not rehash binaries or inspect live process groups.

Run the saved-only replay with a standard Python 3 interpreter:

```sh
python3 validation/propagated-dual-joint-budget-core-tests/check.py
```

For a minimal portable copy, copy this entire six-file directory and only
`manifest.json` plus `payload.tar.gz` from its sibling
`checked-g-generalized-core-tests` directory, preserving that sibling name. The
checker restores only the selected inherited objects, verifies every archived
source/log/receipt, reapplies all stored source hunks, checks actual Cargo events
and one-test execution summaries, and reproduces `qualification.json`. The parent
capsule's test provenance is not replayed or added to this capsule's 15-test count.
The terminal functional record also preserves a separate historical absence check
for all 27 owned build/test process groups and the source/Cargo release.

`package.py` can rebuild this capsule from the explicitly named owned source
snapshots and saved evidence in the original worktree. It never invokes Cargo,
the libtest executable, the producer or a numerical evaluator. Neither packaging
nor replay creates a new runtime qualification.

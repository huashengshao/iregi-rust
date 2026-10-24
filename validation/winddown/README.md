# Preserved unfinished work

These archives consolidate private source and evidence at the user's requested
pause. They are **not production patches or new numerical qualification**.
`manifest.json` records every member hash and explicitly lists omitted compiled
products. The completed N7 and scheduler qualifications have their own sibling
capsules outside this directory.

| Archive | Scope at pause |
| --- | --- |
| `native-f64-sixpoint-composition.tar.gz` | Reviewed combined optional master policy; 8 metadata checks, 4 code-generation steps and 20 ordinary exact tests passed. Seven constructor tests and whole-array numerical regressions did not run. |
| `n6-numeric-types-dual.tar.gz` | Private numeric-type/dilation-Dual pilot, source reviews and unfinished bounded runner/comparator preparation. No compiler or numerical execution. |
| `scheduler-optimized-followup.tar.gz` | Current-source/dependency census and source-only reference-cohort review. No fresh optimized build or timings. |
| `historical-session-context.tar.gz` | Earlier rolling context notes. Their running/pending statements are historical; `HANDOFF.md` and sealed receipts take precedence. |

The archives contain no wheels, libraries, executables, credentials or private
license environment. Rebuildable products remain in ignored local caches, where
available. Hashes and original commands remain in the evidence so future builds
can be compared without committing those products.

Inspect or extract into a **fresh** directory. For example, from the repository
root after `source scripts/env.sh`:

```sh
tar -tzf validation/winddown/native-f64-sixpoint-composition.tar.gz
mkdir -p target/restored-native-composition
tar -xzf validation/winddown/native-f64-sixpoint-composition.tar.gz \
  -C target/restored-native-composition
python validation/winddown/check.py
```

Original private runners use the original `target/...` paths and refuse to
overwrite attempt directories. A fresh checkout needs reconstruction and new
artifact/source bindings. A paused execution grant is not permission to resume
an old attempt blindly: inspect the relevant protocol and create fresh attempt
records after the user resumes the overall task. Do not relax numeric gates or
rewrite earlier receipts merely to make restored paths work.

The checker verifies archive bytes/members, the new sealed numerical capsules,
report source bindings, and preservation of all 279 result objects from
`007ca9f`. It evaluates no integral and runs no benchmark.

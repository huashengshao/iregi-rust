# Production ordinary-root allocation qualification

The production change is exactly `production.patch`: the two fresh ordinary
SSA factories call Symbolica's existing `optimize_stack` once, after the
optional Dualizer branch. The Dual branch remains unchanged. Symbolica's
zero-Horner fast path returns fresh SSA before its usual root allocation,
which explains the original gap; `dependency-audit.json` records the source
checks and affected monitors.

The uninstrumented current-source test binary passed all 30 execution,
8 contraction and 29 stability tests (67 total; no failures or ignored tests).
It uses opt2 and the retained full-workspace feature-union dependency archives.
`compile.json`, `preparation.json` and `runs/*/result.json` bind the source,
compiler, dependencies, binary, commands and logs. Test durations are diagnostic
only; project work was active concurrently.

The exact source is commit 80949db plus the retained four-line patch. The frozen
80949db optimized kernel and physical benchmark binaries do not include it.
This qualification makes no new opt3 or reference-IREGI performance claim.

The target snapshot and binary are retained at `target/core-stack-adoption`.
To repeat the focused checks with those exact bytes:

```sh
source scripts/env.sh
python3 -B target/core-stack-adoption/run.py execution::tests:: 30
python3 -B target/core-stack-adoption/run.py contraction::tests:: 8
python3 -B target/core-stack-adoption/run.py stability:: 29
```

The runner requires fresh per-filter output directories and a valid Symbolica
license from the environment. Preserve existing logs when rerunning. Rebuilds
with different dependency bytes are new qualifications even when filenames
match; the snapshot inventory and recorded direct-rustc argv define this run.

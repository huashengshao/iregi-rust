# Private lazy receipt capture: correctness only

The candidate leaves outgoing distance-proof receipts absent until the first
certified zero or validated incoming-covered pair needs retaining. It preserves
conditioning, complete Taylor selections, source identity, ordered schema,
precision context, checked counters, and error harvesting. Production is unchanged.

The independent review passed. The bounded native-debug build passed, followed by
20 receipt/lifecycle tests (12 existing + 8 new), 6 accounting tests, and all 14
paired workload cases. Every cold/warm/final comparison includes exact input and
output bits, context, metadata/status/flags, public statistics/diagnostics and
private proof-work counters. Both sides confirm inactive N5 fallback counters.
The corpus contains 10,560 distinct complex output slots over 231 lane instances,
with seven calls per implementation per case. `fixed_iterations` log values are
inert inherited labels, not loop counts executed by this correctness-only driver.

This uses the retained current debug native dependency closure and supplemental
thiserror archive described in `dependencies/`. It is a different build scope from
the earlier optimized performance cohort. The supplemental thiserror record has
completed metadata/proc-macro events and source/fingerprint/native ELF evidence;
it does not claim a completed rlib Cargo event. No numerical dependency was rebuilt.

No timing, reference comparison or production adoption is qualified here. Build
and test elapsed times are diagnostics only. The preceding final performance
cohort, including its two regressions, remains unchanged. Lazy setup now occurs
inside the arguments-stage timer; any future performance decision must use total
time rather than infer improvement from stage boundaries.

`source-snapshots.tar.gz` retains 30 baseline, 31 candidate, and 31 narrow test-source
files. `source-manifest.json` and the reviews bind their hashes and the compact
test-module mapping. The scripts and logs retain exact commands, bounds and
pre/post input checks. Reproduction requires the recorded frozen native dependency
artifacts; those compiled files are intentionally not copied into this package.
Restore source/script files to `target/raw-distance-lazy-capture-candidate`, keep
the prior input/dependency paths from the manifests, source `scripts/env.sh` and
the untracked license environment, then use a fresh numbered build attempt:

```
python3 target/raw-distance-lazy-capture-candidate/build.py 002
python3 target/raw-distance-lazy-capture-candidate/run.py 002 receipts
python3 target/raw-distance-lazy-capture-candidate/run.py 002 accounting
python3 target/raw-distance-lazy-capture-candidate/run.py 002 snapshots
```

The first command enforces an overall 180-second compilation bound; each runtime
group has a 120-second bound. Existing records are never overwritten. The license
value is neither recorded nor included in this package.

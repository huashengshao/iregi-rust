# Final receipt implementation cohort

All 14 untimed comparison cases passed. Performance timing is pending a separate quiet-window grant. The 17.40 s preflight duration is validation only.

The baseline core is 21622ec plus the common collector, independently verified to match 06706e2. The candidate adds the final reviewed automatic-planar, error-accounting and checked receipt patch. Both sides use the same frozen 6b24 master/Symbolica artifacts. All cases have two or three propagators; the automatic five-propagator path remains inactive. This is a new cohort, separate from the earlier receipt measurements.

`source-snapshots.tar.gz` contains the exact 24 baseline and 30 candidate source files. The sole private instrumentation is a read-only accessor for existing proof counters, called outside timing. Build records bind the independent source review, source manifest, paired archives, protocol, and dependency closure. The preflight retains all exact result snapshots and permits no public statistics differences.

After an explicit timing grant, from the repository root:

```sh
source scripts/env.sh
source .local/symbolica-license.env
python3 target/raw-distance-final-performance/protocol/run_timing.py --cpu GRANTED_CPU --quiet-manifest WINDOW_JSON
```

The fixed protocol uses all 14 cases, 41 alternating paired blocks, five warm calls per implementation, and shared calibration until the faster side takes at least 200 ms. The whole numerical process has a 600 s limit. Analysis retains every row and uses the preregistered 99% paired-bootstrap interval and 2% width gate. No favorable-block selection or confidence-driven stopping is allowed.

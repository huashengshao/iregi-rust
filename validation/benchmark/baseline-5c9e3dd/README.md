# Optimized interpreter checkpoint: 5c9e3dd

All eight massive bubble/triangle rank-zero/rank-one comparisons pass the
unchanged `1e-10` complete-array gate. Six timing comparisons are regressions;
two exceed the 2% uncertainty limit and remain inconclusive. Performance
acceptance is not met.

This measures the retained commit before default root-stack reuse, generalized
PV dispatch, and lazy scalar solve-vector changes. It does not qualify later
working-tree performance. Both executables, source snapshot and the live
measurement script passed provenance checks. CPU 0, binary64 Hybrid, batches
1/32, five warmups, 21 randomized paired blocks targeting 30 ms, independent
profiling passes, release thin-LTO Rust and `-O3` Fortran were used.

Reproduction from the repository root, after sourcing `scripts/env.sh` and
obtaining the shared Symbolica runtime slot:

```sh
python3 validation/benchmark/build.py --revision 5c9e3dd
python3 validation/benchmark/run.py --cpu 0 --ranks 0 1 \
  --mass-classes massive --batches 1 32 --repeats 21 --warmup 5 \
  --block-ms 30 --timeout 60 --output target/benchmark/repeated-5c9e3dd.json
```

The recorded run selected preserved executables and their matching manifests
under `target/benchmark/builds/5c9e3dd3f60c9d16c38704865cd8c1d3ed855176/`
using the runner's four explicit binary/manifest flags. The runner executed
verified private copies; their paths and hashes appear in `results.json`.
`inputs.json` is the durable copy of the raw artifact's `results-inputs.json`.
Every block and the separate profiling responses passed all tensor and Laurent
comparisons. Raw samples and the two noisy outcomes remain in `results.json`.

Do not compare absolute timings with earlier sessions: each ratio uses the
reference measured in the same paired run. The build and measurement scripts
are identified separately because the qualified runner is newer than the
measured Rust commit.

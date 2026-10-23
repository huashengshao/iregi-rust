# Optimized 80949db kernel comparison

All eight massive bubble/triangle rank-0/1 tensor-array comparisons at batches 1/32 pass the unchanged dimensionally normalized `1e-10` tolerance. Five timing rows regress and three are inconclusive because their 99% ratio intervals exceed the permitted 2% relative width. The performance requirement remains unmet.

This is the frozen optimized default SymbolicaBatch 80949db build, after master-root stack reuse, generalized PV and lazy Cayley solve. Later private core/cache/n-way/near-vacuum experiments are excluded. The accepted license is described only by capability; no key is retained.

The coordinator held project builds and numerical tasks during the CPU-0 run; a pending native D0 compilation was suspended. External host activity was not controlled. Five warm-ups precede 21 randomized paired blocks targeting 30 ms. All requested tensor/Laurent slots and the exact same input file are used; transport is excluded. The separately instrumented stage medians are diagnostic and do not sum to the uninstrumented gate time.

`results.json` preserves every raw paired sample, stage observation, ordering, input identity, environment, compiler, source map and binary hash. Build manifests and standard-error logs are adjacent. `qualification.json` records an independent rehash of all 401 immutable build-source files, both binaries and the harness. Earlier 4c32ece and 5c9e3dd sessions remain separate; changes in absolute times across sessions establish no causal revision speedup.

Reproduce from the repository root after making the recorded build available:

```bash
source scripts/env.sh
python validation/benchmark/run.py \
  --rust target/benchmark/workspace-builds/80949db-default-resume/bin/kernel_benchmark \
  --reference target/benchmark/workspace-builds/80949db-default-resume/bin/iregi-benchmark \
  --rust-build-manifest validation/benchmark/baseline-80949db-licensed/rust-build.json \
  --reference-build-manifest validation/benchmark/baseline-80949db-licensed/reference-build.json \
  --input validation/benchmark/baseline-80949db-licensed/results-inputs.json \
  --batches 1 32 --algorithm Hybrid --cpu 0 \
  --repeats 21 --warmup 5 --block-ms 30 \
  --output target/benchmark/reproduced-80949db/results.json
```

Use a quiet coordinated window and an authorized Symbolica license. Reproduction is a new measurement, not a replacement for these retained observations.

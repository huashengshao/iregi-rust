# Optimized 6b24c03 kernel comparison

All eight massive bubble/triangle rank-0/1 tensor-array comparisons at batches
1/32 pass the unchanged dimensionally normalized `1e-10` tolerance. Seven
timing families regress against original IREGI; triangle rank-one singleton
timing remains inconclusive because its 99% interval exceeds the permitted
2% relative width. Performance parity remains unmet.

This is the immutable optimized default `SymbolicaBatch` build of
`6b24c0372022e22606a1ac85f30c7fa579fb41f0`, including ordinary core temporary
storage reuse and typed per-lane conditioning context reuse. The complete
workspace build finished successfully, with recorded Cargo exit status zero.
Private RealBall, alias-collector, planar and scalar-series candidates are
excluded.

The coordinator held all other project builds and numerical jobs during the
run. CPU 254 was selected after a read-only host load survey; CPU 0 was fully
occupied by unrelated work. External host activity remained uncontrolled.
Five warm-ups precede 41 randomized paired blocks targeting 100 ms. Both
engines use identical inputs, the same pinned CPU and all requested Cartesian
moments and native Laurent slots. Transport is excluded. Separately
instrumented stage measurements do not enter the uninstrumented timing gate.

`results.json` retains every paired sample, ordering, input identity,
environment, compiler, source map and binary hash. `qualification.json`
records an independent source/binary/harness rehash and recomputation of all
eight bootstrap ratio distributions. The historical 80949 session used a
different CPU and shorter blocks. Only each session's paired IREGI reference
supports a timing conclusion; these sessions do not establish a causal
revision-to-revision speedup.

Reproduce from the project root with an authorized local Symbolica license:

```bash
source scripts/env.sh
source .local/symbolica-license.env
python3 validation/benchmark/run.py \
  --rust target/benchmark/workspace-builds/6b24c03-default/bin/kernel_benchmark \
  --reference target/benchmark/workspace-builds/6b24c03-default/bin/iregi-benchmark \
  --rust-build-manifest validation/benchmark/baseline-6b24c03-licensed/rust-build.json \
  --reference-build-manifest validation/benchmark/baseline-6b24c03-licensed/reference-build.json \
  --input validation/benchmark/baseline-6b24c03-licensed/results-inputs.json \
  --batches 1 32 --algorithm Hybrid --cpu 254 \
  --repeats 41 --warmup 5 --block-ms 100 \
  --output target/benchmark/reproduced-6b24c03/results.json
```

Use a coordinated quiet window and retain a new result directory. The
preliminary three-block, one-millisecond correctness smoke is retained under
`target/benchmark/6b24c03-correctness-smoke`; its timings are not qualified.

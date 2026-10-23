# First controlled baseline

This measures the committed `4c32ecec25e3067cfd43a72cea204eab8cdc6bef`
implementation with its Symbolica batch-interpreter scalar backend. It does
not measure subsequent workspace changes or the opt-in generated Rust backend.

All eight topology/rank/batch comparisons pass the unchanged numerical gate.
Seven fail the performance-parity gate. The rank-zero bubble at batch32 is
faster than the reference. Every paired-ratio 99% confidence interval meets
the runner's width requirement; build and binary provenance checks pass.
These are limited massive bubble/triangle families through rank one, not
final project qualification. See `results.json` for every sample, uncertainty,
component timing, execution counter, CPU setting and source/binary identity.

Reproduce from the project root with other heavy workloads paused:

```sh
source scripts/env.sh
python3 validation/benchmark/build.py --revision 4c32ece
python3 validation/benchmark/run.py --cpu 0 --ranks 0 1 \
  --mass-classes massive --batches 1 32 --repeats 21 --block-ms 30 \
  --timeout 120 --output target/benchmark/baseline-4c32ece.json
```

`inputs.json` is the complete input corpus. The retained build manifests
identify optimized Rust and Fortran builds; subprocess transport is excluded.
The instrumented component pass is separate from the uninstrumented ratios.

# Generated Rust master timing baseline

This is the immutable `4c32ecec25e3067cfd43a72cea204eab8cdc6bef` implementation with the opt-in `iregi-masters/native-batch` backend. It does not qualify later working-tree changes.

All eight identical-input numerical comparisons pass the unchanged `1e-10` gate. Paired timing gives two improvements, one parity result, and five regressions; the overall performance goal is not met. Measurements used CPU 0, 21 paired 30 ms blocks, warm-up, optimized builds, and the same uncertainty gate as the interpreter baseline. All agent-owned heavy jobs were held during measurement.

| Family | Batch | Rust / IREGI | 99% interval | Gate |
|---|---:|---:|---|---|
| n2-r0-massive | 1 | 0.992746 | [0.986575, 1.002663] | parity |
| n2-r0-massive | 32 | 1.030861 | [1.024135, 1.042498] | regression |
| n2-r1-massive | 1 | 1.533804 | [1.526101, 1.548830] | regression |
| n2-r1-massive | 32 | 1.068719 | [1.061674, 1.081032] | regression |
| n3-r0-massive | 1 | 0.849494 | [0.844473, 0.857912] | improvement |
| n3-r0-massive | 32 | 1.714652 | [1.703520, 1.723159] | regression |
| n3-r1-massive | 1 | 0.849801 | [0.844259, 0.853890] | improvement |
| n3-r1-massive | 32 | 1.220063 | [1.205695, 1.228473] | regression |

Absolute reference timings differ substantially from the earlier interpreter run despite identical reference binary and inputs. Each verdict uses its own paired reference measurements; do not infer a direct backend speedup by dividing medians across the two sessions. Both run manifests preserve CPU/frequency observations and full raw blocks.

Reproduce from the project root:

```sh
source scripts/env.sh
python3 validation/benchmark/build.py --revision 4c32ece --native-batch
python3 validation/benchmark/run.py --ranks 0 1 --mass-classes massive \
  --batches 1 32 --repeats 21 --block-ms 30 \
  --output target/benchmark/native-4c32ece/results.json
```

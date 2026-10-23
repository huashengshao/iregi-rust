# Native scalar-master batch policy measurement

The existing `Whole` policy remains preferable for the measured 32-row f64
workloads. Smaller blocks increased runtime in every family and ordering.
This measurement selects a batch policy; it is not a comparison with original
IREGI and does not establish precision-rescue or Dual performance.

| Family | Ordering | Whole median per batch | FixedRows4 speedup | FixedRows8 speedup | FixedRows16 speedup |
| --- | --- | ---: | ---: | ---: | ---: |
| C0 | homogeneous | 255.52 µs | 0.728 | 0.826 | 0.916 |
| C0 | interleaved | 599.12 µs | 0.463 | 0.643 | 0.821 |
| C0 | grouped | 611.37 µs | 0.680 | 0.874 | 0.884 |
| D0 | homogeneous | 11.131 ms | 0.386 | 0.586 | 0.813 |
| D0 | interleaved | 12.584 ms | 0.364 | 0.528 | 0.755 |
| D0 | grouped | 12.313 ms | 0.425 | 0.643 | 0.869 |

Speedup is the paired median of `Whole / FixedRows` within timing blocks;
values below one are slower. Every listed comparison has a per-comparison
99% bootstrap interval below one. Exact intervals and absolute timings are
in `summary.json`. The same-stride FixedRows32 control differed by roughly
one to two percent, so small differences at that scale are not treated as
optimization evidence. Intervals are not simultaneous across comparisons.

The benchmark used CPU0 during an exclusive quiet window, 21 rotated blocks
per policy with at least 30 ms per block, and fresh evaluators configured
before warmup. Homogeneous batches replicate one physical point; interleaved
and grouped batches contain the same four points in different orders.
Preparation and initial parity checks were excluded from timings. Normal
adapter result allocations remain included.

Before timing, the strengthened native physical test compared the same four
fixture rows against Symbolica and passed. The probe then required every
physical output (finite, total single pole, double pole, UV, IR) and lane
status to match bitwise across all policies. Every timed lane was valid.

`raw.csv`, `physical-parity.log`, and `probe.log` retain the observations.
`provenance.json` records the source revision, compiler, artifact hashes,
commands, affinity, and reproducible probe source. The backend is the frozen
optimized `4c32ece` build, linked from its preserved release archives; later
working-tree Dual changes were not silently mixed into this measurement.

# Direct-engine same-session benchmark (30 October 2026)

TIRust's public binary64 default (`TensorReductionPlan::new` + `TensorWorkspace`,
which now selects the direct numerical engine) against original IREGI and
COLLIER 1.2.10 on the fixed 18-row opening corpus, in one session, on one pinned
core, with interleaved paired blocks. Every ratio has TIRust in the numerator
(below one: TIRust faster).

- Host CPU 199 (AMD EPYC 9754 128-Core Processor); load average 135.80 / 129.07 / 121.72
  at start and 125.62 / 116.71 / 117.66 at the end (shared host).
- Rounds: 11 (batch 1) and 7 (batch 32), ~20 ms blocks,
  seeded random order per round, fresh process per candidate and row.
- TIRust git head `c063a78db343`; binary SHA-256 values in `summary.json`/`build.json`.
- Accuracy: E/A: dimensionally rescaled whole-array max discrepancy over all moments and four Laurent slots, versus the archived reference tensors admitted against quadruple-precision original IREGI.
- Selection: IREGI: fastest mode with a complete finite lane-0 array within E/A<=1e-3 of the reference; COLLIER: archived opening-double selected public configuration; TIRust: public default facade (Hybrid, binary64).

## Results

### Batch 1

| Input | TIRust | E/A | IREGI (mode) | TIRust/IREGI | COLLIER | TIRust/COLLIER |
|---|---:|---:|---:|---:|---:|---:|
| N=1, R=0 | 271 ns | 0.0e+00 | 769 ns (PV) | 0.3551 [0.3447, 0.3591] | 388 ns | 0.700 [0.695, 0.706] |
| N=1, R=6 | 2.75 µs | 1.6e-20 | 23.10 µs (Hybrid) | 0.1191 [0.1155, 0.1238] | 4.38 µs | 0.628 [0.625, 0.629] |
| N=2, R=1 | 698 ns | 4.4e-16 | 3.03 µs (PV) | 0.2301 [0.2284, 0.2339] | 1.13 µs | 0.617 [0.609, 0.623] |
| N=2, R=6 | 4.94 µs | 4.4e-16 | 383.40 µs (IBP) | 0.0129 [0.0128, 0.0130] | 8.42 µs | 0.589 [0.581, 0.596] |
| N=3, R=2 | 5.14 µs | 4.0e-15 | 24.92 µs (PV) | 0.2064 [0.2027, 0.2084] | 8.32 µs | 0.618 [0.594, 0.625] |
| N=3, R=3 | 5.88 µs | 4.0e-15 | 67.12 µs (PV) | 0.0876 [0.0870, 0.0878] | 10.55 µs | 0.557 [0.553, 0.560] |
| N=3, R=6 | 11.35 µs | 4.0e-15 | 2.71 ms (IBP) | 0.0042 [0.0042, 0.0043] | 51.50 µs | 0.221 [0.209, 0.224] |
| N=4, R=4 | 22.16 µs | 1.6e-14 | 529.10 µs (PV) | 0.0419 [0.0418, 0.0428] | 49.65 µs | 0.446 [0.445, 0.452] |
| N=4, R=6 | 31.97 µs | 1.6e-14 | 12.49 ms (IBP) | 0.0026 [0.0025, 0.0026] | 264.19 µs | 0.121 [0.120, 0.122] |
| N=5, R=5 | 64.70 µs | 6.1e-12 | 8.69 ms (Hybrid) | 0.0074 [0.0074, 0.0075] | 303.78 µs | 0.213 [0.212, 0.216] |
| N=5, R=6 | 87.25 µs | 2.4e-11 | 46.94 ms (IBP) | 0.0019 [0.0018, 0.0019] | 1.06 ms | 0.083 [0.080, 0.083] |
| N=6, R=6 | 215.78 µs | 1.2e-11 | 199.51 ms (IBP) | 0.0011 [0.0011, 0.0011] | 1.93 ms nonfinite (diagnostic) | no ratio |
| N=1, R=6 ν1=2 | 3.45 µs | 4.5e-16 | 34.55 µs (IBP) | 0.0997 [0.0989, 0.0999] | outside API | — |
| N=2, R=2 ν1=2 | 2.18 µs | 2.6e-16 | 27.39 µs (IBP) | 0.0797 [0.0777, 0.0807] | outside API | — |
| N=3, R=4 ν1=2 | 13.75 µs | 7.1e-15 | 546.24 µs (IBP) | 0.0252 [0.0251, 0.0252] | outside API | — |
| N=4, R=6 ν1=2 | 78.98 µs | 8.2e-14 | 14.98 ms (IBP) | 0.0053 [0.0053, 0.0053] | outside API | — |
| N=4, R=6 ν1=3 | 107.15 µs | 1.1e-13 | 18.84 ms (IBP) | 0.0057 [0.0056, 0.0057] | outside API | — |
| N=3, R=2 D=6 | 5.85 µs | 1.7e-14 | 79.37 µs (IBP) | 0.0734 [0.0729, 0.0749] | outside API | — |

### Batch 32 (time per point)

| Input | TIRust | E/A | IREGI (mode) | TIRust/IREGI | COLLIER | TIRust/COLLIER |
|---|---:|---:|---:|---:|---:|---:|
| N=1, R=0 | 175 ns | 0.0e+00 | 786 ns (PV) | 0.2217 [0.2211, 0.2510] | 394 ns | 0.442 [0.425, 0.485] |
| N=1, R=6 | 2.59 µs | 1.6e-20 | 23.33 µs (PV) | 0.1108 [0.1086, 0.1146] | 4.52 µs | 0.573 [0.564, 0.573] |
| N=2, R=1 | 551 ns | 4.4e-16 | 3.04 µs (PV) | 0.1814 [0.1749, 0.1838] | 1.13 µs | 0.487 [0.463, 0.493] |
| N=2, R=6 | 4.64 µs | 4.4e-16 | 392.07 µs (IBP) | 0.0119 [0.0118, 0.0120] | 8.58 µs | 0.539 [0.537, 0.564] |
| N=3, R=2 | 4.99 µs | 4.0e-15 | 24.91 µs (PV) | 0.2004 [0.1988, 0.2114] | 8.25 µs | 0.605 [0.595, 0.638] |
| N=3, R=3 | 5.69 µs | 4.0e-15 | 66.71 µs (PV) | 0.0849 [0.0816, 0.0903] | 10.69 µs | 0.530 [0.498, 0.565] |
| N=3, R=6 | 11.09 µs | 4.0e-15 | 2.77 ms (IBP) | 0.0040 [0.0040, 0.0040] | 51.06 µs | 0.217 [0.215, 0.219] |
| N=4, R=4 | 22.10 µs | 1.6e-14 | 520.91 µs (PV) | 0.0424 [0.0420, 0.0428] | 50.76 µs | 0.435 [0.428, 0.444] |
| N=4, R=6 | 31.83 µs | 1.6e-14 | 12.73 ms (IBP) | 0.0025 [0.0025, 0.0025] | 266.04 µs | 0.120 [0.112, 0.120] |
| N=5, R=5 | 65.28 µs | 6.1e-12 | 8.74 ms (Hybrid) | 0.0075 [0.0074, 0.0075] | 302.89 µs | 0.215 [0.214, 0.218] |
| N=5, R=6 | 86.47 µs | 2.4e-11 | 46.81 ms (IBP) | 0.0018 [0.0018, 0.0019] | 1.06 ms | 0.082 [0.081, 0.083] |
| N=6, R=6 | 216.13 µs | 1.2e-11 | 207.95 ms (IBP) | 0.0010 [0.0010, 0.0011] | 1.51 ms nonfinite (diagnostic) | no ratio |
| N=1, R=6 ν1=2 | 3.23 µs | 4.5e-16 | 34.46 µs (IBP) | 0.0936 [0.0926, 0.0943] | outside API | — |
| N=2, R=2 ν1=2 | 2.08 µs | 2.6e-16 | 32.25 µs (IBP) | 0.0639 [0.0626, 0.0657] | outside API | — |
| N=3, R=4 ν1=2 | 13.48 µs | 7.1e-15 | 560.69 µs (IBP) | 0.0241 [0.0237, 0.0242] | outside API | — |
| N=4, R=6 ν1=2 | 78.65 µs | 8.2e-14 | 15.48 ms (IBP) | 0.0051 [0.0050, 0.0051] | outside API | — |
| N=4, R=6 ν1=3 | 107.04 µs | 1.1e-13 | 19.00 ms (IBP) | 0.0056 [0.0055, 0.0057] | outside API | — |
| N=3, R=2 D=6 | 5.57 µs | 1.7e-14 | 83.72 µs (IBP) | 0.0664 [0.0642, 0.0668] | outside API | — |

Lanes 1–31 of each batch-32 request are binary-exact perturbations
(shifts×(256+l)/256, masses²+l/64). TIRust and same-session IREGI IBP agree on all of
them (`tirust_iregi_cross_error_lanes`, at most
1.6e-10).
COLLIER's N6R6 output is nonfinite in its archived selected configuration, as in the
26 October campaigns; its time is diagnostic only and enters no ratio.

Rejected IREGI modes (retained in `summary.json`, `iregi_modes`):
- ordinary-n2-r6 IREGI PV: rejected, no result (Fortran STOP)
- ordinary-n2-r6 IREGI Hybrid: rejected, no result (Fortran STOP)
- ordinary-n3-r6 IREGI PV: rejected, E/A 1.9e-03
- ordinary-n3-r6 IREGI Hybrid: rejected, E/A 1.9e-03
- ordinary-n4-r6 IREGI PV: rejected, E/A 6.2e-03
- ordinary-n4-r6 IREGI Hybrid: rejected, E/A 6.2e-03
- ordinary-n5-r6 IREGI PV: rejected, unstable/nonfinite lanes
- ordinary-n6-r6 IREGI PV: rejected, E/A 5.9e-03
- ordinary-n6-r6 IREGI Hybrid: rejected, E/A 5.9e-03

## Reproduce

```bash
source scripts/env.sh
python3 validation/benchmark/direct-engine-20261030/make-inputs.py
python3 validation/benchmark/direct-engine-20261030/build.py
python3 validation/benchmark/direct-engine-20261030/run.py --cpu <idle CPU> --output target/direct-engine-20261030/captureNNN
python3 validation/benchmark/direct-engine-20261030/summarize.py target/direct-engine-20261030/captureNNN summary.json
```

`capture001/` archives the capture's raw per-block observations (`raw.jsonl`), the
runner summary (`capture-summary.json`) and its log. `publish.py` appends the
records to `docs/data/results.json` and reseals the report proof.

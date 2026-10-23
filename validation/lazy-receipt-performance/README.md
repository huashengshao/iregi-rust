# Lazy receipt capture performance

The fixed optimized cohort contains **five qualified improvements, six parity results, and three qualified regressions**. All 14 intervals meet the preregistered 2% width gate. The lazy patch is not recommended for adoption under the all-family no-regression criterion; production is unchanged.

Every displayed ratio is **TIRust(lazy) / TIRust(eager)**; below one is faster. The paired variants use the same accepted current master adapter and unchanged opt3 numerical dependencies. This is not an IREGI/COLLIER comparison.

| Workload | Batch | Lazy / eager | 99% interval | Relative width | Classification |
|---|---:|---:|---:|---:|---|
| bubble-mixed-dual | 1 | 0.994489 | [0.993151, 0.996893] | 0.376% | improvement |
| bubble-mixed-dual | 32 | 0.999556 | [0.995835, 1.002062] | 0.623% | parity |
| bubble-ordinary | 1 | 0.991308 | [0.987072, 0.997625] | 1.065% | improvement |
| bubble-ordinary | 32 | 0.995745 | [0.993528, 0.996831] | 0.332% | improvement |
| bubble-zero-complex | 1 | 0.997248 | [0.995272, 0.997939] | 0.267% | improvement |
| bubble-zero-complex | 32 | 1.000823 | [0.998726, 1.003112] | 0.438% | parity |
| bubble-zero-real | 1 | 0.998446 | [0.994032, 1.004514] | 1.050% | parity |
| bubble-zero-real | 32 | 1.008938 | [1.003773, 1.015893] | 1.201% | regression |
| ggh-mixed-complex | 1 | 0.997944 | [0.995738, 1.001910] | 0.618% | parity |
| ggh-mixed-complex | 32 | 0.999879 | [0.997502, 1.001748] | 0.425% | parity |
| ggh-zero-real | 1 | 0.995093 | [0.988961, 0.997328] | 0.841% | improvement |
| ggh-zero-real | 32 | 1.002200 | [1.000219, 1.006051] | 0.582% | regression |
| triangle-ordinary | 1 | 1.007687 | [1.005314, 1.010818] | 0.546% | regression |
| triangle-ordinary | 32 | 1.001849 | [0.998143, 1.003412] | 0.526% | parity |

The single 256.685 s process completed all 1,148 observations (14 cases × 41 paired blocks), below the fixed 600 s bound. Five warm calls precede shared-count calibration to at least 200 ms on the faster side. Order alternates, with 21 eager-first and 20 lazy-first blocks. All cases, calibration trials and outcomes are retained; there were no timing retries or confidence-driven omissions.

The reported statistic is a median paired log ratio with 20,000 paired bootstrap resamples, seed 14050301 and a 99% percentile interval. Parity means the interval includes one, not proof of equivalence. This is a per-case conditional classification, not a familywise guarantee. The coordinator serialized project computation on CPU 254; the pre-window survey observed 0.664% CPU busy, and unrelated host activity was uncontrolled.

Optimized preflight compared all 14 exact snapshots (10,560 complex slots), ordered precision/Taylor context, metadata, status, flags, public statistics and proof counters. Both variants also checked exact cold/warm/final snapshots in the timing process. Each timed iteration checks the top-level Result; full lane-status parity is checked outside the timed blocks. The prior 26 debug tests remain separately qualified and were not rerun in the optimized binary.

All workloads have two or three propagators, including flattened mixed Dual cases. Automatic N5 fallback is inactive. Both sides use SymbolicaBatch by default; no native-selection or arity-two dependency candidate is included. The earlier eager-final-versus-core cohort, including its two regressions, remains separate and unchanged; cross-cohort ratios must not be multiplied.

To verify the retained package (no numerical runtime):

```sh
python3 validation/lazy-receipt-performance/verify.py
```

To reproduce the frozen analysis from retained raw inputs (no timing):

```sh
python3 validation/lazy-receipt-performance/protocol/analyze.py
```

`source-snapshots.tar.gz` contains all 61 eager/lazy core files plus 26 shared-adapter source files. `source-manifest.json`, `build/build.json`, and `shared-adapter/` retain exact commands, flags and dependency identities. Rebuilding requires the matching external hash-bound numerical archives; the original scripts intentionally retain their historical workspace paths. New builds or timings require a separate authorized experiment and must not overwrite this evidence.

`readiness*.json`, `timing-ready.json`, and `quiet-window/completion.json` are historical immutable snapshots. Their pending/unmeasured labels describe their creation time; `qualification.json` is the final append-only analysis record. No license key or secret is included.

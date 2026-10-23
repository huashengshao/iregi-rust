# Final receipt implementation performance

The fixed final-patch cohort completed all 14 cases: **11 qualified improvements, one parity result, and two qualified regressions**. Every 99% interval meets the preregistered 2% width gate. The result does not meet an all-family no-regression criterion; no production adoption is recorded.

The 325.77 s run includes preparation and calibration; reported batch latencies exclude those stages. All 1,148 observations are retained (14 cases × 41 alternating pairs). No case was dropped or repeated based on confidence intervals.

| Workload | Batch | Candidate / baseline | 99% interval | Relative interval width | Classification |
|---|---:|---:|---:|---:|---|
| bubble-mixed-dual | 1 | 0.512274 | [0.510059, 0.513187] | 0.611% | improvement |
| bubble-mixed-dual | 32 | 0.581191 | [0.579871, 0.582852] | 0.513% | improvement |
| bubble-ordinary | 1 | 1.028988 | [1.024310, 1.032655] | 0.811% | regression |
| bubble-ordinary | 32 | 0.992378 | [0.991585, 0.995671] | 0.412% | improvement |
| bubble-zero-complex | 1 | 0.508779 | [0.508001, 0.509293] | 0.254% | improvement |
| bubble-zero-complex | 32 | 0.498021 | [0.496113, 0.498794] | 0.538% | improvement |
| bubble-zero-real | 1 | 0.509383 | [0.506290, 0.510190] | 0.766% | improvement |
| bubble-zero-real | 32 | 0.495426 | [0.494231, 0.497297] | 0.619% | improvement |
| ggh-mixed-complex | 1 | 0.670623 | [0.667992, 0.673935] | 0.886% | improvement |
| ggh-mixed-complex | 32 | 0.621474 | [0.618962, 0.626713] | 1.247% | improvement |
| ggh-zero-real | 1 | 0.674227 | [0.671673, 0.677279] | 0.831% | improvement |
| ggh-zero-real | 32 | 0.622261 | [0.618266, 0.626569] | 1.334% | improvement |
| triangle-ordinary | 1 | 1.005977 | [0.999937, 1.009410] | 0.942% | parity |
| triangle-ordinary | 32 | 1.006935 | [1.001978, 1.012558] | 1.051% | regression |

Baseline: the 06706e2-equivalent core. Candidate: the same core plus the final reviewed automatic-planar, accounting, and checked-receipt patch. Both use the same frozen 6b24 master/Symbolica archives. Every case is N2/N3, so N5 fallback is inactive. All pre/post comparisons retain exact input/output bits, contexts, public metadata/statistics, flags, and diagnostics.

The coordinator serialized project work on CPU254. External host activity was uncontrolled; the pre-window survey recorded 27.7% busy on that CPU. The raw observations, calibration records, immutable window manifest, source/binary bindings, and independent review are retained.

`qualification.json` remains the original readiness record referenced by the immutable quiet-window manifest. `performance-qualification.json` records the completed new cohort. The historical first-cohort receipt measurements remain separate. No IREGI-reference performance parity or multiplication of separate optimization gains follows from this comparison.

# Binary64 opening-table capture

All timings use f64 / binary64. Error is the dimensionally rescaled array-relative discrepancy; diagnostic rows have no usable complete output.

| Input | TIRust total µs | Measured relative error | Status | COLLIER total µs | COLLIER relative error / nonfinite |
| --- | ---: | ---: | --- | ---: | --- |
| ordinary-n1-r0 | 0.965581 | 0 | complete finite output | 0.380531 | 0 / 0 nonfinite |
| ordinary-n1-r6 | 60.0769 | 0 | complete finite output | 4.36737 | 1.56892e-20 / 0 nonfinite |
| ordinary-n2-r1 | 6.70152 | 4.4152e-16 | complete finite output | 1.08918 | 1.10802e-15 / 0 nonfinite |
| ordinary-n2-r6 | 1485.18 | 0 | complete finite output | 8.36155 | 2.24978e-16 / 0 nonfinite |
| ordinary-n3-r2 | 1309.26 | 4.01465e-15 | complete finite output | 8.19898 | 6.96111e-15 / 0 nonfinite |
| ordinary-n3-r3 | 1449.82 | 4.01465e-15 | complete finite output | 10.4515 | 6.96111e-15 / 0 nonfinite |
| ordinary-n3-r6 | 5650.71 | 4.01465e-15 | complete finite output | 49.97 | 6.96111e-15 / 0 nonfinite |
| ordinary-n4-r4 | 1522.11 | 0 | complete finite output | 48.9723 | 9.73989e-15 / 0 nonfinite |
| ordinary-n4-r6 | 11256.4 | 1.68657e-14 | complete finite output | 261.912 | 9.73989e-15 / 0 nonfinite |
| ordinary-n5-r5 | 5388.35 | 6.31731e-12 | complete finite output | 293.291 | 1.10084e-11 / 0 nonfinite |
| ordinary-n5-r6 | 12952 | 2.45939e-11 | complete finite output | 1051.82 | 4.26744e-11 / 0 nonfinite |
| ordinary-n6-r6 | 419120 | 1.23023e-11 | complete finite output | 2819.23 | 1.70509 / 195 nonfinite |
| extended-n1-r6-dot2 | 69.6573 | 4.15757e-16 | complete finite output | outside direct API | — |
| extended-n2-r2-dot2 | 71.4351 | 5.50615e-16 | complete finite output | outside direct API | — |
| extended-n3-r4-dot2 | 1552.45 | 7.01193e-15 | complete finite output | outside direct API | — |
| extended-n4-r6-dot2 | 26117.3 | unavailable | refused output; diagnostic timing | outside direct API | — |
| extended-n4-r6-dot3 | 25510.5 | unavailable | refused output; diagnostic timing | outside direct API | — |
| extended-n3-r2-h1 | 127.87 | 1.67992e-14 | complete finite output | outside direct API | — |

The initial38 TIRust candidates plus four explicitly post-hoc public PV/permuted-denominator trials are retained. All run at working53 significant bits; only ordinary N5R5/N5R6/N6R6 request accuracy39 (about1e-6). Others retain53. COLLIER tries32 public configurations, all binary64; the high3 request1e-6, the others1e-10. No native flag alone disqualifies finite output within three relative digits.

The initial TIRust audit compares32,512 complex fields from68 successful arrays and checks eight null refusal payloads. Four supplemental attempts also refuse at unchangedrequest53. COLLIER saved replay passes20,991 checks: eleven complete finite selected rows, one incomplete N6R6 result. Finite-subset error on a nonfinite array is diagnostic only. No controlled-host speed gate follows from selecting optimistic means.

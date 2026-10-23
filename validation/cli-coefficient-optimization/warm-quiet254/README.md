# Private CLI coefficient CSE timing

The frozen quiet-window run retains all **16** rows: two compiler candidates, four physical numerator graphs, and batches1/32. CSE0 has eight improvements; Pair1 has six improvements and two results classified as inconclusive because their99% confidence interval is wider than2% of the median. No production change or IREGI performance acceptance is implied.

This is the warm complete `CoefficientWorkspace::evaluate` call, with f64 inputs, an opt2 caller, and coherent frozen6b24 optimized dependencies. Each block includes N result allocations and N−1 preceding-result drops; the final result is checked and dropped outside the timer. Input preparation, plans, exact proofs, mapping and packing are excluded and separately recorded.

CPU254 was reserved by the externally bound quiet-window manifest. Both modes ran once, in one coordinated cohort, with21 seeded balanced-order paired30ms blocks. Two2ms pilots selected one shared fixed iteration count per row. There is no per-call clock. Every variant matches its own saved output bits, precision and signed-zero before/after all pairs.

| Candidate | Graph | Batch | Baseline µs | Candidate µs | Ratio [99% CI] | Decision |
|---|---|---:|---:|---:|---|---|
| cse0 | ggh | 1 | 1.248 | 1.139 | 0.911480 [0.904938, 0.923111] | improvement |
| cse0 | ggh | 32 | 49.810 | 46.269 | 0.928089 [0.921340, 0.933318] | improvement |
| cse0 | gghh | 1 | 20.627 | 17.497 | 0.847868 [0.846374, 0.849842] | improvement |
| cse0 | gghh | 32 | 867.798 | 750.213 | 0.866321 [0.864232, 0.867717] | improvement |
| cse0 | gghhh | 1 | 92.052 | 78.701 | 0.853099 [0.847522, 0.855540] | improvement |
| cse0 | gghhh | 32 | 3629.424 | 3097.413 | 0.854512 [0.850496, 0.855060] | improvement |
| cse0 | gggg-up | 1 | 478.925 | 338.464 | 0.707071 [0.702812, 0.709946] | improvement |
| cse0 | gggg-up | 32 | 17374.971 | 14021.338 | 0.805057 [0.801190, 0.811003] | improvement |
| pair1 | ggh | 1 | 1.183 | 0.851 | 0.719341 [0.713790, 0.723073] | improvement |
| pair1 | ggh | 32 | 50.179 | 32.317 | 0.644711 [0.642220, 0.647711] | improvement |
| pair1 | gghh | 1 | 20.121 | 12.026 | 0.598264 [0.597432, 0.601337] | improvement |
| pair1 | gghh | 32 | 862.491 | 486.726 | 0.562492 [0.559033, 0.568036] | improvement |
| pair1 | gghhh | 1 | 94.059 | 53.287 | 0.566916 [0.552248, 0.571979] | inconclusive-noise |
| pair1 | gghhh | 32 | 3633.493 | 1889.959 | 0.520497 [0.519670, 0.521774] | improvement |
| pair1 | gggg-up | 1 | 480.368 | 219.707 | 0.457032 [0.455238, 0.460507] | improvement |
| pair1 | gggg-up | 32 | 17468.183 | 8539.086 | 0.486526 [0.478030, 0.490005] | inconclusive-noise |

Ratio is candidate/baseline paired latency. Confidence intervals use the frozen10,000-resample percentile99% median helper. Pair1 ggHHH singleton and massless up-box batch32 remain inconclusive despite lower candidate medians. These are not silently counted as passing performance gates.

## Unchanged raw failures and separate dimensional qualification

The prior exact proof covers223 coefficient expressions and their physical scaling. The raw coefficient criterion `|a-b|/max(1,|a|,|b|)<=1e-10` remains unchanged and fails for some near-zero dimensionful coefficients, including baseline results. This timing cohort retains those failures. Its separate, prereviewed dimensional check divides by `max(Q^(N-rank),|a|,|b|)` and passes at1e-10 against a Float256 evaluation of exactly lifted represented inputs. This does not replace the raw gate or qualify final physical integrated amplitudes.

| Candidate | Graph | Batch | Raw failed real components: baseline / candidate |
|---|---|---:|---:|
| cse0 | ggh | 1 | 0 / 0 |
| cse0 | ggh | 32 | 0 / 0 |
| cse0 | gghh | 1 | 1 / 1 |
| cse0 | gghh | 32 | 32 / 32 |
| cse0 | gghhh | 1 | 2 / 3 |
| cse0 | gghhh | 32 | 64 / 96 |
| cse0 | gggg-up | 1 | 3 / 4 |
| cse0 | gggg-up | 32 | 96 / 128 |
| pair1 | ggh | 1 | 0 / 0 |
| pair1 | ggh | 32 | 0 / 0 |
| pair1 | gghh | 1 | 1 / 2 |
| pair1 | gghh | 32 | 32 / 64 |
| pair1 | gghhh | 1 | 2 / 6 |
| pair1 | gghhh | 32 | 64 / 192 |
| pair1 | gggg-up | 1 | 3 / 4 |
| pair1 | gggg-up | 32 | 96 / 128 |

Rows32 repeat the same canonical input; these counts are retained observations, not independent kinematic coverage. The wider numerical corpus and exact homogeneity proof remain in the parent qualification. Different compiler modes can change output rounding, signed-zero and tracked precision; only each variant’s repeated own outputs are required to be bitwise identical.

## Preparation observations

The following exact-plan build costs are single observations from this run, not repeated latency benchmarks. Reusing a workspace is necessary to realize the warm costs above; no amortization claim is made. Graph preparation, proof, numerical mapping and input packing are also retained per row in `results.json`.

| Candidate | Graph | Direct plan ms | Candidate plan ms |
|---|---|---:|---:|
| cse0 | ggh | 0.551 | 0.647 |
| cse0 | gghh | 1.306 | 6.129 |
| cse0 | gghhh | 4.389 | 24.441 |
| cse0 | gggg-up | 29.261 | 128.455 |
| pair1 | ggh | 0.160 | 2.380 |
| pair1 | gghh | 1.178 | 12.552 |
| pair1 | gghhh | 5.315 | 53.610 |
| pair1 | gggg-up | 27.996 | 431.678 |

## Evidence and reproduction

`qualification.json` binds the quiet manifest/completion, parent correctness qualification, static binary, runtime manifest and all raw files. `raw-timing.tar.gz` retains every original per-graph JSON, stdout/stderr log and runtime manifest; `raw-index.json` lists individual hashes. Sources, assets, compiler command/log, runner, parser tests and bootstrap helper are included.

Restore sources/assets to `target/cli-coefficient-cse-timing`, use `compile.py` with the preserved complete6b24 dependency closure, and run `run.py NEW_DIRECTORY CPU` only in a newly authorized quiet window. Never overwrite `quiet254`. `analyze.py quiet254` reconstructs this result from the retained raw artifacts. The original interrupted compile attempt remains under `target/cli-coefficient-cse-timing/earlier-attempts/user-pause-20261023`; it is not a timing attempt.

Independent review passed589 retained-data/protocol checks, including all16 classifications, paired intervals, order strata, repeated output metadata and provenance. The separate dimensional reference maximum is2.2075794361255787e-15;396 baseline and660 candidate raw failure instances remain visible across the repeated observations.

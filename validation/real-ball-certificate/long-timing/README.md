# Longer slim RealBall timing: all four outcomes retained

This separately registered follow-up run completed on CPU254 with 41 alternating paired blocks per case, five warm-up pairs and calibration verifying at least200ms on the faster side. The frozen binaries and inputs are identical to the first21-block run. Project compilers and other numerical jobs were held; external host activity remained uncontrolled, with27.7% load recorded before the window. Both producers exited successfully, and source/binary/dependency checks passed before and after execution.

| ggH tensor-kernel case | Original median | Slim median | Paired slim/original ratio | 99% interval | Relative interval width | Decision |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| Real masses, singleton |561.61µs|319.33µs|0.56754|[0.56534,0.57094]|0.9874%|Improvement|
| Real masses, batch32 |15.543ms|7.650ms|0.49066|[0.48870,0.49938]|2.1782%|Inconclusive noise|
| Complex masses, singleton |550.48µs|553.67µs|1.00743|[1.00243,1.00951]|0.7032%|Regression|
| Complex masses, batch32 |15.534ms|15.613ms|1.00624|[1.00242,1.00880]|0.6341%|Regression|

Each median is nanoseconds per batch before conversion to the displayed units. The paired-ratio median is computed directly from corresponding blocks, rather than by dividing the two separate medians. The unchanged statistics use10,000 paired bootstrap median resamples and require a99% interval no wider than2% of the median. Real batch32 therefore remains inconclusive, and both complex controls regress. **The candidate has not passed the familywise performance requirement and is not adopted.**

This is a private binary64 Hybrid rank-two ggH tensor-kernel comparison against the original6b24 core, with only the reviewed slim certificate changed. It is not an IREGI/MadLoop performance comparison or physical end-to-end measurement. The complex controls have complex squared masses and real momentum shifts; the certificate conservatively classifies the whole argument row. True complex momentum/Taylor behavior has separate correctness coverage, not a timing qualification here.

All192 response pairs (384 raw responses) were compared exactly, including complete tensors, statuses, counters and other non-timing metadata:190,080 complex Laurent slots across calibration, warm-up and measured blocks. Prior independent reference agreement remains in the separate full-core qualification. The first run remains unchanged at `../full-core/evidence/kernel-quiet-001`; the two runs are neither pooled nor used to replace one another. The apparently conflicting small complex-control results across runs remain visible.

The raw ledgers, calibration attempts, full responses, registration, executed runner, input catalog, frozen statistics and comparison helpers, environment, source and binary bindings, quiet-window manifest and completion are retained. Binaries and the complete dependency closure remain locally under `target` and are hash-bound rather than committed. The registration's `registered_not_run` status is a historical pre-execution document; the completed raw ledger records execution separately.

Verify every retained response and recompute the original bootstrap statistics without numerical-engine execution:

```sh
source scripts/env.sh
python3 validation/real-ball-certificate/long-timing/verify.py
```

No additional timing run, candidate variant or production adoption follows from this record.

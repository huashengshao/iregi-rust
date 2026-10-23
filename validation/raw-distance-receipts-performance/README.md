# Isolated exact raw-distance receipt performance probe

This probe compares the same private slim RealBall baseline with and without call-local exact-zero proof receipts. It does not compare the slim engine to the previous complex-ball engine, and it is not an IREGI reference benchmark. The production library remains unchanged.

Both paired libraries are frozen from the qualified 49-test/120-snapshot experiment. The probe requires exact floating-point bit equality of every successful tensor/Laurent/Taylor coefficient, complete ordinary metadata/status/diagnostic equality, and expected receipt work counters before and after timed blocks. Results are not serialized or compared inside each timed iteration. All timing lanes must succeed. Invalid/unstable lane coverage remains in the separate correctness qualification.

Fourteen cases cover singleton and batch32 for ordinary nonzero bubble/triangle controls, equal-mass lightlike bubbles with real and complex masses, mixed ordinary/lightlike complex Dual lanes, and real/mixed-complex ggH kinematics. Preparation, warmup/parity, and serialization are excluded from each numeric interval. Ordinary controls retain analytic-capable parent allocation while reusing zero proofs in no lane. Batch32 mixed cases exercise row selection and Taylor masks.

The predeclared protocol uses fixed iteration counts, 21 alternating AB/BA paired blocks, and one CPU0 process in an explicitly granted project-wide quiet window. Each row is classified independently using a deterministic 20,000-resample paired bootstrap of the median log time ratio, a 99% interval, and relative interval width at most2%; broader intervals remain inconclusive. No workloads are pooled. The runner freezes the verified executable, saves terminal state before final hash checks, and verifies all865 retained closure files plus source and archives before and after execution.

The original compile launcher is retained as build-launched.py. Independent review strengthened build.py for future builds so a recorded source/archive change fails qualification. All subsequent execution wrappers explicitly require the original build provenance flags to be true and bind both library closure manifests, so the active first build need not be repeated merely for that launcher change.

Correctness-only preflight has no --time flag. Timing requires a new explicit root-coordinator grant.

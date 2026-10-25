# Public four-point rank-six mixed Dual precision rescue

One actual public `TensorRescueWorkspace::new_dual` run evaluated the fixed EC27 N4 rank-six massive spacelike unit-power PV family. The static base and dynamic `[scaled2, invalid_mu, base]` calls returned all 210 moments, four native Laurent slots and six ordered Taylor components. The empty call reset all counters. Three valid lanes retained the originating binary64 `pv_node_8`, Taylor-component2 cancellation guard and then reported convergence using working128/verification256 precision. The invalid lane remained `NotRequested` for rescue.

The independently written saved checker passed 35,280 complex comparisons: 15,120 against previously qualified Float128 values, 15,120 against original quadruple-precision IREGI unit/dot/triple response columns and 5,040 scaling comparisons. Every returned scalar coordinate is exactly representable as binary64 with stored precision53. Metadata, signed zeros, preserved inputs, static/dynamic agreement, per-stage counters, statuses and failure isolation are checked. The fixed dimensionally normalized tolerance is1e-10.

Internal working128 and verification256 result arrays were not serialized. Their agreement is observed through the actual `Converged` statuses and counters; it is not independently reconstructed here. The separate Float128/256 qualification remains in the parent rank-six capsule. Exact nearest conversion from the hidden256 array is not claimed. Nearest casts of the external128 control are diagnostic only: tiny roundoff-zero values can differ. The initial checker incorrectly required exact external128 rounding; its source and failed report are retained. The corrected observer changes no numerical gate or tolerance.

The initial example compilation failed only in the new rescue helper's error collection type. The two other frontend products passed. Its failed receipt, diagnostic and old helper are preserved; the actual example-only rebuild and its complete106 selected source snapshots are retained as hash-deduplicated text deltas against the parent. This is not a complete dependency closure. Native executables are omitted with their hashes. The one native capture completed in185.02seconds under a fixed900/60/780second bound and32GiB address-space limit; this is correctness evidence, not a timing benchmark.

The earlier D0 mixed-f64 guard failure and N5 f64/DoubleFloat guard failures remain in the parent and are not overwritten. This capsule qualifies the explicit D0 rescue example only. Generic detailed stage reports and accepted sensitivity envelopes are explicitly unavailable; no public highpoint Dual, arbitrary kinematics, physical numerator, rigorous derivative error or complete-feature claim is made.

```sh
python3 validation/public-four-point-dual-rescue-rank6/check.py
```

Replay uses only pinned saved bytes and exact standard-library validation arithmetic. It imports no producer comparator and runs no native executable, integral or algebra evaluator. `restore_files(manifest)` exposes the reconstructed aliases for future saved checks.

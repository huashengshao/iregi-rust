# Exact invariant certificate evidence

`evidence.json`, `runtime.log`, and `snapshot/` preserve the first independently
compiled certificate prototype: seven tests passed in 2.64 seconds. The recorded
source and binary hashes identify that run exactly. The snapshot predates the
public opt-in scalar wrapper and the reusable exact-zero predicate adapter; its
success does not qualify either integration.

`zero-preflight-qualification/report.json` preserves the subsequent workspace
run: all eight invariant tests and four generic exact-zero tests passed, as did
the listed ordinary scalar and rounded-zero integration regressions. The public
certified six/seven-point wrapper reached a 90-second timeout during preparation;
it remains unqualified. This build predates the nonzero-invariant conditioning
monitor, whose changes require fresh tests and performance measurements.

The current source additionally tests a rank-five matrix with no regular
principal four-dimensional chart, preventing an incorrect lower-rank diagnosis.
Current module tests can be reproduced from the project directory after the
normal dependency setup:

```sh
source scripts/env.sh
cargo test -p iregi-rust --lib invariant_certificate::tests -- --test-threads=1
cargo test -p iregi-rust --lib exact_zero_certificate::tests -- --test-threads=1
cargo test -p iregi-rust --lib certified_scalar::tests -- --test-threads=1
```

Run Symbolica test processes sequentially under the configured license. The
certificate tests exercise exact conversions, alternative charts, translation,
mixed Taylor coefficients, lane isolation, and adaptive refinement. The wrapper
tests separately compare coordinate and invariant reductions and reject invalid
lanes. New integration measurements must be recorded separately rather than
overwriting the historical prototype evidence.

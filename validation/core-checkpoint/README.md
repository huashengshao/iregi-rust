# Reduction checkpoint qualification

`qualification.json` records bounded validation of the current reduction and
CLI checkpoint. It retains executable hashes, source hashes, commands and raw
logs. Test wall times are not performance benchmarks.

The main checks cover the exact-zero and relative-conditioning gates before
scalar-master evaluation, mixed input/Taylor precision, underflow, independent
lane failures, evaluator/cache reuse, scalar interfaces, UV power counting,
legacy snapping and precision rescue. Original-reference and independent Gamma
comparisons inspect complete Laurent coefficient arrays.

Reproduce from the project root, serially under the installed Symbolica license:

```sh
source scripts/env.sh
export RUST_MIN_STACK=67108864
cargo test --workspace --no-run
cargo test -p iregi-rust --lib stability::arguments::tests:: -- --test-threads=1
cargo test -p iregi-rust --lib execution::tests:: -- --test-threads=1
cargo test -p iregi-rust --test oracle -- --test-threads=1
cargo test -p iregi-rust --test triangle_gamma -- --test-threads=1
cargo test -p iregi-rust --lib snapping::tests::legacy_batched_tensor_arrays_match_original_iregi -- --exact --test-threads=1
cargo build -p iregi-cli
python3 validation/cli_smoke.py
```

This checkpoint does not qualify the whole implementation plan. The experimental
certified scalar wrapper exceeded its 90-second preparation limit. The public
shifted-pentagon DoubleFloat/Float batch test exceeded 150 seconds without a
numeric result; its standalone master tests are separately qualified. Generic
high-point preparation, broader mixed-precision stability monitoring, native
E6 execution and per-family performance parity remain open.

An earlier new regression required bitwise equality between a heavily cancelled
Float128 calculation and a regular-coordinate calculation. Their finite results
differed by about `2.7e-25`; the corrected test requires `1e-20` mixed agreement
across every Laurent coefficient, still much tighter than the requested `1e-10`
gate. The underlying false binary64 result differs by `log(5/4)` and is rejected
before master evaluation. No production tolerance was relaxed.

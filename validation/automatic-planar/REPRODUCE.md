# Reproduce the listed scopes

Run from `/shared/external/iregi/iregi-rust`. The reviewed source patch is `final/adoption.patch`; it has not been applied by this evidence bundle. `final/production-source.tar.gz` contains all proposed core source files. `final/test-source.tar.gz` differs only by the independently audited test-module selection described in `final/source.json`.

After adoption into a working copy, the corresponding ordinary Cargo test filters are:

```sh
source scripts/env.sh
source .local/symbolica-license.env
cargo test -p iregi-rust execution::planar_fallback::tests:: -- --test-threads=1
cargo test -p iregi-rust execution::proof_receipt_tests:: -- --test-threads=1
cargo test -p iregi-rust execution::tests::accounting_ -- --test-threads=1
```

The exact qualified optimized private builds use the full commands, compiler version, environment, source hashes, six direct dependency archives, and completed dependency-closure bindings in `combined/build.json` and `final/build.json`. Corresponding build scripts and source archives are retained. Restore archives into a fresh project-local destination and adapt only the explicit destination/source paths in those scripts; they intentionally refuse to overwrite prior build records. Existing binaries remain in the original project-local target paths with their recorded hashes.

The bounded run scripts record selected and ignored tests, a fixed timeout, source/binary integrity, and final exit status. For a fresh rerun, use a fresh output directory in a copied supervisor and retain its new hash; do not overwrite the original failed or successful records. Numerical test processes ran on CPUs16/17. Source the local license file without printing it. Correctness runs overlapped a compiler, so wall times are not performance measurements.

Verify retained files with `python3 validation/automatic-planar/verify.py`. This checks file identities, not numerical results; numerical qualification comes from the bound test records and code assertions.

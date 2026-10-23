# Production promotion and supplemental checks

The reviewed `plan.rs` and `pv.rs` candidate was promoted without source changes.
`promotion-compile-manifest.json` records the exact production source hashes and
successful optimized core build. The historical candidate results in `README.md`
and `qualification.json` remain immutable, with their original dependency scope.

The promoted build and supplemental test executable use the recorded compatible
private dependency archives, including the previous default scalar-master
strategy. This does not establish native Cargo integration or qualify a later
master strategy change. Those checks belong to the final workspace build.

Five supplemental integration tests are in
`crates/iregi-rust/tests/generalized_pv.rs`:

- Supplied scalar products remain authoritative when Cartesian vectors are
  deliberately changed; the rank-zero scalar interface agrees with the same
  original fixtures. Both eligible and ineligible generalized requests are used.
- Multinomial weighting is compared with original IREGI tensor arrays containing
  a nonzero mixed moment. Expected integer weights use Symbolica factorials.
- Two complex generalized scalar cases are compared in all three Rust modes.
- Complex generalized tensor batches compare independent Rust PV and IBP
  recurrences. The original generalized tensor wrapper does not accept complex
  masses; its six recorded transport rejections remain visible.
- A collinear generalized triangle exercises numerical Hybrid retry and lane
  isolation. Its Gram determinant and the IBP dimension-recurrence coefficient
  both vanish; the test requires a retained combined failure diagnostic rather
  than claiming successful recovery.

The first combined production run passed four tests. Its fallback isolation test
failed because the intended regular binary64 neighbor triggered the existing
finite-cancellation guard, so both lanes retried and remained `Unstable`.
`combined-runtime.log` and its manifests preserve this failure and all four
passing results; `supplemental-binary64-failed-source.rs` preserves the exact test.
The retry changed only that fixture's working precision to 128 and 256 bits while
retaining its 53-bit accuracy request and the required singular-lane failure.
It passed at both precisions: the regular lane remained successful and unchanged,
only the singular lane retried, and the combined failure diagnostic was retained.
`combined-precise-runtime.log` records this targeted retry. Thus all five behaviors
are qualified across the four passing first-run tests and the corrected fixture's
passing retry, using the same combined generalized-PV/IBP-solve-vector core.
`supplemental-qualification.json` records the comparison counts, preserved initial
failure and precision-rescue scope. Native Cargo integration remains pending;
these direct builds use the archived prior-default master strategy. These
correctness checks do not constitute performance qualification.

From the repository root, the native Cargo integration command is:

```sh
source scripts/env.sh
RUST_MIN_STACK=67108864 cargo test --frozen -p iregi-rust --test generalized_pv -- --test-threads=1
```

`bundle-manifest.json` hashes the original imported candidate evidence. Additional
promotion and supplemental files have their own manifests and do not alter that
historical bundle.

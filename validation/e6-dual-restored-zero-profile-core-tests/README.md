# Restored exact-zero profile dispatch: actual current24 focused tests

The final restored-source build is `b0695760…`, with frozen libtest
`749b2ae3…`. Its actual focused run `65bc99d8…` passed all 24 distinct selected
tests in 26.859 seconds: one listing group plus 24 exact test groups, all with
clean ownership and unchanged input guards. This capsule replays saved source,
Cargo, listing and test records only; it does not compile or execute Rust.

Production `execution.rs` removes exactly the earlier 15-line bypass of optional
exact-zero profile dispatch for full-component quadrature calls. The rest of
that source body is byte-identical to the historical compiled source. The first
restored build and final corrected build have identical production execution;
only the regression source differs.

The N5/rank-0/D6 `f64` Dual regression has three lanes. Its first two lanes pass
with complete Laurent/Taylor results, independent scalar/derivative anchors,
and owned propagated quadrature contexts. The transverse third-lane germ keeps
the ordinary baseline's existing E6 `NonConvergent` refusal at order 128; lane,
error, origin and primal-envelope accessors reject it, and its analytic flag is
false. The initial restored test incorrectly expected all three lanes to
succeed. That build, its 23 prior passes, failed assertion and actual refusal
are preserved. The corrected test does not relax a production guard or qualify
the third germ.

The bound build history also retains the earlier 780-second optimized-build
timeout and separate root-authorized cancellation of the subsequent build.
Neither produced a successful frozen product. The two restored builds have
actual Cargo profile `{opt_level: "3", debuginfo: 0, debug_assertions: false,
overflow_checks: false, test: true}`. This profile evidence and focused runtime
are not a numerical-equivalence or performance claim.

```sh
python -S -B validation/e6-dual-restored-zero-profile-core-tests/check.py
```

The historical source210, five optional DD example bodies, DD reference and all
earlier failure packets are borrowed through `e6-dual-postfix-nonfinite-boundaries`
(`792765c1…`). Only three newly required source bodies are owned: restored
production execution, the initial restored regression, and its final corrected
body. Existing canonical aliases remain historical. Use
`current_source_aliases` or `compiled_sources[build_receipt_alias]` for the actual
restored build snapshots; they never overwrite earlier canonical source bytes.

Native artifacts are omitted with their historical hashes and are never opened
or rehashed. Selected source guards are reconstructed, not a hermetic dependency
build closure. Active full-rank captures and their mutable outputs are outside
scope. The focused rank-zero regression does not supply a new complete rank-six
tensor array, precision pair, full objective completion, or performance result.

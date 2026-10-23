# Generalized PV qualification

This isolated candidate restores original per-scalar generalized mode dispatch for
one through four propagators. With `e=sum(nu_i-1)` and `k=h-e`, requests with
`nu_0=1` and `k>=0` use the existing canonical PV coefficient, multiplied by
`(-2)^k/product((nu_i-1)!)`. Ineligible terms use IBP, including explicit-PV mode.
The derivation and original Fortran source locations are in `design.md`.

Nine focused tests passed in 14.91 seconds, including 21 retained generalized
fixture/mode comparisons. The independent new capture compares 36 requests and
all 312 complex Laurent slots at fixed dimensionally normalized tolerance
`1e-10`; the largest error is `7.034186491019454e-12`. These are 27 anchored
generalized requests in the three modes and nine translated direct scalar calls.
See `qualification.json` and `reference-comparison.json` for complete scope.

All source, binary and dependency hashes are retained. The source patch applies
to commit `5c9e3dd3f60c9d16c38704865cd8c1d3ed855176`; the only implementation
changes are `plan.rs` and `pv.rs`. Tests used copied coherent dependency archives
from that commit, including the previous default scalar-master strategy. They
do not qualify later shared-tree or master-strategy changes. `build-manifest.json`
is the immutable pre-runtime build record; subsequent runtime manifests contain
its hash and the completed outcomes. Setup failures are retained as separate logs.

The original generalized tensor wrapper accepts real masses only. Six explicit
complex tensor transport rejections and two successful complex generalized
scalar API results are retained separately. The latter have not yet been
compared to Rust. These failures cannot be counted as validated complex tensors.

Higher-point canonical generalized PV remains unqualified. Those requests retain
the genuine IBP/E6 path and explicit preparation diagnostics. Supplied-G,
multinomial weighting, and a dedicated generalized Hybrid runtime fallback witness
remain targeted follow-up checks. There is no performance claim in this artifact.

To repeat the production regression tests after applying the patch, run from the
repository root:

```sh
source scripts/env.sh
RUST_MIN_STACK=67108864 cargo test --frozen -p iregi-rust generalized_pv_ -- --test-threads=1
```

The standalone independent comparator is `reference_compare.rs`. Its exact
historical linked dependencies are recorded in `frozen-dependencies.json`; compile
it against the candidate core rlib and those Symbolica/serde_json archives, using
`-L dependency=target/generalized-pv/frozen-deps`, the existing Cargo dependency
directory and GMP native library directory. The recorded invocation was:

```sh
RUST_MIN_STACK=67108864 taskset -c 0 timeout 120s target/generalized-pv/reference-compare
```

The capture scripts write beneath `target/generalized-pv`, preserve input/stdout/
stderr for every original-IREGI subprocess, and record the historical driver
source that matches the executable. Later driver differences are retained and
the inactive scope is explained in capture provenance. To restore a saved evidence
bundle for inspection, copy its contents beneath `target/generalized-pv`; no
compiled executables or dependency archives are stored in the bundle.

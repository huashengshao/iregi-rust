# Symbolica build metadata qualification

Patch `0003-limit-git-watches-to-version-fallback.patch` makes Cargo's Git
metadata watches follow the version source. A usable `IREGI_UPSTREAM_VERSION`
file supplies a fixed label and needs only that file and `build.rs` watched.
The existing Git/package-version fallback still watches Git metadata when the
file is absent, empty, or unreadable. The displayed vendored version is
unchanged.

The test driver compiles the build scripts directly with `rustc` and uses
temporary Git repositories. It checks emitted version values and watch
directives across embedding-project commits, version-file changes/removal,
empty and invalid UTF-8 files, packed refs, and missing Git/repository cases.
It does not link or run Symbolica. `baseline-build.rs` retains the script from
the same pinned upstream with patches 1–2 applied, for the comparison.

Run from the iregi-rust project directory, using a new output directory:

```sh
source scripts/env.sh
python3 validation/symbolica-build-metadata/check.py \
  --baseline validation/symbolica-build-metadata/baseline-build.rs \
  --candidate dependencies/symbolica/build.rs \
  --output target/symbolica-build-metadata-tests
python3 scripts/prepare-symbolica-patch.py --vendor \
  --output target/symbolica-build-metadata-reproduced
```

`results.json` records the six build-script tests, source/binary hashes, and
raw directives. `reproduction.json` records an exact replay of the three-patch
vendor inventory. `integration.json` compares all retained source hashes
before and after integration: only `build.rs` changes; all 216 other retained
files, including numerical and license implementations, are identical.

These checks qualify the build metadata behavior. They do not measure rebuild
time or claim a new numerical or performance qualification. The earlier
Symbolica runtime evidence remains in
`validation/symbolica-production-qualification.json`.

# Unapplied certified-master API patch

`production.patch` adds the explicit `iregi_masters::certified` API, its
private finite-D0 series implementation and three focused integration tests.
It is prepared from the exact v3 sources qualified against the complete
current release dependency closure. The ordinary master API and default E6
path are unchanged. This package does not apply the patch.

`cleanup.patch` is the narrow difference from those qualified sources.
`cleanup-proof.json` records an exact whitelist replay: seven unconditional
trace statements and their timer are removed, module/API documentation is
updated, and four prototype diagnostic strings receive production wording.
No arithmetic, domain, resource limit, accuracy decision or dispatch changes.
The other 15 Rust files match the qualified snapshot byte for byte. Removing
the new module/error declarations reconstructs the live ordinary master
library exactly. Formatting is preserved; the pinned environment has no
`rustfmt` executable.

The independent review and metadata-only test typecheck passed. The three
tests have not been executed against the promoted crate. After applying the
patch, build one combined integration executable and run:

```sh
source scripts/env.sh
source .local/symbolica-license.env
cargo test -p iregi-masters --test certified -- --test-threads=1
```

The tests cover lane isolation and batching, explicit error budgets, changed
contexts, unsupported shapes, ordinary fallback without a certificate, and
the nonzero third common-mass Taylor coefficient at exact vacuum. They
verify full rectangle distances against exact budgets and independent
vacuum identities. Their typecheck used public import paths against the
qualified API, without linking or rerunning four separate drivers.

The source archive contains the four proposed files. `git apply --check`
validates the patch against the recorded live baseline. Public error enums
gain variants, so downstream exhaustive matches may need updating. Requested
bits remain diagnostic when callers supply custom explicit budgets. These
certificates cover exact represented master inputs; upstream input rounding
and E6 quadrature remain separate work.

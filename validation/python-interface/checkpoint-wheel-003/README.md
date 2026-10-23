# TIRust installed-wheel baseline 003

The numerical and native interoperability API is validated on the exact local
dev wheel recorded here. The focused suite has **28 passes and one real upstream
SVG rendering failure**, with zero skips. Installed-wheel consumer typing passes
with zero errors/warnings. This is deliberately not an all-tests-pass claim.

The failure occurs in the actual upstream diagram renderer after all 18 packaged
font assets validate: `RuntimeError: painted coordinates must be numbers`.
The original failure log/JUnit, both preceding fixed build timeouts and the
jobs-only build continuation evidence are retained. A later rendering repair
must use a separate qualification capsule and preserve this baseline.

`sources.tar.gz` and `source-files.json` freeze the implementation, pinned local
owners, patches/provenance, scalar expression evaluator assets, Cargo manifests
and lock. Font binaries are omitted but all source/package hashes are bound by
the inspection and asset receipts. Neither the wheel nor the native shared
library nor a provided Symbolica license is included.

Reproduce from the matching repository/source overlay with the usual configured
Symbolica license environment. Source `scripts/env.sh`, build using the exact
Maturin command in `wheel-003-start.json` (eight jobs, dev profile, local Linux
compatibility), install that wheel in a fresh local venv with the pinned versions
in `wheel-003-fresh-install.json`, then run the exact focused pytest command in
`wheel-003-runtime.json`. Run the installed client typing command/config from its
receipt without adding the source Python directory to the search path.

The machine-readable qualification states precise scope, counts and limitations.
Full Community-host integration, release wheels and performance remain separate.

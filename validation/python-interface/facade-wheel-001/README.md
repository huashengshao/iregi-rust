# Retained shared-facade Python wheel

This historical Linux/CPython3.13 standalone dev wheel passes35 installed tests:
the unchanged29 interoperability/numerics cases, four new generic/profile/Dual
cases, and the retained N6rank1 and N7rank0 public batching/contraction/state
cases. Installed consumer typing reports zero errors and warnings. The native
library uses the actual upstream shared PyO3 types and the shared Rust facade.

The same fresh wheel **demonstrates a user-facing upstream precision bug**:
native integer multiplication reduces an asymmetric complex value's128-bit
imaginary component to2bits. This result is preserved. The later two-branch
Numerica correction is a different source build and requires its own tests;
this capsule does not qualify it.

Run `python -I -S -B check.py` here for a portable saved-only replay. Its two
archives contain116 exact owned source/context files and55 evidence files.
Compiled wheel/native artifacts, environments and caches are omitted, with
their actual hashes/sizes retained. The archives are an admitted local source
context, not a complete compiler/native/system dependency closure.

N6/N7 results here validate the fixed Python interface cases and source context.
They do not extend the supported rank/domain/precision claims of their Rust
backends. Stage durations are correctness diagnostics, never benchmark data.

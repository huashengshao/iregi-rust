# Optional exact-zero profile: current source and focused tests

This capsule binds the actual fresh core libtest build to 210 selected source
bodies and 24 distinct focused test passes. The initial run passed 23 tests,
then timed out during the new real N5/rank-0/D6 Dual regression after 60.104
seconds. A later exact run of that same test and frozen libtest passed in
143.571 seconds of native time (146.707 seconds total). The original timeout
is retained, not rewritten as a successful first attempt.

The production change skips an optional exact-zero-profile specialization
when there is more than one Taylor component and a prepared quadrature
dependency. The unchanged input continues through ordinary reduction and its
existing guards. The new test checks that behavior and coupled quadrature
contexts against explicitly disabled optional dispatch. The existing
failed-optional-profile retry and lane-order regression is included among the
24 tests. The source proof and actual compiled source bodies are preserved;
this capsule does not execute Rust or Symbolica.

Four older allocation failures remain visible as terminal receipts, complete
small logs, no-array capture JSON, and original failure summaries. Additive
corrections preserve the earlier diagnosis verbatim. Hybrid64, PV128, and
PV256 logs show the ordinary N5 child preparation ending before a second
12,318-alias pass, consistent with optional runtime zero-profile preparation.
The earlier Hybrid32 primary preparation failure is separate. None of those
failed attempts supplies a tensor result or qualifies Hybrid numerically.

Run the saved-only replay from the project directory:

```sh
python validation/e6-dual-optional-zero-profile-core-tests/check.py
```

The four files in this directory and the twelve shallow source archive and
manifest files listed in `manifest.json` are sufficient. Parent checkers and
their dependency trees are not used. Of the 210 source bodies, 205 are borrowed
by exact archive member identity; only five optional DD example bodies
(47,527 bytes) are newly stored. `compiled_sources` and `restore_files()` expose
the canonical and actual immutable snapshot aliases for later capsules.

The saved Cargo event and guarded source/build/test files are checked.
Native artifacts are omitted, with their historical hashes retained; no native
artifact is read or rehashed during replay. The DD provenance build receipt
and older failed receipts are historical documents, without a claim to their
entire dependency closures. This is selected source and focused test evidence,
not a hermetic build closure, full rank-6 Dual qualification, a new full tensor
precision comparison, or a performance result. Live full-rank captures are
outside this capsule.

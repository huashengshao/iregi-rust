# Baseline native notebook qualification: partial result

This capsule installs and exercises the actual inspected wheel with SHA-256
`cdb52418ca8dd2909d6d2b88b6aed82c4d3ff64e9eb09a935336fbb2345d8ce0`.
It contains no wheel, shared library, numerical mock or replacement graph.
The extension is installed without dependency changes into the existing
marimo 0.24.0 notebook environment.

Four native test methods complete in 5.18 seconds under a 360-second cap.
Two methods pass: the dotted bubble/Dual/precision/invalid-neighbor controls,
and the edited-topology guard. Two methods have three error occurrences:
default bubble, triangle Float and bubble double-double stop at the real
upstream diagram display with `RuntimeError: painted coordinates must be
numbers`. The graph error occurs before the numerical assertions in those
notebook-01 test branches; they are not counted as successful tensor checks.

One export of each notebook is retained. Notebook 01 exits with error and its
21-cell HTML contains the real rendering error. Notebook 02 exits successfully
with 19 successful cells. Its native test verifies the dotted/Dual identity,
digits beyond binary64 and failed-lane isolation; finite-difference values are
computed/displayed but no additional finite-difference acceptance threshold is
claimed by this test. Browser qualification of these two native notebooks
remains pending.

Every test/export records source hashes before and after execution. Exact
source and both HTML artifacts are archived, including the failed output.
Full stdout/stderr and bounded command receipts are preserved in `attempt001`.
The numerical API's separate focused-wheel/typing qualification is owned by
the Python interface capsule. This partial notebook result does not qualify
the complete gallery or hide the upstream renderer failure.

Reproduction uses the exact wheel, the recorded marimo environment and an
authorized Symbolica license environment. Run only `NativeGalleryTests` in
`tests/python/test_gallery_runtime.py`, then export notebooks 01 and 02 once
each. The provided credential is never stored in this capsule.

# New metadata was incorrectly required from the frozen old wrapper

The18 source protocol tests passed. Driver-only linking passed against the
unchanged COLLIER archive. The bounded correctness capture completed in25.502s,
with source/input/binary guards unchanged and112 isolated request attempts.
All34 fixed rows remain present; no timing was performed.

All16 retained N2/N3/N4 rows were blocked by a harness validation defect: the
immutable old dedicated-wrapper binary reports its `collier_mode`, clock, poles
and tensors, but predates `interface` and `direct_tensor_threshold` header
metadata. The new adapter mistakenly required those newer fields. Every raw
response was retained before validation rejected it. New-driver responses and
all original-IREGI mode outputs were retained, with exact retained Hybrid
regressions passing. This is not evidence of a numerical or COLLIER failure.

The fixed gate correctly blocked all18 N5/N6/N7 rows. Their status is `not_run`,
rather than accepted zero or numerical failure. No retry or fixture change was
performed. A separately reviewed fourth source candidate validates the actual
legacy header schema, keeps all exact binary/output/status/pole regression
checks, and leaves the strict newer-driver metadata requirement in place.

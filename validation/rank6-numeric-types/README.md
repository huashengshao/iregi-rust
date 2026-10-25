# Rank-six numeric types and tensor Dual validation

This capsule preserves 24 actual captures on the same frozen `480a47a8` Cargo example: 21 passed and three returned precision-guard failures. Every successful array contains all 210 four-dimensional tensor monomials, all four native Laurent slots, and every ordered Taylor component. Preparation uses Symbolica; the independent saved checker uses exact `Fraction` arithmetic only for validation.

Coverage includes N1/N3/N4 plain f64 and DoubleFloat; N1/N3/N4/N5 mixed second-order static/dynamic Float128/256; N2 first/mixed f64 and DoubleFloat; C0/D0 mixed DoubleFloat; and C0 mixed f64. The N5 Float pair requested96 accuracy bits. The preserved failures are D0 mixed f64, N5 plain f64, and N5 plain DoubleFloat at requested96. Failed coefficients remain null. This capsule does not qualify those failed domains or imply successful public precision rescue.

The audit checks 446,880 complete complex comparisons: 216,720 original-quad reference controls, 73,920 scaling controls, 55,440 strict DoubleFloat comparisons, 40,320 f64 controls, and 60,480 Float precision pairs. Reference/f64 tolerance is the fixed dimensionally normalized1e-10; strict DoubleFloat and Float convergence use2^-80. All retained values, actual precision and signed zeros, static/dynamic agreement, invalid-lane isolation, empty-state reset, original inputs, counters, raw commands and terminal cleanup metadata are retained.

The checker independently reconstructs the mass-squared/dilation Taylor columns using unit, first dotted and tripled-propagator anchors. The reviewer authored the earlier four N2 rank-six prefix adapters, so no author-independent claim is made for those producer adapters. The other20 producer captures were authored by another agent. Original-reference finite-coefficient certification limits remain in force. Five mutation probes reject altered finite values, incomplete complex pairs, input precision loss, signed-zero drift and fabricated coefficients for failed lanes.

Inherited source context, older N2 controls and exact original-quad anchors remain in the pinned `rank7-numeric-jets` and `quad-original-iregi-low-n-rank6-dot-triple` capsules. This payload adds text captures, receipts, source and stop histories; it contains no ELF, source archive or dependency closure. No old producer comparator, integral or native executable is run by replay. Current process absence and current-main compatibility are not inferred from historical receipts. No generic highpoint Dual, finite-difference, arbitrary kinematic family, branch certificate, rigorous derivative error, performance or complete-feature claim is made.

From the repository root:

```sh
python3 validation/rank6-numeric-types/check.py
python3 validation/rank6-numeric-types/check.py --mutations
```

`restore_files(manifest)` returns project-relative saved byte aliases for future independently written checks. Default replay runs only the unchanged independent saved audit. The optional mutation replay repeats only the five saved-byte falsification probes.

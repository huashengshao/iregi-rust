# Proposed private zero-cofactor mask for certified planar charts

This is a source-only design. It has not changed the reduction implementation.
The bounded thin N6 attempt remains a failed numerical qualification.

The exact retained-input census identifies one unnecessary child in each failed
pentagon chart: the box on original lines `[0,1,2,5]`. Its Gram matrix has rank
2 and determinant zero; its Cayley matrix has rank 4 and determinant −4. Both
selected chart coefficient vectors are `[1,-1,-1,0,1]`. The selected chart
determinants are 1/2 for N6 pinch 3 / omitted coordinate row 3, and 1 for N6
pinch 4 / omitted coordinate row 0. All other eight chart-box occurrences have
regular rank-three Gram matrices. Direct exact PV preparation rejects the
singular box, while the existing ScalarCompiler prepares all four raised-power,
h=1 requests needed by its rank-one IBP representation. These are preparation
facts, not numerical integral agreement or a trace of the first nonfinite
instruction in the failed runtime.

The current `five_point_moment` skips only coefficients that are structurally
zero. A generic chart coefficient is an alias whose value can vanish at a
particular input, so the recursive singular-box PV expressions remain in that
chart. Removing a child by testing only the primal coefficient would be wrong
for Dual inputs. The separate mixed-cofactor proof perturbs original line 5 by
`x*y` along time for the first chart and along z for the second. The entire
planar constraint still vanishes, the chart denominator retains a nonzero
primal, and the previously zero coefficient has a nonzero mixed component.

For each existing chart, build raw polynomial numerators with Symbolica's
matrix determinant operations: Cramer's numerator for each non-origin
coefficient, and the negative Symbolica sum of those numerators for the origin
coefficient. Use the same unsnapped coordinate differences, squared masses and
chart row order as `constant_chart`. The common denominator is the existing
chart determinant. Check exact symbolic equality against the existing solved
coefficients before using this representation. This delegates matrix and
polynomial arithmetic to Symbolica; it adds no custom elimination or jet
convolution.

Only the certified-planar wrapper may authorize a structural inactive-child
mask. For every input batch and every lane it must establish:

- The existing coordinate-rank constraint is exactly zero in the complete
  requested Taylor shape.
- The selected chart determinant has a nonzero primal, so its inverse exists in
  that Taylor algebra.
- Every masked child's cofactor numerator is exactly zero in every requested
  Taylor component, using the existing `ExactZeroConstraintPlan` and certificate
  workspace on represented inputs. A tolerance, an uncertain proof, or a zero
  obtained by ordinary floating-point cancellation does not authorize a mask.

A full-shape zero numerator divided by a unit denominator has a zero coefficient
jet. Symbolica/Dualizer equality tests must cover this implication, including
mixed components. A failed/unknown cofactor proof simply retains that child and
its existing failure behavior. Do not project inputs or weaken the existing
chart or numerical guards. Qualification initially remains the retained massive
fixture and the existing certified-planar domain; this design does not assert
regularity of new threshold or singular-physics cases.

Group accepted lanes by `(omitted_coordinate_row, inactive_child_mask)` and use
one chart batch per group. Extend the private chart-plan/cache key by the mask;
keep the complete ordered Dual shape in the existing execution cache key. Pass
the mask only through the private certified chart constructor, preserve it when
specializing the analytic jet order, and set those proven coefficient entries
to structural zero before `five_point_moment` requests recursive children.
Ordinary PV plans, supplied-G plans and unverified chart callers must have no
way to enable this mask. Leave unrelated coordinate-identity policy unchanged.

The mask is structural, but the evidence authorizing its use is fresh per call.
It must not survive an input, precision, shape or row-map change. Independent
workspaces own their numerical state. This path should retain the existing
no-transfer boundary for raw-distance receipts across CertifiedPlanar; no proof
receipt from the N6 parent or a different chart may authorize a mask. Child
values and native primal envelopes must scatter together through the existing
verified lane mapping. Preserve flags and work counters for all attempted
charts, including certificate-only failures and masked/active child counts.

Before numerical retry, require exact tests for all five coefficient numerators,
translated/reversed routing, the two retained charts, regular-denominator
selection, full-shape zero positive controls, and the zero-primal/nonzero-mixed
negative controls. A transverse shape must still fail the planar constraint.
Test unknown certificate outcomes, reordered/chunked/mixed batches, independent
workspaces, and success→failure→empty→success reuse. No failed demanded child may
be replaced by zero. Then retry the unchanged N6 rank-two fixture at Float128
and Float256/request53, comparing all 60 native complex Laurent slots with the
original IBP reference and the existing convergence tolerance. The earlier
failure remains visible. No rank-seven retry or adoption follows from source
proof alone.

An explicit N4 Hybrid/IBP child route is a separate possible follow-up for a
nonzero full-Taylor multiplier. The exact census establishes compiler
feasibility for the one retained box, not a batched numerical fallback or an
error-envelope contract. It should not be smuggled into this zero-mask change.

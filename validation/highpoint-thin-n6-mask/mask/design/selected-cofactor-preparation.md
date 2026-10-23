# Selected cofactor preparation (source-only proposal)

The frozen mask candidate compiled successfully. Its first ordered four-component mask test timed out at the declared 30-second protocol cap before completing any test. The log contains only test entry, so no preparation substage has been measured. No numerical success, speedup, or adoption is claimed.

## Observed source path

`CertifiedPlanarReductionPlan::new` constructs the original five plane/chart determinants plus twenty Cramer numerator expressions. `CertifiedPlanarWorkspace::prepare` obtains a shape-specific `ExactZeroConstraintPlan` for all twenty-five residuals. `InvariantCertificatePlan::from_zero_polynomials` checks each expression with Symbolica polynomial conversion and constructs the unit plus all twenty-five roots. `compile_polynomials` builds that evaluator and then uses Symbolica Dualizer on the complete ordered shape. Four components therefore produce 104 output slots. `check_selected_batch` restricts inspection, not evaluator roots: each of the five cofactor passes still evaluates the complete graph.

The separate `thin-n6-mask-phase` source adds only stderr/Instant markers around the original five determinants, all cofactor construction, every polynomial conversion, scalar evaluator construction, and Dualizer. It is not built or run.

## Conservative follow-up candidates

Retain the original five plane/chart constraints in the base certificate. After full requested-shape planarity and a regular primal chart are proved, build only cofactor certificates for the selected chart. Key immutable structural plans by the full ordered shape and selected chart; every call still obtains new exact input rows and performs fresh proofs. No result cache or receipt crosses a context.

Two implementations use existing Symbolica and exact certificate APIs:

1. One certificate per selected chart, containing all five cofactor polynomials. This preserves common expressions and incurs one build per chart/shape. It produces 24 output slots for a four-component shape, but current selected-result inspection would still evaluate all five cofactors for each mask pass.
2. One certificate per selected chart and child, containing one cofactor polynomial. This produces eight output slots for a four-component shape (unit plus one root), using the existing `ExactZeroConstraintPlan::new_dual(parameters, &[cofactor], shape)` API and `check_batch`. Group all accepted rows for that chart/child into one batch. It avoids unused roots, at the cost of more small structural builds and less shared evaluation. Only measured phase evidence can choose between them.

A lazy certificate alone does not remove eager construction of all twenty Cramer Atoms. If determinant construction dominates, add a selected-chart constructor using the same existing Symbolica Matrix determinant operations, with exact equality against the frozen all-chart helper. No custom determinant, cofactor expansion, polynomial, Boolean, or Dual algebra is needed.

## Required semantics

- Nonzero primal chart determinant plus full requested-shape planarity remain prerequisites.
- Only an exact zero certificate over every requested cofactor component authorizes a bit. Nonzero or unresolved proofs retain the child.
- Any cheap primal test may select proof candidates only; it cannot authorize pruning.
- Preserve original lane order while grouping and scattering, and keep complete ordered shape in every structural key.
- Record and harvest actual certificate work before propagating errors. Budget changes must reach all cached per-target workspaces and newly prepared workspaces.
- Preserve mask in chart/analytic variant identity and order rebuild. Reject invalid or all-inactive masks.
- Reset per-call masks, diagnostics and attempt counters on empty, malformed and failed calls.
- Local certificate IDs must map explicitly to original chart/child IDs; do not infer them from diagnostic strings.
- Retain mixed-only nonzero cofactors, unresolved proofs, failed neighbors, reorder/chunk/repeat/empty controls and complete native Laurent arrays.

This proposal has not changed the frozen candidate, mathematical acceptance thresholds, or time bounds.

## Subsequent bounded phase evidence

The separately instrumented copy completed the one blocked exact test in 35.04 seconds under its new declared 60-second cap. Its base determinants took1.115 seconds, all twenty cofactor Atoms0.061 seconds, polynomial conversion0.014 seconds, scalar evaluator0.002 seconds and Dualizer0.349 seconds. Those preparation stages total about1.54 seconds. The remaining roughly33.5 seconds cover certificate checks and lifecycle operations without finer markers. This rules out those constructor phases as the dominant cost for this test; it does not yet isolate one numeric certificate pass. The original30-second failure is retained, and the other13 exact tests and all integrated numerical captures remain pending.

## Independent source review

The call chain is `CertifiedPlanarWorkspace::prepare` to
`CertifiedPlanarReductionPlan::certificate`, then
`InvariantCertificatePlan::from_zero_polynomials` and `compile_polynomials`.
The last function applies Dualizer after building all scalar roots.
`InvariantCertificateWorkspace::check_batch_inner` evaluates the full graph;
its `inspect` function subsequently applies the requested constraint/component
selection. These are source facts, not a timing attribution for the unmarked
part of the diagnostic run.

The pinned `dependencies/symbolica` exposes expression-list construction before
Dualizer, but no public evaluator-root projection API. Its internal
`retain_vector_component` serves generated function bodies. Use the existing
expression-list API if a later measured optimization selects fewer cofactor
roots; do not copy that internal pruning implementation. Changing
`cpe_iterations` alone does not avoid Dualizer's unconditional final common-pair
pass, and the present direct-translation/zero-Horner scalar path already skips
scalar CPE.

The selected-chart five-root option is the conservative first candidate: fewer
structural builds, shared cofactor subexpressions, and the existing complete
ordered Taylor shape. The one-child option gives smaller graphs but requires
more cache entries and lane groups. Neither option has measured performance
evidence here. The unchanged frozen candidate's complete baseline qualification
comes first; per-check markers are needed before attributing the remaining
diagnostic time or choosing an optimization. Existing evidence is preserved.

# Certified planar pentagon prototype

This isolated implementation is pending numerical qualification and production integration. It does not yet change the ordinary `Workspace` dispatcher.

## Mathematical domain

For preserved Cartesian shifts, unit propagator powers, and D=4-2epsilon, let K contain the four columns p_i-p_0 and let f_i=(p_i-p_0)^2-m_i^2+m_0^2. The certificate proves det(K)=0 in every component of the requested Symbolica Taylor algebra. It separately proves that one matrix B, formed from three coordinate rows and f, has nonzero primal determinant. Consequently B is invertible in that Taylor algebra. Symbolica solves Bx=(0,0,0,1); the omitted coordinate equation follows from det(K)=0. With c_0=-sum(x_i), the identity sum(c_i D_i)=1 holds for all requested Taylor coefficients and for every Cartesian numerator.

Inputs are never projected. A nonzero rank determinant is outside this interface; unresolved predicates and absent regular constant-one charts are explicit failures. In particular a chart determinant with zero primal and a nonzero derivative is not accepted. Lower-rank and homogeneous-only families remain pending.

## Architecture

`CertifiedPlanarReductionPlan` stores immutable source polynomials and memoized structural charts. `CertifiedPlanarWorkspace<T>` owns exact-certificate scratch and numeric chart workspaces. It first checks the entire rank jet, then selects a proved nonzero chart primal, groups lanes by the omitted coordinate row, and calls the existing instruction-major reducer once per group. Failed samples never expose initialized zeros through `BatchResult::lane`.

The private `ReductionPlan::new_certified_planar` hook checks N=5, rank<=7, PV, preserved coordinate inputs, unit powers, D=4 and the chart range. Its fixed chart survives all Dual specializations; exact-zero profile dispatch is disabled. No unchecked plan is exposed by the public wrapper. The fixed chart returns directly to existing box/tensor recurrences, scalar-master batching, local Taylor stability checks and primal amplitude checks.

## Existing algebra and provenance

The chart matrix and constant-one solve are extracted from the existing qualified `PvCompiler::five_point_constant_relation` prototype. All determinants, linear solves, expression manipulation and Taylor lowering use Symbolica. Exact represented-input conversion and certified ball batch evaluation reuse `ExactZeroConstraintPlan` unchanged. No hand-written elimination or derivative algebra is introduced.

The three prior checks are recorded in `docs/research/highpoint-exceptional-audit.md`: Symbolica Numerica matrix APIs; matrix in-tree/API tests and existing IREGI scalar solves; FeynKit IntegralFamily partial_fraction and HEPKit tensor-reduction facilities. The current unit-power constant-one special case reuses the project’s existing Symbolica PV solver; FeynKit partial_fraction remains relevant for homogeneous transfer and repeated powers outside this initial domain.

## Qualification pending

The source includes tests for all 330 rank-seven moments and all four Laurent slots against an independently fixed box identity; seven input lanes with two chart groups and mixed failures; rotating-plane second/mixed Dual jets with MadLoop/multinomial metadata; transverse first/second/mixed jets; a nilpotent-only chart determinant; rounded-false-zero determinants; homogeneous-only families; empty/oversized buffers and constructor guards. Test presence is not a pass claim. Compiler manifests, exact dependency archive hashes and subsequent runtime logs are retained beside this note.

## Rebase boundary reviewed after generalized PV promotion

Production plan.rs now contains generalized PV dispatch, ScalarMethodUsage, compile_scalar_tensors, per-request compile_generalized_scalar calls, alias/leaf merging, and the generalized-IBP snapping-zero-image predicate. None may be replaced by the older isolated snapshot. Planar promotion must add only its field/private constructor/strict domain guard, variant forwarding, ordinary compile_pv option, and zero-profile exclusion. The ordinary compile_pv option is passed at its two current ordinary call sites. Generalized scalar compilation does not receive this option: the private planar constructor requires unit powers and dimension shift zero. In pv.rs, preserve the promoted compile_generalized_scalar method and append only the fixed-chart/refactored coordinate helper seams.

## Additional unqualified binary64 candidates

An independent source review proposed equal-mass Euclidean tetrahedra to investigate the current f64 box monitor warning without altering a threshold. Four spatial corners (-1,-1,-1), (1,1,-1), (1,-1,1), (-1,1,1), with a center fifth shift, m²=1 and mu=1, obey 4D_center−ΣD_corner=12. All corner-pair distances are −8, center-pair distances −3, and every box pinch has a regular Gram matrix. The simplex polynomial lies in [1,4]. Replacing the center by (1/4,0,0) gives coefficients [-3,-5,-5,-3,16]/47. These are test candidates, not measured stability or performance claims. The original failed mass-hierarchy fixture must remain visible.

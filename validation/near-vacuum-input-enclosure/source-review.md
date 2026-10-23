# Independent candidate-source review

Reviewer: `/root/pentagon_precision/e6_series_review`.
Reviewed source SHA256:
`79b07d47c00d9bf79675461f270148eda90bcaace94fc5376b27589bc2d0fb79`.
This review covers the private `source/near_vacuum.rs` input-enclosure extension,
not the later comparison driver, compiled binary or runtime results.

The reviewer found no concrete arithmetic or Rust API defect. The auxiliary
mass `M` is fixed at the exact represented nominal first mass; thus
`L=max(abs(Re(M)),abs(Im(M)))` remains a valid lower bound on its modulus while
physical masses vary independently in supplied rectangles. The component L1
suprema of the mass deviations and invariants conservatively majorize all
Taylor coefficients, including mixed components. Numerica uses outward
rational conversion, absolute interval norms and interval complex division.

Unordered or nominal-excluding rectangles fail containment before conversion.
The whole rectangle must have real invariants, positive real masses and
nonpositive imaginary masses; boundary mass jets have corresponding checks.
The existing rho and full-output-rectangle accuracy gates remain mandatory.
The optional point-only path retains its arithmetic but currently constructs
an unnecessary reference ball, a possible allocation cleanup only.

The caller must prove that supplied rectangles contain intended exact inputs;
containment of nominal points alone cannot prove that relationship. The driver
therefore checks both intended and nominal values explicitly. The reviewer
recommended a degree3 exact-vacuum control with zero nominal jets and first
mass-jet intervals `[-1,1]`; N2 must retain the nonzero third-order tail implied
by `D0=1/[6(1+u)^2]`. This control has been added to the separate driver.

No numerical runtime or compilation was performed by this reviewer. No E6
quadrature or general geometry certificate is implied.

## Independent driver review

Reviewer: `/root`, after the degree3 control was added and before compilation.
The full `input_enclosure_compare.rs` review found no concrete issue. It checked
all eight contour outputs for intended-plus-represented containment, exact
invariant compatibility, per-component accuracy budgets, enclosed coefficients
and Jacobian in the final contraction, the nine-lane rejection controls,
reversed and empty batches, and the zero-primal third-tail control.

The independent-oracle comparison does not accept intersection alone: the
numeric-output distance and the whole candidate-rectangle distance both
include the independent oracle radius and must fit the requested budget.
The review retains the one-point, exact-supplied-geometry scope. It does not
certify quadrature. This source review precedes metadata and runtime checks.

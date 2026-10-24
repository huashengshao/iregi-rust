# Restricted six-point API integration candidate

This is a source-only patch against the 44 production crate files recorded in
`baseline.json` at commit `1e06fc546d0c0fafe4b44d532900921c6a566731`.
No production source was changed, and no candidate build or numerical execution
has been performed.

Review `integration.patch`, then `source.json`. The patch adds the explicit
`SixPointReductionPlan` and `SixPointWorkspace<T>` API for N6, ranks zero through
three, unit powers, dimension shift zero, preserved Cartesian shifts, PV,
native IREGI normalization and raw components. Its contraction adapter uses
the existing Symbolica implementation. Public numerical Dual support and
higher ranks remain unavailable through this API.

Ordinary workspace construction keeps its previous execution policy. Retained
primal sensitivity operands and the five-point planar retry are enabled only
by the explicit six-point child path. Full-shape cofactor certification stays
private, and missing quadrature-error transport remains an explicit failure.
Certificate work is reported separately and retained before child errors.

`independent-review.json` and `independent-review-final.json` review the
non-owned integration slices and documentation. `execution-independent-review.json`
reviews the separately implemented execution policy. `package-audit.json`
independently verifies the complete archive, patch reconstruction, source
bindings and include fixtures. `math-reuse.json` records byte identity of eight
specific mathematical functions with the qualified private implementation;
it does not replace integrated testing.

`sources.tar.gz` contains 103 members: 59 candidate files (including all seven
compile-time fixtures) and the 44 production-baseline files. The archive and
patch are bound by `source.json`. The candidate directory is frozen. The
production baseline is retained separately so subsequent unrelated production
changes cannot silently alter this comparison.

`qualification-proposal.json` proposes bounded build, focused semantic tests,
ordinary default regression, public rank-three numerical comparison, and
rank-two lifecycle/contraction checks. It is not execution authorization.
The source-only capture drivers live beside the frozen candidate so their
review does not mutate the candidate archive. Actual scripts, complete
protocol pins and numerical comparators require review before execution.

Historical private rank-two and rank-three evidence supports this narrow
integration proposal. The separate rank-seven capsule records complete
128/256-bit diagnostic arrays but retains the failed original-reference gate.
Nothing in this source package upgrades that gate or establishes performance
parity, arbitrary complex-mass coverage or numerical Dual qualification.

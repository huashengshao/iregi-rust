# Certified planar generalized scalar vertical slice

This packet is source preparation. The preceding actual Cargo library build and
all eight new exact tests passed, with independent saved review, in
`target/certified-planar-generalized-scalar-qualification`. **No new example
build, scalar capture, mass jet, finite difference or parameter quadrature has
run for this packet.** The finite catalogue needs an exact independent source
review and root grant before execution. There is no performance claim.

The reusable example is
`crates/iregi-rust/examples/certified_planar_scalar.rs`. It uses the public
`CertifiedPlanarReductionPlan` and owned `CertifiedPlanarWorkspace<Float>` APIs.
It performs no recurrence or master calculation itself. Numerically supplied
inputs are built separately using Symbolica; first-order mass jets use its
expression differentiation and exact substitution, and the core propagates
those components using its existing Symbolica Dualizer. No polynomial, matrix,
Taylor or partial-fraction engine is added.

The fixed massive spatial fixture is the existing rank-three planar example:
`0,ex,ey,ez,ex+ey+ez`, squared masses `4,9,16,25,36`, and energy scale `mu=3`.
Every pair distance is nonpositive, so the defining parameter denominator is
at least four on the simplex. The eleven primary requests are h=1 unit powers,
all five individual dots at h=0 and all five at h=1. The ordinary h=0 unit
scalar is an additional derivative control. D=4+2h-2epsilon throughout.

Every output keeps the native order `[UV1,IR1,IR2,finite]`; nothing merges or
projects poles. On this finite domain the independent native finite answer is
`i*pi^(2+h)*J_h`. The ordinary unit control requests PV; the generalized scalars
request IBP and use the checked constant-one chart before Cayley. Actual
selected chart rows are exported from the public diagnostic strings, with
raw diagnostics retained. The compiled core guard rejects an unexpected
high-point master and the capture also requires `pentagon_box_rows==0`.
This is not a qualification of the genuine full-rank D6 quadrature backend.

## Numerical batches and independent checks

Each of the eleven scalar requests is captured at Float128 and Float256 with
requested accuracy80. A five-lane batch contains base, scale-by-two, nonplanar
invalid, spatially translated and repeated base rows. The invalid lane must
return its explicit status and `slots:null`; other lanes must remain successful.
Repeated rows must agree exactly; scale and translation identities are checked
before reference agreement. The squared natural unit is `(Q²)^d`, where
`Q²=max(1,|m_i²|,|(p_i-p_j)²|)` and `d=4+2h-2*sum(powers)`.

The two unit plans additionally capture a seven-lane first-order Dual batch:
five separate sample lanes seed the five mass derivatives, one same-primal
transverse time jet is invalid, and the first mass lane repeats. Each sample
has two Taylor components, in ordered shape `[[0],[1]]`. Samples and Taylor
components remain separate axes. Compare each derivative with the corresponding
one-dot scalar and direct oracle, using its mass dimension `d-2`. Derivatives
of the chart coefficients remain part of the core program.

The two unit plans also capture 21-lane finite-difference batches: base plus
both signs at steps2^-12 and2^-16 for each mass. Record coarse and fine centered
differences; compare Richardson `(256*fine-coarse)/255` with ordinary dot and
oracle values at1e-10. The finite-slot error against the ordinary dot must
improve, unless both coarse and fine errors are already below2^-80. Oracle
monotonicity is diagnostic because quadrature uncertainty may dominate it.
Finite differences have no2^-80 accuracy claim.

The capture records exact input values and numeric precisions before and after
reduction, and requires them unchanged. Signed-zero preservation is explicitly
not checked by these rational fixtures. Propagated output precision metadata
must be positive and no greater than working precision; equality is not
assumed and working precision is not an achieved-accuracy claim.

`oracle.py` reuses only the existing hash-pinned Gauss-Legendre rule from
`validation/shifted-pentagon/adjudicate.py`, through isolated AST extraction.
It never imports that module's old reference harness. One four-dimensional
pass computes all eleven defining integrals plus the unit D4 control. The
Rust example builds U/F, the simplex map, Jacobian and mass derivatives with
Symbolica using FeynKit's documented one-loop Symanzik convention. Three exact
numeric map/F/Jacobian witnesses are checked independently by the oracle,
which never interprets expression strings or uses a reduction result as an
integrand. See [ORACLE.md](ORACLE.md) for signs, normalization and limitations.

The proposed oracle orders12/16/20 at50/70/90 decimal working digits are an
initial finite catalogue. Working digits do not establish quadrature accuracy.
All successive normalized differences must pass1e-12; otherwise qualification
is inconclusive and no automatic finer order is run. Direct reducer/oracle
agreement uses1e-10. Float128/256 agreement separately uses2^-80. All thresholds
are squared exactly for squared-complex-error tests. Failed and missing runs
remain visible and cannot improve a score by exclusion.

## Finite execution proposal

`catalog-draft.json` specifies exact arguments and unmeasured proposed bounds:

| Stage | Cases | Total wall cap per case | Cleanup reserve |
|---|---:|---:|---:|
| Actual Cargo example build, j2 CPUs20/21 | 1 | 600s; child550s | 30s |
| Scalar Float128/256, paired CPUs20/21 | 22 | 180s | 20s |
| Unit mass jets, paired CPUs20/21 | 4 | 300s | 30s |
| Unit finite differences, paired CPUs20/21 | 4 | 180s | 20s |
| Oracle order12/digits50, CPU22 | 1 | 120s | 15s |
| Oracle order16/digits70, CPU22 | 1 | 240s | 20s |
| Oracle order20/digits90, CPU22 | 1 | 480s | 30s |

No native job is authorized by this table. After source is complete,
`prepare.py` freezes exact source/tool bindings into `catalog.json` without
building or evaluating anything. An independent review must bind its exact
hash. A root grant must bind both catalogue and review and list selected jobs.
`run.py JOB --grant GRANT.json --review REVIEW.json` then executes exactly one
case. Existing attempt directories are never overwritten and no automatic
retry, precision change or budget extension exists. A failed case does not
suppress independently granted cases. The orchestrator must keep at most two
native cases active and preserve the declared order and CPU assignments.

The build snapshots current root/core/master/facade/example source, compile
fixtures and three relevant Symbolica source/manifest leaves. It guards the
leased originals through artifact creation only, then releases main/Cargo.
Captures guard immutable snapshots and the frozen artifact, avoiding a new main
lease. These narrow guards are not a hermetic historical dependency/compiler
closure. The actual Cargo example is copied once into a readonly frozen file.
Per-job owned executable paths are readonly hardlinks to that same inode, with
both hashes checked before/after the job; they are honestly labelled shared
storage rather than independent byte copies. This avoids30 large duplicate
binaries. Each job still owns its process group, with waits clamped to its
absolute deadline. Future portable capsules omit all compiled aliases and keep
only their historical hashes. The Symbolica license is supplied externally;
only presence is recorded, never the literal value or license file.

`compare_saved.py` performs saved-only exact Fraction comparisons and complete
failure accounting. It does not import reducer/oracle producers, invoke native
code or infer accuracy from stable flags. Catalogue/grant/build/capture metadata
and raw output hashes remain separate from the mathematical comparisons.

## Source review and remaining work

The preliminary example mathematical/API reading found no blocker. Before any
build, a source-formatting mistake was caught: writing rustfmt's file-labelled
stdout had inserted a filename header. The bad source and reviewer limitation
are preserved under
`target/certified-planar-generalized-scalar-numeric-source-review`; the header
was removed, formatting now uses stdin, and the actual saved file was parsed.
The prior preliminary receipt is historical and does not admit the corrected
final packet. The added before/after input witness also needs final review.

Pending are final source/math/runner/comparator review, acceptance of concrete
finite bounds, one actual example build and all33 numerical/oracle cases,
independent saved-value review and compact durable preservation. This corpus
would still cover only these massive positive-F rank-zero families. Higher dots,
generalized tensors, other shifts, lower-span/homogeneous charts, massless or
complex endpoints, general Dual orders and performance remain outside its claim.

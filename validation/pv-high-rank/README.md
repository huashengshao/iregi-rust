# Original bubble rank-four discrepancy

For shifts `(0,0,0,0)`, `(0,1,0,0)`, squared masses `4,9`, scale `mu=3`,
the untouched original IREGI returns different finite coefficients for the raw
`qx^4` tensor component. Original IBP gives `45.43163000150602 i`, while original
PV and hybrid give `46.11123944517427 i`. All three calls report stability. Their
UV residues agree at `96.22864291062125 i`.

An independent Feynman-parameter integral confirms the IBP result. Write
`F(x)=4(1-x)+9x+x(1-x)`. After shifting the loop momentum and performing the
rotationally invariant Gaussian integral, the regulated integral is

```text
epsilon I(qx^4)/(i pi²) = (9/pi)^epsilon Gamma(1+epsilon)
  integral_0^1 dx F(x)^(-epsilon)
    [ 3 F(x)^2 / (4(epsilon-1)(epsilon-2))
      + 3 x² F(x)/(epsilon-1) + x^4 ].
```

The value at epsilon zero gives the UV coefficient; its derivative gives the
finite coefficient. Existing mpmath quadrature/differentiation at 50 and 80
decimal digits gives finite `45.43163000150589518329979586611707229587461094099688 i`.
This computation does not call either reduction implementation.

The original high-rank PV bubble branch in `pave_reduce.f90` uses quadratic roots
whose denominator appears to divide only the square-root term. This is a
candidate source diagnosis, separate from the independently established output
discrepancy. Reference files have not been changed. Rust PV validation uses
untouched original IBP for this family, and retains this counterexample.

Reproduce from the repository root:

```sh
source scripts/env.sh
python3 validation/pv-high-rank/parameter_check.py --write
```

The script records the original oracle values and numerical integration evidence
in `evidence.json`. mpmath is an optional reference-validation dependency only.

`high_point_coverage.py` records an additional rank-seven corpus in
`reference-coverage.json`. At the recorded box point, original PV and IBP both
claim stability but one finite coefficient differs by about 11.22 in native
units; the high-rank bubble branch also appears in its pinched subintegrals.
For the recorded five-, six-, and seven-point inputs, original PV reports
instability while original IBP reports stability. These failures remain visible;
original PV outputs marked unstable are never accepted as numerical answers.
The complete rank-seven Rust PV comparison therefore selects untouched original
IBP for its tensor targets and independently queries each scalar master.

Numerical comparison uses mass dimension `rank + 4 - 2N`: divide each component
by `Q^(rank+4-2N)`, where `Q²` is the largest absolute squared mass or pairwise
squared distance (with a lower bound of one in the fixture's units). The mixed
absolute/relative tolerance stays `1e-10`; the dimensional normalization ties
the comparison to the characteristic scale of each fixture. Real and imaginary components are both
checked. This report does not claim all rank-seven cases have passed until the
corresponding test run is recorded.

The original rank-seven axis corpus includes a lightlike internal bubble:
propagators 3 and 4 have shifts `(0,0,0,1)` and `(1,0,0,0)`, whose difference
has zero Minkowski square. This point is retained. The PV compiler treats such
subtopologies analytically instead of inverting their zero Gram matrix. For
`k` metric pairs and `b` factors of the relative momentum, the coefficient is
`(-1/2)^k b! J_(k+b)(1,1+b)`. Symbolica's scalar recurrence evaluates the
lightlike limit, and a lazy conditional selects it for symbolic input plans.
Unequal masses use exact partial fractions; equal nonzero masses use the
analytic joint mass/momentum jet; the fully scaleless branch keeps cancelling
UV/IR poles. The plan must supply the Dual algebra's total nilpotent degree
before compiling such jets. This description records the implementation;
validated coverage remains limited to the explicitly recorded test results.

`lightlike_feynman_parameters.py` provides a second independent parameter
integral for this analytic subtopology. It evaluates the raw `qx^r` moments,
`r=0..3`, for shift `(1,1,0,0)` and squared-mass pairs `(4,9)` and `(4,4)`.
The script checks exact UV residues, compares an explicit finite integrand to
differentiation of the regulated gamma integral, and checks convergence at
60 and 100 decimal digits. Results in both OneLoop and native IREGI
normalizations are committed in `lightlike-feynman-parameters.json`.

```sh
source scripts/env.sh
python3 validation/pv-high-rank/lightlike_feynman_parameters.py --write
```

The first full rank-seven sweep passes all Cartesian moments through four
propagators. At five propagators, the finite `q0^5 qz` component differs between
the two binary64 routes by `1.1701e-10`, exceeding the unchanged gate. The
`pv_precision_probe` example evaluates its exact Symbolica coefficient with
native scalar masters at 128 and 256 bits. Both converge to
`-0.0024383789354471229393924987498432753476200154688257048533643618299720430 i`.
The binary64 Rust expression differs by `2.23e-10`; original IREGI IBP differs
by `3.40e-10`. Both binary64 results therefore require an instability diagnostic
or precision rescue. This evidence does not qualify the failed family.

```sh
source scripts/env.sh
cargo run -p iregi-rust --example pv_precision_probe --offline
```

Inputs and outcomes are preserved in `precision-probe.json` and
`rust-coverage.json`. The full oracle records failures per topology and still
fails its gate after the remaining topologies have been examined.

For this component, the sum of absolute finite master terms is
`55375.72548164514891993307` in OneLoop units, corresponding to roughly 28 bits
of relative cancellation. Rounding the converged masters to binary64 and
retaining 256-bit reduction arithmetic gives only `3.11e-12` absolute error;
using binary64 arithmetic on those rounded masters gives `2.23e-11`. Both are
smaller than the error from original binary64 master values. This experiment
supports improving scalar-master precision and preserving cancellation
warnings, rather than loosening the comparison threshold.

An independent parameter integral now confirms that converged value.
`pentagon_simplex_oracle.py` derives the rank-six moment from Gaussian loop
integration and evaluates its smooth four-dimensional Feynman simplex with
SciPy's adaptive cubature. Two simplex coordinate maps give
`-0.002438378935447123 i` and `-0.0024383789354471227 i` in native units, with a
maximum reported absolute quadrature error of `2.77e-15`. The integral agrees
with the 256-bit reduction to binary64 rounding accuracy. This computation
does not call a reduction implementation or scalar-master library. It is an
independent accuracy check, not a certified interval bound or a benchmark.
The binary64 failures remain failures. Reproduce the retained
`pentagon-simplex-oracle.json` with:

```sh
source scripts/env.sh
python3 validation/pv-high-rank/pentagon_simplex_oracle.py --write
```

The exact PV suite additionally compares Symbolica Dualizer outputs with the
independent first derivative in the supplied squared invariant at the
lightlike point. The test uses jet order one and both mass configurations;
all four Laurent slots and primal/derivative components agree. This isolates
the PV coefficient jet from the separately qualified scalar-master backend.

The full oracle can be bounded to a single topology, rank, and routing variant:

```sh
IREGI_PV_ORACLE_N=6 IREGI_PV_ORACLE_RANK=7 IREGI_PV_ORACLE_VARIANT=base \
  cargo test -p iregi-rust --offline pv::tests::original_iregi_cartesian_moments \
  -- --exact --ignored --test-threads=1 --nocapture
```

The default variants are `base`, `translated`, `order_reversed`, and
`loop_reversed`; each filter also accepts a comma-separated list. Each run
retains inputs and all discrepancies in `oracle-runs/`. A failed comparison
does not stop the remaining selected cases or relax the acceptance tolerance.
An interrupted run retains its initial `started` record, so it cannot be
mistaken for a passing result.

The six-point base run through rank seven now completes all 330 moments. It
fails the unchanged binary64 gate in 430 component comparisons: 256 finite
imaginary components and 174 UV components. The maximum normalized mixed
error is `1.12176789154650173e-6`. All UV residues in this family vanish by
power counting; both numerical routes accumulate nonzero UV errors. Finite
coefficients require higher-precision adjudication before attribution. Inputs,
every discrepancy, and a matching precision-probe input are retained under
`oracle-runs/`. This family remains unqualified.

The independent six-point parameter integral now adjudicates its worst
component, `qx*qz^6`. Two SciPy GK21 simplex coordinate maps give native
finite `-0.004930291971105485 i`, with maximum reported absolute uncertainty
`6.07e-14` and a mapping difference of `4.34e-18`. Relative to this value,
the original IBP mixed error is `1.12e-6`; the Rust PV expression evaluated
with original Fortran binary64 masters has mixed error `1.95e-10`. Both fail
the fixed `1e-10` gate for this component. This does not measure the public
Rust workspace with its native scalar-master backend. The derivation,
exploratory quadrature failures, and unmodified library statuses remain in
`sixpoint-simplex-oracle.md` and `sixpoint-simplex-oracle.json`; the independent
script is `sixpoint_simplex_oracle.py`.

The complete six-point array now converges at 128 and 256 bits using exact
numeric-specialized PV coefficients and native oneloop scalar masters. Across
all 330 moments, four Laurent slots, and both complex components, the largest
dimensionally normalized mixed difference is `6.46e-29`. Against those values,
original binary64 IBP fails 566 component comparisons at the unchanged
`1e-10` gate, with maximum error `1.12e-6`. The retained Rust PV expressions
using original Fortran binary64 masters also fail: among the retained
disagreement rows, moment 214, `q0^5*qx^2`, has error `7.06e-8`. This is a
lower bound on that route's maximum error because its earlier record retained
only disagreements, rather than the complete Rust array. Neither result is a
public Rust Workspace evaluation or a performance measurement.

The precision input and complete results are
`oracle-runs/n6-base-precision-input.json` and
`oracle-runs/n6-base-precision.json`; the comparison is
`oracle-runs/n6-base-precision-adjudication.json`. The comparison validates the
embedded input snapshot, distinct precisions, full canonical tensor ordering,
all finite coefficients, and the reference stability flag before accepting
convergence. Missing or malformed data fail closed. Reproduce the comparison:

```sh
source scripts/env.sh
python3 validation/pv-high-rank/compare_precision_oracle.py \
  validation/pv-high-rank/oracle-runs/n6-base-rank7.json \
  validation/pv-high-rank/oracle-runs/n6-base-precision.json \
  validation/pv-high-rank/oracle-runs/n6-base-precision-adjudication.json
```

The exact suite now has ten passing checks. The newest constructs a
seven-point system whose initial denominator chart is singular at the sample
while an alternate chart is regular. It verifies the determinant boundary,
the complete denominator-polynomial identity, and its first Dual derivative.
This checks chart selection, not full seven-point tensor qualification.

The seven-point base rank-seven sweep reached its 90-second preparation
limit before numerical evaluation. Its retained record is
`oracle-runs/n7-base-rank7.json`; the timeout does not establish a numerical
failure or success. Routing variants remain unqualified.
The separately captured original-only array is
`oracle-runs/n7-base-reference-rank7.json`, reproduced by
`capture_sevenpoint_reference.py`. Original IBP reports stability but has 315
normalized UV components above `1e-10`, with maximum residue `0.085873`.
Every true UV pole vanishes because the maximum superficial degree is minus
three; the positive massive Feynman polynomial (`F >= 3.75`) also excludes IR
poles. Both original IR arrays are zero. These independent pole constraints
rule out the original UV results, without adjudicating its finite array.

The physical canonical `ggHHH` pentagon has a separate reference discrepancy:
untouched original IBP and PV disagree on `q0*qz^3`, while both claim stability.
The script `canonical_pentagon_threshold_probe.py` preserves a scan of the
original input threshold and a one-ULP routing perturbation. Making just one
almost-lightlike shift exactly lightlike changes the original IBP answer by
about `1.07e-6` in OneLoop units; the original PV answer barely changes. This
indicates sensitivity in the original IBP route, but does not by itself identify
the correct canonical answer. The threshold input controls on-shell snapping;
it does not vary the separate, compile-time recurrence threshold.
Original IBP also returns a native UV pole of `3.3369176606729786e-6 i` for this
component. The rank-four five-point integral has superficial degree minus two
and positive internal masses, so its UV and IR poles vanish. This independently
rules out that pole. Conversion of the erroneous UV residue into the OneLoop
finite convention explains why the finite discrepancy has different reported
magnitudes in the two conventions.

`crates/iregi-rust/examples/pv_physical_precision.rs` evaluates the same
canonical tensor using exact Symbolica PV coefficients and native scalar
masters at selected binary precisions. Its decimal inputs are embedded at
1024 bits and then converted to exact binary rationals, without passing through
binary64. It accepts `IREGI_PV_PHYSICAL_INPUT`, `IREGI_PV_PHYSICAL_MOMENTS`, and
`IREGI_PV_PHYSICAL_BITS`; the defaults are the canonical pentagon, moment 54,
and precisions 128 and 256. Both precisions now converge for moment 54, with
OneLoop finite value approximately
`(3.3474440772594743330 + 2.9254797223941252086 i) * 10^-13`; the UV residual
falls from `7.9e-31` to `2.3e-69`. This supports original PV/hybrid for this
component and rejects original IBP. The retained precision output is
`canonical-pentagon-precision.json`; `compare_canonical_pentagon.py` produces
`canonical-pentagon-adjudication.json` with decimal comparisons and source
hashes. This does not qualify a complete physical tensor or graph contraction.
A real-simplex quadrature without contour deformation is not
an independent oracle here, because the physical Feynman polynomial crosses
zero inside the simplex.

```sh
source scripts/env.sh
cargo run -p iregi-rust --example pv_physical_precision --offline \
  > validation/pv-high-rank/canonical-pentagon-precision.json
python3 validation/pv-high-rank/compare_canonical_pentagon.py
```

For a complete tensor array, set `IREGI_PV_PHYSICAL_MOMENTS=all`; use a separate
output file so the retained physical component evidence is not overwritten.
The optional `IREGI_PV_PHYSICAL_ALIASES=1` compiles a Symbolica alias DAG and
lowers it through the exact complex evaluator. This experimental preparation
path preserves the inline default and records its representation in the
output; it must pass the retained inline fixtures before being used as further
evidence.

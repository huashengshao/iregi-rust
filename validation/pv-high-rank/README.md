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

The exact PV suite additionally compares Symbolica Dualizer outputs with the
independent first derivative in the supplied squared invariant at the
lightlike point. The test uses jet order one and both mass configurations;
all four Laurent slots and primal/derivative components agree. This isolates
the PV coefficient jet from the separately qualified scalar-master backend.

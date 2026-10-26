# Public N6 rank-six mass finite differences

This saved-evidence child of the immutable [PV mixed-Dual capsule](../public-n6-affine-mixed-dual/README.md)
qualifies one fixed real massive N6/rank-six, unit-power, h=0 family. It checks
first and normalized second derivatives in the first squared mass against the
admitted original-IREGI dot/triple arrays and the qualified public Float256 AD
outputs. The ordinary reductions use Float384, requested accuracy160 and PV.

“FD5” here means **five total ordinary samples**: the central mass and positive/
negative perturbations at `h=2^-12` and `h=2^-18`. They form two three-point
central stencils sharing the center, not one fourth-order five-point stencil.
Existing Symbolica `Matrix.solve` generates the exact rational weights. The
second stencil extracts the second Taylor coefficient directly, including its
factorial normalization; no additional factor is applied afterward.

The frozen checker reproduces **6,720 comparison records** and **3,360 final
fine-step accuracy gates** at the unchanged normalized `1e-10` tolerance. The
coarse-step comparisons are diagnostic: their largest errors are about `2e-8`.
The fine-step maximum errors against the original-quad first/second derivatives
are approximately `4.63100e-12` and `5.76765e-12`.

All **420 resolved transitions** improve by at least the required factor16.
Another **1,260 transitions remain explicitly classified at the convergence
floor**; they do not establish resolved truncation convergence. The floor is
the maximum of 32 times the AD256/quad gap, 32 times the AD128/256 gap, and
`2^-80`. It classifies convergence only and does not relax any final `1e-10`
accuracy gate. A fixed nonpolynomial scalar finite first-mass witness resolves.

The native capture contains all five parent arrays (4,200 complex Laurent
slots), twenty actual N5 child rows and **25 complete native sensitivity
contexts**. Actual input subsets, output/context coupling and every child’s
explicit `KnownNoQuadrature` origin are checked. Zero error arrays never
substitute for missing origins or unavailable contexts. Inputs remain unchanged.

The initial exact-weight preparation fails on Symbolica’s undefined `0^0`
input. Its original receipt/log remain failed and contain no generated weights.
The reviewed repair supplies the degree-zero matrix row as literal one and
uses the same existing Symbolica solver. The successful weight-generation
receipt, source, exact residuals and actual wheel/import identity are retained.
This preparation performs matrix algebra only, with no integral reduction.

Run using Python’s standard library from any directory:

```sh
python3 -I -S -B validation/public-n6-rank6-mass-fd/check.py
```

The replay reconstructs the declared PV parent and exact new byte aliases,
checks the original 24-file/27-read evidence index and every new receipt input/
output association, then executes the unchanged independent saved-arithmetic
callback. Its complete numerical, observer and convergence report must equal
the original, apart from wrapper bookkeeping. No native module, Symbolica
solver, compiler or integral is executed during replay. Executable/native
identities and historical process cleanup remain saved metadata, not fresh
binary or process probes. No new source archive is needed; the actual
119-source observer context is inherited unchanged.

Ordinary finite differences and AD share integration software; the original
quad anchors retain their separate independent admission. This one direction
does not certify arbitrary derivatives, branches or kinematics, rigorous error
bounds, propagated-quadrature budgets, full feature acceptance or performance.
The separate sealed Hybrid/DoubleFloat capsule remains unchanged.

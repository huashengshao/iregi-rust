# Independent planar scalar defining-integral oracle

This directory contains **source preparation only**. No quadrature, Symbolica
evaluation, native driver or new integral has been run for this oracle. The
three-run catalogue below is proposed for a separately authorized finite
qualification. The earlier eight exact Rust tests establish compilation and
structural routing; they do not establish these numerical integrals.

The oracle calls no reducer, master evaluator or reference executable. It uses
the defining Feynman-parameter integral, rather than the known problematic
original standalone shifted-pentagon fallback. The separate Rust example owns
all symbolic preparation, using Symbolica and the documented FeynKit Symanzik
convention. This Python file performs only numerical integration and exact
checks of exported numerical sample values. It neither parses expressions nor
implements a polynomial, simplification, differentiation or matrix engine.

## Fixed inputs and mathematical convention

The metric is `(+---)` and denominators are `(q+p_i)^2-m_i²+i0`. In original
propagator order the shifts are

```text
p0=(0,0,0,0), p1=(0,1,0,0), p2=(0,0,1,0),
p3=(0,0,0,1), p4=(0,1,1,1).
m²=(4,9,16,25,36), mu=3.
```

All masses and components are exact integers. Every squared pair distance is
nonpositive. The oracle evaluates the numerical one-loop pair sum

```text
F(x) = sum_i x_i m_i² - sum_(i<j) x_i x_j (p_i-p_j)²,
sum_i x_i=1, x_i>=0.
```

Consequently `F>=4` throughout the simplex. These eleven requests are UV and IR
finite, including at its boundary. This particular massive domain justifies
zero oracle pole slots; it does not justify deleting any pole computed by the
reducer or asserting zero poles for massless or scaleless families.

For one loop FeynKit documents `U=det(M)` and `F=Q.adj(M).Q-U*J` when
`sum_i x_i D_i=k.M.k+2k.Q+J`. At `U=sum_i x_i=1` this gives the pair sum above.
The inspected source is
`../references/gammaloop_feynkit/crates/feynkit-graph/src/integrals/parametric.rs`,
SHA256 `40a60ad2be73f794256022de073ccb8177bc7c7691d88e0e7fea3df47303030a`.
The driver must obtain its expressions using these existing algebra APIs; no
new symbolic operation is needed here.

With the core normalization `J_h=pi^(-h) I_(4+2h-2epsilon)`, stripping the common
`i*pi²`, the finite defining integrals are

| Request | Integral on the four-dimensional simplex |
|---|---|
| h=0, unit powers (additional control) | `J0=-2 integral F^-3 dx` |
| h=1, unit powers | `J1=-integral F^-2 dx` |
| h=0, propagator i doubled | `dot0_i=+6 integral x_i F^-4 dx` |
| h=1, propagator i doubled | `dot1_i=+2 integral x_i F^-3 dx` |

The eleven requested outputs are h1-unit followed by the five h0 dots and five
h1 dots. The h0-unit control is accumulated simultaneously, making twelve
integrals per pass. The JSON `requests` array contains those eleven objects;
`h0_unit_control` additionally provides the ordinary scalar J and its four
native Laurent slots. The `finite_integrals` vector is ordered as J0-unit,
J1-unit, five h0 dots, five h1 dots. Dot signs are positive because
`d/d(m_i²) (q²-m_i²)^(-nu)=+nu (q²-m_i²)^(-nu-1)`.

All oracle outputs retain `[UVsingle, IRsingle, IRdouble, finite]`. On this
pole-free domain their native finite coefficient is `i*pi^(2+h)*J_h`; the real
part vanishes. The oracle computes pi at its own working precision. It does not
use a binary64 pi constant or rescale through an intermediate f64. Since poles
vanish, the native epsilon normalization creates no pole-to-finite mixing.

## Numerical map and existing quadrature reuse

Use the existing stick-breaking map from
`validation/shifted-pentagon/adjudicate.py::parameter_integrals`:

```text
x0=u
x1=(1-u)v
x2=(1-u)(1-v)w
x3=(1-u)(1-v)(1-w)z
x4=(1-u)(1-v)(1-w)(1-z)
Jacobian=(1-u)^3 (1-v)^2 (1-w)
```

The independent oracle uses the existing `unit_rule` helper through extraction
of its one hash-pinned AST function. It does **not** import or execute the
producer module, which imports the old reference-capture harness. Full source
SHA256 is `ef11c91cbdaf453733e8f710237245d647c79dbe5f619c514295d2654444a1ca`;
the extracted function source SHA256 is
`fd8e964d56aa8519d8ff7fb42083f184ace108a2d8da79016be0799cfb2d5480`.
The function delegates node/weight construction to mpmath's Gauss-Legendre
implementation. No local polynomial, root finder or quadrature rule is added.

All twelve integrands share one four-dimensional quadrature pass. The
denominator is the direct numerical pair sum from the original inputs, not an
expanded polynomial borrowed from the reduction. Common reciprocal powers and
weights are reused numerically. All physical integrands have fixed sign here;
ordinary accumulation is not exposed to a difference of large contributions.
The common-mass residual remains a cancellation diagnostic.

## Driver preparation interface

The example exports an `oracle_preparation` JSON object, either as a standalone
file or inside its complete result:

```json
{
  "schema_version": 1,
  "algebra_provider": "Symbolica",
  "cube_variable_order": ["u", "v", "w", "z"],
  "simplex_variable_order": ["x0", "x1", "x2", "x3", "x4"],
  "F_expression": "Symbolica expression string",
  "jacobian_expression": "Symbolica expression string",
  "evaluations": [
    {
      "cube": ["1/2", "1/3", "1/4", "1/5"],
      "simplex": ["five exact rational strings"],
      "F": "exact rational string",
      "jacobian": "exact rational string"
    }
  ]
}
```

The illustration shows one witness; the actual file must contain exactly
three, with cube coordinates

```text
(1/2,1/3,1/4,1/5)
(1/7,2/5,3/8,4/9)
(3/4,1/6,2/7,3/10).
```

The driver obtains F, the map and the Jacobian using Symbolica and its matrix
determinant API. At those three numerical points the oracle independently
checks the exported values with exact Fraction arithmetic. Expression strings
are provenance, never executable input to the oracle. These samples are useful
consistency witnesses; they do not prove symbolic polynomial equality or
independently certify every possible map input. Driver-side Symbolica identities
remain necessary.

## Proposed finite catalogue — all unrun

| ID | Order per axis | Decimal working digits | Four-dimensional nodes |
|---|---:|---:|---:|
| q12-d50 | 12 | 50 | 20,736 |
| q16-d70 | 16 | 70 | 65,536 |
| q20-d90 | 20 | 90 | 160,000 |

No automatic retry or finer order exists. Default invocation prints this
catalogue without importing mpmath or performing quadrature. After explicit
finite-run authorization, one capture can be made from the project directory:

```sh
source scripts/env.sh
python3 validation/certified-planar-generalized-scalar/oracle.py \
  --run q12-d50 --preparation-json CAPTURE_WITH_PREPARATION.json \
  --output NEW_ORACLE_CAPTURE.json
```

Each run needs an external finite wall/CPU deadline and saved provenance like
other validation jobs. Existing outputs are never overwritten. Exceptions
produce a failed capture with `requests=null`, never successful zero arrays.
The script uses no threads, native library subprocesses or reducer calls. The
order-20 grid has 160,000 denominators and twelve simultaneous accumulators;
Python arbitrary-precision arithmetic may still be costly. Its diagnostic wall
time is not a benchmark of TIRust.

Working digits control arithmetic, **not quadrature accuracy**. Compare all
eleven normalized finite coefficients between successive orders before claiming
agreement. A proposed empirical refinement target is `1e-12`, leaving a margin
under the `1e-10` reducer/oracle gate. Use the same dimensional mixed norm as
the reducer comparisons. For these scalar generalized requests set

```text
Q²=max(1, |m_i²|, |(p_i-p_j)²|),  d=4+2h-2*sum(powers),
error²=|actual-reference|² / max((Q²)^d, |reference|²).
```

Use native complex coefficients on both sides, and the finer-order oracle as
reference for refinement. The base fixture has Q²=36. Square the amplitude
thresholds exactly when testing squared errors. This definition retains the
shift/power mass dimension instead of applying the ordinary unit-power formula
to dotted outputs. Refinement differences are convergence observations,
not interval bounds. Any failed, incomplete or inconclusive order remains
visible. If order20 fails this gate, qualification remains inconclusive until
root approves a new finite catalogue; increasing digits alone cannot fix
insufficient quadrature order.

The separate Rust128/Rust256 `2^-80` gate measures numerical agreement of those
two reducer captures. It is not a promised error bound for this initial oracle
catalogue. Increasing quadrature order and arithmetic digits together also does
not isolate rounding error; a same-order higher-digit repeat, if necessary,
requires a separately approved finite run.

## Derivative, scaling and routing checks

Away from singularities the positive-F bound permits differentiation under the
integral. For each i and fixed h,

```text
d/d(m_i²) J_h(unit) = J_h(dot_i).
sum_i J_h1(dot_i) = -J_h0(unit).
```

Thus the direct dot integrals independently determine the five first mass
derivatives. Compare Rust Dual mass jets against both independently integrated
dots and the ordinary dotted captures. Retain derivatives of all chart
coefficients; differentiating only the child masters is insufficient. Taylor
first coefficients are derivatives, with no factorial at first order. A
same-primal p4.time transverse jet must be rejected by the exact full-Taylor
certificate. Sample lanes and derivative components remain separate dimensions.

The displayed common-mass residual shares all quadrature nodes and integrands;
it checks signs, weights and accumulation, but is **not** independent derivative
qualification. Its exact mathematical identity does not certify numerical
quadrature convergence.

Optional independent centered differences require separately captured shifted
unit integrals:

```text
D(h) = [J(m_i²+h)-J(m_i²-h)]/(2h)
h_coarse=2^-12, h_fine=2^-16
D_Richardson=(256 D(h_fine)-D(h_coarse))/255.
```

For a smooth function the coarse error is typically O(h²), so the coarse result
serves as a convergence witness and need not itself pass `1e-10`. Richardson
cancels its leading term; finer steps amplify independent integration or
rounding errors by approximately `1/h`. Compare against the direct dot oracle
and preserve disagreement. No `2^-80` finite-difference claim follows. The
optional `--mass-shifts` flag expresses the five exact squared-mass changes and
does not authorize extra captures. Fixed Gauss nodes may correlate errors
between shifted masses; report this limitation alongside differences.

For p→lambda*p, m²→lambda²*m² and mu→lambda*mu, the scalar outputs scale by
`lambda^(4+2h-2*sum(powers))`: h1-unit by lambda^-4, h0-dot by lambda^-8, and
h1-dot by lambda^-6. The additional h0-unit control scales by lambda^-6.
Optional `--scale` applies exact positive lambda to all those numerical inputs;
mass offsets are applied **before** scaling. A purely spatial common routing
translation leaves these scalar integrals unchanged. Compare the scaled and
translated Rust lanes against these identities, keeping each failed lane and
all four native Laurent slots visible.

No evidence here qualifies higher dots, tensor numerators, additional dimension
shifts, massless/complex endpoints, lower-rank or homogeneous-only planar charts,
physical graphs, general Dual orders or runtime performance.

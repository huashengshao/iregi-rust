# Private E6 N2 typed validation

This package extends the numerical qualification of the **unchanged private
N2 engine** in `validation/e6-direct-n2`. Its source is byte-identical, with
SHA-256 `9abf3dc1bbe6c2d2437f6e06d637593cd53a57767107635824b7c0d9560e0513`.
No production implementation, public API or default E6 dispatch changed.
The earlier 23-file package remains unchanged, including its independent
nonzero small-routing oracle. The accepted numerical fixtures here have
zero invariants and a common complex squared mass; deliberate guard cases
also exercise inputs outside that domain.

All ten bounded correctness groups passed. Each numeric type was exercised
with four and six mixed Taylor components, giving 130 primary physical
rows: 65 accepted rows, 320 accepted components and 65 expected rejections.

| Numeric type | Working bits | Requested bits | Component shapes |
| --- | ---: | ---: | --- |
| `f64` | 53 | 40 | 4 and 6 |
| Symbolica `DoubleFloat` | 106 | 80 | 4 and 6 |
| Symbolica `Float` | 128 | 80 | 4 and 6 |
| Symbolica `Float` | 256 | 128 | 4 and 6 |
| Symbolica `Float` | 384 | 128 | 4 and 6 |

The explicit absolute and relative budgets are both `2^-requested_bits`.
Acceptance compares squared error against the larger squared absolute or
relative budget for each component. The four-component shape is
`[00,10,01,11]`; the six-component shape is `[00,10,01,20,11,21]`.
Static `Mixed4`/`Mixed6` and dynamic `HyperDual` metadata prepare identical
Symbolica expressions, and actual component values round-trip through both
carriers. Workspaces store the underlying native numeric type, while
Symbolica's Dualizer implements Taylor arithmetic. This does not test a
`Workspace<StaticDual<T>>` interface.

The independent oracle is the exact common-mass identity
`-1/(24*M(x,y)^2)`. Symbolica differentiates it, divides by the appropriate
factorials and substitutes zero auxiliary variables. Existing Symbolica
rational-polynomial conversion and evaluation supply exact complex rational
coefficients. No polynomial, differentiation or integration engine was
implemented in the driver. For every accepted component, the numeric error
and the distance from the oracle to the entire candidate rectangle satisfy
the original budget, and the rectangle contains the exact oracle value.

The primary common mass is `M=2-i`; small linear mass jets include both real
and imaginary parts. The second accepted common mass is `3-i/2`. Fixtures
also cover a `2^-80` mass change, mixed 53-bit/working-precision `Float`
components, physical scale and scale-jet independence, and the exact vacuum.
The beyond-53-bit mass change is preserved by every type except `f64`, where
the expected input rounding is checked explicitly. Mixed-precision checks
certify the exact represented inputs, without claiming that a low-precision
input carries high-precision scientific information.

The large linear common-mass jets remain accepted for the four-component
shape, which needs only quadratic terms. For the six-component shape they
produce a nonzero exact `[21]` coefficient omitted by N2. All five numeric
groups reject that lane as `UncertifiedComponent(5)`, retain a positive
remainder bound despite zero primal deviation, and hide values. Other
expected rejections cover an upper-half-plane mass, the analytic-radius
limit, invalid physical scale, nonreal invariant, imaginary mass jets at a
real branch boundary and a zero mass.

The 13-row odd batch packs 12 scale-valid rows, seven of which reach the
series evaluation. Numeric, ball-enclosure and tail evaluators each receive
one instruction-major batch call. Estimated exported numeric
instruction/lane visits are 19166 for four components and 36295 for six;
these are program instruction counts multiplied by active lanes, rather
than a separate runtime trace. Empty and malformed inputs,
reversal, chunks, a fresh dynamic plan, singleton comparison and two
concurrent independent workspaces are checked. Rejected neighbors do not
alter successful results.

The first build failed before numerical execution because the validation
oracle selected an evaluator requiring a floating domain and two seed
expressions needed owned rational values. `attempt001-compile-failure`
retains its complete source, log, reviews and preservation inventory.
`oracle-api-correction.diff` records the narrowly reviewed replacement with
the existing exact rational-polynomial API and ownership-only clones.
Neither candidate arithmetic, fixtures nor accuracy budgets changed.

`build.json` and per-group records retain diagnostic observations, not
performance benchmarks. The corrected native-object build took about
6.88 seconds; whole validation groups took 1.62 to 2.13 seconds. There was
no isolated timing comparison or uncertainty estimate. The tested binary
is `target/e6-direct-n2-typed/validate`, SHA-256
`1e4ef5cdbcd2bfcaad1120256774907118c52adb86718fb44f9110c112994ccc`.

The 116 frozen dependency/native-library files are reused from
`target/e6-direct-n2/deps` and `native`; `closure-preparation.json` and
`upstream-preparation.json` retain the completed
`06706e2a1e4f0082889a53187c80bbe97803340f` Cargo provenance. Supervisors
verify source and closure hashes before and after every operation.
The build uses `opt-level=0`, no ThinLTO and no dependency rebuild.

From the project directory, the recorded supervisors are:

```sh
source scripts/env.sh
python3 target/e6-direct-n2-typed/build.py
source .local/symbolica-license.env
python3 target/e6-direct-n2-typed/run.py
```

They refuse to overwrite completed attempts. Reproduction requires a new
attempt directory and a matching frozen dependency closure. The untracked
license file is not included in this package. Exact commands and bounded
deadlines are preserved in the JSON records.

This checkpoint does not qualify unequal masses, nonzero routing for every
type, generalized powers or dimensions, N4 expansion, full contour geometry
or quadrature certification, or a public/default E6 path. Earlier production
E6 `Unstable` results remain unchanged.

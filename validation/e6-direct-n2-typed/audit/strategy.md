# Typed direct-E6 output audit

This strategy applies to the private N2 driver only. It requires no Rust build,
Symbolica invocation, polynomial engine, or change to existing qualification
bundles. The eventual Python checker uses exact rational arithmetic on emitted
scalar data and established common-mass identities.

## Source review before computation

Reviewed driver SHA256:
`6e33c98c01d9448e79a0ebe927aaf31804428bd1642fffa7db7e90b3865e3c97`.
The engine is byte-identical to the prior N2 checkpoint, SHA256
`9abf3dc1bbe6c2d2437f6e06d637593cd53a57767107635824b7c0d9560e0513`.
No material correctness issue was found in the reviewed driver.

The independent identity is prepared entirely with Symbolica. It differentiates
`-1/(24*m(x,y)^2)`, divides by each axis factorial, sets both formal variables
to zero, and evaluates over exact rational complex numbers reconstructed from
the represented numeric input. It explicitly requires zero invariant jets and
five identical complete mass jets before using that identity.

The first build failed before numerical execution because the generic
expression evaluator requires a real domain for this API and because two seed
expressions used unsupported borrowed-Rational division. The original source,
log, and prior review are preserved under `attempt001-compile-failure`. The
corrected driver retains the same Symbolica derivatives and factorials, then
uses the existing `d0_near_vacuum_oracle.rs::evaluate_exact` pattern: convert
the expression with Symbolica's Q/Z rational-polynomial API, verify the explicit
variable map, and evaluate numerator and denominator at exact complex-rational
inputs with Symbolica. A nonzero denominator is required. Seed operands are
cloned before division; their exact values are unchanged. This correction
changes neither the candidate engine nor fixtures, component shapes, numeric
types, acceptance tests, or requested budgets. This source review does not
assert that the corrected driver compiles or that numerical tests have run.

The driver compares both the numeric output and every point of the candidate
rectangle to the exact identity. It also requires the identity point to lie
inside the candidate rectangle. A later audit independently recomputes the
allowed budget and the output-to-rectangle distance, so the engine's recorded
budget does not establish its own validity.

The arbitrary-precision mixed-input row deliberately combines 53-bit and
workspace-precision objects. Its values are exact dyadic numbers at both
precisions. The unchanged engine reconstructs each represented input as an
exact rational, normalizes exactly, then converts at workspace precision.
Consequently this control checks object-precision propagation without claiming
additional scientific information about a low-precision measured input.

Static Mixed4/Mixed6 and dynamic HyperDual carriers use the same explicitly
checked shapes and component arrays. Prepared plans must have identical shapes
and integrated expressions. These are metadata and transport checks; numerical
derivative arithmetic continues through Symbolica's Dualizer. Components remain
separate from the thirteen sample rows.

Two independently instantiated workspaces run in separate scoped threads over
forward and reversed inputs. Each owns its evaluators, receives immutable input
and accuracy references, and is joined before comparison with the primary
result. The driver also checks fresh singleton, chunked, reversed, empty and
malformed-input evaluations. These controls are compiled assertions plus
successful execution; their full result arrays are not separately serialized.

## Expected groups and rows

There are ten groups: f64, DoubleFloat, Float128, Float256 and Float384, each
with Mixed4 and Mixed6. Requested bits stay at 40, 80, 80, 128 and 128
respectively. Working precision is 53, 106, 128, 256 and 384 bits.

Mixed4 uses `00,10,01,11`; Mixed6 uses `00,10,01,20,11,21`. Every group has
thirteen physical rows. Positive-scale validation packs twelve rows, and the
analytic input guards leave seven active rows. Primary numeric, enclosure and
tail evaluators each run once. The emitted instruction-lane visit field is an
estimate derived from the prepared instruction count, not a hardware trace.

Rows 0,1,2,4,8,10 must succeed in both shapes. Row 6 also succeeds for Mixed4;
its complete degree-two moment fits N2. Mixed6 row 6 must fail component 5
with zero primal rho and a positive omitted mixed cubic tail. Rows 3,7,9,11,12
fail physical-input validation; row 5 is outside the analytic radius. Every
failed row must expose `values: null`.

Across all groups this gives 130 physical rows, 65 successes, 65 rejected rows,
and 320 independently checked successful components. Chunk counters should be
`packed=5, active=4` for rows 0..5 and `packed=7, active=3` for rows 5..13.

## Exact recorded-input checks

Bind the runtime, source manifest, binary, build, prepared dependency hashes,
and the existing N2 qualification. Verify every emitted physical row has
`16*components` entries and each numeric field parses as an exact rational.

Reconstruct the fixture scalars directly: common primal masses `2-i`, row-4
mass `3-i/2`, seeds `a=2^-64*(1+i/2)` and `b=2^-64*(-1/2+i)`, and the
large-seed row with the corresponding unit-scale a,b. Row 2's real mass shift
is zero relative to baseline in f64 and exactly `2^-80` in all other types.
Check both each mass value and all five repeated copies. The other deliberate
faults, zero jets, scale changes, and scale jet are also fully serialized.

For arbitrary-precision row 10, verify that both 53-bit and working-bit
components are present while exact represented values agree with row 0.
For each accepted row, require ten complete zero invariant jets, five equal
mass jets and zero unseeded higher mass components before applying the scalar
identity. No identity is applied outside those preconditions.

For `m=M+a*x+b*y`, the established scalar coefficient identities are:

| Component | Exact value |
| --- | --- |
| 00 | `-1/(24*M^2)` |
| 10 | `a/(12*M^3)` |
| 01 | `b/(12*M^3)` |
| 20 | `-a^2/(8*M^4)` |
| 11 | `-a*b/(4*M^4)` |
| 21 | `a^2*b/(2*M^5)` |

Evaluate these finite scalar formulas using rational real and imaginary parts,
not a polynomial or series implementation. Check that every emitted oracle
center equals the independently evaluated scalar identity. For Mixed6 row 6,
verify its independent mixed cubic is nonzero and lies inside the recorded
rejected component rectangle; the first budget violation must be component 5.

## Component accuracy

For each successful component, recompute the exact squared numeric error, the
farthest candidate-rectangle distance to the identity, and the farthest
candidate-rectangle distance to the returned value. All three must be bounded
by `2^(-2*requested_bits)*max(1,abs(returned)^2)`. Recompute and match every
recorded error field; require ordered endpoints, nonnegative truncation, and
exact identity containment. No budget is changed during audit.

Require complete row equality for rows 0 and 1 (scale independence), and for
rows 0 and 10 (mixed object precision). Compare the represented physical
inputs as well, excluding the explicit scale changes for row 1. Verify the
above-53-bit mass distinction propagates to the finite primal in every type
except f64.

## Float256 to Float384 convergence

Pair groups by shape and rows by index, requiring identical represented
physical inputs and exact identity centers. Requested accuracy must remain
128 bits in both groups. For each successful component and coordinate compute

    rounding_width = upper - lower - 2*truncation.

Check this value against the recorded rounding width and require it to be
nonnegative. Zero widths may remain zero. Positive Float256 rounding widths
must strictly decrease at Float384; report exact ratios where both are
positive, and count transitions to exact zero separately. Require that at
least one positive width is compared in each shape. Preserve any failure as
inconclusive or failed convergence rather than altering an accuracy budget.

The comparison covers 64 successful components across the two shapes, with
128 coordinate widths. Fixed N2 truncation can dominate total uncertainty,
especially for omitted cubic components. This check establishes convergence
of arithmetic enclosure widths; it does not claim that a fixed truncation
floor or an exactly zero retained cubic disappears with higher precision.

# Private non-dyadic physical-input enclosure experiment

This is separate from the explicit certified-master API promotion. Its new
side-input rectangle method is not applied to production. The existing public
API certifies its represented inputs, and this experiment investigates caller
uncertainty before that API boundary.

At the exact contour point `x=2/5`, `t=x/(1-x)*(1-i)=2/3*(1-i)`, the shifted
mass is `5/3-2/3*i`. Float256 cannot represent these values exactly. A Symbolica
program computes the contour shift, common shifted mass, Jacobian and five
coefficient updates in Float256 and Numerica ComplexBall256, using the same
instructions. It uses exact unshifted Cayley coefficients from the independent
oracle; geometry rounding is outside this experiment. Every output enclosure
must contain the intended exact rational output and its represented numeric
output. The physical-input rectangle method retains its own containment check.

The candidate freezes an auxiliary `M` at the represented first primal mass.
All physical masses and their Taylor components still vary inside the supplied
rectangles. `L=max(abs(Re(M)),abs(Im(M)))` remains a fixed exact lower bound on
`|M|`. Numerica subtraction/division carries physical rectangles through the
normalized arguments. Their component L1 suprema majorize the complete Taylor
series tail, including all mass-jet components. Branch checks cover the whole
rectangle. The unchanged acceptance rule checks worst-corner distance to the
returned number, with requested128-bit absolute/relative budgets.

The driver batches five boxes with four rejection controls, checks an
independent reversed workspace and an empty batch, and contracts full box
rectangles with enclosed coefficient updates and contour Jacobian. A separate
exact-vacuum degree3 uncertainty control places all represented mass jets at
zero but encloses first mass jets in `[-1,1]`. N2 must reject and retain a third
component tail at least `2/3`, from the independent common-mass identity
`D0=1/[6(1+u)^2]`.

## Existing algebra facilities checked

1. Numerica source: `dependencies/symbolica/lib/numerica/src/domains/float/interval.rs`
   supplies `ComplexBall`, directed `RealBall::from_rational_bounds`, absolute
   interval `Real::norm`, and interval arithmetic. No interval implementation
   or polynomial algebra is added here.
2. Existing tests cover rational input enclosures, nonzero radii, complex
   multiplication, quotient and inverse containment in that file. The core
   `crates/iregi-rust/src/invariant_certificate.rs` already maps the same
   Symbolica program to batch ComplexBall evaluation.
3. A source search for `ComplexBall`, `RealBall` and `from_rational_bounds`
   in FeynKit/gammaloop, `crates/iregi-prepare`, and
   `dependencies/feynkit-integrals` found no additional facility. This uses
   the existing Numerica one rather than introducing an alternative.

Independent source review found the fixed-anchor and all-component majorant
construction sound, with no concrete false-Success path. The bounded private run passed all five box values, the contraction and mapped
integrand at working256/requested128 bits. All rejection, reversal, empty-batch
and degree3 tail controls passed. The caller must establish that supplied
rectangles contain intended exact inputs; the API cannot infer that relationship
from a numeric point. Independent audits passed982oracle checks,366candidate
numerical checks and936candidate provenance checks, with zero failures. The
compact final receipt is `qualification.json`; detailed checks stay in `oracle/`.

Scope remains one private primal contour point plus a derivative rejection
control. This does not certify Gauss nodes, weights, geometry solves,
quadrature truncation, production E6 results, or performance.


## Recorded attempts

The original standalone metadata check omitted a trait import; its failure is
retained under `attempt001-metadata-failure`. The next link was interrupted at
the user's pause request (`attempt002-user-interrupted`). A resumed link
encountered shared filesystem exhaustion; no executable or link exit record was
available, and this is retained as infrastructure failure under
`attempt003-storage-failure`. None of those attempts ran the candidate.

The successful retry used identical Rust source to the user-interrupted
attempt. Its compiler pause for the public API build is logged in
`build-control-events.jsonl`. The run uses the frozen completed6b24 release
dependency closure, checking all870files before/after. Durations are diagnostic,
not benchmark timings. The exact oracle was reused without rerunning it.

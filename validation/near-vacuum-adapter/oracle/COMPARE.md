# Private five-pinch adapter comparison

`five_pinch_compare.rs` consumes the exact oracle `output.json` documented in
README.md and evaluates the five D0 rows together through the isolated
`AccuracyMasterEvaluator`. It requires a finite certificate for every lane at
working256/requested128, with explicit absolute and relative budgets 2^-128.
It checks exact preservation of all 55 complex inputs, native zero poles, the
formula selection, and all component certificates. It never permits ordinary
uncertified fallback for this experiment.

For each box, the comparison checks the numerical result and the entire
candidate rectangle against the independent exact oracle center and remainder.
It recomputes the certificate's maximum squared distance and allowed budget
using Symbolica Rational arithmetic. Candidate and oracle rectangles must
intersect. Oracle-rectangle containment is recorded as an additional
observation, not used as a necessary mathematical condition.

The contraction expression sum_i C_i*D0_i is prepared by Symbolica once and
mapped to both Float256 and ComplexBall256. Each exact Matrix-derived C_i
gets a point enclosure, which covers its numeric conversion; every D0 gets
its full certified rectangle including omitted-series tails. Thus the final
ball includes coefficient conversion, box errors, multiplications, and the
sum's roundoff for these fixed exact coefficients. The numerical contraction
and the entire resulting rectangle must agree with the independently
integrated J5^D4 oracle within the unchanged requested128 budget.

This is the exact x=1/2 contour probe. It deliberately does not execute the
production geometry solve or the finite-precision construction of t and m+t.
No upstream contour/shift uncertainty, algebraic Gauss root or weight error,
quadrature truncation, public E6 execution, Dual convergence, or performance
qualification is covered. Zero and missing certificates remain distinct.

Exit codes: 0 all comparisons pass; 2 adapter rejects a selected lane and
hides values; 3 an error bound does not certify agreement; 1 malformed inputs
or structural failure. The saved build/run manifests bind source, input JSON,
private adapter source/archive, library dependencies, logs and executable.

# Independent real-part zero identity for the retained N6 fixture

This is an analytic domain check plus saved-data diagnostics. It does not change
any output, project away real parts, replace the failed complete-array reference
gate, certify imaginary coefficients, or identify a numerical failure's cause.

The premise is valid for this fixture: native IREGI normalization, six ordinary
unit-power propagators, dimension shift zero, real Cartesian numerator and routing,
real positive squared masses, positive real scale, and the Feynman prescription.
IREGI's raw tensor measure is given in Appendix C.1, Eq. (C.1) of
[Alwall et al.](https://arxiv.org/html/1405.0301v2#A3.SS1). The standard parameter
combination/completion of the square and Wick rotation are independently stated
in Eqs. (3)–(6) of
[Bern, Dixon and Kosower](https://cds.cern.ch/record/247616/files/9212308.pdf).

For simplex coordinates x_i, let P=sum_i x_i p_i. Completing the square produces
`(q+P)^2 - F + i0`, with
`F=sum_i x_i m_i² - Var_x(p^0) + sum_(a=1..3) Var_x(p^a)`.
The retained masses have minimum one, every time coordinate lies in [0,1/2], and
all spatial coordinates are real. The elementary bound on a weighted variance
of values in [a,b] is `(b-a)²/4`: it follows from
`E[(X-a)(b-X)] >= 0` and `(E[X]-a)(b-E[X]) <= (b-a)²/4`.
Consequently **F >= 1 - 1/16 = 15/16** throughout the closed simplex.
This strict bound prevents a physical cut or endpoint infrared singularity at
this point and permits the usual Feynman-contour deformation.

Now shift k=q+P. Real P leaves every numerator expansion coefficient real.
Under Wick rotation `k^0=i k_E^0`, `d^D k=i d^D k_E`. A surviving Euclidean
angular moment has each coordinate to an even power; odd angular moments
vanish. Thus every surviving time-coordinate factor is `i^(2j)=(-1)^j`, a real
sign. Denominators, real shifts, metric factors and radial gamma-function
coefficients are real for real epsilon near zero, with analytic continuation
where needed. The sole common phase is the measure's factor i. Expanding in
epsilon therefore gives **Re I_alpha^(pole/finite)=0** for every real Cartesian
monomial in this domain, including odd total ranks (their shifted even terms
still have real coefficients). This conclusion does not depend on a PV/IBP
recurrence or a scalar-master implementation.

The convention check is independent of the above argument: original
`mis_warp.f90` declares `ipi2 = (0, pi²)` and its A/B/C/D scalar wrappers use
real Laurent-normalization constants. `IREGI4ML5_interface.f90:77,158–160`
removes this factor with `1/(i*pi²)`; our reference driver sets
`ML5_CONVENTION=true` solely for unweighted components and does not call that
adapter. TIRust's copied `convention.rs:83–102` applies i*pi² times a Laurent
map with real gamma/log(pi)/pi² coefficients. Tensor weights and odd-rank
MadLoop signs are real, but the present data specifically use native Components.

For these requested degrees, superficial UV degree is `r+4-2N=r-8<0` for
r=0..7. Together with F>0, all three pole slots actually vanish, a stronger
identity already checked separately. Here the new independent observable is
`abs(Re output) / S`, where `S=Q^(r-8)` and the frozen dimensional scale is Q=2.
We also record the same real-part residual with the original full-array
normalizer `max(S,abs(original_complex))`, solely to relate it to that failed
gate. Comparing these residuals to 1e-10 is an additional zero-identity check;
it says nothing about the remaining imaginary-part accuracy or all-array
convergence. No real part is overwritten or discarded.

Sources and the exact fixture are hash-bound by `phase-zero-diagnostics.json`.
No symbolic or numerical kernel was evaluated to establish this premise.

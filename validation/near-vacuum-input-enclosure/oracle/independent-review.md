# Independent source and mathematical review

Reviewer: `/root/pentagon_precision/nondyadic_oracle/nondyadic_bound_review`.
Scope: read-only source review and analytic bounds. No Rust builds, numerical
oracle execution, or edits were performed by the reviewer.

Final source SHA256 independently confirmed:
`a12d96533f48983bd38f5835c2085dfcb8579707363371385aabc8df33460081`.

No blocking mathematical, ownership, or API issue was identified in adapting
the existing independent oracle to x=2/5. Symbolica derives and exactly checks
t=(2/3)(1-i), M=5/3-(2/3)i, and dt/dx=(25/9)(1-i).

The routing identity holds on every face, including pinch 0. For eta=2^-64,
the real part of the Symanzik denominator obeys Re(F)>=5/3-eta>0, while
Im(F)=-2/3. The Taylor expansion therefore stays in the intended analytic
domain. Taking L=5/3 and r=(3/5)*2^-64<1/4, the exact tail formulas give

    R5 = r^5*(21-35*r+15*r^2)/(12*L^3*(1-r)^3)
       < (27216/390625)*2^-320 < 2^-320,

    Rbox = r^9*(10-9*r)/(6*L^2*(1-r)^2)
         < (524880/48828125)*2^-576 < 2^-582.

Thus inclusive orders N4 and N8 remain sufficient with the original strict
remainder threshold. No acceptance threshold was weakened.

The Cayley coefficients retain B=-b0, b0=1/(2+eta), and b1..4=-b0/2. At the
shifted point C0=1/(2*M+eta), C1..4=-C0/2. With a=10/3+eta and b=4/3,
(a+b)/(a^2+b^2)<=21/58 bounds |C0|_1. Hence

    Rcontraction <= (63/58)*Rbox < 2^-581,
    Rmapped <= (175/29)*Rbox < 2^-579.

The multiplier's complex norm upper bound is 50/9. The reviewer suggested
making the mapped-radius bound executable; the source now separately asserts
mapped_radius<2^-320 and records this guarantee only after that assertion.

This review qualifies the source derivation and bounds only. Exact oracle
execution, numerical input-enclosure agreement, and E6 quadrature remain
separate validation steps.

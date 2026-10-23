# Exact non-dyadic five-pinch contour oracle

This source is prepared for private validation. It has not been built or run
unless a separate build/run manifest records that execution. The target source
and this directory's durable source are byte-identical. Existing dyadic-oracle
sources and evidence are preserved.

The independent oracle links Symbolica and serde_json only. It calls neither
iregi reduction nor oneloopmaster. Routing polynomials, the Cayley matrix solve,
contour differentiation, rational-function evaluation, series construction,
Jacobian calculation, and polynomial integration all use Symbolica.

The fixture remains q0=0, qi=delta*e_(i-1), metric (+---), delta=2^-32,
eta=2^-64, original squared masses 1, and mu_squared=1. The exact contour probe
is now x=2/5. For t(x)=(1-i)*x/(1-x), Symbolica derives and exactly evaluates

    t = (2/3)(1-i),
    M = 1+t = 5/3-(2/3)i,
    dt/dx = (25/9)(1-i).

Unlike the previous x=1/2 fixture, the contour point, shifted mass, and mapped
weight are non-dyadic. Their exact rational values are the reference inputs;
rounding them first would remove the input-enclosure test. This point carries
no Gauss abscissa or quadrature weight.

For each pinch, all six distances follow from the retained original routing.
The simplex polynomial is F=M-eta*Q, with
Q=sum_(i<j) sij_unit*x_i*x_j. Symbolica verifies the equivalent expression
Q=sum_(retained original i=1..4) sigma_i*x_i*(1-x_i) after stick breaking.
Consequently |Q|<=sum_(i>=1)x_i<=1 on every face, including the full pentagon.

Each D0=integral_Delta3 F^-2 uses a Symbolica series through order eight and
exact polynomial integration over the mapped cube. Independently,
J5^D4=-2*integral_Delta4 F^-3 uses order four and four cube coordinates. The
simplex volumes are checked as 1/6 and 1/24. Their native UV/IR poles vanish
in this massive analytic domain; this oracle reports finite primals.

The rigorous absolute remainder is

    |normalization| * volume(Delta) * T_(p,N)(r) / L^p,

where L=5/3<=|M|, r=eta/L=(3/5)*2^-64, and T_(p,N) is the positive omitted
tail of (1-r)^-p. Symbolica constructs this tail by series and exact
subtraction. No hand-coded polynomial or Dirichlet integration engine is used.
All remainders are exact rationals, and the existing strict assertion
radius<2^-320 is retained.

Order four is sufficient for the direct pentagon at this new point. Its tail
is r^5*(21-35r+15r^2)/(1-r)^3. Because 0<r<1/4, the numerator is at most 21
and (1-r)^-3<64/27. Therefore the pentagon radius is strictly smaller than

    (27216/390625)*2^-320 < 2^-320.

The box tail is r^9*(10-9r)/(1-r)^2. The corresponding bound is strictly
smaller than

    (524880/48828125)*2^-576 < 2^-320.

These coarse inequalities explain why neither series order nor acceptance
threshold needs changing. The executable retains its exact-rational radius
checks. The one-million-term cap applies to the retained expanded polynomial;
the parent must also bound runtime and memory during symbolic construction.

Geometry is independent of the production external-Gram solve. Symbolica
inverts the full unshifted Cayley matrix R_ij=eta*sij_unit-2 and checks R*b=1,
B=-1/(2+eta), b0=1/(2+eta), and b1..4=-b0/2. It evaluates
C_i=b_i/(1-2*t*B), then checks (R-2*t*ones_matrix)*C=1 directly. Thus
C0=1/(2+eta+2*t) and C1..4=-C0/2 at the exact non-dyadic t.

Symbolica evaluates the five-box contraction at exact series centers. Its
radius is sum_i (abs(Re(C_i))+abs(Im(C_i)))*box_radius_i. This interval must
overlap the independently integrated direct-pentagon interval. The mapped
integrand uses the exact dt/dx above and the conservative norm bound 50/9.
Writing C0=1/(a-i*b), with a=10/3+eta and b=4/3, gives
|C0|_1=(a+b)/(a^2+b^2)<=21/58. Since C1..4=-C0/2, the contraction radius
is at most (63/58)*box_radius and the mapped radius at most
(175/29)*box_radius. The source separately asserts the mapped radius is
strictly below 2^-320.
JSON records each exact input, routing, integrated polynomial, center, radius,
geometry coefficient, contour map, derivative, and normalization.

The output is an independent reference for a later input-enclosure comparison.
It does not by itself qualify the numerical enclosure implementation, Dual
derivatives, production E6 quadrature, Gauss-node or weight construction, or
performance.

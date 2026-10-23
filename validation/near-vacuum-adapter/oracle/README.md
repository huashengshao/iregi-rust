# Exact five-pinch contour-point oracle

This standalone, target-only validation source links Symbolica and serde_json.
It calls neither iregi reduction nor oneloopmaster. It has not been run unless
an accompanying runtime manifest explicitly records that execution.

The fixture is q0=0, qi=delta*e_(i-1), metric (+---), delta=2^-32,
eta=delta^2=2^-64, original squared masses 1, and mu_squared=1.
At the exact contour probe x=1/2 with scale=slope=1, t=1-i,
all shifted squared masses are M=2-i, and dt/dx=4-4i.
This point is not a Gauss abscissa and carries no quadrature weight.

For each pinch, the code derives all six distances from the retained original
routing vectors. The simplex polynomial is F=M-eta*Q, where
Q=sum_(i<j) sij_unit*x_i*x_j. Symbolica verifies the equivalent expression
Q=sum_(original i=1..4 retained) sigma_i*x_i*(1-x_i) after stick breaking.
Thus |Q|<=sum_(i>=1) x_i<=1 on every face, including the full pentagon.

The five D0 integrals are +integral_Delta3 F^-2. Each is expanded through
eta/M order eight with Symbolica.series, mapped to a three-dimensional cube
with a Symbolica Matrix-derived Jacobian, and integrated exactly using
Symbolica polynomial antiderivatives and endpoint replacement. Independently,
the code integrates J5^D4=-2*integral_Delta4 F^-3 through order four using
four cube coordinates. The leading constants are checked to be 1/6 and
-1/12 before restoring M^-2 and M^-3. All native UV/IR pole components vanish
in this massive analytic domain; this source reports only the finite primals.

For denominator power p, let T_(p,N)(r) be the positive omitted Taylor tail
of (1-r)^-p, constructed by Symbolica series and exact subtraction. Since
L=2<=|M| and r=eta/L, an absolute complex remainder is

    |normalization| * volume(Delta) * T_(p,N)(r) / L^p.

This is T_(2,8)(r)/24 for each box and T_(3,4)(r)/96 for the direct pentagon.
All radii are computed as exact rationals and asserted smaller than 2^-320;
the direct pentagon order four is therefore sufficient for requested128 and
for a much stricter absolute comparison. No floating-point conversion enters
the calculation. The implemented one-million-term cap applies to the retained
expanded parameter polynomial; a parent-enforced time/memory bound is still
needed around symbolic construction.

Geometry is derived independently of the production Gram solve. Symbolica
Matrix<Q> inverts the full unshifted Cayley matrix R_ij=eta*sij_unit-2,
then multiplies it by the ones vector. The result is checked against R*b=1,
B=-1/(2+eta), b0=1/(2+eta), and b1..4=-b0/2. Symbolica rational-function
evaluation computes C_i=b_i/(1-2*t*B), and the full shifted relation
(R-2*t*ones_matrix)*C=1 is checked directly.

Symbolica evaluates the contraction sum_i C_i D0_i at the five exact series
centers. The contraction radius is sum_i |C_i|_1*box_radius_i, using
|C_i|_1=|Re C_i|+|Im C_i| as a conservative complex-norm upper bound. Its
center must differ from the independently integrated J5^D4 center by no more
than the sum of their radii. The mapped integrand multiplies the contraction
by 4-4i and bounds its error with the norm upper bound 8.

JSON output includes every exact input, pinched routing, integrated polynomial,
center, radius, geometry coefficient, and normalization. This is primal-only
reference preparation. It does not qualify production arithmetic, general
kinematics, Dual derivatives, E6 quadrature, or performance.

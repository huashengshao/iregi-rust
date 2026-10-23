# Source-only independent E6 oracle expansion recommendation

Status: design only; no build, Symbolica execution, quadrature, or numerical trial was performed. Existing frozen packages and the private N2 engine are unchanged. A 20–120 second numerical allowance is a proposed cap, not a measured runtime prediction.

## Smallest useful staged experiment

Keep the existing Mixed6 shape `00,10,01,20,11,21`, N2 candidate, and represented-input contract. Start with one Float256 group, not all ten typed groups. Use two successful physical rows and the existing degree-three rejection control:

1. **Exact vacuum derivative row:** zero primal invariants and equal primal squared masses, with independent invariant jets, unequal mass jets, and nonzero direct `20`, `11`, and `21` input components. Adapt `crates/iregi-rust/examples/support/d0_near_vacuum_oracle.rs:570` to five simplex parameters, ten lexicographically ordered invariants, five masses, and the E6 normalization `-integral_Delta4 F^-2`, volume `1/24`. Differentiate the *unexpanded physical integrand* with Symbolica, set the jet coordinates to zero, and integrate the remaining exact parameter polynomials. Every requested coefficient has remainder radius exactly zero. This tests new derivative directions independently, but does not qualify nonzero primal invariants or unequal primal masses.

2. **Sparse nonzero primal row:** take `eta=2^-64`, `delta=2^-32`, `M=2+2^-80-i`, and shifts `q0=0`, `q1=(delta,0,0,0)`, `q2=(0,2delta,0,0)`, `q3=(0,0,3delta,0)`, `q4=(0,0,0,4delta)` in metric `(+---)`. Symbolica independently derives the lexicographic squared distances `eta*[1,-4,-9,-16,-3,-8,-15,-13,-20,-25]`. Use squared masses `M+eta*[-2,-1,0,1,2]`. All ten primal invariants are nonzero and the four shift vectors are independent. The oracle's expansion center is M, whereas the candidate freezes the first physical mass `M-2eta`.

For both rows, a small proposed jet set is `s01[10]=eta`, `s23[01]=2eta`, `m1[10]=eta*(1+i/2)`, `m3[01]=eta*(-1/2+i)`, `m4[20]=eta/2`, `m2[11]=eta/4`, and `m0[21]=eta/8`; unspecified nonprimal components are zero. These are Taylor coefficients, not unnormalized derivatives. The invariant jets are independent analytic directions in invariant space; they are not asserted to arise from a common variation of the displayed routing. The primal routing is physical. All masses have strictly negative imaginary parts. The higher direct input components keep every requested nonprimal output at order eta, so an absolute budget cannot silently turn the higher mixed comparison into a near-zero check.

Freeze the fixture, source, component budgets, and resource caps before any run. The displayed fixture is a proposal requiring source review, not a proven numerical pass.

## Independent integral and component-tail construction

For the second row form the physical polynomial independently:

`F(x;t) = M + eta R(x;t)`, where `R = sum_i c_i(t) x_i - sum_(i<j) d_ij(t) x_i x_j`, `sum x_i=1`.

Use Symbolica's inclusive order-four expansion of `-1/F^2` in eta, then Symbolica normalized derivatives in `t0,t1` and origin substitution. Integrate each resulting coefficient exactly. This is a finite approximation to the physical integral with an independent remainder; comparison of two N2 expressions alone would only establish consistency of the same truncation. Do not call the candidate's polynomial, coefficient, envelope, or integration helpers.

Reuse the D0 positive generating-function argument at `d0_near_vacuum_oracle.rs:399–470` and the E6 measure/sign checks at `crates/iregi-rust/examples/e6_parameter_series.rs:173–211`. For each monomial `t^alpha`, let `B_alpha` be the sum of `abs(real)+abs(imag)` of the coefficients of all its mass and invariant terms. This deliberately coarse bound follows independently from `0<=x_i<=1`; no candidate max-envelope helper is needed. With `B(t)=sum B_alpha t^alpha` and `L=max(abs(Re M),abs(Im M))`, verify `eta B_00/L<1`. The positive coefficientwise oracle remainder generator is

`H4(eta B(t)/L)/(24 L^2)`, with `H_N(z)=z^(N+1)*((N+1)/(1-z)+1/(1-z)^2)`.

Symbolica verifies the generating-function identity and extracts every normalized `t^alpha` coefficient at the origin. Those exact nonnegative rational coefficients are individual complex-modulus remainder bounds. All nonprimal seeds carry eta, so differentiating in t does not remove powers of eta. A primal-only radius is insufficient. Unit-size invariant jets would instead lower the effective eta order and require a separately justified higher oracle order.

The reference mass M and all exact represented input coefficients must be serialized. Formal `i` and the existing exact rational numerator/denominator evaluator preserve complex coefficients without floating conversions (`d0_near_vacuum_oracle.rs:122`). At Float256 the proposed dyadic inputs, including `2^-80`, are represented exactly. Other types require new oracles for their actual represented inputs.

## Budget proof, beyond binary64

Retain the existing 128-bit request and relative budget, but strengthen the new row's absolute budgets from uniform `2^-128` to `2^-128` for the primal and `eta*2^-96 = 2^-160` for each nonprimal component. This does not loosen any existing budget. Before qualification, use exact Fraction arithmetic on emitted scalars to check:

- each oracle radius is nonnegative and its coordinate intervals lie inside the complete candidate rectangle;
- both numeric-to-oracle and worst-candidate-corner-to-oracle distance bounds, including the oracle radius, are below the explicitly serialized allowed budget;
- the candidate's own rectangle error and `max(absolute^2, relative^2*|returned|^2)` recompute exactly;
- each nonprimal oracle interval has magnitude bounded below by `eta/2^15`, and upper bounded by eta, so `2^-160` absolute error implies at least 81 bits of relative agreement. These inequalities are prospective gates to prove, not assumptions or observations; if any fails, preserve the failure and review the fixture before any new run;
- all rejected rows hide values, and successful components and batching counters are counted without exclusion.

For rational-only squared tests, a conservative enclosure uses per-coordinate differences enlarged by the oracle complex radius, then sums their squares. This avoids square roots and remains stronger than required when it passes. It is scalar bound auditing, not a polynomial engine. Keep the cubic rejection control, since exact physical integral derivatives at zero primal deviation can be nonzero even when N2 returns a zero polynomial coefficient.

## Triple reuse checks and concrete sources

1. **Symbolica API/source:** `../references/symbolica/src/atom/core.rs:734` (`AtomCore::series`); `src/poly/polynomial.rs:7057` (`integrate`), `:2733` (`replace`), `:2981` (`replace_with_poly`), `:2318` (`coefficient`), `:3806` (`to_multivariate_polynomial_list`), and `:2934` (`evaluate_with_coeff_map`). `src/poly/series.rs:784` distinguishes a known zero coefficient from one beyond the known truncation. No new differentiation, expansion, substitution, integration, matrix, or jet algebra is needed. Formal series truncation does not supply a numerical remainder theorem.
2. **Usage/tests:** Symbolica `examples/series.rs:7` demonstrates inclusive order four; `src/poly/univariate/tests.rs:175` tests integration against differentiation. Project `d0_near_vacuum_oracle.rs:109` supplies normalized derivatives; `:145` and `:570` supply the independent integrated-series and exact-vacuum patterns. `target/near-vacuum-input-enclosure/oracle/five_pinch_oracle.rs:140–158` converts the factored Atom directly to a Q polynomial and uses exact integration/endpoints. Its direct pentagon is D4 with `-2 F^-3`, so it cannot be copied unchanged for E6's `-F^-2`.
3. **FeynKit/GammaLoop:** `../references/gammaloop_feynkit/crates/feynkit-graph/src/integrals/parametric.rs:376` (`IntegralFamily::symanzik`) builds U/F through Symbolica determinant/cofactor operations; `:23–73` shows checked multivariate extraction. `docs/products/feynkit/content/integral-families.typ:287` explicitly leaves measure, powers, and prescriptions to the caller. `docs/products/feynkit/content/feyncalc-coverage.typ:396` delegates polynomial integration to Symbolica. Searches found no ready-made certified simplex integration/remainder oracle in these sources. Existing facilities cover the required algebra; the analytic remainder proof is the separate mathematical obligation.

## Resource and evidence limits

Reuse the already validated cube integration path first. An optional independent coordinate path is nested simplex integration: replace `x4=1-x0-x1-x2-x3`, integrate x3 to `1-x0-x1-x2`, then x2, x1, x0, using Symbolica `integrate` plus `replace_with_poly`. All polynomial variable maps must match. This avoids the cube Jacobian but is not measured, and `replace_with_poly:2999` recomputes endpoint powers per monomial, so it could be slower.

Keep numeric fixture coefficients fixed before polynomial conversion, at most two jet symbols, four integration coordinates, and one expansion symbol. Do not prepare a generic order-four expression in all fifteen physical arguments. Retain a parameter term cap (for example the exact vacuum oracle's 100,000), but remember that a post-conversion cap cannot prevent conversion from exhausting memory. Use the parent's coordinated external wall-clock and address-space caps; stop on either, preserve logs, and do not silently reduce precision or weaken a budget. Source and dependency provenance and the unchanged N2 hash must accompany any eventual result.

Existing production `crates/iregi-masters/src/pentagon6.rs:702` uses differences of successive quadrature orders as an error estimate. Its precision tests at `:879–904` compare a decimal value; they do not produce rigorous derivative interval bounds for these new rows. Therefore it can provide an auxiliary cross-check, not this experiment's sole certified oracle. The existing E6 exact series and contour oracle historical timings concern different fixtures and are not a runtime guarantee or a performance benchmark.

# Generalized scalar terms through existing PV coefficients

This candidate changes only `plan.rs` and `pv.rs` in the isolated source
snapshot. It has no production changes until independent qualification and
promotion. All matrix, polynomial, factorial and expression operations reuse
Symbolica and the existing PV/IBP compilers.

For each positive-power scalar request, write `e = sum(nu_i - 1)` and `k = h-e`.
The original generalized interface chooses PV exactly when `nu_0=1` and `k>=0`;
otherwise it uses IBP, even when the requested mode is PV. The tests are in
reference `gti_reduce.f90:355-366,469-480`, using `idim=2h`. They apply to each
scalar term in the tensor expansion, not just the initial powers/dimension.

Reference `si_reduce.f90::IBP2PAVE` (1159-1177) gives the native multiplier
`(-2)^k * pi^h / product((nu_i-1)!)`. Internal Rust `J_h` removes `pi^h`, so the
candidate calls the existing canonical coefficient with `metrics=k` and
`momenta=nu[1..]-1`, multiplying each Laurent slot by
`(-2)^k / product((nu_i-1)!)`. The existing `lightlike_expansion` implements the
inverse relation for bubbles, independently confirming the normalization.
The mapped coefficient rank is `2k+e` and has its own preparation-budget check.

The existing tensor generating polynomial, coefficient collection, external
normalization and multinomial weights are unchanged. Generated scalar requests
are dispatched individually. Their master leaves are deduplicated by kind and
active propagators; the existing globally named master slots coincide. IBP and
PV aliases remain in dependency order. An actual IBP-usage flag preserves the
legacy zero-diagonal guard in mixed generalized tadpoles.

Canonical metric coefficients are used only for one through four propagators.
The high-point Cartesian tensor decomposition does not determine an independent
canonical metric coefficient: the genuine D6 pentagon is the known example.
Consequently higher-point generalized requests retain the genuine IBP/E6 route
and explicitly report that canonical PV coverage is unqualified. This is not a
claim of complete generalized-PV parity with original IREGI.

`algorithm_used=PassarinoVeltman` denotes a PV primary which can include
mathematically ineligible IBP scalar terms, as in original generalized IREGI.
Preparation notes report both request counts. A primary with no PV terms reports
IBP. Hybrid prepares the independent full IBP fallback and retains the ordinary
batched numerical retry diagnostics; preparation failures also fall back to IBP.

The focused tests cover exact recurrence equivalence for shifted and raised
powers through boxes; ineligible first powers/negative shifts; factorial and
metric factors; translated negative-shift tensors with mixed eligibility;
native `pi^(2+h)` UV normalization; D6 preservation; preparation budget and
Hybrid diagnostics; legacy negative-mass rejection in a mixed tadpole; all four
slots of seven retained generalized fixtures in three modes; and a three-lane
second-order mass Dual comparison. Runtime evidence must be recorded separately.

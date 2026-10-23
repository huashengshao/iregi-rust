# COLLIER 1.2.10 reference adapter: independent source review

Status: source-only review. No compilation, numerical run, or timing was performed for this review. The proposed normalization still needs numerical witnesses, including an integral with a nonzero IR double pole, before the optional adapter is qualified. This review adds no production code. COLLIER source provenance and GPLv3 status are recorded in `docs/research/collier-1.2.10-manifest.json`; all COLLIER line citations below refer to the extracted tree `target/reference/collier/source/collier-COLLIER-1.2.10`.

## Public API and requested output

The implementing harness owner has selected a strict initial adapter domain: N=2..4, rank 0..3, exactly zero first shift, purely spatial real shifts, positive real part of every squared mass, and nonpositive imaginary parts. Its first performance pilot is the narrower existing N2/N3, rank0/1 massive suite. The detailed signatures independently checked below are the N2/N3 calls; the owner must separately verify the N4 call and the rank2/3 gather. Translated inputs are rejected by this initial adapter rather than silently changing the numerator; the translation discussion below specifies a future extension. `CHECK` is to probe each Delta outside timing on every lane, and `BENCH` is to use one full-tensor call plus native normalization and status handling only after the declared IR-finite domain passes those checks.

Use `Bten_cll(T,Tuv,MomVec,MomInv,mass2,R,Terr)` for N=2 and `Cten_cll(...)` for N=3. Their exact combined-array signatures are in `src/collier_tensors.F90:792` and `:1499`. For the proposed first envelope, initialize `call Init_cll(3,1,'')`, then explicitly select `SetMode_cll(1)` for COLI or `SetMode_cll(2)` for DD; publish the branches separately. These numbers are not IREGI IBP/PV mode numbers. COLLIER mode 3 evaluates both branches and is a separate, more expensive cross-check policy. Keep the required accuracy explicit; the default is only 1e-8 (`src/collier_init.F90:240`), and agreement is still independently judged at the project's unchanged 1e-10 tolerance.

For rank bound R, output tensors have shape `(0:R,0:R,0:R,0:R)`. `T(n0,n1,n2,n3)` is the Cartesian moment with those component multiplicities, without a multinomial weight. Read only entries with total multiplicity at most R. Avoid assuming that flattened Fortran storage or COLLIER's optional one-dimensional representation matches the project's ordering: gather by explicit exponent tuples into ascending total rank and then descending n0, n1, n2. Rank zero/one is `(1,q0,q1,q2,q3)`. The manual's component table at `manual/collier_manual-1.2.10.tex:2010` and full-tensor API at `:2176` specify this interpretation. `src/tensors/BuildTensors.F90:240` and `:425` explicitly scatter each component through `LorIndTab`.

The standard public calls have unit propagator powers and D=4-2 epsilon. They do not accept generalized powers or an `idim` argument. Reject those requests explicitly in this optional adapter. Double-complex squared masses with nonpositive imaginary part are supported; the manual explicitly says that nonzero imaginary parts of momentum vectors/invariants are unsupported, despite their double-complex Fortran types (`manual/collier_manual-1.2.10.tex:2103`, `:2198`). The N=2/3, rank 0/1 overlap is within both COLI and DD coverage. Do not infer rank-seven or generalized coverage from this first adapter.

## Routing, metric, and scales

COLLIER defines `N_k=(q+p_k)^2-m_k^2+i0`, p0=0, with the `(time,x,y,z)` convention (`manual/collier_manual-1.2.10.tex:931`). For original input shifts s0,...,s(N-1), supply `p_i=s_i-s0`; for the first benchmark all s0 are already exactly zero. Momentum invariant order is:

| Family | MomVec | MomInv |
|---|---|---|
| Bubble | p1 | p1 squared |
| Triangle | p1, p2 | p1 squared, (p2-p1) squared, p2 squared |

Use metric (+---), preserve the exact binary64 inputs, and preserve negative imaginary squared masses. The triangle order is independently visible in `C_main_cll(...,p10,p21,p20,...)` (`src/collier_coefs.F90:698`) and its call from the full-tensor routine (`src/collier_tensors.F90:1535`).

The two COLLIER scale setters take squared scales: `call SetMuUV2_cll(mu*mu)` and `call SetMuIR2_cll(mu*mu)` (`src/collier_init.F90:685`, `:738`). IREGI's public mu and OneLOop's `olo_scale` take mu itself. Setting both COLLIER scales to mu would silently compare different integrals.

For translated routing s0 != 0, COLLIER's local integration variable is k=q+s0. Rank-one original moments are therefore `T_original^mu=T_local^mu-s0^mu*T_local_scalar`, separately for every Laurent slot. Higher-rank translation belongs to the existing Symbolica preparation facilities. Supplying only shift differences without translating tensor numerators back is incorrect. Reversing the sign of the loop variable introduces the corresponding odd-rank sign; merely reversing the list of propagators does not justify a global rank sign.

## Full Laurent normalization

The existing reference driver `validation/benchmark/driver.f90:55` sets `ML5_CONVENTION=.true.` solely for unweighted moments and calls `tensor_integral_reduce` directly. It does not call the `IMLOOP` adapter. Therefore the comparison target is the native four-slot array `[U,I,J,F]`, including its overall i*pi^2, and no extra MadLoop odd-rank sign.

COLLIER returns the full expression at user-selected `DeltaUV`, `DeltaIR1`, `DeltaIR2`, plus a separate UV coefficient `Tuv`. Its default zeros return a finite coefficient in its own cGamma convention. At zero deltas define, for each tensor component:

```
Fc = T(DeltaUV=0, DeltaIR1=0, DeltaIR2=0)
Uc = Tuv at the same settings
Ic = T(DeltaUV=0, DeltaIR1=1, DeltaIR2=0) - Fc
Jc = T(DeltaUV=0, DeltaIR1=0, DeltaIR2=1) - Fc
a  = EulerGamma + log(pi)

U = i*pi^2 * Uc
I = i*pi^2 * (Ic - a*Jc)
J = i*pi^2 * Jc
F = i*pi^2 * (Fc - a*(Uc+Ic) + (a*a/2 + pi*pi/12)*Jc)
```

`Ic` includes the scale-dependent `Jc*log(muIR^2)` contribution: it is the coefficient obtained by varying DeltaIR1 at the actual supplied scale, not the scale-independent symbol a1 of the manual. This follows from `manual/collier_manual-1.2.10.tex:1092` and the independent setters at `:2351`; the setter order is `(single,double)`, not the order used by some internal DD routines.

The manual explicitly states that the OneLOop/Ellis convention has finite coefficient `L0=Fc+(pi^2/6)*Jc`, while simple and double poles are unchanged (`manual/collier_manual-1.2.10.tex:1179`–`:1189`). Combining this with the supplied IREGI scalar wrapper (`../references/madgraph/vendor/IREGI/src/mis_warp.f90:319`–`:321`, `:412`–`:414`) gives the equations above. In particular, copying the project's OneLOop-to-native formula directly onto unshifted COLLIER Fc uses the wrong sign/size for the double-pole finite shift. An equivalent implementation may set DeltaIR2=pi^2/6 for the baseline to obtain L0 first, then use the existing OneLOop-to-native conversion. These are convention conversions, not reduction algebra.

For the first massive Euclidean N2/N3, rank0/1 benchmark family, IR poles are absent. The one-call specialization is consequently:

```
U = i*pi^2 * Tuv
I = 0
J = 0
F = i*pi^2 * (T - a*Tuv)
```

The N3 rank0/1 UV coefficient is also zero, but retaining its returned array makes that check visible. This specialization must be restricted to a proven IR-finite envelope. Massless on-shell triangles and scaleless bubbles need the full UV/IR distinction; a vanishing combined result does not imply separate poles vanish. Off-shell massless Euclidean cases can be added only with their IR-finiteness classification explicitly recorded.

The public API does not return a complete IR Laurent array in a single call. A generic adapter using the three delta evaluations must include those extra reductions and delta-setting costs in its full-output timing and must not compare that cost to an unmatched one-call scalar-only workload. A one-call massive specialization is fair when both engines are required to return the same complete tensor/Laurent arrays and the two zero IR slots follow from the declared benchmark envelope. Independently verify the specialization with delta probes outside timing.

## Numerical cache and failure policy

Use only per-call recurrence memoization, with no cross-lane or cross-iteration numerical result reuse. `Init_cll` already calls `InitCacheSystem_cll(0,Nmax)` (`src/collier_init.F90:269`). Zero here means **local-only cache**, not fully disabled: `src/Aux/cache.F90:101` sets `onlyinternal=.true.`, and `:131` sets the internal mode to -1. In that mode the cache resets its rank/value storage at the master call (`:1278`–`:1291`). `SwitchOffCacheSystem_cll` also requests local-only mode, despite its name (`:553`); `InitCacheSystem_cll(-1,Nmax)` instead removes local recurrence memoization and changes the comparison policy. Retain the default zero-external-cache configuration and report it explicitly.

Reset error and accuracy flags per lane using `InitEvent_cll()` or the two dedicated reset calls, and retain both `GetErrFlag_cll` and `GetAccFlag_cll`, the optional tensor error estimates, and finite-value checks in captured output. `InitEvent_cll` performs these resets at `src/collier_init.F90:530`; it returns immediately from the global-cache initialization in local-only mode (`src/Aux/cache.F90:942`). Negative error/accuracy flags must remain visible; do not manufacture a successful zero. COLLIER's estimates are order-of-magnitude diagnostics, not accuracy certificates (manual `:2146`).

The existing IREGI timed kernel calls `IREGI_FREE_PS` after each lane (`validation/benchmark/driver.f90:129`), so it already prohibits numerical reuse across samples. Its per-call recurrence values remain available while reducing that lane. Include comparable per-lane reset/check/disposal work inside the timing region for each reference. Initialization, input parsing, and subprocess I/O remain outside both kernels. COLLIER's batch-32 reference is 32 scalar calls; label it as such.

Keep `Init_cll` defaults that calculate UV terms and include IR rational terms (`src/collier_init.F90:291`–`:296`). The CMake build must retain its default `-DSING` (`CMakeLists.txt:90`), otherwise the Delta setters explicitly become ineffective (`src/collier_init.F90:803`, `:870`). Use `folder_name=''` and suppressed optional output for benchmark kernels, but preserve errors/statuses in the JSON transport. Mode, accuracy, scale, compiler flags, exact source hashes, and cache policy belong in the qualification manifest.

## Required adapter qualification before timing claims

1. Compare all native slots/components for every massive N2/N3 rank0/1 fixture, including odd-rank signs and all lanes, using the original 1e-10 dimensionally normalized tolerance.
2. On those exact fixtures, independently vary each Delta and confirm the zero IR slots and returned UV arrays. Keep checks outside the production timing region.
3. Include one IR-double-pole scalar triangle, one single-IR-pole example, and a scaleless bubble to validate the full normalization and UV/IR separation. This expands correctness coverage, without silently expanding the one-call performance envelope.
4. Test common-shift translation and at least one nonzero time component; the current all-spatial Euclidean baseline alone cannot expose every routing/sign error.
5. Use identical input batches and outputs, local-only numerical caches, one pinned core, optimized builds, warm-up, paired repeated measurements, and the existing uncertainty gate. Keep unsupported, failed, and noisy families visible.

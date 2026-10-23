# Independent driver source review

Reviewed file: `validation/collier-reference/driver.f90`, initial SHA256 `047d5ca26e162849713e3770fe6f77b671bb1bf387ca0116771ded5ed6f7a886`.

This is a source-only review during the compilation hold. No compiler, reference executable, or numerical benchmark was run. Line references below identify that initial snapshot; implementation-owner fixes require a subsequent source hash/recheck.

## Concrete findings

1. **CHECK does not reject nonfinite pole-probe values.** `verify_poles` reads baseline tensors and UV arrays and computes `abs`/normalization at lines 224–247 without checking finiteness. A nonfinite delta-varied value can yield NaN, and Fortran `max(previous,NaN)` plus a final `>1d-12` comparison cannot be relied on to flag it. The final ordinary evaluation may be finite, allowing an unsuccessful pole check to appear successful. Check real/imaginary parts of every gathered probe component, UV component, and error estimate explicitly, retain a finite failure diagnostic, and mark the lane/request failed before any `max` update.

2. **Scale validation admits underflow to zero.** Line 47 rejects nonfinite mu and mu squared, but finite positive mu can have `mu*mu==0`. Require the represented squared scale to be strictly positive as well as finite before passing it to both COLLIER scale setters.

3. **Derived invariants may overflow even when shifts are finite.** Lines 60 and 158–167 check only input shift finiteness; finite coordinate differences or squares can overflow. Reject nonfinite constructed `MomInv` values before a public tensor call. This is a boundary of the declared supported domain rather than a new physical branch.

4. **Lane JSON does not preserve earlier failures.** Each `tensor_call` assigns `stable(k)` from the current call at line 184. Earlier CHECK/warm-up/repeat failures remain in global `all_stable`, but a later successful evaluation can emit lane `status=success`. Likewise a failed pole comparison increments global `bad_poles` without changing that lane's status. Keep a cumulative per-lane status if per-lane JSON is intended to describe the entire request. The current global flag prevents the request from being accepted when it is correctly checked; this finding concerns inconsistent per-lane reporting and loss of the failing lane identity.

## Reviewed without a source blocker

- The Bten/Cten/Dten combined-array overloads accept the supplied rank-four output arrays, `(0:3,N-1)` momentum arrays, invariant lengths 1/3/6, and squared-mass lengths N. Passing the contiguous section `masses(:,k)` to COLLIER's explicit-shape `mass2(0:N-1)` correctly associates its first actual element with dummy element zero; matching caller lower bounds is unnecessary.
- N4 invariant order is exactly `(p1²,(p2-p1)²,(p3-p2)²,p3²,p2²,(p3-p1)²)`. The independent source signature is `src/collier_tensors.F90:2590`, `Dten_args_cll(...,p10,p21,p32,p30,p20,p31,...)`; the driver's assignments at lines 158–167 match it.
- The nested loops over ascending total rank then descending time/x/y exponents reproduce the original IREGI Cartesian ordering through rank three. They gather only defined tensor entries and attach no multinomial weights.
- For the explicitly IR-finite massive Euclidean domain, the conversion `U=i*pi²*Tuv`, `I=J=0`, `F=i*pi²*(T-a*Tuv)` is the correct native normalization. No MadLoop rank sign belongs here.
- Exact zero origin, zero time components, positive real parts of squared masses, and nonpositive imaginary parts are explicitly enforced. The source does not silently accept translated routing, massless cases, timelike shifts, generalized powers, or dimension shifts.
- CHECK resets both delta parameters before every variation and after every lane. Each probe invokes `InitEvent_cll`, which resets accuracy/error flags without enabling external result reuse. The baseline for the next lane therefore starts with zero deltas.
- `Init_cll(n,rank,'',.false.)` on a later request invokes `Reset_cll` when already initialized (`src/collier_init.F90:119`), resets policies, and creates local-only cache mode via `InitCacheSystem_cll(0,Nmax)` (`:269`). The driver's explicit settings are applied afterwards. No cross-request numerical event cache is retained by this policy.

## Limits still requiring qualification

Source inspection does not demonstrate numerical agreement, error-flag reliability, complete pole checking, or performance. The first numerical qualification should retain full per-lane tensor/Laurent arrays, the CHECK deltas and status flags, and an exact source/build binding. Current lane JSON emits only a boolean-derived status, so raw COLLIER error/accuracy flags and tensor-error estimates are unavailable for later diagnosis. Also, the timed `evaluate_batch` includes `prepare_lane` momentum/invariant construction in addition to the public tensor call, normalization, and checks; record that timing boundary accurately.

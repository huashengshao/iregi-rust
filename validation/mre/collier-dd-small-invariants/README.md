# COLLIER 1.2.10 (DD branch): wrong pentagon tensors for tiny nonzero invariants

## Summary

COLLIER's DD branch (`SetMode_cll(2)`) returns a wrong rank-5 pentagon tensor
when the squared momenta of massless legs are tiny but not exactly zero. In
the reproducer the invariants are 8.8e-11 and −7.6e-11 GeV², their binary64
values computed from the momenta, against internal masses m_t² = 29929 GeV².
COLLIER reports error flag 0.

The integral is regular there: with massive internal lines it changes by about
|p²|/m² ≈ 3e-15 when these invariants are replaced by exact zeros. COLI
(`SetMode_cll(1)`) behaves accordingly and agrees with its exact-zero result.
DD instead differs from it by E/A = 0.30 over the rank-5 tensor, and by 5% in
the scalar pentagon T(0,0,0,0).

Found in iregi-rust's binary64 stability study
(`validation/benchmark/stability-20261030`). That study now passes massless
invariants as exact zeros (invariants below 1e-12 of the largest), as an
amplitude code with on-shell masses would, so its COLLIER results are not
affected.

## Affected version and build

COLLIER 1.2.10, unmodified, built under `target/reference/collier/build-attempt001`
(gfortran, binary64). Not checked: other versions.

## Reproducer

[`collier_small_invariants.f90`](collier_small_invariants.f90) is self-contained:
one gg→Hgg top-loop pentagon at √s = 1 TeV (stability-study point pentagon-r5
#0), with μ² = 10⁶ GeV².

1. Compute the 10 invariants from the momenta in binary64.
2. Call `TNten_cll(N = 5, R = 5)` twice in each mode: with these invariants,
   and with those below 1e-12 of the largest set to exactly zero.
3. Print `T(0,0,0,0)`, the error flag, and the E/A of the full tensor
   (moments weighted by μ^rank) between the two calls.

```sh
gfortran -O2 -ffree-line-length-none -I <collier>/modules collier_small_invariants.f90 \
  <collier>/libcollier.a -o collier_small_invariants
./collier_small_invariants          # COLLIER defaults
./collier_small_invariants study    # SetReqAcc 1e-10, SetCritAcc 1e-3, SetTenRed 6
```

## Observations (both settings identical)

```
invariants as computed from the momenta (GeV^2):
   0.000E+00   0.000E+00   8.822E-11   1.563E+04  -7.640E-11
   1.000E+06  -2.884E+05   2.379E+05   2.729E+05  -2.501E+05
mode 1 exact-zero invariants: err flag  0  T(0,0,0,0) =   4.523561779037885E-16   3.294327305103391E-16
mode 1 computed invariants:   err flag  0  T(0,0,0,0) =   4.523561779037889E-16   3.294327305103394E-16
   E/A of the rank-5 tensor, computed against exact-zero invariants:  1.012E-38
mode 2 exact-zero invariants: err flag  0  T(0,0,0,0) =   4.523561779037885E-16   3.294327305103388E-16
mode 2 computed invariants:   err flag  0  T(0,0,0,0) =   4.751859970713821E-16   3.638157785023940E-16
   E/A of the rank-5 tensor, computed against exact-zero invariants:  2.981E-01
```

- With exact zeros, COLI and DD agree to 1e-15. Both agree with TIRust's
  256-bit evaluation and quad-precision original IREGI in the stability study.
- With the computed invariants, COLI is unchanged and DD is wrong already in
  the scalar pentagon, with no error flag.

## Likely origin (hypothesis)

DD treats the two near-lightlike invariants as nonzero and evaluates the
scalar four- and five-point functions with general-p² formulas. These cancel
like m²/p², the same mechanism as a general-p² B0 at small p², which fails in
binary64 for p² ≈ 1e-10 and m² ≈ 3e4. COLI appears to snap such invariants
internally. Not confirmed by instrumentation.

## Workaround for users

Pass exact zeros for the squared momenta of massless legs, or snap invariants
far below the other scales to zero, before calling COLLIER.

## Reporting

Not reported upstream. This file and the reproducer are the ready-to-send
report, through the contact on https://collier.hepforge.org, if the user wants.

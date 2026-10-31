# COLLIER 1.2.10: NaN (COLI) or a fatal DD error for a regular seven-point tensor

## Summary

`TNten_cll` for a seven-point integral with exact dyadic shifts, positive
squared masses 1–4 and every invariant far below threshold:

- **COLI** (`SetMode_cll(1)`) returns NaN tensor components from rank 4 on,
  with error flag 0. Ranks 0–3 are finite and the scalar is unchanged.
- **DD** (`SetMode_cll(2)`) stops with "fatal error in DD: -10". With
  `SwitchOffErrStop_cll`, as in iregi-rust's drivers, it returns NaN instead.

The point is the N7R7 row of iregi-rust's opening timing corpus. Its reference,
from TIRust's direct engine at 256 bits, is confirmed by quadruple-precision
original IREGI (IBP) to E/A 6.3e-17
(`validation/benchmark/direct-engine-20261030/n7r7/check.json`).

## Reproducer

[`collier_n7_nan.f90`](collier_n7_nan.f90) evaluates the point at ranks 0–7 in
both modes, with μ² = 9 and the invariants computed from the shifts:

```sh
gfortran -O2 -ffree-line-length-none -I <collier>/modules collier_n7_nan.f90 \
  <collier>/libcollier.a -o collier_n7_nan && ./collier_n7_nan
```

## Observations

```
mode 1 rank 3: finite T  err flag  0  T(0,0,0,0) = -1.476735E-04  2.891037E-17
mode 1 rank 4: finite F  err flag  0  T(0,0,0,0) = -1.476735E-04  2.891037E-17
...
mode 1 rank 7: finite F  err flag  0  T(0,0,0,0) = -1.476735E-04  2.891037E-17
 COLLIER: fatal error in DD:          -10
 execution of program stopped
```

Shifts: 0, e_x, e_y, e_z, e_t/2, e_x + e_y and (1/4, 3/8, 1/8, 5/8). Squared
masses: 1, 2, 3, 4, 2, 3, 4.

## Not yet narrowed down

- Which sub-integral produces the first NaN.
- Whether other seven-point points behave the same: see COLLIER's results
  on the physical gg→ggggg heptagons of the stability study (capture 003).

## Reporting

Not reported upstream. This is the ready-to-send report, through the contact
on https://collier.hepforge.org, if the user wants.

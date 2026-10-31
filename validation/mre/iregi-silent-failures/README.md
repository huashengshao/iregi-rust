# Original IREGI: wrong tensor integrals reported as successful

## Summary

`tensor_integral_reduce` returns wrong tensor arrays for regular top-loop
integrals, with stability flag `.true.`. Three representative points from
iregi-rust's binary64 stability study (`validation/benchmark/stability-20261030`):

| case | IREGI mode | IREGI binary64 E/A | quad IREGI IBP E/A | COLLIER COLI E/A | TIRust default E/A |
|---|---|---|---|---|---|
| gg→HH top box, rank 6 (#0) | PV | 9.7e-2 | 6.3e-17 | 1.3e-15 | 1.1e-15 |
| gg→gggg top hexagon, rank 6 (#0) | IBP | 5.2e55 | 7.6e55 | 4.0e-13 | 0 |
| gg→Hgg top pentagon, rank 5 (#27) | IBP | 0.91 | 4.8e-12 | 2.0e-15 | 5.1e-15 |

E/A is the dimensionally rescaled whole-array maximum discrepancy, over all
Cartesian moments and Laurent slots, against TIRust's direct engine at 256
bits. In the study that reference is confirmed per point by quadruple-precision
original IREGI. COLLIER, which is independent of both, agrees with it here.

Frequencies in the study (capture 002; IREGI flagged none of these points):

- PV fails on all 10,000 rank-6 boxes, where the rank exceeds N.
- IBP is worse than 1e-3 on 268 of 5,000 pentagons (worst 4e22) and on 1,987
  of 1,994 hexagons (worst 4e80).
- On the physical heptagons of capture 003, IBP is off by about 1e85, and
  quad IREGI also disagrees with TIRust and COLLIER by E/A 0.01–1.

The three cases have different characters:

- **Box, PV:** a rank-above-N limitation of the PV recursion that is not
  reported. IBP and quad agree with the reference.
- **Pentagon, IBP:** precision loss. The quad build is accurate to 5e-12.
- **Hexagon, IBP:** an algorithmic failure. The quad build is just as wrong.

## Build

Original IREGI objects under `target/reference/objects` (with the narrow,
separately documented `funlib` factorial-table repair of iregi-rust), linked
with the study's driver `validation/benchmark/stability-20261030/drivers/iregi_physical.f90`
by that directory's `build.py`. `INITIREGI(.true., 2, 1d-12)`,
`ML5_CONVENTION = .true.`, IREGI's default on-shell snapping. The quad
reference is `target/quad-iregi-source-audit/build-v6-001`.

## Reproducer

`<case>.in` holds the driver request for one point: the `BENCH` header with
the mode (0 = IBP, 1 = PV), then n rows of shift components, squared mass and
power. `<case>-reference.json` holds the 256-bit array (77 digits) in the
driver's moment order (increasing rank, IREGI's monomial order) with the four
Laurent slots. `summary.json` holds the numbers in the table.

```sh
target/stability-20261030/bin/iregi-physical < validation/mre/iregi-silent-failures/box-r6-0-pv.in
```

The driver prints one `RESULT {json}` line, whose `lanes[0].moments` is
compared with the reference.

## Reporting

Not reported upstream. These files are the ready-to-send report, if the user
wants it sent.

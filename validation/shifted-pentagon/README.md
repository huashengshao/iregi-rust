# Standalone shifted-pentagon reference audit

`adjudicate.py` compares the defining finite D6 scalar pentagon integral with
the repaired reference's scalar and generalized interfaces. The only reference
repair remains the documented generalized factorial-table initialization fix.
No production Rust reduction contributes to the independent parameter oracle.

From the project root, after building the reference:

```sh
source scripts/env.sh
python3 validation/shifted-pentagon/adjudicate.py --write
```

Validation requires mpmath; the script supports the pinned Nix development
environment's installed package. `evidence.json` records input, binary hash,
quadrature orders and precision, all Laurent slots, normalization checks, a
mass-shift integral check, and the reference's common-mass derivative.

The full-rank test has strictly positive Feynman-parameter denominator. Direct
parameter integration and the independently sampled D4 mass-shift identity
agree. All three original modes return a different standalone D6 finite
coefficient while declaring stability. This evidence does not adjudicate
complete physical tensor outputs, and it makes no runtime-performance claim.

See `docs/research/shifted-pentagon.md` for the normalization, derivation,
continuation domain, and proposed genuine-master extension.

`contours.json` deliberately retains a **failed reference comparison** at a
negative-width point. Its four-dimensional parameter oracle is independent.
One pinched box returns zero because the bundled OneLOop complex-box formula
requires a positive external Källén discriminant. A direct scalar-master
probe reproduces that behavior without IREGI. Reproduce it with:

```sh
source scripts/env.sh
gfortran -O3 -I target/reference/objects \
  validation/shifted-pentagon/box_probe.f90 \
  target/reference/objects/avh_olo_foriregi.o -o target/reference/box-probe
python3 validation/shifted-pentagon/contours.py --write
```

The JSON `status` is `reference_failure`; the script retains all outputs
instead of discarding the case. This artifact alone does not qualify the
Rust complex-contour evaluator.

The Rust prototype and public-core independent checks are separately retained
in `rust-focused.log` and `core-qualification.log`. Reproduce the public test:

```sh
source scripts/env.sh
cargo test -p iregi-rust --test shifted_pentagon -- --test-threads=1
```

The public test covers the positive-F and negative-width values, three mixed
lanes, explicit rejection of an unqualified zero-width endpoint, zero Laurent
poles, scale covariance, empty batches, and internal box-row counters. Its
first, stricter backend-budget attempt remains in
`core-four-bit-margin-failure.log`. The final output accuracy target is
unchanged; Symbolica propagates componentwise quadrature estimates through
the reduction before accepting a lane.

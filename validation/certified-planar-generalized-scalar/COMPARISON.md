# Saved comparison contract

`compare_saved.py` is implementation source for the finite vertical slice. It
is **not an independent numerical review** of the example or parameter-oracle
producer. No captures or integrals have been evaluated while preparing this
source. Its imports are exclusively from Python's standard library, and it
never imports the Rust driver, oracle, mpmath or lifecycle controller.

The comparator consumes the frozen `catalog.json` produced from the reviewed
draft and all 33 required result/receipt pairs under
`target/certified-planar-generalized-scalar-numeric`. An explicit `--catalog`
can select another byte-pinned catalogue copy. All 22 scalar, four mass-jet,
four finite-difference and three parameter-oracle jobs are mandatory. It
continues through missing, failed, truncated or malformed independent captures,
retaining per-case errors and blocked numerical gates. Missing data never
becomes a successful zero array, and incomplete subsets cannot qualify.

After separately authorized captures, saved comparison is invoked as:

```sh
source scripts/env.sh
python3 validation/certified-planar-generalized-scalar/compare_saved.py \
  --catalog validation/certified-planar-generalized-scalar/catalog.json \
  --capture-root target/certified-planar-generalized-scalar-numeric \
  --output NEW_COMPARISON.json
```

Existing comparisons are never overwritten. Malformed catalogue/global
metadata produces an explicit failed comparison. The optional `--self-test`
performs synthetic parser and exact-threshold controls only; it reads no
actual capture and calls no integral or native code.

## Saved metadata and input checks

Each receipt must bind the complete catalogue job and exact catalogue hash,
have terminal capture status, unchanged input guards, no cancellation or
cleanup errors, and exactly one successful owned child. CPU, arguments, native
cap and aggregate deadline must match the catalogue. Receipt authorization and
independent-review hashes must be well-formed and present in the guarded input
maps. Every capture uses the same frozen independent source review and
catalogue; distinct phase grants are allowed. Their grant provenance is
reviewed separately. The source catalogue remains
immutable pending a separate root grant, so no mutable `authorized=true` bit
is required in the source catalogue.

The common example digest comes from the saved admitted build receipt. Rust
receipts must attest the same digest and honestly mark their owned executable
aliases as shared inodes. The comparator neither opens nor rehashes native
executables, checks inodes, signals processes or repeats PID absence probes.
It hashes only the small saved JSON, log and owned-oracle source outputs. This
is a saved attestation check, not a new hermetic build/native provenance claim.

Rust metadata must retain native IREGI convention, raw scalar components, exact
positive propagator powers, h, precision request, rank-zero basis, sample
labels and separate derivative shape. Component precision is a positive
integer no larger than working precision; it is not assumed equal to working
precision. Before/after numerical input values **and precision metadata** must
match exactly, and match the complete expected input table. Rational fixtures
make no signed-zero preservation claim.

All valid rows must use chart zero, with the corresponding raw diagnostic,
and must report success without fallback or genuine E6 work. Invalid controls
must be `InvalidInput`, have null slots/chart, and never enter an analytic
chart. Certificate and recurrence counters must attribute the complete batch
to one chart reduction batch. Exact Symbolica numerical preparation witnesses
are checked without interpreting their expression strings.

The three oracle captures must retain all twelve finite integrals and explicit
native Laurent slots, all eleven generalized request identities and the
ordinary unit control. The defining-integral signs, positive-F input values,
quadrature order, digits, node count, preparation payload hash and existing
quadrature-helper pins are checked. Their flags must not claim a rigorous
error bound, prior convergence, broad domain or performance qualification.

## Exact numerical gates

All real/imaginary decimal or rational strings are parsed into `Fraction`.
NaN, infinity, booleans in numerical fields, duplicate JSON keys, missing
components and invalid array shapes are rejected. Decimal arithmetic is used
only to display the square root of an already exact squared error.

For scalar mass dimension `d=4+2h-2*sum(powers)`, use

```text
Q²=max(1, |m_i²|, |(p_i-p_j)²|),
error²=|actual-reference|²/max((Q²)^d, |reference|²).
```

A first mass derivative has dimension `d-2`. All 128/256 precision pairs use
Float256 as reference and amplitude tolerance `2^-80`; direct oracle and
identity gates use `1e-10`. Successive oracle orders 12→16 and 16→20 use the
finer result as reference and tolerance `1e-12`. The squared thresholds are
exactly `2^-160`, `1e-20`, and `1e-24`, respectively.

The fixed inventory contains **2,064 mandatory gates** and **80 additional
finite-difference diagnostics**. Gates cover all four Laurent slots and every
successful derivative component. There are 440 precision-pair gates, 96 oracle
refinement gates and 660 exact positive-F pole gates. The expected output
values are preserved unchanged; no pole is projected or merged.

For each scalar request, the base agrees with the finest independent oracle;
the scaled row follows the exponent d, spatial translation preserves the
scalar, and the repeated row agrees exactly. All successful rows additionally
participate in the 128/256 pair check. The nonplanar row is rejected.

For each unit mass-jet context, the six valid primal rows agree with the unit
oracle, and each first derivative agrees with both the matching dotted scalar
and independently integrated dotted oracle, with positive mass-derivative
sign. Both components of the repeated mass lane must agree exactly. The
transverse time jet is rejected.

Finite-difference rows remain numerical samples, not Taylor components. Both
central differences and Richardson `(256*fine-coarse)/255` are saved for every
Laurent slot. Richardson must agree with both the ordinary dot and oracle at
`1e-10`. The finite-slot error against the ordinary dot must improve, unless
both errors are already below the `2^-80` precision floor. Oracle monotonicity
is diagnostic because quadrature uncertainty may dominate it. All coarse/fine
errors against both references remain visible. No finite-difference `2^-80`
accuracy claim is made.

The pole coefficients must remain exactly zero throughout this strictly
massive positive-F corpus, including derivative components and shifted masses.
This is a mathematical domain-specific expected value, checked against each
raw result; it is not a rule for massless or scaleless integrals.

A pass means these fixed saved numerical gates passed. It does not independently
audit the producer, prove a rigorous quadrature bound, qualify a later build or
all generalized kinematics, or establish performance. Missing oracle refinement
or failed FD/precision controls remain failed or inconclusive. No automatic
extra order, retry or failed-case exclusion exists.

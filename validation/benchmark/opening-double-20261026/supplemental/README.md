# Supplemental denominator-order / PV observations

These four additional candidates were declared **after** both fixed IBP master
policies refused the N4 rank-six dotted request at binary64/request53. They do
not replace or modify the original 38-candidate protocol, inputs or evidence.

For dot2 and dot3, permute denominator triples `(shift, squared mass, power)` by
`[1,0,2,3]`, then request public Passarino–Veltman with NativeF64Abc and Symbolica
master policies. The loop variable and numerator remain unchanged: the product
of denominators is identical, so every Cartesian tensor moment can be compared
directly to the original-order saved tensor. Generalized PV dispatch retains
IBP for ineligible scalar terms; this is not an all-PV guarantee. The public
constructor accepts nonzero first shifts through relative-geometry evaluation.

All candidates use `f64`, 53 working bits, the unchanged accuracy parameter53,
three warmups and 11 fixed-count blocks targeting30ms, capped at10000 calls per
block. No precision promotion, unsafe result access or tolerance change occurs.
Refused arrays remain null even when their diagnostic runtime is measured.

The same frozen `opening_double` binary and original215-file build guard are
used. New helpers and the protocol have separate hash bindings. CPU18 and process
group supervision follow the parent campaign. Preparation, first call, warmups,
output checks and serialization remain excluded from the warm timing split.

Root-owned execution, after the initial campaign has finished:

```sh
source .local/tirust-current-toolchain-roots/env.sh
source scripts/env.sh
source .local/symbolica-license.env
python3 validation/benchmark/opening-double-20261026/supplemental/run.py prepare
python3 validation/benchmark/opening-double-20261026/supplemental/run.py run --cpu 18 --timeout 1800
python3 validation/benchmark/opening-double-20261026/supplemental/run.py summarize
python3 validation/benchmark/opening-double-20261026/supplemental/independent_check.py
```

The prepare/run steps refuse overwriting existing records. A saved-data replay
does not evaluate any integral. Report the additional post-hoc search explicitly
if a new candidate is selected for the optimistic opening tables. The reference
is the previous finite-precision full tensor independently checked against
original IREGI; its E/A error is empirical, not a certified integral bound.

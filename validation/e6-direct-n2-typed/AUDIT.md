# Independent typed-output audit

`audit/result.json` reports **24,889 passed checks, 166 hash verifications
and zero failures**. The checker independently recomputes scalar rational
comparisons from the serialized evidence, without running Symbolica or
reusing the candidate's polynomial integration. A separate reviewer checked
the checker and independently cross-checked all 320 accepted component
bounds, 65 hidden rejections and 128 precision-comparison coordinate widths.
The review receipt is `audit/review.json`.

For identical represented inputs at Float256 and Float384, both with
requested accuracy 128, all 102 positive arithmetic coordinate widths
strictly shrink. The remaining 26 widths are exact zero at both precisions.
These widths remove twice the recorded analytic truncation radius from the
full rectangle width. They measure arithmetic convergence; the fixed N2
expansion's omitted mixed cubic term can remain a nonzero error floor.
The audit retains that error and checks the complete rectangle against the
unchanged budget at each precision.

The source review and successful compiled assertions establish reversal,
chunking, fresh-plan, singleton and concurrent-workspace equality. The
independent audit checks their serialized counters and provenance. Full
repeated arrays are not serialized, and instruction/lane visits are
structural estimates rather than execution traces. The three recorded
batch calls use the complete active-lane count.

The audit result SHA-256 is
`14692f726442b2e7d42d5692dae9daa62e47d4dcae705bf2f8dc54f69663d0f3`.
The independent review SHA-256 is
`80567ec0ea5ca011fc73734b2ea793a3c97f852837b41c2b2abd1d26cb92782d`.
The frozen result binds original retained runtime paths; the qualification
inventory separately binds their byte-identical durable copies.

The checker accepts an optional `--base` directory. Running against the
retained target attempt reproduces the recorded audit:

```sh
source scripts/env.sh
python3 target/e6-direct-n2-typed/audit/audit_typed.py \
  --output target/e6-direct-n2-typed/audit/recheck.json
```

It refuses to overwrite an existing result, so select a fresh output path
for each recheck. It requires the retained binary and frozen dependency
closure for provenance checks. No benchmark or public/default E6 coverage
follows from this audit.

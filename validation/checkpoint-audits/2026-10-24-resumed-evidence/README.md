# Resume evidence checks

These lightweight checks inspect saved source/raw evidence; no integral or
performance kernel was executed. `integrity.json` records qualification-bound
file hashes plus a license/compiled-artifact scan for 87 evidence files.

The frozen typed audit recomputed all 24,889 checks with zero failures. Its
`typed-recheck.json` has the same numerical, transport, input and convergence
results as the original independent audit, with durable-copy paths in the
provenance map. The invocation passed a relative output path: after successfully
saving the result, the checker's final status-print path formatting raised
ValueError. `typed-recheck-receipt.json` records this invocation issue; the frozen
checker was not modified. No numerical/audit calculation failed.

Reproduce with an **absolute fresh output path**, since the checker preserves
existing results and expects the output to lie under the project:

```sh
source scripts/env.sh
python3 validation/e6-direct-n2-typed/audit/audit_typed.py \
  --base validation/e6-direct-n2-typed \
  --output /shared/external/iregi/iregi-rust/target/typed-new-recheck.json
```

The checker requires retained local build artifacts to verify original runtime
provenance. It does not establish public/default E6 coverage or performance.

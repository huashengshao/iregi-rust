# Separate posthoc per-family admission correction — source proposal only

The original frozen analysis is preserved unchanged. Its summary SHA-256 is `e4b807914566d52e61798848344a59455f21f839d70f2faa2fca592f3a2513c3`: five ratios are short-block-inconclusive and 35 are correctness-or-cohort-failed. No new kernels, timings, numerical thresholds, measured samples, or production changes are proposed.

## Observed accounting defect

The producer aggregates all row statuses into `receipt.status`. One COLLIER acceptance interval in N2/rank0/batch1 (quartet32, raw serial159, 134147 iterations) reconstructed to 99,893,971ns, below the frozen 100,000,000ns minimum. That family correctly remains inconclusive for all five ratios. The other seven families completed all 48 quartets with no short intervals. Every full before/after comparison passed; all three subprocesses exited0, cleanup errors are empty, inputs are unchanged, no error/guard/raw-hash field exists, and final elapsed416.58924018696416s is below700s.

`analyze.py::validate_terminal` nevertheless requires aggregate status `completed`. The expected row-local inconclusive status therefore short-circuits its enclosing global-admission try block before later guard/control assertions execute. This does not demonstrate a numerical failure in the seven complete families; those global assertions must be independently executed before any revised admission is allowed.

## Proposed narrow correction

Create a separately named analyzer and output, explicitly labeled posthoc analysis revision2. Keep the original runner, receipt, raw log, source, frozen summary, and all prior failures immutable. Reuse the frozen analyzer's input accounting, initialization, exact snapshots, numerical comparisons, COLLIER pole/status checks, shared iteration checks, order validation, ratio samples, bootstrap procedure, confidence interval, and width gate verbatim.

Replace only the aggregate terminal-status admission with a derived clean-terminal check. Require timing mode, all expected eight coordinates, and the original finite ordered elapsed values within700s; unchanged inputs; all three zero exit codes; no cleanup errors, timeout, global error, guard error, or raw-hash error; verified raw digest; initialization and controls passed. Reject any missing, running, failed, calibration-inconclusive, budget-inconclusive, or otherwise unrecognized row. For this narrow correction, allow only `completed` and `short-block-inconclusive` rows, with no row error. Require48 complete quartets and successful before/after qualification for every row, derive short counts directly from all elapsed values, and require stored row status/counts to agree. Require aggregate status to be `completed` iff all rows completed, otherwise exactly `inconclusive-or-failed` with at least one genuinely short row. No other reason for an unsuccessful aggregate status is admitted.

All original global checks must then run; the terminal check must not bypass any later source/qualification/raw/control validation. For each family, retain `summarize_family` unchanged: any short block disqualifies all five family ratios; 48 valid quartets, exact/numerical admission, 99% bootstrap confidence intervals and maximum2% relative width remain mandatory. Every family and every ratio remains visible. No aggregate speedup is proposed.

## Saved-data controls before analysis

Use copied synthetic receipts and saved raw metadata only. Confirm acceptance of clean all-completed and clean one-short receipts, with the latter still disqualifying all five affected ratios. Mutate each terminal error/cleanup/deadline/exit/elapsed/hash field, each row status/error/count/shape, and mismatched aggregate status to ensure rejection. Verify a real numerical/control/snapshot failure still rejects every dependent ratio. Confirm all40 paired sample arrays, medians, confidence intervals, widths, order strata and slower-pair counts remain exactly equal to frozen analysis; only admission/gate metadata may change. Preserve both original and revised output paths with explicit source/hash bindings.

This proposal awaits ROOT review and authorization before implementation or execution. It is an analysis correction after observing the cohort, not a preregistered rule and not an adoption decision.

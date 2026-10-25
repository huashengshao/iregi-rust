# Independent saved-timing statistics

`timing_statistics.py` uses only the Python standard library. It imports no
producer code and has no import-time computation or I/O. Actual statistical
evaluation is deferred until the root releases the quiet timing lease and the
caller admits the terminal saved corpus. This folder currently contains source
and tiny deterministic mock tests, not measured timing results.

API:

```python
summarize(left, right, admitted=True, short=False)
summarize_stratified(left, right, numerator_first, admitted=True, short=False)
```

`left` is the TIRust numerator latency sequence. Pairing is by original quartet
index, never by sorting the timing sequences. `summarize` returns `samples`,
`median`, `ci99`, `relative_ci_width`, `gate`, `historical_gate`, and
`slower_pairs`. `summarize_stratified` requires exactly 48 pairs and a boolean
order mask with 24 numerator-first and 24 denominator-first entries; it adds
`order_strata` with the same summary fields for both subsets.

The median interval uses 10,000 medians of `random.Random(173).choices` samples,
resetting the RNG for each complete summary or stratum. Quantiles interpolate
linearly at `fraction * (N - 1)` for fractions 0.005 and 0.995. Relative width
must be at most 0.02. Historical gates preserve the exact order of checks and
strict/non-strict comparisons in `validation/benchmark/run.py::ratio_summary`.

The nested historical gate is `correctness-failed` when the family is rejected
or short. The outer `gate` instead reports `correctness-or-cohort-failed` or
`inconclusive-short-block`. Incomplete families return
`inconclusive-incomplete-family` without computing a bootstrap. Empty generic
input returns `None`. Malformed lengths, nonfinite/nonpositive durations, and
unbalanced complete order strata reject explicitly.

Six tiny source-only tests use injected bootstrap results or a fake RNG with
two tiny draws. No real bootstrap, timing corpus, numerical implementation,
compiler, or executable under test was run. `source-review.json` and
`source-only-test-results.json` pin the implementation and exact source-only
scope. The integrating saved-data auditor owns correctness, lifecycle, hash,
calibration, quartet-order, short-block, and quiet-release admission.

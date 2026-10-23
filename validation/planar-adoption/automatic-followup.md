# Separate follow-up: automatic planar fallback

This is a source design only. The standalone adoption patch does not implement it.

The ordinary `Workspace::reduce_batch` outer boundary must first complete the
existing implementation, including its current PV→IBP retry. Only an `Ok` batch
result with failed, originally valid lanes is eligible for an additional planar
attempt. A malformed batch or another global error keeps the existing return path.
Use the original input rows, full ordered Dual shape and current requested accuracy.

Eligibility is structural and narrow: ordinary requested PV or Hybrid, five
propagators, rank≤7, unit powers, dimension shift zero, preserved Cartesian inputs.
Exclude certified children and analytic specializations. Explicit IBP behavior is
unchanged. Store a lazy boxed certified workspace inside the ordinary workspace;
fixed-chart children carry no such capability, preventing recursive retries.
Retain the exact eligibility information through ordinary Dual preparation.

Pack failed eligible rows once, call the certified wrapper once, and scatter by
the retained original lane indices. That wrapper performs full-Taylor rank and
chart certification and groups numerical work by chart. No outer sample loop
may invoke individual reductions. All original rows and successful primary
coefficients stay unchanged.

Replace a primary failure only when the corresponding certified result is
`Success`, its basis and full metadata match, and the coefficient buffer has the
expected width. On unresolved certificates, nonplanar/transverse jets, numerical
guard failures or chart preparation failures, preserve the original status and
append the attempted-path diagnostic. A fallback certificate's `InvalidInput`
must not relabel an originally valid ordinary input. An error from the auxiliary
wrapper is recorded on the attempted lanes after completed child work is collected;
it does not manufacture zero coefficients or erase the original failure.

Aggregate actual argument, master, reduction and analytic work with checked
counters, including work completed before errors. Count fallback attempts per
stage, and count success only when a failed primary lane becomes successful.
Preserve previous fallback/analytic flags and add the attempted path's flags.
Certificate-only failed attempts must remain distinguishable from numerical
chart attempts. Add the child's stage times to the parent, while the single outer
timer measures the entire call and closes on every return path. Propagate profiling,
accuracy changes and clone ownership to an already-created child.

Required focused tests before enabling this path:

- Ordinary PV and Hybrid batches containing a stable nonplanar primary lane,
  two certified planar successes, bad mu, and a planar numerical-guard failure.
- The unchanged binary64 spatial family remains unsuccessful; the original
  failure is retained even after its certified numerical attempt fails.
- Ordered rectangular and six-component mixed jets: tangent lanes can succeed,
  transverse mixed components preserve the primary failure plus certificate
  diagnostic, and a failed lane cannot contaminate another lane.
- Empty, singleton, odd-size, reordered and chunked batches; metadata/basis
  equality, exact attempted/success counters, profiles after global errors,
  accuracy changes and independent cloned workspaces.
- A fixed-chart child never constructs or invokes another planar fallback.

Full rank-seven standalone precision/Dual evidence remains a prerequisite for
broad rank-seven claims; it does not replace these automatic-dispatch tests.

# TIRust four-engine whole-call protocol v3

Version 2 failed its initial exact CONTROLS preflight before any calibration or
performance sample. Its source, readiness and failed raw records remain immutable.
Version 3 adds explicit untimed preparation in the original qualification order;
all exact snapshot and numerical admission gates stay unchanged. The initialization
study is preserved in validation/selected-native-initialization-order. It found
stable within-process results and exact saved-snapshot reproduction under CASE-first,
with small CONTROL-first differences; it did not prove an instruction-level cause.
ROOT must separately approve the new untimed preflight and grant a quiet window.

Before CONTROLS or any timed request, send all eight original TIRust CASE requests
in order (N2 rank0/rank1 then N3 rank0/rank1, each batch 1 then 32), immediately
repeating each once: exactly 16 requests. These are the same public calls as the
original optimized qualification, with no engine selector and empty timing arrays.
Check full arrays/statuses/master captures against the existing exact snapshots.
Then run CONTROLS and require exact equality to the original qualified controls.
Retain every preparation response and make the analyzer independently verify the
sequence and values. This is process-global symbolic preparation, outside the
acceptance interval; numerical result cache policies are unchanged. The ordinary
per-family before/after admission and exact own-output checks still follow.

A new preflight mode performs this sequence, all eight four-engine before/after
numerical checks, and final CONTROLS with no calibration or acceptance requests.
Its process/cleanup/postguard budget is 120 seconds; all failed/unrun rows remain visible.
Only a separately reviewed passed preflight and immutable readiness can enable
an independently granted 700-second timing cohort. No prior timing sessions are
combined. The pinned historical prototype is tested; current production Rust may
have advanced. Immutable compiled archives and copied prototype sources are guarded,
while historical successful build records retain the original source identities.
No equality with the mutable current production tree is claimed.

The four engines are baselineTIRust (the qualified complete public call with
Symbolica masters), candidateTIRust (the same complete call selecting existing
native A0/B0/C0 for plain f64), original IREGI, and COLLIER1.2.10 COLI mode1.
External TIRust labels map to the unchanged probe selectors baseline/candidate.
The optimized Rust binary, core libraries, scalar adapter, IREGI executable and
validated COLLIER33704d executable are unchanged. Python adds one COLLIER
subprocess. There is no new numerical implementation or Fortran rebuild.

Use exactly the eight frozen massive Euclidean N2/N3 rank0/1 batch1/32 families
(input SHA65d0d2fd554807478569ac88b6d689c9132ce541e98cfb2a3a55b8ef98e5c7ef).
Every family has48 quartets: each of the24 engine permutations twice, shuffled
with Random(173). All four engines use one shared positive integer iteration
count. After ten warm calls, use at most eight calibration rounds; if the
FASTEST measured engine is below100ms, set
n=max(n+1,ceil(n*110,000,000/min_elapsed_ns)). All four intervals must reach
100ms before acceptance starts. Counts remain fixed through all48 quartets.
Capture/profiling are disabled and Rust arguments/results black_box protected.
Each Rust block uses one clock pair; status checking and owned result drop stay
inside the interval. Both unchanged Fortran drivers expose floating ns/call;
their elapsed time is reconstructed as ns/call times integer iterations and is
not described as exported raw integer clock ticks.

The cap is fixed at700 seconds before any observations. The minimum acceptance
workload grows from100.8 seconds in v1 (8*42*3*100ms) to153.6 seconds here
(8*48*4*100ms), before slower-engine imbalance, calibration and admission costs.
A700-second bound gives additional room for the fourth engine and larger balanced
cohort while imposing a hard resource ceiling. It does not promise all families
fit under extreme engine imbalance. Budget-inconclusive and unrun rows remain
visible; neither timing values nor confidence intervals can increase the cap.
Short acceptance intervals remain in raw data and mark the family inconclusive.
No rerun or case exclusion is allowed to narrow a confidence interval.

Before and after each family, compare every tensor/Laurent coefficient from all
four engines. Capture all six scalar-master outputs for each TIRust variant
outside timing and compare exact own snapshots to optimized admission. COLLIER
uses CHECK with zero warmup and one iteration for full native [UV single, IR
single, IR double, finite] arrays and all three independently varied pole
parameters; require every probe error finite, nonnegative and<=1e-12. Reuse the
independent UV identities. These checks stay outside acceptance timing. BENCH
requires pole_check_errors=null, exact own arrays/status/mode/clock identity,
complete finite outputs and success for every lane. The pinned COLLIER driver
folds ErrFlag==0 and AccFlag==0 into stability on every call; numeric flag values
are not exposed and will not be invented. Its IR slots are zero only within this
fixed massive IR-finite domain, verified by the separate pole probes.

The only five timing ratios are:

- baselineTIRust / IREGI
- candidateTIRust / IREGI
- baselineTIRust / COLLIER
- candidateTIRust / COLLIER
- candidateTIRust / baselineTIRust

Every ratio uses matching quartet rows from this cohort. Never multiply medians
from earlier IREGI/COLLIER or native/Symbolica sessions. Use the existing paired
median bootstrap with10,000 resamples,99% intervals and2% relative-width rule.
Retain raw samples, order strata and all failed/inconclusive families. Every
new ratio definition and nested summary uses TIRust as the numerator. Historical
COLLIER/IREGI-only evidence remains unchanged and separate.

Pre/post hashes bind sources, helper imports, executable/library provenance,
inputs, qualifiers, protocol and ROOT's immutable quiet manifest. Preserve the
complete raw response log with its digest and require all three subprocesses
to exit0. Posthoc statistics wait until ROOT releases the global quiet window.
A private candidate result cannot replace the current production gate before
any eventual adoption and combined-source benchmark.

Executable copies are frozen by digest before launch. Every successfully or partially
created child is tracked and cleaned independently on failure. Terminal exit/error
state is saved before post-run hashes; failed hashes and any deadline overrun
disqualify admission. Cleanup durations are recorded separately and cannot silently
extend the accepted fixed cohort bound.

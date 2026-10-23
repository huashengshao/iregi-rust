# Corrected dispatch: fixed interfaces pass, broader capture remains partial

The corrected official Bten/Cten/Dten dispatch passes every one of the16 fixed
N2/N3/N4 per-engine interface regressions exactly: native statuses, accepted
arrays and pole probes. All retained IREGI comparisons also pass exactly.
The six original N4 COLI accuracy rejections remain rejected. This does not
rehabilitate the generic attempt001, which remains separately preserved.

The new driver-only link used the same immutable COLLIER archive. All15
protocol tests passed. Correctness completed in8.991 s, with source, input,
module and executable guards unchanged. No performance cohort was run.

N5 COLI mode1 singleton ranks0/1/2 return accepted complete Cartesian/native
Laurent arrays, agreeing with original IREGI at maximum normalized error
`4.629855701881312e-12`. DD mode2 returns its native `ErrFlag=-10` on those
three rows, so none is a qualified DD comparison. These numerical agreements
still require an independent durable-package audit before reporting new
qualified coverage.

Two separate failures prevent broader qualification:

- Every higher-point batch32 row fails before transport because its unchanged
  base/scaled/mass-deformed cycle contains different renormalization scales.
  The frozen Fortran BENCH header has one common scale per request. Inputs
  were preserved; no scale was normalized or substituted. The next transport
  adapter must partition lanes by exact scale, retain every complete group
  response, and reassemble the original lane order. This is a wire-format
  correction, not a change of kinematics or normalization.
- The first N6 singleton's COLLIER process aborts with
  `free(): invalid next size (fast)` and SIGABRT. Its backtrace names
  `CalcTensorTNrRed`, `CalcTensorTNr` and `TNten_main_checked_cll`. All three
  original IREGI responses for that row were already captured successfully.
  Later N6/N7 singleton rows retain the process-already-exited error, while
  their original IREGI results are still captured. The library's exact memory
  fault is unresolved; the stack is evidence of the failing path, not proof
  of a particular erroneous source statement.

The full capture has34 fixed rows and145 complete responses:13 accepted-COLI
rows (10 retained old rows plus3 new N5 singletons),6 retained N4 rejections,
and15 transport/process failures. All rows remain visible. The artifacts tar
contains the exact abort stderr, and compressed raw JSON contains every
response collected before each failure. No failed case is represented as a
successful zero, and no missing higher-point result is counted as agreement.

A next diagnostic protocol should isolate each failing COLLIER policy/case
in a fresh process so one abort cannot stand in for every later case. Native
failure, raw diagnostics and successful responses must remain distinct.
The actual N6 fault requires an independent diagnosis before deciding whether
an official alternative API/configuration is appropriate. No source patch,
padding workaround, rank inflation, threshold change or different fixture
has been applied. All further numerical/build work is on hold for the ROOT
quiet window; source-only review can proceed.

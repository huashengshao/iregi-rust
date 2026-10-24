# Explicit six-point API: isolated integration qualification

This capsule qualifies the exact V2 source patch in an isolated build. It
does not substitute for the separately recorded production application and
Cargo build. The ordinary API is unchanged on the complete paired fixture
set; the new explicit `SixPointReductionPlan` / `SixPointWorkspace<T>` accepts
N6, ranks 0 through 3, unit powers, dimension shift zero, supplied Cartesian
shifts, Preserve, PV, native IREGI normalization and tensor components.

The public workspace accepts one ordinary component. Generic Rust typing is
broader than the high-point numerical evidence. Numerical Dual inputs,
binary64/DoubleFloat high-point accuracy, arbitrary complex masses, generalized
powers/shifts, broader kinematics, N7, rank7 and performance parity are not
qualified here. Unsupported settings reject explicitly. A failed lane cannot
be counted as numerical agreement or expose partial coefficients.

## Qualified checks

- All 34 selected tests passed. Other tests in the same binary were not run.
- All 12 ordinary baseline/candidate cases match exactly, including full
  values, precision, signs, settings, statuses, flags, diagnostics and counters:
  f64/DoubleFloat/Float128, including the existing ordered Dual settings.
  The 42 successful lanes and 18 matching rejection controls are counted
  separately; the latter establish rejection parity only.
- The retained base N6 rank3 fixture passes all 140 native Laurent slots at
  both Float128 and Float256/request53 against untouched stable original IBP
  with the unchanged dimensionally normalized 1e-10 tolerance. Each precision
  has 105 exactly zero pole slots. The full precision comparison passes 2^-80.
- Eleven rank2 Float128/request53 calls cover singleton/scaled inputs, failed
  neighbors, reorder/chunk/repeat behavior and empty batches. Seventeen
  successful lanes contribute all 1020 moment slots and 68 contraction slots;
  seven rejected lanes and two empty calls remain explicit. Certificate and
  executor counters, flags and resets are checked separately.

The contraction uses the existing Symbolica adapter for
`2 - 3*q0 + q1 + 4*q2*q3`. Its saved-data oracle is the complete rational sum
of captured components and the corresponding untouched original IBP sum.
The scale is `sum_j |c_j| Q^(rank_j - 8)`; no tolerance was enlarged.

## Provenance and reproduction

`qualified-v2/integration.patch` is the tested patch. V2 changed only malformed
input validation relative to the first source candidate. The original source
and unexecuted runner drafts, including the independently found lifecycle
defect and its repair, remain in this capsule. No failed attempt is relabeled
as a pass. `payload-origins.json` maps every copied byte to its original path.

`source-v1/sources.tar.gz` contains 59 candidate plus 44 original baseline
members under `candidate/` and `production-baseline/`. The 59-member
`qualified-v2/sources.tar.gz` contains the actual compiled V2 source and all
seven compile-time fixtures. The production baseline and source archives are
distinct from the initial source manifests. Compiler flags, all native/extern
dependencies, exact commands and output hashes are recorded in the approved
protocol and build/run receipts. No live dependency search fallback was used.
The six executable/archive outputs are retained in the original build folder
and bound by SHA256; they are intentionally not committed in this capsule.

Restore those archives at the target locations declared in the protocol,
restore the recorded dependency closure, and inspect `harness_common.py` before
reproduction. The runners refuse to overwrite prior attempt directories.
An independent reproduction must use newly named attempt directories and new
receipts; it must not change or reuse the approval/terminal records here.
The recorded sequence is build, exact tests/comparison, ordinary baseline,
ordinary candidate/comparison, public128/comparison, public256/comparison, then
lifecycle/comparison. Source the project environment and private Symbolica
license environment without printing it. No license value is stored here.

Every child ran in an owned process group, with cleanup after leader exit or
interruption and a terminal event before hashing. Aggregate caps were 180s
for build/exact/public/lifecycle and 120s for each ordinary capture, with 25s
build or 20s runtime reserves. All 19 owned groups were confirmed absent after
the full window. These durations are diagnostics, not performance benchmarks.

The previous private rank7 discrepancy remains in
`validation/highpoint-thin-n6-rank7-phase`; its failed original-reference gate
is not changed by this restricted rank3 integration checkpoint.

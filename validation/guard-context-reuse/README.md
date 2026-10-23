# Isolated guard-context reuse experiment

This experiment compares exact core sources at `80949db` with a private candidate
under `target/guard-context-reuse`. It follows the rejected repeated-term cache
experiment; no term estimates are cached here. The isolated experiment passed
qualification and was approved for adoption. `adoption.json` and `adoption.patch`
record the subsequent production rebase onto `d1a4b8e`, preserving the ordinary
evaluator's existing stack allocation. Current-source checks are recorded
separately from the original experiment. `adoption-qualification.json` records
76 passing current-source tests and exact agreement on a fresh 120-snapshot
comparison against the current baseline, using the frozen full-feature
dependency archives. This does not claim a fresh full-workspace rebuild.
`final-adoption-qualification.json` additionally binds the final source after
removing only the experimental constructor logging hook and updating its module
documentation; all 14 added context/lifecycle tests passed on that cleaned source.

The candidate constructs the requested tolerance and prototype roundoff unit
once per numeric workspace, updates tolerance when the requested accuracy
changes, and lazily reuses the physical scale and signed dimensional powers
within a single compact lane. It resets all lane values unconditionally. Distinct
dimensions receive dense slots during workspace preparation. Operation-factor
casts, contribution sums, norms, reference scales, target products, precision
provenance and diagnostic ordering retain their original implementation.

All numeric operations use the existing Symbolica numeric APIs. In particular,
negative powers still use `pow(abs).inv()` and exponent zero retains the selected
scale's precision. Equal-value Float lanes are never treated as cache keys.
Fallback, analytic-profile and precision-rescue workspaces own independent state.

`prepare.py` reconstructs both sources and records their hashes. `build.py`,
`build_tests.py` and `build_probes.py` use identical frozen dependency archives and
matching compiler flags, pinned to CPUs 10 and 11. Candidate test-only wrappers
also compare each existing direct guard test against its uncached implementation.
`context_tests.rs` and independently prepared `execution_tests.rs` cover precision
ties, resets, clone independence, accuracy updates, existing and late children,
zero/invalid inputs, and error precedence. `run_checks.py` records test counts,
commands, binary hashes before/after execution, and retained logs.

The public protocol compares 120 snapshots, including exact represented output
values, precision metadata, signed zeros, Laurent/Taylor ordering, statuses,
diagnostics and execution counters. Structural profile lines can be enabled by
`IREGI_GUARD_CONTEXT_PROFILE=1` in the private instrumented snapshots; these count
dimensions and checks without making any timing claim. Production omits that
experimental environment/logging hook. The paired performance probe runs only during a coordinated
quiet window. `decision.json` binds the original evidence: 62 baseline and 76
candidate targeted tests passed, including 14 added regressions, and all 120
public snapshots agreed exactly. Two pre-existing expensive rescue tests remain
ignored in this targeted run; the broader unit suite is not claimed here.

The twelve paired timing rows produced six qualified improvements, no qualified
regressions, and six inconclusive rows. Qualification requires a 99% paired
bootstrap interval with width at most 2% of its median latency ratio. The largest
qualified changes were scalar tadpoles: candidate/baseline ratios 0.8342 for a
singleton and 0.7637 for 32 rows. All rows, including noise, remain in
`performance-analysis.json`. These are isolated direct-rustc diagnostic results,
not full IREGI reference performance acceptance. Do not combine these gains
multiplicatively with separate allocator or native-master experiments.

Source `scripts/env.sh`, then the private `.local/symbolica-license.env` when
running numerical qualification. The license value is neither recorded nor
committed. Public license capability evidence is retained separately in
`validation/concurrent-workspaces/license-capabilities.json`.

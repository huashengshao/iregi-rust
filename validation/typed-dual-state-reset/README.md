# Public typed-Dual observation reset

`Workspace::reduce_dual_batch` now clears its previous execution statistics,
profiling times and diagnostics before validating typed inputs. Static and dynamic
Dual adapters both delegate here. Rejected calls retain their requested row count;
the reset performs no multiplication, and `usize::MAX` still reaches the existing
checked overflow rejection. Numerical formulas, inputs and evaluator caches are
unchanged.

Two exact integration tests execute real work before each rejected call:

- `typed_errors_clear_real_bubble_work_and_legacy_boundary_diagnostics`: the
  existing threshold-1/4 timelike B0 fixture creates actual recorded equality-branch
  diagnostics, alongside an invalid-scale lane. Truncated input, incompatible
  dynamic shape, malformed component storage and row-count overflow must clear the
  previous observations. Input preservation, owned earlier outputs and recovery
  are checked.
- `genuine_mass_dual_recovers_after_malformed_typed_length_and_shape`: a genuine
  two-component A0 mass derivative evaluates nonzero before malformed static
  length and dynamic shape probes; valid evaluation then recovers exactly.

The final locked/offline actual-Cargo build passed in 18.06 seconds on CPUs 20/21.
The exact listing and both selected tests passed in 15.36 seconds on CPU 22, within
180/20 and 90/15 second total/cleanup budgets. All captured source guards remained
unchanged; all owned process groups were cleaned. These timings establish bounded
correctness execution only.

The first compile failure (test referenced a crate-private observation accessor)
and the subsequent runtime fixture failure (zero threshold produced no branch
message) remain intact, with their precise earlier test sources. The final test
uses the pre-existing public boundary fixture and retains the diagnostic assertion.
The original source-only `proposal.json` records the earlier planning state.

Run `python3 validation/typed-dual-state-reset/check.py` from the project directory.
It checks the retained receipts, exact test logs, guard bindings, source delta and
preserved failures without compiling or evaluating integrals. Shared source context
is inherited by hash from the ordinary rank-seven and literal six-point capsules;
this 141 kB payload stores the two affected sources, small source versions,
patches, runners, Cargo artifact messages and logs. Test executables are omitted
with their exact hashes retained. This is targeted public API regression evidence,
not a dependency closure, performance result or new general Dual qualification.

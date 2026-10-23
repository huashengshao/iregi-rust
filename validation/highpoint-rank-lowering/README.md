# Private Cartesian high-point rank lowering

Production source baseline: `06706e2a1e4f0082889a53187c80bbe97803340f`.
This directory contains an isolated Symbolica recurrence experiment, not an
adopted production change. Its domain is preserved Cartesian inputs, unit powers,
zero dimension shift, and ordinary N6/N7 PV tensors. The existing rank-zero path
and pentagon routing are unchanged.

`source-initial.json`, `source-prepared.json`, and `source-final.json` bind the
snapshots, candidate patch, and added exact tests. `build.json` binds independently
compiled baseline/candidate public drivers to the frozen historical 112-Rust,
three-native archive closure and toolchain. Core builds are development-profile
diagnostics; these are not optimized timing comparisons.

The exact gate is recorded in `exact-qualification.json`: fifteen regular
integrand fixtures, sixty Cartesian directions, and 576 exact rational mixed
Taylor constraint coefficients. The fixtures include translation, propagator
permutation, momentum reversal, complex masses, a changed active origin, and an
independent perpendicular loop square. Structural singular cases are retained.
The initial test incorrectly treated the retained N6 first-mass-plus-one fixture
as regular; its two-pass/one-failure output remains. The corrected exact test uses
a separate half-unit mass perturbation and tests the original singular input as
a no-solution control. The v2 evaluator API compile failure also remains; v3 uses
Symbolica's existing rational-ring evaluator.

The first public numerical captures are:

- `n6-rank1-baseline-128.json`: old independently compiled public path rejected
  the lane with nonfinite reduction coefficients; no numerical array is exposed.
- `n6-rank1-candidate-128.json`: private candidate returned Success and all five
  moments × four native complex Laurent slots at Float128/requested53.

`qualify_rank1.py` is the separate candidate-to-original comparison. It binds the
full exact source/build/run chain, the original reference executable and retained
reference capture, the complete runner guard inventories, and every numerical
slot. It explicitly reports paired baseline/candidate agreement as unavailable
when the old path rejects the lane. `compare_lowrank.py` retains the stricter
two-successful-array comparison for future cases where both paths succeed.

The source-only v4 test snapshot adds actual `moment()` dispatch witnesses:
twelve cases and 48 independent nonzero Laurent-slot identities, including
wrong-rank child sentinels, all four selected numerator directions, the unchanged
rank-zero path, and structural fallback. It remains separate from the completed
v3 gate until its own build/run record succeeds.

Reproduction runs must start in the project directory with:

```sh
source scripts/env.sh
source .local/symbolica-license.env
```

The executable `run.py` records bounded commands, immutable inputs and output
hashes. Existing outputs are never overwritten. Initial bounds are 240 seconds
for the paired build, 100 seconds for each separately recorded corrected test
build, 60 seconds for exact tests, and 180 seconds per rank-one public capture.
Higher-rank probes and their bounds require separate records. Source-only future
composition ideas are in `docs/research/highpoint-batched-child-dispatch.md`;
they do not broaden this experiment's scope.

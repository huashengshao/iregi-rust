# Lazy scalar Cayley solve qualification

The promoted change uses Symbolica `Matrix::solve(ones)` when a scalar recurrence
only needs `b = R^-1 1` and `B = sum(b)`. Raised powers still request the complete
inverse; a cached scalar geometry upgrades before any inverse entry is accessed.
Unique-solution and exceptional-kinematics semantics are unchanged. No stability
threshold, operation factor, or scalar-master implementation changed.

The patch is confined to `crates/iregi-rust/src/ibp.rs`: 131 added and eight removed
lines, including two regression tests. `promotion-proposal.json` records the exact
baseline, candidate, patch and production hashes. The baseline file is from commit
`5c9e3dd3f60c9d16c38704865cd8c1d3ed855176`. `independent-review.json` records the
separate review before promotion.

## Qualified checks

- Baseline IBP: 24 tests passed. Candidate IBP: 26 tests passed, including unique
  solve/singular rejection and compile-driven scalar-to-full-cache upgrades.
- Each variant passes 400 independent triangle Gamma coefficient identities and
  80 generalized power/dimension identities. That triangle has singular Cayley
  `R`, so these do not replace the regular-matrix checks.
- A side-by-side exact Symbolica comparison covers regular matrices for one
  through five propagators and shifts -3 through +4: 44 successful requests agree
  in all four Laurent slots, and four unsupported requests return identical
  errors. Genuine D6 leaves are tested both disabled and enabled. Constrained
  regular C0/D0 cases preserve their original complete master leaves.
- The supplied-Gram public N6 fixture retains exact rank-four certification and
  rejects an incompatible Gram lane. Baseline and candidate binary64 both reject
  a valid lane at `ibp_0_node_14` for estimated cancellation. This is guard parity,
  not proof that the rejected numerical value would have been inaccurate.
- Candidate Float128 and Float256, both with **requested accuracy 53 bits**,
  accept both valid lanes and isolate the incompatible lane. All poles are zero.
  All four slots converge; the finite-slot difference, normalized by `35^4`, is
  `3.30930511165431783718881296037556292348e-32`.
- The Float256 finite coefficient is
  `4.2986076669270135250890508385335492354527879747290809724950896812967315e-8`
  in OneLoop normalization. It differs from the independent direct-simplex
  quadrature estimate by `1.5251e-23`, below that oracle's conservative **estimated**
  uncertainty `6.11e-22`. This uncertainty is not an interval-certified bound.

The Float test does not claim delivery of 128- or 256-bit requested accuracy.
Public N7, mixed-Dual integration, the combined current-source integration gates,
and controlled performance qualification remain pending in this evidence set.

## Retained failures and timing scope

`runs/vector_public_n6.*` preserves the original candidate public test failure:
it reached evaluation but unwrapped a lane rejected by the unchanged guard.
`runs/alias_public_n6.*` preserves the 180-second baseline timeout during the
coordinate comparator. Neither run is successful numerical agreement.
The later certified-only probe reports the baseline status before attempting
that unnecessary comparator and establishes the guard parity above.

Single-run chart preparation was about 77.6 seconds for the matched baseline and
17.2 seconds for the candidate; the later candidate Float probe prepared the chart
in 16.7 seconds. These are **diagnostic spans**, not performance acceptance: there
are no repeated controlled measurements or uncertainty estimates here. The final
certified-only probes were launched with `taskset -c 0`; the quadrature ran on
CPU12. All original logs, bounds, exit statuses and hashes remain in `runs/`.

## Provenance and reproduction

The two source variants used the same private dependency archives. `archives.json`
records 51 copied artifacts and the remaining immutable dependency links;
`post-build-archive-check.json` records that they stayed unchanged. Build manifests
contain complete commands, source hashes, dependency hashes and binary hashes.
Compiled binaries and the 1.37 GB archive snapshot remain generated artifacts
under `target/certified-scalar-matched`; they are not committed. These manifests
identify the historical experiment and must not be relabeled as a later build.

The exact test probes and runners are retained in `reproduction/`. They use the
historical `target/certified-scalar-matched` layout recorded in the manifests.
`frozen_certified_scalar.rs` preserves the fixture source identified by the oracle.
Reconstruct the baseline file from the recorded commit, apply the retained patch
for the candidate, and build each copied source with the recorded arguments and
matching dependency/source hashes. A fresh build against newer dependencies is a
new qualification run, even if all tests pass.

With the preserved artifacts available, the final bounded checks are:

```sh
source scripts/env.sh
taskset -c 0 python3 target/certified-scalar-matched/run_probe.py fresh_alias_status alias status --limit 120
taskset -c 0 python3 target/certified-scalar-matched/run_probe.py fresh_vector_float vector float --limit 180
```

The runner refuses changed binary/source hashes or a changed independent oracle.
It validates the oracle fixture, normalization, and positive finite uncertainty
before launching the Float test. Binary64 status-test success is diagnostic only;
the emitted statuses determine its finding. `independent-n6/README.md` documents
the six Gauss-Jacobi rules, two mappings, library provenance and reproduction of
the defining-integral check. `files.sha256.json` hashes the retained evidence.

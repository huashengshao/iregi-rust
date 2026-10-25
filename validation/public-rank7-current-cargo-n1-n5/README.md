# Actual current-Cargo N1–N5 rank-seven qualification

This capsule preserves ten successful ordinary public-API captures made with the
actual Cargo-built `highpoint_public` executable, SHA256
`8166f6e799b241c7e09550a6e970d5e89d2386a2bda3930d97794b4560ec1f93`.
Every topology N1–N5 uses all three exact conditioned-mass fixture rows,
Float128 and Float256, requested accuracy53bits, rank7, PV, unit propagator
powers, native IREGI normalization and raw Cartesian components. Every capture
returns all330moments and all four separated Laurent coefficients. Inputs are
preserved and represented exactly; stored component precisions retain
Symbolica's cancellation-adjusted metadata separately from working precision.

The saved gates compare39,600complete complex slots to the separately audited
original-IREGI quadruple IBP anchors,19,800precision-pair slots,13,200uniform
scaling slots,19,800exact IR zeros and996exact convergent UV zeros. Reference
agreement uses a mixed absolute/relative1e-10tolerance after dimensional
normalization. Precision convergence and exact scaled-input homogeneity use
2^-80. Reference PV failures are preserved in the inherited reference capsule
and are never accepted as anchors. No successful output is replaced by zero.

The exact current64-source context is stored once in `sources.tar.gz`, including
both crate manifests, the root manifest/lock, all core/master Rust files and the
public example. `source-inventory.json` links every byte to the actual build's
source snapshot. Later capsules can inherit this archive and add a small source
overlay. Earlier pre-Cayley snapshots are not substituted for this context.
The actual51-test Cargo prerequisite, actual executable artifact metadata,
source/runner review, ten owned capture receipts/logs/results, comparison and
independent saved audits are retained in `evidence.tar.gz`. Native executables
and caches are deliberately omitted; historical identities remain explicit.

The reference parent is `../quad-original-iregi-small-n-rank7`, which includes
all26requested reference outcomes, known PV failures,14new eligible IBP arrays
and the inherited N5base anchor. It in turn inherits the original-IREGI source
and precision audit capsules. This capsule reuses that provenance instead of
copying the large reference closure.

Run the portable checks from the repository root:

```sh
source scripts/env.sh
python validation/quad-original-iregi-small-n-rank7/check.py
python validation/public-rank7-current-cargo-n1-n5/check.py
```

The checker uses only the Python standard library. It validates closed archive
inventories, restores source identities and independently replays every saved
numeric gate. It never starts native code, compilers, algebra systems, reference
integrals or process probes. Optional `--reconstruct target/NAME` writes restored
source/evidence aliases for inspection. It does not rebuild a native executable.

For a new actual numerical reproduction, use the repository's pinned development
environment and licensed Symbolica setup, build the unchanged `highpoint_public`
example, then apply a new explicitly bounded capture recipe to the same exact
inputs. The retained controller documents the historical commands and budgets;
its original paths and no-overwrite guards intentionally preserve those
attempts. No license literal is included in this capsule.

All ten attempts completed, with30/30successful sample lanes, no rejected or
omitted cases, no retry, no timeout and no cleanup failure. All observed
arguments and recurrence operations processed the three-row batch; scalar
family batches were1,2,3,4,4andmaster rows3,9,21,45,90forN1–N5at both precisions.
Every fallback/analytic flag was false for this regular family. The retained
independent lifecycle audit establishes historical process-group absence.

This is a restricted correctness milestone. It does not qualify arbitrary
rank-seven kinematics, other arithmetic types, Duals, dotted propagators,
dimension shifts, IBP/Hybrid requested modes or physical graph preparation.
Its diagnostic durations are not performance measurements or comparisons.

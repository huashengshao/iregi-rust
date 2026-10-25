# Private rational-field routing preparation: sixteen exact algebra cases pass

The isolated proposed `ibp.rs` module compiles, and all original sixteen selected
exact algebra cases pass: thirteen new helper/compiler-API cases and three
existing recurrence cases. This qualifies a **private preparation experiment**.
It does not change production or qualify complete high-point integral outputs,
current Cargo integration, derivative accuracy or performance.

The proposal keeps the existing constant-first and homogeneous denominator
relations, propagator power/dimension recurrences, active-index order, aliases
and structural caches. It changes only the routing linear solve's coefficient
domain for a narrow eligible subset. Symbolica owns all polynomial conversion,
matrix elimination, exact solution checks and expression conversion. Explicit
affine matrices of at most five rows/six columns use its rational-polynomial
field over exact rational or Gaussian coefficients. Other syntax and larger
systems retain the original AtomField path; no floating literal is rationalized.

The normal generic reduction-plan path is eligible because
`compile_scalar_tensors` introduces bare squared-distance aliases before forming
the Cayley matrix and registering routing. `ScalarCompiler::with_aliases` alone
only enables recurrence aliases. Actual compiler API tests verify generic N6/N7
distance-alias input, structural cache reuse, and an unaliased quadratic family's
preserved AtomField fallback. Other cases cover fractional/Gaussian coefficients,
underdetermined and homogeneous solves, later feasible constraints, bounded
admission, exact denominator identities, certified covectors, repeated powers
and negative dimension shifts.

The harness imports the actual proposed module and reuses immutable historical
native Symbolica archives. It does not rebuild dependencies or establish the
later current-Cargo feature/source-build closure. The frozen source proposal,
research note, exact command/dependency inventories, reviewers, raw logs and all
intermediate failures are in `source-results.tar.gz`; compiled executables and
credentials are excluded. The executable hash remains recorded for provenance.

| Stage | Retained outcome |
| --- | --- |
| First build | Failed with 48 missing `CARGO_CRATE_NAME` diagnostics; no executable or tests. |
| Corrected build | Passed, 24.535s overall; only the standard compile-time crate-owner environment and fresh paths changed. |
| First exact stage | Canceled during a ROOT scheduling race, 42.172s; nine cases fully guarded. A tenth child passed but its postguard was interrupted, leaving it unadmitted; six later cases did not run. |
| Original CPU6 continuation draft | Preserved unexecuted. |
| CPU8 continuation | All seven remaining admissions passed, 52.359s within the unchanged 300s/25s reserve/120s-per-case limits; the earlier admitted nine were not rerun. |
| Combined gate | All sixteen unique original cases pass; full compiled listing contains 39 cases. |

These durations verify supervised lifecycle limits and include provenance work;
they are **not performance benchmarks**. ROOT independently checked all 176
protected inputs, two exact dependency-directory inventories, retained binary,
strict logs and listing, CPU8 commands, complete original gate and owned-group
absence. The earlier failed/canceled receipts remain unchanged.

The final protocol is
`db71a781e007593bc67f4c88e19da61aca61b627b07df5a343c6b1686fd38fda`;
the independent saved audit is
`f90159f1026745b9f596104aa083cbd5a7f2d2801c33fd37464f436f6f50abf5`.
`qualification.json` binds the compressed archive and all 82 exact member hashes.

From the repository root, verify the portable saved evidence without loading
Symbolica, invoking Rust, or evaluating an integral:

```sh
source scripts/env.sh
python3 validation/routing-rational-preparation/check.py
```

Before considering production adoption, build the complete private core and
compare full N6/N7 generalized Laurent arrays numerically against unchanged
baseline, original IREGI and higher precision. Include dots, dimension shifts,
exceptional lanes and the existing stability/derivative guards. Actual batching,
native numeric types, public interfaces and measured performance remain separate
gates. Affine partial fractions preserve dimension shifts and cannot replace a
genuine D6 pentagon master.

# Symbolica evaluator patch series

The series applies to `alphal00p/symbolica` revision
`9cdc2949cdb153478c1eca0d40690dc0abfc616e`. `provenance.json` records all three patches
and their source hashes. The retained source is in `dependencies/symbolica`;
its `IREGI_PROVENANCE.json` inventories every upstream or patched file.

The original direct translator copies its inherited expression cache for each
unresolved conditional. A public five-point, rank-seven rescue run exceeded a
240-second preparation limit before numerical evaluation. The same frozen core
source linked to this patch passed all 1,320 coefficient comparisons at 128 and
256 bits in 115.35 seconds. Its first reduction evaluator prepared in 1.784
seconds, with 10.2 billion inherited cache entries avoided. Stability-plan
construction remains the largest preparation stage. These are single diagnostic
runs, with distinct dependency builds; they establish preparation progress and
numerical agreement, not a benchmark speedup or broad domain qualification.
Complete evidence and caveats are in `validation/rescue-pentagon-rank7.json`.

`0001-journal-conditional-cache.patch` replaces cache copies with a journal of
branch-local insertions. Parent expressions remain visible to both branches;
new expressions from each branch are removed before its sibling is compiled.
Nested checkpoints restore overwritten entries and tolerate condition
temporaries already removed by constant-condition pruning. Completed
conditional results remain cached in their parent scope. Algebra, numerical
instructions, public precision types, and license handling are unchanged.

With `SYMBOLICA_SCOPE_PROFILE=1`, the translator reports branch scope counts,
the inherited entries that would otherwise be copied, reverted entries, and
root linearization time. The direct translator with zero Horner iterations
does not run CSE/CPE passes; this patch addresses cache bookkeeping during
direct translation.

Three isolated public regression tests passed, covering conditional reuse,
captured mixed-Dual components, lazy siblings, nested branches, and an
alias-valued constant condition. Existing serialization and JIT assertions
passed. See `validation/symbolica-scoped-cache.json` for that original probe.
The vendored Symbolica library unit suite now compiles with the production
features, and all four focused scope tests pass, including the internal journal
test for nested overwrites and removed temporaries. Its saved IREGI baseline
also passes 57 focused core tests and the full 1,320-coefficient rank-seven
rescue in 109.44 seconds. This later diagnostic run used a preserved source
snapshot and concurrent workspace compilation; it is not a benchmark. Current
integration status, source/archive hashes, and limitations are recorded in
`validation/symbolica-production-qualification.json`.

`0002-identify-vendored-source-version.patch` changes only build metadata. An
explicit `IREGI_UPSTREAM_VERSION` file supplies the display label
`9cdc2949-iregi-scope-cache`, preventing the embedded source from inheriting the
outer project's Git label. The qualified experimental executable predates this
metadata patch; its provenance records its exact source hashes independently
of the displayed version.

`0003-limit-git-watches-to-version-fallback.patch` also changes only build
metadata. When the explicit version file is usable, Cargo watches that file
and `build.rs`; unrelated commits in the embedding project no longer invalidate
Symbolica through Git HEAD/ref watches. Missing, empty, or unreadable version
files retain the upstream Git/package-version fallback and its existing
HEAD/ref/packed-ref watches. The vendored display label remains unchanged.

Six standalone build-script tests compile only `build.rs`, then use temporary
Git repositories to check outer-project commits, version-file edits/removal,
empty and invalid UTF-8 files, packed refs, and environments without Git or a
repository. They assert the emitted Cargo watch directives and version values;
no Symbolica library or numerical runtime is invoked. Evidence is recorded in
`validation/symbolica-build-metadata/results.json`. This metadata test does not
replace numerical qualification of the evaluator patch.

Recreate the retained source in a new directory, from the project directory:

```sh
source scripts/env.sh
python3 scripts/prepare-symbolica-patch.py --vendor \
  --output target/symbolica-vendor-reproduced
```

Omit `--vendor` to retain the entire upstream archive, including optional
benchmark fixtures. The script locates a local checkout containing the exact
revision; an explicit checkout can be supplied with `--source`. It refuses an
existing output directory and verifies patch and retained-source hashes.
Cargo's cached checkout and the supplied reference remain untouched.

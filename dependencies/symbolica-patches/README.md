# Symbolica evaluator patch series

The series applies to `alphal00p/symbolica` revision
`9cdc2949cdb153478c1eca0d40690dc0abfc616e`. `provenance.json` records both patches
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
passed. A separate internal journal unit test is included in the patch but was
not run by that external probe. See `validation/symbolica-scoped-cache.json`.

`0002-identify-vendored-source-version.patch` changes only build metadata. An
explicit `IREGI_UPSTREAM_VERSION` file supplies the display label
`9cdc2949-iregi-scope-cache`, preventing the embedded source from inheriting the
outer project's Git label. The qualified experimental executable predates this
metadata patch; its provenance records its exact source hashes independently
of the displayed version.

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

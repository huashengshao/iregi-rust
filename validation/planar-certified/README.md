# Isolated certified-planar evidence

This bundle preserves partial validation of an **isolated planar N5 prototype**.
It does not promote production support or integrate automatic fallback. All
executed binaries used the earlier isolated baseline and frozen dependency
archives, before production generalized-PV commit `80949db`. The separate rebase
in `candidate/` is source-reviewed and patch-checked only: it has not been
compiled or run.

The proposed domain is preserved Cartesian shifts, five unit-power propagators,
zero dimension shift, PV, and a regular rank-three constant-one chart. Exact
certification checks the entire requested Taylor rank constraint and a nonzero
primal chart determinant. It does not certify numerical conditioning. Rank
seven remains unqualified.

## Recorded outcomes

[qualification.json](qualification.json) is the canonical index of exact test
names, source variants, build/binary hashes, logs, exit codes and time limits.
Its current preflight records supersede the historical preflight observations.

| Scope | Recorded outcome | Limits |
| --- | --- | --- |
| Current constructor/input-domain guards | PASS, tetrahedron binary | Source-matched rerun; no unchecked plan exposed |
| Full Taylor rank and primal chart-unit predicates | PASS, tetrahedron binary | Includes transverse first/second/mixed jets and nilpotent-only charts |
| Rounded-false-zero and homogeneous negative cases | PASS, tetrahedron binary | Includes empty and oversized buffers |
| Rank ≤2 ordinary Float batches | PASS, focused binary | 128/256-bit arithmetic, target53, two charts, seven lanes; all tensor/Laurent slots against boxes and 128→256 convergence |
| Rank ≤2 rotating mixed/second Taylor jets | PASS, focused binary | Float128/target53; reordered six-component shape, MadLoop/multinomial metadata, transverse failure isolation |
| Equal-mass tetrahedron at binary64 | PASS, tetrahedron binary | Three repeated valid lanes and two invalid lanes; all 15×4 complex slots against five independent boxes |
| Original binary64 mass-hierarchy family | FAIL, original and diagnostic variants | Cancellation-monitor rejections remain visible; the older alternate fixture also has nonfinite descendants at lightlike differences |
| All 330 rank-seven moments | TIMEOUT, focused and phase variants | Neither run established tensor/Laurent agreement |

The passing Float and tetrahedron slot comparisons use complex-norm error
`≤ 1e-10 * max(1, |reference|)`; the 128→256 convergence check uses
`≤ 2^-65 * max(1, |reference|)`. The failed binary64 family uses separate real and
imaginary component comparisons when reached. These checks are **not the final
dimensionally normalized acceptance gate**. Core target53 stability guards
remained active. Adding dimensional test scaling and rerunning the comparisons
remain pending alongside rank-seven qualification.

The phase run ended after 180.393 seconds during **stability primal-amplitude
construction**, before rank-seven numerical evaluation or comparison. Its log
records 31.098 seconds for structural chart construction, then 12.245 seconds for
local checks over 13,798 aliases, producing 8,234 checks and 277,942 expression
roots. These are diagnostic observations from individual runs, not performance
benchmarks. All recorded runtime grants used CPU 0; there are no repetitions,
timing uncertainty estimates, or parity claims. The phase run additionally set
`IREGI_PREPARATION_PROFILE=1` and `IREGI_PV_PREPARATION_PROFILE=1`; these surrounding
settings were omitted from the original runner's command arrays and are recorded
explicitly in this bundle.

## Source and provenance

- `source/` is an exact copy of the executed `focused-source` tree. Its 19 Rust
  files match `builds/compile-focused.json`. The `planar_focus` cfg excludes other
  modules' unit tests from this focused executable.
- `variants/` contains independent patches against a fresh copy of `source/`
  for diagnostic-focused, roundoff-diagnostic, tetrahedron and phase binaries.
  Do not apply these patches sequentially. Full resulting file hashes and build
  mappings are in [source-manifest.json](source-manifest.json).
- `builds/` retains the original build manifests/logs and exact hashes of the six
  frozen dependency archives. Binaries and dependency archives are intentionally
  excluded. The frozen `iregi_masters` archive, rather than the current production
  master source, defines the masters used by these observations.
- The initial three PASS logs and original binary64 failure remain as historical
  evidence. Their original wrapper hash `06d82935…` is no longer available; that
  source file was later changed. Matching binary and build-manifest hashes are
  retained, but those historical observations are not attributed to `source/`.
  The three current preflight reruns have matching preserved source.
- The old diagnostic build/runtime commands say `focused-source` and
  `core-tests-focused`. Their recorded hashes belong to the preserved
  **diagnostic-focused** variant and `diagnostic-core-tests-focused`, not the
  current focused binary. Duplicated filenames are resolved by hashes.
- `docs/` preserves design and audit context, including the future fallback test
  plan. Historical status statements in those documents are superseded by
  `qualification.json`; their original repository links may require the original
  `docs/research/` location. `build-context/` retains Cargo manifests/lockfile and
  the pinned shell as context, not proof of an exact historical compiler version.

The separate `candidate/normalized-comparison-tests.patch` proposes dimensional
scaling for tests only. Its JSON records the exact tetrahedron-wrapper baseline
and candidate hashes. Apply it inside the reconstructed tetrahedron `source/`
directory, after that variant patch. It has not been compiled or run and adds no
validation claim to the observations above.

## Reproduction and path remapping

Run from the repository root. Restore a fresh copy of `source/` into a disposable
directory under `target/planar-certified/`, then apply the chosen variant patch
with that directory as the patch root; patch paths are `a/source/...` and
`b/source/...`. Verify the resulting files against `source-manifest.json` before
compiling. The unchanged focused source needs no variant patch.

Use the corresponding build manifest's `command` array. Replace its historical
checkout prefix with the current checkout, and its `*-source/lib.rs` argument
with the reconstructed `source/lib.rs`. Map the output path to the intended
`target/planar-certified/core-tests[-VARIANT]`. For the diagnostic-focused build,
also remap the reused focused source/output names as described above. Keep
`--cfg planar_focus`, optimization and metadata arguments from that manifest.

The six direct `--extern` archives must match `builds/frozen-dependencies.json`.
The commands also require `target/cargo-build/debug/deps` and the GMP/MPFR native
output directory. Their complete transitive/native hashes and exact compiler
version were not captured, so this compact bundle is **not a self-contained
binary-rebuild archive**. Rebuilding dependencies creates new provenance and
requires renewed qualification; it must not be represented as the old binary.

After explicitly authorizing execution and restoring matching binaries, use the
retained runner for individual commands.

The runner also reads `target/planar-certified/compile-VARIANT.json`; restore the
matching manifest from `builds/` at that path. For an unchanged recorded binary,
copy the recorded manifest byte-for-byte. For a rebuilt binary, write a new
manifest with the actual build command, source/dependency hashes and resulting
binary hash instead of attributing it to the old build. The diagnostic variant
needs these explicit aliases: `diagnostic-core-tests-focused` becomes
`core-tests-diagnostic-focused`, and `builds/diagnostic-compile-focused.json`
becomes `target/planar-certified/compile-diagnostic-focused.json`. Use
`IREGI_PLANAR_VARIANT=diagnostic-focused` for those aliases. The original variant
uses `core-tests` and `compile.json` with no variant environment variable.

For example, with the tetrahedron binary and its matching manifest restored:

```sh
IREGI_PLANAR_VARIANT=tetrahedron taskset -c 0 python3 validation/planar-certified/run.py \
  certified_planar_tetrahedron_rank_two_binary64_isolates_failed_rows 60
```

The runner writes new logs under `target/planar-certified/`, leaving this evidence
bundle unchanged. Phase reproduction requires the two profiling environment
variables above. Use the recorded full test names and bounds in
`qualification.json`; no run or build is performed by reading this bundle.

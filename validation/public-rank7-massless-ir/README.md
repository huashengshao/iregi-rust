# Restricted massless rank-seven saved evidence

This capsule preserves three fixed ordinary massless one-loop points at cumulative rank seven: a routed scaleless lightlike bubble, a triangle with two on-shell legs and invariant 4, and a box with invariants 4 and −2. Each array contains 330 Cartesian moments and four separate native Laurent coefficients, `[UV single, IR single, IR double, finite]`, in IREGI ordering. Inputs use `(q+p)^2−m²+i0`, metric `(+---)`, unit propagator powers, dimension shift zero, scale 3 and preserved inputs.

The three stable original quad-precision IBP arrays contain 3,960 complex slots. Six Rust arrays at working precision 128/256 bits and requested accuracy 53 bits contain 7,920 complex slots. All six used the actual `PassarinoVeltman` algorithm and analytic routes, with no fallback. The saved independent audit recomputes every one of the 7,920 reference comparisons, 3,960 precision pairs and four committed scalar-B0 anchor checks: **11,884 records, zero failures**. Reference agreement uses amplitude tolerance `1e-10`; precision pairs use `2^-80`. Acceptance arithmetic uses exact rational values and dimensionally normalized complex errors; Decimal is used only to reproduce the saved 100-digit error display.

The maximum reference error is approximately `2.522e-16`, and the maximum precision-pair error is approximately `5.891e-37`. Each pole slot is compared separately. The scaleless bubble retains 36 represented nonzero UV poles and 36 cancelling IR single poles per array. No UV/IR merge, zero projection or positive-F pole-zero identity is applied. Counts of represented nonzero slots do not establish a residue's significance.

## Replay

From the repository root, with Python available:

```sh
python3 validation/public-rank7-massless-ir/check.py
python3 validation/public-rank7-massless-ir/check.py --reconstruct /tmp/tirust-massless-rank7-restored
```

The destination must not exist. The replay uses only the standard library and the exact parent files declared in `manifest.json`; it needs neither `target/`, reference checkouts, a Symbolica license, Rust/Fortran compilers nor native executables. It first validates and restores the existing actual-Cargo N1–N5 parent and its quad-reference chain, then restores this capsule's original-path aliases. The public helper `restore_files(manifest)` returns those byte aliases; `replay(files)` verifies this capsule.

`check.py` executes no producer comparator or controller. It mechanically adapts the retained independent numeric audit (`237bb627…`) through an AST allowlist: exclude its original filesystem `read`/`load` functions and output-writing `__main__` block; provide in-memory reads; preserve the historical fixture pathname; hash the preserved audit bytes. Parsing, arithmetic, controls and its `main()` remain unchanged. The complete recomputed independent receipt must equal the preserved receipt. The metadata audit script is preserved as bytes and never executed, since its original review includes native-file hashes and process checks.

## What is preserved

The deterministic `payload.tar.gz` retains all 83 noncompiled files from the private corpus and both external metadata-review files: fixtures, original raw stdout/stderr, complete Rust results, nine capture receipts and step logs, all comparison records, controller and preparation sources, three unexecuted earlier drafts, source-review fixes and controls, the numeric review's initial failed precision-metadata assumption and corrected review, grants, releases, both qualification stages and the executor's schedule attestation. Byte-identical own files share archive members. `payload-origins.json` maps every alias to its original path and hash. `copy-receipt.json` records the restored inventory digest and replay result.

The parent `validation/public-rank7-current-cargo-n1-n5` supplies the exact 64-source Cargo archive and its artifact/build/test provenance; its quad-reference parents supply the reference sources and upstream GPL `COPYING`. Their declared files are borrowed directly, without copying the wide source closure. No compiled executable, object, cache or literal Symbolica license is included. Nine owned executable copies and the two original executables remain explicit historical digest attestations, as do the immutable external tool hashes.

## Scope and limits

The final qualification is an exact byte copy of `qualification-after-independent.json`, with its independent numerical and metadata reviews. It qualifies these saved results from frozen Cargo artifact `8166f6e7…` and its archived sources, rather than a rebuild of later live edits. All nine per-case bounds and terminal metadata passed. Original executable hashes and group absence were independently checked in the retained metadata review; portable replay does not repeat those checks, rehash old executable copies or probe processes.

The six phases `[1,1,1,2,2,2]`, session mapping and maximum concurrency two are **executor-attested**. Controllers did not save UTC start/finish timestamps, so portable absolute chronology and nonoverlap cannot be independently proved. No timestamps or mtime inference are substituted. Elapsed durations include guards and executable copies and are diagnostic only.

The native quad witness is 113-bit storage with 33 decimal digits, not a claim of achieved 33-digit accuracy. Rust working precision and propagated component precision differ; tiny cancellation residuals can carry lower component precision, which is recorded without replacing numerical agreement gates. This capsule does not qualify the full massless domain, Dual values, generalized powers, shifted dimensions, physical graphs, current live Cargo sources or performance. Failed original PV evidence in the inherited parent remains visible.

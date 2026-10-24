# Optional native f64 backend capability qualification

This private TIRust candidate adds an explicit `NativeF64Abc` execution policy and `native-f64-abc` feature. The default remains unchanged. The selected path uses the existing oneloopmaster-generated A0/B0/C0 Rust modules only for ordinary f64; D0, dB0, DoubleFloat, Float and Dual use Symbolica under the explicit policy.

Seventeen focused public API tests passed. A separate read-only observation overlay passed all 38 requests, including all eight retained bubble/triangle tensor families and all six master outputs, exact own repeats, IREGI agreement at the original 1e-10 normalized tolerance, precision/Dual fallback, invalid-lane controls and cache interleaving. Independent numerical and provenance audits are included.

The original broad `native-batch` metadata attempt reached its 60-second limit; the remaining seven compatibility checks were not run. That failure remains visible. A later separately authorized compatibility-only attempt, if performed, must have its own receipt and does not rewrite this snapshot. No production integration, default change or performance claim follows from this package.

`compiled-sources.tar.gz` preserves the exact public and observation Rust snapshots. `archive-map.json` maps every preserved original path and decompressed digest. The external hash-only list explicitly identifies omitted binaries, toolchain and dependency archives. Logs, original inputs, source and admission scripts, raw JSONL/stdout, producer and independent receipts, command plans and authorization records are preserved under `producer/`; large files use deterministic gzip. No license material is included.

Reproduction requires restoring mapped bytes at their original project-relative paths and obtaining the pinned toolchain/dependency closure. The original commands and bounded lifecycle are recorded in the build and runtime receipts. Merely rerunning a producer is not independent admission: the saved-data validators and independent reviews are separate evidence.

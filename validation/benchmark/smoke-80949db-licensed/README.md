# Optimized 80949db licensed kernel smoke

All eight massive bubble/triangle rank-zero/one configurations pass the unchanged
`1e-10` dimensionally normalized correctness criterion at batch widths 1 and 32.
Every requested tensor component and native Laurent coefficient is checked.
`qualification.json` records source, build, executable, harness and raw-file hashes.

This run is **not a performance qualification**: three blocks target only 0.1 ms,
with zero warm-ups and unrelated builds active. Raw timing and ratio objects are
retained in `results.json` for audit; they must not supply a parity or speedup claim.
The accepted user license was loaded outside tracked files; no key is retained.

The retained `rust-build.json` and `reference-build.json` identify exact build
snapshots. Reproduction requires those matching binaries and source hashes;
rebuilding later sources creates a new experiment. Use the root kernel harness
with the recorded manifest paths, inputs, batches, repeats, warm-up and block
target. Numerical validation precedes every measured configuration.

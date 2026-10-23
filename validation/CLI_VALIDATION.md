# CLI validation snapshot

The recorded executables pass six CLI unit tests and twelve integration
checks: exact input precision, dimension and supplied-invariant packing,
FeynKit graph import, batched binary64/DoubleFloat/arbitrary-precision reduction,
bubble and triangle contraction, supplied-invariant parity, mixed-rank input
rejection, and independent failure handling for invalid kinematics and singular
numerator coefficients. Commands, binary hashes and a source snapshot are in
[`cli-results.json`](cli-results.json). The six unit tests include JSON
decimal-token preservation and characteristic-scale normalization. They ran
against the integrated core. All twelve integration checks pass with the rebuilt
CLI, including the fixture comparison command. The earlier model-import
regression from `serde_json/arbitrary_precision` was resolved by an exact
preparation-boundary adapter for FeynKit quantum numbers; the failed attempt is
retained in the evidence history.

The complete original-IREGI oracle now has **31 passing cases out of 31**.
Thirty pass at binary64. `C0_power2_1_1_rank2` requires explicit precision rescue
at 128 bits followed by an independent 256-bit convergence check. This is not a
claim that every case passes at binary64. The earlier conservative cancellation
guard rejection and its executable identity remain in the evidence history.

The physical `g g -> h` top triangle passes the complete FeynKit DOT to Rust
reduction and contraction path. All 60 Laurent tensor slots agree with original
IREGI at the canonical FeynKit routing to a maximum normalized error of
`1.86e-15`. The contracted fixed-color finite coefficient is
`-147.86843349622455 + 9.85e-13 i`, compared with MadLoop's independently
mapped `-147.8684334962245 - 4.00e-13 i`, with mixed error `9.38e-15`;
single and double poles agree. R2 and UV counterterms are excluded; bare poles
and R1 remain. See [`physical/ggh-cli-comparison.json`](physical/ggh-cli-comparison.json)
for all values, normalization, hashes and the reproduction command.

These are correctness checks using binary64 reference data. Test durations and
the CLI's single-execution timers are not benchmark measurements.

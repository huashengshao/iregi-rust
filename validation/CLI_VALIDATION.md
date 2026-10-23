# CLI validation snapshot

The recorded executables pass eleven CLI unit tests and nineteen integration
checks: exact input precision, dimension and supplied-invariant packing,
FeynKit graph import, batched binary64/DoubleFloat/arbitrary-precision reduction,
bubble and triangle contraction, supplied-invariant parity, mixed-rank input
rejection, and independent failure handling for invalid kinematics and singular
numerator coefficients. Commands, binary hashes and a source snapshot are in
[`cli-results.json`](cli-results.json). The unit tests include JSON decimal-token
preservation, characteristic-scale normalization, rescue policy validation and
signed-zero preservation and exact legacy snapping configuration. All nineteen
integration checks pass, including explicit
verified rescue of the generalized triangle, independent working/accuracy
precision, and rescue lane isolation. Tensor verification also converges for a
lane whose singular numerator independently fails contraction, demonstrating
the reported tensor-only verification scope. Earlier integration results retain
their executable identities in the history. The earlier model-import
regression from `serde_json/arbitrary_precision` was resolved by an exact
preparation-boundary adapter for FeynKit quantum numbers; the failed attempt is
retained in the evidence history.

The legacy-policy CLI checks compare both the ordinary and translated complex
bubble fixtures with original IREGI, preserve a threshold beyond binary64
precision, verify the supplied-invariant bypass, and isolate a rejected
negative-reference zero-diagonal lane from a valid sample. Coordinate input
with five propagators returns an explicit unsupported error. Generalized powers
and dimension shifts forward the same core policy; separate numerical
qualification for those legacy-policy domains is still outstanding.

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

The full `g g -> h h h` pentagon also passes independent 128- and 256-bit
CLI reruns, each targeting 53-bit accuracy. All 280 tensor slots agree with
original PV/hybrid within `4.63e-14`, and the MadLoop graph contraction agrees
within `9.30e-14`. The known original-IBP rank-four mismatch remains visible,
so the reports deliberately retain a failed all-mode aggregate. The separate
physical and PV/hybrid checks pass, and the complete reruns agree within
`7.79e-17` in the tensor comparison. See the retained
[`128-bit report`](physical/gghhh-cli-hybrid-float128-comparison.json),
[`256-bit report`](physical/gghhh-cli-hybrid-float256-comparison.json), and
[`precision comparison`](physical/gghhh-cli-precision-convergence.json).

These are correctness checks using binary64 reference data. Test durations and
the CLI's single-execution timers are not benchmark measurements.

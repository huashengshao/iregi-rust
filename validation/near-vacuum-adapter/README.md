# Private accuracy-aware D0 adapter checkpoint

This experiment applies the qualified near-vacuum series to an isolated copy
of `iregi-masters`. The committed production master and reduction sources are
unchanged. `proposed-adapter.patch` is a review artifact, not an applied patch.
`private-sources.tar.gz` contains the complete frozen private master sources,
drivers, run tools and independent contour-oracle sources. `qualification.json`
binds the source archive, patch, measurements and dependency provenance.

The adapter accepts explicit per-component absolute/relative accuracy. It
returns an optional finite rectangle for each successful certified lane and
keeps absent certificates distinct from zero error. Physical input validation
precedes series dispatch. Certified lanes bypass only the unused DNS formula
and its discriminant; the ordinary API and its existing guards are preserved.
N2 and N4 workspaces evaluate each instruction over active sample lanes.

Four final typed runs pass the seven-lane, six-component mixed batch:

| Type | Working bits | Requested bits | Certified component comparisons |
|---|---:|---:|---:|
| f64 | 53 | 40 | 24 |
| DoubleFloat | 106 | 80 | 24 |
| Float | 128 | 100 | 24 |
| Float | 256 | 128 | 24 |

These 96 comparisons match the previously independently qualified candidate's
numerical values and entire error rectangles exactly. Two initial runs retain
48 additional repeated comparisons. The drivers also check empty and reversed
batches, scale-only jets, zero poles, impossible accuracy requests, physical
domain failures and interleaved rejected rows. Rejected rows hide values.

The seeded overlap row retains its existing ordinary derivative-domain
rejection. A separate safe primal row outside the series radius succeeds
through explicitly permitted ordinary fallback, matches the legacy API
exactly, and remains labeled `OrdinaryUncertified` without a finite certificate.
Requiring a certificate rejects that same row. Ordinary success therefore does
not imply certified accuracy.

The independent exact contour probe uses x=1/2, t=1-i, common shifted squared
mass M=2-i and the original nonzero routing scale eta=2^-64. It evaluates all
five pinched boxes in one N2 batch at Float256/request128. Symbolica derives
the routing, Cayley inverse and coefficients, integrates independent exact
parameter series, and evaluates the contraction with ComplexBall. Each D0
rectangle and the complete contraction rectangle satisfy the unchanged
requested budget against their independent oracle. A separate audit recomputed
232 numerical/provenance checks across 36 uniquely hashed files. See
`oracle/README.md`, `oracle/COMPARE.md` and the retained JSON for the exact
normalization and bounds.

The contour probe does not execute production geometry or floating-point
mass-shift construction. It does not include Gauss-node/weight uncertainty,
quadrature truncation, full public E6 reduction or core error propagation.
This milestone establishes the selected finite box path and exact-coefficient
contraction. It does not qualify production E6 or performance parity. All
reported durations are diagnostic; correctness runs used CPUs4 and5 and may
have overlapped.

Two adapter implementation issues must be addressed before promotion:

- Series preparation currently runs for every valid opt-in D0 row, and N4
  retries every rejected row. Add eligibility and refinement filtering.
- Unsupported series shapes abort preparation even if ordinary fallback was
  explicitly allowed. Preserve the ordinary path for those requests.

The scalar backend archives are retained, pinned artifacts; Symbolica predates
the later default allocator-stack change. The oneloop archive enables its
Rust-codegen API, while the private adapter itself has no native-batch feature.
`build-provenance.json` and individual run manifests record exact hashes.
The initial missing-feature and prototype-constructor compilation failures
remain in the build logs; they produced no numerical results.

To inspect or reproduce, extract the source archive into a fresh directory
under `target`, use the recorded library build command with the retained
archives, then compile `adapter_validate_v2.rs` with the recorded externs and
`CARGO_CRATE_NAME=near_vacuum_adapter_validate_v2`. Run it as
`adapter_validate_v2 <f64|dd|float128|float256> <output.json>`. The independent
oracle and comparison have complete commands in their build/run manifests.
Use the repository environment and the local license separately; license
contents are never part of this package. `archive.py` rechecks the original
retained runs and rebuilds this compact evidence package without rerunning
numerical evaluation.

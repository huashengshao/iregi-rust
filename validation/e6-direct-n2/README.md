# Private direct E6 N2 checkpoint

This is a validation-only specialization of the qualified near-vacuum D0
engine. It evaluates the genuine unit-power D6 pentagon directly as
`-integral_Delta4 F^-2`, with Symbolica series and exact parameter integration.
No production implementation, public API or default E6 dispatch changed.
The previous public contour failures remain separate evidence.

The private Float256/request128 run passed nine physical lanes with four
native one-axis Taylor components each. Four lanes expose successful values
(sixteen components). Five lanes reject as intended, including a cubic
common-mass component whose N2 truncation is insufficient despite a zero
primal deviation. All rejected lanes hide values. This does not qualify
mixed-axis derivatives, arbitrary precisions, other numeric types, unequal
complex masses or a general E6 domain.

The independent audit in `audit/result.json` passed 513 checks and 140 hash
verifications with no failures. It independently recomputed the sixteen
accepted component budgets, full oracle containment, negative controls and
source/build/run/binary/dependency provenance. Its checker uses exact scalar
rational arithmetic on emitted evidence; it does not run Symbolica or share
the candidate's polynomial integration.

The accepted lanes are the retained tiny-routing exact-series fixture,
the same fixture with different physical `mu_squared` and a scale jet,
the equal-mass vacuum, and the vacuum with a small common-mass jet. Rejections
cover the radius limit, upper-half-plane mass, invalid physical scale,
insufficient cubic-component accuracy, and a nonreal invariant. Empty input,
malformed row length, oversized shape and reversed samples in an independent
workspace are also checked. The physical sixteen-argument row ends in
`mu_squared`; the separate prepared sixteen-argument polynomial ends in the
fixed expansion mass. The driver explicitly validates and maps them.

The retained exact E6 oracle is copied unchanged from
`validation/shifted-pentagon/series-oracle.json`. Its SHA-256 is
`0cf780289cf24e409aebc27d4cc51ccca3e4c02d386b4198cf16f0656cc974c3`.
An independent common-mass identity is expanded with Symbolica in the driver.
For each successful component, both the numeric result and every point in
the candidate rectangle meet the explicit budget relative to the oracle
interval. The candidate contains the complete oracle interval; intersection
alone is not the acceptance test.

The candidate is derived by the 29 explicit substitutions in
`source/family-transform.json`, with a complete diff alongside. The original
D0 source is retained byte-for-byte. A source/math review approved the
family conversion before computation; its final record binds the hardened
driver and candidate hashes in `review-before-compute.json`. Production D0
acceptance, shape checks, full-jet remainder and failure hiding were reused.
The changes are five simplex/four cube coordinates, ten lexicographic
invariants/five masses, the negative sign, volume denominator 24, and
envelope factor 2/5. No integration or polynomial engine was introduced.

The exact preparation used 27810 cube-polynomial terms, 136 integrated terms
and 2987 exported numeric/Dual instructions, within unchanged resource caps.
The primary evaluation packed eight scale-valid rows, with five active series
rows and one batch each for numeric values, ball enclosures and positive tails.

`build.json` and `run.json` record bounded diagnostic observations, not
benchmarks: the native-object direct build took about 5.48 seconds and the
whole validation process about 0.817 seconds; exact preparation accounted
for about 0.668 seconds. There was no timing isolation, optimized kernel
comparison, uncertainty estimate or performance qualification.

The 116 frozen dependency/native-library files remain under
`target/e6-direct-n2/deps` and `native`. Their hashes and completed Cargo
provenance are in `preparation.json` and `upstream-preparation.json`; they
bind the completed `06706e2a1e4f0082889a53187c80bbe97803340f` master build.
The tested binary is `target/e6-direct-n2/validate`, SHA-256
`dcf03d03f843b207b6e45b98353f5fa5438fa1ec53c1518bbf4582c01fe8f801`.
Build and run supervisors check frozen source and dependency hashes before
and after execution. The compiler reused native-object archives with
`opt-level=0`, no ThinLTO and no dependency rebuild.

From the project directory, the recorded private supervisors are:

```sh
source scripts/env.sh
python3 target/e6-direct-n2/build.py
source .local/symbolica-license.env
python3 target/e6-direct-n2/run.py
```

They deliberately refuse to overwrite an existing attempt. Reproduction
requires a new attempt directory and frozen dependency closure satisfying
the recorded hashes; do not delete the retained result to rerun it. The
license file is untracked and is not included in the evidence. The precise
compiler/runtime arguments are recorded as JSON arrays in the build/run
records.

The two prior design notes remain unchanged. Their hashes are
`03a859ecc4da5ece34cf83a1a1ea68821a149494243be8826222fd0754744bd0`
for `docs/research/e6-certified-path.md`, and
`cdf9961a28790f1e01cb91494d4f701d670070c15017aafed61505ece291aa9c`
for `docs/research/e6-near-vacuum-direct.md`.

# Private v3 adapter contract qualification

V3 fixes two reviewed dispatch issues in the private adapter. It leaves the
frozen v2 package and production sources unchanged.

A valid native Dual shape outside the bounded series domain now skips series
preparation. Under `RequireFiniteCertificate`, it exposes no values and
reports why the series facility is unavailable. Under the explicit
`AllowOrdinaryUncertified` policy, the same request uses the ordinary path and
retains no finite certificate. Physical input errors still take priority.
Only N2 results with `UncertifiedComponent` are retried at N4; outside-domain,
invalid and nonfinite series results do not trigger an unused N4 plan.

The dispatch contract test uses the native univariate Taylor shape of degrees
zero through five. Exact-vacuum kinematics with constant or scale-only jets
exercise both policies. Ordinary fallback matches all five Laurent groups
bit-for-bit, while all nonprimal finite and pole components vanish. Invalid
mass and scale rows remain hidden under either policy. Empty and reversed
batches preserve the contract. A three-row outside-domain batch prepares only
N2, executes zero active series rows and never prepares N4. Independent audit
checked 199 semantic/provenance assertions and 28 unique file hashes.

The accepted-output regression repeats the four numeric settings from v2:
f64/request40, DoubleFloat/request80, Float128/request100 and
Float256/request128. All 96 accepted mixed components and their candidate
rectangles still pass; serialized values and lane statuses match frozen v2
exactly. The independent five-pinch contour comparison is separately rebuilt
against the v3 library. It retains the exact oracle and unchanged requested128
budget from the previous package.

The explicit Rational absolute/relative budgets define the accuracy
guarantee. The binary constructor used here sets both to 2^-requested_bits.
For a custom context the requested-bit field is diagnostic and does not
override its supplied budgets. A finite rectangle encloses the function of
the exact represented master inputs; upstream routing or mass-shift errors
are outside this contract.

The ordinary fallback policy handles lane/domain and shape unavailability.
Shared symbolic-preparation and evaluator errors remain whole-call errors.
Supported opt-in D0 requests still prepare N2 before checking numerical
eligibility. The original ordinary API incurs no new work. N2/N4 and the
shape, degree and resource caps remain explicit limits.

`qualification.json` binds the package. `private-sources.tar.gz` contains all
frozen sources. `v2-to-v3.patch` shows only the reviewed contract changes;
`proposed-adapter-v3.patch` is the full unapplied production proposal.
`library-build.json` records the actual private library build command, its
successful exit, and source/archive hashes. The contract and contour build
records bind the linked library independently. Large executables stay in
`target`; their hashes remain in the committed evidence.

No production geometry, shifted-input rounding, Gauss-node/weight intervals,
quadrature truncation, public E6 result or performance gate is qualified.
The retained dependency archives precede the default allocator-stack change.
Correctness processes used CPUs18 and19 and could overlap; all durations are
diagnostic. The production promotion proposal is
`docs/research/near-vacuum-adapter-production.md` and requires a current locked
workspace build and public-API checks before promotion.

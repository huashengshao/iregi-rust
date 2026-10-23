# Independent review of the staged certified-master patch

This review covers the unapplied staging tree at
`target/near-vacuum-production-ready/crates/iregi-masters`. Live production
sources were not changed by this review. The reviewer performed source
inspection, exact text replay and file-hash checks. The reviewer did not
compile the staged library or tests, run Symbolica, or execute numerical tests.
Any subsequent typecheck, build or runtime evidence must be recorded separately.

## Cleanup equivalence

The reference is the exact private v3 source qualified against the retained
current dependency closure in
`validation/near-vacuum-adapter-current/qualification.json`. Its source hashes
are recorded in `thin-lto/build.json` beneath that directory.

Independent replay of every `old`/`new` entry in `cleanup-proof.json` reproduced
both staged changed files byte for byte. Each replaced fragment occurred
exactly once at its replay step. Reconstructing the unified diff reproduced
`cleanup.patch` exactly. The other 15 Rust source files matched their qualified
counterparts and recorded hashes. The qualification, qualified-build, cleanup
patch, preparation script and live production library hashes also matched the
proof record.

The permitted changes are:

- Remove seven complete `eprintln!` statement sites and the single
  `preparation_started = Instant::now()` binding. One statement site was inside
  the three-coordinate integration loop. The polynomial term-limit guard
  remains present.
- Update the two module introductions and document that `requested_bits` is
  diagnostic metadata; explicit rational budgets determine acceptance.
- Replace four diagnostic strings containing validation-stage wording with
  near-vacuum wording. These are observable message changes and are explicitly
  enumerated in the proof.

No arithmetic expression, Symbolica integration or Dualizer operation, branch
predicate, acceptance threshold, resource limit, recurrence order, lane
selection or fallback decision changed. The executable content of
`certified.rs` is unchanged. No general string stripping, token normalization
or formatter was used in the equivalence proof.

The staged `lib.rs` is identical to the qualified v3 library. Its differences
from the live ordinary library consist of two module declarations and the
`InvalidAccuracy` and `UncertifiedFinite` variants with their display arms.
Removing those exact additions reproduces the live library bytes. The native
batch module is also unchanged. This is a source-preservation result; it does
not substitute for compiling and exercising the public API.

## Focused public tests

The staged integration test file uses the public `iregi_masters::certified`
API, ordinary public master types and Symbolica numeric types. It contains
three tests:

1. An odd, five-row f64 batch covers an exact vacuum, a tiny invariant, invalid
   scale, an upper-half-plane mass and a safe ordinary point outside the series
   radius. It checks lane isolation, hidden failed values, exact vacuum
   `1/6` enclosure, zero Laurent poles, batch counters, empty and reversed
   batches, input preservation, explicit ordinary fallback, and absence of
   unnecessary N4 preparation before tighter requests. Further calls check
   tighter and impossible budgets, custom budgets independent of the diagnostic
   bit field, invalid contexts, buffer/size errors and separately owned
   workspace state.
2. A Float256/request128 batch contains a common-mass jet through degree three
   and a scale-only jet. The exact identity
   `D0(s,s,s,s; p=0) = 1/(6 s^2)` gives normalized Taylor coefficients
   `[1/6, -1/3, 1/2, -2/3]` at `s=1+t`. The test requires N2 to reject the third
   common-mass coefficient despite zero primal radius, N4 to certify all four
   coefficients, and the scale-only lane to finish at N2 with zero higher
   coefficients. It checks the exact targets against complete rectangles,
   per-component error budgets, zero poles and selective N4 batching.
3. A native-valid degree-five scale-only shape exercises the bounded-series
   rejection path. Required certificates hide results without preparing either
   series order. Explicit ordinary fallback matches every legacy Laurent
   component bit for bit, carries no finite certificate, and preserves the
   physical rejection of an invalid mass lane.

The rectangle helper recomputes the maximum squared distance from the returned
number to the entire rectangle using Symbolica rationals. It checks the
reported bound and the explicit mixed budget, rather than only checking that
an oracle value lies inside an interval. The fixed vacuum identities are
independent numerical targets; the tests introduce no polynomial or jet engine.
Assertions use typed errors and statuses rather than the four changed messages.

Source inspection found no concrete mathematical or API-usage defect in these
tests. This statement makes no claim that they have compiled or passed.

## Public contract and remaining limits

The existing public `MasterError` and `LaneError` enums are exhaustive. Adding
variants can require changes to downstream exhaustive matches, even though
ordinary numerical evaluation is unchanged. The promotion must describe this
source-compatibility effect.

Certificates apply to the function of exactly represented master inputs.
They do not enclose routing or mass-shift errors made before the call, production
Gauss nodes or weights, quadrature truncation, or public E6 results. Ordinary
fallback is explicitly uncertified. Shared symbolic-preparation or evaluator
errors still return whole-call errors. Preparation resource checks occur after
some intermediate expressions have been constructed; they are not hard peak
memory bounds. No performance claim follows from this review or these tests.

## Reviewed hashes

| Artifact | SHA256 |
| --- | --- |
| Current private qualification | `e444a5cdd5c0d6dedf4046da53e7aaa0c4f99c4d6487c9001cbfa6d6b0afd7be` |
| Qualified current build record | `0dbf82fc43ed5fc97fa6de9829d29daaa5fb770908d55d7546a78ae8ac923102` |
| `cleanup-proof.json` | `73b344359e41557bc5dcf21382b4757b3a76fa6f23163eac491cfda3433f33f1` |
| `cleanup.patch` | `4f2c63fa4a509e9cbafcc79f3cf35cdfad4b9786b055f3fdc0a20ab57850c0e7` |
| `prepare.py` | `a8af5fa5fdfa3f012f6937b53d57d27679029e123e7879ce60c76bc78ceb4389` |
| Staged `src/near_vacuum.rs` | `046bb0e22fe5ec63489f94352a61eecb20020647bd8d893dc585e99e46663a57` |
| Staged `src/certified.rs` | `a33fb74c5b4122cab8e716f6105f4a91bccb397110ffe621344e9166b1a9b941` |
| Staged `tests/certified.rs` | `27f6995d2f7d950fce269519dd8b07cb1593eec83fe37b9d961e19b3039b70d9` |
| Live ordinary `src/lib.rs` | `47b74a182fb2953b4676a95fe108a1065b142f46b4f758418b44578922466883` |

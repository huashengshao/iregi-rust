# Standalone certified planar API qualification

This private candidate rebases the certified planar interface onto the production
generalized-PV, allocator and conditioning-context implementation at `6b24c03`.
It exports `CertifiedPlanarReductionPlan` and `CertifiedPlanarWorkspace`, with
full-Taylor rank certificates, regular constant-one chart selection, genuine
instruction-major grouped reductions and unchanged numerical guards.

The ten focused runs and their exact scope are recorded in `qualification.json`.
The rank-seven runs retain every one of the330×4 complex coefficients and the
corresponding five-box identity in exact rational form, including each real and
imaginary component's working precision. The256-bit run binds its128-bit input
artifact by SHA256 and checks dimensionally normalized convergence.

The wrapper now validates each row before certification using the same helper
and exact check order as the ordinary executor. Analytic attempts and actual
child work are counted separately; profiling closes after errors and includes
completed child work. Failed lanes cannot be read as successful zero arrays.

The four-line Symbolica `Atom::add_many` amplitude accumulation change is retained
from the previous independently qualified private candidate. The full patch also
contains opt-in phase diagnostics and tests; it is a review patch, not an automatic
production adoption instruction. Automatic ordinary `Workspace` fallback remains
off. Rank-seven Dual coverage is outside this bundle.

Historical failures and180-second timeouts remain in `validation/planar-certified`.
This is correctness and provenance evidence, not a matched performance experiment.
Rational serialization preserves numerical values but not signed-zero bit patterns.

`source/` includes the complete frozen core and its three include fixtures.
Build and run scripts retain their historical `target/planar-integrated` paths.
Binaries and dependency archives remain hash-bound under `target`; exact commands,
direct archive hashes, all retained source hashes and raw output are committed here.
`files.json` binds all retained files. No production Rust source was changed.

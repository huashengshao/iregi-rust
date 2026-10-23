# Private selected-native whole-reduction qualification

This opt0 correctness experiment selects the unchanged native A0/B0/C0 kernels
only for ordinary `f64` masters, after the original exact plan is instantiated.
The public master adapter retains its validation, normalization, six outputs,
UV/IR handling and diagnostics. D0/dB0, DoubleFloat, Float and Dual shapes retain
their original Symbolica evaluator. Production source and the global default
backend are unchanged. There is no performance or adoption result here.

The one bounded qualification completed in12.32 seconds. All eight frozen N2/N3
rank0/1 singleton/batch32 families pass complete tensor/Laurent comparison with
both the private Symbolica baseline and original IREGI at normalized1e-10.
Each backend returns1,584 complex Laurent coefficients; the actual297 master
rows retain1,782 complex coefficients, including the sixth private discriminant.
The largest normalized whole-result difference is2.06015e-13 between backends
and3.37757e-13 against IREGI. The largest master difference is1.69483e-14.
Statuses, diagnostics, fallback/analytic flags, family ordering, request ordering
and counters agree. All eight complete repeated responses are retained and each
backend reproduces its own represented value, precision and zero sign exactly.

Public-adapter controls cover34 selected-family cases:57 successful and21 failed
lanes, with342 successful complex coefficients. Ten unchanged master paths span
33 cases,49 successful and6 failed lanes, retaining432 complex coefficients.
They include mixed precision and inputs beyond53 bits, Float53 remaining distinct
from `f64`, primal-only/seeded/constant Dual shapes, D0/dB0, empty/odd/reused
buffers, invalid neighbors, scaleless pole cancellation and physical complex
branches. Three unchanged whole-core controls retain80 coefficients. Failed
lanes remain explicit errors with null output evidence. The direct-control
repeat and unchanged-pair checks are assertions in the frozen Rust probe;
only their first/common output snapshots are saved. Their second snapshots
are not independently reconstructible from this raw artifact.

The selected-master library compiled in16.75 seconds; baseline/candidate cores
in4.02/3.93 seconds. The first probe compilation stopped in0.37 seconds because
a fixture used an unavailable Rational string parser. Its original fixture
source and diagnostic are retained. Replacing that constructor with existing
`Rational::from((i64,i64))` preserved the exact input; the corrected probe linked
in26.64 seconds, reusing the three successful libraries with explicit guards.
No numerical dependency, D0 native module or full workspace was rebuilt. The
debug native-object dependency closure and optimized dependency profiles are
recorded; these heterogeneous build profiles cannot support timing claims.

The private source change is in `private.patch`, `source/selected_batch.rs` and
`source/master_capture.rs`. `source-manifest.json` binds unchanged production
source from06706e2 and the private copies; two core builds differ only in the
immutable private selection cfg. Exact cache keys include that policy bit.
Capture is disabled by default and enabled sequentially for qualification.
It is inside the profiling interval, so captured durations must never be used
as reduction/master performance measurements.

The durable `qualification/results.json.gz` contains the complete raw JSON,
deterministically compressed without removing fields. Its uncompressed digest
is retained in `qualification.json`; the private expanded original remains
under `target/selected-native-reduction/qualification-001/results.json`.
`admission-controls.json` records24 rejected malformed-output controls, using
the exact frozen runner parser. Independent review is recorded separately.

Reproduction from the retained workspace (all commands from the repository):

```sh
source scripts/env.sh
python target/selected-native-reduction/build.py NEW_ATTEMPT
source .local/symbolica-license.env
python target/selected-native-reduction/run.py NEW_ATTEMPT NEW_RUN
```

The build uses existing immutable archives identified by their completed Cargo
events and hashes. It fails if these are absent or changed; it does not rebuild
them implicitly. Runtime is bounded to120 seconds. A future optimized build and
whole-call timing require a separately recorded protocol and scheduling grant.

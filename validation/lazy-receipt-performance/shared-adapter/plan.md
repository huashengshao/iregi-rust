# Matched optimized whole-reduction experiment — source-only proposal

No build or timing is authorized by this document. The private opt0 semantics
qualification remains separately frozen in `validation/selected-native-reduction/`.

## Shared current adapter and unchanged optimized dependencies

Use the runtime opt3 archives in
`target/benchmark/dependency-closures/6b24c03-complete-kinds`, admitted by
`closure-audit.json`. Its completed build is release opt3, ThinLTO,
codegen-units1, with no RUSTFLAGS override and debug assertions/overflow checks
off. The298 recorded Symbolica/Numerica/Graphica and OneLoop source files match
both the completed before/after inventory and current files byte-for-byte.
Git also has no intervening dependency-source change. Cargo.toml/lock and the
rustc1.99.0 b940084d7 x86_64 toolchain match. Runtime metadata explicitly resolves
Symbolica to Numerica f2720232 and OneLoop to Symbolica2ae1abcc; complete observed
transitive archives and the same-toolchain sysroot are hash-checked. Host opt0
variants, the debug closure and the independent binary-fold candidate are excluded.

The selected runtime roots are:

| Crate | Archive stem | Original optimization/features |
| --- | --- | --- |
| Symbolica | symbolica-2ae1abcc9fd9c0db | opt3/cgu1; bincode,float-mpfr,integer-gmp,native_code_generation,serde,tracing_max_level_info |
| Numerica | numerica-f2720232b78e95ca | opt3/cgu1; bincode,float-mpfr,integer-gmp,serde |
| Graphica | graphica-0f8ec0b96b63d035 | opt3/cgu1; no features |
| OneLoop | oneloop-6117c7de19c8681b | opt3/cgu1; default,generated-evaluators,prebuilt,rust-codegen |
| serde | serde-bde6fd4136f3a6c8 | opt3/cgu1; alloc,default,derive,serde_derive,std |
| serde_json | serde_json-d5ce7f4fcf58bd84 | opt3/cgu1; alloc,arbitrary_precision,default,float_roundtrip,std |
| thiserror | thiserror-7d7ef35ea784c43a | opt3/cgu1; default,std |
| gmp-mpfr-sys | gmp_mpfr_sys-abd713454cac2ce0 | opt3/cgu1; default,mpc,mpfr |

The frozen native GMP/MPFR/MPC archive bytes are reused from the recorded release
closure. Their historical build-script flags are not inferred anew; the audit
records exact native hashes and search directory. No native library rebuild is
planned. Symbolica/Numerica/OneLoop archive objects are LLVM bitcode (`4243c0de`),
so the final probes require compatible ThinLTO rather than a debug/native-object
shortcut. This is the concrete reason for permitting a bounded final link.

Do **not** reuse the old6b24 master archive: current067 adds certified and
near-vacuum code. Compile exactly one current shared private master adapter from
`target/selected-native-reduction/copied/crates/iregi-masters`, whose production
and narrow private-delta hashes are already correctness-qualified. It retains
the existing public adapter, adds the reviewed concrete selected variant and
six-output observation accessor, and defaults to Symbolica. Both native-core
variants and both lazy/eager receipt cores consume this identical archive.
Only the native candidate calls the consuming selector; all baseline/eager/lazy
policies remain false. No global native-batch feature or native D0 module.

## New build recipe and ownership

`native_stack_batch` owns the shared adapter build after ROOT authorization.
The frozen source-only recipe is `build_shared.py`; no invocation has occurred.
Output is under `target/selected-native-optimized/shared/build-ATTEMPT/`, with
the successful archive and build digests published in `shared/accepted.json`.
Consumers must resolve that receipt rather than guess an archive filename.
`numeric_batch_audit` consumes that one archive and owns its separate lazy/eager
core/probe build. No numerical dependency is rebuilt or compiled twice.

All new private Rust libraries use identical declared release semantics:

```text
--edition=2024 --crate-type=rlib
-C opt-level=3 -C codegen-units=16 -C embed-bitcode=yes
-C debuginfo=0 -C debug-assertions=no -C overflow-checks=no
```

Use the exact retained dependency/native search paths and explicit runtime
`--extern` archives. Freeze compiler path/hash/version, sources, feature/cfg set,
nonsecret environment, commands and complete archive hashes before compilation;
recheck after each command. Retain normal unwind behavior and default target CPU;
no fast-math or target-native override. `CARGO_CRATE_NAME=iregi_rust` remains the
same for both core copies so Symbolica symbol namespaces do not change.

Compile the entire public master adapter once, and two entire native-experiment
core libraries from the already qualified current067 source copies. Only their
crate disambiguators and candidate `--cfg private_selected_native` differ.
The exact-plan cache retains its immutable private policy key. Do not substitute
a raw-master microbenchmark or omit adapter validation, result construction,
recurrence, stability inspection or fallback handling.

One binary64-only whole-call probe links both cores with:

```text
-C opt-level=3 -C codegen-units=16 -C embed-bitcode=yes -C lto=thin
-C debuginfo=0 -C debug-assertions=no -C overflow-checks=no
```

These new cgu16 flags are deliberately distinguished from the retained
dependencies' original cgu1 profile. Both experiment sides have the same flags.
Proposed caps:180 seconds for the shared adapter,180 seconds per core library,
and600 seconds **per** ThinLTO probe. Use CPUs20/21 for this owner; the other
owner uses its assigned cores after coordination. On a timeout/failure, preserve
the terminal record and stop that candidate; never silently downgrade flags,
extend the bound or rebuild a dependency. Every process group is owned/tracked.

## Optimized numerical admission

Before timing, rerun all eight frozen massive N2/N3 rank0/1 families at outer
batch1/32, with input SHA65d0d2fd554807478569ac88b6d689c9132ce541e98cfb2a3a55b8ef98e5c7ef.
The exact original IREGI binary and full reference-build/source manifest are
bound: `target/benchmark/iregi-benchmark` SHA256
`4c2241f6dd557db4e9348f0fd397484a72d71f83b953a6efc8010c61d1bdd389`,
with `target/benchmark/reference-build.json` SHA256
`488782471657193e0e09f69c283cb82d8534577bb4fccd23f3087192c0f2f782`.
It uses the existing GNU Fortran15.2 `-O3` build (no fast-math). Compare
every tensor/Laurent coefficient against both baseline and original IREGI at
the unchanged dimensional1e-10 gate. Save exact own-backend repeats, all six
master outputs, request ordering, statuses, diagnostics, counts, fallback and
analytic flags. Run this gate again after the eventual timing window. A failed
or missing case blocks performance qualification and remains visible.

The already qualified precision/Dual controls remain explicit prior semantics
evidence; the optimized performance probe is binary64 only and makes no new
higher-precision performance claim. The lazy/eager owner separately repeats its
14 complete paired correctness cases against this same adapter before timing.

## Proposed one-window timing protocol

Freeze this protocol before any measurement and require ROOT's quiet grant.
Use the same coordinator-selected idle core for all three engines. The public
reduction call is the timed unit; input serialization, plan preparation and
subprocess transport remain outside. Both Rust variants use warmed immutable
plans and independent retained workspaces, with numerical recurrence values
reevaluated each call. Original IREGI retains its existing per-sample numerical
cache disposal inside the timed kernel. Capture and profiling are disabled for
warmup, calibration and acceptance blocks; instrumented component profiles, if
requested, are a separate diagnostic cohort.

Proposed balanced triplets:42 blocks per family, with each of the six
baseline/candidate/IREGI orders used seven times and frozen shuffle seed173.
After10 warm calls per engine, use separate2ms pilots and one shared integer
iteration count targeting100ms average per engine block. Each fixed-count block
has one elapsed-time read pair; Rust inputs/results remain black-boxed and every
call's successful status is checked, as in the current public benchmark. Retain
every raw duration, iteration count, order and pre/post result. Existing IREGI
BENCH iteration counts and kernel clocks are used unchanged.

Compute candidate/baseline and each Rust/IREGI ratio from the same triplet rows.
Use the existing frozen paired median/bootstrap helper,10,000 resamples and99%
intervals, with the existing2% relative interval-width gate. Report every one
of the eight families separately, both order effects and all noise/failure/
regression outcomes. No CI-dependent repeat or omission. Expected acceptance
block time is about101 seconds plus pilots/checks; propose a300-second process
bound. Host load remains separately recorded even when project jobs are held.

This is an isolated selected-master policy experiment on the current067 core.
The lazy/eager receipt experiment uses its own final-e23 private core variants;
shared dependencies do not make their performance ratios composable. Any later
combined production change needs its own complete qualification. Current state:
source/ABI plan only; compilation, numerical gates and timing remain unrun.

# Fresh matched optimized scheduler build

This private stage builds fourteen products only. It does not run a probe,
numerical integral, test or timing experiment, and does not change production
source. The execution owner is `/root/scheduler_perf_resume`; the root agent
authorized a bounded compiler stage after independent source review.

Run from `/shared/external/iregi/iregi-rust`, after `source scripts/env.sh`, using
the independently reviewed hash of `fresh-build-protocol.json`:

```sh
python3 target/guard-performance-review/optimized-performance-proposal/build_fresh.py <reviewed-protocol-sha256>
```

No Cargo process is launched. The sequential compiler uses CPUs 32 and 33, which
the root coordinator has separated from native-policy CPUs 6 and 7 and typed-Dual
CPUs 14 and 15. The fixed lifecycle bound is 3,600 seconds with 30 seconds reserved
from compiler work. Individual compiler caps are 600 seconds for Symbolica, 300
for OneLoop, 180 for masters, 240 for each core, and 480 for each linked probe.
Their sum exceeds the aggregate bound; the aggregate hard bound wins and later
steps may remain unrun. The unchanged owned-process-group helper stops on the
first failure, timeout, cancellation or cleanup problem. A terminal receipt is
written before reading post-execution artifacts. No automatic retry or extension
is allowed.

Each variant builds Symbolica, OneLoop, an accessor-enabled masters archive,
captured core/probe, and uncaptured core/probe. All fresh products use opt3,
16 codegen units, embedded bitcode and disabled debug/overflow checks; final probes
use ThinLTO. Exactly the scheduler source differs between baseline and candidate.
The existing frozen source snapshots include current polynomial patch 0004.
The accessor in the shared masters archive only returns a read-only slice; timing
cores omit the capture cfg and timing probes contain no capture calls. Both probes
must link exactly their own Symbolica, OneLoop, masters and core archives, verified
from full linker maps.

The lower dependency context is the hash-pinned historical optimized
`6b24c03-complete-kinds` closure. Numerica/Graphica source remains identical and is
guarded in v2. Its serde/bincode/serde_json features are broader than the current
Cargo graph. This is a matched frozen lower dependency context, **not an exact
current Cargo feature build**. Old optimized Symbolica, OneLoop, masters and core
archives are not reused. Their presence in the historical search directory must
not substitute for any fresh archive; linker-map admission enforces identity.

The complete first proposal, before adding current Numerica/Graphica and old lock
guards, is preserved in `draft-001`. No compiler ran for that proposal. v2 adds
57 provenance guards; all fourteen commands and generated probe source remain
unchanged.

After successful compilation, the next separately bounded stage must repeat the
retained 60-request captured corpus, including all eight N2/N3 rank 0/1 width 1/32
families, own repeats, retained workspace calls, precision/Dual/master controls,
cache interleaving and forbidden timing/backend fields. Independently review all
saved exact records. Then qualify both uncaptured probes outside timing, including
all controls, and compare every non-capture numerical/status/diagnostic field with
the matching captured probe. The newly linked uncaptured binary must not be timed
before those gates pass.

Only a later preregistered same-cohort experiment may measure the two TIRust
scheduler variants alongside hash-pinned IREGI and COLLIER. Preserve all eight
families and old measurements; TIRust is always the numerator for comparison
ratios. The historical short family is N2 rank 0 width 1, not the last row. No
performance or default-adoption claim follows from a successful compiler stage.

## ThinLTO correction and pinned source cohort

The original fourteen-product attempt stopped after five successful compiler
invocations: its first linked probe passed compilation, then the literal
four-original-archive-path map assertion failed. The failed receipt remains
unchanged in `fresh-build-001/build.json`. ThinLTO incorporates upstream Rust
objects before the native linker and can omit the original pure Rust archive
paths from its map; see `provenance-v3-research/README.md` and the local compiler
source bindings. A native linker map is retained for its actual transformed-link
scope, and is no longer represented as a list of pre-LTO Rust archives.

The reviewed continuation is `v3/protocol.json`. It reuses all five successful
compiler products and compiles only the nine previously unrun products under a
new fixed 2,400-second lifecycle bound with 30 seconds reserved, still on CPUs 32
and 33. Actual metadata observations bind the four fresh project roots and all 127
lower crate identities. These comprise 108 original guarded lower archives and 19
new full sysroot metadata companions. The first failed metadata read of a sysroot
linker stub and its relocated ICE report remain visible. No compiler or numerical
failure is hidden by those new supplemental observations.

The nine new compilers use 108 exact closed lower aliases rather than the broad
historical dependency search directory. That historical directory was not fully
inventoried before the original five compilers, and no retrospective closed-search
claim is made. The successful original compiler argv, guarded explicit externs,
fresh metadata dependency identities and Rust's hash matching establish the
original input selection; they are preserved with the original failed map gate.

Live production origins have been separated from active compiler inputs. Their 257
hashes are pinned to committed revision `2c1f334` in
`v3/pinned-origin-context.json`. All actual private source, manifest, asset, tool
and archive inputs remain guarded. Production integration can therefore proceed
independently. This experiment must be labelled the **source cohort pinned to
2c1f334, in a frozen optimized lower dependency context**, even if main advances.

`complete-build-admission.json`, if successfully produced, is a new combined
compiler/provenance admission. It explicitly links the original failed receipt;
it does not rewrite it or imply numerical/performance qualification. The captured
60-request stage, uncaptured complete projection stage, independent saved-data
reviews and same-cohort reference preflight still precede timing.

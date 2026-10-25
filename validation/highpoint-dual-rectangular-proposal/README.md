# Private rectangular first-mass / dilation source proposal

This proposal is frozen source only. It has not been compiled, tested, or
numerically evaluated, and root has not authorized its execution. The completed
four-domain full-component cohort in `../numerical-v1` stays unchanged.
Full IREGI rank-seven correctness is the project's current priority.

`source-manifest.json` identifies all 93 source files. It inherits the completed
92-file numerical source freeze and changes exactly two files: the capture
module and a new `rectangular_inputs.rs`. The original core sensitivity model,
child-layout guard, imported full-component amplitudes, result interpretation,
input policy, scalar masters, and branch/failure guards remain inherited.
The changed capture is an observation driver; it provides no public API.

The variables are an independent additive first squared-mass perturbation `a`
and common dilation `lambda=1+b`. The exact ordered quotient shape is
`[[0,0],[1,0],[0,1],[1,1]]`, with no pure second-mass component. Every shift
and mu scales by lambda, every squared mass by lambda squared, and only the
first squared mass then receives `+a`. Symbolica's Dualizer generates all 124
input components over Q. Both seeds equal one.

Changing the integration variable proves
`F(a,b)=lambda^-8 I6(m0_squared+a/lambda^2,...)`. Thus the rectangular response
is `lambda^-8*unit+a*lambda^-10*dot0` modulo `a^2`. Ordinary Symbolica
derivatives of this response and the abstract unit/dot variables produce the
four-by-two target matrix. A deliberately co-scaled mass perturbation has a
mixed coefficient of minus eight times dot0; the intended independent additive
mass perturbation has minus ten times dot0. The source tests distinguish them.
There is no second-mass derivative to assume or evaluate in this shape.

The capture driver proposes five fixed calls: singleton `[0]`, mixed
`[0,1,0]`, reordered `[0,0,1]`, empty `[]`, and singleton again `[0]`, where
profile one rejects mu=0. Intended coverage is six successful parent lanes,
two invalid controls and one empty call. All successful parent/actual packed
child values, amplitudes, native precision, signed zeros, actual routes,
interpretation metadata, clone mutation probes, and work counters are kept.
Plan/workspace/accuracy/batch failures serialize their stage and available
child observations. Inputs preserve their exact represented values.

Any later finite protocol must first qualify the six helper source tests,
review the actual frozen driver/dependency closure, then evaluate Float128 and
Float256 with the same exact 31-parameter fixture and independently audited
unit/dot targets used by the completed mass cohort. Every native Laurent and
rectangular output must pass the unchanged dimensionally normalized `1e-10`
gate and complete `2^-80` precision-convergence gate. Raw value/precision/sign/
route contexts and all invalid/empty/repeated calls remain required. Root must
approve a finite reviewed recipe before those compiler or numerical jobs.

This proposal checks one independent mass/dilation cross direction. It does
not qualify arbitrary mixed mass/momentum directions, pure higher-mass
derivatives, finite differences, public N6/N7 Dual constructors, current-Cargo
integration, rigorous achieved-error enclosures, E6 backend uncertainty, or
performance. Public exposure still requires those relevant broader gates.

Independent source review passed in
`independent-capture-source-review.json` (SHA256
`2598bae41ad009550c17b322f46d88e00a982c962a42d732da1aa51833eb9381`).
It establishes source consistency only. The inherited file writer uses ordinary
`std::fs::write`, without atomic replacement or power-loss synchronization.
Base parsing, helper preparation and exact-conversion failures occur before the
initial capture record; a future runner must retain stderr plus missing or
partial capture files as failed outcomes. Existing later stage errors are
serialized. None of those outcomes may be promoted to a successful zero result.


The separate committed source-proposal bundle pins the sealed full-component
parent capsule and retains only this source patch, complete source inventory,
research and independent source reviews. The patch contains the entire new
helper and its six source tests; large inherited generated programs are omitted.
Run `python3 validation/highpoint-dual-rectangular-proposal/check.py` from the
repository root to replay the source patch in memory and check all 93 resulting
files. This invokes only the committed parent capsule's byte reconstruction
facilities. It does not compile Rust or execute a Symbolica evaluator or test.
Original target paths inside historical manifests/reviews identify the frozen
source history; the portable source check does not read those ignored paths.

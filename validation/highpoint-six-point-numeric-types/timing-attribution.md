# Typed N6 timing attribution: saved logs and source only

The available logs directly show repeated **20.8–22.8 second scalar-master exact-evaluator preparation**. They do not time the numerical master kernel. This note reads existing artifacts only: no compilation, integral, evaluator, profile, retry, budget extension or production change was performed.

| Saved run | Scalar-master preparation events, in emission order (seconds) | Last durable capture | Step / runner aggregate seconds |
|---|---|---|---|
| Float128 dynamic Dual | 22.110825; 0.000040; 21.548351; 20.799653 | One affine singleton captured; `mixed` active at cancellation | 154.296796 / 164.436043 |
| Float256 dynamic Dual | 22.827833; 0.000008; 21.854441; no fourth completion line | First affine singleton active; no complete result | 153.629966 / 164.159543 |

Both were fixed 180-second lifecycle stages with a 20-second post-work reserve. The step timeout values were 153.643139 and 153.027857 seconds after immutable input checks. Both owned process groups are recorded absent. The wrapper totals include preparation, computation and lifecycle overhead; they are not benchmark kernel timings.

The machine-readable companion preserves all **74 emitted timing events** individually (38 and 36), their exact printed decimals, units and log line numbers, together with 20 inspected-file SHA-256 bindings. No durations are summed, subtracted from wall time, converted into a percentage, or extrapolated. Console messages have no scope IDs or timestamps; later preparation can be inside `reduce_batch` during lazy retry/chart setup. The final Float256 log line reports a primal exact evaluator, so the missing following scalar-master timer does not establish what finished or how much time remained in that stage.

The pinned runtime `execution.rs` labels the observed scalar-master interval around construction/reuse of `ExactMasterPlan::new_dual` programs. Numeric coefficient mapping is a separately emitted stage. Its per-prepare `PreparedMasterCache` already shares family programs during recursive fallback preparation. A `ReductionPlan` also retains exact execution through an ordered-shape `OnceLock`. Lazy planar retry retains a `CertifiedPlanarWorkspace`, whose per-chart numerical workspaces are separately cached. These source facts support investigating repeated exact preparation across separately prepared charts; the logs alone cannot identify every repeated block's chart or family. The capture already retains one outer `ThinSixWorkspace` across the entire schedule.

Concrete reuse options already provided by the inspected APIs:

- Keep `iregi_masters::ExactMasterPlan::new_dual(family, shape)` and call `instantiate(prototype)` at each desired numeric domain/precision. It retains exact rational instructions and the complete ordered shape, while each instantiated `MasterEvaluator` owns numerical buffers.
- Retain/clone immutable reduction plans so their existing Arc caches survive. A future shared preparation context could extend the private `PreparedMasterCache` across lazy chart construction; that wiring is **proposed work**, not an existing public constructor or a measured speedup. Preserve family, complete ordered shape, expression revision/configuration and backend semantics in any wider cache key; ordinary `None` and a one-component primal Dual are different layouts.
- Symbolica's `ExpressionEvaluator::clone`, `map_coeff_with_prec` and `into_batch_evaluator` support exact-program reuse followed by direct conversion and independent batch buffers. Reinstantiate from exact coefficients when precision rises; cloning a rounded evaluator cannot restore precision.
- `map_to_ring` consumes an exact evaluator and rejects external functions. It suits the algebraic input helper, not numerical log/dilog scalar-master preparation. `EvaluationDomain` is a function-resolution/domain trait. No `PreparedScalarMasters` symbol exists in the searched current crates and dependency/source trees; the actual public reuse API here is `ExactMasterPlan`.

Keep numerical workspaces, requested accuracy, precision, policies and derivative context separate. Every represented row still requires fresh planar/cofactor certificates; structural caching cannot reuse a prior sample's authorization to omit terms. No numerical-value cache is proposed.

Child sensitivity/error imports remain **primal-only**. The available affine scale identity does not qualify derivative uncertainty at requested 53 bits, independent directions, full Dual schedules, paired convergence or public N6 Dual support. Nothing here changes the failed/incomplete gates or authorizes another numerical attempt.

The complete source/log hash map and API anchors are in `timing-attribution.json`; that file is diagnostic evidence, not a new qualification or performance measurement.

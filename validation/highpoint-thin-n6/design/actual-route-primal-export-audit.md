# Actual-route primal envelope export for a thin N6 parent

Source-only audit, 2026-10-23. No implementation, build, test, numerical execution, or timing was performed. The frozen final candidate and the independent lazy-receipt review were not changed. This note defines a private interface needed before composing batched N5 results into a thin N6 result; it does not qualify that composition numerically.

All source references below are relative to `target/raw-distance-final-performance/candidate/crates/iregi-rust/src/`.

## Existing semantics and concrete seams

`PrimalCheck` contains monitor-value and amplitude offsets, dimension, and a label, but no output index (`stability.rs:46–52`). `prepare_primal_amplitudes` traverses basis then Laurent slot, appending sparse `[value, amplitude]` pairs only for outputs that depend on the master-amplitude map (`404–445`). That map starts with `ABS` of scalar leaf slots and propagates affine absolute contributions through the shared recurrence DAG. Constants in a master-dependent affine expression contribute their absolute value (`1140–1195`).

The monitor is explicitly a primal sensitivity estimate, not a backend-error bound or a compounded higher-Taylor error bound (`836–840`). `inspect_primal_lane_impl` uses operand-dependent roundoff on the amplitude and compares it with `2^(19-accuracy_bits) * max(|monitor value|, natural)` (`868–947`). Native operands retain their own precision; `OperandRoundoff` uses that precision, the configured precision, the fixed/tracked-domain margin, and underflow handling (`1240–1357`). Exporting only f64 magnitudes, ratios, or configured precision would lose this information.

Ordinary scalar execution fuses primal monitors after the ordinary output and local monitors; Dual execution evaluates a separate primal-only buffer without Dualizing ABS (`execution.rs:809–850,2037–2073`). The separately evaluated monitor value must not be substituted for the actually returned component zero or assumed bit-identical to it.

The direct success seam is `execution.rs:2124–2126`, inside the loop mapping `successful_lanes[compact]` to the original lane. Capture there, after finite-output, output-precision, local full-Taylor, primal, and applicable quadrature checks have passed. At this point the actual output slice, correct fused/separate primal slice, input row, and current lane guard context coexist. Reading `Workspace.primal_output`, `output`, or `guard_context` after the call cannot reliably reconstruct an analytic or fallback result.

`GuardContext` is mutable workspace scratch with plan-specific dimension/slot tables and lane-local lazy normalization caches (`stability/context.rs:9–18,21–65`). `begin_lane` resets it (`72–75`). Do not retain a reference to this cache as evidence for an earlier lane.

## Minimal private contract

A private per-lane sidecar on `BatchResult`, such as `primal_envelopes: Vec<Option<ChildEnvelope<T>>>`, is a suitable atomic carrier if every value replacement copies its matching sidecar in the same branch. It must have exactly one entry per original input lane, start entirely unavailable on every call, and be owned by the returned result. An internal result wrapper with a lane accessor returning values and evidence together is equally suitable. A separate unversioned `last_primal_output` accessor is not sufficient.

The surrounding `BatchResult` supplies the actual signed values, complete basis, convention, tensor weights, component count, full ordered Dual shape, and statuses. A successful sidecar needs:

- An explicit producing-route descriptor: terminal direct plan plus any analytic-profile, generic-fallback, certified-chart, and automatic-planar substitutions. Existing `fallback_used` and `analytic_used` flags describe attempts and cannot identify the final producer.
- Configured working bits and requested accuracy bits, plus the native amplitude values with their original operand precision retained. Require the expected working/accuracy context when importing a child; the first thin design should reject mismatches.
- A structurally indexed entry for every output slot `basis_index * 4 + Laurent_slot`. Add `output_index` to `PrimalCheck` during preparation; never recover it by parsing `label` or by zipping sparse monitors with dense outputs.
- Explicit distinction between `MasterDependent { amplitude, monitored_primal_value }`, structurally `NoMasterDependence`, and unavailable evidence. A missing buffer, an unsupported route, and an absent monitor are not interchangeable.
- An immutable snapshot identifying the current guard model and the producing plan's normalization context. For monitored outputs this can be the mapped dimension and native `natural` value, with lane-level native tolerance/prototype-unit and working/requested bits. A private method inside `stability` can map/copy these existing values without exposing `GuardContext` internals. If instead retaining a producing-plan handle, bind the exact snapshot/input layout to that handle; do not export a bare mutable cache.
- An explicit indication that the actual route requires propagated E6 quadrature estimates. Such a route is unavailable to this amplitude-only N6 interface.

Use the stored output order exactly: row, basis, `[UV1, IR1, IR2, finite]`, then Taylor component (`types.rs:143–157,203–208`). Primal evidence has one entry per basis/Laurent slot, not one per Taylor component. Metadata equality must include the ordered shape, not merely its component count (`types.rs:160–193`). The sidecar carries an estimated model, never an exactness certificate.

A `None` sidecar is acceptable as the minimum representation only if the thin parent always rejects it and cannot interpret it as zero error. A reason enum or existing diagnostics should distinguish failed lanes, missing capture, unsupported E6 propagation, and incompatible metadata. Ordinary child API success can remain unchanged while this narrower consumer rejects unavailable evidence.

## Route propagation and lifecycle

| Producer/replacement | Source seam | Required transfer |
|---|---|---|
| Direct ordinary result | `execution.rs:2058–2127` | Commit original-lane values and the just-accepted envelope together. |
| Analytic profile | `execution.rs:2333–2350` | Copy child `compact` evidence through the same `lanes[compact]` map as values; preserve the child producer and append the profile route. |
| Generic PV-to-IBP fallback | `execution.rs:2155–2189` | On successful fallback copy, replace the failed primary evidence with the fallback's actual producer. |
| Certified planar chart | `certified_planar.rs:486–509` | Copy the selected chart's actual child evidence alongside its values, preserving nested child fallback provenance and chart identity. |
| Automatic planar retry | `execution/planar_fallback.rs:148–202` | Keep existing whole-result basis/metadata/dimension validation at `174–188`; accept values and matching chart evidence together only on successful replacement. |

Failed primary attempts have no successful export. A failed zero-profile child that rejoins ordinary reduction must not leave an envelope in that lane (`execution.rs:1730–1739`). A failed retry must retain the original lane failure and no success envelope. A later successful route replaces both payloads. On an outer `Err`, no partial batch export is consumable. Keep all existing child statistics, proof-work, profile, and diagnostic harvesting before propagating errors.

The new per-result storage must be initialized before early malformed, empty, or all-invalid returns can expose a result; do not depend on existing late scratch clears (`execution.rs:1370–1450`). No evidence survives a second call by reference to old workspace scratch. Capture can be opt-in for the private thin-parent entry so ordinary reduction need not allocate this sidecar when unused.

## Parent preparation and recombination constraints

The current production `CertifiedPlanarReductionPlan` accepts only N5 (`certified_planar.rs:71–83`), chooses one chart for each lane, and scatters that chart's ordinary Workspace result (`441–510`). It contains no production weighted child aggregation. Its `box_identity` helper (`820–940`) is under `#[cfg(test)]` (`576`): it demonstrates batched pinches and signed Symbolica/Dualizer weighted sums and ordering, but it does not establish a production composed stability contract.

For the thin N6 route, signed recombination must still use Symbolica and the exact ordered Dual shape. A separate primal-only expression may propagate each actual child route amplitude through absolute primal weights. Keep parent local checks and output-precision checks on every Taylor component. Do not Dualize ABS or present component-zero envelopes as higher-Taylor error estimates.

A synthetic `ReductionPlan` containing external child values and amplitude parameters needs explicit preparation support. Existing amplitude preparation seeds only `plan.leaves` slots (`stability.rs:410–415`); adding child values to `plan.parameters` alone produces no external amplitude dependency. Existing parameter dimensions default to one except masses/scalar products (`98–106`), so imported N5 moments need their actual structural dimensions, as do their amplitude seeds. Preserve the N6 original kinematic `InputLayout` for parent normalization. Unit-power N5 output dimensions are rank minus six; N6 dimensions are rank minus eight (`156–166`). A child snapshot is provenance and cannot replace the parent's normalization or requested-error check.

A zero default for an absent child primal monitor needs special care. A structurally master-independent child output has no child master-sensitivity check, but when that contribution enters a parent expression that also depends on masters, the existing affine amplitude builder includes the absolute constant contribution (`1188–1193`). Reclassifying every imported child output as a synthetic master variable and seeding the independent ones with zero can drop that contribution. Preserve the independent operand's coefficient role in parent preparation, or provide its native absolute returned primal as the imported operand contribution. Only an explicit structural zero can safely be treated as zero without this distinction. This is separate from accepting a child as exact, which is never justified by `Success`.

## E6 exclusion and remaining blockers

`QuadratureWorkspace` stores backend per-Taylor error estimates and evaluates their positive coefficient contractions separately from primal amplitude (`execution.rs:435–448,500–584`). The final guard checks all Taylor components; component zero combines propagated quadrature error with the primal working-unit sensitivity in one budget (`stability/quadrature.rs:206–210,320–367`). Exporting only the primal amplitude loses this work even when the child returns `Success`.

For this bounded contract, reject actual producing routes with a nonempty propagated E6 quadrature model. Conservatively marking any actual terminal `QuadratureWorkspace` as unsupported is sufficient; do not infer absence of an error obligation from a rounded zero estimate. A narrower inactive-route exemption would require an explicit structural/provenance argument outside this minimal proposal. A different successful planar/analytic replacement without E6 can export its own evidence normally.

Concrete implementation blockers remain: structural output mapping and absence classification; a private external-value/amplitude seed and dimension contract; immutable per-lane guard snapshots; atomic propagation through every successful replacement; and explicit E6 rejection. These are necessary before the thin parent can rely on the export. The coupled sidecar design addresses stale-buffer risks but does not by itself close these preparation or numerical-qualification requirements.

Future validation must exercise different successful routes within one batch, sparse output monitors, master-independent nonzero terms mixed with master-dependent terms, malformed/empty/reordered consecutive calls, failure then fallback success, chart failure rejoining ordinary reduction, full Dual ordering, lower-precision native operands, and E6 rejection. None was run for this audit.

## Frozen source hashes (SHA-256)

- `stability.rs`: `36db72b53c56a7cbea033806b96a705c35eed6c6c2fd2e504234aa49551093a4`
- `stability/context.rs`: `0a6016687b4b2d0e5505cd4a1ca8574dd4d901c5cf003f9fca177f49fe78af4d`
- `stability/quadrature.rs`: `993dca8bfc6c82cb64a930346ad2eb7724b2cfb7d61e7e7abd3fe5fa8263ba43`
- `execution.rs`: `6b9aa6742d13a7e19b094f61b242bafece895c6a5dd54c6a7246e73bd76a0d6f`
- `execution/planar_fallback.rs`: `1e0186c4b61a386e4ecd19dc9c119a407643f220f04694d096056644b9cc662b`
- `certified_planar.rs`: `9dbb9735e5760c327095b1e61a8a3f0c04a03b1d6e4908d185a3023d0a39d749`
- `types.rs`: `18ade4026a89f98a4b7980a453ae87596caefb7bf2d5396db86506641d811849`

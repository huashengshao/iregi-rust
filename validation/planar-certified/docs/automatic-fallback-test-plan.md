# Automatic planar fallback qualification plan

Status: design only; implementation and production promotion await wrapper rank-seven qualification and review.

## Eligibility and routing

Only ordinary N5 with unit powers, h=0, preserved Cartesian inputs, and requested PV/Hybrid may attempt the fallback. Explicit IBP, supplied invariants, legacy snapping, generalized powers/dimensions, active zero profiles, and already-certified fixed charts are excluded. Preserve caller convention, tensor weights, target accuracy, prototype, complete ordered Dual shape, profiling selection, and input values.

The dispatcher belongs after `reduce_batch_impl` returns a complete result at the public outer boundary, so primary failures returned early by argument/master/profile processing are still eligible. Select original row IDs with Unstable/MasterFailure; never use an internal compacted valid-lane list as the original batch index. Pack a single attempted batch; the wrapper certifies all Taylor components and groups chart calls internally. Suppress duplicate attempts in Hybrid children and all certified chart children.

## Result and diagnostic invariants

Only a successful complete wrapper lane can replace a primary result. Preserve the original primary status and diagnostics when certification, chart preparation, or retry fails; a transverse/unsupported certificate may not turn a rescuable Unstable into InvalidInput. Keep a note of both primary failure and retry outcome. Successful retry marks fallback_used and analytic_used, preserves metadata, and copies every output component. Malformed outer buffers return their original error without starting a retry.

Stats count actual work: primary input_rows unchanged, fallback_rows adds original attempted rows once, fallback_successes counts only recovered lanes, and child argument/master/reduction/analytic counters are aggregated once. A certificate-only rejection contributes no numerical master/reduction rows. Profiling includes lazy preparation and certificate time, adds child stages once, and outer elapsed total covers the entire attempt. No per-sample scalar reduction loop is permitted.

## Required regression cases

1. Exact planar batch with two charts, repeated/reordered lanes, a nonplanar failed row, invalid scale, and a successful ordinary nonplanar control. Compare all outputs to the qualified explicit wrapper and independent boxes. Verify input and full metadata preservation, diagnostics and counter deltas.
2. Tangential reordered mixed/second Dual jets plus a transverse jet; retain valid lanes, reject transverse retry, and preserve its original primary failure category. Compare all Taylor/Laurent/tensor values.
3. Both requested PV and Hybrid dispatch once. Explicit IBP remains untouched. Fixed chart children and preexisting exact profiles cannot recursively invoke the planar wrapper.
4. Empty batch, wrong component count/buffer length, certificate unavailable for a custom numeric domain, no regular chart/homogeneous geometry, and deliberately failed numerical child. No rejected lane exposes initialized zero values.
5. Change accuracy/profiling before and after lazy wrapper creation, clone workspace, reorder/chunk batches, and reuse the same plan with independent workspaces. Structural memoization must preserve full ordered shape; numerical buffers never leak across lanes or calls.
6. Rank-seven qualification retains all330 tensor moments times four Laurent slots, including UV poles, before automatic production promotion. Binary64 failed families remain visible; a separate positive family cannot erase them.

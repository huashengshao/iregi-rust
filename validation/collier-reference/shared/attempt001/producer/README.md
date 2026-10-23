# Generic TNten shared-domain source candidate

This directory is a new optional reference-tooling candidate. It is excluded
from the current report's evidence freeze. No driver compilation, Symbolica
input preparation or reduction execution has occurred for it. Existing
N2/N3 timing and N4 failed/diagnostic receipts remain unchanged. Production
Rust and both external reference libraries are unchanged.

The source inventory is `driver.f90`, `support.py`, `prepare_inputs.py`,
`build.py`, `run_correctness.py` and `test_protocol.py`. The driver is derived
from the reviewed N4 diagnostic source and calls generic `TNten_cll`, with
explicit `SetTenRed_cll(6)`. It supports ordinary N2–N7, preserves error and
accuracy gates, and exposes native flags/absolute estimates plus separately
labelled rejected raw moments. The first runner admits only ranks0–2 at
N5–N7. COLI1 and DD2 remain separate policies. A generic DD N7 tensor can
reduce through lower-point DD calls; coefficient-level G_cll's unsupported
status must not be applied to that path without execution evidence.

The immutable original-IREGI benchmark executable already supports N<=7 and
rank<=7 with finite real four-vectors. Its original tensor interface, native
four-slot output, input-preserving configuration and per-sample cache disposal
are reused directly. **No IREGI build or relink is needed.** Generalized powers
and dimension shifts are explicitly rejected by this shared comparison,
rather than silently ignored. Exact rational inputs must be representable at
the binary64 external-reference boundary; precision loss is an explicit error.

The source-defined matrix has17 families, each at batch1 and32, for34 rows:

- The unchanged four N2/N3 rank0/1 families and four N4 rank0–3 families come
  first, preserving their exact32 input lanes.
- N5/N6/N7 rank0/1/2 use the respective prefixes of all three retained
  conditioned-mass rows. Batch32 cycles the base/scaled/mass-deformed rows
  explicitly: this is three distinct kinematics, not32 independent branches.

The existing Symbolica `prepare` CLI constructs every exact scalar invariant
and positive Feynman-mass-polynomial bound used for admission. The sufficient
bound is `min(m_i²)-max(0,s_ij)/2>0`, using the sum of pairwise Feynman weights
at most1/2. This new envelope permits a real time component but restricts
squared masses to positive real values. Exact prepared constants, input DOTs,
CLI hash and source/model/fixture guards must accompany the generated input.
The Fortran driver independently rejects a nonpositive numerical bound.

All16 fixed N2/N3/N4 batch rows must pass their per-engine interface regression
before **any** higher-point call. Hybrid IREGI outputs/status compare exactly
to retained prior captures, and all three N4 IREGI modes compare to their
retained captures. The generic and old COLLIER wrappers compare exact native
statuses, accepted complete outputs and pole probes in both modes. Rejected
raw numbers are additionally compared as diagnostics and cannot qualify a
lane. A failed regression marks every higher-point row `not_run`; no case is
omitted. Fixed N4 accuracy rejections are expected and must remain rejected.

Higher-point execution, once separately authorized, compares every requested
Cartesian component and all native `[UV1,IR1,IR2,finite]` slots against all
three original IREGI methods. Delta-parameter pole probes and independent UV
checks remain explicit. The complete response is saved before validation can
raise. Native error or accuracy rejection stays visible even when raw numbers
meet the external1e−10 tolerance. This runner has no timing-cohort mode; the
internal one-call clock fields are diagnostic transport only.

The build and execution plan is bounded and sequential:

1. Run the14 low-cost protocol tests once (authorized), preserving their log
   and source bindings. These tests exercise index ordering, full Laurent
   arrays, beyond53-bit rejection, unsupported interfaces and failure gates.
2. Obtain the narrow read-only source/protocol review, binding every candidate
   `.py` and `.f90` file. Until then, do not run the linker or reference kernels.
3. When authorized, prepare the fixed input/domain witnesses on CPU26 with a
   120 s request deadline. Expected duration is seconds; no reduction is run.
4. Link only the reviewed driver at the existing strictO3 flags against the
   immutable COLLIER archive and module files, CPU26, hard60 s link cap. Expected
   duration is below one second, based on the preceding diagnostic link.
5. Execute the frozen34-row correctness protocol, CPU26,20 s per request and
   120 s request deadline, plus up to15 s process-close finalization. A separate
   outer135 s cap can enforce that bound. There are202 preregistered requests
   if all fixed interface checks pass; otherwise higher-point calls are skipped
   visibly. No performance cohort is authorized by this plan.

The sum of those preparation/link/correctness caps is315 s, serial, with no
library rebuild or background work. A noisy host or numerical failure does
not authorize fixture substitution or threshold changes. All runs use new
attempt directories and preserve partial output, first errors, source guards
and prior failures. After capture, package full JSON with deterministic gzip,
input/preparation artifacts and exact producer snapshots, compact family
statuses, all source/input/binary/module hashes, and an independent package
review. Rebuild the Typst report only from that durable evidence, retaining
the current timing cells and showing new failures without timing values.

Proposed commands, **pending source review and execution authorization**:

```sh
python3 validation/collier-reference/shared/prepare_inputs.py \
  --output target/collier-reference/shared-inputs-NEW --cpu 26
python3 validation/collier-reference/shared/build.py \
  --output target/reference/collier/shared-build-NEW \
  --review validation/collier-reference/shared/source-review.json --cpu 26
python3 validation/collier-reference/shared/run_correctness.py \
  --input target/collier-reference/shared-inputs-NEW/inputs.json \
  --build target/reference/collier/shared-build-NEW/build.json \
  --output target/collier-reference/shared-correctness-NEW --cpu 26
```

Source details and supported-policy caveats are derived in
`docs/research/collier-n5-n7-harness-design.md`. This source candidate is not a
numerically qualified implementation or a timing result.

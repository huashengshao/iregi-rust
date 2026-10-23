# Private selected-native whole-reduction experiment

Status: source proposal only; no compilation, numerical execution or timing yet.

## Scope and selection seam

Copy the current production core and masters source, unchanged since commit
06706e2a1e4f0082889a53187c80bbe97803340f (including the stability collector).
Build two private core libraries from the same copied source and one shared
private masters library. A compile-time private policy selects the candidate;
the baseline retains Symbolica. Do not enable the existing global native-batch
feature, import generated D0, rebuild dependencies, or edit production files.

The private masters library adds a concrete binary64 evaluator variant using
the unchanged generated A0/B0/C0 modules and constants. A consuming selector on
an already instantiated MasterEvaluator changes only its evaluator field, and
only when the shape is None, T is exactly f64, and the family is A0/B0/C0.
All other cases return the original evaluator unchanged: DoubleFloat, Float,
ordinary D0/dB0 and all Dual shapes. Any downcasts of the existing input/output
Vec buffers are checked std::any::Any downcasts, without unsafe code, numeric
conversion, copying or intermediate allocations. The concrete native dispatch
keeps the existing Whole batch policy, six outputs and primitive/control graph.

Core selection occurs after ExactMasterPlan::instantiate, so structural plans
and their ordered expressions remain identical in both copies. Both variants
therefore pay the same exact preparation before optional native setup. This
experiment measures warmed whole calls later; it makes no preparation-speed
claim. Add the immutable private policy bit to the exact cache key explicitly.
Numerical workspaces are independently owned; no numerical cache is shared.

The public MasterEvaluator::evaluate_batch body is unchanged apart from its
one new evaluator-dispatch arm. Input validation, valid-lane compaction,
normalization, D0 relabelling, six-output storage, UV/IR handling, derivative
discriminants, output validation and all public errors remain the same code.
The existing new/new_dual/default-backend APIs are unchanged. A private accessor
can expose the retained sixth output for diagnostics, without recomputation.

Both core libraries receive the same optional observational master hook. It is
disabled by default and enabled explicitly during numerical qualification.
Later timing must disable it before any warmup/pilot. Retain exact request
ordering, all six master outputs, backend names, final tensor arrays and lane
diagnostics. The root-owned stability collector remains unchanged.

## Closure and bounded build

Reuse target/e6-direct-n2/preparation.json and its retained complete native-object
debug closure, originating from validation/near-vacuum-production/attempt004.
Relevant archives are oneloop-ad2b1eccf125afee, symbolica-06e42762cabb77d9,
serde-b04ba25115fa19f8, serde_json-d657c5438f354a41. Reuse the documented
thiserror native archive/proc macro from target/core-fused-cse-census rather than
rebuilding it. Record the actual completed Cargo events, profiles/features,
all source and archive hashes, compiler version and ELF-object checks.

First compile the selected master rlib and both core rlibs with opt0, no ThinLTO,
no debug info, on CPUs20/21; each command is bounded to180 seconds. Link one
combined correctness probe using this same closure, initially opt0 and no
ThinLTO, bounded to600 seconds. No dependency build is permitted. A later
optimized pair would require explicit scope/scheduling confirmation; debug
semantics results cannot support performance claims.

## Numerical admission before timing

Run under120 seconds total, with all missing/failed cases retained:

- All eight frozen N2/N3 rank0/1, singleton/batch32 families, whole tensor and
  Laurent arrays, baseline/candidate and original IREGI at the existing
  dimensionally normalized1e-10 criterion. Same frozen inputs and reference
  binary as validation/native-master-replay. Preserve statuses, diagnostics,
  fallback/analytic flags and actual ordered master group counts.
- Public adapter controls adapted from existing tests: empty/singleton/odd
  batches, mixed valid/invalid neighbors and branches, invalid shapes/scales,
  complex masses, scaleless B0 UV/IR cancellation, reused buffers and recovery.
  Compare all six retained master outputs on successful lanes.
- Explicit unchanged-path controls for D0/dB0, DoubleFloat, Float including
  mixed precision and beyond53-bit inputs, and ordinary/seeded Dual shapes.
  Assert backend selection and exact represented value/precision/zero-sign
  parity for these paths. Reuse current fixture inputs rather than inventing
  algebra or weakening thresholds.

The selected native formulas can round differently from Symbolica; do not demand
cross-backend bit identity. Each backend must reproduce its own outputs exactly
on repeated calls, and unchanged paths must remain bit/precision/sign identical.
This experiment may establish whole-call correctness and later whole-call
performance only after separate timing authorization. It is not production
adoption, a raw-kernel speed prediction or an IREGI performance claim.

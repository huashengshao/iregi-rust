# Optimistic double-precision COLLIER opening-table campaign

This is a new campaign; the earlier `opening-collier-20261026` archive remains
unchanged. All arithmetic is COLLIER 1.2.10 binary64. The exact E-family routing,
real squared masses, scale, and every cumulative Cartesian tensor through the
requested rank are preserved. All four native Laurent slots are compared against
the retained independently qualified TIRust arrays from the earlier opening suite.

The public requested accuracy is **1e-6 for N5R5, N5R6, and N6R6**, and **1e-10
for the other nine rows**. Critical accuracy is 1e-3 for every row. This is an
optimistic timing showcase, not the earlier strict 1e-10 coefficientwise gate.
Native error/accuracy flags, internal rank-error estimates, nonfinite fields,
and independent UV/IR parameter probes remain available; native warning flags
alone do not discard an observed time.

The predeclared public options are:

| Rows | Candidate options |
| --- | --- |
| Nine N<=4 rows | COLI or DD; threshold 6; argument permutation off |
| N5R5 | COLI or DD; argument permutation off or on |
| N5R6 | COLI; argument permutation off or on |
| N6R6 | COLI or DD; tensor threshold 6 or 7; argument permutation off or on |

DD does not support N5R6. Threshold 6 uses N6 direct tensor reduction; threshold 7
constructs coefficients and then tensors. Public argument permutation preserves
the integral and its Cartesian components, but explicitly disables the cache
system, including local memoization. Ordinary candidates retain local-only
memoization reset by every root tensor call; no candidate uses an event cache.
These are all public options in the unmodified COLLIER library, not precision
promotion or private implementation patches. Relevant upstream sources are
`src/collier_init.F90` (`SetMode`, `SetReqAcc`, `SetCritAcc`, `SetTenRed`,
`SwitchOnArgPerm`) and `src/tensors/TensorReduction.F90:973`; the shipped manual
has the mode, accuracy, tensor-reduction, and argument-permutation API sections.

Every one of the **32 candidates** is measured: preflight pole probes, a warm
pilot, eleven fixed blocks targeting 30 ms per block, and postflight pole probes.
The pilot calibrates only the call count (cap 1,000,000); it does not select a
candidate. The opening cell selects the smallest eleven-block mean among complete,
finite candidates with achieved whole-array relative error <=1e-3. If no candidate
meets this threshold, the fastest observed duration remains visible with the actual
accuracy/nonfinite warning. Every trial is retained. This is an absolute timing
showcase; it is not a synchronized TIRust/COLLIER ratio or a controlled-host
performance qualification.

The displayed achieved relative error is a true whole-array norm ratio after
physical dimensional normalization. For moment degree d and N propagators, put
`s_j = mu^(d+4-2N)`, `E = max_j |computed_j-reference_j|/s_j`,
`A = max_j |reference_j|/s_j`, and `delta_rel = E/A`, with j ranging over all
cumulative Cartesian moments and all Laurent coefficients. The old maximum
coefficientwise mixed normalized error is also retained for audit. Finite
fields are compared using their exact binary64 rational values. Nonfinite fields
are counted and never treated as zero; the finite-subset error cannot
qualify a partially nonfinite tensor.

The timer includes invariant/routing preparation, per-root `InitEvent_cll`,
public tensor calls including masters, normalization and gathering all requested
Cartesian outputs. Native diagnostic/finite scans and full-array comparisons are
**outside** the timer, as are initialization, warmup, pole probes, block snapshots,
transport and JSON serialization. Internal COLLIER error propagation is untouched.

The source driver is derived narrowly from the prior opening COLLIER driver.
Initialization capacity safeguards remain: `Nmax=max(N,2)` and
`Rmax=max(R,1,N-max(N-2,4))`. They avoid upstream initialization corner cases
without changing the requested rank, tensor shape, or mathematical integral.

Root owns the build, frozen binary/library/module receipts, process-group
supervision and CPU quiet window. This runner never compiles or imports native
Python modules. From the project root, after sourcing the pinned toolchain env:

```sh
python3 validation/benchmark/opening-double-20261026/collier/run.py \
  --binary target/reference/collier/opening-double-build001/collier-opening-double \
  --binary-sha256 "$COLLIER_DOUBLE_BINARY_SHA256" \
  --inputs validation/benchmark/opening-double-20261026/inputs.json \
  --output target/opening-double-20261026/collier-capture001 \
  --cpu 18 --quiet-note 'Root-granted CPU18 numerical quiet window'
```

Use the binary digest from the retained root build receipt. Output must be a new
`target/` directory, and every later attempt needs its own directory. No failed
or slower candidate may overwrite an earlier capture.

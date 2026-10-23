# Private deterministic coefficient compiler experiment

No production change or timing qualification. The current CLI still uses direct translation.

The same four prepared physical numerators were compiled with Symbolica using:

- `direct`: `direct_translation(true)`, zero Horner iterations.
- `allocated`: the direct program followed by `optimize_stack()`.
- `cse0`: one deterministic Horner pass with zero candidate variables and zero common-pair passes; Symbolica then removes common instructions and allocates storage.
- `pair1`: the same setup with one common-pair pass, at most 100,000 pair-cache entries and distance 64.

An empty Horner variable list deliberately excludes variable-order factoring. The root evaluator with zero Horner iterations bypasses CSE/CPE, so changing only its common-pair setting would not exercise those optimizations. No global expression expansion was removed.

## Exact algebra and preparation diagnostics

All 223 physical coefficient expressions, in unchanged loop-monomial order, were proved equal for all four compiler modes: **892 exact identities**. The validation interpreter reads exported instructions into Symbolica `Atom` operations and requires every output-minus-original expanded difference to be literal zero. All operand reads precede aliased writes. It rejects control flow, registered constants and helpers rather than guessing their meaning. The three-source API investigation and independent source review are in `preparation.json`. Sixteen constant-only proof cases and empty-numerator controls also passed.

| Graph | Direct multiplications | CSE0 multiplications | Pair1 multiplications | Direct/CSE0/Pair1 temporary slots | Pair1 preparation diagnostic |
|---|---:|---:|---:|---|---:|
| ggH | 909 | 796 | 423 | 149 / 37 / 59 | 1.08 ms |
| ggHH | 15,132 | 12,450 | 6,035 | 2,674 / 357 / 451 | 13.26 ms |
| ggHHH | 68,582 | 57,756 | 28,853 | 8,261 / 865 / 1,063 | 77.88 ms |
| massless up box | 308,938 | 246,438 | 114,436 | 44,407 / 5,080 / 5,455 | 463.27 ms |

Preparation values are single diagnostic observations in one process, with modes in the displayed order. They are **not** latency comparisons or throughput acceptance. Changed instruction counts and arithmetic counts do not imply a speedup.

## Numerical results and retained raw failures

There are 347,880 real-component comparisons across f64, DoubleFloat, Float128, Float256 and mixed80/128/256-bit Float inputs. Batches are empty, singleton, odd,32 and reused smaller shapes. Inputs, support, row/component metadata and prototype contexts are unchanged. The corpus includes canonical nonzero numerators, zero and negative-zero coupling, complex coupling, values distinguishable beyond53bits, malformed-shape recovery, missing parameter bindings, and constant-only/empty numerators.

The original raw test remains

`|actual-reference| / max(1, |actual|, |reference|) <= 1e-10`

for each real and imaginary coefficient component. It reports **1,281 failures**, all in binary64 near-zero dimensionful coefficients; the direct baseline is included among the failures. The ggHH, ggHHH and up-box processes retain their nonzero exit statuses. Extra18-digit mixed-input diagnostics also fail on the larger graphs. No tolerance was changed to hide these results.

DD and Float128 agree with a256-bit evaluator of exactly lifted represented inputs at the retained20/28-digit thresholds. Float256 candidate-versus-direct is a same-precision consistency check, not an independent256-bit accuracy certificate. Near-zero reference values may retain very few tracked precision bits. Output precision tracking and zero signs may change with arithmetic order; they are recorded and counted, not described as bitwise preserved. The reference lift treats zero as an exact rational value, so it is not a signed-zero oracle. The inspected physical programs contain no inversions or conditionals, and their only non-polynomial operation is a positive constant square root.

## Separate physical dimension diagnostic

The raw test above is unit-sensitive for a coefficient whose physical dimension is nonzero. A separate Symbolica calculation verifies all223 scaling identities

`c(lambda*p, lambda*m) = lambda^(N-rank) * c(p,m)`

for these fermion-loop numerators. Masses and external momenta have dimension1; gauge/Yukawa couplings and the supplied external polarization vectors have dimension0. The assumed total numerator dimensions3/4/5/4 are therefore checked for every expression. The display-name namespace renaming is injective, and evaluator admission verifies that every coefficient free input is bound (unused declared inputs are allowed).

The separate diagnostic uses

`|actual-reference| / max(Q^(N-rank), |actual|, |reference|)`,

where `Q` is the maximum absolute component of the dimension-one masses/momenta in that lane; those inputs are checked real. It has **zero failures** at1e-10 and maximum **2.20758e-15**. This does not replace the raw criterion, qualify end-to-end physical accuracy, or authorize adoption.

For example, ggHH coefficient35 multiplies `q0` and has dimension3. With `G=1`, `MT=173`, external energy300 and the exact saved binary64 input context, direct evaluation gives `-2^-28`. The256-bit evaluation leaves an approximately2.90e-70 residual with three tracked bits. Symbolica exact substitution proves the coefficient is **exactly zero**. Its natural scale is `Q^3=300^3`; `gghh-residual-witness.json` retains the complete input context and every mode's original raw residual.

## Reproduction and scope

`compile.py` and `compile_dimension.py` use only the retained complete6b24 dependency closure, CPU8/9, opt2, thinLTO and one codegen unit. Source, archive and binary hashes are checked before and after compilation. `run.py` records a300-second bound per graph and all failures. `dimension-run.json` binds the separate bounded proof command, exact inputs, source and binary. `analyze.py` reproduces both unchanged raw metrics and the separately labelled dimensional diagnostic.

The four canonical kinematic points and coupling controls do not establish general conditioning, overflow or physical-process coverage. No occurrence-Horner search, production change or warm timing was attempted. Every original output, prepared coefficient expression, structural record and failed-run log is included in `raw-qualification.tar.gz`, with individual hashes in `raw-index.json`. The original target paths and static binaries are also retained.

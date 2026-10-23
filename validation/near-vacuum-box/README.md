# Validation-only near-vacuum box series

The implementation lives in
`crates/iregi-rust/examples/support/near_vacuum_box.rs`. It does not alter scalar
master dispatch or the reduction library. The current compact evidence is
`qualification.json`; historical failures remain beside successful attempts.

The first qualified family uses 256-bit working arithmetic, a requested
absolute/relative budget of `2^-128`, and the Symbolica Taylor shape
`[00,10,01,11,20,02]`. Order four certifies four tiny-invariant or vacuum lanes,
24 components in total. Order two certifies the exact-vacuum components and
rejects the tiny-invariant mixed components that its remainder cannot cover.
Rejected lanes expose no result values. The moderately small-invariant overlap
is separately certified at 24 bits; its ordinary DNS comparison is primal.
These observations do not qualify general D0 or production E6 accuracy.

The current package contains 15 distinct validation settings and three final
source-provenance repetitions, all passing. Primal and mixed shapes pass with
the following explicit working/requested precisions; no type is claimed to
deliver more than its tested budget.

| Type | Working bits | Requested bits |
|---|---:|---:|
| f64 | 53 | 40 |
| DoubleFloat | 106 | 80 |
| Float | 128 | 100 |
| Float | 256 | 128 |

Unequal primal masses separated by `eta=2^-64` remain exactly represented in
DoubleFloat and both Float settings, with six components checked in three
lanes for each type. The heterogeneous exact-vacuum test checks seven components
in three lanes at Float256/requested128. Order four succeeds; order two hides
its incomplete results and rejects the omitted third derivative. Including the
three final source repetitions, the compact manifest binds 261 accepted
primary component checks. Expected rejection cases remain visible.

The candidate integrates a generic order-N polynomial using Symbolica exact
rational polynomials, compiles its derivative components with Dualizer, and
evaluates each instruction across active sample lanes. ComplexBall evaluates
the retained polynomial enclosure; a separate RealBall program bounds every
component of the omitted series. Acceptance uses the maximum distance from
the returned value to the entire enclosing rectangle, with the full tail
added. The independent oracle derives the routing polynomial, integrates a
different order-eight expansion in `eta/M`, and differentiates its exact mass
dependence. Neither oracle calls the candidate or production reduction.

The retained failed attempts establish why preparation changed:

| Attempt | Outcome |
|---|---|
| N2/N4 expression-valued polynomial coefficients | Both reached a 60-second preparation bound without numerical output |
| Instrumented N2 | Series ready in 8 ms; conversion to an expression-valued polynomial timed out |
| Exact rational N2, original oracle | Candidate ready in 48 ms; redundant oracle expression expansion timed out |
| Exact rational N4, original resource cap | 103243 terms exceeded the initial 100000-term cap |
| Exact rational candidate and direct polynomial oracle conversion | N2 and N4 selected mixed-derivative validation passed |

The final bounded preparation cap is 150000 terms, enough for the complete N4
basis. No numerical tolerance changed. Durations are diagnostic process or
preparation observations; they are not performance comparisons.

Run the current Rust examples from the repository root after sourcing the
development environment. A locally supplied Symbolica license can be sourced
separately; it must not be committed or printed.

```sh
source scripts/env.sh
cargo run --locked -p iregi-rust --example near_vacuum_validate -- 4 mixed float256 128
cargo run --locked -p iregi-rust --example near_vacuum_heterogeneous -- 4
cargo run --locked -p iregi-rust --example near_vacuum_unequal -- float256 128
```

The latter two examples are separately qualified stages; consult the latest
manifest for exact coverage and source provenance. The heterogeneous
vacuum oracle differentiates the unexpanded integrand and integrates the exact
finite jets, giving zero reference truncation radius. The unequal-mass oracle
uses `m_i²=M+[-1,0,1,2]_i*eta` and a different auxiliary expansion center from
the candidate, preserving input mass separations beyond 53 bits.

For the recorded isolated builds, `build.py` freezes source snapshots and
links retained baseline oneloop/Symbolica archives. `run.py` pins one CPU,
enforces a timeout, and checks source, archive, and binary hashes before and
after each run. Its manifest identifies the exact older dependency scope;
ordinary Cargo reproduction uses the current pinned workspace dependencies.
The estimated exported-instruction count multiplied by active lanes is
labelled as an estimate, not runtime instrumentation. Actual batch-call counts
and the existing Symbolica instruction-major evaluator establish the execution
layout separately.

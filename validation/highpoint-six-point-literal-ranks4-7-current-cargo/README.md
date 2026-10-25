# Literal N6 ranks four through seven in the captured current Cargo context

All eight public SixPoint captures passed: literal ranks 4, 5, 6 and 7, each at
Symbolica Float128/256 and requested accuracy 53, with one retained real massive
base sample, unit propagator powers, h=0 and native raw Cartesian components.
Every cumulative moment and all four complex Laurent coefficients are retained.

The saved gate compares 5,888 coefficients with original quad-precision IREGI
at the unchanged dimensionally normalized mixed tolerance 1e-10, the same 5,888
coefficients with the earlier qualified rank-seven prefixes at 2^-80, and 2,944
cross-precision pairs at 2^-80. The fixed rank-r unit is 2^(r-8). The unchanged
example emits exact represented rationals and actual component precision, but
no signed-zero flags. Timings are correctness diagnostics, not performance
comparisons.

This capsule includes the adopted routing/Cayley patch provenance, actual
51-test IBP Cargo receipt/log, captured Cargo contexts, six-point build
event/receipt/log, all eight result/receipt/log triples, saved comparisons and
independent source, build and numerical/terminal reviews. Compiled binaries
are omitted explicitly; their historical hashes and independent build/owned
process cleanup evidence remain recorded. No live process claim is replayed.

The source parent is the exact 64-file archive under
`validation/public-rank7-current-cargo-n1-n5`, plus the unchanged `six_point`
example retained here. The earlier rank-seven reference parent is
`validation/highpoint-six-point-rank7-lifecycle`. Keep both directories beside
this capsule. This is the immutable context captured after Cayley adoption
and before the separate typed-Dual early-error reset edit; it does not claim
that subsequently changed main sources match this snapshot.

Run from the repository:

```sh
source scripts/env.sh
python3 validation/highpoint-six-point-literal-ranks4-7-current-cargo/check.py
```

The checker verifies all contained files, durable parents, exact source and
receipt guards, then replays only the frozen saved-data numerical comparator
through an isolated in-memory path adapter. It invokes no Rust, Symbolica,
scalar master, reference executable or compiler. Independent audits remain
preserved historical reviews; replaying the producer's saved comparator does
not create a new independent audit.

This is one retained family. Other kinematics, complex high-point masses,
Duals, dotted propagators, dimension shifts, physical numerators, concurrency,
performance and the full port remain separate qualification requirements.

# Ordinary rank-six orthogonal CLI record — partial

Twelve of fourteen Float128/256 CLI calls produce complete tensor arrays and
pass all24,444 available numerical checks. The two collinear zero-Gram N3 calls
remain unqualified: both PV and IBP fallback report nonfinite coefficients, and
no successful moment arrays are returned. The whole catalogue remains failed/
partial. These are functional reduction failures, not timeouts or resource caps.

The successful calls cover three equal-mass N2 threshold positions and N2/N3/N4
complex squared masses in the lower half-plane, at rank6 with unit powers. Each
lane requests all210 cumulative Cartesian tensor moments and all four native
slots `[UV1,IR1,IR2,finite]`. Requested Hybrid runs actual PV through the Generic
engine. Successful lanes use no analytic route, fallback or precision rescue.
Below-threshold batches contain good, invalid-mu and duplicate-good neighbors:
the two good arrays agree exactly and the invalid lane returns no coefficients.

The independent stdlib/Fraction audit reproduces11,760 reference comparisons,
5,040 precision pairs,1,680 exact duplicate checks,5,880 separate IR checks,
80 convergent UV checks and4 below/boundary scalar branch checks. Above-threshold
absorptive signs and both invalid neighbors are also checked. Maximum normalized
reference error is `2.629e-15` at N4; precision-pair error is `7.167e-36`.
Thresholds remain `1e-10` and `2^-80`. The two failed cases leave1,680 unavailable
complex slots; they are not represented by successful zeros or omitted from the
catalogue outcome.

Six original quad reference arrays are admitted by the existing independent
reference review. Original N4 complex quad output is retained as **rejected**:
its `stable=true` and zero finite scalar are insufficient. N4 instead uses the
independently audited order32 full-array parameter oracle, admitted by
`0352163a…`/`b2a68e18…`. Its convergence is empirical, not a rigorous enclosure.

The exact77-file source snapshot and CLI build are inherited from
`validation/n6-rank6-generalized-current-cli`; the complex oracle is inherited
from `validation/complex-parameter-tensor-oracle`. The small new payload contains
the14 terminal CLI captures, inputs/controllers, missing threshold/collinear
original quad raw files, independent audit and final partial qualification.
All parents and byte identities are pinned. No ELF, Python cache, literal
Symbolica license or new compiler/dependency closure is included. Omitted native,
external tool and process attestations remain historical; replay does not
freshly verify those files or process absence.

From the repository root:

```sh
python3 validation/orthogonal-rank6-current-cli/check.py
python3 validation/orthogonal-rank6-current-cli/check.py --reconstruct target/orthogonal-rank6-restored
```

Both commands use only the standard library and declared saved parent capsules.
They restore byte aliases and call the unchanged independent audit with a byte
reader; no producer, Symbolica, mpmath, reference/evaluator executable, compiler
or PID probe runs. The optional reconstruction destination must be new/empty.
It contains saved evidence and historical snapshot aliases, not a hermetic native
build environment. `restore_files(manifest)` and `replay(files, manifest)` are
available to later preservation capsules.

The CLI records requested output precision and accuracy, with no per-component
precision tags or numeric before/after input witness. Working bits do not assert
achieved accuracy; signed-zero/input-mutation preservation is not qualified by
this record. Duals and threshold derivatives were not requested. No broad
threshold, complex-mass, generic-rank6, higher-N, physical or performance claim
is made. This frozen CLI predates later supplied-G/Legacy/Hybrid source changes
and does not qualify those later sources.

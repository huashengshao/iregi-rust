# Certified planar generalized scalar qualification

TIRust passes the independent numerical vertical slice for eleven rank-zero
five-propagator requests: the D6 unit scalar and each of the five individual
positive dots in D4 and D6. The defining parameter integral supplies the oracle;
it calls neither the reducer nor a scalar-master/reference executable.

The public certified-planar API uses its existing full-Taylor certificate and
constant-one denominator relation, then lowers to shifted masters with at most
four propagators. No genuine D6 pentagon leaf is evaluated. The fixed fixture is
`0,ex,ey,ez,ex+ey+ez`, squared masses `4,9,16,25,36`, and `mu=3`, with metric
`+---`. Its parameter denominator satisfies `F>=4` on the simplex. Symbolica
prepares the input jets, Symanzik expression, derivatives and Jacobian separately
from reduction. The numerical oracle reuses the existing Gauss-Legendre helper.

| Saved cohort | Exact decisions | Outcome |
|---|---:|---|
| Original grids12/16/20 | 2,040 passed;24 failed | Inconclusive quadrature convergence; retained |
| Refined grids24/28/32 | 2,064 passed;0 failed | Independently qualified for this slice |

The refined oracle differences are at most `1.065e-13` and `5.398e-16`, below
the fixed `1e-12` gate. Reducer/oracle agreement is at most `2.749e-18`, below
`1e-10`. Float128/256 agreement is at most `7.854e-32`, below `2^-80`.
Mass-jet derivatives agree with one-dot scalars to `2.943e-32`; the independent
centered-difference/Richardson check agrees to `5.906e-21`. These are dimensionally
normalized mixed absolute/relative errors. No threshold was relaxed.

Thirty Rust captures contain196 successful sample lanes,26 explicit invalid
lanes with null outputs, and880 successful complex Laurent/Taylor components.
All four native slots `[UV1,IR1,IR2,finite]` remain separate. Checks cover every
dot position, scale changes, common routing translations, repeated samples,
first-order mass jets, finite differences, precision metadata and before/after
input values. The independent audit reproduces every exact Fraction operand,
normalized squared error, threshold, label and decision. Eight negative controls
are retained for each cohort. An ordinary D4 unit integral is an additional
mass-derivative control.

Three earlier optional-import failures are preserved. Several installed mpmath
packages made the original optional selector ambiguous; root authorized an
explicit immutable Python3.13/mpmath1.3.0 import path. Those attempts evaluated
no quadrature. Their byte-identical directories were moved to a named failure
namespace before the explicitly authorized oracle-only continuation populated
the canonical slots. Original failed comparisons and relocation records remain
available. The subsequent finite grid refinement was separately authorized;
no Rust capture was repeated. Historical source-formatting and reviewer-only
failed assumptions are also retained without upgrading their old statuses.

The actual Cargo example build, its75-file selected source snapshot, all six
successful quadrature captures, all Rust arrays, both independent audits,
protocols, grants and logs are archived. The31 omitted executable paths are
hardlink aliases of one558,710,824-byte artifact; they are not31 independent
binaries. Compiler, native, system-library and external mpmath hashes are
historical attestations. The capsule does not freshly verify omitted files or
process absence. The literal Symbolica license and Python caches are excluded.

## Portable check and reconstruction

From the repository root, using only Python's standard library:

```sh
python3 validation/certified-planar-generalized-scalar-qualification/check.py
python3 validation/certified-planar-generalized-scalar-qualification/check.py --reconstruct target/planar-scalar-reconstructed
```

The checker verifies the exact archive/origin inventory, recorded small output
hashes and75 captured source files. It restores saved evidence into a temporary
directory and executes the unchanged independent audit scripts with only their
path globals redirected. No producer module, Symbolica, mpmath, compiler,
reference/evaluator executable or PID probe runs. It reproduces both2,064-decision
cohorts, including the original24 failed convergence decisions. Temporary replay
outputs are removed. `--reconstruct` additionally writes the254 archived aliases
and the75 selected source paths into a new empty tree. This is the selected
source/evidence context, not a hermetic native build closure.

For other preservation capsules, `restore_files(manifest)` returns an alias-to-
bytes dictionary, `replay(files)` repeats both independent audits, and
`reconstructed_files(files, origins)` adds the75 selected source paths. The
capsule is self-contained; no parent capsule or original `/shared` tree is needed.

This evidence qualifies one massive positive-F planar scalar family, Float128/
256 and the specified first-order mass jets. It does not qualify generalized
rank-seven tensors, arbitrary dots/shifts or endpoints, lower-span charts,
genuine full-rank D6 pentagons, signed zeros, all Dual orders, physical MadLoop
examples, rigorous quadrature enclosures or performance. Native timing numbers
are diagnostic wall times, not comparative benchmarks. Executor-observed launcher
stamps do not supply independent UTC process-overlap proof. The snapshot does
not claim to be a later mutable-main binary.

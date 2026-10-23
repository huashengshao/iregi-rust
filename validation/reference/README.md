# Original IREGI reference oracle

This is validation tooling, not part of the production Rust library. It builds
the supplied MadGraph IREGI and bundled OneLOop 3.4 into standalone Fortran
processes. QCDLoop/FF are also linked to satisfy the original module references;
the driver selects OneLOop for all evaluations. Original sources and their
licenses remain in `../references/madgraph/vendor/IREGI` and are never modified.

Run all commands from the `iregi-rust` repository root:

```sh
bash scripts/build-reference.sh
python3 validation/reference/capture.py --write-fixtures
```

The build script discovers `gfortran` and Python on PATH, with fallbacks for the
provided Nix environment. `FC` and `PYTHON` override discovery; `--fc PATH` and
`--jobs N` are also accepted. Build outputs stay in `target/reference`:

- `iregi-reference-original`: untouched source with the validation driver.
- `iregi-reference`: the same executable with only the generalized factorial
  table initialization repaired.
- `factorial-table-check`: exposes all entries of the repaired table for an
  independent integer-binomial check.
- `provenance.json`: compiler/version/options, MadGraph revision, individual
  original-source SHA-256 hashes, driver hash and exact repair-patch hash.
- `validation.json`: executed checks and the original failure transcript.

Both variants use `-O3 -fPIC -std=legacy -fallow-argument-mismatch`. The last two
flags permit the bundled legacy dependency sources to compile with modern
gfortran; they do not modify the source. Build subprocesses retain repository
root as their working directory.

## Persistent request protocol, version 1

Start an executable, wait for `READY IREGI_REFERENCE_V1`, then send requests:

```text
EVAL request_id tensor 2 2 2 0 3.0 0 1e-6
0 0 0 0 4 0 1
0 1 0 0 9 0 1
```

The header fields, in order, are:

```text
EVAL id api mode propagator_count rank dimension_shift mu snap threshold
```

Each following propagator row contains:

```text
p0 p1 p2 p3 mass_squared_real mass_squared_imag power
```

- `api=tensor` calls ordinary tensor reduction and requires powers one and
  dimension shift zero. Real and complex squared masses are supported.
- `api=general` calls generalized tensor reduction, requires a zero first shift
  and real masses, and accepts positive powers and even dimension shifts. Use
  the repaired executable; the untouched executable demonstrates the defect.
- `api=scalar` calls the lower-level scalar IBP recursion, accepts real/complex
  masses, powers and dimension shifts, and requires rank zero. `mode` is ignored
  for this API because the scalar recursion is the IBP entrypoint.
- Modes `0`, `1`, and `2` request IBP, PV, and hybrid PV-to-IBP respectively for
  ordinary tensor reduction. The original generalized API internally selects
  eligible PV coefficients for either nonzero mode; it does not provide all
  ordinary hybrid fallback semantics.
- Capacities are one through seven propagators, rank zero through seven, and
  input powers one through ten. These are reference capacities, not assertions
  that every possible combination is stable or implemented correctly.
- `mu` is positive and is the renormalization scale, not its square. `snap=0`
  preserves input scalar products; `snap=1` enables legacy on-shell repair.
  `threshold` controls the original snapping/mass-reference policy.
- IDs are short ASCII identifiers without whitespace, quotes or backslashes.
  Fortran list-directed input also accepts `D`-format floating point exponents.

Every completed request emits one line prefixed by `RESULT ` followed by JSON:

```json
{"id":"request_id","stable":true,"poles":["uv1","ir1","ir2","finite"],"moments":[[[0,0],[0,0],[0,0],[0,0]]]}
```

The numbers above illustrate the shape only. Every moment has four complex
numbers, each encoded `[real, imaginary]`. Ignore untagged lines: original
OneLOop writes a startup banner, and IREGI may write warnings. Flushes after
READY and each RESULT support an interactive long-lived process. Requests may
also be supplied back-to-back as a batch. Each request gets fresh numerical
caches; topology/rank initialization remains warm. EOF or `QUIT` ends the
process. Empty lines and header comments beginning `#` are ignored.

A malformed request or original Fortran `STOP` ends the process. **A zero exit
code is insufficient to establish success:** require one valid RESULT with the
matching ID for every submitted request. A `stable=false` result can contain
partial coefficients and must be rejected as a numerical answer. Nonfinite
output produces `stable=false`, `error="nonfinite_reference_output"`, and
`moments=null`; it must likewise be rejected by the caller.

## Mathematical contract

Denominators follow `(q+p_i)^2 - m_i^2 + i0`, with real shifts ordered
`(time,x,y,z)` and metric `(+---)`. Numerators use four-dimensional Cartesian
components. Integration is dimensionally regulated; `dimension_shift` adds to
`4-2*epsilon`. The driver returns native IREGI Laurent normalization, including
separate UV and IR single poles. It sets `ML5_CONVENTION=true` solely to select
**unweighted Cartesian monomial moments**; it does not call the IMLOOP Laurent
normalization adapter or apply its rank sign.

There are `binomial(rank+4,4)` moments. Rank blocks increase from zero. Within a
rank block, the exponent of `q0` descends, then the exponent of `q1` descends,
then the exponent of `q2` descends; the `q3` exponent is the remainder. Rank two
therefore has `00,01,02,03,11,12,13,22,23,33`. A prepared polynomial coefficient
array in this order contracts directly with the returned moments.

The raw scaleless bubble has UV pole `+i*pi^2` and IR single pole `-i*pi^2`.
Their sum vanishes, but the separate values matter for generalized recurrences.
Do not discard them when comparing native outputs.

## Confirmed defect and narrow repair

At MadGraph revision `6c1b4684b46ad26c4f0ebc57eb9963649f350142`, every first call
to `general_ti_reduce` initializes a table of
`factorial(i+j-1)/(factorial(i-1)*factorial(j))` for `i<=10`, `j<=7`. The helper
supports factorials only through 12, so this reaches a Fortran STOP before
evaluating even a rank-zero tadpole. The captured stdout contains:

```text
ERROR: i > 12, please take long type (KIND=LINT) integer
```

The original process exits with status zero and produces no RESULT. The repair
in `factorial_pair.patch` replaces only the factorial quotient by the equivalent
recurrence `table(i,j)=table(i,j-1)*(i+j-1)/j`. No reduction algorithm, threshold,
scalar master, or ordinary tensor path is changed. The builder verifies that
its source edit exactly matches the committed patch before compiling.

`capture.py` verifies all 80 entries against Python's exact integer binomial
coefficient, compares 24 ordinary fixtures against the untouched executable
with exact equality, checks generalized unit-power results against the ordinary
API, and exercises independent analytic A0 normalization, A0 mass derivatives,
the tadpole identity `I(D+2,nu+1)=-pi/nu*I(D,nu)`, and B0 mass derivatives by
central finite differences. These checks do not assert correctness of every
generalized-domain combination.

`fixtures.json` records 31 independent reference cases: scalar A0/B0/C0/D0,
bubble/triangle ranks one through three in every mode, a scaleless bubble, a
complex-mass triangle, and generalized powers/dimension shifts. Each fixture
states whether the repaired executable was used. Run `capture.py` without
`--write-fixtures` to repeat validation without changing committed expected
values. Fixture preparation and process transport are not reduction benchmarks.

## Additional original-reference disagreement

`python3 validation/reference/audit.py` reproduces a distinct rank-four bubble
problem in the untouched source. With squared masses 4 and 9, shifts zero and
`(0,1,0,0)`, and scale 3, the finite `q1^4` moment is
`45.43163000150602 i` in IBP mode but approximately `46.11123944517427 i` in PV
and hybrid mode; all three return `stable=true`. The UV poles agree. The
quadratic-root expressions in the two real-mass bubble analytic branches appear
to divide only the square-root term by `2*P02`, rather than the complete
numerator. This is a suspected cause, separate from the reproduced disagreement.

The captured inputs and outputs are in `known-issues.json` (regenerate with
`audit.py --write`). No repair for this second issue is applied by the builder.
PV/hybrid results in this domain require additional independent evidence before
being accepted as oracle truth.

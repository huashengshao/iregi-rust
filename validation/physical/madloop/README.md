# Graph-isolated MadLoop reference

From the repository root:

```sh
source scripts/env.sh
python3 validation/physical/madloop/run.py
python3 validation/physical/madloop/run.py --case gghh
python3 validation/physical/madloop/run.py --case gghhh
python3 validation/physical/madloop/run.py --case gggg-up
```

The optional Python/Fortran harness creates an isolated reflink copy of the
supplied MadGraph checkout under `target/physical/madgraph`. It generates
`g g > h [sqrvirt=QCD]` with the filter `n==3 and 6 in loop_pdgs`, explicitly
disables loop grouping, builds a standalone executable, and selects only IREGI
at runtime. MadGraph requires its bundled CutTools library at export/link time.
No production Rust path depends on either reference library.

| Case | Selected loops | Separate graphs | Rank | Center-of-mass energy | FeynKit group |
| --- | --- | ---: | ---: | ---: | ---: |
| `ggh` | Top triangles | 2 | 3 | 125 GeV | 1 |
| `gghh` | Top boxes | 6 | 4 | 600 GeV | 2 |
| `gghhh` | Top pentagons | 24 | 5 | 750 GeV | 5 |
| `gggg-up` | Massless up-quark boxes | 6 | 4 | 400 GeV | 2 |

All cases use `[sqrvirt=QCD]` to retain individual complex loop amplitudes before
any Born interference. The complete graph map records each generated diagram,
coefficient group, amplitude slot, symmetry factor, multiplier, vertex routines,
and external vertex order. It follows generated wavefunction parent indices;
shared intermediate wavefunctions do not merge the final graphs. The selected
FeynKit graph has ascending external order and the `L1_2` fermion orientation.

For two outgoing particles the scattering angle has cosine `3/5`. The three
outgoing Higgs bosons have energy 250 GeV each, with equal spatial momentum
magnitudes and azimuths separated by 120 degrees. These describe the requested
driver point. MadLoop's `ImprovePSPoint=2` can adjust that point before HELAS;
the JSON records both the request and the point actually evaluated. Every generated reference graph in this table was
successfully exported with IREGI reporting stability; independent Rust/FeynKit
agreement is a separate validation gate.

Schema version 2 adds `metadata.evaluated_external_momenta`: arrays of four
decimal strings per external leg in physical incoming/outgoing convention.
Use this field for independent numerator bindings and routing comparisons.
`metadata.external_momenta` retains the requested driver inputs. The independent
`metadata.coefficient_construction_momenta` captures the coefficient routine's
`P` argument and is checked against the evaluated momenta. Raw complex HELAS
momenta appear in `metadata.wavefunction_momenta`, keyed as `leg_component`
with one-based leg indices and zero-based components; their sign is negative
for incoming legs and positive for outgoing legs.

The distinction matters for the pentagon: MadLoop changes the first beam energy
from 375 to approximately 375.000004659088 GeV. Binding the requested point to
the numerator but using the adjusted denominator shifts causes a spurious
pointwise mismatch. The selected graph's affine relation `x=p1-q` uses the
evaluated `p1`. All exported `PDEN` shifts already come from the reduction seam.

To reuse generated sources, run `--stage export`; `--helicity 1` through `4`
selects `(--0)`, `(-+0)`, `(+-0)`, or `(++0)`. The momenta are the on-shell
125 GeV Higgs decay configuration crossed to two incoming gluons. Model values,
couplings, actual HELAS polarization components, source revision, and source
hashes are included in the JSON result. Values are serialized as decimal strings
to retain the reference binary64 output exactly.
For additional Higgs bosons append their scalar zero helicities; the four-gluon
case has 16 helicity configurations, whose actual signs are recorded in JSON.
Generation replaces only that case's generated directory under
`target/physical`. Logs are kept under `target/physical/logs/<case>`.

The exported data comes from `TIR_interface.f` after the tensor/numerator
contraction and before the normalization and counterterm/process accumulation.
Each record contains all 35 polynomial coefficients through rank three and all
105 converted tensor Laurent entries, propagator shifts and squared masses,
scale, stability flag, raw contraction, normalized amplitude, and a complex
numerator probe evaluated by MadLoop's own `EVAL_POLY` routine. The process-level
squared answer is never used. The generated double- and quadruple-precision R2
calls and UV counterterm amplitudes are explicitly zeroed.
Bare poles and reduction-generated R1 remain included.

Boxes export 70 coefficients and pentagons export 126, with three tensor Laurent
entries for every coefficient. Both precision variants zero the complete
`AMPL(:,1:NCTAMPS)` range while retaining the external wavefunctions needed by
the loop numerator.

| Fixture orientation | MadLoop diagram | Coefficient group | Amplitude slot | Fixed equal-gluon-color factor |
| --- | ---: | ---: | ---: | ---: |
| `a→b→c→a`, the supplied FeynKit triangle | 1 | 1 | 2 | −1/2 |
| Reversed fermion orientation | 2 | 2 | 3 | −1/2 |

Each graph has multiplier and symmetry factor one. `LOOPCOEFS` excludes both the
closed-fermion sign and color trace. `ML5_0_LoopColorFlowCoefs.dat` supplies −1
for each loop amplitude in the `Tr(1,2)` color basis. Fixed equal adjoint colors
give `Tr(TᵃTᵃ)=1/2`; the color-summed metric is 2 and must not be substituted for
this fixed-color factor. An individual oriented graph receives no additional
factor of two.
The four-gluon box instead has a four-generator trace. Its full MadLoop
color-flow data is included in the JSON; the two-gluon `-1/2` factor must not be
reused for that case. For adjoint components `(0,0,0,0)`, the exact Spenso SU(3)
tensor contraction confirms `Tr(T0^4)=1/8`, so the combined fixed-color and
closed-fermion factor is `-1/8`.

`PDEN=[0,p1,p1+p2]` defines denominators `(Q+PDEN)^2-m^2`, while the exported
numerator polynomial is in `x=-Q`. Feed positive `PDEN` to the Rust reduction
with `Convention::MadLoop`: the convention already includes the odd-rank sign
used by the reference `IMLOOP`. `CONVERT_IREGI_COEFFS` only reorders components.
Equivalently, use negative shifts with `Convention::OneLoop`; do not combine
negative shifts with the MadLoop sign conversion.

The FeynKit fixture places its loop momentum `q` on `a→b`. Its comparison is
therefore `N_FK(q) = -1/2 P_ML,1(p1-q)` after matching couplings and external
polarizations. The JSON `probe_momentum` is an argument of `P_ML`, not `Q` or
the FeynKit routing. The MadLoop coefficient-index metadata comes directly from
its `Polynomial.get_coef_at_position` API.

Laurent slots are `[finite, single pole, double pole]`. The normalized amplitude
equals the raw contraction divided by `16*pi^2`; the fixed-color factor remains
external to both arrays. The stored fixture establishes a successful reference
export, not a completed independent FeynKit/Rust comparison. That comparison
must report its own measured discrepancy before being counted as validated.

The instrumentation preserves a `.iregi-original` copy of each modified
generated source. It fails on changed source anchors, topology, or incomplete
exports so an upstream change cannot silently alter the reference contract.


## Internal graph timings

After generating a case and building the original reference objects:

```sh
python3 validation/reference/build.py
python3 validation/physical/madloop/benchmark.py --case ggh --cpu 0
python3 validation/physical/madloop/benchmark.py --case gghh --cpu 0
python3 validation/physical/madloop/benchmark.py --case gghhh --cpu 0
python3 validation/physical/madloop/benchmark.py --case gggg-up --cpu 0
```

Choose a permitted, otherwise idle CPU, shared with the Rust comparison. These
commands write `target/physical/<case>-benchmark.json`; they do not overwrite
committed correctness fixtures. They rebuild generated HELAS and process code
with `-O3`, and link an archive of the original `-O3` objects from
`target/reference/objects`. The archive uses untouched `funlib.o`; the
generalized-interface factorial repair is unnecessary for these unit-power
physical graphs. Source/library hashes and reference build provenance are
recorded alongside compiler flags, CPU affinity, CPU model, frequency/governor
when available, and timestamps.
Each attempt is retained under `target/physical/benchmarks/<case>/`, and the
latest path records running, failed, or measured status. A failed build or run
replaces the latest status with its error rather than exposing an older success.
The exact executable, linked libraries, model card, reduction card, and harness
sources are hashed.

The timer uses Fortran `SYSTEM_CLOCK` with 64-bit counters, calibrated blocks of
at least 30 ms, five warm-up blocks, and 21 measured blocks, separately for batch
widths 1 and 32. Each batch repeats identical physical inputs. Original IREGI
reuses numerical intermediates inside each sample; `IREGI_FREE_PS` clears them
after each sample, inside the timer. No generation, compilation, printing, or
subprocess transport is timed. Runs without `--cpu` are explicitly unqualified.
Raw samples are in nanoseconds per batch, with block iteration counts retained.
These physical references retain MadLoop's legacy on-shell snapping at its
`1e-6` threshold; the JSON records that policy. Match it explicitly when comparing
Rust at identical reduction inputs. Separate runs of the reference and Rust
require independent-sample uncertainty estimates, not paired resampling.
MadLoop's earlier phase-space adjustment is separate from IREGI snapping and is
also outside the timer; all timed graphs use `evaluated_external_momenta`.

| Stage | Measured work |
| --- | --- |
| `numerator` | Original MadLoop `EVAL_POLY` at the recorded complex probe |
| `numerator_assembly` | Original HELAS vertex, wavefunction update, and merge calls for the selected oriented graph |
| `reduction` | IREGI `IMLOOP`, tensor/Laurent ordering conversion, numerator contraction, and numerical cache cleanup |
| `total` | Graph numerator assembly followed by reduction |
| `preparation`, `masters` | Unmeasured separately; serialized as `null` |

External HELAS wavefunctions are prepared once and excluded from every stage.
Feynman-rule generation and symbolic numerator preparation are also excluded.
Scalar masters are included in reduction; the separate master field is not an
estimate. Polynomial probing is a separate diagnostic workload and is not added
to the physical total, which contracts the prepared coefficient array directly.

The harness follows parent wavefunction indices to replay only the selected
graph's dependency chain, copying existing generated calls without symbolic
manipulation. Before timing it checks every replayed numerator coefficient,
every tensor Laurent coefficient, and the contracted result against the ordinary
MadLoop path. When a matching committed fixture exists, it also checks the
optimized build against that capture. This establishes the reference workload;
Rust agreement and performance parity remain separate qualification gates.

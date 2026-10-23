The physical fixtures are individual oriented quark loops, not summed
process amplitudes:

- `examples/graphs/ggh_top_triangle.dot` uses two `V_137` gluon vertices and one
  `V_141` Higgs vertex from the pinned SM model.
- `examples/graphs/gghh_top_box.dot` uses two vertices of each kind.
- `examples/graphs/gghhh_top_pentagon.dot` uses two `V_137` and three `V_141`
  vertices.
- `examples/graphs/gggg_up_box.dot` uses four `V_135` up-quark/gluon vertices.

These DOT graphs include the closed fermion-loop factor `-1`; no additional
automorphism factor is applied. `iregi-prepare` applies the model's vertex and
propagator numerators, contracts tensors through the exact Spenso HEP library,
and extracts coefficients of `iregi::q0` through `iregi::q3` using Symbolica.
External spin wavefunctions may remain symbolic. Residual color or Lorentz
indices require an explicit component selection in declared logical axis order.

Physical comparison must first establish the graph correspondence, external
ordering, coupling values and loop routing against generated MadLoop output.
Compare the numerator pointwise after the routing change before comparing
integrated Laurent coefficients. Record each selected graph and helicity; a
process total alone cannot validate an individual graph.

Use the generated MadLoop `TIR_interface.f` reduction seam: export loop
coefficients, masses and momenta before contraction, then export the complex
loop result before counterterm and process summation. MadLoop's TIR interface
applies `1/(16*pi^2)` after contracting tensor and numerator coefficients; its
interference mode additionally takes `2 Re`. Disable denominator grouping or
record its explicit graph map. Exclude R2 and UV counterterms, retain the bare
Laurent poles and R1, and keep physical numerator algebra four-dimensional.

Use the momenta at MadLoop's numerator seam. MadLoop may adjust the requested
external point before constructing its wavefunctions; the five-point fixture
exposes a change at approximately `1e-6`. Keep both the requested and evaluated
momenta in the capture, and bind the latter in FeynKit, including the momentum
used in the affine loop-variable change.

The captures in `madloop/fixtures/` retain the MadGraph revision, generated-file
hashes, complex numerator coefficients, HELAS external wavefunctions, evaluated
momenta, an independently evaluated complex probe, and the graph map.
`ggh-numerator-reference.json` is a compact copy of the selected triangle record.
For these oriented graphs the MadLoop polynomial variable is `x = p1 - q`,
where FeynKit's `q` labels the `a -> b` edge and `p1` is the evaluated first beam.

| DOT graph | Selected MadLoop group | Fixed color factor | Prepared degree |
| --- | ---: | ---: | ---: |
| `ggh_top_triangle` | 1 | `-1/2` | 2 |
| `gghh_top_box` | 2 | `-1/2` | 4 |
| `gghhh_top_pentagon` | 5 | `-1/2` | 4 |
| `gggg_up_box` | 2 | `-1/8` | 4 |

The factors include the closed fermion-loop sign and the fixed adjoint-color
trace; a separate exact Spenso test checks `Tr(T0^2)=1/2` and `Tr(T0^4)=1/8`.
The up-quark comparison sets the full SM snapshot's `UFO::MU` parameter to zero,
matching MadLoop's massless restriction. The pentagon capture allocates degree
five, while its Dirac trace leaves a polynomial of degree four.

The preparation integration tests compare each graph at three independent
real or complex loop momenta before invoking scalar masters or tensor
reduction. They use 128-bit Symbolica evaluation of the exact prepared
expression and compare to the independently captured binary64 HELAS numerator.
All four graph comparisons, thirteen general preparation tests and four
exact-number model-boundary regression tests passed;
`numerator-evidence.json` records the checks and source hashes. These test
durations are validation observations, not throughput benchmarks.
To regenerate the CLI inputs from those checked routing and wavefunction
bindings, run:

```sh
IREGI_PHYSICAL_INPUT_DIR=validation/physical scripts/cargo.sh test \
  -p iregi-prepare --offline --test madloop_numerator
```

The resulting `*-cli-input.json` files use canonical `(q+p_i)` denominators in
the prepared graph's edge order. Integrated comparisons must additionally
check all Laurent coefficients and the selected reduction convention; a
numerator test alone does not establish the integrated result.

`compare_cli.py` performs the integrated check for any of the four fixtures:

```sh
source scripts/env.sh
python3 validation/physical/compare_cli.py --case gghh --algorithm hybrid
python3 validation/physical/compare_cli.py --case gghhh --algorithm ibp
python3 validation/physical/compare_cli.py --case gggg-up --algorithm pv
```

Each invocation prepares the physical numerator through the Rust CLI, reduces
it, and compares its finite, single-pole and double-pole contraction to the
selected MadLoop graph. All tensor coefficients are also checked against
original IREGI reevaluated at the canonical FeynKit shifts. MadLoop's captured
tensors use the different variable `x`; they are not compared directly. The
default checks all three original IREGI modes independently. Repeat
`--reference-mode 0`, `1` or `2` to select particular modes. The report preserves
disagreement and failed modes, with overall success requiring every requested
tensor comparison and the physical contraction to pass. In particular, a PV
failure is retained while an independent IBP result is checked.

Reports and accompanying CLI/oracle outputs are written under
`target/physical/`. `--output` selects another report path. A failed process,
timeout, unstable reference or numerical mismatch is retained as a failed
report rather than discarded. `--cli-result PATH` rechecks saved CLI JSON
without starting a new Rust process and explicitly records that the producing
binary's identity was not inferred. Source and input hashes accompany every
report. Comparison arithmetic and independent captures are binary64 even when
the Rust invocation selects `--precision dd` or `--precision float`.

The numerical comparison first removes mass dimension using
`Q = max(mu, abs(shift components), sqrt(abs(mass_squared)))`. It then uses
`abs(actual/Q^d - expected/Q^d) / max(1, abs(expected/Q^d))`, with tensor
dimension `d = 4 + rank - 2*N` and graph dimension `4 - external boson count`.
This matters for the negative dimensions of high-point integrals. The report
keeps both raw graph contractions and the values after MadLoop's final
`1/(16*pi^2)` normalization. Color and fermion factors are already included in
the FeynKit numerator and are applied only to the stripped MadLoop reference.

Run `python3 validation/physical/audit_reference.py` to compare original IREGI's
three modes at these canonical points without executing Rust. The retained
`canonical-reference-audit.json` records agreement for the triangle and both
boxes, but a disagreement in five finite rank-four coefficients of the
pentagon. Every reference mode reports this point stable; PV and hybrid agree
with each other, while IBP differs. The maximum dimensionless difference is
approximately `0.6001`. This observation alone does not determine which mode
is correct. The audit exits nonzero on disagreement and saves the raw reference
outputs, so the discrepancy remains visible during independent checks.

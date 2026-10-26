# Current CLI and retained physical graph integration

The current standalone CLI passes all fourteen listed tests. Four complete
physical recomputations also pass their independent original-IREGI tensor and
MadLoop graph comparisons: one top-loop `gg→HH` box at Float128/256 and one
`gg→HHH` pentagon at Float256/384. Both numerators have rank four, with seventy
Cartesian moments and all four Laurent slots retained per moment. These are
physical spot checks; they do not establish rank-six physical coverage.

The CLI executable is the exact `098f3879…` product and its test executable is
`e8ef4f78…`, both inherited from
[wheel003](../python-interface/facade-wheel-003/README.md). Their build source
context is `e873a0bec5cdb087caa812c6f2b1c668323f3670daed8438d3f538686da0c29c`.
This capsule adds twenty saved input/helper/controller files, including the
pinned model, DOT graphs, physical inputs and captured MadLoop fixtures. It
inherits the parent's 147 selected build sources; it does not claim a complete
compiler, dependency or system closure. Executables and credentials are omitted.

| Graph | Working bits | Original IREGI modes | Full tensor checks | Largest tensor error | Largest MadLoop error |
|---|---:|---|---:|---:|---:|
| Box, N4/R4 | 128, 256 | IBP, PV, Hybrid | 1,680 | 1.144×10⁻¹³ | 4.766×10⁻¹⁵ |
| Pentagon, N5/R4 | 256, 384 | PV, Hybrid | 1,120 | 4.616×10⁻¹⁴ | 9.291×10⁻¹⁴ |

The external comparison gate remains `1e-10` with dimensional normalization.
Comparison arithmetic and the external reference values are binary64. The
current CLI requests Hybrid and selects PV in these successful cases. MadLoop
uses isolated graph groups two and five, equal fixed gluon colors, the retained
helicity-one inputs, and the documented graph factor `-1/2`. Its three merged
Laurent coefficients are compared after combining the UV and IR single poles;
the complete original-IREGI tensor checks retain their separate Laurent slots.
Bare UV/IR poles and reduction R1 are included; R2 and UV counterterms are
excluded. Existing numerator/routing correspondence is reused, rather than
claiming a new unintegrated MadLoop numerator export in this spot cohort.

An additional saved-only comparison uses exact `Fraction` arithmetic on decimal
strings for every tensor and contracted Laurent slot. The box128/256 and
pentagon256/384 pairs each pass 280 tensor plus four contracted complex checks,
for **568 pair checks** at `2^-80`. It uses
`Q=max(mu, abs(Cartesian shift components))`, verifies the squared-mass complex
L1 norm is at most `Q²`, and tests

```
abs(delta.real) + abs(delta.imag)
  <= 2^-80 * max(Q^dimension, abs(higher.real), abs(higher.imag)).
```

Tensor dimension is `4 + rank - 2N`; contracted dimensions are zero for the box
and minus one for the pentagon. Here `Q` is 600 and 750. The largest normalized
L1 differences are `7.951531766e-36` and `6.144962810e-55`. This establishes
agreement of two independently recomputed, represented-input evaluations; it is
not a certified bound on eighty achieved accuracy bits. The older binary64
precision-pair reports remain separately preserved.

The first physical controller remains **failed**: pentagon Float128 was rejected
by its conservative cancellation estimate at `pv_node_852`, with working
precision128 and requested accuracy53. It returned no tensor array or integral;
no subsequent original-IREGI or MadLoop comparison ran for that failed lane.
The controller's planned pentagon256 and128/256 pair stages did not run.
Prospective256 and384 recomputations then passed in independent receipts, with
the requested accuracy unchanged. No128-bit failure is promoted to success.
Pentagon original-IREGI IBP was not requested here; its historical disagreement
remains in the earlier physical qualification.

Run the saved replay from any directory:

```bash
python3 -I -S -B validation/current-cli-physical-integration/check.py
```

The checker validates inherited source/product identities, hashes, fourteen
actual CLI test results, saved process cleanup, full original-IREGI arrays,
captured MadLoop graph results, exact precision agreement and failed/unrun
statuses. It reuses only definitions extracted from the pinned comparison
helper; it never invokes that helper's `main`, `evaluate`, subprocesses, a native
host, a compiler or an integral. No new timing measurement is supplied.

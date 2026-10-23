# Public six/seven-point rank-seven qualification

`highpoint_public` exercises `ReductionPlan::new`, `Workspace<Float>::new`, and
`Workspace::reduce_batch` with ordinary coordinate inputs. It does not specialize
symbolic coefficients to a sample or substitute original Fortran scalar masters.
The rank-seven output has 330 Cartesian moments, with all four native IREGI
Laurent coefficients retained as exact rationals representing the returned
floating-point values. Failed lanes have no exposed scratch values.

This evidence addresses the gap left by `validation/pv-high-rank/`: its previous
six-point 128/256-bit full-array result used numerically specialized coefficients,
and its seven-point preparation reached a 90-second limit. Those records remain
unchanged and do not qualify this public interface.

The conditioned family has shifts
`0, (0,1,0,0), (0,0,1,0), (0,0,0,1), (1/2,0,0,0), (0,1,1,0), (0,0,1,1)`
and squared masses `1,2,3,4,2,3,4`, with `mu=3`. Samples include the base point,
an exact uniform scale factor two, and an increase of the first squared mass by
one. The external coordinates span four dimensions. All inputs are exactly
represented dyadics. The original binary64 IBP and hybrid implementations report
stability for these samples; their zero-pole residuals pass the unchanged
dimensionally normalized `1e-10` gate. Original PV reports instability. None of
these observations alone establishes finite-coefficient agreement.

The wider squared-mass choice `9,11,13,17,19,23,29` remains in `fixture.json` and
`reference.json`. Despite reporting stability, original IBP has 85 failing
six-point and 257 failing seven-point base UV coefficients. Two additional
explorations are retained under `halfstep_masses` and `offset_masses`; their pole
failures are visible. This is a conditioning investigation, with no threshold
change and no claim that one structured family covers general high-point inputs.
At every requested rank, `rank+4-2N<0`; the positive Feynman-polynomial lower
bounds recorded by the capture independently exclude both ultraviolet and
infrared poles. Each reference capture retains the original request, response,
binary hash, stability flag, and every pole failure.

The public probe writes a ledger before plan preparation, workspace preparation,
and reduction, so a bounded interruption identifies the unfinished stage.
Working precision and requested accuracy are recorded separately: using 128 or
256 working bits with a 53-bit requested target is a precision-recovery test,
not a claim of 128- or 256-bit delivered accuracy. Diagnostic elapsed times are
not performance gates.

Build and reference reproduction, from the project directory:

```sh
source scripts/env.sh
python3 validation/public-highpoint/capture_reference.py --family conditioned_masses
python3 validation/public-highpoint/capture_reference.py --family halfstep_masses --base-ibp-only
python3 validation/public-highpoint/capture_reference.py --family offset_masses --base-ibp-only
cargo build -p iregi-rust --example highpoint_public --locked --offline
```

The isolated development build uses `build_probe.py` and the immutable archives
identified by the ordinary-stack-adoption build manifest. It guards all linked
and shared dependency files before and after compilation, and records the exact
historical core sources; later edits are not silently included in qualification.
`run_probe.py` uses that recorded binary and a new evidence name for each bounded
run. Acquire the shared Symbolica runtime lease before any numerical probe.

```sh
python3 validation/public-highpoint/build_probe.py
python3 validation/public-highpoint/run_probe.py n6-rank7-pv-128-53 6 --limit 180
```

Public numerical qualification is pending until successful complete arrays,
independent comparison, and higher-precision convergence have been recorded.

The first public six-point rank-seven PV run (`n6-rank7-pv-128-53`) reached its
180-second limit during `Workspace::new`. Its structural plan completed in
107.836 seconds, with 330 moments, 31,670 aliases, and 56 scalar-master leaves.
Numerical reduction never started. The timeout, last-stage ledger, complete
preparation log, and unchanged source/input/binary hashes are retained. This
baseline uses the default stack allocator but predates the later scalar
solve-vector optimization and generalized-PV integration. It establishes no
public numerical agreement or performance result.

`simplex-summary.json` adds three independent finite witnesses using SciPy
Gauss–Jacobi rules, increasing orders 8/12/16/20, and two simplex mappings.
The native finite imaginary values are approximately `0.008265462463864115`
for the six-point scalar, `-0.0185617665062893` for six-point `qx*qz^6`, and
`-0.0012422321746125768` for the seven-point scalar. Estimated dimensionally
normalized uncertainties are respectively `1.40e-13`, `5.28e-16`, and
`6.87e-13`. These are convergence estimates, not certified intervals. The
original complex outputs agree at `1e-10`, although the rank-seven witness is
close to that limit (`9.35e-11` including its spurious real component).
This does not establish agreement for the other tensor coefficients.

The scalar integrands use the standard Feynman-parameter formula. The six-point
rank-seven integrand is reused unchanged from the existing independent oracle
in `validation/pv-high-rank/sixpoint_simplex_oracle.py`; the numerical script
does not implement polynomial manipulation or a reduction algorithm.
Reproduce each retained configuration separately, preserving old output files:

```sh
python3 validation/public-highpoint/simplex_oracle.py 6 --order 20 --mapping 0
python3 validation/public-highpoint/simplex_oracle.py 7 --order 20 --mapping 1
python3 validation/public-highpoint/summarize_simplex.py
```

After two successful public runs, `compare_public.py low.json high.json out.json`
validates exact input identity, all 330 basis entries and Laurent-array shapes,
then compares all complex coefficients with original IBP and between working
precisions. Its gates remain `1e-10` for the original comparison and `2^-80` for
dimensionally normalized mixed convergence. Incomplete or rejected outputs fail
closed. The independent simplex witnesses remain separately identified.

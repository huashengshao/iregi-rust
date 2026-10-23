# Isolated native scalar stack-allocation candidate

This experiment regenerates the existing six-output ordinary scalar roots using Symbolica's `optimize_stack` through the already-adopted `exact_scalar_master_evaluator`. It does not implement algebra, alter Dualizer, change native arithmetic, or modify production files.

C0/D0 paired modules are retained exports from the independently qualified production-factory experiment; A0/B0/dB0 were exported from its frozen factory binary using the same qualification path. Their baseline module text exactly matches the current production native kernel after expanding constant-table indices to their exact `ConstantSpec` text. `baseline-source-equivalence.json` records this check; no arithmetic normalization is used.

All five scalar emitted portions are byte-identical between baseline and candidate. For batch source, the ordered operand/control/constant/helper-call shape matches after expanding transparent outlining wrappers and ignoring only storage addresses/capacity. This is a supplementary source check, not a proof of correct addresses. C0/D0 source-length outlining boundaries can shift when slot indices become shorter; compiled layout need not be identical.

The arena totals, including unchanged shared helper argument/result storage, are:

| Family | Baseline slots | Candidate slots |
|---|---:|---:|
| A0 | 46 | 14 |
| B0 | 513 | 23 |
| dB0 | 1961 | 34 |
| C0 | 1431 | 1219 |
| D0 | 29772 | 4787 |

Root-only temporary counts are C0 220 to 8 and D0 25010 to 25. Slot reduction alone does not establish performance improvement.

`prepare.py` copies and hashes the frozen default-stack-allocator production archives and retained paired exports. `build.py FAMILY` builds old/new kernels into one binary at the same optimization level, and saves source, archive and binary hashes. Build CPUs are 20 and 21; no numerical runtime starts during a build. The upstream dependencies were built with the workspace dev dependency optimization level 2; the new generated generic kernels use optimization level 3 and 16 codegen units. This is a matched storage experiment, not the final release benchmark.

`run.py FAMILY` checks the binary hash, saves stdout/stderr, retains earlier attempts, and records failures and timeouts. With the user-provided licensed environment loaded after `scripts/env.sh`, correctness runs use root-assigned CPUs12/13 and record only license-environment presence. No key or license value is saved. Timing still requires a quiet window granted by the root agent and CPU0 pinning. `--export` invokes the qualified factory probe for missing families. `--benchmark` runs paired 21-block 30ms native-only measurements after fresh workspace initialization, warmup and old/new result comparison.

Strict old/new qualification checks all six output components, exact represented values, tracked precision and signed zeros for f64, DoubleFloat and Float256. Empty/singleton, odd rows, tails, reordered/branch-mixed rows, retained stride, scale changes and scaleless/massless cases are included. The ordinary output layout is `[finite,total_single,IR_double,UV_single,IR_single,derivative_boundary]`. The final input is squared renormalization scale. Higher precision inputs are created from exact represented binary64 rationals, not through a new binary64 conversion.

The independent Symbolica interpreter is evaluated on the same rows. Any native/interpreter represented-value, precision or signed-zero differences are recorded separately and must be examined. Existing native primitives (especially DoubleFloat's commutative compensated product) can differ from Symbolica primitive arithmetic, so exact old/new storage parity cannot by itself establish exact cross-backend parity. Nonfinite interpreter controls fail the updated harness. The final C0 probe includes this validity guard. An initially added fully-scaleless raw dB0 case produced matching infinity in both native variants; that failed finite-parity run remains retained. This point is outside the public API domain, which explicitly reports `UndefinedScalelessDerivative`. The updated dB0 probe checks that public rejection and raw nonfinite classification separately, then evaluates the supported corpus; the unsupported point remains visible and has no kernel timing score.

`analyze.py` reuses the project's benchmark bootstrap-median confidence and gate function. It reports candidate/baseline ratios per family, batch1/batch32, and branch ordering. Noisy rows remain inconclusive. Timed native kernels are the same compiled paired kernels as qualification; preparation and subprocess transport are excluded. This experiment is neither an IREGI kernel timing comparison nor public reduction end-to-end qualification.


## Timing protocol correction (prepared, not yet executed)

The original per-call-clock protocol remains in `timing-summary.json`: all 24 rows are retained, with two measured regressions and 22 rows too noisy for the 2% confidence-width gate. Blanket native-kernel adoption is rejected. Those results are not overwritten or silently replaced.

`probe-fixed.rs` corrects a measurement-design issue: the original loop queried `Instant` after every kernel call. The new loop calibrates each variant with excluded fixed-loop pilots lasting at least 2ms, then chooses one shared iteration count targeting the mean 30ms block cost. Each of 21 alternating measured blocks performs that fixed count, protects input/output with `black_box` on every call, and reads elapsed time once after the loop. It subtracts no estimated overhead.

`build_fixed.py FAMILY` prepares separate f64-only paired binaries using the same generated modules, frozen runtime archives, opt3 and 16 codegen units. The original all-domain binaries and their qualifications remain separate; f64-only monomorphization may change compiled layout. `run_fixed.py FAMILY --phase before`, then `--benchmark`, then `--phase after` records all 24 f64 configurations before and after timing, with binary hashes and timestamps. Correctness uses assigned CPUs12/13 and timing requires root-granted CPU0 quiet access. `analyze_fixed.py` rejects mismatched binary hashes, incomplete matrices, changing iteration counts, missing or reversed qualification/timing order, and invalid parser fixtures. Root released the quiet window and the original D0 build resumed first. Corrected f64-only builds and correctness are allowed on CPUs20/21; corrected timing still awaits a fresh quiet-window grant. Strict represented-value, precision and signed-zero checks also follow warmup, pilots and every completed measured pair, outside the timed blocks.

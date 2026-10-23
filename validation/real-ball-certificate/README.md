# Private RealBall certificate experiment

The isolated candidate passes four baseline/candidate comparisons and eight inherited certificate tests. It has not been applied to the library. The exact source, raw logs, build commands, dependency hashes and separate timing samples are retained here; binaries and dependency archives remain under `target`.

The candidate uses Symbolica's existing `RealBall` batch evaluator only when the entire exact polynomial instruction program has real coefficients and no hidden function calls, and every input component of a lane, including all Taylor components, is real. Other lanes use the existing `ComplexBall` arithmetic. Both groups execute by instruction across lanes, then restore original lane order. Inspection, exact-zero requirements, selected constraints, active-lane refinement and precision budgets are unchanged. Tests retain tiny real/imaginary nonzero residuals, unresolved rational equalities, complex Taylor jets, mixed derivatives, alternative Gram charts, translated inputs, empty and reordered batches.

At the represented binary64 ggH point, the same 33-addition/45-multiplication polynomial certificate has these diagnostic medians:

| Batch | ComplexBall baseline | RealBall candidate | Candidate / baseline |
| --- | ---: | ---: | ---: |
| 1 | 168.820 µs | 49.908 µs | 0.296 |
| 3 | 499.619 µs | 147.414 µs | 0.295 |
| 32 | 5.324 ms | 1.552 ms | 0.292 |

These are separate CPU-12 runs, each with three warm-up blocks and 21 retained blocks of 32 invocations, including fresh exact input conversion. They are not a quiet-window comparison, full reduction measurement or performance gate. The first candidate adds partition/scatter work to complex-only inputs; that overhead has not been timed. Any integration should preserve the original direct complex-only path and receive its own tests and full pipeline measurements.

The public ggH counter witness records two argument batches and one analytic child batch. It ran concurrently with compilation and establishes execution counts only. The isolated certificate cost explains a material portion of the earlier physical argument-stage cost, without establishing an exact attribution of its remainder.

`artifacts/profile_probe-build.json` records an unused initial `candidate.rs` hash even though that baseline includes only `profiled.rs`. The exact initial candidate is retained as `candidate-at-profile-build.rs`; the tested candidate has a different, explicit hash. The initial link without ThinLTO and initial `.repeat()` test typecheck failures remain as historical logs. The successful build metadata binds the corrected final sources. The generation script reproduces the initial candidate; the final timing-accounting change is visible in `candidate-experiment.patch` and final source. No source-only clean-build claim is made for the preserved archive set.

Verify retained files and qualification without a numerical engine:

```sh
source scripts/env.sh
python3 validation/real-ball-certificate/verify.py
```

The preserved build commands require the hash-matching optimized `80949db` archive set. Numerical reproduction uses `source .local/symbolica-license.env` after the environment setup, then the recorded binaries; the key itself is not part of this bundle. `certificate_tests --test-threads=1 --skip candidate:: --skip baseline:: --skip profile::` runs the four paired tests. `certificate_tests candidate::tests:: --test-threads=1` runs the eight inherited tests. `certificate_tests --ignored --exact profile_candidate_certificate_components --nocapture` produces the candidate profile; `profile_probe` produces the baseline profile. CPU affinity was 12 for numerical runs and 12/13 for compilation.

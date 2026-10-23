# Native stack-allocation candidate evidence

No production native kernel is adopted. A0/B0/dB0/C0 old/new outputs match exactly over 160 configurations (5,664 complex outputs), covering f64, DoubleFloat and Float256. Native/interpreter differences are retained separately. D0 numerical qualification remains pending its original long compilation; exported source provenance and ordered operand checks already pass.

Two timing protocols are retained. The original per-call-clock protocol gives two regressions and 22 noisy groups. The corrected fixed-loop protocol gives two singleton parity groups and 22 noisy groups; none of its 12 batch32 groups meets the performance gate. C0 batch32 candidate/baseline median ratios are 1.032, 1.066 and 1.052 for grouped, homogeneous and interleaved lanes; their CI99 lower bounds exceed one, but interval widths exceed the 2% noise limit. These measurements cannot justify adoption. They compare allocated native kernels with existing native kernels, not original IREGI or full reduction.

`generated-modules.tar.gz` preserves every exact baseline/candidate module, exact constant table and wrapper for all five families, with individual hashes. These are generated using existing Symbolica allocation and oneloopmaster emission; no custom algebra is introduced. The full IR provenance and source-reconstruction experiment is in `../stack-reuse/production-factory`. Runtime archive provenance is in that experiment's `current-workspace-build/{source-before.json,build-result.json,masters-diff.patch}`. `inputs.json`, `transitive-local-archives.json` and each build report record the retained runtime archive hashes; large archives and executable binaries are intentionally uncommitted. Historical archive hashes define the measured binary scope; a fresh dependency rebuild is a new experiment and is not asserted byte-identical.

For report-only replay in a fresh checkout, from the project root:

```sh
source scripts/env.sh
python validation/native-stack-batch/restore.py
python target/native-stack-batch/analyze.py
python target/native-stack-batch/analyze_fixed.py
```

`restore.py` verifies the evidence manifest and exact generated-module hashes, and refuses to overwrite an existing target directory. The archived analyzers use `validation/benchmark/run.py`; its hash is recorded in the manifest and must match before replay. This permits inspection and deterministic re-analysis without the runtime archives or a license.

For new numerical runs, restore the frozen archives into `target/native-stack-batch/deps` with the recorded hashes and matching registry transitives (or prepare and record a new dependency build). The source and archive paths and rustc arguments are explicit in each build JSON. The archived `build.py` uses the all-domain template; the exact historical per-family source is separately retained, including the dB0 unsupported-domain correction. `build_fixed.py FAMILY` uses the corrected f64-only template and refuses to overwrite a prior build report. Preserve historical reports elsewhere before making a new experiment. Correctness commands are `run_fixed.py FAMILY --phase before --cpus 20,21` and `--phase after`; timing uses `--benchmark --cpus 0` only in a coordinated quiet window. Load the private licensed environment after `scripts/env.sh`; never print or archive its value. Original all-domain evidence remains separate because f64-only compilation changes code layout.

`db0-parity.json` retains the initial failed unsupported raw-scaleless control; `db0-parity-2.json` retains the explicit public `UndefinedScalelessDerivative` rejection and matching raw nonfinite classification, followed by the supported corpus. Failed and unsupported cases are visible and are not counted as performance wins. The build pause log records only the validated owned D0 process group. It contributes to elapsed wall build duration and does not modify mathematical inputs.

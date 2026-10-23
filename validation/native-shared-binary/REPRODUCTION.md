# Reproduce this private experiment

Run all commands from `/shared/external/iregi/iregi-rust`. This bundle records a private B0/C0 lowering candidate, separate from the allocator and duplicate-body dense-span candidates. It makes no production change or original-IREGI performance claim.

`restore.py` verifies this bundle and extracts generated source into a fresh `target/native-shared-binary`. The archive contains both emitters, exact generated constants, baseline/candidate modules, wrappers and instruction provenance. All top-level Rust probes and Python scripts are also committed here. Binary/runtime archives are omitted; exact build commands and SHA256 hashes are in the build reports. Restore the frozen oneloop/Symbolica/iregi-masters runtime archives described in `validation/native-stack-batch/REPRODUCTION.md` before recompilation. They must match the build-record hashes.

Source `scripts/env.sh`, then the private `.local/symbolica-license.env` for numerical execution. Never print or commit the license. The reports record only whether the license environment is present.

For a restored snapshot, run `check_baseline.py` and `check_shape.py`. `build_probe.py` compiles the combined typed binary. It refuses to overwrite a prior build report: preserve all old reports before rebuilding, and treat the new binary as a separate timing cohort. Run `run_probe.py`, `qualify.py`, `code_size.py`, and `inspect_dispatch.py` to qualify old/new exact results and inspect compiled code. No new symbolic algebra is implemented: generated expressions and guarded fixtures come from Symbolica; arithmetic calls existing oneloopmaster primitives.

To regenerate sources, use the archived private emitters with `build_generator.py`, `run_generator.py b0`, `run_generator.py c0`, `build_fixture_generator.py`, and `run_fixture_generator.py`. The frozen public emitter assertion must still pass. `prepare.py` documents how the private patch was derived from the preceding dense-span source snapshot; it is not needed when restoring archived emitters.

Timing requires a coordinated quiet window. Run all-type `run_probe.py --phase before`, then `run_timing.py b0 --cpus CPU --quiet-window MANIFEST` and the corresponding C0 command sequentially. Run all-type `run_probe.py --phase after`, then `analyze_timing.py`. The same binary is used for all numeric qualification and f64 timing. Each family retains every requested group, including failures, noise and regressions. Statistical analysis uses the committed frozen `benchmark_helper.py`.

Scripts refuse to replace prior numerical/timing attempts. Preserve failures and changed-binary cohorts separately rather than overwriting them. Source and data analysis may be replayed without numerical execution or a license, except binary/code-size checks naturally require the compiled executable.

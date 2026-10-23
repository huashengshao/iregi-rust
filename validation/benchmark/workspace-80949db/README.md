# Unified optimized 80949db build

Both `kernel_benchmark` and `physical_benchmark` were compiled in one Cargo
workspace invocation from immutable commit
`80949dbc4711947971a702643f75d639ef217e82`. The profile was opt3, thin LTO and one
code-generation unit, with two build jobs on CPUs 2–3. Cargo recorded exit code
zero after 1,094.09 seconds. Both executables and their matched core/master/
Symbolica/oneloop archives are retained locally under
`target/benchmark/workspace-builds/80949db-default-resume/`.

The actual scalar-master feature list is `[default]`, with `native-batch`
absent. The target Symbolica library includes `tracing_max_level_info` and uses
opt3; Cargo separately compiled a host/build dependency variant without tracing.
The full feature/artifact records are in `workspace-build-recovered.json`.
No numerical benchmark is implied by this build qualification.

The initial build attempt was interrupted at the user's pause and its cache was
reused. The resumed Cargo compilation succeeded, but the original builder's
postprocessing rejected verbose build-script lines mixed into the JSON stream.
`workspace-build.json` retains that failed postprocessing record. Recovery
recognized 162 package-prefixed diagnostic lines, required well-formed Cargo JSON
and both successful artifact records, reverified source/asset inventories,
backend features, reference hashes and retained binary copies, then published
`workspace-build-recovered.json` without recompiling. The raw streams are
compressed here; their original hashes are in `qualification.json`. The recovery
script and exact original/recovery helper bytes are retained independently of
the benchmark source snapshot.

The historical child compatibility manifests omit a top-level `returncode`;
the successful compiler status is recorded in the parent manifest as
`resources.returncode = 0`. They are preserved unchanged. Strict consumers must
bind them to that verified parent rather than infer success. Future builder
exports now carry the verified compiler exit code, rejecting missing or nonzero
completion; parser/export regression tests cover this separately.

The existing optimized Fortran benchmark binary and build manifest were matched
to the selected timing driver and retained, without rebuilding the reference.
Compilation resource observations are diagnostic build costs and cannot satisfy
any reduction-performance acceptance criterion.

# Private CLI coefficient stack-allocation qualification

The private candidate adds Symbolica `optimize_stack()` once to each newly built ordinary `CoefficientPlan` evaluator. Empty numerators retain `None`; packing, support order, numerical mapping, batching and public interfaces are unchanged. This candidate has **not been adopted into production**. The CLI coefficient API has no Dual constructor, so this experiment makes no claim about a new Dual interface.

The baseline CLI sources are identical to revision `6b24c0372022e22606a1ac85f30c7fa579fb41f0`. Both variants were linked into one opt-level-2, thin-LTO, one-codegen-unit binary using the frozen completed 6b24 workspace dependency closure. Its full-workspace success and feature/artifact checks are bound by `dependency-workspace-completion.json`; `compile.json` records the exact command, compiler, source and archive hashes. All 865 retained dependency/native files were checked before and after compilation. Binary SHA-256: `af3a3b1a17821b35168f54037eaeb8496a4d6ef2a0c19b52756d1a46d046903b`.

| Physical numerator | Coefficients | Instructions | Temporary slots before | Temporary slots after |
|---|---:|---:|---:|---:|
| top-loop ggH | 15 | 149 | 149 | 63 |
| top-loop ggHH | 69 | 2,686 | 2,674 | 500 |
| top-loop ggHHH | 69 | 8,273 | 8,261 | 2,701 |
| massless up-quark four-gluon box | 70 | 44,407 | 44,407 | 8,396 |

All four cases passed. Exact exported dataflow, ordered operations/operands, constants, outputs and helper definitions agree after accounting for slot renaming. Complete coefficient arrays agree in represented rational values, precision metadata and signed zeros across f64, DoubleFloat and Float128. The 12 ordinary-domain suites each reuse workspaces through batch sizes 0, 1, 3, 7, 32, 3 (72 comparisons). Another 12 batches use Float256 workspaces with independently mixed 80-, 128- and 256-bit original input components.

The controls include canonical nonzero physical coefficients, vanishing numerators at zero strong coupling, complex couplings, a coupling perturbation visible only beyond 53 bits, changed parameter bindings, malformed batch shapes followed by successful reuse, and empty or constant-only numerators. Support ordering and output dimensions are checked. `exact-outputs-and-inputs.tar.gz` contains all complete outputs, packed inputs, prepared polynomial coefficients, structural proofs, source graph/model/input fixtures and logs. `exact-output-index.json` hashes every uncompressed archived file. Rational serialization includes explicit sign and precision fields for numeric coefficients.

These are correctness and storage results. Command elapsed time and RSS include physical graph preparation, proof export and JSON serialization during other work. They are not kernel timings, and no performance improvement or IREGI parity is inferred. The frozen 6b24 benchmark results exclude this private candidate.

For local reproduction, preserve existing evidence and use fresh output directories. From the project root, `source scripts/env.sh`, then load the untracked local Symbolica license environment without printing it. The retained source, archive paths and exact compiler command are in `compile.py`/`compile.json`; the coherent closure is `target/benchmark/dependency-closures/6b24c03-complete-kinds`. The original private source directory is `target/cli-coefficient-stack/source`, and input assets are under `target/cli-coefficient-stack/assets`. Run the compiled probe with, for example:

```sh
timeout 240 taskset -c 8 target/cli-coefficient-stack/probe ggh target/cli-coefficient-stack/replay-ggh
```

Repeat with `gghh`, `gghhh` and `gggg-up`, using a different new output directory each time. `run.py` records all four bounded commands and checks source, asset and binary hashes before and after execution. Its `qualification` directory must be absent before a new run.

Earlier failed attempts are retained separately: an older transitive dependency mismatch, an omitted explicit-rlib SymJIT dependency in the first 6b24 closure, a probe-only missing trait import, and an unavailable `/usr/bin/time` launcher path. No numerical failure occurred in those compile/launch attempts. The successful run used the installed `/run/current-system/sw/bin/time` and the corrected complete-kinds closure. An independent source review by `native_stack_batch` found no concrete issue in the patch or qualification scope.

A subsequent private paired timing experiment is retained in [warm-quiet254](warm-quiet254/README.md). It found a possible ggHH batch32 regression, so production remains unchanged; the correctness and storage results above do not imply blanket performance improvement.

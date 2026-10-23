# Physical numerical pipeline comparison

The completed attempt002 compares the default `SymbolicaBatch` executable from
immutable revision `80949dbc4711947971a702643f75d639ef217e82` with MadLoop's
selected-graph replay at the same preserved external point, wavefunctions,
parameters, helicities, and graph factors. These are equivalent complete graph
pipelines. Their internal ranks and routings differ; tensor-stage timing ratios
are not claimed. Final convention and graph-factor comparison adapters are
outside both timed bodies.

All six measured ggH, ggHH, and up-quark-box rows passed complete canonical
tensor and preserved graph-slot comparisons. Their ratio confidence widths
exceed the unchanged 2% gate, so every measured timing remains
`inconclusive-noise`. The observed Rust/MadLoop median ratios, about 4.1–12.0,
are optimization evidence and do not establish a qualified performance gate.
Both ggHHH rows fail during preparation with a binary64 derived-distance
conditioning diagnostic. They have no Rust timing samples and remain visible.

The CPU0 window used 21 blocks, five warm-ups, and a 30 ms target for singleton
and batch32. Rust and MadLoop ran sequentially; independent bootstrap samples
are used. The recorded project quiet window does not prove an absence of other
host activity, and the confidence intervals do not measure drift between the
two engines. Attempt001 was interrupted after a live validation-source edit;
it is retained separately and contributes no qualified result.

`qualification.json` is the compact summary. `files.json` binds every retained
text artifact to its original bytes, including all raw responses, complete
stage timings, original stdout, reference traces, generated Fortran sources,
producer snapshots, and build records. Large text files use deterministic gzip.
Frozen executables and archives remain hash-bound in the original `target`
directories and are not committed here. Paths inside raw records are unchanged
historical paths. Verify the committed bundle without running either engine:

```sh
source scripts/env.sh
python3 validation/benchmark/physical-joint-quiet/verify.py
```

The original numerical invocation was:

```sh
source scripts/env.sh
source .local/symbolica-license.env
taskset --cpu-list 0,16,17 python3 validation/benchmark/physical_joint.py --execute \
  --rust target/benchmark/workspace-builds/80949db-default-resume/bin/physical_benchmark \
  --build-manifest target/benchmark/workspace-builds/80949db-default-resume/physical_benchmark-build.json \
  --cases ggh gghh gggg-up gghhh --batches 1 32 --cpu 0 --build-cpus 16,17 \
  --repeats 21 --warmup 5 --block-ms 30 --timeout 600 --phase-timeout 1800 \
  --quiet-window-note '<record the actually coordinated quiet window>' \
  --output target/benchmark/physical-joint/new-quiet-run/results.json
```

Use a fresh output directory and coordinate a new quiet window before repeating
the measurement. The committed qualification records the actual note and times.

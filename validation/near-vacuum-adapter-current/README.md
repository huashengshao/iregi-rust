# Private adapter v3 with the current release dependencies

This directory repeats the selected v3 checks against the retained complete
`6b24c03-complete-kinds` dependency closure. It does not apply the prototype
patch, change production masters, or certify production E6 integration.
The unchanged Rust sources are retained in
`../near-vacuum-adapter-v3/private-sources.tar.gz`; build and runtime manifests
bind their exact hashes to the private library and drivers.

The first direct-rustc attempt omitted the workspace's thin-LTO settings.
Its valid oneloop archive contains LLVM bitcode, so ordinary native linking
failed before any numerical run. `failed-first-attempt.json`, the original
builder, progress record and logs preserve that attempt. The isolated retry
uses `-C opt-level=3 -C lto=thin -C embed-bitcode=yes -C codegen-units=1`.
It searches only the retained dependency and native-library directories.

`build_thin_lto.py` selects unique opt3, non-test Cargo library events for
oneloop, Symbolica and serde_json and records the complete closure before and
after linking. `run_current.py` verifies library and native manifest hashes,
runs each case with a 60-second bound on CPU18, records before/after hashes,
and rechecks the entire closure after all six cases. The cases are the four
existing typed mixed-component checks, the unsupported-shape/fallback and
unused-N4 preparation contracts, and the independent exact five-box contour
comparison. No accuracy budget is changed.

The commands, run only from the repository root, are:

```sh
source scripts/env.sh
source .local/symbolica-license.env
taskset -c 18,19 python3 validation/near-vacuum-adapter-current/build_thin_lto.py
taskset -c 18,19 python3 validation/near-vacuum-adapter-current/run_current.py
python3 validation/near-vacuum-adapter-current/audit.py
```

The builders and runner intentionally refuse to overwrite frozen scratch
directories or completed run files. Fresh reproductions need new output
paths and their own provenance. The historical private v3 source can be
restored into `target/near-vacuum-adapter-v3` from its committed source
archive before building. The full release dependency closure is a retained
build artifact bound to its successful workspace build; it must be present
or independently rebuilt and documented.

All six repeats passed. The four typed runs cover f64 working 53/requested 40,
DoubleFloat 106/80, Float 128/100 and Float 256/128. Their 96 accepted mixed
components exactly match the durable v3 checkpoint. The dispatch contracts
and the five primal boxes plus their contraction also passed. The independent
audit completed 4,845 checks with zero failures and zero serialized
differences, including all 37 native-library manifest rows and the four
unchanged 870-file closure inventories. The six contour comparisons satisfy
their original 128-bit budgets and contain the independent oracle rectangles.
`qualification.json` binds the complete evidence package. Compiler wall
times include the explicitly recorded 301.352638-second quiet-window pause;
none of the six numerical runs was paused or timed out.

All durations here are concurrent correctness diagnostics, not benchmark
results. Passing these checks establishes selected private-prototype
compatibility with this closure. It does not prove general D0 accuracy,
requested256-bit coverage, upstream rounded input enclosure, quadrature
error certification, or public E6 agreement.

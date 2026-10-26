# Current standalone Python facade wheel

A fresh Linux CPython 3.13 development wheel passes **64 installed API cases**,
consumer typing with zero errors or warnings, and **seven actual marimo notebook
runtime cases**. The wheel uses the shared Symbolica, Numerica, FeynKit and Spenso
PyO3 classes in one native host. Its native SHA256 is
`d86087ad79159c9340363c536c0ea645f1340d1cb76d2da8abff532e86b9982f`;
the wheel SHA256 is
`0851a691754b2fcf1da73558f06bc6e70fe514ae193c852a717e5a1dac9c051d`.

The 64 API cases comprise 25 upstream numeric precision/Float cases, 29 existing
numerical and native-object interoperability cases, and ten facade cases. The
facade suite covers actual engine tags, profiling, explicit ordered Duals,
checked supplied-product constructor guards, rejection before scalar masters,
batch lifecycle, sparse contraction, invalid-lane isolation and result ownership.
Eligible six-point profiling and primal-only Dual workspaces now select
`affine_power`; the old generic-routing observer was updated to the actual policy
and additionally checks empty nested counters and retained Dual shape.

The current checked-input cases reject deliberately inconsistent Cartesian and
supplied-product data in ordinary, profiling and primal-only Dual workspaces.
They establish guard behavior and empty reset, not successful checked rank-six
integrals. The retained six-point rank-one and seven-point scalar fixtures are
frontend regressions, not new high-point reference validation. No positive-rank
seven-point work, full six-point Dual array qualification or performance result
is claimed here. The seven notebook cases use the actual installed wheel,
including graph rendering, numerator preparation, batch contraction, dots,
Duals, beyond-binary64 input transport and the existing benchmark explorer.

Three initial failures remain visible:

- Nix toolchain paths disappeared during the first wheel build. That build
  failed with an unexecuted `rustc` and `ENOENT`. The exact preceding Rust/Cargo
  1.99 closure was restored from the binary cache and protected with project
  GC roots. All 146 common frozen inputs are identical across attempts.
- The first fresh-environment installation stopped at an offline cache miss for
  pinned marimo 0.24.0. Installing the same requested pins with downloads allowed
  succeeded in that newly created environment.
- The eight-case dispatch phase reached its fixed 325-second child deadline
  after seven exact pytest nodes had passed. Its final checked-Dual node was
  unfinished. Only that node was run again with a full 240-second case budget;
  it passed in 43.42 seconds. The original failed receipt and raw partial log
  remain unchanged. Numerical assertions and accuracy guards were unchanged.

The source archive contains 147 selected files from the actual owned build
snapshot. It is not a complete compiler, native or system closure. The evidence
archive binds the source context, actual wheel/native identities, raw logs,
receipts, successful XML, consumer typing and the three failed attempts. The
standalone CLI and its test executable were also compiled from this source
context; their hashes are recorded, while their binaries are omitted. All
owned process groups were recorded gone with empty cleanup errors. No wheel,
native binary, environment, cache or credential is committed in this capsule.

Run the saved stdlib replay, which starts no compiler, native host or integral:

```bash
python3 -I -S -B validation/python-interface/facade-wheel-003/check.py
```

It checks archive/member hashes, selected sources, successful cases, the seven
partial-run positives plus the one completed exact node, typing, identities and
preserved failures. Actual frontend test reproduction uses a freshly built wheel
and `tests/python/test_tirust_{interop,numerics,dispatch}.py`, the two upstream
Numerica Python test files, `tests/python/test_gallery_runtime.py`, and the
installed consumer from `tests/python/typing_example.py`.

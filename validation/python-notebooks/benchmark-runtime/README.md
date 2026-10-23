# Actual benchmark-only notebook execution

This separate capsule qualifies notebook `03_benchmark_explorer.py` only. It
does not import the `tirust` numerical extension. The first two graph/numerical
notebooks, native-wheel tests and graph/math visual review remain pending.

One bounded execution runs the three actual benchmark notebook tests and all
six real marimo cohort selections. Each selection returns its exact eight
saved rows and original gates. A single headless HTML export follows. Both
commands complete successfully in 2.74 seconds total under the declared
120-second cap; no Rust build, package install, numerical reduction or timing
measurement is performed. Receipts and stdout/stderr are in `attempt001`.

The exported HTML is retained as `attempt001/export.html.gz`. Its embedded
session has eleven successful cells, eight selected-TIRust/COLLIER default
rows, seven regressions, one short-block gate and eight uncertainty intervals.
The export inspection checks those actual outputs, rather than searching the
embedded source for example strings. `inspect_export.py` reproduces the check
against `target/gallery/benchmarks-posthoc.html`.

The HTML uses the official marimo 0.24.0 jsDelivr frontend, including scripts,
fonts and styles. It is not an offline self-contained export. No local browser
was available; no browser was installed and no browser visual pass is claimed.
Static export does not establish reactive browser controls. Actual backend
selection tests cover all six choices separately.

The source-only checkpoint and source archive remain in
`validation/python-notebooks/benchmark-posthoc`. Its historical predecessor is
reproducible at commit `1e06fc5`. The execution receipts bind to that reviewed
source checkpoint and verify its source hashes afterward; they do not claim an
independent before/after process guard that the wrapper did not record.

Reproduction from the project directory:

```sh
.local/notebooks-env/bin/python validation/python-notebooks/benchmark-posthoc/execute_benchmark.py
.local/notebooks-env/bin/marimo export html examples/notebooks/03_benchmark_explorer.py -o target/gallery/benchmarks-posthoc.html
.local/notebooks-env/bin/python validation/python-notebooks/benchmark-runtime/inspect_export.py
```

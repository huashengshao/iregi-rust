# TIRust notebook qualification

The gallery lives in `examples/notebooks`. The binding implementation and
numeric/type interoperability are owned by `iregi-python`; the notebook helpers
only format values and read frozen benchmark evidence. No symbolic algebra,
reduction, tensor contraction or fake numerical backend is implemented here.

The notebook sequence and visual hierarchy were inspired by the exact HEPKit
[four-loop numerator notebook](https://hepkit.org/gallery/notebooks/four_loop_numerator.py).
Reference URLs, hashes and the pinned Symbolica Community extension guide are
recorded in `source-reference.json`. Upstream source was read without executing
it. No external image assets or copied reference source are required at runtime.

Current qualification: source review and official marimo 0.24.0 strict lint pass
for all three notebooks; nine evidence/display-helper tests pass. The actual
standalone wheel, numerical notebook execution, static HTML exports and visual
review remain pending. No notebook runtime success is claimed before those
checks finish. The core Rust implementation does not depend on Python.

The first strict JSON-format lint invocation found zero issues but hit an
upstream CLI `UnboundLocalError` while deciding its exit code. Its stdout,
stderr and source hashes are preserved in `lint-attempt001`. Repeating the same
strict checks using the normal text formatter passes with exit 0 in
`lint-attempt002`; no marimo source, rule, threshold or notebook was changed.

Reproduce source checks with the repository's Python environment:

```sh
source scripts/env.sh
python3 validation/python-notebooks/review_source.py
.local/notebooks-env/bin/marimo check --strict examples/notebooks/01_numerator_to_integral.py examples/notebooks/02_dots_and_derivatives.py examples/notebooks/03_benchmark_explorer.py
```

The source checker parses the notebook, helper and test files without importing
or running them. It checks cell return definitions, argument ownership and
acyclic dependencies. Official marimo lint is required separately.

When the real wheel is available, install it in a fresh private Python 3.13
environment alongside `marimo==0.24.0`. Both numerical notebooks import inputs
and tools from the same `tirust` native host; do not mix a separately compiled
Symbolica/Community wheel's objects. Then run:

```sh
.local/notebooks-env/bin/python -m unittest discover -s tests/python -p 'test_gallery_*.py' -v
.local/notebooks-env/bin/marimo export html examples/notebooks/01_numerator_to_integral.py -o target/gallery/first-reduction.html
.local/notebooks-env/bin/marimo export html examples/notebooks/02_dots_and_derivatives.py -o target/gallery/dots-and-derivatives.html
.local/notebooks-env/bin/marimo export html examples/notebooks/03_benchmark_explorer.py -o target/gallery/benchmarks.html
```

An unavailable or broken native extension is a test failure, not an automatic
skip or an invitation to substitute mock numerical results. All native Laurent
coefficients, real shared object identities, full tensor arrays, nonidentical
batch lanes, mass derivatives, precision distinctions and failure masking are
checked using the actual compiled API. Static export alone does not qualify
every interactive control or exceptional kinematic domain.

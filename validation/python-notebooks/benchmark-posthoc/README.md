# Separate benchmark-explorer source checkpoint

The original nine-test/source-lint qualification is unchanged at
`validation/python-notebooks/qualification.json`; its exact gallery source is
committed at `1e06fc5`. This capsule checks the later explorer revision rather
than rewriting that historical evidence.

The explorer now offers five source-bound comparisons from the same frozen
four-engine session, alongside the historical `6b24c03` production snapshot.
Every ratio has TIRust in the numerator. The private baseline and selected
native-master prototypes remain explicitly labelled, with no adoption or
current-production equivalence claim. The separate posthoc correction and
original conservative verdict remain visible; the short bubble singleton is
retained in every private comparison. Archival IREGI/COLLIER absolute times are
still displayed separately. No timing ratios are reconstructed across sessions.

Reproduce the AST dependency check, official marimo 0.24.0 strict lint and the
15 pure evidence/display tests from the project directory:

```sh
.local/notebooks-env/bin/python validation/python-notebooks/benchmark-posthoc/validate_source.py
```

The focused checks compare all 40 displayed private ratios and 80 confidence
interval endpoints directly with saved data; test both hash and comparison
rejections; retain all short/noisy/failed gates; and prevent mixed comparison
labels in one chart. The numerical notebooks and their real API examples are
unchanged. No native wheel, numerical reduction, notebook execution, static
export or browser rendering is qualified by this source checkpoint.

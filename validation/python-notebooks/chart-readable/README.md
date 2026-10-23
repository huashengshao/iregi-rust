# Readable mobile uncertainty chart

The benchmark chart now keeps its 930-pixel SVG width inside the existing
horizontal overflow container. Labels retain their readable size on narrow
screens while the page itself stays within the viewport. The table, ratios,
confidence intervals, qualification gates and numerical notebook source are
unchanged. This supersedes only the mobile chart typography limitation recorded
by the historical `benchmark-browser` capsule; no earlier receipt is rewritten.

One source/helper/execution/export sequence passes: official marimo 0.24.0
strict lint for three notebooks; fifteen pure evidence/display tests; three
actual benchmark-app tests plus all six cohort selections; and a fresh static
HTML export. Before/after source guards are recorded for every command. No
numerical backend is imported or executed.

One browser check uses the same pinned Playwright/Chromium environment and
scoped Nix loader closure. Desktop and narrow/dark grid/chart screenshots pass,
with no request, HTTP, console or page error. The narrow chart has 930 pixels
of scrollable content within 348 visible pixels; the document remains 390
pixels wide. Left/right crops show readable labels and the panned plot.

The new source and protocol scripts are archived in `source.tar.gz`; exact
HTML output is retained as `export.html.gz`. Dependency paths and the earlier
loader failure remain in the historical browser capsule. Static export still
requires the official marimo CDN frontend and has no reactive backend. Native
graph/numerical notebooks and their wheel-backed visual evaluation remain a
separate qualification.

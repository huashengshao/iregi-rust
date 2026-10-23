# Actual static benchmark browser smoke

This supplement covers the existing `03_benchmark_explorer.py` static HTML
export only. It changes no notebook/helper source, HTML, timing data or network
policy. It does not load a numerical backend or qualify notebooks 01/02.

Playwright 1.55.0 and its Chromium 140.0.7339.16 headless shell were installed
into project-owned environment/cache paths. The first browser attempt failed
before opening a page because the host lacked the required shared-library
search path. That failure and the browser installer's dependency warning are
preserved in `attempt001`.

The authorized environment-only correction selects 23 already installed Nix
libraries through 18 scoped `LD_LIBRARY_PATH` entries. `ldd` then reports no
missing browser dependency. Exact library paths, resolved hashes and browser
digest are retained in `attempt002/loader-environment.json`; no shared library
or browser executable is copied into this capsule. Package versions are pinned
in `requirements.txt`. No system or global environment setting was changed.

The successful smoke renders desktop 1440×1100 and mobile 390×844 views, each
with eight ratio cells, the preserved short-block status and rendered KaTeX.
The followup crops the existing offscreen grid and chart, including horizontal
scrolling of the mobile grid. Both phases together take 9.61 seconds under the
120-second browser budget. All 1272 ordinary frontend requests are recorded;
none failed and there are no page errors. No certificate, network or frontend
error policy is bypassed.

Screenshots show readable desktop cells and readable narrow/dark cells through
the grid's own horizontal scrolling. The mobile SVG chart scales its labels
small; that remains a visual limitation. Full-page screenshots only cover the
marimo internal scroll viewport, so the targeted grid/chart crops are retained
separately. The export includes code and requires the official marimo CDN
frontend; it is neither an offline package nor a reactive backend. This is a
bounded static-browser smoke, not complete gallery visual qualification.

To reproduce in the recorded environment, set the scoped loader path from
`attempt002/loader-environment.json` and the project browser cache, then run
`smoke_browser.py` and `inspect_grid.py` with the browser environment's Python.
The HTML source/hash remains the exact export archived by the separate
`benchmark-runtime` capsule. Preserve these receipts before creating any new
attempt; the scripts are reproduction commands, not automatic retry loops.

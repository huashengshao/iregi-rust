# Publication inventory and historical preservation

`publish.py` only reads or writes saved artifacts. It does not compile code,
execute a tensor reduction, or infer accuracy from a native warning flag.
Run it from the project root with the pinned Python environment sourced.

The pinned previous publication is
`78193d6ea5dd8804b25032a65d47492a128f427e`. All **469** of its top-level
`docs/data/results.json` values retain their exact JSON spelling. New source,
SHA256 and JSON-snapshot records are appended under the
`opening_double_precision_` prefix. The previous report proof, including its
entire existing nested history, is copied under
`previous_78193d6_publication`; its original byte hash is recorded separately.

The campaign manifest covers every file in this directory recursively except
the manifest itself, `__pycache__` subtrees, and unfinished `*.partial` files.
It records each relative project path, SHA256 and byte count. Raw logs remain
byte-identical, including upstream banners with trailing blanks. A source
or additional capture written after binding invalidates the inventory; finish
the complete campaign and its reviews before binding it. Files under `target/`
are not implicitly archived: relocate retained raw evidence before binding.

Default required bindings are:

| Result key suffix | Source relative to this directory |
| --- | --- |
| `examples` | `summary.json` |
| `build` | `build.json` |
| `qualification` | `qualification.json` |
| `independent_review` | `independent-review.json` |
| `manifest` | `manifest.json` |

If present, `collier/{summary,build,supervision,qualification,independent-review,manifest}.json`
are bound separately under `opening_double_precision_collier_*`. Use
`--binding opening_double_precision_NAME=PROJECT_PATH` for additional retained
receipts or captures. The four main source paths can be overridden with
`--summary`, `--build`, `--qualification` and `--independent-review`.

The summary must retain each of the exact 18 historical IDs once, preserving
their N, rank, propagator powers and dimension shift, with `numeric_type: "f64"`
and `working_bits: 53`. The three ordinary high-point rows use `requested_bits: 39`
(approximately `1e-6` under the existing guard); other rows use 53. Failed
candidate rows remain in the summary. This metadata check does not certify a
candidate's numerical result or impose the historical strict accuracy gate.

After raw captures, source receipts, summary, qualification and independent
review are final:

```sh
python3 -I -S -B validation/benchmark/opening-double-20261026/publish.py bind --dry-run
python3 -I -S -B validation/benchmark/opening-double-20261026/publish.py bind
bash scripts/build-benchmark-report.sh
typst compile --root . --creation-timestamp 1792972800 \
  docs/benchmark.typ target/opening-double-20261026/independent.pdf
```

Inspect the actual rendered opening pages, record the page count, and write a
root review with a `passed...` status. The review can bind the PDF, Typst,
results, manifests, README and HANDOFF, but must not bind the final proof's
hash: the proof binds the root review, avoiding a hash cycle. Then seal:

```sh
python3 -I -S -B validation/benchmark/opening-double-20261026/publish.py seal \
  --page-count ACTUAL_PAGE_COUNT \
  --independent-pdf target/opening-double-20261026/independent.pdf \
  --root-review docs/data/opening-double-root-review-20261026.json \
  --render-check 'Describe the pages actually inspected and their observed layout.'
python3 -I -S -B scripts/check-benchmark-report.py --preserve-from 78193d6
```

`seal --dry-run` checks the bound inventory, source hashes, root-review status
and its `report_artifacts` hash mapping, precision metadata, and independent
PDF equality at a distinct file path without writing the proof.
The real seal repeats these checks, refreshes the source ledger and current
artifact hashes, preserves the old proof, and runs the report checker. Pass
`--artifact PROJECT_PATH` for additional final report artifacts or
`--known-limit TEXT` for an extra scope note. The descriptive means and
candidate selection are an optimistic timing showcase; they do not establish
a controlled-host comparative speed gate.

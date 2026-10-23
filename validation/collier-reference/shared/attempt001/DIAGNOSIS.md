# Preserved generic TNten interface regression

This package contains the reviewed first generic driver, its strictO3 link,
all prepared inputs and Symbolica witnesses, and the complete bounded
correctness capture. Source/input/binary guards passed. Input preparation took
3.678 s, driver-only linking1.070 s, and correctness5.543 s. The original IREGI
and COLLIER libraries were unchanged. No timing cohort was run.

All16 fixed N2/N3/N4 batch rows were captured, with112 complete engine
responses. All exact retained IREGI comparisons passed. The generic-vs-old
COLLIER interface gate failed at N2 and COLI N4 tensor ranks, so all18 higher-N
rows remain `not_run`. No N5/N6/N7 request was issued. The six `accepted-COLI`
row labels in the raw capture refer only to the four fixed triangle rows and
two scalar-box rows, not to successful broader qualification.

The upstream source explains the discrepancies:

- In
  `target/reference/collier/source/collier-COLLIER-1.2.10/src/tensors/BuildTensors.F90`,
  SHA-256 `082b29e72a067c42c011ef1eee8a1f2b0e772131a8c2bff6fe7cd2e484fa209e`,
  `CalcTensorTN_list` initializes `TNuv=0` at line1424 and comments out the
  scalar UV assignment at line1426. Generic TNten therefore drops the scalar
  bubble's UV coefficient. The fixed deltaUV probe rejects it, and the native
  finite normalization differs. The dedicated Bten API returns the UV term.
- In
  `target/reference/collier/source/collier-COLLIER-1.2.10/src/collier_tensors.F90`,
  SHA-256 `84eb74151250657fd7b08510b966b09b6bf84bac2abdb7c484407c95d3cba0db`,
  generic TNten uses a scale floor for relative error normalization at
  lines6153–6181, explicitly marked as a2023 addition. Dedicated Dten uses
  the actual component norm at lines2340–2365. On these fixed N4 inputs the
  complete raw arrays and absolute estimates agree, while generic TNten
  reports `AccFlag=0` and Dten reports `AccFlag=-1`. This changes the upstream
  API's status policy and cannot silently replace the preserved N4 rejection.

The next candidate may use the unchanged official Bten/Cten/Dten interfaces
at N<=4 and generic TNten only at N5–N7, with the actual interface recorded.
It requires a new source/protocol review before linking or execution. No
ad-hoc UV repair, flag compensation, library patch, tolerance relaxation or
fixture replacement is justified by this package.

`qualification.json` binds every compressed payload and the frozen producer.
JSON gzip files preserve the exact raw bytes (`mtime=0`, compression level9).
The deterministic tar.gz archives contain sorted relative regular-file paths,
zero owner/time metadata and mode0644; their file inventories and uncompressed
archive hashes are recorded. Prepared DOT/JSON/log artifacts, source snapshots,
module hashes, source review and prior protocol tests remain available for an
independent audit. These diagnostics do not qualify a failed lane.

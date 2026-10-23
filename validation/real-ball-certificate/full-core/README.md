# Slim RealBall certificate: private full-core qualification

The candidate passes 88 focused core tests, eight paired kernel packets, 15 paired precision/Dual cases and two physical ggH comparisons. Only `invariant_certificate.rs` differs between the frozen core snapshots. The source is revision `6b24c0372022e22606a1ac85f30c7fa579fb41f0`; the candidate certificate is SHA256 `9a89286f2e7f2c515ac48284c3ddbff101bec83cbab191c93bc263a0a50a5fc2`. There are no proof receipts and no production changes in this qualification.

The focused core filters cover execution (35), certificates (8), exact zero (4), stability (38) and rescue (3). Two highpoint rescue tests remain explicitly ignored. Kernel cases cover real, complex and invalid lanes at singleton, odd and batch-32 widths: 6,000 complex Laurent slots agree exactly. The typed cases compare 3,600 complex Laurent/Taylor slots using binary64, DoubleFloat and Float128, ordinary values and static/dynamic first/mixed Dual carriers. Requested accuracy is 53 bits; metadata, all input components, statuses, diagnostics and counters agree. The 31 protocol checks include malformed precision, axes, shapes, lane and counter records.

The physical ggH comparisons retain 256 paired complex tensor/contraction slots at batches one and three. Both variants agree independently with all three preserved canonical IREGI modes and preserved selected MadLoop graph slots at the unchanged `1e-10` tolerance. Maximum normalized tensor error is `3.54e-15` and graph error `8.01e-15`. The physical baseline reuses the completed immutable6b24 Cargo executable; its link recipe differs from the private candidate. These are correctness comparisons only. The kernel timing pair uses identical direct-rustc recipes.

The first quiet timing run uses CPU254, 21 alternating paired blocks, five warm-up blocks and an initial 30ms calibration target. The existing frozen benchmark statistics use 10,000 paired bootstrap median resamples, a 99% confidence interval and a maximum 2% relative interval width. All raw outputs, block order, responses, binary/source hashes and completed window metadata are retained. Real ggH singleton and batch32 ratios are 0.5767 and 0.5060, but their interval widths are 3.06% and 6.10%; both remain **inconclusive**. Complex controls qualify as singleton parity and batch32 improvement. This narrow tensor-kernel experiment makes no physical end-to-end, IREGI/MadLoop speed, aggregate performance or production-adoption claim.

The subsequent 41-block, at-least-200ms protocol is separately registered and unrun here. It cannot replace the first run. The earlier parent-directory profile measures a different certificate candidate; its timings must not be attributed to this implementation. The existing 23 module tests remain separately documented under `../slim`. Current certified-planar API interaction tests are a separate pending qualification.

`HANDOFF.json` preserves the historical pause state; `qualification.json` describes this completed evidence bundle. Source snapshots can be reconstructed from the recorded Git revision and `evidence/sources.json`, replacing the candidate certificate with `source/candidate_invariant_certificate.rs`. The complete compiler commands, toolchain, selected library events, source inventory and binary hashes are in the build manifests. The coherent dependency closure metadata is retained in `../slim/dependency-closure`; the 865 matching library/native artifacts and executables remain locally under `target`, are not committed, and are not claimed to be reproducible byte-for-byte.

Verify the committed evidence without numerical execution:

```sh
source scripts/env.sh
python3 validation/real-ball-certificate/full-core/verify.py
```

To replay locally, first restore the snapshots into `target/real-ball-core` using `restore_sources.py`, preserve or reconstruct the exact recorded dependency closure, and copy the retained top-level scripts from `evidence` to that directory. The original build scripts and logs document every invocation. The existing bounded test and paired correctness runners can then be used; numerical execution requires sourcing `.local/symbolica-license.env` after `scripts/env.sh`. Do not overwrite existing run ledgers. Timing requires a new explicitly coordinated quiet window and output directory. The secret license is not part of this bundle.

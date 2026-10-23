# Slim certificate and current planar API interaction

The private candidate passes nine existing certified-planar tests and one new original/slim certificate comparison. Existing tests cover invalid input isolation, exact full jets and chart units, explicit binary64 guard rejection, Float128/256 convergence, rotating mixed jets against independent box identities, reordered/empty batches and workspace reuse. Three high-rank artifact tests remain explicitly excluded.

The new control uses the actual planar polynomials and six Taylor components. Symbolica constructs imaginary first jets whose product yields a real mixed coefficient. It compares interleaved real/complex rows, deliberately nonplanar mixed jets, a tiny residual unresolved at128bits and resolved at512bits, selected primal chart components, reordered/empty masks and subsequent empty/all-complex calls against the original ComplexBall implementation. Source review corrected two fixture errors before numerical qualification.

The candidate captures current core revision21622ec plus the separately hash-bound collector implementation, replacing only the production certificate module with the reviewed slim source. Original certificate modules and the appended test are private validation aids. Exact snapshots, inventories, compiler commands, test membership, logs and failed attempts are retained. The shared filesystem ENOSPC build failure is historical; no result from it was qualified.

This uses the coherent completed6b24 dependency closure. It qualifies local current-core/planar integration, not the later public-master API or complete project acceptance. Production was not modified, and there are no timing claims. The executable and865dependency/native artifacts remain under target with hashes; they are not committed.

Run the offline verifier from the project directory:

```sh
source scripts/env.sh
python3 validation/real-ball-certificate/planar-interaction/verify.py
```

The retained build and bounded runner scripts replay using the recorded source snapshots and exact dependency closure; numerical execution additionally requires sourcing the untracked `.local/symbolica-license.env`. Preserve existing build/run records before any replay.

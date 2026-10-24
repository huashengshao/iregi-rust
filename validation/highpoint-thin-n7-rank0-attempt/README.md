# Failed private N7 rank0 qualification attempt

**Numerical qualification FAILED.** This capsule retains the original failed build001 and the six authorized API2 stage records. The successful helper build and necessary-domain audit did not establish a numerical N7 result.

- Generic plan preparation timed out after a recorded 290.991932-second subprocess. Capture including postguards took 300.928116 seconds, exceeding its 300-second total bound; the receipt flags the failure. No Rust numerical values, completed plan or completed workspace were recorded.
- Original IREGI IBP and Hybrid returned identical stable finite observations. PV explicitly returned unstable zeros. These observations do not establish a successful Rust comparison.
- The independent oracle completed exactly six fixed rules (orders 8/12/16 and two mappings). Its saved estimated normalized uncertainty is 7.695957034646326e-10, above the unchanged 1e-10 threshold; it exited 2 for insufficient convergence. There was no adaptive extra rule or relaxed threshold.
- Comparison admission rejected the capture's exceeded total bound before spawning the comparator. Its receipt has zero subprocesses and no comparison output. Numerical qualification remains failed.

`qualification.json`, `final-independent-review.json`, `build-domain-review.json`, stage receipts, partial results and logs are byte-identical copies. `initial-failed-001/` preserves the first helper compile failure; `api2/` preserves all six later stages. `provenance/` retains original external text receipts and data. No historical target path inside a copied record has been rewritten.

`sources.tar.gz` contains the exact 40 frozen N7 core files and their source/protocol history, both rank0 source/protocol/grant/review snapshots, earlier source revisions, and bound external helper scripts. Its sorted regular-file members use fixed metadata and deterministic gzip. `payload-origins.json` maps every copied file and archive member to its original path and hash. `manifest.json` hashes every payload file and archive member; it excludes its own hash.

`protocol-input-bindings.json` retains all 240 immutable protocol input hashes, closure inventories and package locations. Compiled binaries, rlibs, native libraries, dependency trees, Python packages, toolchains and caches are excluded. This is an evidence capsule, not a self-contained build environment. Original artifact hash bindings remain in the unmodified receipts.

The separate [exact-test capsule](../highpoint-thin-n7-exact/README.md) records 17 selected exact tests passed and one ignored generic constructor test explicitly UNRUN. That historical exact result remains distinct from this failed numerical attempt. Its parent manifest, source archive and core source manifest hashes are bound here.

Packaging performed only file reads, hashing, saved-data consistency checks and deterministic serialization. It did not run any build, Rust test, candidate script, runtime bootstrap or numerical integral. This capsule makes no higher-rank, Dual, batching, precision, physical-graph, performance or production qualification claim.

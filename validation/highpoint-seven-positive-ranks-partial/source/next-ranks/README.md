# Capture-only ranks two and seven

This is an unexecuted source proposal. It reuses the admitted actual-Cargo
generic probe from `../probe-fix-v2/runs/build-002`: SHA-256
`213ea01fd30a8acf2a794474db09ad9fc367fb9561667c23f73c76c4953a7e19`.
There is no rebuild, metadata query, cache copy, preparation-only numerical
process, or public API change. Existing frozen helpers and receipts are untouched.

`prepare.py` is a one-shot source/hash-only stage with total/reserve bounds
180/30 seconds, no child process, CPUs 20–21. It uses the old admitted protocol's
explicit 128-file inventory and build002's input identities, including the
corrected probe digest. It reads exactly those files, checks their hashes, and
writes a deterministic read-only `source-snapshot.tar.gz` plus
`source-manifest.json`. It performs no source-directory walks or transitive
dependency checks. The resulting small protocol binds the snapshot, single
shared executable, active helpers, fixture, exact quad requests/raw arrays,
required runtime environment and flat historical attestation receipts.

Runtime guards hash that compact set once before and once after each stage.
Historical receipts remain attestations: their embedded input maps, external
source trees, old core/masters products and old owned probe copies are never
recursively merged into a current guard. This preserves the build provenance
without imposing the old 31,250-file live closure. External native-link closure
qualification remains explicitly false. The shared executable must remain a
read-only regular file; captures execute it directly without making extra copies.

`rank_adapter.py` supplies only capture/comparison operations to `run.py`.
The latter retains the reviewed finite controller's original absolute deadline,
pre/post guards, whole-process-group cleanup and final-save machinery. Its
unreachable cache/build branches are removed. Lifecycle source is unchanged
`../lifecycle.py`, SHA-256
`c193cd7282d63b63a8f627612df684242a2a8941d1d0a35588514d0415ab8824`.

Rank1's passed paired gate is fixed to receipt
`1d65ca0fd43ea574e1b5b04e5766483ee376e5239b7d04f7901cb1a3db2553a1`
and comparison
`a6e1a41c364423e10ecbe2f11394fdd0952d643cf7c69034dc4316a3604fa935`.
Rank2 then uses total/reserve/child bounds 900/120/600 seconds at 128 bits and
1200/150/960 at 256 bits. Only a passed rank2 paired gate admits rank7, whose
bounds are 1680/120/1500 and 1980/120/1800 seconds. Each precision has exactly
one attempt and no retry. Each saved comparison uses 120/15 seconds, no child.
All guards, cleanup, output hashes and final serialization share the original
absolute deadline; reserves never renew that deadline.

The 128-bit controller owns CPU6; 256-bit owns CPU7. At most two captures of one
rank may run concurrently under the explicit root correctness grants. Each
controller is a separate Python process, each child uses `start_new_session`,
and c193 cleanup targets only its recorded `owner.pid` process group. Output
directories and signal handlers are independent. This is a correctness run,
not a performance measurement; sequential launches are also possible.

The existing `../compare_positive_saved.py` is reused byte-for-byte. Shape
checks call the retained `canonical_basis`: rank2 has 15 moments/60 complex
Laurent slots; rank7 has 330/1320. Fixture SHA is `6c78096e…89d2`.
Quad rank2 maps to `quad_n7_seventh_time_quarter_rank2.txt` and
`capture-001/request-1.stdout`; rank7 maps to its corresponding request and
`request-2.stdout`. Independent quad audit stays `f0b8f077…73fd`.
Every complex slot is checked against the quad reference at 1e-10, paired
128/256 convergence at 2^-80, with native poles, exact inputs, precision
metadata and the execution ledger retained. Normalization uses the existing
rank-dependent natural scale. Rank7 child masters remain rank-dependent;
no 105-row assumption is introduced. Failed arrays/diagnostics stay visible.

After successful preparation, an independent `source-review.json` must pin
both protocol and preparation receipt. Exact root per-stage grants under
`grants/rank{rank}-{operation}.json` bind that review, resources and prerequisite
paired gate. No capture can run before those checks. This source proposal
creates no protocol, snapshot, review, grant or producer output. After review
and grants, commands from the project root are:

```text
<frozen-python> -B <this-directory>/prepare.py
<frozen-python> -B <this-directory>/run.py 2 capture128
<frozen-python> -B <this-directory>/run.py 2 capture256
<frozen-python> -B <this-directory>/run.py 2 compare
<frozen-python> -B <this-directory>/run.py 7 capture128
<frozen-python> -B <this-directory>/run.py 7 capture256
<frozen-python> -B <this-directory>/run.py 7 compare
```

Public rank support remains unchanged pending the separate decision after
rank7's full gate. No accuracy or performance qualification is claimed here.

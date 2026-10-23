# Private planar rank-seven qualification

The isolated certified planar wrapper now passes the complete 330-moment,
four-Laurent-slot rank-seven identity against five independent box reductions
at Symbolica Float128, with requested accuracy53. The test compares complex
errors against `1e-10 * max(|reference|, physical_scale^(rank-6))`.
All primary and independent-box lane statuses were successful.

The same frozen binary passes the seven-lane, two-chart rank-two ordinary
corpus at Float128 and Float256, including normalized `2^-65` convergence,
and the ordered six-component rank-two mixed/second-Dual corpus at Float128.
Tangential jets pass all independent-box comparisons; the transverse mixed jet
is rejected. Failed lanes and exact ordered Dual metadata are asserted.

This candidate adds only four accumulator changes to use Symbolica
`Atom::add_many`, plus the test-only dimensional normalization. Existing phase
instrumentation and numerical guards are retained. The first compile exposed
two errors in the previously uncompiled test patch; that failure and the
checked rank conversion/local slot-count repairs are retained.

The rank-seven run completed in258.79seconds under a300second bound.
The prior180second timeouts remain in `validation/planar-certified`; this is
not a matched timing comparison and does not establish an optimization gain.
Primal amplitude preparation alone consumed135.44seconds.

This remains an isolated wrapper, without automatic public `Workspace`
fallback integration. The original wrapper chart-dispatch statistics issue
remains visible, and the candidate has not been compiled against the newer
production generalized-PV/allocator changes. Rank-seven Float256 convergence
and rank-seven Dual coverage are not established by this increment.

`qualification.json` records the exact scope. `source/` is the full frozen
core source used by the binary. Build records bind all dependency archives,
source hashes and binary hashes. Raw build/run paths are historical paths;
large binaries/archives remain hash-bound under `target` and are not committed.
`candidate.patch` applies to the phase-instrumented baseline recorded in the
previous bundle. `files.json` binds every retained artifact. The compile and
run scripts are the actual historical scripts and retain their original
`target/planar-certified` paths.

No production Rust file was changed by this increment.

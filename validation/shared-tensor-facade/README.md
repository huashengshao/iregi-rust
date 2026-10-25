# Shared tensor facade: saved source and test proof

This compact capsule preserves the actual default-feature Cargo test build for the
additive `TensorReductionPlan` / `TensorWorkspace` core facade. Six ordinary tests
passed. One separately bounded, explicitly selected Float128/requested53 test
passed for the retained exact N6/N7 scalar fixtures, comparing the facade against
the existing public wrappers with shared immutable plans. It checks all four
native Laurent slots, invalid lanes, input preservation, common contraction,
actual tagged counters, and empty-call reset. The original failed Cargo build and
its one test-only `FloatLike` → `SingleFloat` import repair remain visible.

Run the portable proof from the project root:

```sh
python3 validation/shared-tensor-facade/check.py
python3 validation/shared-tensor-facade/check.py --reconstruct /new/empty/source-directory
```

The checker uses Python's standard library only. It verifies exact capsule and
parent hashes, reconstructs all 65 relevant source files, checks the independent
source review plus narrow import addendum, and replays saved commands, finite
bounds, terminal receipts, Cargo artifact metadata and complete selected-test
logs. It does not import the historical controller, build, evaluate an integral,
execute a binary, inspect a current native artifact, or probe a process. Native
binary digests and terminal group absence are historical receipt attestations.

The source context is reconstructed from the existing 64-source
`public-rank7-current-cargo-n1-n5` archive, the exact `execution.rs` member of
`typed-dual-state-reset`, and four facade overlays. The original failed-build
context is independently reconstructed by reversing the single ignored-test
import; its exact 65-entry inventory is preserved. Only four declared parent
files are needed; no unrelated historical proof is replayed.

The original build used `cargo test --locked --offline -p iregi-rust --lib
--no-run --message-format=json -j2`, CPUs18/19, default features. Runs used a
frozen owned copy of that test artifact on CPU18 with one Rayon and one test
thread. The compiler failure took9.56s; successful build48.63s; ordinary stage
7.72s; specialized stage276.56s. These are diagnostic elapsed times, not a
performance benchmark. The actual controller's earlier cleanup reserve values
are retained as historical facts, without claiming the current runner policy.

This qualifies delegation in the saved source context. It is not a new
independent integral oracle, complete dependency/native-build closure,
feature-union, higher-point Dual, rank/domain, performance, later joint-main or
CLI/Python qualification. Dual, profiling, native-policy and rescue requests use
existing generic APIs. The ordinary thin selector preserves exact requested
settings; `Default` is eligible only when the effective compiled default is
`SymbolicaBatch`. Tagged nested diagnostics retain actual engine work counters.

`qualification.json` and all original evidence files are byte-exact copies.
Its note saying an import addendum was requested records the earlier state;
the now-sealed independent addendum is included and verified by this capsule.
No binaries, caches or license literals are included.

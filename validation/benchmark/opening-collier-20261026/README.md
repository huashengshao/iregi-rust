# COLLIER column for the opening tensor table

This is a separate absolute-timing campaign for the twelve ordinary entries in
`../opening-rank6-20261026/inputs.json`. It leaves those inputs and the earlier
TIRust measurements unchanged. COLLIER 1.2.10 uses binary64 and predetermined
COLI mode 1, including N5/rank6. No mode selection, retry or per-row retuning is
allowed. These observations are not a synchronized TIRust/COLLIER ratio campaign;
the original TIRust rows explicitly retain their own working precision.

`driver.f90` derives from the frozen
`validation/collier-reference/shared/candidate004/driver.f90`. It adds the public
Aten interface for N1, restricts the admitted domain to N<=6/rank<=6 and records
all normalized Cartesian tensors and diagnostics after every timing block.
The arithmetic, normalization, pole probes and strict status gates are retained.

The requested input is unchanged: exact shifts, positive real squared masses,
mu=3, unit propagator powers and h=0. Each result contains every Cartesian moment
through R and all four native Laurent slots. IR slots are zero only on this
positive Feynman-polynomial family, checked separately by varying both COLLIER
IR delta parameters as well as the UV delta parameter outside the timed loop.

COLLIER initialization capacity is `Nmax=max(N,2)` and
`Rmax=max(R,1,N-max(N-2,4))`, leaving requested ranks and outputs unchanged.
The N>=5 bound is the inherited public generic-interface BinomTable safeguard.
The N1 safeguard avoids upstream `SetIndCombisEq(Nmax-1,Rmax)` with N=0; the
rank-zero safeguard avoids `SetAddIndTab(0)` allocating zero entries then writing
entry 1. These are supported initialization-capacity arguments, not patches to
COLLIER or changes to the integral.

The internal monotonic wall timer includes the public tensor call, per-root
`InitEvent_cll`, invariant/routing preparation, native normalization and Cartesian
gathering, and the inherited error/finite scans. The scans are a small explicit
scope difference from the earlier TIRust table, whose post-call full-output
checks occur outside its timer. Initialization, warmup, separate pole probes,
transport, block snapshots and JSON I/O are excluded. COLLIER's scalar masters
remain included in its total; no fictitious phase decomposition is inferred.
Local memoization is reset for every root tensor call and no event cache is used.

For each row, a CHECK request, a warm three-call pilot and one calibrated BENCH
request are made. The single pilot chooses a fixed call count targeting 100 ms
per block, capped at 1,000,000. The BENCH request runs three warmup calls and
11 fixed blocks with the same count. Every block retains complete normalized
arrays and cumulative stability/error estimates; postflight CHECK repeats pole
probes and validates deterministic values. Failed status or agreement is retained
and makes the row ineligible even if it has raw timings.

The root process owns compilation, frozen binary/library/module hashes,
CPU pinning and the numerical quiet window. `run.py` accepts an already-built
binary and requires its expected SHA256 plus the explicit quiet-window note.
It never builds, imports a native Python extension or evaluates a TIRust integral.

## Reproduction workflow

From `/shared/external/iregi/iregi-rust`, source
`.local/tirust-current-toolchain-roots/env.sh` and `scripts/env.sh`. The root
controller links the driver against the retained COLLIER 1.2.10 static archive
with the retained strict optimized compiler flags, without upstream source
changes. The intended build product is
`target/reference/collier/opening-column-build001/collier-opening`. Use the exact
binary SHA256 from its root-owned build receipt, not a digest silently recomputed
to admit a changed binary. The root controller supervises the following command
as one process group, including its native children:

```sh
python3 validation/benchmark/opening-collier-20261026/run.py \
  --binary target/reference/collier/opening-column-build001/collier-opening \
  --binary-sha256 "$COLLIER_OPENING_BINARY_SHA256" \
  --output target/collier-opening-column-20261026/capture001 \
  --cpu 18 \
  --quiet-note 'Root-granted CPU18 numerical quiet window, opening COLLIER column'
```

`COLLIER_OPENING_BINARY_SHA256` is a task-specific variable populated from the
retained build receipt. The output directory must not already exist; preserve
each attempt and select a fresh named directory for any later investigation.
The runner does not retry failed rows. All stdout, stderr, wire requests, parsed
responses, per-block arrays and assessments are retained below that directory.
The publication records the root build/capture receipts alongside these source
files; copying a failed observation over an earlier one is not permitted.

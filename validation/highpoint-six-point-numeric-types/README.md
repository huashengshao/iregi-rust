# Private six-point numeric-type pilot

The complete DoubleFloat gate passes at the retained real massive scalar N6
point. The f64 positive lanes all fail cancellation guards. Float128 dynamic
Dual produces one successful affine singleton containing 24 complete Laurent /
Taylor slots, then exceeds its fixed work budget during the mixed batch.
Float256 dynamic Dual exceeds the fixed work budget before returning an array.
The full Dual schedules and paired precision convergence are **not qualified**.

| Domain | Available complete output slots | Full numerical gate |
|---|---:|---|
| f64 | 0 / 40 | Failed: 10 positive cancellation-guard rejections |
| DoubleFloat | 40 / 40 | Passed: 10 successes, 2 invalid controls and empty reset |
| Float128 dynamic Dual | 24 / 240 | Failed: incomplete schedule after affine singleton |
| Float256 dynamic Dual | 0 / 240 | Failed: no complete output before work alarm |

All 64 available output slots pass the independent original/analytic target
checks. Every one of the 1,736 represented input slots was independently checked,
including information at `2^-60` and `2^-120`. These facts do not convert missing
or rejected arrays into agreement. The three positive ordinary profiles have
one common primal point; the two formal Dual variables describe one physical
dilation direction. The nonlinear product-profile evaluation remains incomplete.

The isolated core/driver build took 35.644 s within its 90 s aggregate bound.
Four independent capture attempts took 68.568, 43.913, 164.436 and 164.160 s within
their respective 180 s aggregate bounds. The two failed Dual captures exhausted
the work deadline while retaining cleanup/postguard reserve. No bound was
extended, no attempt repeated and no new reference executed. All six owned
process groups were verified absent. These unoptimized qualification timings
include preparation and immutable-input checks; they are not kernel benchmarks.

`qualification.json` is an exact immutable snapshot of the producer's scoped
outcome. The two final independent audits recompute numerical inputs/results and
check the recorded source/native/tool/process provenance without importing the
producer. `timing-attribution.md` explains the limited timing information already
present in logs and identifies an existing exact-plan cache reuse API. It makes
no new performance measurement or promised speedup.

The compact `payload.tar.gz` preserves every changed/new source and raw terminal,
partial, failure, result, comparison and grant artifact. It overlays the existing
committed 81-member [source archive](../winddown/n6-numeric-types-dual.tar.gz),
whose exact hash/member inventory is bound in `manifest.json`; the unchanged
61-file core is not duplicated. Three Rust capture/jet/driver helpers and the
complete reviewed Python protocol are exactly reconstructible in a fresh clone.
The private README inside that reconstruction is the immutable pre-execution
snapshot; its later `RESULTS.md` records actual outcomes.

Run the portable checker from the project root:

```sh
source scripts/env.sh
python3 validation/highpoint-six-point-numeric-types/check.py
python3 validation/highpoint-six-point-numeric-types/check.py --reconstruct target/typed-n6-source-restored
```

The checker needs only Python's standard library and committed files. It
verifies archive and file inventories, reconstructs all 61 core files and 59
qualified original restorations, checks reviewed source bindings, and recomputes
all available saved scalar/scale-jet comparisons plus all exact input jets. It
imports no numerical library and executes no compiler, integral, reference or
benchmark. Reconstruction refuses an existing destination and writes no binaries.
The reconstructed old attempts remain immutable evidence, not authorization to
rerun them. Reproducing a new native execution still requires its actual reviewed
dependency/tool closure, a fresh protocol and appropriate root coordination.

Compiled ELF/rlib outputs and Python bytecode are omitted, with their recorded
hashes retained as historical metadata. No license literal is included. The
portable checker does not freshly requalify omitted native binaries, process
state, every linker-wrapper subtool or the operating-system/sysroot closure.

Child sensitivity/error imports remain primal-only. Partial derivative identities
provide no achieved derivative-error enclosure. No public Dual constructor,
arbitrary independent derivatives, static Dual, generalized N6 powers/dimension
shifts, higher rank, current-Cargo type qualification, production adoption or
performance parity follows from this capsule.

# Optional IREGI versus COLLIER reference comparison

This tooling compares **original IREGI with COLLIER**, independently of the
Rust-versus-IREGI performance gate. It does not link either Fortran library into
the Rust implementation. COLLIER 1.2.10 is GPLv3; source and download provenance
are recorded in `docs/research/collier-1.2.10-manifest.json`.

The initial vertical slice uses the exact existing massive N2/N3 rank0/1
inputs in `validation/benchmark/baseline-6b24c03-licensed/results-inputs.json`,
at batch sizes 1 and 32. These eight rows do not complete the user's requested
shared-domain benchmark. The current driver also accepts ordinary N4 and ranks
up to three, but those extensions require their own complete-array validation
before being reported as covered.

## Current explicit domain and conventions

- Unit positive propagator powers, ordinary `D=4-2epsilon`, four-dimensional
  Cartesian numerator moments. No dotted propagators or shifted dimension.
- Initially `N=2..4`, rank `0..3`; zero-origin routing, finite purely spatial
  real shifts, squared masses with positive real and nonpositive imaginary part.
  Positive internal masses ensure the initial rows have no IR poles.
- COLLIER COLI mode 1 is the default; IREGI hybrid mode 2 is recorded separately.
  These integers describe different library settings and are not identified.
- Public `mu` is squared before both COLLIER UV and IR scale setters.
- Native output order is `[UV single, IR single, IR double, finite]`, with
  finite `i*pi²*(COLLIER_finite-(EulerGamma+ln(pi))*COLLIER_UV)` and UV
  `i*pi²*COLLIER_UV`. IR slots are zero only within this explicitly IR-finite
  domain. See `convention-review.md` for the full IR adapter and finite correction.
- All requested symmetric Cartesian components are gathered in IREGI ordering;
  no multinomial weights and no extra odd-rank sign are applied.
- `CHECK` performs separate UV/IR delta-parameter variations for every lane
  outside the measured region. It checks returned UV against the UV variation
  and verifies both IR variations vanish. Independent scalar/vector UV
  identities test the native normalization and odd-rank sign.

Both engines retain local recurrence memoization within one sample. IREGI frees
its phase-space caches after each sample; COLLIER uses its local-only cache,
reset by each root call. No external/event numerical cache is enabled.

The COLLIER timer covers invariant and momentum-array construction, the public
full tensor call, native conversion and status/finiteness checks. The existing
IREGI timer covers mass-reference setup, its tensor call, status/finiteness
checks and cache disposal. Input parsing, initialization, pole probes, process
transport and output serialization are outside both measured regions. These
are callable tensor-kernel boundaries, not bare scalar-function timings.

## Reproduction

Run commands from `/shared/external/iregi/iregi-rust`. Source `scripts/env.sh`.
If CMake is not on PATH, provide its installed absolute path with `--cmake`.
The build copies the verified source inside the project and modifies only the
GNU release flags in its generated CMake file: `-O3`, no fast-math. Every command,
source, object, library and executable is hashed. The first attempt is capped
at 300 seconds and two build jobs; use a new attempt directory for every run.

```bash
python3 validation/collier-reference/build.py \
  --output target/reference/collier/build-attempt001 --cpus 26,27 --jobs 2 --timeout 300 \
  --cmake /path/to/cmake
python3 -m unittest discover -s validation/collier-reference -p 'test_*.py'
python3 validation/collier-reference/run.py \
  --build target/reference/collier/build-attempt001/build.json \
  --output target/collier-reference/correctness-attempt001 --cpu 26
```

Timing remains unrun until the root agent grants a project quiet window. Then
the runner requires the matching successful correctness receipt and an explicit
quiet-window note. It uses one pinned core, the same iteration count for both
engines, warm-up, randomized paired blocks, a 99% bootstrap interval and the
existing maximum 2% interval-width gate. It validates complete arrays in every
measured block and retains failed or unresolved rows. Correctness-run durations
are diagnostic and must not be copied into benchmark timing cells.

## Shared-domain progression still required

1. Qualify the eight initial rows and their pole/UV checks.
2. Extend massive undotted N4 scalar, rank1 and rank2 rows; include rank3 where
   practical. Validate tensor metric signs and complete Laurent arrays first.
3. Add N5/N6/N7 scalar, rank1 and rank2 with public `TNten_cll` and its exact
   cyclic invariant ordering. Reuse the conditioned high-point fixture and its
   retained cases. Its time component requires a separately reviewed relaxation
   of the initial purely-spatial gate. Positive internal masses still exclude
   IR poles; thresholds and ill-conditioning remain explicit failures.
4. Add representative higher ranks within both libraries' supported envelope
   up to the requested IREGI rank-seven limit. COLLIER's COLI branch is configured
   by `Init_cll(Nmax,rmax)` and has generic higher-point recurrences; independently
   check actual calls and resources before declaring a row supported. Its DD
   branch is explicitly limited to pentagon rank five and hexagon rank six
   (manual lines1694–1696 and `DD_global.F90:117–126`); do not use DD to assert
   rank-seven hexagon agreement.
5. Add complex masses and massless shared cases with separately validated
   branches and all UV/IR conventions. General IR rows need additional public
   delta-variation calls to obtain every Laurent coefficient; timing must expose
   that output contract, rather than replacing those slots with zero.

The table schema must list each requested topology/rank/batch family, including
unsupported, failed and unmeasured rows. A successful first slice, a source/API
review or a completed build does not qualify the broader envelope or numerical
performance parity. All new results feed the Typst report with their own source,
compiler, input, timing-policy and revision records.

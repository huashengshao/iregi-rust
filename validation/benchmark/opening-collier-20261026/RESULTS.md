# Published COLLIER column

The twelve ordinary inputs from the existing opening table were evaluated once
with COLLIER 1.2.10, COLI mode 1, binary64, on CPU18. The earlier TIRust inputs
and timings are unchanged. This is a separate absolute-time capture, not a
paired speed or equal-precision comparison. TIRust N5/N6 rows use Float128.

Nine rows through N4/rank6 pass the native status, complete-array `1e-10`
agreement, and outside-timer UV/IR pole checks. Their 3,864 distinct complex
Laurent coefficients are qualified. Three rows are rejected:

| Input | Native accuracy flag | Independent coefficient check | Observed duration, diagnostic only |
| --- | ---: | --- | ---: |
| N5, R5 | -1 | 11 finite mismatches; maximum normalized error `3.8833e-10` | 0.597 ms |
| N5, R6 | -1 | 62 finite mismatches; maximum normalized error `1.5052e-9` | 2.097 ms |
| N6, R6 | -2 | 195 nonfinite coefficients and one finite mismatch; pole checks fail | 3.293 ms |

Amber cells say **Rejected**. Their subordinate observed durations are not
successful reduction benchmarks and do not enter a speed ratio or aggregate.
These outcomes concern this input family, precision, policy and library
version. They are not a claim that the public integral API lacks those rows.
No retry, mode change, threshold relaxation or fixture change was made.

The native capture contains 132 timed blocks and 2,047,397 timed calls, plus
separate pole probes, a pilot and warmup. The independent audit examines all
6,048 distinct complex fields: 5,853 finite and 195 nonfinite; the finite
fields include 74 mismatches (11+62+1). It checks all 216 saved arrays and all
48 request wires. Early rejection by the producer's comparison is not counted
as zero mismatches in this independent accounting.

`capture001/` is a byte-identical archive of the original target capture. Raw
JSON retains its original target paths. The portable checker maps that prefix
to this archive and needs no native binary, compiler, library, license or old
target directory:

```sh
source scripts/env.sh
python3 validation/benchmark/opening-collier-20261026/independent_check.py
python3 validation/benchmark/opening-collier-20261026/summarize.py
```

`build.json` pins the reused, unmodified COLLIER archive, all28 module hashes,
strict optimized compiler flags, wrapper sources and frozen executable.
`supervision.json` records outer process-group cleanup and unchanged guards.
The campaign exits1 to expose the three retained numerical failures; every
native child exits0 and no process remains. `qualification.json` separates
the nine accepted rows from all three rejected rows. Working precision,
timing boundaries and recapture commands are detailed in `README.md`.

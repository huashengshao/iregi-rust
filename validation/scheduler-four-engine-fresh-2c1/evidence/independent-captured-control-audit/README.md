# Independent saved CONTROL audit

`check.py` is a standalone Python-standard-library audit of saved records only.
It does not import the producer admission code, load a numerical library, run a
compiler, execute a probe, evaluate an integral, or measure performance.

The audit binds the pinned `2c1f3342e189a20fef3bbf7dd9e0baa372e2b4a2`
isolated source context and the optimized captured qualification receipt
`0450b25c2a806c81f4410f567b370612f82401d9a322cb2f87d4115f53770232`.
It is independent of the concurrently modified project working tree.

The checker reconstructs the frozen Rust fixture constants and layouts itself,
then checks those against both `control-shapes.json` and actual responses. All
four CONTROL responses (baseline, candidate, and each one's repeat) must agree
as complete records. This includes values, exact represented rationals,
component precision, signed zero, errors, statuses, inputs, and execution
counters. The saved response bodies are not original-IREGI comparison evidence.

The result is **PASS: 42,964 assertions**, with 708 input hashes independently
checked before and after the audit:

- 67 direct-master cases, 133 rows: 106 successful and 27 explicit expected
  errors with null output. All 774 successful complex entries cover all six
  master slots and every represented derivative component.
- Three whole-core controls contain 80 tensor complex entries and 72 captured
  master complex entries. They cover a first-order dynamic f64 Dual, ordinary
  DoubleFloat, and ordinary Float256. The latter two preserve a core mass of
  `2 + 2^-53` exactly.
- The four cache reference contexts alternate ordinary and first-order dynamic
  Dual workspaces; all eight interleaved results equal their complete reference
  records, including observed master inputs and counters.
- Direct A0 controls preserve `1 + 2^-80` in DoubleFloat and independently
  varying 64/128/256-bit Float lane precisions under 128/256-bit prototypes.
  Their UV coefficients equal the exact input mass with the original precision.
  Scaleless B0 preserves cancelling `UV=1`, `IR=-1` instead of discarding poles.

**Coverage limit:** this 60-request runtime contains only dynamic Dual shapes
`[[0]]` and `[[0],[1]]`. It does not exercise static Dual values, higher-order
Duals, or mixed Dual derivatives. Earlier local scheduler tests provide separate
evidence for those cases; this audit does not relabel that evidence as runtime
coverage. Mixed Float precision is not mixed Dual differentiation.

`review.json` contains the per-case inventory, counts, source bindings, complete
before/after input hashes, and explicit scope limits. No timing, production
adoption, uncaptured executable, or independent original-IREGI qualification is
claimed.

Reproduction from the project directory:

```sh
source scripts/env.sh
python3 target/guard-performance-review/optimized-performance-proposal/independent-captured-control-audit/check.py
```

# Supplemental preflight CONTROL witness

`check.py` checks saved data only. It imports only the hash-pinned independently
authored primitives from `../independent-captured-control-audit/check.py`, never
the producer's validator. It never executes a compiler, probe, integral,
numerical library, bootstrap, or timing experiment.

The actual completed six-process preflight receipt is bound by SHA256
`10a8ca2bd11c881c353fb5cfda2944333c0f4adcf1cc2c09b4ac01700ac9be39`.
All 336 saved events are paired and counted. This supplemental witness audits
only the eight CONTROL replies at serials 65–68 and 165–168; the remaining
responses require the separate unified preflight audit.

Result: **PASS, 270,806 assertions and 838 before/after input hashes**. All four
TIRust roles' CONTROL records agree with the independently audited canonical
body, allowing exactly one change: capture-free binaries have empty
`master_captures` arrays at the fifteen frozen core/cache result paths. Every
other key and value agrees exactly. Each role's before/after CONTROL replies
also agree as complete records.

Each CONTROL reply contains 67 direct-master cases, 133 rows, 106 successful
rows, 27 explicit expected null-output errors, and 774 successful complex
entries spanning all six master slots and represented derivative components.
The three core controls contain 80 tensor complex entries. Captured roles also
contain 72 captured core master entries. Four cache reference contexts and all
eight interleaving steps retain exact full record equality.

Float/DoubleFloat precision, signed zero, and values beyond 53 bits are retained.
Dynamic Dual shapes here are only `[[0]]` and `[[0],[1]]`; static, higher-order,
and mixed Dual coverage must be reported from separate evidence.

No timing, original-IREGI numerical comparison, production adoption, or full
336-event numerical admission is claimed by this supplemental control witness.
The previous sealed reports are unchanged.

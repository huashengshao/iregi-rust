# Private v3 exact-contour regression

The unchanged five-pinch comparison source was rebuilt against the private v3 adapter archive. It reads the frozen independent exact Symbolica oracle in `target/near-vacuum-adapter/oracle/output.json`; no prior frozen file was changed.

At the exact contour point x = 1/2, with shifted squared masses 2 − i and routing scale eta = 2^-64, all five D0 rows returned complete order-2 finite certificates in one batched evaluation. The Float256 values and full rectangles satisfy the exact requested 128-bit mixed error budget against their independent oracle enclosures. The Symbolica-evaluated five-box contraction likewise satisfies that budget against the independently integrated J5^(D=4) oracle. All six independent oracle rectangles lie inside the corresponding candidate rectangles, and the final rectangle encloses the exact-coefficient linear combination of the five complete box rectangles.

The serialized result equals the prior adapter result apart from diagnostic duration. The CPU19 run exited successfully within the 60-second bound (1.418 seconds, 320240 KiB reported peak RSS). This concurrent correctness duration is not a benchmark.

`build.json` records the exact compiler command, source identity, linked archive hashes and captured private source hashes. `run.json` records before/after hashes and output/log hashes. The comparison source is unchanged; the linked external alias points explicitly to `libiregi_masters_certified_v3.rlib`. The retained Symbolica/oneloop dependency archives are private validation dependencies, so this does not qualify a build against the current workspace dependency stack. Library source-to-archive build provenance belongs to the parent's v3 library build record.

`audit.json` records a separate exact-rational arithmetic and provenance audit. This verification recomputes serialized bounds; it does not rerun Symbolica or any scalar master.

The fixture deliberately uses exact shifted inputs and exact Matrix-derived coefficients. It does not cover production geometry or mass-shift rounding, production Gauss nodes or weights, quadrature truncation, public E6 execution, Dual derivatives, or performance. Production source remains unchanged.

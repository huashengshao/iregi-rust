# Conditioned N6 temporal sixth moment

The six independently parameterized SciPy Jacobi rule evaluations give native
finite `(0, -0.05166894942216114)` for raw `q0^6`, zero-based component126 of the
rank-seven array. The numerator degree is six. The estimated absolute native
uncertainty is `7.780455047365738e-16`, or `3.1121820189462953e-15` after dividing
by the dimensional unit `U=1/4`. These empirical order/mapping and roundoff
estimates are **nonrigorous**; no interval certificate is claimed.

| Candidate / reference operand | Mixed error plus estimated uncertainty |
| --- | ---: |
| TIRust PV Float128 / independent oracle | 3.248856945702998e-15 |
| Original IREGI IBP / independent oracle | 4.273454476687555e-10 |
| Original IREGI Hybrid / independent oracle | 4.266824937506172e-10 |
| Original IREGI PV / independent oracle | native-rejected diagnostic |

The strict `1e-10` gate is unchanged. The original 330-moment/1320-complex-slot
array comparison remains failed. This component favors the saved TIRust value
against the original reference; it does not establish a cause or qualify the
other 329 moments, physical graphs, precision convergence, or performance. The
separate original-reference comparator argument order and denominator are also
preserved in `summary.json`; they are not silently exchanged with the oracle.

Symbolica performs the shifted-numerator binomial expansion, Gaussian-kernel
coefficient multiplication/extraction, and an exact-zero identity check in
exactly three CLI calls. SciPy supplies the existing Jacobi rules at orders
12/16/20 for identity/reversed simplex coordinates, totaling 8,994,816 nodes.
The reversed map changes only integration coordinates, not physical routing.
`Gamma(6)` is already in the Gaussian coefficients; the weights supply simplex
volume 1/120. The recorded positive-F bound is 15/16, so poles vanish and native
finite normalization is `i*pi^2` times the real OneLoop simplex integral.

The artifact archive retains exact final sources, root/peer reviews, both
unexecuted source drafts, the initial failed eight-test run, its exactSuccess
schema diagnosis, the freshly granted corrected eight-test pass, all three
Symbolica DOT/stdout/stderr tables and zero witness, all six numerical rule
outputs and statistics, saved raw native operands, and process/guard receipts.
All owned groups are gone. No compiled libraries, executables, Python bytecode,
license contents, or performance measurements are packaged. Historical
readiness/failed labels are preserved unchanged as chronological evidence.

The existing CLI binary is hash-pinned. Contextual preparation sources in the
archive do not claim a newly source-matched CLI build. The saved original data
and failed whole-array comparison are retained with their original hashes.
Reproduction commands and phase-specific root review requirements are included
under `target/temporal-sixpoint-oracle/commands.json` inside the archive. Earlier
failures and current successes must remain separate when reproducing them.

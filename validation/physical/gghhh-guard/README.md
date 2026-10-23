# Preserved ggHHH conditioning diagnosis

The frozen binary64 physical benchmark remains failed. Its canonical routing
contains a distance formed from two coordinates one binary64 ULP apart. The
exact represented-input invariant is approximately `-4.263256361592901292e-11`,
while its positive cancellation envelope is about `281249.993`. The existing
relative conditioning guard rejects that computation at 53 bits.

The same binary64 input components were promoted exactly, including four
negative zeros, and evaluated with the unchanged guard and requested accuracy
53. Working precision 128 reaches a later cancellation guard at `pv_node_852`.
Working precisions 256 and 512 succeed. All 70 moments × 4 complex Laurent slots
converge with maximum dimensionally normalized difference `2.173e-55`; the
contracted graph difference is `3.345e-57`. Full arrays agree with original
IREGI PV/hybrid to `4.617e-14`, and all three graph slots agree with preserved
MadLoop to `9.289e-14`, within the unchanged `1e-10` criterion. The known
original-IBP discrepancy remains recorded.

This validates one physical point through the full higher-precision CLI
pipeline. It does not test the library's automatic rescue wrapper or establish
performance parity. The binary64 timing rows are unchanged. Wall times include
preparation and have no benchmark qualification.

The initial 256-bit driver saved a successful numerical response before its
binary64-only comparison adapter rejected rational input strings. That producer
failure remains in `run.json`; the separate successful comparison uses the
original binary64 input metadata only for reference normalization. The 512-bit
driver uses the corrected adapter. Convergence compares complete textual
outputs at 200 decimal digits, without converting them through binary64.

`routing-audit.json` records the independent input/routing audit and source
hashes. `convergence.json` retains the full comparisons. `files.json` binds every
copied file to its original bytes; historical paths inside records are intact.
Executables are hash-bound and retained under `target`, not committed here.
These shell commands perform only artifact verification:

```sh
source scripts/env.sh
python3 validation/physical/gghhh-guard/verify.py
```

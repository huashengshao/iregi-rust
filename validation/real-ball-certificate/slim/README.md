# Slim RealBall certificate: isolated semantic qualification

The slimmer private candidate passes all 23 tests: seven baseline/candidate comparisons, eight existing certificate tests on the candidate, and eight baseline controls. Both independent source reviews found no correctness blocker. Production remains unchanged, and no performance measurements were made for this variant.

The candidate checks every argument and Taylor imaginary component once per call. All-complex active batches use the original ComplexBall mapping, packing, and direct output evaluation. Mixed batches evaluate complex lanes compactly, restore them backwards into their original slots, and then fill real slots from a Symbolica RealBall batch. Exact-zero/nonzero inspection, selected masks, precision budgets, diagnostics, and refinement remain unchanged. The same polynomial-only and real-coefficient instruction proof guards RealBall mapping.

The tests include 510 real/complex patterns through batch size eight with distinct exact residual centers, mixed-to-complex-only refinement, imaginary Taylor seeds producing a real mixed component, empty selected masks and repeated workspace reuse. Earlier profile results under the parent folder measure a different candidate and must not be attributed to this slim implementation. The remaining classification and slot-scan overhead, full reduction integration, and physical pipeline performance are unqualified.

The first build failed before compilation because the retained dependency inventory omitted `symjit`, whose Cargo target kind is explicitly `rlib`. Its logs and metadata diagnosis remain under `failed-first-attempt`. The successful retry uses the corrected complete-kinds closure and independently verified successful whole-workspace completion at revision `6b24c0372022e22606a1ac85f30c7fa579fb41f0`. Every one of the 865 retained Rust/native artifacts was rehashed before and after compilation and runtime. The closure's original pending status remains historical; `workspace-completion.json` supplies the separate completion binding. No shared mutable dependency search directory was used.

The source patch and both source snapshots are retained. The compiled executable and full dependency archives remain under `target`, bound by their hashes; their binaries are not committed. This qualification covers the certificate module, not a candidate replacement of the complete core library.

Verify retained source, logs, closure manifests, completed-library selection, and qualification without numerical execution:

```sh
source scripts/env.sh
python3 validation/real-ball-certificate/slim/verify.py
```

With the recorded dependency archives available, the original build and runtime scripts are retained under `qualified`. Numerical execution also requires sourcing `.local/symbolica-license.env`; the secret is not part of the evidence. Compilation used CPU12/13 and tests used CPU12, with one Rust test thread. There was no performance quiet-window claim.

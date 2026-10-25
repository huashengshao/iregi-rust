# Corrected standalone Python facade wheel

A fresh Linux CPython3.13 development wheel passes60 installed tests and consumer typing with zero errors or warnings. It links the actual shared Symbolica, Numerica, FeynKit and Spenso PyO3 classes and the public Rust `TensorReductionPlan`/`TensorWorkspace` facade. Its compiled default master backend is Symbolica.

Coverage comprises25 upstream numeric tests (six new native-operand precision regressions and19 existing Float/ComplexFloat tests),29 existing interoperability/numerical tests, four generic facade tests, one six-point rank-one frontend test and the existing seven-point scalar frontend test. The facade cases cover explicit Dual layouts, profiling, actual engine tags, packed batching, sparse contraction, invalid-lane isolation, empty/reset state, result snapshots and recovery.

The installed native reproducer confirms the upstream ComplexFloat correction: native integer multiplication retains128 imaginary bits even when the real component has two bits, exactly matching the explicit128-bit Float operand. Existing tracked operands and the minimum-component `.precision` property remain unchanged. The earlier trap wheel is retained separately in [facade-wheel-001](../facade-wheel-001/README.md).

Two initial upstream stages had24 passes and one historical trait-surface observer failure. Both raw logs, XML and failed receipts remain unchanged. The successful third stage only adds Rust-only `real_classify` and mutating `set_precision` to its existing exclusions; Python uses immutable `with_precision` copies. Numerical assertions, tolerances, wheel and environment did not change. Remaining runtime moved from CPU28 to CPU30 under an explicit affinity-only scheduling amendment.

The sources archive reconstructs the116 inputs owned at build time; post-build observer source changes are separately retained. The trait observer's Rust `float.rs` read was outside the original116 guarded build inputs: its post-observation copy is evidence, not a retrospective preflight guarantee. This is implementation context, not a complete compiler/native/system closure. Compiled wheel/native artifacts, environments, caches and credentials are omitted; their actual captured hashes and sizes remain recorded.

The six-/seven-point tests qualify frontend behavior on the specified retained positive-mass fixtures. They add no full-array reference or performance qualification, no public high-point Dual claim and no positive-rank seven-point work. The project qualification target is at most six propagators and rank six, including positive propagator powers and dimension shifts; seven-point and rank-seven challenges remain separately reported.

Run the portable stdlib-only saved replay from any directory:

```bash
python3 -I -S -B validation/python-interface/facade-wheel-002/check.py
```

It starts no native host, subprocess, compiler, integral or PID probe. The manifest binds both archives and the checker. All13 owned process groups, including the two failed observers, were recorded gone with empty cleanup errors by their original supervisors; replay checks those saved observations.

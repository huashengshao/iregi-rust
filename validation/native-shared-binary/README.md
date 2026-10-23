# Private shared binary-column candidate

This experiment is separate from the rejected dense-span and root allocator candidates. Production is unchanged. It lowers only two-operand Add/Mul instructions to a shared non-inlined batch kernel. Other instruction bodies stay unchanged. Operand order, exact constants, active lanes, parent stride and aliases are preserved. B0 uses existing `inline_add`/`inline_mul`; C0 uses existing `add`/`mul`, including DoubleFloat's commutative multiplication policy. No primitive is reimplemented.

The shared kernel dispatches positional column/constant operand categories once per instruction, then handles contiguous or sparse active lanes. Loop bodies are shared across DAG instructions. Span metadata follows the already reviewed entry/control/outlined-state invariant. Every operation finishes both operand reads before replacing a destination that may alias either source.

Baseline emission uses the frozen public emitter and the unallocated scalar expression graph. The comparison includes all six outputs and retains original helper/slot/branch provenance. All-type physical and guarded alias fixtures were tested in one combined binary. Source size, preparation, compile time and correctness are separate records.

## Measured outcome: rejected

All numerical qualifications passed, including 80 physical configurations (2,928 complex outputs), 108 guarded alias/outline configurations (8,568 outputs), and 720 direct operand/alias/precision configurations (95,040 active/inactive arena comparisons). Binary64, DoubleFloat and Float256 retain exact represented values, precision and signed zero. Mixed Float80/128/256 inputs and beyond-53-bit constants are included in direct kernel controls. Existing native/interpreter differences are reported separately.

The frozen combined binary was measured on CPU254 in the coordinated `optimization-quiet-20261023b` window. All-type checks before and after timing produced identical CSV and log hashes. Twelve paired timing groups yield one improvement, two parity, seven regressions and two noisy intervals. B0 homogeneous batch32 improves about1.1%, while its grouped/interleaved batches regress about2.2%/2.6%. C0 interleaved batch32 regresses about22.3%. Its grouped batch32 median is about23.7% slower, with the interval too wide for qualification. No row is discarded and no production change is adopted.

Shared dispatch avoids the preceding experiment's 2–3x machine-code expansion, but does not satisfy performance gates. Scalars are byte-identical, so singleton timing changes must not be attributed to the shared batch arithmetic. Native paired microbenchmarks do not establish original-IREGI or end-to-end reduction parity.

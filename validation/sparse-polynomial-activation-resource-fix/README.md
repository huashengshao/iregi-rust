# Sparse-polynomial and leaf-free activation preparation fix

The actual current default Rust core library compiled successfully in46.221s
and passed19focused exact-named tests in8.231s. Tests preserve the full21204-input
parameter layout, late-used symbols, complex mixed/second-order Taylor values,
exact zero-certificate selections, and leaf-free output/monitor alias contexts.
Ordinary with-leaf activation and the unchanged public N7 domain guard also pass.

Production changes use Symbolica automatic polynomial-variable discovery at
two conversion sites while retaining all declared evaluator inputs, their
order, and the original Taylor shape. The declaration boundary remains checked.
Scalar-master activation preparation returns immediately only for a plan with
no local scalar-master leaves; the ordinary with-leaf path is unchanged.

The independently reviewed patch and a separate test-only compile correction
are retained. The latter constructs the Atom coefficient explicitly and uses
Symbolica's existing exact ring evaluator for test expected values. Both
small/wide production Float128 evaluators still evaluate all three sample lanes
in a single batch. No custom polynomial or Taylor arithmetic was added.

Original failed preflight001 and test-only compile002 receipts are preserved,
followed by successful build003. No source/input guard failure, numerical
comparison or integral result is inferred from those failed attempts. The
old wide N7 preparation failure is preserved separately in
validation/highpoint-seven-point-fine-profile-resource-failure.

This capsule proves focused resource-correctness behavior, not successful
N7rank7 integrals, generalized/Dual full-interface acceptance or performance
parity. No new integral driver was run. The public N7 rank0 guard stays intact.
Root holds further long N7 captures while the accepted N6/rank6 full-feature
validation envelope, including dotted propagators, is completed.

No executable, cache or credential is bundled. The archive holds the336
selected actual source files; a complete system/native-link closure is not
claimed. Controllers retain original absolute paths for evidence lineage.
The small reuse-checks path clarification is ../references/gammaloop_feynkit/
crates/idenso/src/dirac/simplify/trace_kernel/collected.rs:107, confirmed using
automatic polynomial variables; this does not change tested code.

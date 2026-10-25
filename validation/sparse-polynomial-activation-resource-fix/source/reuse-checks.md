The polynomial conversion is an existing Symbolica operation, with no new algebra.

1. Symbolica API/source: `dependencies/symbolica/src/atom/core.rs` documents and implements `try_to_polynomial(&Q, None)`; `poly.rs` discovers variables when None and its polynomial representation stores dense exponent blocks.
2. Existing Symbolica usage/tests: `src/expand.rs` and `src/solve/solution_set.rs` use automatic polynomial variables. Reconstruction and absolute coefficient mapping remain Symbolica methods.
3. FeynKit/gammaloop equivalents: `references/gammaloop_feynkit/gammalooprs/src/momentum/mod.rs` uses automatic polynomial variables; FeynKit parametric conversion specifies a map where ordering is required. Here only intermediate zero-exponent axes are removed; all original evaluator inputs, order and Taylor shape remain unchanged.

The leaf-free activation shortcut performs no algebra: without local scalar leaves there are no activation roots or required activation aliases. Existing with-leaf behavior is unchanged and remains covered by active/inactive and conservative master-dependent activation controls.

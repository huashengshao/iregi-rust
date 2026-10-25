# Pinned Symbolica source for iregi-rust

This directory retains Symbolica, Numerica, and Graphica from upstream revision
`9cdc2949cdb153478c1eca0d40690dc0abfc616e`, with the five patches recorded in
`../symbolica-patches/provenance.json`. `IREGI_PROVENANCE.json` lists all retained
upstream/patched files, their hashes, and omitted assets. Upstream `License.md`,
`Readme.md`, and license implementation are unchanged.

The conditional-cache patch replaces repeated cache copies with reversible
branch-local insertions. The second patch sets an explicit source-version
display label. The third avoids Git-metadata rebuild triggers when that explicit
label is used. The fourth validates polynomial exponent bounds against the
existing signed conversion, avoiding wraparound for compact oversized powers.
The fifth retains dominating zero/nonzero facts for the exact same SSA condition
inside its selected branch, pruning unreachable repeated conditional arms.
Numeric condition values, sibling/function scopes and lazy singular branches are
preserved. These patches do not change algebra rules, arithmetic operations,
precision types, or license checks; the fifth changes generated control flow.
Its 18 focused evaluator tests do not by themselves qualify integral arrays or
performance. Patch rationale and validation limits are documented
in `../symbolica-patches/README.md`.

All Rust test, example, and benchmark source targets are retained. Large
upstream benchmark fixtures are omitted; the optional `slow_fac_operations`
benchmark needs these assets restored from the pinned revision. Retained Rust
sources do not use `include_str!` or `include_bytes!` to load omitted files.
Normal library and test compilation does not need the omitted fixtures.

From the iregi-rust project directory, reproduce this retained tree with:

```sh
source scripts/env.sh
python3 scripts/prepare-symbolica-patch.py --vendor \
  --output target/symbolica-vendor-reproduced
```

The generated output is verified against this directory's inventory. Omit
`--vendor` to restore the complete patched upstream source instead.

## Python complex native operands

Patch6 fixes confirmed loss of a high-precision complex component when the
other component has lower precision and a native Python number is used as an
operand. Native operands now use the larger component working precision.
Existing Float/ComplexFloat operands retain their own precision; the public
minimum-component precision property is unchanged. All arithmetic remains in
Numerica. Six focused regression tests are included. Source/API review passes.
The corrected fresh wheel passes all 60 numerical/interoperability tests and
installed typing. Two failed historical trait-surface observations are retained;
the observer now excludes Rust-only `real_classify` and mutating `set_precision`.
Python floats retain read-only precision and immutable `with_precision` copies.
See `validation/python-interface/facade-wheel-002` for exact source/artifact scope.

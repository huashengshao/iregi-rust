# Pinned Symbolica source for iregi-rust

This directory retains Symbolica, Numerica, and Graphica from upstream revision
`9cdc2949cdb153478c1eca0d40690dc0abfc616e`, with the four patches recorded in
`../symbolica-patches/provenance.json`. `IREGI_PROVENANCE.json` lists all retained
upstream/patched files, their hashes, and omitted assets. Upstream `License.md`,
`Readme.md`, and license implementation are unchanged.

The conditional-cache patch replaces repeated cache copies with reversible
branch-local insertions. The second patch sets an explicit source-version
display label. The third avoids Git-metadata rebuild triggers when that explicit
label is used. The fourth validates polynomial exponent bounds against the
existing signed conversion, avoiding wraparound for compact oversized powers.
These patches do not change algebra rules, numerical operations,
precision types, or license checks. Patch rationale and validation limits are documented
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

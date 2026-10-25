# Pure ABI metadata admission helper

`provenance.py` launches nothing, reads no files and changes no state on import.
The bounded build owner extracts metadata from the actual fresh archive using
the pinned compiler, saves its terminal/cleanup evidence, then supplies that
saved text to the helper. Archive/metadata/source/toolchain byte guards remain
the caller's responsibility. ThinLTO's omission of archive paths from a link map
cannot replace this identity proof.

The accepted lower proof is the completed `lower-admission-inputs.json`, SHA256
`2795e02bb2032578d168eb2a440cf662716885641274a72e354071cf14556399`.
It has108 actual originally guarded lower roots and19 NEW full sysroot `.rmeta`
root observations,127 total. The original stub `.rlib` decoder failure remains
separate and is not relabelled passed. All2416 supporting metadata edges close
against the127 lower and four observed project roots. No numerical qualification
or build success follows from this saved-data proof alone.

Typical bounded caller sequence, after independently pinning the proof bytes:

```python
lower = provenance.lower_from_proof(proof)
requirements = provenance.binding_requirements(proof)
# Bounded owner must actually hash all288 returned file declarations here,
# plus the proof, helper, current commands/sources and actual fresh outputs.
actual = provenance.parse(saved_metadata_text)
admission = provenance.admit(
    actual,
    expected_root_name="iregi_rust",
    allowed_lower=lower,
    required_fresh={
        "symbolica": actual_same_variant_symbolica_metadata,
        "oneloop": actual_same_variant_oneloop_metadata,
        "iregi_masters": actual_same_variant_masters_metadata,
    },
)
```

Required project roots are complete expected transitive predecessor sets, not
just the last direct predecessor. Symbolica has none; OneLoop needs Symbolica;
masters needs Symbolica and OneLoop; core needs all three. Passing complete
predecessor metadata additionally verifies inherited transitive identity edges.
Passing exact hash strings is supported when the bounded owner already admitted
and retains those records. Fresh root names must be the exact plain four project
names. Every unexpected project alias/hash and every unknown lower identity is
rejected, along with duplicate rows, missing required predecessors and hash/name
collisions. Distinct versions of one lower package remain distinct allowed
display names and must each have their own observed crate hash.

The strict parser recognizes the pinned compiler's ordinary dependency rows and
the observed sysroot `linkage Some(RequireStatic)` tail. Unknown format changes
fail rather than silently discard a row. Metadata crate hashes retain their
actual variable-length Rust spelling; they are not artifact suffixes or SHA256s.

`test_provenance.py` checks saved metadata and file hashes only. The latest
`provenance-pure-tests.json` reports127 lower roundtrips, four observed project
archive admissions,288 actual declared file hashes checked and30 meaningful
negative cases. No compiler, integral, executable or benchmark subprocess is
launched by either helper or saved-data test.

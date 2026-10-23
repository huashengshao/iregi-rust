# Compile and source-typing checkpoint

This capsule qualifies source compilation and an actual typed consumer against
the source stubs. **It does not qualify numerical runtime behavior, an installed
wheel, notebook execution or a complete Symbolica Community host.** The first
native wheel was still building when this capsule was frozen.

The final owned-crate Cargo check passed in 1.619 seconds after the documented
font/data setup and DoubleFloat transport changes. The initial full dependency
check reached its 600-second cap; one same-command incremental continuation
passed in 379.677 seconds. All three receipts and complete compressed logs are
retained. These durations describe build checks, not numerical performance.

The actual consumer uses the real Expression, TensorExpression, Float, Model and
reduction API aliases. Its final basedpyright check reports zero errors and zero
warnings. Earlier path-configuration failures, the upstream mypy internal error,
and premature pre-wheel collection failures are retained explicitly.

`sources.tar.gz` contains source/manifests and typed declarations, with exact
inventory in `sources.json`. It excludes compiled objects, font binary assets,
virtual environments and license credentials. The rendering manifest is present
as source provenance; 18 packaged font source payloads were separately compared
with the actual generated upstream Rust expectations.

`qualification.json` binds every receipt, original/decompressed log, shared owner
identity, source archive and limitations. Existing numeric source pins were kept.
Only the new optional Python/native rendering dependency closure was added.

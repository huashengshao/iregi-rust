# Narrow PV coefficient oracle after planar chart refactor

All20 cases passed: N=1..5, moments throughrank2, base/translated/propagator-order-reversed/loop-reversed routing. The complete15×4 complex Laurent tensor outputs were checked in each case at dimensionally normalized mixed1e-10 tolerance.

The Rust side evaluates exact numeric-specialized Symbolica PV coefficients using original Fortran scalar master values. The reference side is original IREGI IBP. This checks the chart/compiler refactor, not the public Rust Workspace or native master backend.

The frozen clean candidate binary is bound through the parent adoption bundle. The supervisor backed up exactly20 generated oracle paths, removed those paths during the test to avoid stale-output acceptance, captured every fresh result, and restored original bytes in a finally block. Every original hash was rechecked. The report agent held reads during this short interval.

The original combined rank-seven Dual timeout and the successful separate full-array comparator remain in their own linked evidence bundles. This oracle does not supersede either record.

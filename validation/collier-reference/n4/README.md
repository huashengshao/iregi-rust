# Fixed-input N4 correctness extension

The eight retained rows are ordinary massive boxes at ranks 0–3, with batches
1 and 32. Inputs and the `1e-10` comparison tolerance are unchanged across all
attempts. This extension has **no timing results**. The earlier N2/N3 benchmark
producer and its measurements are unchanged.

The durable current record is [diagnostics-v1/summary.json](diagnostics-v1/summary.json),
with compressed complete outputs, source/input snapshots and bindings in
[diagnostics-v1/qualification.json](diagnostics-v1/qualification.json).
Only two scalar rows pass both the native COLLIER status gate and the complete
IREGI comparison. All six rank 1–3 rows retain COLI mode 1 `AccFlag=-1` and
remain rejected. The raw arrays agree numerically at the external tolerance,
but that diagnostic agreement cannot override their library status. DD mode 2
returns `ErrFlag=-10` on all eight rows and supplies no qualified comparison.
This is incomplete coverage, with failed rows visible.

A subsequent source-only review gives an **inferred explanation**, not a
captured internal branch trace. The exact upstream source is
`target/reference/collier/source/collier-COLLIER-1.2.10/src/DDlib/DD_4pt.F`,
SHA-256 `6ff001947c81af4156440b79b9f97d00c59bcbb5141ddf89f363a84cc41cb48b`.
In `D0massive_dd`, lines 4448–4498 require positive real Euler-transformation
discriminants and set `stopflag=-10` when a complex shift would be required.
The beta(2) discriminant at lines 4476–4485 is
`(q1+q2-q12)^2-4*q1*q2`. Conditional on the actual routing
`q1=p1^2`, `q2=(p2-p1)^2`, `q12=p2^2`, it is a Gram discriminant that is
strictly negative for noncollinear, purely spatial p1 and p2, as in this
fixture. The source requires checking those routing and noncollinearity
conditions before extending this inference to another case. This supplies a
sufficient unsupported condition without changing the inputs or library.
The source explanation is separate from the frozen rejected outputs and does
not qualify them.

`AccFlag=-1` means that the requested relative accuracy `1e-12` was not reached;
`-2` would mean that the critical `1e-10` accuracy was not reached. These flags
are cumulative over calls since the event reset. Optional tensor estimates
are absolute errors, so their small magnitude does not override the relative
accuracy flag. See upstream manual lines 2724–2740 and
`collier_init.F90:2528–2537`. The error flags and acceptance thresholds were
not relaxed. Rejected moments are returned only in a separately labelled
`diagnostic_moments` field, while the accepted `moments` field stays null.

`diagnostic-driver.f90` adds flags, absolute estimates and rejected raw arrays
to the original driver. ROOT reviewed the exact source before relinking it
against the immutable existing static COLLIER archive. The link took 0.867 s;
the library was not rebuilt. Successful outputs for all initial eight N2/N3
rows and their pole probes are exactly identical to the original executable.
The fixed-input N4 diagnostic took 2.124 s. Both `BENCH` and `CHECK` reject the
higher-rank COLI lanes, so auxiliary pole probes do not cause the rejection.
The internal timing fields of these diagnostic requests are not performance
evidence.

Independent checks use the existing Symbolica CLI to prepare 238 polynomial
numerators and exact coefficient arrays. They cover every native Laurent
slot of rank-two and rank-three metric traces, translated pinch-zero routing,
odd-rank denominator differences, time reflection and UV finiteness. All
eight IREGI rows pass; raw rejected COLI values pass only as labelled
diagnostics. These checks constrain the specified traces and routing
relations; they do not independently determine every spatial tensor
component. Complete-array comparison is separate and retains all six rejected
higher-rank COLI rows. The finite-dimensional trace caveat is derived in
[collier-n4-identities.md](../../../docs/research/collier-n4-identities.md):
the omitted epsilon times six-dimensional scalar/vector box has no pole on
this massive Euclidean domain. Rank four is excluded from that argument.

The source-guarded original attempts are retained under `history/`, including
the initial diagnostic-loss failure and its separate evidence-preservation
repair. Additional diagnostic startup failures and the first spelling error
in the diagnostic runner are retained in the current package. No failed
attempt has been replaced by a successful receipt. The 12 protocol regressions
pass, including preservation of complete failed qualification responses.

Reproduction from the project root, after `source scripts/env.sh` and loading
the Symbolica license environment:

```sh
python3 validation/collier-reference/n4/build_diagnostic.py \
  --output target/reference/collier/n4-diagnostic-build-NEW \
  --review validation/collier-reference/n4/diagnostic-driver-root-review.json
python3 validation/collier-reference/n4/diagnose.py \
  --build target/reference/collier/n4-diagnostic-build-NEW/build.json \
  --output target/collier-reference/n4-diagnostic-NEW --cpu 26
python3 validation/collier-reference/n4/check_identities.py \
  --diagnostic target/collier-reference/n4-diagnostic-NEW/results.json \
  --output target/collier-reference/n4-identity-NEW --cpu 26
python3 -m unittest discover -s validation/collier-reference/n4 -p test_protocol.py -v
```

The link is capped at 60 s. Each diagnostic/identity capture is capped at
120 s. Use new output directories; preserved evidence is never overwritten.
The package script is specifically bound to the retained original attempts
and runs no kernel. A new performance cohort would need a complete acceptance
receipt, an independently reviewed frozen producer, and a separate quiet-window
grant. No N4 timing gate is currently satisfied.

The earlier identity-attempt001 accidentally inventoried an absent
`crates/iregi-graph` directory. Its receipt and producer remain in the package.
The correction to `crates/iregi-prepare`, with an explicit note that current
source inventory is contextual rather than a new source-matched CLI build,
was rerun as identity-attempt002 before packaging the final identity record.
That final run took 1.863 s; its executable hashes, prepared artifacts and
source guards are bound separately from the preserved earlier context.

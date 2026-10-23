# Third candidate: safe initialization and unchanged mixed-scale transport

Source candidate only. All earlier attempts stay immutable and visible. The
separately checked upstream-object diagnostic established a generic entry-point
array-bounds violation at `collier_tensors.F90:5896`: N6/rank0 initialized the
binomial table only through column4, but the entry point reads column6. The
receipt and full runtime error are retained under the low-rank diagnostic.
This identifies a real setup defect; it does not identify every memory write
that caused the original unchecked heap abort.

This candidate uses the official `Init_cll` capacity argument. For N>=5, its
minimum capacity is `max(requested_rank, n-max(n-2,4))`, because upstream sizes
the table through `capacity+max(n-2,4)`. All tensor allocations, tensor calls,
returned Cartesian counts and error arrays keep the requested rank. N<=4
initialization and dedicated B/C/D calls remain unchanged. The initialization
capacity is explicit in each response and validated by the Python adapter.
No upstream library source, library archive, threshold, fixture, accuracy gate,
pole conversion or tensor-reduction method changes.

Each reference input list is partitioned by its exact canonical rational scale.
The complete original sample objects, including all shifts and masses, enter
each wire request unchanged. Each response is retained before validation. The
adapter gathers every lane and pole probe into the original order; it rejects
missing, duplicated, mutated or differently configured groups. Group timings
are diagnostic only, explicitly ineligible for performance evidence. A later
kernel benchmark needs its own reviewed same-input transport policy.

Every engine/mode/scale-group request starts a fresh child. A failed or aborted
process is retained with its stderr and exit code and cannot poison another
policy or family. No request is retried. Even if one engine fails, the other
requests for that fixed row are attempted within the global resource cap.
The frozen16 N2/N3/N4 interface regression rows must all still pass before any
higher-point call. The six retained N4 accuracy rejections must remain rejected.

The first full capture remains the exact17-family/34-row matrix, original
IREGI Hybrid/PV/IBP and COLLIER COLI/DD policies. Scale grouping increases the
maximum transport request count from202 to247. It does not create new sample
branches: each higher-point batch32 cycles the same three retained samples.
Reuse the unchanged304 Symbolica-prepared constants and105 exact positive
Feynman-polynomial witnesses, binding their original preparation.

Before numerical execution, independently review all six source files and run
the18 meaningful protocol tests once. The proposed next numerical step is a
driver-only optimized link against the immutable archive (60s cap), followed
by the full isolated correctness capture (120s global deadline,20s per request,
at most5s finalization;135s outer cap), CPU26. No timing cohort is proposed.
Any resource limit, native rejection, disagreement or transport failure remains
visible and prevents that row from being qualified.

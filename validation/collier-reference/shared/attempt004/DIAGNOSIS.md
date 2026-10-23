# Safe generic initialization; all fixed rows retained

The19 protocol tests and the actual32-response legacy-header audit passed.
The driver-only link used the unchanged optimized COLLIER archive. All16 fixed
N2/N3/N4 interface regressions passed, including preservation of the six N4
COLI accuracy rejections. The run reserved only the minimum initialization table
capacity for generic N>=5 calls; requested tensor ranks and output arrays were
unchanged. No further heap abort was observed.

All34 rows remain visible. Within the120s request deadline and135s outer cap,
239 isolated scale-group requests returned validated responses. Eight requests
were not started after the deadline. Capture/bookkeeping completed in122.797s
with all source/input/binary guards unchanged. No request was retried. The final
N7/rank2 batch32 row contains its complete Hybrid result; PV, IBP, COLI and DD
each lack both original scale groups. It is resource-incomplete, not evidence
of a numerical failure for those eight unexecuted requests. The raw row's broad
`failed-or-rejected` label is supplemented by `resource_incomplete` in summary.

There are17 admitted COLI comparisons: the ten retained old rows, all six new
N5 ranks0/1/2 singleton/batch32 rows, and the N6 rank0 singleton. New admitted
complete Cartesian/native Laurent comparisons have maximum normalized errors
4.757461366865231e-12 (N5) and2.5922501379268064e-13 (N6 scalar). Their scale
groups preserve all original mu=3/6 samples and original lane order. These
agreements are pending independent durable-package audit and further routing
and trace identities; no new performance measurement is claimed.

The remaining actually executed higher-point COLI rows retain native accuracy
rejections. N6/N7 COLI flags include-1/-2, and higher-point DD returns its native
ErrFlag=-10. Original IREGI modes also expose failures or disagreements on the
unchanged conditioned families: PV rejects some N6/N7 lanes, and the N6 rank2
mass-deformed rows have large finite-term IBP/Hybrid disagreement. These are
retained independently of COLLIER's results and cannot enter timing gates.

The original attempt002 N5/rank0 call used the subsequently diagnosed unsafe
binomial-table capacity. Its old raw numerical agreement remains preserved but
unqualified. This new setup does not retrospectively qualify those old bytes.

The package preserves198 assembled responses, every239 complete group response,
all247 planned group attempts, raw rejected diagnostics, stderr, original input
preparation, strict source review, protocol tests, and the outer-cap receipt.
No Rust implementation, dependency, upstream library or accuracy threshold
changed, and no timing cohort was run.

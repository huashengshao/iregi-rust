# Dispatch witnesses and the next tensor rank

The independently reviewed rank-one package remains unchanged. The additional
v4 exact test build/run passed five tests, including twelve actual `moment()`
dispatch cases and 48 independent nonzero Laurent-slot identities. Wrong-rank
child sentinels distinguish rank lowering from same-rank pinching, and the test
also covers the unchanged rank-zero path and structural fallback. This is exact
recurrence routing evidence, not integrated rank-seven numerical evidence.

The unchanged private public candidate was then run at N6 rank two, Float128,
requested53, on the same retained base fixture. It finished preparation and
entered numerical reduction, then rejected the lane because of nonfinite
reduction coefficients. The bounded run lasted 57.823 seconds against a
180-second cap. No tensor values are accessible through the failed lane.
`n6-rank2-rejection-qualification.json` records this as a captured rejection,
with numerical agreement and complete-array flags false.

The specific nonfinite denominator has not been instrumentally localized. The
fact that rank lowering still reaches tensor pentagons motivates the separate
source-only child-dispatch assessment. No longer timeout, rank-seven retry,
global coordinate-identity flag, conditioning threshold change, or child
dispatcher implementation was introduced.

# Private v3 adapter policy and scheduling contracts

The frozen contract driver uses binary64 with requested40 context metadata.
Its ordinary fallback results remain explicitly uncertified; this test does
not convert requested_bits into an ordinary-formula accuracy claim.

The first fixture has the native-valid one-variable shape [0,1,2,3,4,5].
This is the smallest ancestor-closed shape outside the candidate's degree-four
limit. All six invariants are zero and all four squared masses equal one.
One valid lane has mu_squared=1+t, another has constant mu_squared=1. The
mathematical finite result is 1/6 and every higher coefficient and pole is
zero. The other lanes contain an upper-half-plane mass and an invalid scale.

RequireFiniteCertificate must hide every unsupported-shape value and must not
prepare any series. AllowOrdinaryUncertified must evaluate only the two valid
lanes, preserve the original physical failures, return no finite certificate,
and label successful rows OrdinaryUncertified. Every component in each of
five exposed Laurent arrays is compared bit-for-bit against the original
ordinary evaluator, including signed zeros. The two mathematical zero-jet
identities and rounded 1/6 primal are also checked. Empty and reordered batches
are checked. The first expensive step is preparing the ordinary general D0
fifth-order program, before adapter dispatch sees constant physical inputs.

The second fixture repeats the previously validated ordinary primal box
p=[0,-4,-4,0,0,-4], m_i_squared=2-i, mu_squared=1 three times. Its exact series
eligibility bound is rho=3/4. Both policies perform only the N2 eligibility
attempt, with zero active numeric/enclosure/tail rows and prepared orders
exactly [2]. N4 must never be prepared. Require hides values; Allow returns
ordinary uncertified values exactly matching every legacy Laurent component.

The bounded CPU19 run exited successfully within 60 seconds. See contract.json,
contract-run.json, contract-build.json, and contract.log for results, progress,
and hashes. The concurrent correctness run's wall time and memory are
strictly diagnostic. No production files or prior frozen artifacts changed.
Positive N2-to-N4 refinement is covered by the parent's separate regression
runs, not by this rejection-policy fixture. This checkpoint does not qualify
new general kinematics, derivative accuracy, E6 integration, or performance.

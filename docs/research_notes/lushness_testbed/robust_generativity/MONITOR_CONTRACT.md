# Neutral depth queries — engineering contract v1

The physical state is `(e,r,A,B,C,D)` and is the **only** state used for
lushness. The following sparse lifts survey native reaction mechanisms. No
monitor flag, event ID, generation label or detector reset adds entropy.

## Initial-seed witness (five states)

| Query state | Qualifying next native event | Update | Other physical changes |
| --- | --- | --- | --- |
| Waiting | `paid_assisted_A_to_B` with A=1,B=C=0 | Link 1 | Retain waiting only while A=1,B=C=0; otherwise permanent failure |
| Link 1 | `paid_assisted_B_to_C` with B=1,C=0 | Link 2 | Retain link 1 only while B=1,C=0; otherwise permanent failure |
| Link 2 | `paid_assisted_C_to_A` with C=1 | Success | Retain link 2 only while C=1; otherwise permanent failure |
| Success | Any event | Success | Physical process continues |
| Failure | Any event | Failure | Physical process continues; never restart |

The guards apply to pre- and post-event states. Bank/packet changes leave the
guard alone. A may change after link 1 because the newly made B is then the
unique parent; B may change after link 2 because the newly made C is then the
unique parent. A basal or thermal birth cannot substitute for an assisted link.
Assisted and basal channels are declared native mechanisms with distinct
catalytic dependencies; splitting one native channel's labels has no effect.
An ineligible initial frame is marked ineligible/failure, never interpreted as
evidence that it cannot compound. This is a conservative model-relative causal
certificate, not recovered atomic genealogy.

Each physical event advances `(X,m)` to `(X',m')` with its original rate. For
projection S from query states to physical states require `Q_query S = S Q`.
This identity is checked across every query phase, including unreachable ones.
Native channels with the same physical endpoint are aggregated in physical Q.

## Any-start detector (three states)

Waiting scans for the link-1 event from the same eligible A=1,B=C=0 frame.
Link-1/link-2 guards match the primary witness. An ambiguity or completion
returns to waiting. A completion increments a query-side reward by one. The
event that ended an attempt cannot start another; completed chains do not
overlap inside this detector. Unlike the primary witness this detector restarts,
and is always labelled separately.

The expected integrated completion intensity divided by elapsed physical time
is a lower-bound **detected-chain rate**. It is not full genealogy, not a
population generation rate and not necessarily informative in dense productive
states. Report forward/reverse link fluxes, births, losses and retained growth.

## Disruption and joint queries

The prescribed pulse removes one B into precursor, with no-op when B=0, and
releases one unit of stored energy per removed B. Pending queries are updated
with the same physical guard rules; success/failure flags remain permanent.
There is no pulse clock in the physical state.

Strong initial-seed event: success by startup 64 AND loop present then AND
expansion at 256 AND no graph-defined loop closure. The actual graph-closure
set is absorbing, so exclusion at the final checkpoint also excludes prior
entry. Apply checkpoint masks to unnormalized probabilities; never condition
away startup failure. After a pulse, propagate the selected subensemble under
the physical generator. Recovery separately reports pre-function probability,
pre-function AND endpoint restoration, and its conditional ratio.

Removing a required assisted channel tautologically removes this detector's
certificate. Independent ablation evidence must concern physical loop arrival,
retained expansion, capture or recovery, rather than just that disappearance.

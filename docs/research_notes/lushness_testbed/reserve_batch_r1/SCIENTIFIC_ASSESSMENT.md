# Scientific assessment: reserve-sensitive control

All nine frozen cases completed: 198 declared policy evaluations, representing
162 distinct kernel/ledger evaluations across the cases. Each world has 2,560
states. Total charged execution was 1,190.55 seconds (19.84 minutes), below the
3,600-second batch budget; individual jobs stayed below 600 seconds and 1 GiB.
The largest recorded peak was approximately 519 MiB. Source/case manifests were
verified, and compact results retain aliases and numerical ties.

The primary objective remains complete sampled-state conditional history entropy
at each horizon. Rates and offsets are secondary diagnostics. Neither protection
nor reserve stock was added as a reward; all native randomness counts.

## Primary results

At cadence 0.25, the winning stationary policy selected for each horizon was:

| Law | T1 | T4 | T16 | T64 | T256 |
|---|---|---|---|---|---|
| No shocks | Export | Mix75 | Mix25 | Reserve-3/Mix25 | Service |
| Independent, h=0.02 | Export | Mix75 | Mix25 | Service | Service |
| Correlated, h=0.02 | Export | Mix75 | Mix25 | Service | Service |
| Independent, h=0.04 | Export | Mix75 | Mix25 | Service | Service |
| Absorbing damage | Export | Mix75 | Mix25 | Reserve-3/Mix25 | Service |

Mix75 means 75% export and 25% service; Mix25 means 25% export and 75% service.
Reserve-3/Mix25 services below three active units and mixes at three. Reserve
adaptation is expressible only in the left compartment: the right has one slot.
These are stationary policies chosen against different horizons, not adaptive
receding-horizon agents.

The anticipated reserve-sensitive advantage under shocks failed in all 15
registered law/horizon comparisons. Doubling independent hazard or replacing
independent shocks by fully correlated shocks did not change the winning response
at any registered horizon. Longer horizons increased the winning service response
in 17 of 20 adjacent comparisons, with three plateaus and no decreases. Thus the
horizon effect is strong, while the strict risk/correlation adaptation predictions
are unsupported within this family.

The absorbing sentinel had less working stock at the common T64 deadline than
the no-shock comparator at all five optimization horizons. This failed the stock
prediction. It compares different physical laws and does not isolate a preference
for destruction. Stationary exposure fell rather than rose with doubled hazard;
the registered exposure-increase diagnostic did not fire.

## Finite gains, margins and temporal sensitivity

Without shocks, Reserve-3/Mix25 beats constant service by 1.232658 bits at T64,
about 2.35 times effective breadth, while retaining slightly less working stock
(1.322734 versus 1.344372). In the absorbing world its gain is 1.098239 bits,
about 2.14 times breadth. T64 closure probability is 1.274975% versus 1.245663%
under constant service. The finite gain therefore trades a small additional risk
for breadth. By T256, constant service wins in both worlds.

The absorbing world's short-horizon export winner has 2.493837% closure probability
by the same T64 deadline, versus 1.245663% under the long-horizon service winner.
This supports a horizon-dependent protection trade-off without making maximum
protection the objective.

No certified positive/negative reversal occurred in the preregistered fixed-control
cadence comparisons. Nevertheless, overall T64 winners change with cadence.
An exploratory comparison exposes a genuine reversal: no-shock Reserve-3/Mix25
minus constant Mix25 is +9.277903 bits at cadence 0.125, +4.153421 at 0.25, and
-0.581910 at 0.5. This pair was outside the registered comparator set, so it is
reported as exploratory temporal sensitivity, not a retroactively registered hit.
Cadence testing does not establish robustness to state grain.

## Implications and next model boundary

Longer complete-continuation horizons can make maintaining the channel pay without
a semantic protection bonus. They do not yet produce the predicted risk-sensitive
reserve policy. The small intermediate-horizon threshold gains are not a robust
basis for identifying criticality or ethical adequacy. Rate-optimal constant service
also misses these finite gains, illustrating why rate is not the headline objective.

The controls are coarse count-state ensembles, not a microscopic gas. Apparatus
channels are not established valuers; the capped population is not open-ended
compounding. These tests are exhaustive only within the frozen candidate family.

The separate maintained-resource result supplies a positive access/throughput
mechanism, but downstream use does not sustain its enabler. A prospective expansion
should couple resource use to costed regeneration/construction and distinguish
repairable functional damage from irreversible loss of material or capability.
That is a new physical model question, not a post-result adjustment to these cases.
Independent controller subjects and appropriation remain subsequent experiments.

See [automated results](report/RESULTS.md), [compact complete evidence](report/SUMMARY.json),
and the [maintained-resource assessment](../maintained_resource/SCIENTIFIC_ASSESSMENT.md).

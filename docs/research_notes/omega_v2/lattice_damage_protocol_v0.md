# Native bond failures and residual continuation: exploratory protocol v0

2026-10-04. Follow-up to the [2D chemistry pilot](lattice_chemistry_report_v0.md).
The physical generator, energies and rates are unchanged. This is an observation
and branching-simulation extension, not another chemical mechanism.

## Sampling and comparison

Reuse all 384 saved pilot histories at cut t=5, spanning all 32 declared
configurations. Reconstruct the full state x without conditioning on its later
success. At each state, enumerate native thermal bond-break events and compute
their total rate lambda(x). If lambda=0, retain that fact. Otherwise sample one
edge with probability q_e(x)/lambda(x). This is a draw from the native thermal
failure law conditional on that state, not uniform targeting of bonds.

Compare residual trajectories from x with the break skipped and from e(x) with
the break taken. The thermal break leaves fuel unchanged and raises contact
energy by the negative of the old bond energy; the implicit bath supplies that
fluctuation. No external repair policy, clamp or new damage transition is added.
After the cut both arms follow the same generator, including future breaks and
reverse reactions. The comparison concerns a selected event's causal effect,
not the natural association between intact and broken populations.

Use 32 independent continuations per arm at lags 0,0.5,2,5. Save every event,
initial/final state and seed. For aggregation within each physical configuration,
weight states by lambda(x); edge selection has already used q_e/lambda. Thus
lambda is used once and zero-hazard states have zero event-conditioned mass,
but remain in the unconditional failure-intensity denominator. Report both the
mean native failure rate and event-conditioned outcomes. Do not renormalize
away unsuccessful recoveries or trajectories at the horizon.

Pooled structural strata (bridge/non-bridge; currently supporting a catalytic
target or not) are descriptive. They mix chemical regimes and are not matched
causal comparisons between bridge classes. Equal representation of the 32
experimental settings is a design convention, not a physical prior over worlds.

## Observations

- Original bond: first re-formation, present at the horizon, and lost again
  after re-formation. In the skipped arm it starts present; keep that difference
  explicit. First recovery is not permanent recovery.
- Endpoints connected through any bond path, and through a path excluding the
  original bond. This is a connectivity observation, not proof that every path
  carries the same chemical function.
- Joint original-bond/alternate-path state, other bond stock, fuel use, other
  catalytic formations and their current total hazard. Exclude catalytic
  formation of the monitored bond from the downstream event count.
- Empty/concealed/exposed laws at every physical lattice cell, and presence laws
  at every physical nearest-neighbor edge. Coordinates refer to the same
  apparatus in both arms; particle names are absent from these observations.
  Keep the full marginal profiles, not merely pooled averages.
- Diagnostic spatial response over near (minimum Manhattan distance <=1 from
  the two pre-break sites) and farther coordinates. Use the squared difference
  of mean feature vectors, subtracting each arm's unbiased variance of its
  estimated mean. This corrects finite-sample inflation of squared differences.
  Do not clip negative estimates: they are estimator fluctuation, not negative
  physical influence. Normalize separately per observed cell or edge, not across
  unlike observables. This projection diagnostic is neither total variation
  on the full field nor a lushness measure. Formula for independent samples:

    D_hat = ||mean(X)-mean(Y)||^2 - tr(sampleCov(X))/n_X
                                    - tr(sampleCov(Y))/n_Y.

Also retain the broken-minus-skipped mean and its Monte Carlo standard error
coordinate by coordinate. No claim of complete joint-law identification follows
from these marginal summaries; saved trajectories permit further joint queries.

## Structural interpretation and checks

Classify a bridge by whether its removal separates its endpoints. Classify a
currently functional template by whether its removal removes a nonzero
catalytic formation hazard for another bond. These roles are read from geometry,
conformation and rates. The initial connectivity difference is definitional;
later recovery, downstream laws and costs are the experiment.

The shared reservoir and rigid-cluster motion already create effective long
range coupling. A distant response in this coarse model is not evidence of a
new propagation mechanism or a physical signal velocity. Larger component
mobility changes immediately when a bridge is removed; that approximation is
part of what may need refinement after this probe.

Check thermal-break energy/fuel accounting, bridge versus alternate connectivity,
first recovery versus later loss, native zero-hazard handling, and the unbiased
response estimator on an exactly enumerable Bernoulli example. Retain all source
contexts and outcomes. Full microscopic reversibility precludes declaring a
failure permanently irreversible merely because no repair was observed by lag5.

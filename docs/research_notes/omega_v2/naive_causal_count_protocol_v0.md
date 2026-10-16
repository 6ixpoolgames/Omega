# Naive causal count v0

2026-10-05. User authorized trying the naive count, retaining gas/thermal and
dead-end extent. No winner is required. The thermal comparison is an analogy
to a background level, not subtraction of a universal physical constant.

## Executable quantity

Replay native 2D chemistry histories. Each actual event is one node. Track the
last writer of physical positions, conformations, bond-presence guards,
occupancy and the fuel register. An event has incoming dependencies from the
recorded writers of the structural arguments of its local reaction/rate rule.
Initial conditions are boundary facts, not extra counted events. A direct
read dependency is provenance, not proof of causal necessity or a matched
individual counterfactual. Negative guards and the global fuel pool remain.
Dependencies multiplied by an identically zero model coefficient are omitted:
at zero bond energy, conformation rates do not read bonds and reaction rates
do not read target conformations. Bond constraints on motion still apply.
No physical dynamics, probability, noise or terminal-history rule is altered.

Count every event, including leaves that enable nothing else. Transitive
reduction removes redundant graph edges, not events. At each horizon record:

- N: events;
- R: ordered ancestor-descendant pairs;
- N+R: sum of unique-event future-cone sizes, including each root itself;
- mean and maximum future-cone size;
- reduced dependency forks, mergers, depth and maximum depth-layer breadth;
- all nonempty directed paths in the reduced dependency DAG, including
  singleton paths (counts reconvergent routes separately).

Layer breadth is an antichain lower bound for this provenance order, not
physical dimension or a proof of simultaneous executability. Directed paths
are dependency routes, not alternative quantum histories. N+R counts overlaps
between different roots; within one cone an event counts once. Report both
mean log2 route count and log2 of the mean raw route count; they differ.

The main graph includes the shared fuel register. A second projection omits
only those edges to expose its effect; it is not a replacement physics or a
post hoc filter. Graph ancestry within a realized history does not enumerate
the complete alternative multiway future, nor all foreclosed events.
Expectations across all retained native runs provide physical sampling weights.

## Runs

1. Reanalyse all 7,776 prior corridor histories across nine density/binding
   regimes, barriers 0/1/2 and equilibrium/refueled-equilibrium/dispersed-fueled
   preparations. No archived trajectories are overwritten.
2. Add side=12, N=16, bond strengths 0/1/2, with the same barriers and
   preparations, four source chains, 16 draws per chain, 4,000 burn sweeps and
   128-sweep spacing. Cuts 0/1/5/10/20. These are more dilute and include weak
   binding; whether equilibrium is gas-like is checked through its assemblies.
   Sampler motion is not included among physical events.

Ten worker processes maximum. Equilibrium draws remain approximate MCMC, with
source-chain diagnostics retained. Comparisons use chain-level standard
errors and preserve paired preparation/barrier source draws where available.
No result-dependent seed selection or conditioning on successful construction.

Thermal versus fueled preparations have different available free energy.
Refueled-equilibrium and dispersed-fueled share fuel and particle counts, but
not generally bond/conformation or ensemble free energy. Barrier comparisons
within one preparation share initial configurations and energy laws and change
only reversible kinetics. Report these contrasts separately.

Primary purpose: discover where simple counts favor either preparation and
whether branching/merging adds a contrast beyond raw activity. A positive
coordinate is evidence for that declared count, not yet a unique lushness
ordering. Count dependence on rule decomposition and observation resolution
is retained as a limitation, not a reason to prevent the exploratory run.

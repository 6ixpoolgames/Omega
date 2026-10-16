# Thermal baselines and contribution corridor: exploratory panel v0

2026-10-05. Implements the [revised roadmap](contribution_corridor_roadmap_2026-10-05.md).
The physical generator in lattice_chemistry.py is unchanged. No required winner.

## Common physics and equilibrium preparation

N=16 particles, reflecting square sides 8,7,6 (densities .25,.3265,.4444),
bond strength epsilon=1,2,3 and catalytic barrier reduction b=0,1,2.
This fills intermediate settings of the preceding pilot; it does not survey
all chemistry. All other kinetics and energy scales stay as previously stated.

The known equilibrium target is exp(-G). Since each allowed contact bond is
binary and additive, summing over bonds gives the position/conformation weight

    exp(-0.75 sum_i s_i) product_contacts (1 + exp(-e_ij)).

Fuel independently has Binomial(B,1/(1+exp(4))) distribution. Conditional on
geometry and conformations, each contact is bonded with probability
1/(1+exp(e_ij)). We sample the collapsed target using symmetric relocation to
a uniformly proposed lattice site (occupied sites are rejected), and conditional
heat-bath conformation updates. These are numerical preparation moves, NEVER
physical trajectory transitions. Fixed particle count makes the labeling
multiplicity constant. Catalytic barrier does not enter the equilibrium law.

Four independent chains per density/strength, two initially compact/exposed
and two dispersed/fair. Each uses 4,000 burn sweeps and retains 24 states spaced
128 sweeps apart; one sweep updates each particle. Report basic split R-hat
for bonds, contacts, exposure, largest assembly and energy, chain means, and
physical stationarity over the subsequent run. Finite MCMC yields an approximate
equilibrium baseline, not exact independent draws. Problems with mixing remain
visible and qualify comparisons. Inspect equilibrium's actual assemblies rather
than label it a gas. The tiny marginalization and sampler checks use direct
enumeration, not agreement with another MCMC chain.

## Comparisons and accounting

Three preparations at every setting:

- Sampled equilibrium.
- The SAME sampled configuration with all B=16 inventory packets set to fuel.
  Its position/conformation/bond law is exactly shared with equilibrium samples.
  Fuel addition is explicit external preparation; subsequent simulation is native.
- Uniform dispersed positions, fair conformations, no bonds, all B packets fuel.
  Same state samples across b. This is not equilibrium and is not matched to the
  refueled equilibrium state's binding/conformational energy or ensemble entropy.

Thus fuel effects can be paired separately from an initial-organization bracket.
Same-preparation b comparisons isolate the kinetic change. No claim of equal
total nonequilibrium free energy is made across the last two preparations.
State G and mean energy are reported; neither is the ensemble free energy.

Evolve every draw under native kinetics at cuts 0,1,5,10,20. 9 regimes x3 barrier
settings x3 preparations x96 draws =7,776 full physical trajectories, up to ten
workers. Retain full timed events in 324 compressed batches. Preserve failures.
Initial sample pairs are shared across kinetic/preparation contrasts; dynamics
random streams are independent. Uncertainty is summarized across the four
independent source chains, retaining within-chain dependence (only four clusters,
so these are exploratory errors, not tight confidence statements).

## History readouts

Save ordinary assembly, fuel, timing and reaction profiles. Add exact dwell-time
integrals of bonds, fuel and geometrically available template opportunities,
native formation hazards, first joins versus re-formations of material pairs,
and products that later catalyse another formation. Observe productive products
that subsequently disappear; final survival is not required. A bond episode
ends at dissolution, including immediate repair as a new episode. Initial bonds
have no assigned pre-cut ancestry. IDs identify material paths only; no identity
has preferred value. Counted new pairs do not imply new chemical types.

These are mechanism diagnostics. Rate increases, record counts, integrated
occupancy and catalytic depth are not a lushness scalar or the full joint
continuation field. No sum or vote over these coordinates declares a winner.

## Companion working-template failure panel

Reuse all 384 source cuts from the first 2D pilot. Of these, 60 currently support
a fuel-assisted formation through a template. Sample a thermal break only among
those working templates using its native hazard, and branch 64 futures each
with the event taken/skipped, at lags 0,.5,2,5. Keep all noneligible source contexts
with zero class hazard. The class's full-population rarity remains separately
reported; within-class effects are not typical effects of all bond breaks.

Physical rules are unchanged in both arms. Native conditional weighting is
proportional to class hazard at the source, once, since the selected edge already
has conditional hazard weight. Keep full residual trajectories and prior spatial,
recovery and subsequent-construction diagnostics. This is a dependency probe,
not a requirement that generativity survive every perturbation.

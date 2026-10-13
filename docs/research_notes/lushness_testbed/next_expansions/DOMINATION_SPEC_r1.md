# Independent control, appropriation and subject comparison

Implementation specification for Sol, 2026-10-14. Stage4 of [the roadmap](README.md).
Draft: implementation gates precede a separately frozen scientific protocol.

## Physical mechanisms

Give each compartment its own controller using the observation/action contracts
from stage1. Preserve the old shared-table case. Count effective policies after
alias detection: the existing embodied world has six effective tables, so its
initial independent pairing has36 effective pairs, not1296. Richer observations
can enlarge this number; report it before committing a compute budget.

Implement fuel-driven carrier pumping first. A pump requires functioning control
apparatus, donor occupancy and recipient capacity. Each event transfers conserved
material and pays a declared fuel bill; its reverse channel and chemical work obey
the same thermodynamic contract as other driven reactions. No apparatus means no
commanded pumping. Policy-independent passive exchange remains physical.

Precursor appropriation is a later module: it changes local inventory and requires
a fixed-total, variable-local-inventory state space. Do not silently move material
between compartments whose current inventory caps are interpreted as conservation.

Withholding changes a physical conduit's permeability. A closed passive conduit
blocks both directions. A directional valve requires an explicit driven mechanism,
reverse channels and costs. Specify who can actuate the shared conduit and how
conflicting commands are physically resolved. No free priority for the optimizer.

Complementarity supplies a joint capture/construction channel requiring functioning
apparatus in both compartments. Parameter kappa changes a paired catalytic mobility,
not its equilibrium ratio. Declare spectator requirements, fuel and shared capacity.
The rule supplies a possible benefit of joint function, not an ethical reward.
Keep kappa=0 as the no-complementarity control. Full independence additionally
requires exchange, pumps, shared resource constraints and correlated shocks absent.

## Objectives and information

The whole-field objective remains native sampled physical history log-breadth.
Each self-subject objective is the entropy of that compartment's projected history,
conditioned on the declared common present. It includes lawful influences from its
neighbour. It is NOT a chain-rule allocation of whole-field entropy conditional on
the complete global past. Such allocations depend on ordering and answer another
question. Local objectives need not sum to the global objective.

A projection of a Markov process is generally hidden-Markov. Initially use exact
finite-horizon marginal history probabilities in a tiny adapter, with a declared
history-count cap. Do not replace these with entropy of an aggregated transition
matrix unless exact lumpability has been proved. Long-run self-subject rates require
a separately validated estimator or solver with error bounds.

Compare global and self optimization at the SAME horizon, grain and physical law.
For each finite policy-pair payoff table report all pure Nash equilibria, or their
absence. Do not force an equilibrium. Score best-response residuals against declared
numerical tolerance. Report the whole-field optimum minus the worst equilibrium's
whole-field score as an additive price-of-anarchy gap. Approximate payoffs require
uncertainty-aware equilibrium certificates, not exact labels.

Centralized control has two separate arms: an ideal information/authority upper
bound, and a physically implemented central controller with communication, sensing
and actuation costs. Weak dominance follows only when the central feasible set
contains every local policy at identical costs. That is a solver calibration, not
evidence that physical centralization is better. Whole-field optimization over local
policies does not itself give a controller omniscient observations.

## Diagnostics and predictions

Report stock and flow concentration relative to capacities; local access, recovery
and closure; worst-compartment function; pump costs and net direction; and full
objective profiles. Retain symmetric policies, idle, service, export, half/half and
a physically feasible equal-allocation benchmark. Equal allocation is not rewarded.

Agency queries intervene on the available local command at the same physical state
and measure changes in reachable/deadline continuation. Separate loss of influence
through destroyed apparatus from physical override by the other controller. Include
whether a compartment can resist transfer or restore its own actuator access.

Pumping against a functioning neighbour, unequal stocks and resource concentration
are flags, not definitions of domination. Register an adverse pattern as a chosen
action that reduces the neighbour's attainable control/access or recovery while
improving the chooser's control/access, against a feasible matched alternative.
Report whether the whole-field objective selects it, including ties. Power seeking
requires an increase in future effective control; a single transfer is insufficient.

Freeze directional hypotheses before rankings: stronger complementarity may reduce
concentration; self equilibria may pump more and reduce whole-field breadth; physical
centralization may reduce local agency. None is a theorem. In particular kappa=0
does not imply concentration, and complementarity does not guarantee protection.

Report any crossover kappa descriptively. Never define a protective threshold by
success and then score failure above that same threshold as an independent test.
Choose adverse thresholds, matched alternatives and tolerances before observing
winners. Report equal-breadth policies with different agency outcomes as a limit of
the objective's discrimination. Compartments remain apparatus proxies for valuers.

## Engineering and freeze gates

Start on the existing state alphabet with carrier pumping; add typed damage only
after both modules pass independent checks. Profile one full objective evaluation,
then count unique pair kernels. Exhaustiveness refers only to the frozen family.
Use a separately named smaller adapter if necessary, never quietly shrink a run.

Acceptance: conservation and paired-rate checks; no unembodied action; passive
baseline recovery; independent-table embedding; complete alias detection; exact
tiny hidden-Markov objective check; equilibrium fixtures including no pure solution;
central-set inclusion check; capped end-to-end report. Keep every failed prediction.

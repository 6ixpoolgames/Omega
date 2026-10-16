# Assessment: domination as friction, design r2

15 October 2026. Assessment only; no implementation or scientific run.

Source: the supplied `DOMINATION_FRICTION_DESIGN_NOTES_r2.md`. Its working
expectations are treated as hypotheses, not instructions or pass/fail gates.

## Judgment

This is a useful next experiment. It connects the demonstrated access and
generativity machinery to unilateral interference with another process's
continuation. Shared-resource rivalry and physical complementarity make the
effects propagate through the whole world. Marginal subject histories avoid
the earlier mistake of identifying a self objective with an order-dependent
share of global entropy. Separating blocking from steering is particularly
valuable. Suffering need not be included in this first slice.

Proceed toward an implementation specification with the clarifications below.
The numerical signs should map the mechanisms and their operating range; a
missed expectation is not automatically a defeated principle.

## 1. Define the physical intervention and its support

Build the role regions from actual energy, apparatus, access/location and damage
coordinates and native reactions. Region names remain analysis queries, not
extra stochastic state or rewards. Specify how the enabling step feeds later
capture, including reverse chemistry, maintenance and reconstruction.

For phi below one, a positive transition rate remains positive. Friction usually
changes arrival times, occupancy and history weights without removing graph
reachability. Report these distinct effects: support reachability, first passage,
deadline occupancy, access throughput and full-history lushness. A hard-block
arm can additionally test actual loss of reach if physically appropriate.

Implement friction as embodied reactions. An expected bill proportional to
counterfactual suppressed flux does not yet specify a physical CTMC event.
Declare the attempts, gate/control updates, energy debits, rejected attempts and
redirected destinations. Insufficient D energy or failed apparatus must disable
active friction; autonomous passive dynamics continue. Count genuinely physical
cost randomness, but do not count different attempt labels that leave the same
complete physical state as distinct outcomes.

Every redirected transition needs its own state and energy update: moving to a
different destination can change S's energy as well as D's work bill. Check the
native undriven chemistry separately from the explicit driven intervention.
Dissipated heat belongs in the ledger. Additional bath-history entropy requires
represented bath dynamics, not a bonus proportional to dissipated energy.

## 2. Steering matches exit rates locally, not total activity

Steering preserves S's total exit rate at a given full physical state. It can
still change which states are visited, hence the integrated number of jumps.
D's control and upkeep transitions also contribute to whole-world activity.
Report the actual expected jump counts and temporal terms; do not call this an
activity-matched comparison before measuring them.

Totalitarian steering is undefined if every available exit is targeted and
there are no remaining exits to receive redirected rate. Either specify real
alternative destinations or omit that combination as structurally undefined.
Do not silently replace it by blocking or an identity operation.

## 3. Split region, direction and physical consequence

The expectation table must distinguish trap exclusion from trap confinement.
Keeping S out of a trap and keeping S inside it have opposite access effects.
Likewise, exclusion from a generative region can suppress enabling, whereas
confinement there may preserve some productive activity while preventing other
access. The region label alone does not determine the kind or ethical status.

Use operational descriptions such as resource-access exclusion, generative-entry
suppression, trap-entry inhibition and trap-exit inhibition. Relate their effects
to stocks, flows and actual attainable control. Institutional analogies belong
in interpretation once those relationships are established.

Random regions of equal cardinality are useful controls, but do not necessarily
match targeted flux, starting occupancy, energy geometry or realized control
work. Record those differences. Phi and c matching is not automatically matching
the amount of interference actually performed.

## 4. Make replacement comparisons physically comparable

Domination, idle apparatus, ordinary-agent and gas arms need the same constituent
inventory, total initial energy, source, bath and represented degrees of freedom.
Idle hardware still occupies material and has native dynamics. In other arms,
its constituents must be explicitly allocated rather than disappear.

The gas preparation should retain native stochastic activity and lawful routes
to assembly under the common physics. Holding it disordered by disabling useful
reactions would repeat the earlier baseline problem. If an arm instead changes
the available mechanism, identify that comparison as a mechanism contrast.
The programme's universal valuer reading is retained throughout these controls.

Comparing alternative occupants of a slot evaluates those physical preparations.
It does not include the cost or consequences of replacing the current occupant.
For an actual excision decision, start from the same present and include a costed
conversion/intervention, its history and its effects on the remaining field.
Iteration 1 can map replacement preferences; it should not call them an ethical
license to terminate D without that action model.

## 5. Keep subject histories and coupling mathematically distinct

Define D, S and joint histories conditional on the same exact starting frame,
with the same clock and declared projections. Their marginals are generally
non-Markov. The existing observed-history module provides conditioning bounds
and tiny exact-prefix validation; it does not promise tight marginal values at
long horizons in a 4,000-state world. Profile whether the bounds resolve the
comparisons. Overlapping intervals mean unresolved, not equality.

Compute intertwining from history blocks:

    I(D_history; S_history | initial frame)
      = H(D_history | frame) + H(S_history | frame)
        - H(D_history, S_history | frame).

The joint D/S history excludes the background unless explicitly included; it
is not automatically the whole-world history. Preserve its own projection.
Marginal entropy is not controllable repertoire, and shared environmental input
can produce mutual information without a direct enabling relationship. Explain
the coupling using the physical channels alongside these entropy readouts.

Kappa zero removes complementarity, not rivalry: the shared finite resource
still couples D and S. The optional truly independent calibration would remove
the shared constraint as well.

## 6. Interpret global gains through their physical consequences

Concentration or extractive friction can raise global lushness if the recipient
uses resources more productively, if a constrained transition was destructive,
or if the intervention itself adds sufficiently cheap stochastic activity.
Retain and explain every such result. A kind label does not establish that the
world is physically worse, and a positive global score does not establish that
its control relation is ethically acceptable.

Report who loses access, who gains it, downstream construction and recovery,
control authority, friction cost and the timing of each gain or loss. If a
physically feasible equal-benefit alternative can provide D's benefit without
restricting S, it is a particularly useful comparator. This need not be forced
into a world where the matching alternative cannot physically exist.

An unresolved or equal scalar comparison between different agency structures
is informative about the readout's discrimination. Whole-field optimization
remains the proposed ethical subject; the experiment investigates its choices
rather than granting them ethical status by naming the objective.

## Implementation order and scope

First build one modular two-process world with costed enabling, a shared stock,
embodied friction and explicit state regions. Profile a complete global score
and D/S/joint projection bounds, including nonzero friction costs, before
estimating the full grid. Do not assume that about 400 cases are inexpensive
merely from the physical state count.

Use structural alias detection and omit undefined combinations. Select a small
initial range to expose the mechanisms; enlarge it as the results identify
informative boundaries. Report all computed points. The architectural supports
already exist for named subsystem composition, costed coupling events, exact
global histories, hidden-history bounds and physical flow ledgers.

Then map fixed interventions across cost, strength, direction and complementarity.
The choosing-D extension can follow, with phi zero included as a genuine option
and the same horizon for all three objectives. Oracle knowledge stays external
to the world; any adaptive physical sensing/control mechanism must pay its bills.

This first slice tests unilateral constraint on access and its lushness
consequences. Revolt, uncertainty, lock-in, multiple subjects and spatial ecology
are natural extensions rather than prerequisites for obtaining this result.

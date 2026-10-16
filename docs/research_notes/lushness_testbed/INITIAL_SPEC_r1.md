# Access and lushness optimizer test bed: initial specification

Status: DESIGN ENVELOPE, 2026-10-13. User "Go both" authorized the first A/B
implementations and runs. [Results](access_results/RESULTS_r1.md) distinguish
implemented scope from this larger design; executable protocols live in assembly/
and controlled/. This document itself grants no commit or publication permission.

Governing brief: v4 and subsequent user clarifications; see
[foundation contract](testbed-foundation-contract.md). Working repository: original Omega, active branch codex/operational-continuation-comparison. The new-repository launch is deferred.

## 1. Question and first deliverable

Test what policies maximizing declared lushness actually select, how those
policies change access, and whether their consequences support the central wager
that lushness supports the substrate for possible value. Surprising outcomes may
inform the theory, the world model, controller restrictions or numerical methods.
Agreement with an anticipated ethical policy is not an acceptance test.

Access is lawful, weighted availability of continuation, including time, cost,
joint feasibility and dependencies. Generativity is an enabling pattern within
access. No independent cooperation, survival, repair or generativity reward is added.

Deliver two linked fixtures, in order:

1. **A: assembly calibration.** Reversible joining, persistent unused assembly,
   and assembly-mediated feedback. Establish correct rules, kinetics, symmetry,
   measurement, exact/sampled agreement and reproducible reporting.
2. **B: controlled access.** A small driven compartment system with maintenance,
   construction and transfer. Search policies and inspect their consequences.

A alone does not answer how a lushness optimizer behaves. Both fixtures and the
workflow constitute the intended first research release. The first engineering
run covers A only; B follows once its native control and cost table are frozen.

## 2. Selected established foundation

Use **BioNetGen/BNGL** as the first rule language and network-generation engine.
Use its documented binding example as a provenance-tracked calibration, then an
explicitly adapted assembly model. BioNetGen exports species, reactions and
multiplicity factors. This suits a small independent finite-state solver.

The exported reaction network is NOT the state transition matrix: species are
building blocks, whereas a Markov state is a joint population/configuration of
them, apparatus, stores and controller registers. Our adapter must enumerate
reachable states under conserved inventories and derive stochastic propensities
using the engine's conventions, volume units and symmetry factors exactly once.

Two calculation modes share one canonical reaction/transition specification:

- bounded reachable-state enumeration and numerical propagation;
- stochastic sampling from the same propensities and state updates.

The official BioNetGen simulator supplies an additional independent distributional
check. A sampler sharing our transition implementation is useful but cannot alone
detect a common compiler error. Network-free NFsim or Kappa becomes an optional
larger-system backend after an equivalence check, not a launch dependency.

Published examples establish reusable mechanisms and external calibration, not
automatic empirical validity of our adaptations. Record upstream versions,
licenses, source hashes and every modification. Select the calibration before
examining lushness rankings. Do not describe the selected toy as a published model
if only its language or component mechanism is published.

## 3. State and boundaries

Fixture A: one well-mixed compartment, bounded monomer inventory, site-resolved
binding patterns and assembly composition. Start with inventories 2, 3 and 4 as
engineering targets, not promises that enumeration will fit. With a separate
dimer catalyst, inventory 2 cannot exhibit a dimer catalysing a second dimer:
the availability of reactants must be checked before calling a case feedback.

Fixture B: two fixed compartments joined by one potential transport connection;
finite assembly precursors, charged/discharged resource carriers, maintained
apparatus and local controller registers. Incident drive, bath and material
boundaries are explicit and common to matched preparations. Population is coarse;
specific ancestry, reproduction and numerical personal identity are deferred.

Every variable required for future dynamics belongs to the present. Source code
IDs and survey annotations do not become physical state. Well-mixed molecule
labels are not automatically distinct physical alternatives. Physical locations,
sites and records are retained where the adapter resolves them.

The first population parameter specifies installed unit counts/capacities.
Operational population is reported by condition, compartment and capability.
Population growth and heterogeneous inherited controllers are extension targets,
not silently present in the first fixture. Material limits are physical;
enumeration and wall-time limits are computational and cannot act as reflecting
boundaries or remove transitions without declaring a different world.

## 4. Assembly calibration arms

| Arm | Mechanism | Intended question |
|---|---|---|
| R: reversible | Association and dissociation with declared free energies/barriers | Reference assembly dynamics |
| F: frozen accidents | Long-lived bonds, with no rule exploiting assembled structure | Does persistence without reuse account for the effect? |
| C: feedback | Existing assemblies mediate further joining through explicit catalytic rules | Does reusable composition change subsequent access? |

Match matter inventory, volume, initial resource budget, observation convention
and drive where applicable. These three mechanisms define different laws: report
them as mechanism contrasts, not three preparations of one law. Within each law,
also compare assembled/unassembled preparations and a specified disordered prior.
Hold total modeled energy fixed where possible; otherwise expose the mismatch.
Do not add preparation-prior entropy to conditional future breadth.

F has two explicitly separate possible realizations: (i) a high-barrier reversible
bond, physically metastable at the horizon; (ii) a zero-reverse-rate idealization.
The latter may create absorbing classes and is not equilibrium reversible physics
at finite temperature. Do not claim it is guaranteed thermodynamically consistent.

A catalyst changes kinetics without changing equilibrium constants for the same
net reaction. Use reversible catalytic intermediates, or justified paired rate
changes preserving the forward/reverse ratio. A fuel-coupled directional effect
must include fuel/waste and reservoir exchanges. Do not increase forward rates
alone and attribute the change solely to passive catalysis.

Finite inventories test finite feedback and saturation. They do not demonstrate
open-ended growth. A larger inventory is a separate physical system. Eventually
adding material inflow requires a paid boundary model; enlarging a numerical cap
is not a physical process. Use common time units and horizons for comparisons.

## 5. Thermodynamic contract

Energy-based BioNetGen is an available specification method, not a property of
every BNGL file. Its energy-derived reversible portion can enforce detailed
balance. Ordinary kinetic rules, imposed controls and driven boundaries require
their own consistency checks.

Declare temperature or beta, standard free-energy conventions, compartment
volume, molecular inventories, barrier/attempt scales, and reservoir chemical
potentials for any claim of thermodynamic grounding. Verify a closed equilibrium
control and cycle consistency. In the driven model check local detailed balance
with reservoir work and the chosen coarse-state degeneracies; global detailed
balance is not expected under maintained driving. A first-law token ledger alone
does not prove these properties. Free energy and internal energy are not the same
ledger quantity.

No random cost is added to manufacture branching. Fixed-stoichiometry reactions
have fixed bills per occurrence; their times and competing physical outcomes can
still be stochastic. Physical random damage/costs, if included, are declared and
diagnosed separately. An arbitrary deterministic-time replacement changes the
process and is an ablation, not an invariance transformation.

## 6. Controlled fixture B: first design envelope

The next implementation spec must supply explicit BNGL rules for the following
operation families and the exact state/observation table:

| Family | Native effect | Required cost/consequence |
|---|---|---|
| Capture/conversion | Charge a local carrier using the incident gradient | Input, losses, saturation and stored energy |
| Assembly | Bind available precursors into working apparatus | Material, work/fuel, kinetics and intermediate availability |
| Maintenance | Retain or restore apparatus condition | Fuel, occupied capacity, delay and residual wear |
| Transfer | Move a carrier through existing connectivity | Donor depletion, receiver capacity, transport time and work if needed |
| Reconfiguration | Change a physical gate or controller register | Switching implementation, memory, delay and applicable work |
| Wear/disassembly | Alter bonds, function or connectivity | Dissipation, recovered precursors and recovery possibilities |
| Rest | Leave controls unchanged while native processes continue | Time, decay and forgone uses of capacity |

Each controller selects a target for its existing actuator/gate. It cannot change
arbitrary rate constants, read remote inventories, or invoke simulator intervention
commands as free agency. Gates modify native access because of their physical
state. The rule set includes gate-switch execution. Fixed passive operation is a
feasible controller. Communication and extra memory are subsequent costed variants.

Use deterministic local response tables as an engineering reference, and include
stochastic response tables in the first substantive optimizer comparison. Native
decision randomness counts under the user's null measurement hypothesis, alongside
chemical and thermal randomness. A declared coarse stochastic controller/register
is a sufficient model: microscopic randomizer hardware need not be simulated.
Declare its information, timing, outcomes and cost assumptions, including any
idealized zero cost, rather than silently excluding decision randomness.

Declare the observation predicates, table size and probability parameterization
before search; report best-found versus certified-best explicitly. Randomness in
numerical search or redundant action names is not additional world branching.
Where distinct decisions have a resolved physical/register trace, count it once
in the joint history. If only the resulting world state is retained, evaluate its
mixture law instead of adding an extra action-entropy term without justification.

Compare policies from the same full physical root and hardware boundary. Include
passive and simple maintenance/transfer baselines, but do not limit discovery to
named moral strategies. A full-information planner is a separately scoped
benchmark; it is an upper bound only if feasible-set inclusion under the same
objective and costs is proven. Model-based search cost outside the world is
separate from the physical execution cost within it.

The construction must admit a paid loop from capture to assembly to changed
capture/transport and further assembly. It must also permit depletion, access
concentration, apparatus loss and failed recovery. Their ranking is an outcome.

## 7. Measurement and comparison

Use the separate [measurement contract](MEASUREMENT_r1.md). First primary readout:
full declared finite-state configurations sampled at a fixed physical cadence,
including physical controller registers. It is a finite-resolution continuation
readout, not the entropy of the complete continuous-time event history.

Continuous-time event type/timing and finer physical distinctions are separately
audited. No claim that BioNetGen's reaction IDs select the fundamental grain.
Keep thermal/stochastic branching; a proposed persistence-filtered Rule A readout
is optional and not a replacement objective.

This unfiltered treatment is the initial/null measurement hypothesis. The
statistical null for a particular comparison still needs an explicit effect and
test. Rule A is an optional overlay: if tested, freeze its retention definition,
scales and criteria before that test; otherwise explicitly defer it. A later
overlay is a new experiment and cannot retroactively rescue the primary result.
Counting randomness does not prove that faster dispersal always wins: destruction
can change later access, resource use and branching in either direction.

For the next scientific fixture, anchor the cadence to a declared common physical
reference timescale before ranking policies, and sweep fixed multiples of it.
Do not recompute a separate ruler for each policy or arm. Reference relaxation is
one candidate only where it is well-defined; a frozen/absorbing arm may not supply
the required relaxation scale. This does not alter the completed engineering
calibration or claim that its cadence was physically fundamental.

Report the horizon profile. Apply v4 rate-first/offset-second comparison only when
its hypotheses and numerical residuals are established. Distinct policies/laws
can have distinct rates; roots in one finite irreducible law share the rate.
Absorbing, multichain and periodic cases need their actual class structure.

## 8. Automated scientific outputs

Use [experiment workflow](experiment-workflow.md). Each report contains
policy behavior, breadth and uncertainty/certificates, state/class structure,
resource accounts, access/assembly witnesses, loss/recovery profiles, baselines,
all registered outcomes, and grain/clock sensitivity. Record absent phenomena as
not implemented or not observed, rather than treating them as zero by default.

Harm, maintenance and generativity are survey queries about changed continuation.
Structural provenance alone does not prove causal attribution. A causal probe
specifies a feasible alternative, matching conditions and resource bills.

## 9. Build sequence and gates

1. Retrieve and pin an official BNGL binding example; license/provenance review.
   Record platform and engine version. Opus's reported installation is not evidence
   that it is installed or reproducible on this machine.
2. Generate the small network; audit multiplicity, units and physical grain with
   a hand-enumerated monomer/dimer reference. Compile its population-state Q.
3. Implement shared measurement, manifests and report validation before ranking
   any adapted assembly arms. Build the tiny exact and sampled check together.
4. Freeze the adapted rules, thermodynamic parameters, grain, horizons, predictions
   and hit criteria. Run a hard-capped engineering smoke; report runtime/memory.
5. Execute A if gates pass; retain every arm including adverse rankings.
6. Freeze B's full operation and controller tables, verify costs/access witnesses,
   then search and evaluate policies. A's report does not complete this milestone.

No unfrozen generativity parameter search is counted as confirmation. Engineering
profiling can choose computation sizes; choosing favorable kinetics is exploratory
and requires a separate record. The draft configuration deliberately blocks
scientific execution until the unresolved numerical fields are supplied.

## 10. Sources and verification boundary

- [BioNetGen official tutorial](https://bionetgen.org/tutorial): binding examples,
  network generation and multiplicity factors. These features motivate selection.
- [Energy-based modeling in BioNetGen](https://doi.org/10.1109/BIBM.2016.7822739),
  Sekar, Hogg and Faeder (2016). Author manuscript inspected; guarantees apply to
  the energy-based construction, not arbitrary driven rules.
- [Rule-based modeling introduction and eBNGL examples](https://pmc.ncbi.nlm.nih.gov/articles/PMC4526164/):
  primary publication and example models for energy/compartment calibration.
- [Hybrid particle/population simulation](https://arxiv.org/abs/1301.6854):
  established route toward mixed structural and population representations;
  not a proof that any lumping preserves our history readout.
- [Kappa reference guide](https://kappalanguage.org/static/manual.pdf): alternative
  graph-rewrite semantics and CTMC backend; symmetry conventions require audit.

Sources checked 2026-10-13. Local engine/generator compatibility has now been
tested for binding, assembly and three controller settings. Empirical physical
parameter calibration remains open.

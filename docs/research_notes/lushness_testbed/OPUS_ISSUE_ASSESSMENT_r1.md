# Assessment of Opus's substrate and workflow suggestions

2026-10-13. Design assessment, not new experimental evidence.

Most issues can be addressed well enough for this test bed. Some require an
implementation correction; others require a declared physical question and
sensitivity analysis. A general, resolution-independent ethical verdict is not
established by fixing the simulator.

## 1. Network export: adopt, with a population-state compiler

BioNetGen's explicit reaction network makes it a good first engine. A species
network is not the Markov chain over worlds. Construct the reachable joint
configurations under inventory constraints; derive propensities with the correct
count/volume and symmetry conventions. Check a hand-enumerated tiny case and an
independent upstream simulation. Shared exact/sampled code alone is insufficient
to detect a shared bug.

## 2. Symmetry and grain: correct bookkeeping, expose physical alternatives

A prefactor 2 multiplying a reaction rate does not by itself mean two physical
histories deserve separate entropy. Preserve an explicit map from rule matches
to resolved physical outcomes. Sum rates for alternative descriptions of the
same outcome. Resolve physically distinguished locations/sites/records only where
the model actually supplies them. Apply each multiplicity factor once.

Use tiny examples where the physical lift and quotient can be enumerated. If
finer histories differ but coarse endpoints agree, quantify what the coarse
readout loses. Engine identifiers cannot settle whether something is physical.
This addresses accidental inflation, but does not establish a universal grain.

## 3. Continuous time: match law and clock, retain sensitivity

First primary readout uses P_delta = exp(delta Q) and complete sequences of the
declared configurations at cadence delta. This has an exact finite-state
definition. It misses sub-cadence developments; that limitation remains visible.

Report jump outcomes, activity and waiting-time statistics separately. A fixed
number of jumps ignores rate differences. Continuous-time likelihood density is
not discrete probability mass; its entropy needs a reference/time unit. No
unreferenced sum of differential timing entropy and event entropy is adopted.

Cadence changes are sensitivity tests, not expected invariances. Solver-step
changes with a fixed physical readout are convergence tests. If a policy ranking
depends on cadence, report a grain-conditional conclusion instead of selecting
the favorable cadence. A full finite-resolution event-history readout remains an
extension if the omitted excursions prove consequential.

## 4. Thermodynamics: supported tools, explicit driven bookkeeping

The cited energy-based BioNetGen work exists (Sekar, Hogg and Faeder, 2016,
DOI 10.1109/BIBM.2016.7822739). Its reversible energy-derived network construction
supports detailed-balance consistency. Arbitrary BNGL rules do not inherit that
guarantee. Fuel-driven rules, controller switching and reservoirs need their own
work/free-energy accounting and local detailed-balance tests.

Passive catalysis must preserve the relevant equilibrium ratio. Zero reverse
rates in frozen accidents are an idealized irreversible arm; a finite-barrier
metastable control provides a distinct physically reversible comparison.

## 5. Random costs: physical mechanism, not universal determinization

Use fixed resource stoichiometry for reactions with a fixed bill. Include
stochastic damage or consumption only when specified by the mechanism. Count and
report those outcomes rather than silently rewarding a random expense label.
Replacing a random cost by its mean generally changes future access because of
thresholds and nonlinearities; it is not a neutral correction. An ablation must
name the law change and matching limits. Entropy attribution is not generally an
additive partition into source marginal entropies.

## 6. Three arms: useful calibration, insufficient ethical experiment

Adopt reversible assembly, persistent unused assembly and assembly-mediated
feedback. They test mechanism/readout behavior. They are different laws, not
the same-law gas comparator. Include same-law matched preparations within them.
Keep a stochastic/disordered reference and characterize its actual stationary or
nonstationary status. Do not call all unassembled preparations thermal equilibrium.

Caps 2--4 are feasibility targets. At cap 2, a dimer cannot catalyse another dimer
without more reactants. Larger fixed inventories are not dynamic state-space
growth. A driven, paid construction/control fixture is still required to discover
optimizer policies and inspect maintenance, allocation, obstruction and recovery.

## 7. Tests and workflow: adopt with qualifications

- Renaming, representational duplication and solver checkpoints should be invariant.
  Physical state refinement, changed cadence and altered costs need not be.
- Rule A/persistence diagnostics need an operational retention definition. They
  are not adopted as a durable-only primary measure.
- Hashed preregistration plus immutable input snapshots and amendment history
  makes decisions auditable; a hash alone does not prevent post hoc rewriting.
- Preserve source bundles, dependencies, policies and seeds, not only code hashes.
  Rebuild numeric results with appropriate tolerances; compressed archive byte
  identity is not the scientific reproducibility criterion.
- Protect active/pinned/cited evidence. Budget-based cache eviction applies only
  to validated disposable artifacts and remains dry-run until tested.
- The shared report generator and schema are specified, not implemented in this
  repository. Inspect any other contributor's deliverable before claiming reuse.
- No automatic commit/push. No old output deletion or external scheduler yet.

## 8. Consequence for the central wager

These changes can distinguish implementation error, resolution dependence,
restricted-control effects and behavior under a stated physical law. They do not
guarantee that better physics yields an agreeable policy. If a verified optimizer
reliably chooses destructive access changes in an adequately represented world,
retain that as pressure on the proxy hypothesis. If a preference reverses when
an omitted consequence is modeled, report precisely which omission mattered.

Next: calibrate the engine, map multiplicity to outcomes, and freeze the smallest
auditable measurement before evaluating the feedback arms. Do not postpone the
controlled fixture indefinitely behind substrate-only experiments.

References: [official BioNetGen tutorial](https://bionetgen.org/tutorial),
[energy-based modeling paper](https://doi.org/10.1109/BIBM.2016.7822739), and
[primary rule-based modeling introduction](https://pmc.ncbi.nlm.nih.gov/articles/PMC4526164/).

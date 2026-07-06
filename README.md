# Omega

[![Lean AlphaOmega](https://github.com/6ixpoolgames/Omega/actions/workflows/lean-alphaomega.yml/badge.svg?branch=master)](https://github.com/6ixpoolgames/Omega/actions/workflows/lean-alphaomega.yml)
[![Baseline Witness Smoke](https://github.com/6ixpoolgames/Omega/actions/workflows/baseline-witness-smoke.yml/badge.svg?branch=master)](https://github.com/6ixpoolgames/Omega/actions/workflows/baseline-witness-smoke.yml)
[![Validation Router](https://github.com/6ixpoolgames/Omega/actions/workflows/validation-router.yml/badge.svg?branch=master)](https://github.com/6ixpoolgames/Omega/actions/workflows/validation-router.yml)

Omega is a research program for treating alignment as the problem of
preserving the corridor of compatible, value-bearing futures.

The repo is the formal toolbench for that program. It proves small, auditable
theorems about when abstractions can be trusted, when proxies fail, when
decision procedures have certified routes, when corridors confine persistence,
and when update rules fabricate safety by deleting the world that would refute
them.

If the long-term goal is to mark the safe path for intelligent agency, the
first problem is not drawing the path. It is proving that the map is not lying.

## The Thesis

Alignment is not only an objective-selection problem. It is also an
abstraction-integrity and continuation problem.

Any intelligent system acts through models, metrics, summaries, observations,
boundaries, policies, update rules, and compressed presentations of the world.
Those presentations can fail in several dangerous ways:

- They can merge states whose consequences are different.
- They can make two futures look equally viable when one has lost a necessary
  distinction.
- They can create phantom reachability or phantom viability that is not present
  in the exact system.
- They can preserve a proxy while destroying the target the proxy was supposed
  to protect.
- They can update the system's information state by excluding the true model
  and then certify behavior only inside the false remaining world.

Omega studies the formal conditions under which those failures can be detected
or ruled out.

## Value Requires Valuers

Value does not float freely in the universe. Value requires valuers, or at
least value-capable trajectories: systems able to encounter, preserve, revise,
compare, create, and be affected by what matters. If no possible future
contains valuers, then no possible future contains realized value.

That makes the central alignment problem deeper than choosing the right reward
function. Before asking which futures are good, we have to ask what makes
value-bearing futures possible at all. The target is the substrate of
compatible continuations in which valuers can arise, persist, interact, and
mature without destroying the conditions that make future value possible.

This is the object Omega is trying to track: not a single utopia, final state,
or utility function, but the viable corridor of value-bearing continuation. The
project starts below value because the preservation problem starts below value.

## Alpha-Omega In Plain English

Alpha-Omega is the project's name for studying that object from both ends.

Alpha is the primitive end. It asks what must be true before valuers are even on
the table: relation, distinction, asymmetry, consequence, and the conditions
under which a difference can matter because erasing it changes what can follow.

Omega is the terminal ambition. It asks what it would mean to preserve the
richest compatible continuation of the value-bearing substrate: the shared
corridor in which many value-capable trajectories can remain possible without
collapse, capture, or irreversible loss.

The current effective-layer map is deliberately staged:

```text
Alpha constrains Continuation.
Continuation constrains Agent.
Agent constrains Valuer.
None of the upward maps is canonical by default.
```

So Alpha is not a separate toy theory and Omega is not a mystical endpoint.
Alpha studies the seed conditions of consequence-bearing mattering. Omega
studies the possible maximal compatible development of that mattering into
value-bearing continuation. The repo's job is to make every bridge in that
tower explicit enough to audit.

## From Intuition To Formal Machinery

The formal stack asks what has to be true for that ambition not to collapse
into poetry.

A difference must be consequence-bearing. A proposed abstraction must not erase
consequence-separated states. A proxy must not be trusted when the target
changes while the proxy stays fixed. A viability or reachability claim must
survive exact checking, because bad presentations can fabricate possible
futures or hide irreversible loss. A decision procedure must justify itself
through certified routes. A learning process must update its information state
without deleting the true model that generated the evidence.

All of these are pieces of one question:

```text
When can a representation, policy, update rule, or decision surface be trusted
not to erase, fabricate, or hide continuation-relevant structure?
```

The current center of gravity is the decision/corridor stack. It combines
certified map use, robust viability corridors, deterministic and stochastic
Blackwell-shaped comparison bridges, registered arbitration scaffolding, and an
adaptive fixed-world learning layer.

This is already useful as a constraint-based alignment floor. Before solving
value, agency, or Omega, the repo can formally reject unsafe maps of
continuation. A representation is not admissible merely because it is useful or
predictive; it has to preserve the consequence-bearing facts it is being used
to reason about.

## Current Reading

The old public framing over-centered proto-teleology and early future-field instrumentation. Those remain useful foundation and provenance. They are not the current front door.

The live formal posture is:

```text
effective layers:
  Alpha constrains Continuation;
  Continuation constrains Agent;
  Agent constrains Valuer;
  none of the upward maps is canonical by default.

certification:
  abstractions, presentations, observations, and update rules must preserve
  the facts they are used to justify.

corridors:
  if persistence under declared constraints is required, admissible behavior
  must remain inside the relevant robust viability corridor.

learning:
  unknown-but-fixed ambiguity can sometimes be converted into information by
  sound update; certified finer observations weakly widen the adaptive
  corridor; fabricated model elimination can create phantom safety.

recovery:
  some losses are not merely local violations; they can destroy registered
  correction or revision capacity in ways the declared repair surface cannot
  recover.
```

The newest B2.1 checkpoint is important: the repo now has a Lean information-state lift for fixed-world ambiguity, strictness witnesses for learnable and unlearnable ambiguity, a fake-update phantom corridor witness, an infinite fixed-model realizer, policy/finite-bad-prefix theorems, and a deterministic observation-informativeness theorem:

```text
some stationary information-state policy guarantees from an information state
iff
that information state lies in AdaptiveKernel.
```

This is still claim-bounded. It is a policy-level and finite-refutation correspondence over the lifted information-state system, not yet a fully packaged maximal fixed-world trajectory semantics theorem.

The observation theorem adds the first direct weld to Blackwell-shaped
comparison: when a coarse observation factors through a finer deterministic
observation, any coarse-safe adaptive information state has a nonempty
fine-safe refinement.

The newest recovery checkpoint adds a small Lean interface for bounded repair
reachability and nonrecoverable contraction. It includes finite witnesses for
ordinary state recovery, epistemic recovery, correction-register collapse, and
phantom recoverability. Internally we keep the evocative alias
`self-lobotomy` for the correction-register collapse pattern; formal prose uses
`nonrecoverable revision-capacity loss`.

The follow-on recovery-aware corridor checkpoint makes that interface
load-bearing for the decision floor: if bounded recoverability is the declared
local requirement, an action whose successor nonrecoverably contracts the
declared fact cannot be licensed against that corridor.

The phantom-recoverability checkpoint adds the corresponding warning: a
corrupted recovery frame can counterfeit recoverability and license what the
true recovery-aware corridor refuses. The gate is only as strong as the
declared and certified recovery register.

The latest recovery checkpoint adds the positive twin and a scoped comparison
surface: if a believed recovery frame reflects into the true frame, believed
recovery-aware licenses remain true; declared nonrecoverable-loss profiles can
be compared by down-closed inclusion; and a sacrifice/cancer stress witness
shows why local self-loss is not the same thing as joint loss.

The colonization-axis discovery checkpoint tests a separate question: whether
cross-scale certified viable refinement has signal after ordinary viability,
word-count, recurrence, entropy, and maintenance summaries are matched. The
retained finite audit found a separated signal. That makes colonization a live
candidate descriptive coordinate, not a proof of lushness, value, standing, or
global presentation invariance.

The future-field reorientation checkpoint then culls the tempting overreach:
scalar field-measure, fraction-of-field foreclosure, strong vacancy, population
optimum, and "value-substrate field theory" language are not foundations.
Per-valuer expansion is now a declared theorem layer; cross-valuer comparison and
directive force remain registered debt.

The substrate/deformer checkpoint adds the missing branch-control language:
continuation is oriented downstream dependence, not a commitment to open
futurism; quantum relevance changes preservation adapters, not moral standing;
and technologies, platforms, civilizations, organisms, and memetic systems may
be large deformers without thereby being valuers or agents.

## Decision-Theory Surface

The decision-facing stack is currently grouped under the working title
"Omega Decision Theory" in the notes. Treat that as a working label, not a
finished doctrine.

The stack already behaves differently from several familiar decision-theory
templates:

- It licenses before it ranks: a proposed action must route through certified
  facts and preserve the declared corridor before comparison matters.
- It compares licensed outcome surfaces by value-parametric dominance rather
  than forcing a scalar best action.
- It treats observation quality as part of the decision surface: deterministic
  factorization and finite rational stochastic garbling compile policies in
  Blackwell-shaped ways.
- It keeps arbitration registered: least-violation choice exists only relative
  to declared frontier and violation data, not as a source of moral authority.
- It now has a fixed-world learning surface: sound information-state update can
  widen what is safely maintainable, while fabricated model elimination can
  create phantom safety.

Headline notes:

1. [Omega Decision Stack Checkpoint](docs/research_notes/omega_theory/omega_decision_stack_checkpoint_v0.md)
2. [Omega Decision Floor v0](docs/research_notes/omega_theory/omega_decision_floor_v0.md)
3. [Omega Decision Dominance v0](docs/research_notes/omega_theory/omega_decision_dominance_v0.md)
4. [Deterministic Blackwell Conservativity](docs/research_notes/omega_theory/omega_decision_blackwell_conservativity_v0.md)
5. [Stochastic Blackwell Forward Bridge](docs/research_notes/omega_theory/omega_decision_stochastic_blackwell_v0.md)
6. [Omega Decision Arbitration v0](docs/research_notes/omega_theory/omega_decision_arbitration_v0.md)
7. [Adaptive Fixed-World Corridor B2.1](docs/research_notes/omega_theory/adaptive_fixed_world_corridor_b21.md)
8. [Adaptive Observation Informativeness v0](docs/research_notes/omega_theory/adaptive_observation_informativeness_v0.md)
9. [Recovery Reflection and Nonrecoverable-Loss Dominance v0](docs/research_notes/omega_theory/recovery_reflection_and_loss_dominance_v0.md)
10. [Colonization Axis Report v0](docs/research_notes/omega_theory/colonization_axis_report_v0.md)
11. [Future-Field Reorientation and Declaration Culling v0](docs/research_notes/omega_theory/future_field_reorientation_and_declaration_culling_v0.md)
12. [Substrate Classes and Large Deformers v0](docs/research_notes/omega_theory/substrate_classes_and_large_deformers_v0.md)
13. [Expansion Dominance v0](docs/research_notes/omega_theory/expansion_dominance_v0.md)
14. [Termination Supremum v0](docs/research_notes/omega_theory/termination_supremum_v0.md)
15. [Ensemble Span Report v0](docs/research_notes/omega_theory/ensemble_span_report_v0.md)

The proved layer is still partial. Hypothesized next behavior includes
unsafe-identification/no-go results and eventually endogenous register updates.
None of this currently claims final value, agency, moral standing, or a
complete decision theory.

## Start Here

For the current docs front door:

1. [Docs Front Door](docs/README.md)
2. [Active Surface Area](docs/research_notes/omega_theory/active_surface_area_v0.md)
3. [Claims Ledger](docs/CLAIMS_LEDGER.md)
4. [Omega Decision Stack Checkpoint](docs/research_notes/omega_theory/omega_decision_stack_checkpoint_v0.md)
5. [Adaptive Fixed-World Corridor B2.1](docs/research_notes/omega_theory/adaptive_fixed_world_corridor_b21.md)
6. [Adaptive Observation Informativeness v0](docs/research_notes/omega_theory/adaptive_observation_informativeness_v0.md)
7. [Recovery Frame / Irreversibility Weld v0](docs/research_notes/omega_theory/recovery_frame_irreversibility_weld_v0.md)
8. [Recovery-Aware Corridor v0](docs/research_notes/omega_theory/recovery_aware_corridor_v0.md)
9. [Phantom Recoverability Gate v0](docs/research_notes/omega_theory/phantom_recoverability_gate_v0.md)
10. [Recovery Reflection and Nonrecoverable-Loss Dominance v0](docs/research_notes/omega_theory/recovery_reflection_and_loss_dominance_v0.md)
11. [Colonization Axis Protocol v0](docs/research_notes/omega_theory/colonization_axis_protocol_v0.md)
12. [Colonization Axis Report v0](docs/research_notes/omega_theory/colonization_axis_report_v0.md)
13. [Future-Field Reorientation and Declaration Culling v0](docs/research_notes/omega_theory/future_field_reorientation_and_declaration_culling_v0.md)
14. [Substrate Classes and Large Deformers v0](docs/research_notes/omega_theory/substrate_classes_and_large_deformers_v0.md)
15. [Expansion Dominance v0](docs/research_notes/omega_theory/expansion_dominance_v0.md)
16. [Termination Supremum v0](docs/research_notes/omega_theory/termination_supremum_v0.md)
17. [Ensemble Span Protocol v0](docs/research_notes/omega_theory/ensemble_span_protocol_v0.md)
18. [Ensemble Span Report v0](docs/research_notes/omega_theory/ensemble_span_report_v0.md)
19. [B2 Viability / Safety-Game Docking](docs/research_notes/omega_theory/b2_viability_safety_game_docking_v0.md)
20. [Effective Layers](docs/research_notes/omega_theory/effective_layers_realization_forgetting_emergence_v0.md)
21. [Omega Theory Notes Index](docs/research_notes/omega_theory/README.md)

For first-contact narrative:

1. [Project Overview](docs/PROJECT_OVERVIEW.md)
2. [External Reader Guide](docs/EXTERNAL_READER_GUIDE.md)
3. [Omega Formalism Primer](docs/OMEGA_FORMALISM_PRIMER.md)
4. [Omega Lite Worked Examples](docs/OMEGA_LITE_WORKED_EXAMPLES.md)

For validation and contribution hygiene:

1. [Validation](docs/VALIDATION.md)
2. [Public Results Index](docs/PUBLIC_RESULTS_INDEX.md)
3. [Adversarial Review Guide](docs/ADVERSARIAL_REVIEW_GUIDE.md)
4. [How To Add A Witness](docs/HOW_TO_ADD_A_WITNESS.md)
5. [Human-AI Workflow](docs/HUMAN_AI_WORKFLOW.md)

## Formal Spine

The current Lean work is concentrated under:

```text
formal/lean/OmegaProper/Decision/
formal/lean/OmegaProper/Trajectory/
formal/lean/OmegaProper/Recovery/
formal/lean/AlphaCore/
```

Decision stack entry points:

1. [Decision umbrella](formal/lean/OmegaProper/Decision.lean)
2. [License / ODT0](formal/lean/OmegaProper/Decision/License.lean)
3. [Robust Corridor](formal/lean/OmegaProper/Decision/RobustCorridor.lean)
4. [Ambiguity Family](formal/lean/OmegaProper/Decision/AmbiguityFamily.lean)
5. [Containment](formal/lean/OmegaProper/Decision/Containment.lean)
6. [Trajectory Converse](formal/lean/OmegaProper/Decision/TrajectoryConverse.lean)
7. [Adaptive Fixed World](formal/lean/OmegaProper/Decision/AdaptiveFixedWorld.lean)
8. [Adaptive Observation](formal/lean/OmegaProper/Decision/AdaptiveObservation.lean)
9. [ODT1 Dominance](formal/lean/OmegaProper/Decision/Dominance.lean)
10. [Deterministic Blackwell](formal/lean/OmegaProper/Decision/BlackwellDeterministic.lean)
11. [Stochastic Blackwell](formal/lean/OmegaProper/Decision/BlackwellStochastic.lean)
12. [ODT2 Arbitration](formal/lean/OmegaProper/Decision/Arbitration.lean)
13. [Recovery-Aware Corridor](formal/lean/OmegaProper/Decision/RecoveryAwareCorridor.lean)
14. [Nonrecoverable-Loss Dominance](formal/lean/OmegaProper/Decision/NonrecoverableLossDominance.lean)
15. [Expansion Dominance](formal/lean/OmegaProper/Decision/ExpansionDominance.lean)
16. [Termination Supremum](formal/lean/OmegaProper/Decision/TerminationSupremum.lean)

Trajectory/recovery entry points:

1. [Observed Word Monotonicity](formal/lean/OmegaProper/Trajectory/ObservedWordMonotonicity.lean)
2. [Finite Deformer Profile Strictness](formal/lean/OmegaProper/Trajectory/FiniteDeformerProfileStrictness.lean)
3. [Non-Factorization](formal/lean/OmegaProper/BaselineWitnesses/NonFactorization.lean)
4. [Recovery umbrella](formal/lean/OmegaProper/Recovery.lean)

## What Is Proved So Far

The strongest current results are deliberately conditional and finite:

- Certified licensing: ODT0 actions must route through reflecting facts, preserve a declared corridor, and respect certified quotient use.
- Robust corridors: controlled viability kernels provide the fixed-point floor for persistence under declared constraints.
- Switching ambiguity: shared-action robust viability reduces to an existing robust corridor over a merged system, and per-model corridor intersection can overstate safety.
- Fixed-world learning: information-state adaptive kernels distinguish learnable ambiguity from switching ambiguity and expose fake-update phantom corridors.
- Observation informativeness: deterministic finer observations do not shrink the adaptive corridor when the coarser observation factors through them and the fine information state refines the coarse one.
- Recovery gates: recovery-frame reflection preserves recovery-aware licenses, while corrupted recovery frames can create phantom licenses.
- Declared loss profiles: nonrecoverable-loss profiles form a down-closed inclusion order with failure certificates and a monotone-valuation bridge.
- Declared expansion profiles: expansion profiles form the gain-side mirror order with failure certificates and a monotone-valuation bridge, without creating an expansion gate.
- Termination supremum: contracting a top declared fact loss-dominates every other contraction profile over that per-valuer fact order.
- Colonization-axis discovery: a finite preregistered audit found cross-scale certified viable-refinement separation after matching ordinary viability/language/entropy controls.
- Ensemble span: redundant and orthogonal ensembles can match marginal scalar census while differing in exact span rank/order; full-vector-census controls block relational-surplus overread.
- ODT1 comparison: Hoare/Smyth/Plotkin dominance over licensed outcome surfaces has failure certificates and monotone-valuation acceptance theorems.
- Blackwell-shaped bridges: deterministic factorization is equivalent to policy simulation; finite rational stochastic garbling compiles randomized policies in the forward direction.
- ODT2 scaffold: least-violation arbitration exists only relative to a declared finite frontier and violation score.
- Process coherence: path/language transport blocks the false principle that edge-image exactness is enough for process truth.

These are not claims that value or agency has been solved. They are constraints on the maps, policies, and updates that later value- or agency-facing claims would need to consume.

## Current Open Edges

Near-term work should now prefer:

1. Audit ensemble-span v0 and decide whether to run an independent larger variant or move to relational composability.
2. Independent colonization-axis pair or audited `ColonizationOrder.lean` before any cross-scale lushness claim.
3. NOLP / compensation claims only after the expansion mirror and ensemble-span result have been audited.
4. Endogenous register/no-laundering after recovery-frame reflection and NOLP are typed.
5. Plural corridor composition, quantum, or large-deformer relativity only after those interfaces are stable.

## Claim Boundary

This repo does not currently prove:

- value;
- valuerhood;
- agency;
- selfhood;
- identity;
- moral standing;
- a final decision theory;
- a full stochastic Blackwell theorem;
- a full POMDP theory;
- Omega validation.

It proves and tests lower machinery needed before those claims can be made responsibly.

## Repository Map

```text
formal/lean/
  Lean proof-assistant workspace for Alpha, trajectory, recovery, decision,
  corridor, dominance, and adaptive-learning theorems.

omega/
  Python instruments, finite witness tooling, stochastic-channel probes,
  and validation scripts.

docs/
  Public front doors, claims ledger, theory notes, validation reports,
  specs, references, and paper drafts.

docs/research_notes/omega_theory/
  Dense theory notes and theorem-positioning checkpoints.

results/
  Retained local result artifacts.
```

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE).

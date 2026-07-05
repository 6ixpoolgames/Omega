# Omega

[![Lean AlphaOmega](https://github.com/6ixpoolgames/Omega/actions/workflows/lean-alphaomega.yml/badge.svg?branch=master)](https://github.com/6ixpoolgames/Omega/actions/workflows/lean-alphaomega.yml)
[![Baseline Witness Smoke](https://github.com/6ixpoolgames/Omega/actions/workflows/baseline-witness-smoke.yml/badge.svg?branch=master)](https://github.com/6ixpoolgames/Omega/actions/workflows/baseline-witness-smoke.yml)
[![Validation Router](https://github.com/6ixpoolgames/Omega/actions/workflows/validation-router.yml/badge.svg?branch=master)](https://github.com/6ixpoolgames/Omega/actions/workflows/validation-router.yml)

Omega is a research program about alignment, abstraction integrity, and value-bearing continuation.

The repo is not a completed theory of value, agency, identity, moral standing, or Omega validation. It is a formal toolbench for a lower question:

```text
When can a representation, policy, update rule, or decision surface be trusted
not to erase, fabricate, or hide continuation-relevant structure?
```

The current center of gravity is the decision/corridor stack. It combines certified map use, robust viability corridors, deterministic and stochastic Blackwell-shaped comparison bridges, registered arbitration scaffolding, and an adaptive fixed-world learning layer.

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
  sound update; fabricated model elimination can create phantom safety.
```

The newest B2.1 checkpoint is important: the repo now has a Lean information-state lift for fixed-world ambiguity, strictness witnesses for learnable and unlearnable ambiguity, a fake-update phantom corridor witness, an infinite fixed-model realizer, and a policy-level theorem:

```text
some stationary information-state policy guarantees from an information state
iff
that information state lies in AdaptiveKernel.
```

This is still claim-bounded. It is a policy-level fixed-point correspondence over the lifted information-state system, not yet a fully packaged trajectory/maximal fixed-world semantics theorem.

## Start Here

For the current docs front door:

1. [Docs Front Door](docs/README.md)
2. [Active Surface Area](docs/research_notes/omega_theory/active_surface_area_v0.md)
3. [Claims Ledger](docs/CLAIMS_LEDGER.md)
4. [Omega Decision Stack Checkpoint](docs/research_notes/omega_theory/omega_decision_stack_checkpoint_v0.md)
5. [Adaptive Fixed-World Corridor B2.1](docs/research_notes/omega_theory/adaptive_fixed_world_corridor_b21.md)
6. [B2 Viability / Safety-Game Docking](docs/research_notes/omega_theory/b2_viability_safety_game_docking_v0.md)
7. [Effective Layers](docs/research_notes/omega_theory/effective_layers_realization_forgetting_emergence_v0.md)
8. [Omega Theory Notes Index](docs/research_notes/omega_theory/README.md)

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
8. [ODT1 Dominance](formal/lean/OmegaProper/Decision/Dominance.lean)
9. [Deterministic Blackwell](formal/lean/OmegaProper/Decision/BlackwellDeterministic.lean)
10. [Stochastic Blackwell](formal/lean/OmegaProper/Decision/BlackwellStochastic.lean)
11. [ODT2 Arbitration](formal/lean/OmegaProper/Decision/Arbitration.lean)

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
- ODT1 comparison: Hoare/Smyth/Plotkin dominance over licensed outcome surfaces has failure certificates and monotone-valuation acceptance theorems.
- Blackwell-shaped bridges: deterministic factorization is equivalent to policy simulation; finite rational stochastic garbling compiles randomized policies in the forward direction.
- ODT2 scaffold: least-violation arbitration exists only relative to a declared finite frontier and violation score.
- Process coherence: path/language transport blocks the false principle that edge-image exactness is enough for process truth.

These are not claims that value or agency has been solved. They are constraints on the maps, policies, and updates that later value- or agency-facing claims would need to consume.

## Current Open Edges

Near-term work should now prefer:

1. A B2.1 theorem map and documentation cleanup.
2. The full trajectory/maximal fixed-world semantics assembly, if needed for a paper-style theorem statement.
3. Sound observation-informativeness monotonicity: certified better observations should not shrink the adaptive corridor.
4. A general guard theorem for process-coherence attribution.
5. Recovery/irreversibility welds for unsafe identification and forbidden probes.
6. Endogenous register updates only after the observation/update layer is sound.
7. Plural corridor composition after the epistemic/register layer is stable.

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

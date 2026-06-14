# Omega

[![Lean AlphaOmega](https://github.com/6ixpoolgames/Omega/actions/workflows/lean-alphaomega.yml/badge.svg?branch=master)](https://github.com/6ixpoolgames/Omega/actions/workflows/lean-alphaomega.yml)
[![Baseline Witness Smoke](https://github.com/6ixpoolgames/Omega/actions/workflows/baseline-witness-smoke.yml/badge.svg?branch=master)](https://github.com/6ixpoolgames/Omega/actions/workflows/baseline-witness-smoke.yml)
[![Validation Router](https://github.com/6ixpoolgames/Omega/actions/workflows/validation-router.yml/badge.svg?branch=master)](https://github.com/6ixpoolgames/Omega/actions/workflows/validation-router.yml)

Omega is a research program for treating alignment as the problem of preserving the corridor of compatible, value-bearing futures. This repo is the formal toolbench for that program: it proves small, auditable theorems about when abstractions can be trusted, when proxies fail, and when models fabricate continuation or hide irreversible loss.

If the long-term goal is to mark the safe path for intelligent agency, the first problem is not drawing the path. It is proving that the map is not lying.

## The Thesis

Alignment is not only an objective-selection problem. It is also an abstraction-integrity problem.

Any intelligent system acts through models, metrics, summaries, boundaries, policies, and compressed presentations of the world. Those presentations can fail in several dangerous ways:

- They can merge states whose consequences are different.
- They can make two futures look equally viable when one has lost a necessary distinction.
- They can create phantom reachability that is not present in the exact system.
- They can preserve a proxy while destroying the target the proxy was supposed to protect.

Omega studies the formal conditions under which those failures can be detected or ruled out.

## Alpha-Omega In Plain English

The project uses "Alpha-Omega" for the two ends of one structure.

Alpha is the primitive end: relation, distinction, asymmetry, and consequence. It asks how a difference can matter before we assume selves, agents, preferences, rewards, or moral facts.

Omega is the terminal ambition: the maximal compatible development of value-bearing continuation. It asks what it would mean for intelligent agency as a whole to stay inside the narrow corridor where many compatible futures remain open enough for valuers to exist and flourish.

The point of the lower formal stack is to earn the upper language. We do not start by defining a self, an agent, or a value function. We start with consequence-bearing distinctions and ask what abstractions are allowed to erase.

## Why Proto-Teleology Matters

The current milestone is proto-teleology.

This does not mean purpose, intention, morality, or agency. It means directed consequence before any of those are assumed:

```text
A difference matters when erasing it changes what can follow.
```

That is already useful for weak, constraint-based alignment. Even before a full theory of value or valuerhood, we can reject presentations, policies, metrics, or abstractions that hide consequence-bearing loss, invent impossible continuation, or merge distinctions that declared continuation tests separate.

That makes proto-teleology the bridge between low-level formal structure and the larger Gradient Ethics idea, also described as value preservation under uncertainty: under uncertainty and irreversibility, preserving the conditions for future value-bearing continuation becomes a structural safety constraint.

## What Is Proved So Far

The strongest current results are deliberately small.

- **Sound quotients:** a quotient is safe only when its kernel is contained in consequence-identifiability. See [SoundQuotient.lean](formal/lean/OmegaProper/Trajectory/SoundQuotient.lean) and [standard core compression](docs/research_notes/omega_theory/standard_core_compression_v0.md).
- **Class soundness:** a valid class is a clique of pairwise compatibility, not merely a connected component. See [class soundness as clique](docs/research_notes/omega_theory/class_soundness_as_clique_v0.md).
- **Non-factorization:** if a target changes while a summary stays fixed, the target cannot factor through that summary. This is the repo's basic anti-Goodhart instrument. See [NonFactorization.lean](formal/lean/OmegaProper/BaselineWitnesses/NonFactorization.lean) and the [witness index](docs/research_notes/omega_theory/nonfactorization_witness_index_v0.md).
- **Exact recovery:** finite declared recovery is equivalent to observed support disjointness. See [exact recovery support disjointness](docs/research_notes/omega_theory/exact_recovery_support_disjointness_v0.md).
- **Presentation invariance:** sound presentations cannot erase merge-separated consequence structure. See [presentation-invariant consequence](docs/research_notes/omega_theory/presentation_invariant_consequence_v0.md).
- **Reachability and viability:** reach and viability are formalized as fixed-point objects, with reflection contracts for safe abstraction. See [reachability/viability](docs/research_notes/omega_theory/reachability_viability_v0.md), [reachability reflection](docs/research_notes/omega_theory/reachability_reflection_v0.md), and [viability reflection](docs/research_notes/omega_theory/viability_reflection_v0.md).
- **Bad abstractions:** finite theorems show unsound presentations can fabricate reachability or viability and can hide loss. See [phantom reachability](docs/research_notes/omega_theory/phantom_reachability_under_unsound_quotient_v0.md), [hidden reach loss](docs/research_notes/omega_theory/hidden_reach_loss_under_bad_presentation_v0.md), and [hidden viability loss](docs/research_notes/omega_theory/hidden_viability_loss_under_bad_presentation_v0.md).
- **Loss-aware contracts:** stronger contracts separate safe abstraction from tempting but insufficient one-way simulations. See [loss-aware presentation contracts](docs/research_notes/omega_theory/loss_aware_presentation_contract_v0.md), [loss-aware strictness](docs/research_notes/omega_theory/loss_aware_presentation_strictness_v0.md), and [safe loss visibility](docs/research_notes/omega_theory/safe_loss_visibility_v0.md).

These are toy-world theorems by design. Small finite worlds are where false abstraction principles are easiest to expose. If a proposed metric or quotient already fails there, it has not earned trust in a larger substrate.

## Why This Matters For Alignment

This repo is adjacent to familiar ideas in Goodhart's law, abstract interpretation, viability theory, option value, empowerment, impact measures, and attainable-utility or power-seeking analyses. The contribution is not that those literatures are wrong. The contribution is a focused proof discipline for a recurring alignment question:

```text
Does this summary preserve the consequence-bearing target it is being used to stand in for?
```

That question matters for benchmarks, interpretability proxies, reward models, safety constraints, agent boundaries, corrigibility metrics, and long-horizon planning abstractions. A model can look aligned under a lossy presentation while the exact system has already lost the thing the presentation was meant to preserve.

The alignment-facing ambition is to turn this into "yellow paint" for the viable corridor: not a total value function, but a machine-checkable family of constraints showing when a proposed abstraction, policy, or continuation has preserved enough of the value-bearing substrate to remain on the path.

## Current Status

This is active research, not a completed theory of value.

The repo currently supports a disciplined proto-teleological floor:

```text
consequence-bearing distinction
-> sound identification / sound presentation
-> target and profile invariance
-> fixed-point reachability and viability
-> hidden-loss and phantom-continuation counterexamples
-> loss-aware abstraction contracts
```

What remains open is the ascent from these constraints to richer notions of valuerhood, agency, joint viability, recurrence, and ultimately Omega as a compatible value-bearing continuation structure. Those terms are motivations and targets, not already-validated claims.

## Start Here

For the high-level orientation:

1. [Project Overview](docs/PROJECT_OVERVIEW.md)
2. [Omega Formalism Primer](docs/OMEGA_FORMALISM_PRIMER.md)
3. [External Reader Guide](docs/EXTERNAL_READER_GUIDE.md)
4. [Standard Core Compression](docs/research_notes/omega_theory/standard_core_compression_v0.md)
5. [Dynamics Abstraction Status](docs/research_notes/omega_theory/dynamics_abstraction_status_v0.md)

For the current theorem spine:

1. [Sound Quotient](formal/lean/OmegaProper/Trajectory/SoundQuotient.lean)
2. [Class Soundness as Clique](formal/lean/OmegaProper/Trajectory/ClassSoundnessAsClique.lean)
3. [Non-Factorization](formal/lean/OmegaProper/BaselineWitnesses/NonFactorization.lean)
4. [Exact Recovery Support](formal/lean/OmegaProper/BaselineWitnesses/ExactRecoverySupport.lean)
5. [Loss-Aware Presentation Contract](formal/lean/OmegaProper/Trajectory/LossAwarePresentationContract.lean)
6. [AlphaOmega Lean Umbrella](formal/lean/AlphaOmega.lean)

For validation and claim hygiene:

1. [Validation](docs/VALIDATION.md)
2. [Claims Ledger](docs/CLAIMS_LEDGER.md)
3. [Public Results Index](docs/PUBLIC_RESULTS_INDEX.md)
4. [Bad Panel Taxonomy](docs/research_notes/omega_theory/bad_panel_taxonomy_v0.md)

For provenance and workflow:

1. [Human-AI Workflow](docs/HUMAN_AI_WORKFLOW.md)
2. [No-Self Evidence Archival Note](docs/references/no_self_evidence_archival_note.md)

## Roadmap

Near-term work is focused on:

1. Constructor theorems for loss-aware presentation contracts.
2. Irreversible-loss corridor theorems.
3. Joint viability and pairwise-vs-joint compatibility failures.
4. Stronger finite adapters and generated witness families.
5. A cleaner bridge from viability constraints to Gradient Ethics.
6. A more mature account of value-bearing trajectories without assuming self or identity as primitives.

## Repository Map

```text
formal/lean/
  Lean proof-assistant sandbox for Alpha, consequence, presentation,
  reachability, viability, and abstraction-contract theorems.

omega/
  Python instruments, finite witness tooling, stochastic-channel probes,
  and validation scripts.

docs/research_notes/omega_theory/
  Dense theory notes, theorem scaffolds, and status reports.

docs/papers/drafts/
  Draft paper artifacts for internal review.

results/
  Retained local result artifacts.
```

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE).

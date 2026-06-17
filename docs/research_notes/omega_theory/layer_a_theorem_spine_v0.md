# Layer A Theorem Spine v0

Status: consolidation note
Scope: current proved Layer A theorem clusters and finite witnesses
Claim boundary: not Omega validation, not value theory, not agency, not valuerhood, not alignment solved

## Purpose

This note is the short map of what the formal stack currently proves.

The current project should be read as a formal anti-Goodhart and
sound-presentation discipline for consequence-bearing continuation. The core
question is:

```text
When can a summary, quotient, presentation, boundary, or support be trusted
not to lie about continuation facts?
```

The strongest current answer is not a scalar value metric. It is a collection
of small theorem clusters showing when abstraction is sound, when proxies fail,
when future facts are fabricated or hidden, and when recurrent support carries
or loses a consequence distinction.

## Two compact laws

Two statements currently carry most of the public load.

First:

```text
If the target does not factor through the summary, the summary is not a safe
proxy for that target.
```

Lean spine:

```text
same summary + different target => NonFactorization
```

Second:

```text
A quotient or presentation is sound only when every merge it performs is
licensed by consequence-identifiability.
```

Lean spine:

```text
sound quotient = kernel contained in consequence-identifiability
```

These are not Omega. They are the map-integrity floor beneath any later
Omega-like or Gradient Ethics claim.

## 1. Consequence kernel core

Main files:

- [ConsequenceRelation.lean](../../../formal/lean/OmegaProper/Trajectory/ConsequenceRelation.lean)
- [ConsequenceClasses.lean](../../../formal/lean/OmegaProper/Trajectory/ConsequenceClasses.lean)
- [SoundQuotient.lean](../../../formal/lean/OmegaProper/Trajectory/SoundQuotient.lean)
- [ClassSoundnessAsClique.lean](../../../formal/lean/OmegaProper/Trajectory/ClassSoundnessAsClique.lean)
- [PresentationInvariant.lean](../../../formal/lean/OmegaProper/Trajectory/PresentationInvariant.lean)
- [PresentationInvariantExamples.lean](../../../formal/lean/OmegaProper/Trajectory/PresentationInvariantExamples.lean)

Current content:

```text
ConsequenceCompatible is directional.
ConsequenceIdentifiable requires both directions.
ConsequenceMergeSeparated blocks symmetric identification.
SoundQuotient says every quotient merge must be consequence-identifiable.
Class soundness is clique soundness, not connected-component soundness.
Sound presentations cannot erase consequence-separated pairs.
```

What this blocks:

```text
one-way allowance as identity;
chain-connectedness as class validity;
unsound quotient merges;
presentation choices that erase merge-separated distinctions.
```

Public phrase:

```text
A representation is sound only if every merge it performs is licensed by the
consequence kernel.
```

## 2. Non-factorization core

Main files:

- [NonFactorization.lean](../../../formal/lean/OmegaProper/BaselineWitnesses/NonFactorization.lean)
- [FactorizationCriterion.lean](../../../formal/lean/OmegaProper/BaselineWitnesses/FactorizationCriterion.lean)
- [InvarianceNonFactorization.lean](../../../formal/lean/OmegaProper/BaselineWitnesses/InvarianceNonFactorization.lean)
- [CoordinateSplit.lean](../../../formal/lean/OmegaProper/BaselineWitnesses/CoordinateSplit.lean)
- [ReachabilityDeclaredRecovery.lean](../../../formal/lean/OmegaProper/BaselineWitnesses/ReachabilityDeclaredRecovery.lean)
- [MutualInformationDeclaredRecovery.lean](../../../formal/lean/OmegaProper/BaselineWitnesses/MutualInformationDeclaredRecovery.lean)
- [CompressionScoreMergeSoundness.lean](../../../formal/lean/OmegaProper/BaselineWitnesses/CompressionScoreMergeSoundness.lean)
- [ExactRecoverySupport.lean](../../../formal/lean/OmegaProper/BaselineWitnesses/ExactRecoverySupport.lean)
- [MarginalCouplingNonFactorization.lean](../../../formal/lean/OmegaProper/BaselineWitnesses/MarginalCouplingNonFactorization.lean)

Current content:

```text
FactorsThrough f g means a post-map can recover target g from summary f.
NonFactorization f g is witnessed by x,y with f x = f y and g x != g y.
Fiber constancy is equivalent to no such witness.
Summary invariance plus target change gives non-factorization.
Exact declared recovery exists iff observed supports of declared classes do
not collide.
```

What this blocks:

```text
proxy metrics that agree while declared targets differ;
benchmark summaries treated as safety targets without factorization evidence;
coordinate-symmetric summaries used for coordinate-specific targets;
local or marginal summaries treated as joint-coupling evidence.
```

Public phrase:

```text
If two systems have the same score but different safety-relevant targets, the
score does not determine the target.
```

## 3. Fixed-point dynamics core

Main files:

- [PredicateFixpoint.lean](../../../formal/lean/OmegaProper/Trajectory/PredicateFixpoint.lean)
- [ReachabilityViability.lean](../../../formal/lean/OmegaProper/Trajectory/ReachabilityViability.lean)
- [TrajectorySemantics.lean](../../../formal/lean/OmegaProper/Trajectory/TrajectorySemantics.lean)
- [SustainingViableClass.lean](../../../formal/lean/OmegaProper/Trajectory/SustainingViableClass.lean)
- [RecurrentViableClass.lean](../../../formal/lean/OmegaProper/Trajectory/RecurrentViableClass.lean)
- [ViableTrajectoryLanguage.lean](../../../formal/lean/OmegaProper/Trajectory/ViableTrajectoryLanguage.lean)

Current content:

```text
Reachability and viability are fixed-point objects over transition systems.
Reachability matches finite paths to the target.
Viability supplies arbitrarily long finite safe prefixes.
Recurrent viable classes add closed, safe, sustaining, internally connected
support structure.
```

Claim boundary:

```text
The stack does not claim an infinite trajectory converse without extra
compactness, choice, or finite-branching assumptions.
```

What this blocks:

```text
future-language claims without transition semantics;
viability claims with no sustaining support;
recurrent support claims from mere endpoint viability.
```

Public phrase:

```text
Reachability and viability are corridor predicates, not metaphors.
```

## 4. Presentation, reflection, and loss visibility

Main files:

- [PhantomReachability.lean](../../../formal/lean/OmegaProper/Trajectory/PhantomReachability.lean)
- [PhantomViability.lean](../../../formal/lean/OmegaProper/Trajectory/PhantomViability.lean)
- [ReachabilityReflection.lean](../../../formal/lean/OmegaProper/Trajectory/ReachabilityReflection.lean)
- [ViabilityReflection.lean](../../../formal/lean/OmegaProper/Trajectory/ViabilityReflection.lean)
- [HiddenLossUnderBadPresentation.lean](../../../formal/lean/OmegaProper/Trajectory/HiddenLossUnderBadPresentation.lean)
- [HiddenViabilityLossUnderBadPresentation.lean](../../../formal/lean/OmegaProper/Trajectory/HiddenViabilityLossUnderBadPresentation.lean)
- [HiddenJointViabilityLossUnderBadPresentation.lean](../../../formal/lean/OmegaProper/Trajectory/HiddenJointViabilityLossUnderBadPresentation.lean)
- [SafePresentationContract.lean](../../../formal/lean/OmegaProper/Trajectory/SafePresentationContract.lean)
- [SafeLossVisibility.lean](../../../formal/lean/OmegaProper/Trajectory/SafeLossVisibility.lean)
- [LossAwarePresentationContract.lean](../../../formal/lean/OmegaProper/Trajectory/LossAwarePresentationContract.lean)
- [LossAwarePresentationConstructors.lean](../../../formal/lean/OmegaProper/Trajectory/LossAwarePresentationConstructors.lean)
- [LossAwarePresentationStrictness.lean](../../../formal/lean/OmegaProper/Trajectory/LossAwarePresentationStrictness.lean)

Current content:

```text
Bad presentations can fabricate reachability.
Bad presentations can fabricate viability.
Bad presentations can hide reachability, viability, and joint-viability loss.
Reflection contracts prevent phantom reachability/viability.
Loss-aware contracts make declared loss visible rather than hidden.
Strictness witnesses show why weaker contracts are not enough.
```

What this blocks:

```text
phantom futures;
phantom safe corridors;
abstract models that hide exact loss;
post-hoc abstraction choices that preserve the proxy while destroying the
declared target.
```

Public phrase:

```text
Before drawing the safe path, prove that the map is not fabricating or hiding
the path.
```

## 5. Recurrent support integrity core

Main files:

- [DistinctionSupport.lean](../../../formal/lean/OmegaProper/Trajectory/DistinctionSupport.lean)
- [SupportRestriction.lean](../../../formal/lean/OmegaProper/Trajectory/SupportRestriction.lean)
- [SupportMinimality.lean](../../../formal/lean/OmegaProper/Trajectory/SupportMinimality.lean)
- [SupportUnderPerturbation.lean](../../../formal/lean/OmegaProper/Trajectory/SupportUnderPerturbation.lean)
- [RecurrentSupportRobustness.lean](../../../formal/lean/OmegaProper/Trajectory/RecurrentSupportRobustness.lean)
- [IrreversibleRecurrentSupportLoss.lean](../../../formal/lean/OmegaProper/Trajectory/IrreversibleRecurrentSupportLoss.lean)
- [RecurrentSupportTransfer.lean](../../../formal/lean/OmegaProper/Trajectory/RecurrentSupportTransfer.lean)
- [RecurrentSupportRestoration.lean](../../../formal/lean/OmegaProper/Trajectory/RecurrentSupportRestoration.lean)
- [RecurrentSupportPathTransfer.lean](../../../formal/lean/OmegaProper/Trajectory/RecurrentSupportPathTransfer.lean)
- [ParameterizedRecurrentSupport.lean](../../../formal/lean/OmegaProper/Trajectory/ParameterizedRecurrentSupport.lean)
- [RecurrentSupportExtension.lean](../../../formal/lean/OmegaProper/Trajectory/RecurrentSupportExtension.lean)
- [RecurrentSupportLineage.lean](../../../formal/lean/OmegaProper/Trajectory/RecurrentSupportLineage.lean)
- [RecurrentSupportSuccessorDistinction.lean](../../../formal/lean/OmegaProper/Trajectory/RecurrentSupportSuccessorDistinction.lean)
- [RecurrentSupportPerturbationBudget.lean](../../../formal/lean/OmegaProper/Trajectory/RecurrentSupportPerturbationBudget.lean)
- [JointRecurrentSupport.lean](../../../formal/lean/OmegaProper/Trajectory/JointRecurrentSupport.lean)

Current content:

```text
A support can carry a merge-separated consequence distinction.
Restricting support can destroy carrying.
Endpoint support alone is not enough.
Endpoint viability and forward reachability are not enough.
Recurrent carrying can be lost when return structure is lost.
Edge-level transfer gives a sufficient preservation contract.
Path-level transfer allows internal rerouting.
Restoration can return recurrent carrying when recurrence is repaired.
The one-way loss pattern holds for every bounded finite cycle of size n + 2.
Support-extension contracts allow carrying to transfer from support C into
larger support D when old internal paths are replaceable inside D.
Support-lineage contracts allow carrying to transfer between incomparable
supports when the target support explicitly carries the same declared
endpoints.
Successor-distinction contracts allow carrying to transfer from source pair
x,y to translated target pair x',y' under an explicit merge-separation-
preserving relation.
A first exact perturbation-budget floor shows that same dynamics cannot
destroy recurrent carrying, while one return-edge removal can destroy it even
when endpoint viability and forward reachability remain.
Individual recurrent carrying under separate safety predicates need not
compose into recurrent carrying under shared joint safety.
```

What this blocks:

```text
identity-by-wiring;
endpoint viability as support integrity;
forward reachability as recurrent carrying;
exact edge preservation as the only repair route;
two-state toy-world dismissal of the basic one-way-loss pattern;
same-support transfer as the only support-integrity route.
subset inclusion as the only moving-support route.
same-endpoint preservation as the only lineage route.
endpoint viability and forward reachability as perturbation robustness.
isolated recurrent carrying as joint compatibility.
```

Public phrase:

```text
Some consequence distinctions need recurrent return structure, not just
surviving endpoints or one-way reachability.
```

## Current milestone

The safe milestone sentence is:

```text
Layer A now has a first finite local perturbation calculus for recurrently
carried consequence distinctions: support, loss, preservation, restoration,
rerouting, support extension, and a bounded finite family of one-way-loss
loss witnesses; it also has first incomparable-support lineage, successor-
distinction handoff, perturbation-budget, and joint recurrent-support
witnesses.
```

This is still local and finite. It is not agency, identity, value, valuerhood,
alignment, or Omega proper.

## Why this matters for Gradient Ethics

Gradient Ethics wants to reason about the preservation of value-bearing
possibility under uncertainty and irreversibility.

Layer A does not yet define value. It supports the upstream safety discipline:

```text
do not trust a proxy unless the target factors through it;
do not trust a quotient unless its merges are consequence-sound;
do not trust a presentation unless it reflects relevant continuation facts;
do not equate endpoint survival with recurrent carrying;
do not equate forward reachability with preserved support.
```

In other words, before asking which futures are valuable, Layer A asks whether
the formal map used to reason about futures is allowed to erase, fabricate, or
hide the distinctions the downstream target depends on.

## What remains open

The next formal bottlenecks are:

1. Boundary-invariant support:
   recurrent carrying survives sound re-presentation.

2. General perturbation budgets:
   minimum cuts, repair budgets, and probabilistic adapter-level robustness.

3. Joint recurrent support contracts:
   positive conditions under which multiple supports remain jointly carrying.

4. Agency and valuer candidates:
   recurrent support becomes controlled, self-maintaining, and value-capable.

5. Omega:
   maximal compatible development of value-bearing continuation.

Only items 1-3 are near-term formal work. Items 4-5 remain long-run targets.

## Related notes

- [standard_core_compression_v0.md](standard_core_compression_v0.md)
- [bad_panel_taxonomy_v0.md](bad_panel_taxonomy_v0.md)
- [boundary_invariant_continuation_roadmap_v0.md](boundary_invariant_continuation_roadmap_v0.md)
- [joint_recurrent_support_v0.md](joint_recurrent_support_v0.md)
- [safe_presentation_contract_v0.md](safe_presentation_contract_v0.md)
- [loss_aware_presentation_contract_v0.md](loss_aware_presentation_contract_v0.md)
- [recurrent_support_perturbation_floor_v0.md](recurrent_support_perturbation_floor_v0.md)
- [recurrent_support_perturbation_budget_v0.md](recurrent_support_perturbation_budget_v0.md)
- [parameterized_recurrent_support_v0.md](parameterized_recurrent_support_v0.md)
- [recurrent_support_extension_v0.md](recurrent_support_extension_v0.md)
- [recurrent_support_lineage_v0.md](recurrent_support_lineage_v0.md)
- [recurrent_support_successor_distinction_v0.md](recurrent_support_successor_distinction_v0.md)

# Omega Formal Lean Sandbox

Status: local proof-assistant pressure test

This directory contains the Lean 4 sandbox for the Omega formalism. It is not
the full quantale-presheaf formalization. The current root target is the
support-level normal lax distinction-transport calculus.

## Local Toolchain

This workspace uses a portable Lean toolchain:

```powershell
.tools\lean-4.30.0\lean-4.30.0-windows\bin\lean.exe --version
```

Do not assume Lean is globally installed. From the repository root, use:

```powershell
$env:PATH = (Resolve-Path '.tools\lean-4.30.0\lean-4.30.0-windows\bin').Path + ';' + $env:PATH
```

Then build:

```powershell
cd formal\lean
lake build OmegaCore
```

The sandbox now depends on `mathlib` through `lakefile.lean`:

```text
mathlib4 v4.30.0
```

The local cache fetch may fail on this Windows workspace, so required mathlib
modules can be built from source by `lake build OmegaCore`.

## Current Checked Content

`OmegaCore/DistTrans.lean` defines the support-level category target:

```text
PreorderFrame:
  minimal preorder frame

DistTransport:
  source-weakening / target-strengthening closed relation

DistTransport.id:
  identity transport as refinement

DistTransport.compose:
  ordinary relational composition of transports
```

Checked relation-level category laws:

```text
DistTransport.id_closed
DistTransport.compose_closed
DistTransport.left_id_iff
DistTransport.right_id_iff
DistTransport.assoc_iff
```

`OmegaCore/NormalLax.lean` defines the current root Lean skeleton:

```text
ContextCategory:
  relational contexts and composable unfoldings

NormalLaxDistinctionTransport:
  normal lax assignment from contexts/unfoldings to DistTrans

NormalLaxDistinctionTransport.Recovers:
  recoverability as support-level distinction transport

NormalLaxDistinctionTransport.NonErasing:
  non-erasure for declared distinction requirements
```

Checked normal-lax consequences:

```text
NormalLaxDistinctionTransport.identity_recoverability
NormalLaxDistinctionTransport.recoverability_weaken_source
NormalLaxDistinctionTransport.recoverability_strengthen_target
NormalLaxDistinctionTransport.compositional_recoverability
NormalLaxDistinctionTransport.non_erasure_monotonicity
```

`OmegaCore/Recurrent.lean` defines finite-chain recurrent recoverability:

```text
Chain:
  finite composable chain of relational unfoldings

Chain.toHom:
  composite unfolding induced by a chain

RecoverChain:
  stepwise local recovery along a declared finite chain
```

Checked recurrent-recoverability theorem:

```text
recoverChain_sound:
  if a distinction is recovered stepwise along a finite chain, then it is
  recovered through the composed unfolding.
```

This formalizes repeated recovery across a declared unfolding sequence.
Nontriviality, churn, turnover, perturbation, or renewal conditions remain
adapter-specific and are not part of the Lean root skeleton.

`OmegaCore/Completion.lean` defines the finite maximal-completion skeleton:

```text
SubsetMaximal:
  admissible family with no one-way admissible extension

MaxSizedInList:
  admissible listed family whose size dominates every listed admissible family

exists_subsetMaximal_of_finite_enumeration:
  if admissible families are covered by a finite list and at least one is
  admissible, then a subset-maximal admissible family exists.

exists_subsetMaximal_finset:
  if `alpha` is finite and at least one `Finset alpha` candidate family is
  admissible, then a subset-maximal admissible family exists.
```

This file stays abstract over family type, inclusion-like relation, size, and
admissibility. It does not define compatibility, proto-valuers, valuers, ethics,
Future Field Atlas semantics, or empirical adapters.

The explicit `List` theorem remains as the minimal finite-search constructor.
The `Finset`/`Fintype` specialization is now checked with mathlib.

`OmegaCore/Counterexamples.lean` defines finite completion counterexamples:

```text
AdmAtMostTwo:
  all two-element families in Fin 3 are admissible, while the full
  three-element family is not

AdmFork:
  downward-closed fork admissibility with two incompatible maximal branches

GreatestFinset:
  admissible family containing every admissible family
```

Checked counterexamples:

```text
pairwise_admissible_not_joint
distinct_maximal_completions
no_greatest_completion
```

These show that completion structure is n-ary, subset-maximal, and generally
family-valued. They remain abstract finite admissibility examples and do not
define compatibility, proto-valuers, valuers, ethics, Future Field Atlas
semantics, or empirical adapters.

`OmegaCore/MarginalJoint.lean` defines a finite distinction-transport
counterexample:

```text
SrcD:
  source distinctions bot, margA, margB, joint

TgtD:
  target distinctions bot, outA, outB

Phi:
  a DistTransport that carries margA to outA and margB to outB, but does not
  carry the strictly joint distinction
```

Checked theorem:

```text
marginal_non_erasure_not_joint_non_erasure:
  marginal-like non-erasure does not imply strictly joint non-erasure
```

This is the support-level root-calculus analogue of "marginal continuation is
not compatibility." It does not define compatibility, joint field semantics,
Future Field Atlas semantics, proto-valuers, valuers, ethics, or empirical
adapters.

`OmegaCore/AdapterFailures.lean` defines finite transfer-boundary examples:

```text
raw_source_weakening_failure:
  a raw relation can fail source-weakening closure

rawPhi_not_distTransport_exact:
  no exact DistTransport can package that source-weakening-failing relation

raw_target_strengthening_failure:
  a raw relation can fail target-strengthening closure

rawPsi_not_distTransport_exact:
  no exact DistTransport can package that target-strengthening-failing relation

raw_laxity_failure:
  local recoveries can exist while the declared composite recovery is absent

laxity_subset_failure:
  valid one-step transports still fail theorem transfer when the declared
  composite transport does not contain their composed support
```

These examples show that theorem transfer requires actual satisfaction of the
root laws. Invalid or extended adapters must report which laws fail and which
theorems no longer apply.

`OmegaCore/Basic.lean` defines:

```text
DistinctionFrame:
  minimal preorder-like distinction frame

ValueFrame:
  ordered tensor structure for asymmetry/support values

Recovers:
  structural pullback plus thresholded asymmetry support

NonErasing:
  every declared required distinction has a recovering witness
```

Checked lemmas:

```text
recoverability_weaken_source
recoverability_strengthen_target
non_erasure_monotonicity
compositional_recoverability
```

`OmegaCore/PrimitiveWitness.lean` defines a prior substrate-independent witness
calculus smoke:

```text
PrimitiveCalculus:
  contexts, relations, distinction preorders, typed asymmetry witnesses,
  witness weakening/strengthening, and sequential witness composition

PrimitiveWitness.Recovers:
  recoverability as existence of a typed distinction-transport witness

PrimitiveWitness.NonErasing:
  non-erasure for a declared distinction requirement set

PrimitiveWitness.JointPresentation:
  presentation-relative joint contexts and embeddings
```

Checked primitive-witness lemmas:

```text
PrimitiveWitness.recoverability_weaken_source
PrimitiveWitness.recoverability_strengthen_target
PrimitiveWitness.non_erasure_monotonicity
PrimitiveWitness.compositional_recoverability
```

`PrimitiveWitness.IndiscreteUnit` is a deliberately trivial type-checking model.
It is not an empirical adapter and not evidence for Omega. The normal-lax
`DistTrans` layer is now the preferred root skeleton.

The file currently contains no `sorry`, `admit`, or Lean `axiom` declarations.

## Discipline Rule

Do not call a prose result "proved" in public-facing documentation unless the
corresponding Lean file checks without `sorry`.

Allowed weaker labels:

```text
formal scaffold
prose lemma
conjecture
adapter obligation
empirical hypothesis
```

## Next Formal Targets

1. Add nontrivial finite examples for `NormalLaxDistinctionTransport`.
2. Add finite examples that instantiate `DistinctionFrame` and `ValueFrame`.
3. Add a finite transition-system adapter sketch.
4. Add richer finite completion examples tied to declared distinction-transport
   obligations, while keeping valuer semantics out of the root skeleton.
5. Only then lift toward enriched presentations such as the historical
   presheaf/profunctor/quantale kernel.

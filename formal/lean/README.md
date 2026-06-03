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

1. Add finite maximal-completion existence for finite candidate families.
2. Add recurrent recoverability over finite chains.
3. Add nontrivial finite examples for `NormalLaxDistinctionTransport`.
4. Add finite examples that instantiate `DistinctionFrame` and `ValueFrame`.
5. Add a finite transition-system adapter sketch.
6. Add explicit failure examples where a theorem cannot be stated because an
   adapter lacks monotonicity, pullback functoriality, or compositional support.
7. Only then lift toward enriched presentations such as the historical
   presheaf/profunctor/quantale kernel.

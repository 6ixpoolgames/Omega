# Omega Formal Lean Sandbox

Status: local proof-assistant pressure test

This directory contains the first Lean 4 sandbox for the Omega formalism. It is
not the full quantale-presheaf formalization yet. The current target is to make
small recoverability fragments checkable before the project treats them as
stable mathematical infrastructure.

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

`OmegaCore/PrimitiveWitness.lean` defines a substrate-independent witness
calculus for the proposed Omega Primitive Calculus v0:

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
It is not an empirical adapter and not evidence for Omega.

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

1. Add nontrivial finite examples for `PrimitiveCalculus`.
2. Add finite examples that instantiate `DistinctionFrame` and `ValueFrame`.
3. Add a finite transition-system adapter sketch.
4. Add explicit failure examples where a theorem cannot be stated because an
   adapter lacks monotonicity, pullback functoriality, or compositional support.
5. Add a stricter category/setoid layer for witness associativity and identity
   laws before calling A4/A5 fully formalized.
6. Only then lift toward the full presheaf/profunctor/quantale kernel.

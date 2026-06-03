# Primitive Witness Calculus Lean Smoke v0

Status: proof-assistant smoke / primitive-calculus pressure test
Date: 2026-06-03
Claim boundary: checked witness-calculus fragment only; not full Omega proper, not empirical validation, not Omega validation

## Purpose

This pass pressure-tests the proposed "Omega Primitive Calculus v0" in Lean.

The target is the substrate-independent primitive layer:

```text
relation
distinction
asymmetry
```

The goal is not to formalize the quantale-presheaf presentation or the Future
Field Atlas adapter. The goal is to test whether the proposed primitive witness
language can support the basic derived claims without importing state, agency,
value, identity, utility, or empirical labels as primitives.

## Checked Artifact

Lean file:

```text
formal/lean/OmegaCore/PrimitiveWitness.lean
```

Build command:

```powershell
$env:PATH = (Resolve-Path '.tools\lean-4.30.0\lean-4.30.0-windows\bin').Path + ';' + $env:PATH
cd formal\lean
lake build OmegaCore
```

Build status:

```text
PASS
Build completed successfully.
```

The checked Lean files contain no:

```text
sorry
admit
axiom
```

## What Was Formalized

`PrimitiveCalculus` contains:

```text
Ctx:
  contexts

Rel:
  typed relational unfoldings

Dist:
  context-indexed distinction types

dle:
  distinction refinement preorder

Wit:
  typed asymmetric distinction-transport witnesses

wle:
  witness-strength preorder

id_wit:
  identity recovery witness

weaken_strengthen:
  source weakening and target strengthening closure

compose_wit:
  sequential witness composition

compose_mono:
  monotonicity of witness composition
```

Derived definitions:

```text
Recovers:
  recoverability as existence of a typed witness

NonErasing:
  non-erasure for a declared requirement set

ProcessBundle:
  bookkeeping tuple only, not a primitive self or agent

JointPresentation:
  presentation-relative joint context with embeddings

Compatible:
  n-ary, joint-presentation-relative non-erasure
```

Checked derived lemmas:

```text
recoverability_weaken_source
recoverability_strengthen_target
compositional_recoverability
non_erasure_monotonicity
```

## Scientific Read

This is a positive formal pressure test.

It shows that the primitive witness language can state and prove the basic
recoverability and non-erasure lemmas directly from witness closure assumptions.
That supports the current stance that recoverability is derived from asymmetric
distinction transport, rather than being a primitive identity or observation
notion.

This does not show:

```text
full Omega proper is complete;
the full category laws are formalized;
witness associativity and identity laws are fully quotient/setoid-safe;
any nontrivial empirical substrate instantiates the calculus;
the Future Field Atlas adapter satisfies the calculus;
Omega, agency, valuerhood, identity, compatibility, value, support, capture, or
erasure has been detected.
```

## Important Limitation

This pass intentionally does not force the full A4/A5 associativity and identity
witness laws into the first module. Those laws need a more careful equality or
equivalence layer over composed relational terms and witnesses.

Treat them as the next formalization target, not as silently proved.

## Next Formal Targets

1. Add a nontrivial finite `PrimitiveCalculus` model.
2. Add an explicit non-model or failed adapter example where a closure axiom is
   missing.
3. Add a stricter category/setoid layer for relational composition and witness
   equivalence.
4. Formalize A4 and A5 against that layer.
5. Only then connect the primitive witness calculus to the stricter
   quantale-presheaf presentation.

## Claim Boundary

Allowed claim:

```text
The primitive witness calculus can support the basic derived recoverability and
non-erasure lemmas in Lean, without `sorry`, `admit`, or `axiom`.
```

Blocked claim:

```text
Omega proper is proved, empirically instantiated, or validated.
```

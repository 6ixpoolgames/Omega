# Omega Primitive Calculus v0 Lean Root Skeleton

Status: Lean-checked support-level root skeleton
Date: 2026-06-03
Claim boundary: formal skeleton only; not empirical validation, not valuer detection, not Omega validation, not ethical completion

## Purpose

This pass updates the Lean target from the earlier witness-calculus smoke to the
refined Omega Primitive Calculus v0 root formalism.

The current compact root object is:

```text
A : C -> DistTrans
```

where:

```text
C:
  category of relational contexts and unfoldings

DistTrans:
  category of preorder-indexed support-level distinction transports

A:
  normal lax assignment of distinction fibers and transport relations
```

This is a support-level calculus. Weighted, probabilistic, cost-valued,
rank-valued, rate-valued, information-theoretic, quantale-valued, and
Boolean-algebraic versions are presentations or enrichments, not the root
formalism.

## Checked Lean Artifacts

Files:

```text
formal/lean/OmegaCore/DistTrans.lean
formal/lean/OmegaCore/NormalLax.lean
formal/lean/OmegaCore/Recurrent.lean
formal/lean/OmegaCore/Completion.lean
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

## Batch 1: DistTrans

`DistTrans.lean` defines:

```text
PreorderFrame:
  minimal preorder frame

DistTransport:
  relation Phi(p,q) closed under source weakening and target strengthening

id:
  identity transport, Id_P(p,q) iff p <= q

compose:
  ordinary relational composition of transports
```

Checked laws:

```text
identity transport is closed
composition of transports is closed
left identity, relation-level iff
right identity, relation-level iff
associativity, relation-level iff
```

The category laws are expressed as relation-level equivalences. This is the
mathematically relevant extensional equality for support relations.

## Batch 2: Normal Lax Consequences

`NormalLax.lean` defines:

```text
ContextCategory:
  relational contexts and composable unfoldings

NormalLaxDistinctionTransport:
  object part assigns distinction preorders
  morphism part assigns DistTrans transports
  identity is normal
  composition is lax by transport inclusion
```

Checked consequences:

```text
identity recoverability
recoverability weakening
recoverability strengthening
compositional recoverability from laxity
non-erasure monotonicity
```

## Batch 3: Recurrent Recoverability

`Recurrent.lean` defines:

```text
Chain:
  finite composable chain of relational unfoldings

Chain.toHom:
  composite unfolding induced by a chain

RecoverChain:
  local stepwise recovery along the chain
```

Checked theorem:

```text
recoverChain_sound:
  local finite-chain recovery implies recovery through the composite unfolding
```

Interpretation:

```text
Recurrent recoverability is finite-chain compositional recoverability.
It formalizes repeated recovery across a declared unfolding sequence.
Nontriviality / churn is adapter-specific and not part of the Lean root
skeleton.
```

## Batch 4: Finite Maximal Completion

`Completion.lean` defines:

```text
SubsetMaximal:
  admissible family with no one-way admissible extension

MaxSizedInList:
  admissible listed family whose size dominates all listed admissible families

exists_subsetMaximal_of_finite_enumeration:
  finite-enumeration maximal completion existence

exists_subsetMaximal_finset:
  Finset/Fintype maximal completion existence
```

Interpretation:

```text
If admissible candidate families are covered by an explicit finite enumeration
and at least one family is admissible, then a subset-maximal admissible family
exists.

If the candidate universe is finite, then the same subset-maximal existence
result specializes to `Finset` candidate families.
```

This proves the finite completion skeleton only. It does not define
compatibility, proto-valuers, valuers, value, empirical adapters, or Future
Field Atlas semantics.

Implementation note:

```text
The Lean sandbox now includes mathlib v4.30.0. The explicit List theorem is
retained as the minimal finite-search constructor, and the Finset/Fintype
specialization is checked with mathlib.
```

## Scientific Read

This is a stronger root formalization target than the earlier quantale-presheaf
kernel and the witness-calculus smoke.

The quantale-presheaf kernel remains useful as a strict enriched presentation,
but it is not the root formalism. The witness calculus remains useful as a
prior pressure test, but the normal-lax `DistTrans` formulation is cleaner
because associativity and unit behavior live in ordinary relational
composition.

This pass does not show:

```text
that Omega is empirically realized;
that any Future Field Atlas adapter instantiates the root calculus;
that a substrate exposes relation, distinction, and asymmetry honestly;
that value, valuerhood, agency, identity, compatibility, support, capture, or
erasure has been detected.
```

## Remaining Lean Targets

1. Nontrivial finite normal-lax models.
2. Failed-adapter examples showing which theorems stop transferring when a law
   is absent.
3. Add concrete finite Finset examples for the completion theorem.

## Allowed Claim

```text
The support-level normal lax distinction-transport skeleton for Omega Primitive
Calculus v0 is Lean-checkable for DistTrans closure/category laws, the basic
recoverability/non-erasure consequences, and finite-chain recurrent
recoverability, finite-enumeration maximal completion existence, and
Finset/Fintype maximal completion existence.
```

## Blocked Claim

```text
Omega proper is empirically validated, value-bearing, or adapter-instantiated.
```

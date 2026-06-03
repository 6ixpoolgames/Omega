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

1. Finite maximal-completion existence under finite candidate space and at
   least one admissible subset.
2. Recurrent recoverability over finite chains.
3. Nontrivial finite normal-lax models.
4. Failed-adapter examples showing which theorems stop transferring when a law
   is absent.

## Allowed Claim

```text
The support-level normal lax distinction-transport skeleton for Omega Primitive
Calculus v0 is Lean-checkable for DistTrans closure/category laws and the basic
recoverability/non-erasure consequences.
```

## Blocked Claim

```text
Omega proper is empirically validated, value-bearing, or adapter-instantiated.
```

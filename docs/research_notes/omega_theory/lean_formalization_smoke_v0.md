# Lean Formalization Smoke v0

Status: proof-assistant smoke / formalism pressure test
Date: 2026-06-03
Claim boundary: checked order-theoretic scaffold only; not full OmegaCore, not empirical validation, not Omega validation

## Purpose

This pass sets up a local Lean 4 sandbox and checks whether a minimal fragment of
the new Omega Core axioms can be stated and proved without hidden assumptions.

The goal is not to formalize the full quantale-presheaf kernel immediately. The
goal is to make the first recoverability claims fail loudly if their required
order, monotonicity, pullback, or compositional-support assumptions are missing.

## Local Proof Assistant Setup

Lean toolchain:

```text
Lean 4.30.0
Lake 5.0.0
```

Workspace path:

```text
formal/lean/
```

Portable toolchain path:

```text
.tools/lean-4.30.0/lean-4.30.0-windows/bin/
```

Build command from repository root:

```powershell
$env:PATH = (Resolve-Path '.tools\lean-4.30.0\lean-4.30.0-windows\bin').Path + ';' + $env:PATH
cd formal\lean
lake build OmegaCore
```

Build status:

```text
PASS
Build completed successfully (4 jobs).
```

The checked Lean files contain no:

```text
sorry
admit
axiom
```

## What Was Formalized

File:

```text
formal/lean/OmegaCore/Basic.lean
```

The smoke formalizes a deliberately small kernel:

```text
DistinctionFrame:
  preorder-like distinction frame

ValueFrame:
  ordered tensor structure for asymmetry/support values

Recovers:
  source distinction structurally pulls back from a target distinction and
  meets an asymmetry/support threshold

NonErasing:
  every declared required distinction has some recovering target witness
```

Checked lemmas:

```text
recoverability_weaken_source
recoverability_strengthen_target
non_erasure_monotonicity
compositional_recoverability
```

## Scientific Read

This is a useful pass, but modest.

It shows that the basic recoverability monotonicity claims can be made precise
in an order-theoretic fragment.

It does not show:

```text
that the full quantale-presheaf Omega Core is formalized;
that any empirical Future Field Atlas adapter instantiates the kernel;
that the exact profunctor composition law is satisfied by current operators;
that Delta, V, A, or mu are non-vacuous in real substrates;
that Omega, proto-valuerhood, compatibility, support/capture/erasure, value, or
identity has been detected.
```

## Immediate Lessons

The Lean smoke makes the adapter obligations sharper.

To use the prose theorems empirically, a substrate adapter must provide:

```text
1. an explicit distinction preorder or lattice;
2. explicit pullback / reindexing maps;
3. proofs or audits of pullback monotonicity;
4. explicit asymmetry/support values;
5. proofs or audits of source contravariance and target covariance;
6. a compositional-support lower bound for composed recoverability.
```

If an adapter cannot provide these, then the corresponding theorem does not
apply. It may still be useful as an extended or empirical model, but that loss
must be reported explicitly.

## Next Proof Targets

1. Add tiny finite examples that instantiate `DistinctionFrame` and `ValueFrame`.
2. Add a finite transition-system adapter sketch.
3. Add non-models / failed theorem attempts where monotonicity or composition is
   absent.
4. Only after those pass, lift toward the full:

```text
C:
  symmetric monoidal relational context category

Delta:
  complete-lattice-valued distinction presheaf

V:
  unital quantale

A:
  V-valued distinction-transition profunctor

mu:
  joint distinction-composition map
```

## Documentation Rule

Do not call a formal claim "proved" in public-facing documentation unless the
corresponding Lean artifact checks without `sorry`.

Weaker labels remain allowed:

```text
formal scaffold
prose lemma
conjecture
adapter obligation
empirical hypothesis
```

# Expansion Dominance v0

Status: formal theorem note / declared-profile comparison
Scope: per-valuer declared expansion profiles and monotone-valuation acceptance
Claim boundary: not value, not benefit in the final sense, not an expansion gate, not aggregation, not population comparison, not standing, not rights, not agency, not identity, not Omega validation

## Purpose

This note records the gain-side mirror of declared nonrecoverable-loss
dominance.

The loss side compares declared facts that an intervention nonrecoverably
contracts. The expansion side compares declared facts that an intervention
expands, restores, unlocks, or makes newly available inside a registered
valuer/fact order.

The important boundary:

```text
Expansion comparison is not an expansion gate.
```

The floor may refuse certified nonrecoverable contraction. It does not command
maximal expansion.

## Formal Surface

Lean files:

```text
formal/lean/OmegaProper/Decision/ExpansionDominance.lean
formal/lean/OmegaProper/Decision/ExpansionDominanceExamples.lean
```

Core definitions:

```text
ExpansionProfile Fact := Fact -> Prop

CoveredExpansion P f :=
  exists g, P g and f <= g

ExpansionDominates P Q :=
  every covered declared expansion of Q is also covered by P
```

The preorder over facts is registered structure. It is not derived value.

## Landed Theorems

The file proves:

```text
expansionDominates_refl
expansionDominates_trans
not_expansionDominates_iff_exists_failure_certificate
expansionDominates_iff_hoareDominates
expansionDominates_iff_all_monotone_valuation_covers
```

Reading:

```text
Within a declared valuer/register/fact order, one expansion profile dominates
another exactly when every fact expanded by the second is matched or exceeded
by a fact expanded by the first.
```

The ODT1 bridge gives the valuation-facing reading:

```text
ExpansionDominates P Q iff every monotone valuation over declared facts gives
P a pointwise cover of Q.
```

This is value-parametric, not value-free. The declared fact order and monotone
valuation class remain registered inputs.

## Enrichment Witness

The example file includes a small enrichment witness:

```text
ExpandTask:
  expands declared task-success capacity.

ExpandTaskAndRevision:
  expands the same task-success capacity and declared correction/revision
  capacity.
```

`ExpandTaskAndRevision` expansion-dominates `ExpandTask`, while `ExpandTask`
does not expansion-dominate `ExpandTaskAndRevision`. The reverse failure has a
named certificate: the declared revision-capacity fact.

This is the mirror of the correction-register collapse / self-lobotomy
pattern, but on the gain side.

## Why There Is No Expansion Gate

The comparison is symmetric with the loss order. The licensing gate is not.

```text
comparatives can be symmetric;
constraints are one-sided;
refusals compose;
pursuits Goodhart.
```

A recovery-aware gate can refuse an action that destroys bounded recoverability
of a declared fact. The mirror would be an obligation to choose expansion,
which would turn the floor into a maximizer. That is explicitly not the role of
this layer.

## Nonclaims

This note does not claim:

```text
expansion is final value;
expansion is morally mandatory;
more expansion across valuers is better;
there is a population optimum;
there is an expansion duty;
the expanded facts are the correct facts;
the expanded entity has standing.
```

Cross-valuer comparison remains registered-order debt.

## Public Compression

Expansion dominance mirrors nonrecoverable-loss dominance as a declared-profile
comparison. It proves a per-valuer direction of improvement relative to a
registered fact order and monotone valuation class, while deliberately refusing
to turn that comparison into an obligation to maximize expansion.

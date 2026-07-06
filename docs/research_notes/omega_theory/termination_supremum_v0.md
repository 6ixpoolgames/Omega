# Termination Supremum v0

Status: formal theorem note / measure-free contraction result
Scope: per-valuer declared fact orders with a top contracted fact
Claim boundary: not cross-valuer aggregation, not moral standing, not rights, not patienthood, not final value, not agency, not identity, not Omega validation

## Purpose

Earlier future-field discussion used denominator and fraction-of-field language
to express why terminating a live value-contact field is unlike frustrating a
small preference slice. The declaration-culling pass demoted that scalar
language.

This note records the measure-free core:

```text
per valuer, if termination contracts the top of the declared fact order, then
termination nonrecoverable-loss-dominates every other contraction profile over
that order.
```

No field measure is needed.

## Formal Surface

Lean file:

```text
formal/lean/OmegaProper/Decision/TerminationSupremum.lean
```

The theorem assumes:

```text
top : Fact
forall f, f <= top
Termination top
```

and proves:

```text
termination_contracts_top_lossDominates_all
```

meaning:

```text
LossDominates Termination Other
```

for every declared contraction profile `Other`.

It also proves the valuation-facing corollary:

```text
termination_contracts_top_monotone_covers_all
```

via the existing nonrecoverable-loss dominance acceptance bridge.

## Reading

If the declared fact order has a top fact representing the whole live
value-contact/correction/revision field of a valuer, then contracting that top
fact covers every declared contraction below it.

This is the theorem-shaped version of:

```text
termination is maximal per-valuer declared loss.
```

It does not compare different valuers. It does not assign moral standing. It
does not say which fact order is correct.

## Relation To Field-Measure Culling

This theorem replaces a tempting scalar claim:

```text
termination collapses the whole field denominator.
```

with an order-level claim:

```text
termination contracts the top declared fact and therefore dominates all other
declared contractions in that fact order.
```

The first requires a measure. The second only requires a registered preorder
with a top fact.

## Nonclaims

This note does not claim:

```text
which systems are valuers;
which facts should sit in the order;
which fact is the real top;
how to compare different valuers;
that termination of any physical object has occurred;
that termination may be traded for expansion elsewhere.
```

Cross-valuer compensation remains a separate registered claim.

## Public Compression

Termination-supremum is the measure-free replacement for denominator rhetoric:
within a declared per-valuer fact order, contracting a top fact
nonrecoverable-loss-dominates every other contraction profile over that order.

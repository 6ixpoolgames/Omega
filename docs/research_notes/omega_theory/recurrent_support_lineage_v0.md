# Recurrent Support Lineage v0

Status: formal checkpoint note
Scope: pair-relative handoff between incomparable recurrent supports
Claim boundary: not identity, not recoverability, not agency, not deformer theory, not Omega validation

## Purpose

Support extension handles:

```text
C carries before;
D carries after;
C subset D.
```

Support lineage handles the next weaker shape:

```text
C carries before;
D carries after;
C and D need not be related by inclusion.
```

The Lean module is:

```text
formal/lean/OmegaProper/Trajectory/RecurrentSupportLineage.lean
```

## Core contract

The lineage contract is pair-relative. It requires the target support `D` to
provide:

```text
recurrent viability under the target dynamics;
membership for the declared endpoints x and y;
an internal path x -> y inside D;
an internal path y -> x inside D.
```

The source carrying proof supplies the merge-separated consequence distinction.

Then:

```text
RecurrentSupportCarries S Next0 safe0 C x y
+ RecurrentSupportLineageContract Next1 safe1 D x y
=> RecurrentSupportCarries S Next1 safe1 D x y
```

This says a declared consequence distinction can be handed off to a new support
when the new support explicitly carries the same endpoints.

## Incomparable-support witness

The module includes a finite witness with four states:

```text
left, old, new, right
```

Source support:

```text
C = {left, old, right}
```

Target support:

```text
D = {left, new, right}
```

The supports are incomparable:

```text
old is in C but not D;
new is in D but not C.
```

The source support carries the left/right distinction through:

```text
left -> old -> right -> left
```

The target support carries the same left/right distinction through:

```text
left -> right -> new -> left
```

This proves:

```text
incomparable support lineage can preserve recurrent carrying
without same-support identity or subset inclusion.
```

## What this does not prove

This is not a full recoverability theory. It does not show that every support
handoff is valid, or that a support has persisted as the same object.

It proves one controlled handoff shape:

```text
if the source support carries the distinction
and the target support explicitly recurrently carries the same endpoints,
then carrying lineages to the target support.
```

## Why this matters

This is the first support handoff result that does not depend on inclusion:

```text
not same support;
not support extension;
not object identity.
```

It is still pair-relative and exact. That is intentional. The next step toward
recoverability would have to let the distinction itself translate.

## Next target

The natural next theorem layer is successor distinctions:

```text
C carries pair x,y;
D carries translated pair x',y';
the translation is consequence-respecting under an explicit relation.
```

That would move beyond "same endpoints in a different support" without
smuggling identity.

## Related notes

- [recurrent_support_integrity_v0.md](recurrent_support_integrity_v0.md)
- [recurrent_support_extension_v0.md](recurrent_support_extension_v0.md)
- [recurrent_support_perturbation_floor_v0.md](recurrent_support_perturbation_floor_v0.md)

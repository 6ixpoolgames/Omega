# Recurrent Support Successor Distinction v0

Status: formal checkpoint note
Scope: pair translation for recurrently carried consequence distinctions
Claim boundary: not identity, not recoverability, not agency, not deformer theory, not Omega validation

## Purpose

Support lineage still keeps the same declared endpoints:

```text
C carries x,y;
D carries x,y.
```

Successor distinction allows the carried pair itself to change:

```text
C carries x,y;
D carries x',y'.
```

The Lean module is:

```text
formal/lean/OmegaProper/Trajectory/RecurrentSupportSuccessorDistinction.lean
```

## Core contract

The contract requires an explicit pair translation:

```text
R x x'
R y y'
```

and a preservation condition:

```text
ConsequenceMergeSeparated S x y
=> ConsequenceMergeSeparated S x' y'
```

The target support must also recurrently carry the translated endpoints:

```text
D x'
D y'
internal path x' -> y' inside D
internal path y' -> x' inside D
D is recurrent viable
```

Then:

```text
RecurrentSupportCarries S Next0 safe0 C x y
+ RecurrentSupportSuccessorContract S Next1 safe1 D R x y x' y'
=> RecurrentSupportCarries S Next1 safe1 D x' y'
```

## Why this matters

This is the first layer that lets recurrent carrying move without preserving
the exact endpoints.

It avoids saying:

```text
the same object persisted;
the same boundary persisted;
the same pair persisted.
```

Instead it says:

```text
a declared source pair was translated into a declared target pair under an
explicit relation that preserves merge-separation.
```

That is a safer route toward eventual recoverability language.

## Finite witness

The module includes a finite witness with source endpoints:

```text
sourceLeft, sourceRight
```

and target endpoints:

```text
targetLeft, targetRight
```

The relation maps:

```text
sourceLeft  -> targetLeft
sourceRight -> targetRight
```

The source support carries:

```text
sourceLeft -> sourceRight -> sourceLeft
```

The target support carries:

```text
targetLeft -> bridge -> targetRight -> targetLeft
```

The target pair is not the source pair. Carrying is handed off through an
explicit merge-separation-preserving translation.

## What this does not prove

This does not prove that all translations are valid, that the translated pair
is "really the same" distinction, or that a recovered identity exists.

It only proves:

```text
if a translation preserves merge-separation
and the target support recurrently carries the translated pair,
then carrying transfers to that translated pair.
```

## Next target

The natural next formal layer is a perturbation budget:

```text
how many edge/path removals are needed to destroy recurrent carrying?
```

That would provide the first finite cohesion-like measure without defining
identity.

## Related notes

- [recurrent_support_integrity_v0.md](recurrent_support_integrity_v0.md)
- [recurrent_support_lineage_v0.md](recurrent_support_lineage_v0.md)
- [recurrent_support_extension_v0.md](recurrent_support_extension_v0.md)

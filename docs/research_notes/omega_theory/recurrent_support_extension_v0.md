# Recurrent Support Extension v0

Status: formal checkpoint note
Scope: support-extension transfer for recurrently carried consequence distinctions
Claim boundary: not identity, not recoverability, not agency, not deformer theory, not Omega validation

## Purpose

The earlier recurrent-support transfer contracts were same-support results:

```text
C carries before;
C carries after.
```

This note records the next step:

```text
C carries before;
D carries after;
C need not equal D.
```

The Lean module is:

```text
formal/lean/OmegaProper/Trajectory/RecurrentSupportExtension.lean
```

## Core contract

The support-extension contract requires:

```text
SupportSub C D
D is recurrent viable under the changed dynamics
old internal paths in C are replaceable by new internal paths in D
```

Then:

```text
RecurrentSupportCarries S Next0 safe0 C x y
+ RecurrentSupportExtensionContract Next0 Next1 safe1 C D
=> RecurrentSupportCarries S Next1 safe1 D x y
```

This is a sufficient condition, not a necessary condition.

## Why this matters

This is the first moving-support result in the recurrent-support stack.

It avoids the identity trap:

```text
not: the same object persisted;
but: a declared carrying predicate transferred from support C into support D
     under explicit obligations.
```

That is the kind of move needed before anything like recoverability can be
defined responsibly.

## Strict extension witness

The module includes a finite witness:

```text
C = {left, right}
D = {left, mid, right}
```

The source support `C` carries the left/right distinction on a direct endpoint
cycle:

```text
left -> right -> left
```

The target support `D` carries the same distinction after rerouting the return
path through `mid`:

```text
left -> right -> mid -> left
```

The support inclusion is proper because `mid` is in `D` but not in `C`.

This proves:

```text
strict support extension can preserve recurrent carrying
without same-support identity.
```

## What this does not prove

This does not prove:

```text
all support extensions are valid;
all reroutings preserve carrying;
object identity;
recoverability;
agency;
valuerhood;
Omega proper.
```

It proves one controlled transfer shape:

```text
if a target support is recurrent viable and old internal paths are replaceable
inside it, carrying transfers into that target support.
```

## Next targets

The next natural steps are:

1. Support lineage:
   allow handoff between supports without requiring simple subset inclusion.

2. Successor distinctions:
   allow the carried distinction itself to translate from one pair to another.

3. Perturbation budget:
   measure how many edge/path removals are needed to destroy carrying.

4. Joint recurrent support:
   ask when several supports can carry together.

## Related notes

- [recurrent_support_integrity_v0.md](recurrent_support_integrity_v0.md)
- [recurrent_support_perturbation_floor_v0.md](recurrent_support_perturbation_floor_v0.md)
- [parameterized_recurrent_support_v0.md](parameterized_recurrent_support_v0.md)

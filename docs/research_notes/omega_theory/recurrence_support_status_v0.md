# Recurrence and Support Status v0

Status: consolidation note

The recurrence/support floor now has an identity-free Lean spine:

```text
closed viable class
-> recurrent viable class
-> path-carried consequence distinction
-> distinction support
-> support restriction
-> support minimality
```

This stack does not define agency, self, identity, boundary realism, value,
alignment, or Omega proper.

## Landed Layers

```text
SustainingViableClass
```

defines closed sustaining viable classes. Members are safe and have internal
successors.

```text
CarriedDistinction
```

shows that a class can contain consequence-separated members and therefore need
not be a sound merge class.

```text
RecurrentViableClass
```

adds internal paths and strong connectivity inside a closed safe class.

```text
PathCarriedDistinction
```

requires separated members to be internally connected in both directions.

```text
DistinctionSupport
```

packages path-carried distinction as support/extent language.

```text
SupportRestriction
```

proves that restricting a support can destroy support for a fixed pair.

```text
SupportMinimality
```

defines pair-relative minimal support and proves the two-state recurrent cycle
is minimal for its left/right distinction.

## Current Claim

The strongest current claim is:

```text
a recurrent viable region can support a consequence distinction without being
a valid merge class, and support can be tested by restriction/minimality
without assuming identity or boundary realism
```

This is an extent floor, not an object theory.

## Why It Matters

The project needs a way to talk about where consequence-bearing structure is
carried without defining a persisting self or object boundary. This stack gives
the first exact finite vocabulary for that:

```text
support = a declared region over which a consequence distinction is internally
connected
```

Restriction and minimality then make the vocabulary testable:

```text
dropping an endpoint destroys support
no proper sub-support carries a minimal support's fixed pair
```

## Claim Boundary

This layer does not yet prove:

```text
agency
valuerhood
object identity
boundary objectivity
alignment
Omega-terminal structure
large-world scale behavior
```

Those remain downstream.

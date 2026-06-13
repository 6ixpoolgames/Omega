# Path-Carried Distinction v0

Status: foundational theorem note

This note records the strengthening from:

```text
a class contains an internal consequence distinction
```

to:

```text
the class dynamics internally connect the separated pair in both directions
```

This does not define agency, identity, consciousness, value, alignment, or
Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/PathCarriedDistinction.lean
```

## Relationship To Earlier Layers

`CarriedDistinction.lean` says:

```text
a class can carry a consequence-separated pair
```

`RecurrentViableClass.lean` says:

```text
a class can be closed, internally connected, viable, and sustaining
```

This file combines those ideas at the pair level.

## Core Definitions

```text
ClassPathCarriesSeparatedPair D S C x y
```

means:

```text
C x
C y
InternalPath D C x y
InternalPath D C y x
ConsequenceSeparated S x y
```

There is also a merge-blocking version:

```text
ClassPathCarriesMergeSeparatedPair
```

and existential class-level versions:

```text
ClassPathCarriesSomeSeparatedPair
ClassPathCarriesSomeMergeSeparatedPair
```

## Core Theorems

Lean proves that path-carried distinctions imply ordinary carried
distinctions:

```text
pathCarriedSeparated_implies_carried
pathCarriedMergeSeparated_implies_carried
```

and therefore block treating the class as a consequence-respecting merge class:

```text
pathCarriedSeparated_blocks_classRespect
pathCarriedMergeSeparated_blocks_classRespect
```

## Finite Witness

The file reuses the recurrent two-state cycle:

```text
left -> right
right -> left
```

with an identity-based consequence system separating `left` and `right`.

Lean proves:

```text
recurrent_cycle_pathCarries_distinction
```

which packages:

```text
the cycle class is recurrent viable
left and right are internally path-connected in both directions
left and right are consequence-separated
the class is not a valid consequence merge class
```

## Interpretation

This is a safe predecessor to stronger "carried through recurrence" language:

```text
not "an object persists"
but "internal class dynamics connect consequence-bearing differences"
```

Later work can ask about support, extent, composition, and interference of such
path-carried distinctions. Those are not claimed here.

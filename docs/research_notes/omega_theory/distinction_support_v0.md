# Distinction Support v0

Status: foundational theorem note

This note introduces support/extent language for path-carried consequence
distinctions.

The core idea is:

```text
a support is a declared class/region over which a consequence distinction is
internally connected by the dynamics
```

This does not define an object, identity, self, boundary, agency, value,
alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/DistinctionSupport.lean
```

## Core Definitions

```text
SupportContains C x
```

is membership spelling for support classes.

```text
SupportSub C D
```

is support inclusion.

```text
ProperSupportSub C D
```

is proper support inclusion.

```text
SupportsSeparatedPair S Next C x y
```

means `C` path-carries a directional consequence-separated pair.

```text
SupportsMergeSeparatedPair S Next C x y
```

means `C` path-carries a merge-blocking separated pair.

## Core Theorems

Lean proves:

```text
support_implies_pathCarried
mergeSupport_implies_pathCarried
```

Support is therefore not a new truth source; it packages the existing
path-carried distinction relation.

Lean also proves:

```text
support_blocks_classRespect
mergeSupport_blocks_classRespect
```

So a support carrying a separated pair is not a valid consequence-respecting
merge class.

For recurrent supports, Lean proves endpoint viability:

```text
recurrentSupport_left_viable
recurrentSupport_right_viable
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
recurrent_cycle_is_support_for_distinction
```

which packages:

```text
the cycle class is recurrent viable
the cycle supports the left/right consequence distinction
the cycle class is not a consequence-respecting merge class
```

## Interpretation

This is the first sober version of extent:

```text
not a boundary
not an object
not an identity
but a region/class over which a consequence distinction is dynamically
connected
```

The next natural checks are:

```text
restriction can destroy support
minimal support can be defined relative to a pair
```

Those are future claims.

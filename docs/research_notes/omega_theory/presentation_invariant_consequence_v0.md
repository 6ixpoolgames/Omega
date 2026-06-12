# Presentation-Invariant Consequence v0

Status: standard-core bridge note

This note records the first invariant layer over the consequence stack.

The point is deliberately narrow:

```text
if a consequence system blocks a merge,
then no sound presentation can erase that distinction.
```

This is a bridge from quotient/class guardrails toward boundary/presentation
discipline. It does not define identity, selfhood, value, agency,
recoverability, boundary realism, or Omega proper.

## Motivation

The repo avoids treating boundaries or objects as primitive. A proposed
boundary, class, quotient, or presentation is a modeling move. The consequence
layer already says when such a move is sound:

```text
identified pair -> consequence-identifiable pair
```

The invariant reading is:

```text
a consequence-blocked distinction is not erased by any sound presentation.
```

So the project does not need to say:

```text
this is the real object boundary
```

It can say:

```text
this distinction survives every consequence-sound presentation in the declared
family
```

That is the first safe version of "not merely a presentation artifact."

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/PresentationInvariant.lean
```

## Core Definitions

```text
PairErasedByPresentation present x y :=
  present x = present y
```

```text
PairInvariantUnderSoundQuotients S x y :=
  every sound quotient/presentation keeps x and y separated
```

```text
PairInvariantUnderSoundFamily S present x y :=
  every sound member of a declared presentation family keeps x and y separated
```

```text
ErasesMergeSeparatedPair S present :=
  present identifies some pair that S merge-separates
```

## Core Theorems

Sound presentations identify only consequence-identifiable pairs:

```text
soundPresentation_identification_implies_identifiable
```

Non-identifiable pairs are invariant under sound quotients:

```text
notIdentifiable_invariantUnderSoundQuotients
```

Merge-separated pairs are invariant under sound quotients:

```text
mergeSeparated_invariantUnderSoundQuotients
```

Merge-separated pairs are invariant under any declared family of sound
presentations:

```text
mergeSeparated_invariantUnderSoundFamily
```

Any presentation that erases a merge-separated pair is unsound:

```text
erasesMergeSeparatedPair_not_sound
```

## What This Buys

This is the first formal bridge from:

```text
sound quotient
```

to:

```text
presentation-invariant consequence structure
```

It supports the boundary discipline needed by later alignment-oriented theory:

```text
boundaries are not primitive,
but not every boundary/presentation is sound.
```

## Claim Boundary

This note does not claim that all invariant consequence distinctions are
valuers, agents, selves, or value-bearing structures.

It only proves that consequence-blocked distinctions cannot be erased by
sound presentations. Later work can ask which invariant distinctions also
support viability, valuation, agency, or alignment-relevant continuation.

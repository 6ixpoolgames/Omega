# Carried Distinction v0

Status: foundational theorem note

This note records the first bridge from sustaining viable classes to internal
consequence structure.

The core distinction is:

```text
a class can carry a consequence distinction
without being allowed to quotient that distinction away
```

This does not define agency, identity, consciousness, value, alignment, or
Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/CarriedDistinction.lean
```

## Core Definitions

```text
ClassContainsPair C x y
```

means `C` contains both `x` and `y`.

```text
ClassCarriesSeparatedPair S C
```

means `C` contains a directionally consequence-separated pair.

```text
ClassCarriesMergeSeparatedPair S C
```

means `C` contains a merge-separated pair in either direction.

## Core Theorems

Lean proves:

```text
separatedPair_carried_blocks_classRespect
```

and:

```text
mergeSeparatedPair_carried_blocks_classRespect_or_reverse
```

If a class carries an internal separated pair, then it is not a
consequence-respecting merge class.

## Finite Witness

The file reuses the two-state sustaining cycle:

```text
left -> right
right -> left
```

with both states safe and both inside the sustaining class.

It defines a one-context consequence system that compares cycle states by
identity, so:

```text
left and right are consequence-separated
```

Lean proves:

```text
cycleClass_sustains_and_carries_distinction
```

which packages:

```text
the cycle class is closed and sustaining
the cycle class carries a consequence-separated pair
the cycle class is not a consequence-respecting merge class
```

## Interpretation

This is the next identity-free persistence step:

```text
not "the same object persists"
but "a sustaining region carries internal consequence structure"
```

The warning is essential:

```text
carrying a distinction is different from erasing it
```

A sustaining class containing separated members is a structured region, not a
valid quotient class.

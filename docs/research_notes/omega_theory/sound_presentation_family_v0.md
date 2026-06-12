# Sound Presentation Family v0

Status: standard-core bridge note

This note records the declared-family version of presentation invariance.

The project should not say:

```text
this survives all possible boundaries
```

without a declared class of admissible presentations. The finite version is:

```text
this survives every sound member of this declared presentation family
```

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/SoundPresentationFamily.lean
```

## Core Definitions

Sound presentation family:

```text
SoundPresentationFamily S present :=
  every presentation present i is sound
```

Target invariant under family:

```text
TargetInvariantUnderFamily target present :=
  every presentation in the family preserves target fibers
```

Target obstructed by family:

```text
TargetObstructedByFamily target present :=
  some presentation in the family erases a target-distinct pair
```

Pair invariant under family:

```text
PairInvariantUnderFamily present x y :=
  every presentation in the family keeps x and y apart
```

## Core Theorems

Sound family plus consequence-compatible target gives target invariance:

```text
soundFamily_targetRespectsIdentifiability_invariant
```

Any target obstruction blocks family invariance:

```text
targetFamilyObstruction_blocks_invariance
```

Merge-separated pairs are kept apart by any sound family:

```text
mergeSeparated_pairInvariantUnderSoundFamily
```

Target-separated pairs are kept apart by any sound family when the target
respects consequence identifiability:

```text
targetSeparated_pairInvariantUnderSoundFamily
```

If a sound family contains a target obstruction, then the target does not
respect consequence identifiability:

```text
soundFamily_targetObstruction_blocks_identifiabilityRespect
```

## Why This Matters

This is the first finite version of a "gauge" or presentation-family idea
without using speculative machinery.

The discipline is:

```text
1. declare a family of presentations
2. prove each member is sound
3. ask which targets or pairs survive all members
4. treat failures as presentation-relative or target-obstructed
```

This supports later boundary and alignment work without assuming object
identity or privileged self/environment partitions.

## Claim Boundary

This note does not define value, agency, selfhood, recoverability, boundary
realism, or Omega proper.

It only defines finite declared-family invariance for sound presentations.

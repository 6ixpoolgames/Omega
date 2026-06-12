# Target Presentation Invariance v0

Status: standard-core bridge note

This note records the target-level lift of presentation invariance.

The pair-level theorem says:

```text
a sound presentation cannot erase a consequence-blocked pair
```

The target-level theorem says:

```text
a sound presentation preserves any target that is constant on
consequence-identifiable pairs
```

This is the presentation-layer version of fiber constancy.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/TargetPresentationInvariant.lean
```

## Core Definitions

Target respects presentation:

```text
TargetRespectsPresentation target present :=
  present x = present y -> target x = target y
```

This is the same mathematical shape as saying a target is constant on the
fibers of a summary or presentation.

Target obstruction:

```text
TargetObstructedByPresentation target present :=
  some pair is presentation-equal but target-distinct
```

Target respects consequence identifiability:

```text
TargetRespectsIdentifiability S target :=
  ConsequenceIdentifiable S x y -> target x = target y
```

## Core Theorems

An erased target distinction blocks target respect:

```text
targetObstruction_blocks_respectPresentation
```

A target constant on consequence-identifiable pairs is preserved by any sound
presentation:

```text
soundPresentation_preserves_respecting_target
```

Such a target is invariant under all sound quotients:

```text
targetRespectsIdentifiability_invariantUnderSoundQuotients
```

If a sound presentation erases a target distinction, then the target was not
constant on consequence-identifiable pairs:

```text
soundPresentation_targetObstruction_blocks_identifiabilityRespect
```

If a target respects consequence identifiability and distinguishes a pair, no
sound presentation can erase that pair:

```text
targetSeparated_invariantUnderSoundQuotients
```

## Why This Matters

This layer turns presentation invariance into a classifier for targets.

Pair invariant:

```text
this pair cannot be soundly erased
```

Target invariant:

```text
this target survives every sound presentation
```

Obstruction:

```text
this presentation erases a distinction that the target needs
```

This is the bridge from consequence-pair guardrails to alignment-metric
guardrails. A metric or target is only presentation-stable when sound
presentations cannot collapse distinctions that the target treats as relevant.

## Claim Boundary

This note does not define value, agency, identity, recoverability, boundary
realism, or Omega proper.

It only states when a declared target is preserved by sound presentations.

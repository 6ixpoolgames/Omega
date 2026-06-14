# Viable Trajectory Language v0

Status: theorem note

This note records the first finite trajectory-language wrapper over the
existing reachability/viability semantics.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/ViableTrajectoryLanguage.lean
```

## Core Idea

`TrajectorySemantics` already defines:

```text
SafePrefix D safe n x
```

meaning: starting at `x`, there is a finite prefix of `n` transitions that
stays inside `safe`.

`ViableTrajectoryLanguage` gives this object the language needed by the
boundary-invariant continuation roadmap:

```text
ViableWord D safe n x := SafePrefix D safe n x
ViableLanguage D safe x := forall n, ViableWord D safe n x
```

This is not a lushness metric yet. It is the exact finite object a future
path-count or entropy-like candidate would count.

## Theorems

Lean proves:

```text
viable_supplies_word
viable_supplies_language
jointViable_supplies_jointWord
jointViable_supplies_jointLanguage
jointViable_supplies_leftLanguage
jointViable_supplies_rightLanguage
```

So viability supplies finite viable words at every horizon, and joint viability
supplies both joint and marginal finite-prefix languages.

## Relation To Joint Viability

The existing `JointViability.lean` theorem remains the current checked
counterexample:

```text
marginal viability for each constraint separately
does not imply joint viability for their conjunction
```

This file does not duplicate that finite counterexample at prefix-language
level. It only packages the language object that later path-count and richness
candidates should consume.

## Claim Boundary

This file does not define:

```text
value
agency
identity
alignment
lushness
Omega
```

It only packages finite safe prefixes as a clean next object for later
compatible-continuation richness tests.

# Joint Viability v0

Status: foundational theorem note

This note records the first joint-viability guardrail:

```text
being viable for each of two safety predicates separately
does not imply being viable for their conjunction
```

This does not define value, agency, identity, alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/JointViability.lean
```

## Core Definitions

```text
JointSafe safeA safeB x := safeA x and safeB x
```

```text
JointViable D safeA safeB x :=
  Viable D (JointSafe safeA safeB) x
```

## General Theorems

The file proves monotonicity of viability under safety weakening:

```text
viable_mono_safe
```

Then it proves that joint viability projects to each marginal viability:

```text
jointViable_left
jointViable_right
```

So:

```text
joint viability -> marginal viability
```

## Finite Counterexample

The witness has three states:

```text
start
aLoop
bLoop
```

with transitions:

```text
start -> aLoop
start -> bLoop
aLoop -> aLoop
bLoop -> bLoop
```

The safety predicates are:

```text
safeA holds at start and aLoop
safeB holds at start and bLoop
```

So `start` is viable for `safeA` by going to `aLoop`.

It is also viable for `safeB` by going to `bLoop`.

But it is not jointly viable for `safeA and safeB`, because neither loop state
satisfies both predicates.

Lean proves:

```text
marginal_viability_does_not_imply_joint_viability
```

## Interpretation

This is the first formal warning against replacing joint compatibility with
marginal checks.

In plain terms:

```text
two corridors may each be open separately
without there being one corridor that keeps both open together
```

This is a direct precursor to later compatibility and distributed-agency
questions. It is not yet a value theorem.

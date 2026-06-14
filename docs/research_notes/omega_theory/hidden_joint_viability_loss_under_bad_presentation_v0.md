# Hidden Joint-Viability Loss Under Bad Presentation v0

Status: theorem note

This note records the joint-viability loss counterpart to the existing hidden
reach and hidden viability loss examples.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/HiddenJointViabilityLossUnderBadPresentation.lean
```

## Core Idea

A state can leave the jointly viable corridor while remaining viable for one
marginal constraint.

A bad presentation can hide that loss by identifying the before-loss and
after-loss states.

## Definitions

```text
JointViabilityTarget D safeA safeB x :=
  JointViable D safeA safeB x
```

```text
JointViabilityLossStep D safeA safeB x y :=
  D.Next x y
  and JointViable D safeA safeB x
  and not JointViable D safeA safeB y
```

```text
PresentationHidesJointViabilityLoss D safeA safeB present x y :=
  JointViabilityLossStep D safeA safeB x y
  and present x = present y
```

## Finite Witness

The witness has two states:

```text
joint
onlyA
```

Transitions:

```text
joint -> joint
joint -> onlyA
onlyA -> onlyA
```

Safety predicates:

```text
safeA holds at both joint and onlyA
safeB holds only at joint
```

So:

```text
joint is jointly viable
onlyA remains viable for safeA
onlyA is not jointly viable
joint -> onlyA loses joint viability
```

A constant presentation maps both states to the same abstract state, so it
hides the exact loss.

## Theorems

```text
joint_to_onlyA_loses_jointViability
constantPresentation_hides_joint_to_onlyA_loss
constantPresentation_obstructs_jointViabilityTarget
constantPresentation_not_jointViabilityRespecting
joint_loss_can_leave_marginal_viability
```

## Interpretation

This theorem blocks a common shortcut:

```text
one marginal corridor remains viable
therefore the compatible corridor remains viable
```

No. The exact system can lose joint viability while preserving one marginal
viability predicate. A bad presentation can hide that loss.

This is a direct bridge toward the corrected Gradient Ethics shape:

```text
preserve boundary-invariant jointly viable continuation,
not merely the reachability or viability of one selected boundary.
```

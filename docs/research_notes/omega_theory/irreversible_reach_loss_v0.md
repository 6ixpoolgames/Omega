# Irreversible Reach Loss v0

Status: foundational theorem note

This note records the first exact loss object for the Gradient Ethics bridge:

```text
a transition can move from a state that reaches a target
to a state that cannot reach that target
```

This does not define value, agency, identity, alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/IrreversibleReachLoss.lean
```

## Core Definitions

```text
ReachLossStep D target x y
```

means:

```text
D.Next x y
Reach D target x
not Reach D target y
```

The file also defines:

```text
DeadOutsideTarget D target y
```

meaning `y` is not a target and has no outgoing transition.

## Core Theorems

```text
deadOutsideTarget_not_reach
```

A dead state outside the target cannot reach the target.

```text
step_to_deadOutsideTarget_loses_reach
```

Stepping into such a dead state loses reachability whenever the source state
could reach the target.

## Finite Witness

The file includes:

```text
start -> goal
start -> dead
```

where `goal` is the target and `dead` has no outgoing transition.

Lean proves:

```text
start_reaches_goal
dead_not_reaches_goal
start_to_dead_loses_reach
```

## Interpretation

This is the narrow, non-value version of irreversible loss:

```text
some actions move from available continuation to unavailable continuation
```

Later modules can ask how bad presentations hide this loss, and how safe
presentation contracts prevent that.

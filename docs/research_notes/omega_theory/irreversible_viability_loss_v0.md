# Irreversible Viability Loss v0

Status: foundational theorem note

This note records the viability-side loss object:

```text
a transition can move from a viable state to a non-viable state
```

This does not define value, agency, identity, alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/IrreversibleViabilityLoss.lean
```

## Core Definitions

```text
ViabilityLossStep D safe x y
```

means:

```text
D.Next x y
Viable D safe x
not Viable D safe y
```

The file also defines:

```text
NoOutgoing D y
```

meaning `y` has no outgoing transition.

## Core Theorems

```text
noOutgoing_not_viable
```

A state with no outgoing transition is not viable.

```text
step_to_noOutgoing_loses_viability
```

Stepping into such a state loses viability whenever the source state was
viable.

## Finite Witness

The file includes:

```text
loop -> loop
loop -> dead
```

Both states are declared safe, but `dead` has no outgoing transition.

Lean proves:

```text
loop_viable
dead_not_viable
loop_to_dead_loses_viability
```

## Interpretation

This is the viability-corridor version of irreversible loss:

```text
some actions move from sustainable safe continuation
to a state with no sustainable continuation
```

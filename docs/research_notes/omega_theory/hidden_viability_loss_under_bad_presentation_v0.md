# Hidden Viability Loss Under Bad Presentation v0

Status: foundational counterexample note

This note records the viability-side hidden-loss result:

```text
a bad presentation can hide exact viability loss
```

This does not define value, agency, identity, alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/HiddenViabilityLossUnderBadPresentation.lean
```

## Core Idea

If a transition loses viability:

```text
ViabilityLossStep D safe x y
```

and a presentation maps:

```text
present x = present y
```

then the presentation hides the exact difference between:

```text
x is viable
y is not viable
```

## Core Definitions

```text
ViabilityTarget D safe x := Viable D safe x
```

```text
PresentationHidesViabilityLoss D safe present x y
```

means the pair is a viability-loss step and the presentation erases the pair.

## Core Theorems

```text
viabilityLoss_targetSeparated
hiddenViabilityLoss_obstructs_presentation
hiddenViabilityLoss_blocks_targetRespect
targetRespect_blocks_hiddenViabilityLoss
```

These say that a hidden viability-loss pair obstructs target-level presentation
respect for the exact viability predicate. Conversely, a presentation that
respects the viability target cannot hide a viability-loss pair.

## Finite Witness

The file reuses the `loop -> dead` viability-loss witness and maps all states
to `Unit`. Lean proves that this constant presentation hides the loss.

## Interpretation

Phantom viability says an abstraction can invent a viable corridor.

Hidden viability loss says an abstraction can erase the fact that a viable
corridor was lost.

Together they show why viability claims need sound/reflection-preserving
presentations.

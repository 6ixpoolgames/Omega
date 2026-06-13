# Hidden Reach Loss Under Bad Presentation v0

Status: foundational counterexample note

This note records the presentation-level dual of phantom reachability:

```text
a bad presentation can hide exact reachability loss
```

This does not define value, agency, identity, alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/HiddenLossUnderBadPresentation.lean
```

## Core Idea

If a transition loses reachability:

```text
ReachLossStep D target x y
```

and a presentation maps:

```text
present x = present y
```

then the presentation hides the exact difference between:

```text
x reaches target
y does not reach target
```

## Core Definitions

```text
ReachabilityTarget D target x := Reach D target x
```

```text
PresentationHidesReachLoss D target present x y
```

means the pair is a reach-loss step and the presentation erases the pair.

## Core Theorems

```text
reachLoss_targetSeparated
```

A reach-loss step separates the exact reachability target.

```text
hiddenReachLoss_obstructs_presentation
```

The presentation obstructs the reachability target.

```text
hiddenReachLoss_blocks_targetRespect
```

The reachability target is not constant on the presentation fibers.

## Finite Witness

The file reuses the `start -> dead` reach-loss witness and maps all states to
`Unit`. Lean proves that this constant presentation hides the loss.

## Interpretation

Phantom reachability says an abstraction can invent a path.

Hidden reach loss says an abstraction can erase the fact that a path was lost.

Together they show why reachability claims need sound/reflection-preserving
presentations.

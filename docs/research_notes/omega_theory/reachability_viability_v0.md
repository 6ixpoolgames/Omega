# Reachability and Viability v0

Status: foundational theorem note

This note records the first dynamics layer over predicate fixed points.

The purpose is narrow:

```text
reachability = least fixed point
viability    = greatest fixed point
```

This does not define value, agency, alignment, identity, irreversible loss, or
Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/ReachabilityViability.lean
```

## Dynamics

The transition system is:

```text
Dyn:
  State
  Next : State -> State -> Prop
```

`Next x y` means state `x` can step to state `y`.

## Reachability

The reachability operator is:

```text
reachOp target p x :=
  target x or exists y, Next x y and p y
```

The reach set is:

```text
Reach target := lfp (reachOp target)
```

Lean proves:

```text
reachOp_mono
reach_fixed
target_sub_reach
reach_step
```

## Viability

The viability operator is:

```text
viabilityOp safe p x :=
  safe x and exists y, Next x y and p y
```

The viability kernel is:

```text
Viable safe := gfp (viabilityOp safe)
```

Lean proves:

```text
viabilityOp_mono
viability_fixed
viable_sub_safe
viable_has_successor
```

## Why This Matters

This is the formal bridge from consequence/presentation work toward the
Gradient Ethics safety direction.

Reachability captures what can be reached.

Viability captures what can continue while satisfying a declared safety
predicate.

Later modules can ask:

```text
when does erasure contract reachability?
when does a transition leave the viability kernel?
when can an unsound quotient fabricate apparent reachability?
```

Those are future claims. This file only supplies the fixed-point objects.

## Claim Boundary

This note does not claim reachability is value.

It does not claim viability is alignment.

It only defines and proves basic fixed-point facts for reachability and
viability in a nondeterministic transition system.

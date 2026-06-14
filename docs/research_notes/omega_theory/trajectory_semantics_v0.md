# Trajectory Semantics v0

Status: foundational theorem note

This note records the first operational semantics for the fixed-point
reachability and viability layer.

The fixed-point layer defines:

```text
Reach  = least fixed point of the reachability operator
Viable = greatest fixed point of the viability operator
```

Those definitions are mathematically standard, but they are not yet the
path-language that outside readers usually expect. This note closes the first
part of that gap.

This is not a value, agency, identity, alignment, or Omega claim.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/TrajectorySemantics.lean
```

## Finite Path Reachability

Lean defines:

```text
FinitePath D x y
```

for finite paths in a nondeterministic transition system, and:

```text
FinitePathToTarget D target x
```

when some finite path from `x` ends in a target state.

The core theorem is:

```text
reach_iff_finitePathToTarget
```

So the fixed-point predicate `Reach D target x` is exactly equivalent to
existence of a finite path from `x` to the declared target.

The supporting theorems are:

```text
finitePathToTarget_of_target
finitePathToTarget_step
finitePathToTarget_prefixed
finitePath_endpoint_reaches
finitePathToTarget_implies_reach
reach_implies_finitePathToTarget
```

## Viability and Safe Prefixes

Lean defines:

```text
SafePrefix D safe n x
```

where `n` counts transitions. A zero-length safe prefix requires only that the
current state is safe.

It also defines:

```text
ArbitrarilyLongSafePrefixes D safe x
```

meaning `x` has a safe prefix of every finite transition length.

The core theorem is:

```text
viable_implies_arbitrarilyLongSafePrefixes
```

So a viable state supports arbitrarily long finite safe prefixes.

## Claim Boundary

The viability result is intentionally one-way:

```text
Viable -> arbitrarily long finite safe prefixes
```

The file does not claim:

```text
arbitrarily long finite safe prefixes -> Viable
Viable iff infinite safe trajectory
compactness or Koenig-style path extraction
finite branching
choice principles for infinite paths
```

Those require additional assumptions and should be added only when explicitly
needed.

## Why This Matters

The trajectory layer now has an operational reading:

```text
Reach is finite path reachability.
Viable supplies indefinitely extendable finite safe behavior.
```

That makes the fixed-point machinery more legible for viability theory and for
later Gradient Ethics bridge work, while preserving the current claim boundary.

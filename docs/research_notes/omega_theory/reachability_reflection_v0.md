# Reachability Reflection v0

Status: foundational theorem note

This note records the positive counterpart to the phantom reachability
counterexample.

The core statement is:

```text
if an abstract presentation reflects targets and steps back to the exact
system, then abstract reachability implies exact reachability
```

This does not define value, agency, identity, alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/ReachabilityReflection.lean
```

## Problem

`PhantomReachability.lean` proves that an unsound presentation can fabricate an
abstract path that does not exist in the exact system.

The positive question is:

```text
what contract prevents that?
```

## Reflection Contracts

For exact dynamics `DX`, abstract dynamics `DQ`, and a presentation:

```text
present : DX.State -> DQ.State
```

the file defines:

```text
TargetReflects
```

meaning abstract target membership of `present x` implies exact target
membership of `x`.

It also defines:

```text
StepReflects
```

meaning every abstract step out of `present x` is witnessed by some exact step
out of `x`.

In symbols:

```text
DQ.Next (present x) z
  -> exists y, DX.Next x y and present y = z
```

## Main Theorem

Lean proves:

```text
abstractReach_reflects_exactReach
abstractFinitePath_reflects_exactFinitePath
```

If a presentation reflects targets and steps, then:

```text
Reach DQ targetQ (present x)
  -> Reach DX targetX x
```

Using the operational path semantics for `Reach`, Lean also proves:

```text
FinitePathToTarget DQ targetQ (present x)
  -> FinitePathToTarget DX targetX x
```

There is also an unpackaged version:

```text
abstractReach_reflects_exactReach_of_reflects
abstractFinitePath_reflects_exactFinitePath_of_reflects
```

## Interpretation

This is the dynamics-side abstraction contract for reachability claims.

It says:

```text
no invented targets + no invented transitions = no invented reachability
no invented targets + no invented transitions = no invented finite paths
```

This is separate from consequence-sound quotienting. A presentation may need
both consequence soundness and dynamics reflection, depending on the claim.

## Claim Boundary

This theorem does not say an abstraction is useful, minimal, or value-aligned.

It only proves that the declared reflection contract is sufficient to prevent
abstract reachability from overstating exact reachability.

# Dynamics Abstraction Status v0

Status: onboarding/status note

This note summarizes the current dynamics-abstraction layer.

The layer does not define value, agency, identity, alignment, or Omega proper.
It defines fixed-point continuation objects and the abstraction contracts needed
to make claims about them.

## Fixed-Point Objects

```text
PredicateFixpoint.lean
ReachabilityViability.lean
```

The repo defines:

```text
Reach target := least fixed point of reachOp
Viable safe := greatest fixed point of viabilityOp
```

Reachability asks what can eventually reach a target.

Viability asks what can keep continuing while satisfying a declared safety
predicate.

## Phantom Results

```text
PhantomReachability.lean
PhantomViability.lean
```

Bad presentations can fabricate:

```text
apparent reachability
apparent viability
```

## Reflection Results

```text
ReachabilityReflection.lean
ViabilityReflection.lean
```

Reflection contracts prevent fabricated claims:

```text
target reflection + step reflection
  -> abstract reachability implies exact reachability

safety reflection + step reflection
  -> abstract viability implies exact viability
```

## Loss Results

```text
IrreversibleReachLoss.lean
IrreversibleViabilityLoss.lean
```

The repo now has exact loss objects:

```text
ReachLossStep
ViabilityLossStep
```

These capture transitions from available continuation to unavailable
continuation.

## Hidden-Loss Results

```text
HiddenLossUnderBadPresentation.lean
HiddenViabilityLossUnderBadPresentation.lean
```

Bad presentations can hide:

```text
reachability loss
viability loss
```

by mapping the before-loss and after-loss states together.

## Packaged Contract

```text
SafePresentationContract.lean
```

This packages consequence soundness with the relevant dynamics reflection
obligations.

## Current Strong Claim

The current layer supports this claim:

```text
Reachability and viability claims over abstractions require declared
soundness/reflection contracts.

Without those contracts, a presentation can fabricate continuation or hide
loss of continuation.
```

This is the theorem-shaped bridge toward the Gradient Ethics program. It is
not yet a theory of value or alignment.

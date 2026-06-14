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
SafeLossVisibility.lean
```

This packages consequence soundness with the relevant dynamics reflection
obligations.

`SafeLossVisibility.lean` packages the hidden-loss side:

```text
reachTargetRespect_implies_lossVisible
viabilityTargetRespect_implies_lossVisible
```

Target-respecting presentations cannot hide exact reachability-loss or
viability-loss steps.

## Failure And Blocker Matrix

| Failure mode | Lean file | Bad-presentation theorem | Blocking theorem |
| --- | --- | --- | --- |
| Fabricated reachability | `PhantomReachability.lean` | `unsound_merge_fabricates_phantom_reachability` / `unsound_merge_fabricates_phantom_finite_path` | `mergePresentation_not_reachabilitySafeContract`; generally `reachabilityContract_reflects_reach` and `reachabilityContract_reflects_finitePath` |
| Fabricated viability | `PhantomViability.lean` | `bad_presentation_fabricates_phantom_viability` / `bad_presentation_fabricates_arbitrarily_long_safe_prefixes` | `bad_presentation_not_viabilitySafeContract`; generally `viabilityContract_reflects_viability` and `viabilityContract_reflects_safePrefixes` |
| Hidden reachability loss | `HiddenLossUnderBadPresentation.lean` | `constantPresentation_hides_start_dead_reach_loss` / `constantPresentation_not_reachabilityRespecting` | `targetRespect_blocks_hiddenReachLoss`; packaged as `reachTargetRespect_implies_lossVisible` |
| Hidden viability loss | `HiddenViabilityLossUnderBadPresentation.lean` | `constantPresentation_hides_loop_dead_viability_loss` / `constantPresentation_not_viabilityRespecting` | `targetRespect_blocks_hiddenViabilityLoss`; packaged as `viabilityTargetRespect_implies_lossVisible` |

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

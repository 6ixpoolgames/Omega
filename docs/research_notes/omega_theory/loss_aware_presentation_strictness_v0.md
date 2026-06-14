# Loss-Aware Presentation Strictness v0

Status: foundational negative-control note

This note records why loss-aware contracts are strictly stronger than
safe/reflection contracts alone.

It does not define value, agency, identity, alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/LossAwarePresentationStrictness.lean
```

## Core Point

A safe/reflection contract prevents fabricated abstract continuation claims.
That is not the same as preserving visibility of exact loss.

Lean proves finite controls where:

```text
safe/reflection contract holds
loss visibility fails
loss-aware contract therefore fails
```

The examples use universal consequence comparison and an abstract system with
no abstract target/safety claims and no abstract steps. Reflection is therefore
vacuous, but the constant presentation still erases an exact loss step.

## Reachability

```text
reachSafeContract_without_lossVisibility
reachSafeContract_not_lossAware
```

The constant presentation over the reach-loss witness satisfies:

```text
ReachabilitySafePresentationContract
```

but fails:

```text
ReachLossVisibleToPresentation
```

so it cannot satisfy:

```text
LossAwareReachabilityPresentationContract
```

## Viability

```text
viabilitySafeContract_without_lossVisibility
viabilitySafeContract_not_lossAware
```

The constant presentation over the viability-loss witness satisfies:

```text
ViabilitySafePresentationContract
```

but fails:

```text
ViabilityLossVisibleToPresentation
```

so it cannot satisfy:

```text
LossAwareViabilityPresentationContract
```

## Interpretation

This proves the contract taxonomy is doing real work:

```text
safe/reflection:
  blocks fabricated continuation

loss visibility:
  blocks hidden exact loss

loss-aware:
  requires both
```

The strictness examples are intentionally degenerate. Their purpose is not to
model a useful abstraction; their purpose is to show that no-fabrication does
not imply loss visibility.

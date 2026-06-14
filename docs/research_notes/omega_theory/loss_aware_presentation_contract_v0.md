# Loss-Aware Presentation Contract v0

Status: foundational packaging note

This note records the combined contract for presentations that must not
fabricate continuation and must not hide exact continuation loss.

It does not define value, agency, identity, alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/LossAwarePresentationContract.lean
```

## Contract Taxonomy

The current dynamics abstraction layer separates three obligations:

```text
safe/reflection contract:
  no fabricated abstract reachability or viability

loss visibility:
  no hidden exact reachability or viability loss

loss-aware contract:
  both obligations together
```

## Reachability

```text
LossAwareReachabilityPresentationContract
```

packages:

```text
ReachabilitySafePresentationContract
ReachLossVisibleToPresentation
```

Lean proves:

```text
lossAwareReachability_reflects_reach
lossAwareReachability_reflects_finitePath
lossAwareReachability_blocks_hiddenReachLoss
lossAwareReachability_blocks_lossStep_erasure
```

So a loss-aware reachability presentation cannot fabricate reachability and
cannot erase exact reach-loss steps.

## Viability

```text
LossAwareViabilityPresentationContract
```

packages:

```text
ViabilitySafePresentationContract
ViabilityLossVisibleToPresentation
```

Lean proves:

```text
lossAwareViability_reflects_viability
lossAwareViability_reflects_safePrefixes
lossAwareViability_reflects_safePrefix
lossAwareViability_blocks_hiddenViabilityLoss
lossAwareViability_blocks_lossStep_erasure
```

So a loss-aware viability presentation cannot fabricate viability and cannot
erase exact viability-loss steps.

## Interpretation

Reflection prevents false positive continuation claims.

Loss visibility prevents loss from being hidden by a presentation.

Loss-aware contracts require both. This is the narrow dynamics-side bridge
toward irreversible-loss reasoning, not a value or alignment theorem.

## Strictness

The companion strictness file proves this is a real strengthening:

```text
formal/lean/OmegaProper/Trajectory/LossAwarePresentationStrictness.lean
```

Safe/reflection contracts can hold while loss visibility fails, so loss-aware
contracts are not merely a renaming of safe presentation contracts.

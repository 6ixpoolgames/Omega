# Safe Loss Visibility v0

Status: foundational packaging note

This note records the small positive guardrail around hidden reachability and
viability loss.

It does not define value, agency, identity, alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/SafeLossVisibility.lean
```

## Core Idea

The hidden-loss files prove that a bad presentation can erase an exact loss
step:

```text
before-loss state -> after-loss state
```

where the before-loss state still has reachability or viability and the
after-loss state does not.

`SafeLossVisibility.lean` names the positive condition:

```text
ReachLossVisibleToPresentation
ViabilityLossVisibleToPresentation
```

A presentation has loss visibility when it never identifies the source and
target of an exact loss step.

## Core Theorems

```text
reachTargetRespect_implies_lossVisible
viabilityTargetRespect_implies_lossVisible
```

If a presentation respects the exact reachability or viability target, it
cannot hide the corresponding exact loss steps.

The module also records the converse controls:

```text
hiddenReachLoss_blocks_visibility
reachLossVisibility_blocks_hiddenLoss
hiddenViabilityLoss_blocks_visibility
viabilityLossVisibility_blocks_hiddenLoss
```

## Finite Controls

The existing constant presentations remain bad examples:

```text
constantPresentation_not_reachLossVisible
constantPresentation_not_viabilityLossVisible
```

They collapse the before-loss and after-loss states, so they do not make exact
loss visible.

## Interpretation

This is the hidden-loss counterpart to the safe-presentation contract:

```text
do not merely prevent fabricated continuation;
also preserve visibility of exact continuation loss
```

The result is deliberately narrow. It only says that target-respecting
presentations cannot hide exact reachability or viability loss.

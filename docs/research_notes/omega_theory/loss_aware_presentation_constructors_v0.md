# Loss-Aware Presentation Constructors v0

Status: theorem note

This note records constructor theorems for building loss-aware presentation
contracts from simpler obligations.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/LossAwarePresentationConstructors.lean
```

## Background

`LossAwarePresentationContract.lean` defines two packaged contracts:

```text
LossAwareReachabilityPresentationContract
LossAwareViabilityPresentationContract
```

Each combines:

```text
safe/reflection contract:
  no fabricated continuation claim

loss visibility:
  no exact loss step is collapsed by the presentation
```

The strictness module already shows that safe/reflection alone is not enough:
a presentation can avoid fabricating abstract continuation while still hiding
exact loss.

## Constructor Theorems

Lean now proves direct constructors:

```text
mk_lossAwareReachability
mk_lossAwareViability
```

These simply package an existing safe/reflection contract with an existing loss
visibility proof.

The useful sufficient-condition constructors are:

```text
mk_lossAwareReachability_of_targetRespect
mk_lossAwareViability_of_targetRespect
```

They say:

```text
safe/reflection contract
+ exact target is constant on presentation fibers
=> loss-aware contract
```

For reachability, the exact target is:

```text
Reach D target x
```

For viability, the exact target is:

```text
Viable D safe x
```

If a presentation is constant only across states with the same exact
reachability or viability target, it cannot hide a step from target-true to
target-false. Therefore loss visibility follows.

## Reflection Corollaries

The file also proves that contracts built by target respect inherit the
expected reflection results:

```text
targetRespectReachabilityConstructor_reflects_reach
targetRespectViabilityConstructor_reflects_viability
```

## Interpretation

This is a practical construction rule:

```text
To build a loss-aware abstraction, prove the usual safe/reflection obligations
and prove that the exact target does not vary inside presentation fibers.
```

It connects the target-invariance layer to the loss-aware abstraction layer.

This is still not value, agency, identity, alignment, or Omega proper. It is a
contract-construction theorem for the dynamics abstraction stack.

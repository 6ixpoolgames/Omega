# Lean Compression Checkpoint v0

Status: implementation checkpoint
Scope: Lean import-spine and theorem-spine compression
Claim boundary: architecture and theorem reuse; not new value, agency, identity,
or Omega claims

## Summary

This pass compresses the Lean stack in four places:

```text
1. trajectory import spine;
2. target post-processing for recovery;
3. pair-relative carrier transport;
4. fixed-point transport proof patterns.
```

It also removes the deprecated `ProtoOmega.Separations.MarginalJoint` facade
from the active `ProtoOmega` umbrella while leaving the facade file available
for direct compatibility imports.

## Import-Spine Compression

The top-level `OmegaProper.lean` no longer imports every trajectory leaf module
directly. It imports:

```text
OmegaProper.Trajectory
```

which is split into:

```text
OmegaProper.Trajectory.Consequence
OmegaProper.Trajectory.Presentation
OmegaProper.Trajectory.Closure
OmegaProper.Trajectory.Dynamics
OmegaProper.Trajectory.Carrier
```

This does not change theorem content. It makes the public theory map closer to
the conceptual stack:

```text
consequence facts;
presentation and quotient discipline;
closure/common-fact discipline;
dynamics and fixed points;
carrier and recurrent-support transport.
```

## Target Post-Processing

The recovery layer now has:

```text
OmegaProper.Recovery.TargetPostprocessing
```

Core principle:

```text
recovering a finer target implies recovery of any deterministic
post-processing of that target.
```

Joint-to-marginal recovery is now an instance using:

```text
Prod.fst
Prod.snd
```

The recovery layer is not compressed into one mega-definition. Deterministic,
randomized, robust, prior-relative, joint, and policy-conditioned recovery
remain separate axes because they represent genuinely different commitments.

## Carrier Transport

The recurrent-support stack now has:

```text
OmegaProper.Trajectory.CarrierTransport
```

This packages the repeated last step in several support-handoff proofs:

```text
target support recurrent viable;
target endpoints lie in the support;
target endpoints are internally connected both ways;
source merge separation transfers to the target endpoints;
therefore recurrent carrying transfers.
```

The first consumer is `RecurrentSupportLineage`, which now factors its lineage
handoff through this generic carrier-transport theorem.

This remains a sufficient transport certificate. It is not identity,
recoverability, agency, value, or Omega.

## Fixed-Point Transport

The trajectory layer now has:

```text
OmegaProper.Trajectory.FixedPointTransport
```

It packages two proof patterns:

```text
lfp reflection:
  abstract lfp membership reflects through a fiber-wise prefixed witness.

gfp reflection:
  abstract gfp membership reflects when abstract postfixed predicates pull
  back to exact postfixed predicates.
```

`ReachabilityReflection` and `ViabilityReflection` now route their core proofs
through these generic lemmas.

## Legacy Marginal/Joint Facade

`ProtoOmega.Separations.MarginalJointNative` is the active Alpha-native module.
The deprecated `ProtoOmega.Separations.MarginalJoint` facade remains in the
tree for direct compatibility imports, but it is no longer imported by the
active `ProtoOmega` umbrella.

## Non-Compression Boundary

This pass intentionally does not collapse:

```text
all recovery modes into one definition;
all carrier transfer variants into one opaque mega-contract;
all marginal/joint results into one theorem;
all dynamics reflection results into one abstract-interpretation framework.
```

Those would over-compress distinct commitments. The compression here is
therefore structural and theorem-sharing, not semantic flattening.

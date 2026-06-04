# ProtoOmega Marginal/Joint Native v0

Status: Lean-checked Alpha-native finite separation
Scope: marginal transport coverage versus strictly joint transport coverage

## Summary

This pass rebuilds the marginal/joint separation over native transport:

```text
AlphaCore
-> ProtoOmega.Transport.Native
-> ProtoOmega.Separations.MarginalJointNative
```

The checked result is:

```text
marginal_non_erasure_not_joint_non_erasure
```

It says a transport can cover declared marginal distinctions without covering a
strictly joint distinction.

## Lean Artifact

```text
formal/lean/ProtoOmega/Separations/MarginalJointNative.lean
```

Build command:

```powershell
cd formal\lean
lake build ProtoOmega
lake build AlphaOmega
lake build OmegaCore
```

## Construction

The source distinction presentation has:

```text
bot
margA
margB
joint
```

with:

```text
bot <= margA <= joint
bot <= margB <= joint
```

The target distinction presentation has:

```text
bot
outA
outB
```

with no target distinction fine enough to recover the source joint distinction.

The native transport covers marginals:

```text
margA -> outA
margB -> outB
```

and their weaker source distinctions, but not `joint`.

## Checked Theorems

```text
marginal_non_erasing:
  the marginal requirement set is covered

joint_not_non_erasing:
  the strictly joint requirement set is not covered

marginal_non_erasure_not_joint_non_erasure:
  marginal coverage does not imply joint coverage
```

## Relationship To Legacy OmegaCore

This replaces the theorem content of:

```text
OmegaCore/MarginalJoint.lean
```

The old facade remains temporarily:

```text
formal/lean/ProtoOmega/Separations/MarginalJoint.lean
```

## Claim Boundary

This is a finite transport separation. It is not an empirical result, not a
compatibility result, and not an Omega-level result.

It does not define:

```text
value
valuerhood
agency
life
identity
viability
lushness
anti-value
alignment
completion
```

## Next Targets

Recommended next conversions:

```text
1. OmegaAdapters.FiniteBoolean native pass
2. OmegaAdapters.FiniteChannel native pass
3. Probabilistic channel adapter native pass
```

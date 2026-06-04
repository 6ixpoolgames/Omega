# ProtoOmega Recoverability Native v0

Status: Lean-checked Alpha-native recoverability layer
Scope: recoverability, requirement-relative non-erasure, weakening/strengthening, composition, monotonicity

## Summary

This pass rebuilds the recoverability subset of legacy `OmegaCore.NormalLax`
over the Alpha-native transport layer:

```text
AlphaCore
-> ProtoOmega.Transport.Native
-> ProtoOmega.Recoverability.Native
```

It is the second real native ingestion after `ProtoOmega.Transport.Native`.

## Lean Artifacts

Checked files:

```text
formal/lean/ProtoOmega/Recoverability/Native.lean
formal/lean/ProtoOmega/Recoverability/NativeExamples.lean
formal/lean/ProtoOmega/Recoverability/LegacyBridge.lean
```

Build command:

```powershell
cd formal\lean
lake build ProtoOmega
lake build AlphaOmega
lake build OmegaCore
```

## Scope

`Native.lean` defines:

```text
ContextCategory:
  contexts and declared unfoldings, using Hom to avoid conflict with
  AlphaCore.Frame.Rel

NativeModel:
  context category
  Alpha frame for each context
  presentation-level distinction order for each frame
  native transport assignment for each unfolding
  identity-normality
  lax composition

Recovers:
  native transport along a declared unfolding

NonErasing:
  requirement-relative transport coverage
```

Checked consequences:

```text
identity_recoverability
identity_recoverability_iff
recoverability_weaken_source
recoverability_strengthen_target
compositional_recoverability
non_erasure_monotonicity
```

## Relationship To Alpha

This layer is downstream of Alpha. It imports `ProtoOmega.Transport.Native`,
which imports `AlphaCore`.

Alpha supplies:

```text
relation
distinction
asymmetry
```

ProtoOmega recoverability adds:

```text
presentation-level distinction order
transport assignment over declared unfoldings
coverage theorems
```

These are not primitive Alpha.

## Relationship To Legacy OmegaCore

This pass replaces only the recoverability subset of:

```text
OmegaCore/NormalLax.lean
```

Included:

```text
Recovers
NonErasing
identity recoverability
source weakening
target strengthening
compositional recoverability
non-erasure monotonicity
```

Excluded:

```text
ProcessBundle
JointPresentation
Compatible
```

Those remain downstream scaffolds for later conversion.

`LegacyBridge.lean` provides a one-way view from `NativeModel` into the old
`OmegaCore.NormalLaxDistinctionTransport` shape. It is for continuity and
theorem-transfer comparison, not for making legacy code primitive again.

## Important Separations

```text
Recoverability is transport coverage, not identity.

NonErasing is requirement-relative coverage, not value preservation.

Composition is theorem transfer through declared laxity, not substrate truth.

Compatibility and completion remain downstream.
```

## Claim Boundary

This module does not claim:

```text
Omega validation
value or valuerhood
agency
life
identity
viability
lushness
anti-value
alignment
compatibility
completion
```

## Next Targets

Recommended next conversions:

```text
1. ProtoOmega.Recoverability.Recurrent.Native
2. ProtoOmega.Separations.MarginalJoint.Native
3. OmegaAdapters native pass over finite Boolean/channel presentations
```

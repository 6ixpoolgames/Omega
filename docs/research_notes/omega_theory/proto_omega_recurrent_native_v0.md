# ProtoOmega Recurrent Native v0

Status: Lean-checked Alpha-native finite-chain recoverability layer
Scope: finite composable chains, stepwise recovery, composite recovery theorem

## Summary

This pass rebuilds finite-chain recurrent recoverability over:

```text
AlphaCore
-> ProtoOmega.Transport.Native
-> ProtoOmega.Recoverability.Native
-> ProtoOmega.Recoverability.RecurrentNative
```

It is the third native ingestion after native transport and native
recoverability.

## Lean Artifacts

Checked files:

```text
formal/lean/ProtoOmega/Recoverability/RecurrentNative.lean
formal/lean/ProtoOmega/Recoverability/RecurrentNativeExamples.lean
```

Build command:

```powershell
cd formal\lean
lake build ProtoOmega
lake build AlphaOmega
lake build OmegaCore
```

## Scope

`RecurrentNative.lean` defines:

```text
Chain:
  finite composable chain of declared unfoldings in a NativeModel

Chain.toHom:
  composite unfolding induced by the chain

RecoverChain:
  stepwise recovery along a chain
```

Checked:

```text
recoverChain_sound:
  stepwise recovery along a finite chain implies recovery through the chain
  composite

recoverChain_one:
  one-step chain recovery follows from a single step witness
```

## Relationship To Alpha

This layer is downstream of Alpha. It does not add primitive structure. It uses
the context category and native transport assignment already declared in
`ProtoOmega.Recoverability.Native`.

## Relationship To Legacy OmegaCore

This pass replaces the recurrent-recoverability subset of:

```text
OmegaCore/Recurrent.lean
```

The old facade remains available temporarily:

```text
formal/lean/ProtoOmega/Recoverability/Recurrent.lean
```

## Important Separations

```text
Finite-chain recovery is theorem transfer through declared composable
unfoldings.

It is not a substrate discovery claim.

It does not add joint presentation, compatibility, completion, or candidate
family structure.
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
1. ProtoOmega.Separations.MarginalJoint.Native
2. OmegaAdapters native pass over finite Boolean/channel presentations
3. Probabilistic channel adapter native pass
```

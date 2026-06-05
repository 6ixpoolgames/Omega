# OmegaAdapters Probabilistic Channel Cascade Native v0

Status: Lean-checked Alpha-native adapter conversion
Scope: finite natural-weight cascade error bounds over a shared path ensemble

## Summary

This pass migrates the probabilistic-channel cascade theorem into the native
adapter stack:

```text
AlphaCore
-> ProtoOmega.Transport.Native
-> OmegaAdapters.FiniteChannelNative
-> OmegaAdapters.ProbabilisticChannelNative
-> OmegaAdapters.ProbabilisticChannelCascadeNative
```

The stable adapter path:

```text
formal/lean/OmegaAdapters/ProbabilisticChannel.lean
```

now imports both the native probabilistic core and the native cascade layer.
The fixed-declared versus Bayes-best policy example remains a separate pending
native migration pass.

## Lean Artifact

```text
formal/lean/OmegaAdapters/ProbabilisticChannelCascadeNative.lean
```

The native cascade layer defines:

```text
chanComp:
  natural-weight channel composition by finite path summation

tripleWeight:
  path weight pi(x) * K(x,y) * L(y,z)

cascadeTotalMass:
  total mass of the finite path ensemble

cascadeCompositeErrorMass:
  composite decoder error over the path ensemble

cascadeFirstErrorMass / cascadeSecondErrorMass:
  stage decoder errors lifted to the same path ensemble
```

## Checked Theorem Surface

The native module checks:

```text
cascade_composite_error_le_stage_errors:
  composite decoder error is bounded by first-stage plus second-stage decoder
  error over the same weighted path ensemble

cascade_error_bound_same_denominator:
  same-denominator threshold form of the cascade union bound

cascadeTotalMass_eq_totalMass_chanComp:
  cascade path-ensemble total mass agrees with composed-channel total mass

cascadeCompositeErrorMass_eq_errorMass_chanComp:
  cascade composite error mass agrees with ordinary composed-channel error mass
```

## Relationship To Legacy OmegaCore

This replaces the cascade-composition portion of:

```text
OmegaCore/Presentations/ProbabilisticChannel.lean
```

The policy-separation example remains checked in the old `OmegaCore` namespace
until the next native pass.

## Claim Boundary

This is a finite stochastic cascade theorem over declared natural-weight
channels and decoders. Policy, empirical, and compatibility semantics remain
outside this module.

## Next Targets

Recommended next conversions:

```text
1. Probabilistic channel policy native pass
2. Adapter-failure examples native pass
3. OmegaProper scaffold native cleanup
```

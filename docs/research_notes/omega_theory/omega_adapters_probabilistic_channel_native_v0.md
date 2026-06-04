# OmegaAdapters Probabilistic Channel Native v0

Status: Lean-checked Alpha-native adapter conversion, first slice
Scope: finite natural-weight probabilistic recovery over native channel support

## Summary

This pass rebuilds the first probabilistic-channel slice over the active
Alpha/Omega stack:

```text
AlphaCore
-> ProtoOmega.Transport.Native
-> OmegaAdapters.FiniteChannelNative
-> OmegaAdapters.ProbabilisticChannelNative
```

The stable adapter path:

```text
formal/lean/OmegaAdapters/ProbabilisticChannel.lean
```

now imports the native first-slice implementation. Native cascade composition
and fixed-declared versus Bayes-best policy separation remain separate pending
migration passes.

## Lean Artifact

```text
formal/lean/OmegaAdapters/ProbabilisticChannelNative.lean
```

The native module defines:

```text
Supports:
  positive natural-weight channel support

supportRel:
  positive-weight support projection into the native finite-channel adapter

successMass / errorMass / totalMass:
  unnormalized finite decoder-success, decoder-error, and channel/prior masses

PerfectProbRecovers:
  successMass = totalMass

ProbRecoversAtLeast:
  cross-multiplied threshold comparison
```

## Checked Theorem Surface

The native module checks:

```text
exactSupportRecoverable_iff_nativeExactRecovers:
  existential exact support recovery agrees with native finite-channel exact
  recovery over positive-weight support, in the shared label-universe case

successMass_add_errorMass_eq_totalMass:
  success and error mass account for total channel/prior mass

perfectProb_fullPrior_implies_exactSupport:
  perfect probabilistic recovery under a full-support prior implies exact
  support recovery

exactSupport_implies_perfectProb:
  exact support recovery implies perfect probabilistic recovery

perfectProb_not_exact_without_full_prior:
  perfect probabilistic recovery under a non-full-support prior need not imply
  exact support recovery

highProb_not_exactSupport:
  high probabilistic recovery can coexist with support-level ambiguity
```

## Relationship To Legacy OmegaCore

This replaces the exact/probabilistic separation portion of:

```text
OmegaCore/Presentations/ProbabilisticChannel.lean
```

The cascade composition theorem and policy-separation example are not migrated
in this pass. They remain checked in the old `OmegaCore` namespace until their
own native passes.

## Claim Boundary

This is a finite stochastic measurement presentation over native channel
support. Cascade, policy, empirical, and compatibility semantics remain outside
this first slice.

## Next Targets

Recommended next conversions:

```text
1. Probabilistic channel cascade native pass
2. Probabilistic channel policy native pass
3. Adapter-failure examples native pass
```

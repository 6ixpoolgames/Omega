# OmegaAdapters Finite Channel Native v0

Status: Lean-checked Alpha-native adapter conversion
Scope: finite channel / observable-partition presentation

## Summary

This pass rebuilds the finite channel adapter over the active Alpha/Omega stack:

```text
AlphaCore
-> ProtoOmega.Transport.Native
-> OmegaAdapters.FiniteChannelNative
```

The stable adapter path remains:

```text
formal/lean/OmegaAdapters/FiniteChannel.lean
```

but it now imports the native implementation instead of the old
`OmegaCore.Presentations.FiniteChannel` facade.

## Lean Artifact

```text
formal/lean/OmegaAdapters/FiniteChannelNative.lean
```

The native adapter defines:

```text
ObsDist:
  observable labeling / partition of a carrier

obsAlphaFrame:
  Alpha frame whose distinctions are observable labelings

Refines:
  target observation is fine enough to decode source observation

ExactRecovers:
  exact decoder recovery through channel support

channelTransport:
  support-channel-induced native transport over observable distinctions
```

## Checked Theorem Surface

The native module mirrors the useful legacy theorem surface:

```text
exactRecovers_id_iff_refines:
  identity channel recovery is exactly distinction refinement

exactRecovers_comp:
  exact channel recovery composes through support-channel composition

channelTransport_comp_subset:
  channel composition induces native lax-composition inclusion

exact_recovers_changed_carrier_comp:
  exact recovery composes across changed carrier types

not_exact_recovers_constant_bit:
  a constant channel fails to recover a nontrivial bit distinction

exact_recovers_constant_trivial:
  the same constant channel recovers the trivial source distinction
```

## Relationship To Legacy OmegaCore

This replaces the theorem content of:

```text
OmegaCore/Presentations/FiniteChannel.lean
```

The old `OmegaCore` file remains buildable as archive-compatible provenance,
but active adapter imports now route through:

```text
OmegaAdapters.FiniteChannelNative
```

## Claim Boundary

This is a finite support-channel presentation. Downstream probabilistic,
empirical, and compatibility semantics remain outside this module.

## Next Targets

Recommended next conversions:

```text
1. Probabilistic channel adapter native pass
2. Probabilistic channel policy native pass
3. Adapter-failure examples native pass
```

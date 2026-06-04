# OmegaAdapters Finite Boolean Native v0

Status: Lean-checked Alpha-native adapter conversion
Scope: finite Boolean relation-support presentation

## Summary

This pass rebuilds the finite Boolean adapter over the active Alpha/Omega stack:

```text
AlphaCore
-> ProtoOmega.Transport.Native
-> OmegaAdapters.FiniteBooleanNative
```

The stable adapter path remains:

```text
formal/lean/OmegaAdapters/FiniteBoolean.lean
```

but it now imports the native implementation instead of the old
`OmegaCore.Presentations.FiniteBoolean` facade.

## Lean Artifact

```text
formal/lean/OmegaAdapters/FiniteBooleanNative.lean
```

The native adapter defines:

```text
Event:
  Boolean predicates over a carrier

EventAlphaFrame:
  Alpha frame whose distinctions are event predicates

EventLe:
  support-inclusion order over events

SupportRecovers:
  existential forward-image support recovery

supportTransport:
  relation-induced native transport
```

## Checked Theorem Surface

The native module mirrors the useful legacy theorem surface:

```text
supportTransport_id_iff:
  identity relation agrees with native identity transport

supportTransport_comp_subset:
  relational composition induces the native lax-composition inclusion

changed_carrier_composite_recovery:
  support recovery composes across changed carrier types
```

## Relationship To Legacy OmegaCore

This replaces the theorem content of:

```text
OmegaCore/Presentations/FiniteBoolean.lean
```

The old `OmegaCore` file remains buildable as archive-compatible provenance,
but active adapter imports now route through:

```text
OmegaAdapters.FiniteBooleanNative
```

## Claim Boundary

This is a finite Boolean support presentation. Downstream empirical and
compatibility semantics remain outside this module.

## Next Targets

Recommended next conversions:

```text
1. OmegaAdapters.FiniteChannel native pass
2. Probabilistic channel adapter native pass
3. Adapter-failure examples native pass
```

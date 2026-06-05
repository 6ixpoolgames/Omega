# OmegaAdapters Presentation-Native Bridge Repair v0

Status: Lean-checked adapter architecture repair
Scope: finite Boolean/channel presentation split plus explicit substrate bridge

## Purpose

This pass follows the `ProtoOmega.Presentation.Native` split by making the
finite Boolean and finite channel adapters expose their primary presentation
machinery without relying on inert Alpha frames.

The repair separates:

```text
presentation-native:
  distinction, separation, order, and transport objects for a presentation

Alpha-frame compatible:
  existing native transport surfaces kept for downstream modules

substrate bridge:
  explicit proof object required before a presentation can be treated as
  substrate-contacting
```

## Lean Artifacts

Updated:

```text
formal/lean/OmegaAdapters/FiniteBooleanNative.lean
formal/lean/OmegaAdapters/FiniteChannelNative.lean
formal/lean/OmegaAdapters.lean
```

Added:

```text
formal/lean/OmegaAdapters/SubstrateBridge.lean
```

## Finite Boolean Presentation

`OmegaAdapters.FiniteBooleanNative` now exposes:

```text
eventSepPresentation
eventDistPresentation
eventPresentationOrder
supportPresentationTransport
supportPresentationTransport_id_iff
supportPresentationTransport_comp_subset
```

The previous `EventAlphaFrame`, `eventOrder`, and `supportTransport` surface is
retained so downstream modules continue to build, but the presentation-native
surface is now explicit.

## Finite Channel Presentation

`OmegaAdapters.FiniteChannelNative` now exposes:

```text
obsSepPresentation
obsDistPresentation
obsPresentationOrder
channelPresentationTransport
channelPresentationTransport_comp_subset
```

The previous `obsAlphaFrame`, `obsDistOrder`, and `channelTransport` surface is
retained for compatibility with downstream probabilistic modules.

## Substrate Bridge

`OmegaAdapters.SubstrateBridge` adds:

```text
SubstrateBridge
RelationBridge
alphaFrameSelfBridge
alphaFrameRelBridge
```

This is deliberately separate from the finite Boolean/channel presentation
objects. A presentation can satisfy presentation-level transport laws without
thereby proving that it was induced by a substrate's primitive
relation/asymmetry structure. That bridge is a separate proof obligation.

## Validation

Validated by:

```powershell
lake build OmegaAdapters
```

Broader validation should still build `AlphaOmega` and run the adapter boundary
tests before committing.

## Next Repairs

Recommended next steps:

```text
1. Add declared-decoder versus existential-decoder provenance split.
2. Recast probabilistic cascade through a path-ensemble evidence object.
3. Gather native adapter-failure examples into one audit layer.
```

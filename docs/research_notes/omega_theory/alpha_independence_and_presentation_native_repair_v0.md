# Alpha Independence and Presentation-Native Repair v0

Status: Lean-checked anti-self-validation repair
Scope: primitive non-collapse and presentation/substrate separation

## Purpose

This pass adds two guardrails before further native migration:

```text
AlphaCore.Independence:
  finite examples showing that the primitive roles do not collapse into one
  another.

ProtoOmega.Presentation.Native:
  presentation-native distinction/order/transport structures that can be used
  without pretending a full Alpha substrate has been supplied.
```

The goal is to prevent a common failure mode:

```text
define a presentation;
prove the laws built into that presentation;
then accidentally describe the result as substrate-revealing.
```

## Lean Artifacts

Added:

```text
formal/lean/AlphaCore/Independence.lean
formal/lean/ProtoOmega/Presentation/Native.lean
```

Updated:

```text
formal/lean/AlphaCore.lean
formal/lean/ProtoOmega.lean
```

## Alpha Independence

`AlphaCore.Independence` adds finite non-collapse examples:

```text
relation_without_distinction
distinction_without_relation
relation_and_distinction_without_asymmetry
reach_irreversibility_without_asymmetry
asymmetry_implies_relation_and_distinction
```

The point is structural. Relation, distinction, asymmetry, and reach
irreversibility are not interchangeable. Some implications are typed
consequences of the Alpha frame; the reverse implications are not silently
available.

## Presentation-Native Layer

`ProtoOmega.Presentation.Native` adds:

```text
DistPresentation
SepPresentation
DistOrder
Transport
Transport.id
Transport.compose
AlphaCore.Frame.toSepPresentation
AlphaCore.Frame.toDistPresentation
```

This gives the project a clean way to say:

```text
presentation-native:
  distinction/order/transport machinery that can be stated without full
  substrate contact.

Alpha-native:
  machinery that actually depends on the Alpha primitive frame.
```

The bridge functions from `AlphaCore.Frame` are intentionally forgetful. They
do not turn an arbitrary presentation into a substrate bridge; they only expose
the distinction/separation part of an Alpha frame when such a frame already
exists.

## Next Repairs

Recommended next steps:

```text
1. Refactor finite Boolean and finite channel adapters toward
   presentation-native targets where possible.
2. Add explicit substrate-to-presentation bridge objects.
3. Split declared decoder recovery from existential decoder recovery.
4. Recast the cascade theorem through a path-ensemble evidence object.
5. Gather native adapter-failure examples into one audit layer.
```

## Validation

Validated by:

```powershell
lake build AlphaCore
lake build ProtoOmega
```

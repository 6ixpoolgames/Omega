# Presentation Soundness Pattern v0

Status: active compression note
Scope: generic soundness pattern for presentations, quotients, summaries, and coarse views
Claim boundary: not boundary realism, not value, not agency, not Omega validation

## Purpose

This note documents:

```text
formal/lean/OmegaProper/Trajectory/PresentationSoundness.lean
formal/lean/OmegaProper/Trajectory/PresentationSoundnessInstances.lean
```

The compression is:

```text
a presentation is sound when its kernel avoids forbidden merges.
```

## Generic Form

```text
SoundPresentationBy Forbidden present :=
  forall x y,
    present x = present y ->
      not (Forbidden x y)
```

This gives one shared language for several local notions:

```text
primitive-sound presentation;
consequence-sound quotient;
target-respecting presentation;
certified-carrier endpoint visibility.
```

## Existing Instances

Primitive soundness:

```text
PrimitiveSoundPresentation A present
<->
SoundPresentationBy (PrimitiveApart A) present
```

Consequence sound quotient:

```text
SoundQuotient S present
<->
SoundPresentationBy (ConsequenceMergeSeparated S) present
```

Target presentation invariance:

```text
TargetRespectsPresentation target present
<->
SoundPresentationBy (TargetSeparatedBy target) present
```

Carrier certificate visibility:

```text
CarrierCertificate S Next safe C x y
-> ConsequenceMergeSeparated S x y
```

so generic soundness by `ConsequenceMergeSeparated S` keeps certified endpoints
visible.

## Why This Matters

This removes a recurring source of conceptual duplication. The project no
longer needs separate explanations for every kind of sound presentation. The
shared structure is:

```text
what pairs are forbidden to merge?
does this presentation merge any of them?
```

The answer determines soundness for that declared target.

## Non-Claims

The generic pattern does not say which forbidden relation is correct. That is
supplied by the layer:

```text
primitive apartness at Alpha level;
consequence merge-separation at consequence level;
target distinction at target level;
certified carrier pair at carrier level.
```

The pattern only compresses the soundness discipline.

## Related Notes

- [alpha_primitive_derived_surfaces_v0.md](alpha_primitive_derived_surfaces_v0.md)
- [primitive_exposure_realization_bridge_v0.md](primitive_exposure_realization_bridge_v0.md)
- [standard_core_compression_v0.md](standard_core_compression_v0.md)
- [layer_a_theorem_spine_v0.md](layer_a_theorem_spine_v0.md)

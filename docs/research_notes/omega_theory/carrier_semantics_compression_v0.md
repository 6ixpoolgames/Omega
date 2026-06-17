# Carrier Semantics Compression v0

Status: active compression note
Scope: support, generated carrier, and trajectory-language unification
Claim boundary: not identity, not objecthood, not agency, not value, not Omega validation

## Purpose

This note documents:

```text
formal/lean/OmegaProper/Trajectory/CarrierSemantics.lean
```

The compression is:

```text
carrier presentation -> carrier semantics -> carrier certificate
```

Raw support predicates, generated mutual-reach carriers, and path-language
views are all presentations of carrier semantics.

## Generic Carrier Semantics

```text
CarrierSemantics X:
  carrier : X -> Prop
  path    : X -> X -> Prop
```

The raw support denotation is:

```text
CarrierSemantics.ofCandidate Next C:
  carrier = C
  path    = internal paths through C under Next
```

The generated carrier denotation is:

```text
CarrierSemantics.ofGeneratedMutualReach Next Ambient x y
```

which uses the existing mutual-reach carrier candidate.

## Semantic Certificate

The compressed certificate shape is:

```text
recurrent carrier semantics
endpoint membership
round-trip path membership
merge-separated endpoint pair
```

The module proves:

```text
semantic certificate + path-match contract -> ordinary CarrierCertificate
ordinary CarrierCertificate -> semantic certificate for raw support semantics
generated mutual-reach certificate -> semantic certificate
```

## Why This Matters

This prevents raw support predicates from looking privileged.

The project can now say:

```text
support predicates are one carrier presentation;
generated carriers are another carrier presentation;
trajectory languages expose the semantics of either presentation;
certification is the validity check.
```

That is less identity-loaded than saying "this support is the thing."

## Non-Claims

Carrier semantics still does not define:

```text
object identity;
boundary realism;
agency;
valuerhood;
value;
Omega.
```

It only compresses the support/carrying layer into a cleaner semantic surface.

## Related Notes

- [carrier_certificate_v0.md](carrier_certificate_v0.md)
- [generated_carrier_v0.md](generated_carrier_v0.md)
- [carrier_trajectory_language_v0.md](carrier_trajectory_language_v0.md)
- [simulation_transfer_v0.md](simulation_transfer_v0.md)
- [layer_a_theorem_spine_v0.md](layer_a_theorem_spine_v0.md)

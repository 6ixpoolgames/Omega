# Primitive Exposure and Realization Bridge v0

Status: active formal note
Scope: bridge from Alpha-derived primitive surfaces to the later consequence and carrier stack
Claim boundary: not value, not agency, not identity, not Omega validation

## Purpose

This note documents the first explicit bridge from the new Alpha-derived
surfaces into the later Layer A stack.

The Lean files are:

```text
formal/lean/OmegaProper/Trajectory/PrimitiveConsequenceExposure.lean
formal/lean/OmegaProper/Trajectory/PrimitiveDynamicsRealization.lean
```

The bridge is deliberately contract-shaped:

```text
Alpha supplies primitive apartness and primitive paths.
Adapters expose primitive apartness as consequence separation.
Adapters realize primitive paths as transition paths.
Layer A then audits the resulting consequence and carrier facts.
```

This is not the claim that Alpha alone derives consequence, dynamics, value, or
agency.

## Consequence Exposure

The consequence exposure contract is:

```text
ConsequenceExposesPrimitiveApartness S :=
  every primitively apart pair is merge-separated by evaluated consequence.
```

It proves:

```text
primitive apartness blocks consequence identification under exposure;
joint primitive witnesses become consequence-bearing under exposure;
asymmetry witnesses become consequence-bearing under exposure;
primitive nondegeneracy plus exposure yields the existing ProtoTeleologicalSeed;
consequence-sound presentations are primitive-sound under exposure;
erasing an exposed primitive-apart pair makes a presentation consequence-unsound.
```

The important theorem shape is:

```text
PrimitiveNondegenerate A
+ ConsequenceExposesPrimitiveApartness S
-> ProtoTeleologicalSeed S
```

This is the corrected version of the proto-teleology claim. Primitive
nondegeneracy alone is not enough. Exposure is required.

## Dynamics Realization

The dynamics realization contract is:

```text
DynamicsRealizesPrimitiveRel A Next :=
  every primitive relation edge is an adapter transition edge.
```

It proves:

```text
primitive paths become internal adapter paths;
primitive mutual reach becomes adapter round-trip structure;
primitive mutual-reach carriers become generated mutual-reach carriers;
primitive mutual reach plus exposure can certify the top carrier, if the
adapter also supplies recurrence/safety for that carrier;
an asymmetry witness plus reverse primitive path can become a certified
recurrent carrier fact under exposure, realization, and recurrence/safety.
```

The important theorem shape is:

```text
PrimitiveMutualReach A x y
+ PrimitiveApart A x y
+ ConsequenceExposesPrimitiveApartness S
+ DynamicsRealizesPrimitiveRel A Next
+ RecurrentViableClass (top carrier)
-> CarrierCertificate S.toConsequenceSystem Next safe top x y
```

This keeps recurrent carrying downstream of explicit dynamics and recurrence
assumptions.

## Why This Matters

The bridge gives a clean pipeline:

```text
Alpha primitive witness
-> PrimitiveApart + PrimitivePath

PrimitiveApart + consequence exposure
-> ConsequenceMergeSeparated
-> ProtoTeleologicalSeed

PrimitivePath + dynamics realization
-> adapter internal paths
-> generated carrier candidates
-> carrier certificates when recurrence/safety and consequence exposure hold
```

This lets Alpha do more work without inflating it into the whole theory.

## Non-Claims

The bridge does not establish:

```text
all substrates expose primitive apartness;
all primitive paths are real dynamics;
all primitive mutual reach is safe or recurrent;
all primitive witnesses become carriers;
agency;
valuerhood;
value;
Omega-terminal structure.
```

The adapter must still declare and justify the exposure, realization, and
recurrence conditions.

## Related Notes

- [alpha_primitive_derived_surfaces_v0.md](alpha_primitive_derived_surfaces_v0.md)
- [layer_a_derivation_audit_v0.md](layer_a_derivation_audit_v0.md)
- [layer_a_theorem_spine_v0.md](layer_a_theorem_spine_v0.md)
- [carrier_certificate_v0.md](carrier_certificate_v0.md)
- [generated_carrier_v0.md](generated_carrier_v0.md)

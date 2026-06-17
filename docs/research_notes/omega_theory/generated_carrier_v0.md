# Generated Carrier v0

Status: canonical carrier-candidate repair
Scope: generated carrier predicates from mutual internal reach
Claim boundary: not identity, not boundary realism, not agency, not value, not Omega validation

## Purpose

This note documents:

```text
formal/lean/OmegaProper/Trajectory/GeneratedCarrier.lean
```

The problem it addresses:

```text
If supports are declared, how do we avoid arbitrary support choice?
```

The first answer is not a full SCC library. It is a small canonical candidate:

```text
MutualReachCarrier Next Ambient x y z
```

This says `z` is in the ambient region and is mutually internally reachable
with both endpoints `x` and `y`.

## Main Lean shape

```text
MutualReachCarrier Next Ambient x y z :=
  Ambient z
  and x reaches z internally through Ambient
  and z reaches x internally through Ambient
  and y reaches z internally through Ambient
  and z reaches y internally through Ambient
```

## Main results

```text
internalPath_mono_class
mutualReachCarrier_sub_ambient
mutualReachCarrier_contains_left
mutualReachCarrier_contains_right
certified_carrier_sub_mutualReachCarrier
mutualReachCarrier_certificate_of_recurrent
cycle_certificate_sub_generated
```

The central canonicality result is:

```text
Any already-certified carrier inside Ambient is contained in the mutual-reach
carrier generated around its certified endpoints.
```

So generated carrier is not just another arbitrary support name. It is a
candidate selected by path structure.

## What this does not solve

This is not yet:

```text
a finite SCC theorem;
a minimal carrier theorem;
a greatest safe recurrent carrier theorem;
object identity;
recoverability;
agency.
```

It is the first principled replacement for arbitrary carrier declaration.

## Related notes

- [carrier_certificate_v0.md](carrier_certificate_v0.md)
- [simulation_transfer_v0.md](simulation_transfer_v0.md)
- [layer_a_derivation_audit_v0.md](layer_a_derivation_audit_v0.md)

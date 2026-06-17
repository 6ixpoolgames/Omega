# Simulation Transfer v0

Status: principled transfer repair
Scope: map-based and relation-based simulation transfer for carrier certificates
Claim boundary: sufficient-condition layer only; not identity, not agency, not value, not Omega validation

## Purpose

This note documents:

```text
formal/lean/OmegaProper/Trajectory/SimulationTransfer.lean
```

The repair target is transfer.

Earlier transfer modules are useful, but contract-shaped:

```text
preserve these edges or paths;
keep safety;
avoid exits;
therefore carrying transfers.
```

`SimulationTransfer` adds a more principled surface:

```text
a map f sends old carrier states into a target carrier;
old internal edges are simulated by new internal paths between mapped states;
merge separation is preserved by f;
the target carrier is recurrent viable;
therefore the carrier certificate transfers to f x / f y.
```

It also adds the first relational version:

```text
a relation R connects old states to target representatives;
old internal edges are simulated by target paths between related representatives;
merge separation is preserved across related representatives;
the target carrier is recurrent viable;
therefore a carrier certificate transfers to some related target endpoint.
```

This avoids treating a function as the only acceptable transfer witness.

## Main Lean shape

```text
ImageInCarrier f C D
InternalEdgeSimulatedByPath Next0 Next1 C D f
InternalPathSimulated Next0 Next1 C D f
MergeSeparationPreservedByMap S f
CarrierMapSimulationContract S Next0 Next1 safe1 C D f

GraphRelation f
RelatedInCarrier R D x x'
InternalEdgeRelatedByPath Next0 Next1 C D R
MergeSeparationPreservedByRelation S R
CarrierRelationSimulationContract S Next0 Next1 safe1 C D R
```

Core theorems:

```text
certificate_transfers_by_map_simulation
mapSimulationContract_as_relationSimulationContract
certificate_transfers_by_relation_simulation_exists
```

## Why this is stronger than the old transfer layer

The old layer remains valid as a fallback sufficient-condition calculus.

This layer makes the correspondence explicit:

```text
old state -> mapped target state
old edge  -> target path
old pair  -> mapped pair
```

The relation version weakens the correspondence:

```text
old state -> one or more related target representatives
old edge  -> target path to a related representative
old pair  -> related target pair
```

The map version is now formally compressed as a special case of the relation
version, using `GraphRelation f`.

That is closer to simulation/refinement language and avoids treating exact
support identity as the only transfer route.

## What remains open

This is still not full bisimulation, quotient transfer, or boundary-invariant
support. Later work can strengthen:

```text
relation-based simulation
```

to:

```text
two-way bisimulation;
sound dynamic presentation;
trajectory-language transfer.
```

## Related notes

- [carrier_certificate_v0.md](carrier_certificate_v0.md)
- [generated_carrier_v0.md](generated_carrier_v0.md)
- [layer_a_derivation_audit_v0.md](layer_a_derivation_audit_v0.md)

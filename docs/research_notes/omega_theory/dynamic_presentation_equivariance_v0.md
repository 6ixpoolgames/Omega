# Dynamic Presentation Equivariance v0

Status: finite adapter audit pilot
Scope: exact finite transitions, presentations, and projected abstract dynamics
Claim boundary: not identity, not agency, not value, not Omega validation

## Purpose

Static presentation soundness is not enough for trajectory claims. A
presentation can preserve target labels while still lying about what follows.
Before viable-language or "lushness" counts are meaningful, the presentation
must commute with the dynamics being counted.

The finite relational adapter now includes:

```text
dynamic_presentation_equivariance
```

This audit checks a state transition, a presentation, and an abstract transition
over presentation labels.

## Exact Finite Contract

Given:

```text
next : State -> State -> Prop
p    : State -> Label
qnext : Label -> Label -> Prop
```

the audit computes:

```text
projected_exact_edges =
  { (p x, p y) | next x y }
```

It then checks two finite clauses:

```text
preservation:
  every projected exact edge is present in qnext

reflection:
  every qnext edge is the projection of some exact edge
```

The presentation is dynamically equivariant exactly when both clauses hold.

## Failure Modes

The payload separates two ways an abstract dynamics can fail:

```text
missing_projected_edges:
  exact dynamics has a projected edge that the abstract dynamics omits

phantom_abstract_edges:
  abstract dynamics adds an edge not induced by any exact transition
```

This distinction matters because downstream trajectory measures can fail in
opposite ways: they can hide possible continuations or fabricate possible
continuations.

## Why This Matters

The current closure and presentation audits answer static questions:

```text
which target facts survive this presentation family?
which pairs stay visible?
```

Dynamic equivariance answers the next question:

```text
does this presentation preserve the transition grammar used to count futures?
```

This is the first adapter brick needed before finite viable-language or
trajectory-count pilots. It does not say that the presentation is the right
model of a real system. It only says that, for the declared finite model, the
abstract transition is exactly the projection of the exact transition.

## Current Fixtures

The generated adversarial suite includes:

```text
generated_dynamic_equivariance:
  projected role dynamics matches the exact transition projection.

generated_dynamic_non_equivariance:
  abstract role dynamics both misses one projected edge and adds one phantom
  edge.
```

## Related Notes

- [finite_relational_adapter_design_v0.md](finite_relational_adapter_design_v0.md)
- [presentation_fact_closure_v0.md](presentation_fact_closure_v0.md)
- [phantom_reachability_under_unsound_quotient_v0.md](phantom_reachability_under_unsound_quotient_v0.md)
- [adapter_provenance_v0.md](adapter_provenance_v0.md)

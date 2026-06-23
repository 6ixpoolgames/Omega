# Dynamic Presentation Semantics v0

Status: finite adapter audit pilot
Scope: exact finite transitions, presentations, and projected abstract dynamics
Claim boundary: not identity, not agency, not value, not Omega validation

## Purpose

Static presentation soundness is not enough for trajectory claims. A
presentation can preserve target labels while still lying about what follows.
Before viable-language or "lushness" counts are meaningful, the presentation
must preserve process coherence for the dynamics being counted.

The finite relational adapter now includes:

```text
dynamic_edge_projection_exactness
dynamic_step_lifting
dynamic_path_lifting
```

The historical audit name `dynamic_presentation_equivariance` remains as a
compatibility alias for edge-projection exactness. That older name was too
strong: global edge projection is useful, but it is not enough to certify
coherent trajectories.

## Edge Projection Exactness

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

This is now called:

```text
dynamic_edge_projection_exactness
```

It says the abstract edge set is exactly the global image of the exact edge
set under the presentation.

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

## Why Edge Projection Is Not Enough

Edge projection exactness does not imply that abstract paths lift to coherent
exact paths.

Minimal splice pattern:

```text
exact:
  a -> b
  c -> d

presentation:
  p(a) = A
  p(b) = M
  p(c) = M
  p(d) = D

abstract:
  A -> M
  M -> D
```

The abstract edges are exactly the projected exact edges. But the abstract path:

```text
A -> M -> D
```

starting from `a` has no coherent exact lift. It silently switches from the
exact representative `b` to the different representative `c` inside the merged
fiber `M`.

This is the finite adapter version of a process artifact:

```text
the abstraction presents one continuous history,
but no single exact history realizes it.
```

## Step And Path Lifting

Representative-wise step lifting checks:

```text
for each exact state x and abstract edge p(x) -> q',
there exists y such that next x y and p(y) = q'.
```

Finite path lifting checks the corresponding finite-horizon condition:

```text
for each exact start x and abstract path from p(x),
there is a coherent exact path from x projecting to it.
```

These are still finite adapter audits, not a full coalgebraic theorem. They are
the practical repair needed before a presentation can be used for trajectory
or count claims.

## Why This Matters

The current closure and presentation audits answer static questions:

```text
which target facts survive this presentation family?
which pairs stay visible?
```

Dynamic equivariance answers the next question:

```text
does this presentation preserve coherent histories used to count futures?
```

This is the first adapter brick needed before finite viable-language or
trajectory-count pilots. It does not say that the presentation is the right
model of a real system. It only says that, for the declared finite model, the
selected dynamic audit condition holds.

## Current Fixtures

The generated adversarial suite includes:

```text
generated_dynamic_equivariance:
  projected role dynamics matches the exact transition projection.

generated_dynamic_non_equivariance:
  abstract role dynamics both misses one projected edge and adds one phantom
  edge.

generated_edge_exact_path_lifting_failure:
  the abstract edge relation is exactly the global projection of exact edges,
  but representative-wise step lifting and finite path lifting fail.
```

## Related Notes

- [finite_relational_adapter_design_v0.md](finite_relational_adapter_design_v0.md)
- [presentation_fact_closure_v0.md](presentation_fact_closure_v0.md)
- [phantom_reachability_under_unsound_quotient_v0.md](phantom_reachability_under_unsound_quotient_v0.md)
- [adapter_provenance_v0.md](adapter_provenance_v0.md)

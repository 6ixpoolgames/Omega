# ODT Supervisory-Control Docking v0

Status: adjacency note / control-theory docking
Scope: ODT0 Gate G2, robust corridors, and ambiguity-family containment
Claim boundary: not a full Ramadge-Wonham formalization, not controller
synthesis, not optimal control, not stochastic risk, not final value, not
agency, not Omega validation

## Purpose

ODT0 Gate G2 says:

```text
an action is licensed only if every concrete successor remains inside the
declared corridor.
```

The robust-corridor and ambiguity-family containment stack makes this gate a
fixed-point safety condition rather than an arbitrary prohibition.

This note positions that fact relative to supervisory control and shielding.

## Adjacent Shape

Supervisory control theory studies restrictions on a plant's behavior so that
the resulting behavior satisfies a specification, often aiming for a maximally
permissive supervisor under controllability constraints.

ODT0 is adjacent because its corridor is also a greatest fixed point:

```text
largest set S inside Constraint and Requirement
such that some allowed enabled action keeps all successors in S.
```

The ambiguity-family version says the action must be shared across all
candidate worlds:

```text
exists action a before model resolution;
forall models i, a is enabled and keeps successors inside S.
```

This is the reason the shared-action robust viability kernel can be strictly
smaller than the intersection of per-model corridors.

## Current Landed Theorems

The current Lean stack proves:

```text
robust corridor states satisfy the declared constraint and requirement;
robust corridor states have an allowed enabled corridor-preserving action;
an action with a successor outside the corridor fails the corridor gate;
finite ambiguity-family RVK reduces to the merged robust corridor with
family-enabled allowedness;
the ambiguity-family RVK is contained in every per-model corridor;
the intersection of per-model corridors can be too large;
stationary and finite-history fixed-point guarantees exist exactly on RVK;
stationary guarantees extract per-model infinite traces;
switching-adversary finite bad-prefix absence is equivalent to stationary
fixed-point guarantee.
```

## Delta From A Plain Safety Filter

G2 is only one gate.

ODT0 also requires:

```text
G1: the fact justifying the action reflects through a certified presentation;
G3: any decision-process quotient used in the justification is certified as
    consequence-inseparable.
```

So the ODT floor is not merely:

```text
block unsafe actions.
```

It is:

```text
block actions whose safety or permissibility claim is routed through an
uncertified map, and block actions that leave the declared corridor.
```

## What Is Not Claimed

This note does not claim:

```text
full supervisory-control equivalence;
maximally permissive supervisor synthesis;
controllability/observability theorem coverage;
probabilistic risk handling;
that the declared Constraint, Requirement, or ambiguity family is correct;
that persistence should be required;
agency, identity, valuerhood, moral standing, value, or Omega validation.
```

## Public Compression

ODT0 Gate G2 is a corridor-preservation safety filter with a fixed-point
semantics, but ODT adds map-certification and quotient-certification gates
before that safety filter can license a decision.

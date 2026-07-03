# Robust Continuation Corridor v0

Status: Lean theorem note / ODT0 bridge
Scope: controlled worst-case viability corridor for declared local requirements
Claim boundary: not value, not agency, not identity, not moral standing, not a full policy theory, not Omega validation

## Summary

This pass instantiates the abstract ODT0 `Corridor` predicate as a controlled
robust-continuation greatest fixed point.

The object is:

```text
RobustCorridor(D, Allowed, Requirement)
  = gfp S.
      Constraint(x)
      and Requirement(x)
      and exists allowed enabled action a
          such that every successor of (x,a) remains in S
```

The point is deliberately modest:

```text
If a state is in the corridor, some allowed action keeps it in the corridor.
If an action has any concrete successor outside the corridor, it cannot pass
the ODT0 corridor gate.
```

This is the first formal bridge from the decision floor to controlled
viability. It is not yet the full Gradient Ethics bridge because
`Requirement` remains supplied/certified rather than derived.

## Lean Surface

Files:

```text
formal/lean/OmegaProper/Decision/RobustCorridor.lean
formal/lean/OmegaProper/Decision/RobustCorridorExamples.lean
```

Core definitions:

```text
ActionRobustKeeps
RobustPre
robustCorridorOp
RobustCorridor
```

The fixed-point operator uses the existing predicate fixed-point layer:

```text
formal/lean/OmegaProper/Trajectory/PredicateFixpoint.lean
```

## Theorem Spine

### Monotonicity

```text
robustCorridorOp_mono
```

The controlled predecessor operator is monotone in the candidate set. This is
what allows the greatest fixed-point machinery to apply.

### Fixed Point

```text
robustCorridor_fixed
```

`RobustCorridor` is a fixed point of the robust-continuation operator.

### Requirement And Constraint Containment

```text
robustCorridor_sub_constraint
robustCorridor_sub_requirement
```

Every corridor state satisfies the declared concrete constraint and the
declared local requirement.

This is useful for the Gradient Ethics bridge, but it is also the main claim
boundary: the theorem preserves the supplied `Requirement`; it does not prove
that the requirement is value-relevant.

### Sustaining Action

```text
robustCorridor_has_action
robustCorridor_action_safe
```

Every corridor state has an allowed enabled action whose concrete successors
remain in the robust corridor.

### ODT0 License Supply

```text
robustCorridor_supplies_license
```

Given:

```text
x in RobustCorridor
a certified justification route
the quotient side condition
```

there exists an allowed action that satisfies the ODT0 license certificate
against the robust corridor.

This theorem does not say the action is optimal or morally right. It says the
G2 corridor obligation can be discharged by the robust corridor certificate.

### Exit Exclusion

```text
action_with_exit_not_corridorSafe
action_with_exit_not_licensed
```

If an action has any concrete successor outside the robust corridor, then it
cannot be corridor-safe, and therefore cannot be licensed against that corridor.

This is the formal "no guarantee-destroying exit" wrapper for ODT0.

## Tiny Example

The example has:

```text
states:  good, bad
actions: stay, fall
constraint: only good is constrained-safe
requirement: trivial
```

Results:

```text
good_in_corridor
bad_not_in_corridor
stay_can_be_licensed
fall_cannot_be_licensed
```

Interpretation:

```text
stay:
  allowed, enabled, and keeps the state in the robust corridor.

fall:
  has a concrete successor outside the robust corridor, so it fails G2.
```

## Relationship To ODT0

ODT0 previously consumed an abstract `Corridor` predicate:

```text
LicenseVia D Corridor Available quotientOK x a
```

This pass supplies one canonical corridor candidate:

```text
Corridor := RobustCorridor D Allowed Requirement
```

Then ODT0's G2 becomes a direct fixed-point consequence:

```text
license -> all successors remain in RobustCorridor
```

and the reverse constructive direction becomes:

```text
x in RobustCorridor
plus certified route
plus quotient side condition
-> some allowed action can be licensed.
```

## What Remains Open

### Requirement Adequacy

`Requirement` is explicit. The theorem does not decide:

```text
why this Requirement?
why is it value-relevant?
why should it be protected?
does it survive sound presentations?
```

Those are Phi-adequacy and protected-continuation questions.

### Abstraction Reflection

The corridor is concrete. The next abstraction theorem should say when abstract
robust-kernel membership reflects to exact robust-kernel membership.

Expected obligations:

```text
requirement reflection
action realizability
successor over-approximation or implementation reflection
policy-class compatibility
```

### Stochastic Corridor

This pass is possibilistic and worst-case. A stochastic version needs an
explicit risk criterion or ambiguity-set semantics. That belongs after the
deterministic corridor and abstraction-reflection theorem are stable.

### Full Gradient Ethics Bridge

The formal shape now exists:

```text
certified Requirement
controlled dynamics
-> RobustCorridor
-> containment and exit exclusion
-> ODT0 license gate
```

The remaining semantic burden is not hidden:

```text
Requirement adequacy
reflexive/constitutive instantiation, if agency is discussed
protected plurality and joint compatibility, if Gradient Ethics is discussed
```

## Non-Claims

This pass does not claim:

```text
value
agency
identity
selfhood
valuerhood
moral standing
Omega
optimality
complete decision theory
empirical model validity
probabilistic risk handling
```

It is a controlled fixed-point corridor and an ODT0 bridge.

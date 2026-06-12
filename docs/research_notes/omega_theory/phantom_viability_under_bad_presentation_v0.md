# Phantom Viability Under Bad Presentation v0

Status: foundational counterexample note

This note records the viability-side negative control:

```text
a bad presentation can fabricate apparent viability
```

This does not define value, agency, identity, alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/PhantomViability.lean
```

## Exact System

The exact system has one state:

```text
x
```

It is declared safe, but it has no outgoing transition.

Since viability is the greatest fixed point of:

```text
safe x and exists y, Next x y and p y
```

the exact state is not viable. There is no sustaining successor.

Lean proves:

```text
exact_x_not_viable
```

## Abstract System

The abstract system has one state:

```text
qx
```

It is declared safe and has a self-loop:

```text
qx -> qx
```

So the abstract state is viable.

Lean proves:

```text
abstract_qx_viable
```

## Failed Reflection Contract

The presentation maps:

```text
x -> qx
```

The abstract self-loop has no exact step witness. Therefore the presentation
fails the step-reflection contract:

```text
not_stepReflects
```

and therefore fails the packaged viability-reflection contract:

```text
not_viabilityReflectingPresentation
```

## Main Theorem

Lean proves:

```text
bad_presentation_fabricates_phantom_viability
```

which packages:

```text
not Viable exact x
Viable abstract (present x)
not ViabilityReflectingPresentation
```

## Interpretation

The theorem says that abstract viability can be fabricated by adding sustaining
structure that has no exact witness.

This is the viability-side anti-Goodhart point:

```text
apparent viability must be computed over presentations that reflect sustaining
transitions and safety claims
```

Otherwise a coarse or bad model can report a viable corridor that does not
exist exactly.

## Claim Boundary

This does not say all abstractions are bad.

It says that viability claims need a reflection contract. Without one,
abstract viable continuation can be a modeling artifact.

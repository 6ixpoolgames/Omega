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
exact_x_no_safePrefix_one
exact_x_not_arbitrarilyLongSafePrefixes
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
abstract_qx_arbitrarilyLongSafePrefixes
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
bad_presentation_fabricates_arbitrarily_long_safe_prefixes
```

which packages:

```text
not Viable exact x
Viable abstract (present x)
not ViabilityReflectingPresentation
```

The operational safe-prefix version packages:

```text
not ArbitrarilyLongSafePrefixes exact x
ArbitrarilyLongSafePrefixes abstract (present x)
not ViabilityReflectingPresentation
```

The exact negative is proved directly: the exact state has no one-step safe
prefix because it has no outgoing transition.

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

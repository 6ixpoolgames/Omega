# Interface Sharpness Non-Factorization v0

Status: theorem note

This note records a finite anti-reduction witness for the
holographic/interface discipline:

```text
same sharp two-output interface profile
different declared input-distinction recovery
```

## Lean Location

```text
formal/lean/OmegaProper/BaselineWitnesses/InterfaceSharpnessDeclaredRecovery.lean
```

## Setup

Use the shared four-point carrier:

```text
X2 = first bit x second bit
```

Two deterministic binary interfaces are compared:

```text
emitDeclaredFirst:
  output preserves the declared first coordinate

emitNuisanceSecond:
  output preserves the nuisance second coordinate
```

Both interfaces look equally sharp to the coarse summary:

```text
input count: 4
output count: 2
zero-output fiber: 2
one-output fiber: 2
```

But only `emitDeclaredFirst` recovers the declared first input distinction.

## Theorem

Lean proves:

```text
sharpInterfaceSummary_declaredRecovery_nonFactorization
```

and the expanded witness:

```text
same_sharp_interface_different_declared_recovery
```

In words:

```text
a structured or sharpened output profile does not determine whether the
declared input distinction survived the interface
```

## Interpretation

This is a small formal shadow of the holographic interface idea.

An outside profile can be stable and structured while still failing to preserve
the declared distinction we care about. Therefore a deformer/channel/interface
cannot be trusted merely because its output is sharp, compressed, or apparently
organized.

The recovery target must be declared and checked.

## Claim Boundary

This does not define:

```text
deformers
singularities
agency
identity
value
Omega
```

It is only a finite non-factorization witness:

```text
coarse interface sharpness does not determine declared recovery.
```

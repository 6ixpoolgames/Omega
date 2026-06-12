# Predicate Fixed Points v0

Status: foundational theorem note

This note records the first fixed-point layer for trajectory work.

The purpose is narrow:

```text
define least and greatest fixed points for monotone predicate transformers
```

This does not yet define dynamics, reachability, viability, value, agency,
identity, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/PredicateFixpoint.lean
```

## Core Definitions

Predicate inclusion:

```text
PSub p q := forall x, p x -> q x
```

Monotone predicate transformer:

```text
Mono F := p <= q -> F p <= F q
```

Prefixed point:

```text
Prefixed F p := F p <= p
```

Postfixed point:

```text
Postfixed F p := p <= F p
```

Least fixed-point candidate:

```text
lfp F x := x belongs to every prefixed point
```

Greatest fixed-point candidate:

```text
gfp F x := x belongs to some postfixed point
```

## Core Theorems

`lfp` is below every prefixed point:

```text
lfp_le_prefixed
```

Every postfixed point is below `gfp`:

```text
postfixed_le_gfp
```

For monotone `F`, `lfp F` is a fixed point:

```text
F_lfp_le_lfp
lfp_le_F_lfp
lfp_fixed
```

For monotone `F`, `gfp F` is a fixed point:

```text
gfp_le_F_gfp
F_gfp_le_gfp
gfp_fixed
```

## Why This Matters

This is the algebraic base for the reachability/viability bridge.

Later modules can define:

```text
Reach target := lfp reachOp
Viability safe := gfp safeStepOp
```

without re-proving the fixed-point calculus.

## Claim Boundary

This note does not claim anything about value, agency, alignment, irreversible
loss, or Omega.

It only proves fixed-point facts for monotone predicate transformers.

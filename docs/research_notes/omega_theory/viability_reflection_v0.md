# Viability Reflection v0

Status: foundational theorem note

This note records the viability-side counterpart to reachability reflection.

The core statement is:

```text
if an abstract presentation reflects safety and steps back to the exact
system, then abstract viability implies exact viability
```

This does not define value, agency, identity, alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/ViabilityReflection.lean
```

## Problem

Reachability asks whether a target can eventually be reached.

Viability asks whether a state can keep continuing while satisfying a declared
safety predicate.

After `ReachabilityReflection.lean`, the next question is:

```text
what contract prevents an abstraction from fabricating viable continuation?
```

## Reflection Contracts

The file reuses:

```text
StepReflects
```

from `ReachabilityReflection.lean`.

It adds:

```text
SafeReflects
```

meaning abstract safety membership of `present x` implies exact safety
membership of `x`.

In symbols:

```text
safeQ (present x) -> safeX x
```

## Main Theorem

Lean proves:

```text
abstractViable_reflects_exactViable
abstractViable_reflects_exactSafePrefixes
```

If a presentation reflects safety and steps, then:

```text
Viable DQ safeQ (present x)
  -> Viable DX safeX x
```

Using the safe-prefix semantics for `Viable`, Lean also proves:

```text
Viable DQ safeQ (present x)
  -> ArbitrarilyLongSafePrefixes DX safeX x
```

There is also an unpackaged version:

```text
abstractViable_reflects_exactViable_of_reflects
abstractViable_reflects_exactSafePrefixes_of_reflects
```

## Interpretation

This is the dynamics-side abstraction contract for viability claims.

It says:

```text
no invented safety + no invented sustaining transitions = no invented viability
no invented safety + no invented sustaining transitions = no invented
arbitrarily long exact safe prefixes
```

The proof uses the greatest-fixed-point definition directly: an abstract
postfixed viability predicate pulls back to an exact postfixed viability
predicate when safety and steps reflect.

## Claim Boundary

This theorem does not say viability is value or alignment.

It only proves that the declared reflection contract is sufficient to prevent
abstract viability from overstating exact viability.

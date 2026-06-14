# Boundary-Invariant Continuation Roadmap v0

Status: near-term roadmap note

This note records the current bridge from the checked consequence/presentation
stack toward the larger Gradient Ethics and Omega ambition.

## Core Shift

The next bridge should not be recoverable identity. The next bridge should be
boundary-invariant continuation.

The reason is direct:

```text
if value requires valuers,
and valuers cannot be assumed as primitive bounded objects,
then the carrier of value-relevant structure must survive admissible
presentation / boundary / quotient choices.
```

So the guiding question becomes:

```text
Which continuation facts survive sound presentations?
```

This reframes the existing stack as the beginning of a boundary-invariance
discipline.

## Current Formal Base

Already-landed layers include:

```text
sound quotient:
  proposed identifications must be contained in consequence-identifiability

presentation invariance:
  sound presentations cannot erase merge-separated consequence structure

non-factorization:
  summaries that stay fixed while targets change cannot determine those targets

reachability / viability:
  continuation constraints are fixed-point objects

reflection contracts:
  safe abstraction must reflect relevant target, step, reach, and viability
  structure

phantom and hidden-loss examples:
  unsound presentations can fabricate continuation or hide exact loss

loss-aware contracts:
  stronger contracts make loss visibility explicit
```

These are not separate side quests. Together they are the first formal layer of
boundary-invariant continuation structure.

## Immediate Theorem Targets

### 1. Joint viability

Current theorem:

```text
marginal viability for each of two safety predicates
does not imply joint viability for their conjunction
```

Lean:

```text
formal/lean/OmegaProper/Trajectory/JointViability.lean
```

Roadmap role:

```text
individual corridors are not enough;
the alignment-relevant object is compatible continuation.
```

### 2. Hidden joint-viability loss

Target:

```text
a state can leave the jointly viable corridor while remaining viable for one
marginal constraint, and a bad presentation can hide that exact joint loss
```

Roadmap role:

```text
bad abstraction can make a corridor look preserved while joint compatibility
has already failed.
```

### 3. Viable trajectory language

Target:

```text
finite path languages inside viability kernels
```

Roadmap role:

```text
reachability says a target is eventually accessible;
viable trajectory language records the distinguishable continuations that
remain possible inside the corridor.
```

### 4. Lushness candidate

Target:

```text
horizon-indexed count or growth of distinguishable viable continuations
```

Claim boundary:

```text
not value;
not moral worth;
not raw complexity;
not a final Omega metric.
```

Roadmap role:

```text
first technical handle on "rich compatible futures" after compatibility and
sound-presentation constraints are in place.
```

## Gradient Ethics Correction

The Gradient Ethics bridge should not be:

```text
preserve reachability of a bounded agent S
```

unless `S` is explicitly treated as a presentation whose boundary assumptions
are audited.

The safer target is:

```text
preserve boundary-invariant jointly viable continuation under uncertainty and
irreversibility
```

This keeps the option-value / viability insight while avoiding primitive
self-boundary realism.

## Omega Target

Omega should remain downstream.

Near-term wording:

```text
Omega is the target of a boundary-invariant, jointly compatible,
viability-preserving continuation theory.
```

Not yet claimed:

```text
valuer detection
agency detection
identity recovery
terminal coalgebra Omega
complete value theory
```

## Near-Term Sprint

Concrete order:

```text
1. keep joint viability as the first compatibility theorem
2. add hidden joint-viability loss under bad presentation
3. define viable trajectory language v0
4. test simple path-count / lushness candidates
5. add unsound-presentation inflation counterexamples before trusting any
   richness measure
```

The governing rule remains:

```text
every positive measure needs a negative control.
```

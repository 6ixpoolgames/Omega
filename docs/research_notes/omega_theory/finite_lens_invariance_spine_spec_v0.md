# Finite Lens Invariance Spine Spec v0

Status: theorem-spine specification / bounded-fragment debt
Scope: finite transition systems, functional lenses, and preservation/reflection for the bounded fact grammar currently used by the repo
Claim boundary: not full modal mu-calculus, not Janin-Walukiewicz recovery, not global presentation invariance, not value, not agency, not identity, not moral standing, not Omega validation

## Purpose

Several recent branches now point at the same missing theorem:

```text
closure attribution / guard rows;
colonization certified-chain transport;
adaptive observation / corridor transport;
future presentation-sound compensation claims.
```

The shared debt is not another witness. It is a finite lens-invariance spine:
when a presentation is a sound lens, the bounded fact language used by the
repo should preserve and reflect truth along that lens.

This note scopes the theorem before Lean work begins.

## Lens Interface

For finite systems `S` and `T`, a lens is a surjective map:

```text
q : S.State -> T.State
```

with two clauses:

```text
forward:
  concrete steps map to abstract steps.

zig-zag / back:
  every abstract step out of an image state lifts to a concrete step.
```

Reading:

```text
forward blocks hidden-loss / erasure failures;
zig-zag blocks fabricated abstract behavior.
```

The theorem should use this single interface rather than a growing family of
one-off reflection contracts.

## Bounded Fact Grammar

v0 should not attempt the full modal mu-calculus. The target grammar is the
bounded fragment already used by current claims:

```text
atoms:
  declared state predicates that respect q.

boolean:
  and / or.

modal:
  diamond step;
  box step.

named finite fixpoints:
  Reach as least fixed point;
  Viab / corridor as greatest fixed point.
```

This is enough for current reachability, viability, safe-prefix, adaptive
kernel, and process-coherence guard uses.

## Target Theorem

For every formula `phi` in the bounded grammar:

```text
T |= phi at q(s)
iff
S |= phi at s
```

under the lens clauses and atom-respect hypotheses.

Proof route:

```text
structural induction for atoms, boolean, and modal cases;
finite iteration for the named least/greatest fixed points.
```

## Consumers

The theorem should discharge or sharply reduce:

```text
closure guard attribution:
  finite rule-backed rows become theorem instances rather than enumeration
  coincidences.

colonization:
  certified chains get a real lens-invariance check instead of the current
  registered-chain finite audit caveat.

adaptive observation:
  observation-garbling and lifted-system transports reuse the same spine.

compensation:
  certified compensation claims require reflection through recovery/coupling
  frames; the lens theorem gives the generic preservation pattern.
```

## Nonclaims

This spec does not claim:

```text
that all meaningful facts are in the grammar;
that all presentations are lenses;
that colonization is globally presentation-invariant;
that compensation, value, standing, agency, identity, or Omega is derived.
```

## Public Compression

The finite lens theorem should say, once and for all: if a presentation is a
true step-preserving and step-reflecting lens, then the bounded reach/viability
fact language used by Omega survives transport through that presentation.

# Phantom Reachability Under Unsound Quotient v0

Status: foundational counterexample note

This note records a small finite theorem:

```text
an unsound presentation can fabricate apparent reachability
```

The theorem is intentionally narrow. It does not define value, agency,
alignment, identity, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/PhantomReachability.lean
```

## Exact System

The exact transition system has four states:

```text
a, b, c, d
```

with only two edges:

```text
a -> b
c -> d
```

There is no bridge from `b` to `c`, so `d` is not reachable from `a`.

Lean proves this by exhibiting a prefixed barrier:

```text
exactReachBarrier := {c, d}
```

Since `a` is outside that prefixed set, `a` is not in the least fixed-point
reachability set for target `d`.

## Unsound Presentation

The presentation maps:

```text
a -> qa
b -> qm
c -> qm
d -> qd
```

It merges `b` and `c`.

The induced abstract dynamics have:

```text
qa -> qm
qm -> qd
```

So the abstract system appears to reach `qd` from `qa`.

## Why The Merge Is Unsound

The file defines a one-context consequence system that separates exact states
by identity. Under that consequence system, `b` and `c` are merge-separated.

Because the presentation identifies `b` and `c`, Lean proves:

```text
mergePresentation_not_sound
```

using the existing sound quotient guardrail.

## Main Theorem

Lean proves:

```text
unsound_merge_fabricates_phantom_reachability
```

which packages:

```text
not Reach exact a d
Reach abstract qa qd
not SoundQuotient identityConsequenceSystem mergePresentation
```

## Interpretation

The theorem says that an abstraction can create a continuation path that was
not present in the exact system if it merges consequence-separated states.

This is the anti-Goodhart point for reachability:

```text
apparent continuation preservation must be computed over sound presentations
```

Otherwise a coarse model can hide real obstructions or fabricate apparent
paths.

## Claim Boundary

This does not say all quotients are bad.

It says that quotient/presentation soundness is not optional when making
reachability claims.

Future work can ask when sound presentations preserve reachability, when
unsound presentations hide loss, and how this interacts with viability
kernels.

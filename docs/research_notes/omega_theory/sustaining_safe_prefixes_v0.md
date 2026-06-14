# Sustaining Safe Prefixes v0

Status: foundational theorem note

This note connects sustaining/recurrent viable classes to the operational
safe-prefix semantics introduced in `TrajectorySemantics`.

The key point is constructive:

```text
sustaining class membership -> viability -> arbitrarily long finite safe
prefixes
```

This does not prove the compactness converse:

```text
arbitrarily long finite safe prefixes -> viability
```

That converse requires additional finite-branching, compactness, or choice-like
assumptions and remains out of scope.

This is not a value, agency, identity, alignment, or Omega claim.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/SustainingSafePrefixes.lean
```

## Core Theorems

Lean proves:

```text
sustainingClass_member_safePrefixes
closedSustainingClass_member_safePrefixes
recurrentClass_member_safePrefixes
```

So any member of a sustaining viable class, closed sustaining viable class, or
recurrent viable class supplies safe prefixes of every finite transition
length.

## Tiny Finite Witnesses

The file reuses the existing loop and two-state cycle witnesses:

```text
loopClass_member_safePrefixes
cycle_left_safePrefixes
cycle_right_safePrefixes
recurrent_cycle_left_safePrefixes
recurrent_cycle_right_safePrefixes
recurrent_cycle_supplies_safePrefixes
```

The recurrent cycle theorem packages:

```text
the cycle class is recurrent viable
the left state has arbitrarily long finite safe prefixes
the right state has arbitrarily long finite safe prefixes
```

## Interpretation

This is the lighter bridge before any Koenig-style compactness theorem. It says:

```text
if we already have a constructive sustaining/recurrent witness, then the
operational safe-prefix account follows immediately
```

It does not attempt to recover a coherent infinite trajectory from merely
having finite safe prefixes of every length.

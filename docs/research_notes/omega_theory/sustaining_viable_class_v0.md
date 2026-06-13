# Sustaining Viable Class v0

Status: foundational theorem note

This note records a modest identity-free persistence object:

```text
a safe class with an internal successor for every member witnesses viability
for every member
```

This does not define agency, identity, value, alignment, strong recurrence, or
Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/SustainingViableClass.lean
```

## Why Not Call It Recurrence Yet?

The current formal object is intentionally modest.

It proves sustaining continuation:

```text
every class member has some successor inside the class
```

That is enough to witness viability.

It does not yet prove strong graph-theoretic recurrence, strong connectivity,
cycle decomposition, or finite pigeonhole recurrence.

## Core Definitions

```text
ClassSafe safe C
```

means every member of `C` satisfies `safe`.

```text
ClassClosed D C
```

means every outgoing transition from a member of `C` stays inside `C`.

```text
ClassHasSuccessorIn D C
```

means every member of `C` has at least one successor inside `C`.

```text
SustainingViableClass D safe C
```

means `C` is safe and has an internal successor for every member.

```text
ClosedSustainingViableClass D safe C
```

adds closure.

## Main Theorem

Lean proves:

```text
sustainingClass_member_viable
```

If `C` is a sustaining viable class and `x` is in `C`, then:

```text
Viable D safe x
```

The proof uses `C` itself as a postfixed point for the viability operator.

The file also proves:

```text
closedSustainingClass_member_viable
```

for the stronger closed-class package.

## Finite Witnesses

The file includes:

```text
loop -> loop
```

as a one-state sustaining class, and:

```text
left -> right
right -> left
```

as a two-state cyclic sustaining class.

## Interpretation

This is the first safe predecessor to recurrence/vortex language:

```text
not "the same object persists"
but "there is a safe class of states with internal sustaining continuation"
```

Later work can strengthen this toward recurrent classes, carried distinctions,
support/extent, or agency-like structure. Those are not claimed here.

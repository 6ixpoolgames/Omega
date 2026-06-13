# Recurrent Viable Class v0

Status: foundational theorem note

This note records a stronger finite-graph persistence object:

```text
a safe closed class with internal paths between members and an internal
successor for every member
```

This does not define agency, identity, consciousness, value, alignment, or
Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/RecurrentViableClass.lean
```

## Relationship To Earlier Layers

`SustainingViableClass.lean` proved:

```text
safe class + internal successor for every member
-> every member is viable
```

`CarriedDistinction.lean` proved:

```text
a sustaining class can carry an internal consequence distinction
without being a valid quotient class
```

This file strengthens the class shape by adding internal paths and strong
connectivity.

## Core Definitions

```text
InternalPath D C x y
```

is a path from `x` to `y` whose immediate steps stay inside `C`.

```text
ClassStronglyConnected D C
```

means any two class members have an internal path between them.

```text
RecurrentViableClass D safe C
```

means:

```text
ClassSafe safe C
ClassClosed D C
ClassStronglyConnected D C
ClassHasSuccessorIn D C
```

## Core Theorems

Lean proves:

```text
recurrent_implies_closedSustaining
recurrent_implies_sustaining
recurrentClass_member_viable
```

So recurrent viable class membership witnesses viability.

The file also proves internal-path endpoint facts:

```text
internalPath_start_mem
internalPath_end_mem
```

## Finite Witness

The file reuses the two-state cycle:

```text
left -> right
right -> left
```

with both states safe and both inside the class.

Lean proves:

```text
cycleClass_recurrent
recurrent_cycle_left_viable
recurrent_cycle_right_viable
```

It also connects to carried distinctions:

```text
recurrent_cycle_carries_distinction
```

which packages:

```text
the cycle class is recurrent viable
the class carries an internal consequence-separated pair
the class is not a consequence-respecting merge class
```

## Interpretation

This is the next safe predecessor to old vortex language:

```text
not "an identical object persists"
but "there is a closed, internally connected, viable region that carries
consequence structure"
```

Later work can ask whether such regions compose, interfere, recur under
presentation changes, or carry recoverable distinctions over longer dynamics.
Those are future claims, not claims of this file.

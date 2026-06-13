# Support Minimality v0

Status: foundational theorem note

This note defines minimal support for a fixed consequence-separated pair.

Minimality is pair-relative:

```text
a support is minimal for x,y when every sub-support that still supports x,y
must contain the original support
```

This is not a global boundary, object, identity, agency, value, alignment, or
Omega claim.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/SupportMinimality.lean
```

## Core Definitions

```text
MinimalSupportForSeparatedPair S Next C x y
```

means `C` supports the directional separated pair `x,y`, and no proper
sub-support of `C` still supports that same pair.

```text
MinimalSupportForMergeSeparatedPair S Next C x y
```

is the merge-blocking analogue.

## Core Theorems

Lean proves:

```text
minimalSupport_supports
minimalMergeSupport_supports
minimalSupport_no_proper_support_sub
minimalMergeSupport_no_proper_support_sub
```

The negative theorem is the useful guardrail:

```text
if C is minimal for x,y, no proper sub-support of C can still support x,y
```

## Finite Witness

For the two-state recurrent cycle:

```text
left -> right
right -> left
```

the full cycle class is minimal for supporting the left/right consequence
distinction. Lean proves:

```text
cycleClass_minimal_support_left_right
cycleClass_no_proper_support_sub_left_right
```

The reason is intentionally simple: any support for the fixed pair must contain
both `left` and `right`, and the full cycle contains only those two states.

## Interpretation

Minimal support is not identity. It is not a recovered object. It is a
pair-relative extent check:

```text
how much of this declared region is required to carry this declared
distinction?
```

That makes it a safer stepping stone toward later extent or boundary questions.

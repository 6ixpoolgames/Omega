# Support Restriction v0

Status: foundational theorem note

This note records a small guardrail for distinction supports:

```text
restriction can destroy support
```

A support for a fixed separated pair must contain both endpoints of that pair.
If a restricted class drops either endpoint, it no longer supports that exact
pair.

This is not a boundary, identity, agency, value, alignment, or Omega claim.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/SupportRestriction.lean
```

## Core Theorems

Lean proves endpoint requirements:

```text
support_requires_left
support_requires_right
mergeSupport_requires_left
mergeSupport_requires_right
```

and the corresponding restriction failures:

```text
not_supports_if_left_missing
not_supports_if_right_missing
not_mergeSupports_if_left_missing
not_mergeSupports_if_right_missing
```

## Finite Witness

The two-state recurrent cycle:

```text
left -> right
right -> left
```

supports the left/right consequence distinction when the support class contains
both states.

The file then defines:

```text
leftOnlyClass
```

which keeps only `left`. Lean proves:

```text
leftOnly_proper_sub_cycleClass
leftOnly_not_supports_left_right
restriction_can_destroy_support
```

So a proper restriction of a support can destroy support for the declared pair.

## Interpretation

Support is not just any subset near a distinction. It is pair-relative and
endpoint-sensitive. This blocks a common shortcut:

```text
the smaller region still looks related, so it must still support the same
distinction
```

That does not follow. If the restricted region drops a required endpoint, the
support claim fails.

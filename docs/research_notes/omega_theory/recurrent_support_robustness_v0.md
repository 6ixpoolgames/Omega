# Recurrent Support Robustness v0

Status: formal recurrent-support guardrail
Scope: recurrent viable supports carrying merge-separated consequence pairs
Claim boundary: not identity, not agency, not deformer theory, not Omega validation

This note records the recurrent version of support integrity.

The Lean file is:

```text
../../../formal/lean/OmegaProper/Trajectory/RecurrentSupportRobustness.lean
```

## Core Idea

`SupportUnderPerturbation` says a changed support predicate preserves a carried
pair only if the changed support still carries the pair.

`RecurrentSupportRobustness` strengthens this to recurrence:

```text
the class must still be recurrent/viable,
still contain both endpoints,
still internally connect them in both directions,
and still expose the merge-separated consequence pair.
```

This is the identity-free version of robustness. We do not ask whether "the
same object" persisted. We ask whether the changed dynamics/support still
recurrently carries the declared consequence distinction.

## Core Definitions

`RecurrentSupportCarries S Next safe C x y` means:

```text
RecurrentViableClass (dynFromNext Next) safe C
and
SupportsMergeSeparatedPair S Next C x y
```

`RecurrentSupportIntegrityUnder` says recurrent carrying transfers from an
original dynamics/support to a changed dynamics/support.

`RecurrentSupportDestroyedUnder` says the original recurrent support carries
the pair but the changed one does not.

## Guardrails

Lean proves that recurrent support carrying fails if:

```text
the changed support drops x
the changed support drops y
the changed dynamics/support lacks an internal path x -> y
the changed dynamics/support lacks an internal path y -> x
```

The theorem names are:

```text
not_recurrentSupportCarries_if_left_missing
not_recurrentSupportCarries_if_right_missing
not_recurrentSupportCarries_if_forward_path_missing
not_recurrentSupportCarries_if_reverse_path_missing
```

It also proves support-destruction wrappers:

```text
recurrentSupportDestroyed_if_left_missing
recurrentSupportDestroyed_if_right_missing
recurrentSupportDestroyed_if_forward_path_missing
recurrentSupportDestroyed_if_reverse_path_missing
```

## Finite Witness

The existing two-state recurrent cycle carries the merge-separated pair
`left/right`:

```text
cycle_recurrentSupportCarries_left_right
```

The same recurrent support preserves recurrent integrity:

```text
cycle_sameSupport_preserves_recurrent_integrity
```

The left-only support destroys recurrent support for the pair because it drops
the right endpoint:

```text
cycle_leftOnly_destroys_recurrent_support
```

## Why This Matters

This is the first layer that makes robustness depend on dynamics, not just
membership. A support can contain relevant states and still fail to recurrently
carry a distinction if the internal paths break.

That is the safe formal predecessor to stronger perturbation or vortex
language:

```text
preserved recurrently carried distinction,
not persistent object identity.
```

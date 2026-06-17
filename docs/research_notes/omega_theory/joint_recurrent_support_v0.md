# Joint Recurrent Support v0

Status: finite negative witness
Scope: individual recurrent carrying versus shared joint carrying
Claim boundary: not agency, not identity, not value, not alignment, not Omega validation

## Purpose

This note records the first joint recurrent-support guardrail:

```text
formal/lean/OmegaProper/Trajectory/JointRecurrentSupport.lean
```

The theorem is deliberately small:

```text
two supports can each recurrently carry their own consequence distinction
under separate safety predicates, while no recurrent support carries any
distinction under the shared joint safety predicate.
```

This is the recurrent-support analogue of the existing joint-viability
guardrail. Individual viability or carrying is not the same as compatible joint
viability or compatible joint carrying.

## The finite witness

The witness has two disjoint recurrent cycles:

```text
aLeft  -> aRight
aRight -> aLeft

bLeft  -> bRight
bRight -> bLeft
```

The `A` safety predicate accepts only the `a` cycle.
The `B` safety predicate accepts only the `b` cycle.

So:

```text
supportA recurrently carries aLeft/aRight under safeA;
supportB recurrently carries bLeft/bRight under safeB;
JointSafe safeA safeB has no safe state;
therefore no recurrent support can carry any distinction under joint safety.
```

## Main Lean names

```text
supportA_recurrently_carries
supportB_recurrently_carries
no_jointSafe_state
no_recurrentSupportCarries_under_jointSafety
individual_carrying_does_not_imply_joint_carrying
```

The recurrent-support facade exposes:

```text
RecurrentSupportIntegrity.individual_vs_joint_recurrent_support_witness
```

## What this proves

The exact current claim is:

```text
Individual recurrent carrying under separate declared constraints does not
automatically compose into recurrent carrying under their shared joint
constraint.
```

This is a local finite fact. It does not yet define a general compatibility
calculus for many supports.

## Why it matters

The larger project cares about compatible continuation, not just isolated
survival. This witness marks the first recurrent-support version of that
discipline:

```text
separate supports can each look healthy in isolation;
the shared corridor can still be empty.
```

That is a useful bridge toward later joint viability, Gradient Ethics, and
alignment-facing corridor claims, while keeping the current claim finite and
identity-free.

## Related notes

- [layer_a_theorem_spine_v0.md](layer_a_theorem_spine_v0.md)
- [joint_viability_v0.md](joint_viability_v0.md)
- [hidden_joint_viability_loss_under_bad_presentation_v0.md](hidden_joint_viability_loss_under_bad_presentation_v0.md)
- [recurrent_support_integrity_v0.md](recurrent_support_integrity_v0.md)

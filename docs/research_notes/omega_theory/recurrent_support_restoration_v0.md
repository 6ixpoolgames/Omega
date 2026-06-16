# Recurrent Support Restoration v0

Status: finite restoration witness
Scope: recurrent support carrying after explicit loss and repair
Claim boundary: not identity, not agency, not deformer theory, not Omega validation

This note completes the local recurrent-support perturbation story:

```text
full cycle:
  recurrently carries a merge-separated consequence pair

one-way broken cycle:
  endpoints remain supported and viable,
  but the reverse internal path is lost,
  so recurrent carrying is destroyed

repaired cycle:
  the two-way cycle is restored,
  so recurrent carrying is restored
```

The Lean file is:

```text
../../../formal/lean/OmegaProper/Trajectory/RecurrentSupportRestoration.lean
```

## Core Definition

`RecurrentSupportRestoredAfterLoss` packages:

```text
RecurrentSupportDestroyedUnder S Next0 NextLoss ...
and
RecurrentSupportCarries S NextRestored ...
```

This is deliberately pair-relative and support-relative. It does not say that
an object, agent, self, or deformer was restored.

## General Theorem

Lean proves:

```text
recurrentSupportRestored_of_loss_and_repairContract
```

Informally:

```text
if recurrent carrying is lost under one changed dynamics,
and a later changed dynamics satisfies the transfer contract from the original
support,
then recurrent carrying is restored.
```

The repair contract is the same contract introduced in
`RecurrentSupportTransfer`:

```text
safety transfers on the support
no new exits from the support
old internal support edges remain available
```

## Finite Witness

The file defines:

```text
repairedCycleNext := cycleNext
```

Then Lean proves:

```text
repairedCycle_transfer_contract_from_baseline
repaired_right_path_left
repaired_recurrentSupportCarries_left_right
broken_not_transfer_contract_from_baseline
cycle_recurrentSupport_restored_after_broken_loss
recurrent_support_loss_and_restoration_witness
```

The `broken_not_transfer_contract_from_baseline` theorem is important. It
shows the broken one-way dynamics fails the repair/preservation contract
because it does not preserve the old internal edge:

```text
right -> left
```

So the local picture is now:

```text
preservation contract holds:
  recurrent carrying transfers

broken one-way dynamics:
  preservation contract fails
  recurrent carrying is lost

repaired two-way dynamics:
  preservation contract holds again
  recurrent carrying is restored
```

## Why This Matters

This gives a precise alternative to identity language.

We do not say:

```text
the same thing survived, died, and came back
```

We say:

```text
the declared recurrent support carried the consequence pair;
the broken dynamics stopped carrying it;
the repaired dynamics carried it again.
```

That is the shape needed for later perturbation, repair, and alignment-facing
claims without smuggling object identity back into the lower theory.

## Next Step

The natural next strengthening is parameterization:

```text
finite n-cycle carries a distinction through recurrence;
removing a required return edge destroys carrying;
restoring the edge restores carrying.
```

That would move this from a two-state witness to a finite-family theorem.

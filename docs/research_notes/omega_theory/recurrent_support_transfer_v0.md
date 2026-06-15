# Recurrent Support Transfer v0

Status: formal positive-transfer contract
Scope: same-support recurrent carrying under changed dynamics and safety
Claim boundary: not identity, not agency, not deformer theory, not Omega validation

This note records the positive counterpart to recurrent support loss.

The Lean file is:

```text
../../../formal/lean/OmegaProper/Trajectory/RecurrentSupportTransfer.lean
```

## Core Question

The loss theorem says a one-way dynamic change can destroy recurrent carrying
even when endpoints remain viable and forward reachability remains.

The transfer theorem asks:

```text
what contract is sufficient to preserve recurrent carrying?
```

The current answer is deliberately narrow:

```text
same declared support,
changed dynamics,
changed safety predicate.
```

No object identity is claimed. The theorem only says the changed
dynamics/support still recurrently carries the declared consequence pair.

## Contract

`RecurrentSupportTransferContract Next0 Next1 safe0 safe1 C` contains three
obligations:

```text
SafeTransfersOn C safe0 safe1:
  states in C that were safe before remain safe after

NoNewExitsFrom Next1 C:
  changed dynamics has no outgoing exits from C

InternalEdgesPreservedOn Next0 Next1 C:
  every old internal C-edge remains available after the change
```

Together, these are enough to transfer recurrence and path-carried merge
separation.

## Main Theorems

Lean proves:

```text
internalPathTransferOfEdges
internalPath_transfer_of_edges
recurrentViableClass_transfer_of_contract
supportsMergeSeparatedPair_transfer_of_edges
recurrentSupportCarries_transfers_of_contract
recurrentSupportIntegrity_of_contract
```

The main theorem is:

```text
if recurrent support carries a merge-separated pair before the change,
and the transfer contract holds,
then recurrent support carries the same pair after the change.
```

## Finite Witness

The existing two-state cycle satisfies the transfer contract from itself to
itself:

```text
cycle_self_transfer_contract
cycle_self_transfer_preserves_recurrent_support
cycle_self_transfer_integrity
```

This witness is intentionally small. Its job is only to check that the
positive contract composes with the existing recurrent-support stack.

## Relation To The Loss Theorem

`IrreversibleRecurrentSupportLoss` breaks the reverse internal edge
`right -> left`. Therefore it cannot satisfy the internal-edge preservation
part of the transfer contract for the full two-state recurrent support.

This gives the current pair of results:

```text
positive:
  preserve internal support edges, safety, and no-exit closure -> recurrent
  carrying transfers

negative:
  break a required internal return path -> recurrent carrying can be lost even
  when endpoints remain viable
```

That is a clean perturbation discipline without introducing a persisting self,
boundary, or deformer object.

## Next Step

The natural next strengthening is a restoration witness:

```text
full cycle -> one-way broken cycle loses recurrent carrying
one-way broken cycle -> repaired cycle restores recurrent carrying
```

That would separate:

```text
loss detection
from
restoration under an explicit repair contract
```

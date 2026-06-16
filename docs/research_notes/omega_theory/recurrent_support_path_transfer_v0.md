# Recurrent Support Path Transfer v0

Status: formal path-level transfer relaxation
Scope: same-support recurrent carrying under rerouted internal paths
Claim boundary: not identity, not agency, not deformer theory, not Omega validation

This note records a weaker transfer contract than edge preservation.

The Lean file is:

```text
../../../formal/lean/OmegaProper/Trajectory/RecurrentSupportPathTransfer.lean
```

## Why This Exists

`RecurrentSupportTransfer` proved a strong sufficient condition:

```text
every old internal support edge remains available
```

That is clean, but too strict. A benign perturbation may remove an old edge and
replace it with an alternate internal path:

```text
old:
  right -> left

new:
  right -> mid -> left
```

The recurrent carrying should be allowed to transfer when the path structure is
preserved, even if the exact edge is not.

## Core Definitions

`InternalPathsPreservedOn Next0 Next1 C` says:

```text
every old internal path inside C is replaceable by a new internal path inside C
```

`InternalEdgesPathPreservedOn Next0 Next1 C` says:

```text
every old internal edge is replaceable by a new internal path
```

Lean proves:

```text
internalPathsPreserved_of_edgePathPreserved
internalPathsPreserved_of_edgesPreserved
```

So exact edge preservation implies path preservation, and edge-to-path
replacement is enough to preserve all old internal paths.

## Path-Level Contract

`RecurrentSupportPathTransferContract Next0 Next1 safe0 safe1 C` contains:

```text
SafeTransfersOn C safe0 safe1
NoNewExitsFrom Next1 C
InternalPathsPreservedOn Next0 Next1 C
SuccessorsAvailableOn Next1 C
```

The successor clause remains explicit because recurrence includes a one-step
sustaining condition. Path preservation alone does not guarantee that every
support member has an immediate successor in the changed dynamics.

## Main Theorems

Lean proves:

```text
recurrentViableClass_transfer_of_path_contract
supportsMergeSeparatedPair_transfer_of_paths
recurrentSupportCarries_transfers_of_path_contract
recurrentSupportIntegrity_of_path_contract
edgeTransferContract_implies_pathTransferContract
```

The main theorem says:

```text
if recurrent support carries a merge-separated pair before the change,
and the path-level transfer contract holds,
then recurrent support carries the same pair after the change.
```

## Rerouting Witness

The finite witness uses three states:

```text
left
mid
right
```

The baseline dynamics includes a direct return edge:

```text
right -> left
```

The rerouted dynamics removes that edge and replaces it:

```text
right -> mid -> left
```

Lean proves:

```text
rerouted_not_edgeTransfer_contract
rerouted_pathTransfer_contract
rerouted_preserves_recurrentSupport_by_path_contract
path_transfer_strictly_relaxes_edge_transfer_witness
```

The important audit sentence is:

```text
edge-level transfer fails,
but path-level transfer succeeds,
and recurrent support carrying is preserved.
```

## Why This Matters

This is a better perturbation robustness shape.

The earlier edge-level contract said:

```text
preserve the exact wiring
```

The path-level contract says:

```text
preserve the internal carried-connectivity, allowing rerouting
```

That is closer to what later support, repair, and alignment-facing claims will
need. It still avoids identity language:

```text
not the same object persisted;
the declared support still recurrently carries the consequence pair.
```

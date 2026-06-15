# Irreversible Recurrent Support Loss v0

Status: finite one-way dynamics witness
Scope: recurrent support loss with endpoints still supported and viable
Claim boundary: not physical irreversibility, not identity, not agency, not Omega validation

This note records the first small witness where recurrent support is destroyed
by a one-way dynamic change rather than by deleting an endpoint.

The Lean file is:

```text
../../../formal/lean/OmegaProper/Trajectory/IrreversibleRecurrentSupportLoss.lean
```

## Setup

The baseline system is the existing two-state cycle:

```text
left -> right
right -> left
```

The cycle support is recurrent, viable, and carries a merge-separated
consequence pair between `left` and `right`.

The changed system is:

```text
left -> right
right -> right
```

Both endpoints remain in the declared support. Both endpoints remain viable in
the changed dynamics. The one-way path `left -> right` remains.

What disappears is the reverse internal path:

```text
right -> left
```

## Main Witness

Lean proves:

```text
broken_left_viable
broken_right_viable
broken_left_path_right
broken_no_path_right_left
broken_not_supports_merge_left_right
broken_not_recurrentSupportCarries_left_right
broken_destroys_recurrent_support
irreversible_recurrent_support_loss_witness
```

The combined witness says:

```text
baseline recurrent support carries the merge-separated pair;
changed dynamics still keeps both endpoints viable;
changed dynamics still has the forward internal path;
changed dynamics lacks the reverse internal path;
therefore changed dynamics does not recurrently carry the pair.
```

## Technical Note

The file includes a small path-invariant helper:

```text
internalPath_preserves_stepInvariant
```

It proves that an internal path preserves any predicate preserved by each
internal step. Instantiating this with the predicate "is the right endpoint"
shows that, under the broken dynamics, a path starting at `right` can only end
at `right`.

## Why This Matters

This is the next rung toward the Gradient Ethics bridge.

The point is not:

```text
the same entity failed to persist
```

The point is:

```text
an irreversible one-way change can preserve endpoint viability and partial
reachability while destroying recurrent support for a consequence distinction.
```

That is the local finite form of a broader alignment-relevant concern:

```text
ordinary reachability can remain while the substrate's ability to carry a
declared consequence distinction through recurrence is lost.
```

The theorem is still small. It does not define value, agency, deformer
structure, or Omega. It gives the exact support/dynamics fact those later
claims would have to build on.

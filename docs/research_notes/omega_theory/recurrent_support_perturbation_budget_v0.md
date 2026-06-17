# Recurrent Support Perturbation Budget v0

Status: finite threshold witness
Scope: recurrent support carrying under exact dynamic perturbation
Claim boundary: not probability, not identity, not agency, not deformer theory, not value, not Omega validation

## Purpose

This note records the first exact perturbation-budget result for recurrently
carried consequence distinctions:

```text
formal/lean/OmegaProper/Trajectory/RecurrentSupportPerturbationBudget.lean
```

The result is intentionally small. It does not define a general graph cut,
minimum repair metric, stochastic survival probability, or identity of a
persisting object. It proves a finite threshold floor:

```text
zero dynamic change cannot destroy recurrent carrying;
one strategically placed return-edge removal can destroy recurrent carrying.
```

## The finite witness

The baseline support is the two-state recurrent cycle:

```text
left  -> right
right -> left
```

The class recurrently carries the declared `left/right` consequence
distinction because the support contains both endpoints, keeps the merge
separation visible, and has internal paths both ways.

The broken dynamics removes only the return edge:

```text
left  -> right
right -> right
```

In the broken system:

```text
left can still reach right;
both endpoints remain viable;
the forward internal path still exists;
the reverse internal path is gone;
recurrent carrying is destroyed.
```

## Main Lean names

```text
RemovesDirectedEdge
sameDynamics_not_recurrentSupportDestroyed
brokenCycle_removes_return_edge
brokenCycle_keeps_forward_edge
cycle_zeroPerturbation_not_destroyed
cycle_oneReturnEdgeRemoval_destroys_carrying
two_state_recurrent_support_budget_floor
```

The facade also exposes:

```text
RecurrentSupportIntegrity.two_state_perturbation_budget_floor
```

## What this proves

The exact current claim is:

```text
For the two-state recurrent support, no dynamic change cannot count as a
destruction witness, but removal of the return edge can destroy recurrent
carrying while preserving weaker endpoint-viability and forward-reachability
facts.
```

This is the first finite "budget" fact in the recurrent-support stack. It says
that the carried distinction has a threshold of structural fragility in this
toy world.

## What this does not prove

This does not prove:

```text
a general minimum-cut theorem;
a probability of recovery;
a numerical cohesion metric for arbitrary systems;
identity of a support through perturbation;
agency, valuerhood, value, alignment, or Omega proper.
```

Later adapters may turn these exact finite thresholds into probabilistic or
statistical robustness estimates. Core should keep the exact combinatorial
facts separate from those adapter-level interpretations.

## Why it matters

Earlier recurrent-support results already showed:

```text
endpoint viability is weaker than recurrent carrying;
forward reachability is weaker than recurrent carrying;
return structure matters.
```

The perturbation-budget floor adds:

```text
some recurrent carrying can survive zero perturbation but fail under one
critical structural removal.
```

That is a small but important step toward a non-mystical robustness vocabulary:
not "did the same object persist?", but "does the declared recurrent support
still carry the declared consequence distinction under this perturbation?"

## Related notes

- [layer_a_theorem_spine_v0.md](layer_a_theorem_spine_v0.md)
- [recurrent_support_integrity_v0.md](recurrent_support_integrity_v0.md)
- [recurrent_support_perturbation_floor_v0.md](recurrent_support_perturbation_floor_v0.md)
- [irreversible_recurrent_support_loss_v0.md](irreversible_recurrent_support_loss_v0.md)
- [recurrent_support_restoration_v0.md](recurrent_support_restoration_v0.md)

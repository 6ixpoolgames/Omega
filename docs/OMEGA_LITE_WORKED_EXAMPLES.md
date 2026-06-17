# Omega Lite Worked Examples

Status: onboarding artifact
Scope: small examples that explain the current theorem spine without assuming project vocabulary
Claim boundary: illustrative only; not empirical validation or Omega validation

## Purpose

Omega can sound abstract. The core finite lessons are simpler:

```text
1. A score can miss the target.
2. A quotient can fabricate a path.
3. An abstraction can hide loss.
4. A support can lose recurrence even when endpoints survive.
```

These are the current "Omega Lite" examples.

## Example 1: Same Score, Different Target

Suppose two systems receive the same benchmark score:

```text
score(system A) = score(system B)
```

but differ on a safety-relevant target:

```text
target(system A) != target(system B)
```

Then the target does not factor through the score. The score is not a safe
stand-in for that target.

Repo theorem shape:

```text
NonFactorization score target
```

Where to look:

```text
formal/lean/OmegaProper/BaselineWitnesses/NonFactorization.lean
docs/research_notes/omega_theory/nonfactorization_witness_index_v0.md
docs/research_notes/omega_theory/ai_proxy_failure_nonfactorization_v0.md
```

## Example 2: A Bad Quotient Fabricates Reachability

Imagine an exact transition system:

```text
a -> b
c -> d
```

There is no exact path from `a` to `d`.

Now merge `b` and `c` in a coarse presentation:

```text
b = c
```

The abstract system appears to have:

```text
a -> [b=c] -> d
```

The presentation fabricated reachability.

Repo theorem shape:

```text
unsound merge -> phantom reachability
```

Where to look:

```text
formal/lean/OmegaProper/Trajectory/PhantomReachability.lean
docs/research_notes/omega_theory/phantom_reachability_under_unsound_quotient_v0.md
```

## Example 3: A Bad Abstraction Hides Loss

Suppose the exact system loses a target-relevant distinction after a change:

```text
exact before:
  recovery is possible

exact after:
  recovery is lost
```

But the abstraction maps both before and after to the same coarse state:

```text
abstract before = abstract after
```

The abstract map hides the loss.

Repo theorem shape:

```text
same abstraction, different exact loss fact
```

Where to look:

```text
formal/lean/OmegaProper/Trajectory/HiddenLossUnderBadPresentation.lean
formal/lean/OmegaProper/Trajectory/HiddenViabilityLossUnderBadPresentation.lean
formal/lean/OmegaProper/Trajectory/LossAwarePresentationContract.lean
```

## Example 4: Endpoint Survival Is Not Recurrence

Consider a two-state cycle:

```text
left -> right
right -> left
```

The support can carry a consequence distinction because both endpoints return
to each other.

Now break the return edge:

```text
left -> right
```

The endpoints may still be viable, and `left` may still reach `right`, but the
return structure is gone. The support no longer recurrently carries the
distinction.

Repo theorem shape:

```text
endpoint viability + forward reachability
  does not imply recurrent carrying
```

Where to look:

```text
formal/lean/OmegaProper/Trajectory/IrreversibleRecurrentSupportLoss.lean
formal/lean/OmegaProper/Trajectory/RecurrentSupportRestoration.lean
formal/lean/OmegaProper/Trajectory/RecurrentSupportPerturbationBudget.lean
docs/research_notes/omega_theory/recurrent_support_integrity_v0.md
```

## How To Read These Examples

Each example has the same discipline:

```text
declare the exact target;
declare the summary or presentation;
show the summary/presentation cannot determine or preserve the target;
state what is not claimed.
```

The point is not that toy systems are realistic. The point is that unsafe
abstraction principles fail even before realism makes the system harder.

## Relation To The Larger Ambition

The long-run ambition is to mark the viable corridor of compatible
value-bearing continuation.

The small examples do not prove that corridor exists. They prove something
lower and necessary:

```text
some maps of continuation are unsafe because they fabricate, erase, or hide
the facts the downstream target depends on.
```

That is why the project starts with abstraction integrity.

## Related Docs

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- [EXTERNAL_READER_GUIDE.md](EXTERNAL_READER_GUIDE.md)
- [research_notes/omega_theory/layer_a_theorem_spine_v0.md](research_notes/omega_theory/layer_a_theorem_spine_v0.md)
- [research_notes/omega_theory/adapter_provenance_v0.md](research_notes/omega_theory/adapter_provenance_v0.md)

# Coarse/Fine Nonreflection v0

Status: theorem note / protected-plurality bridge
Scope: deterministic target postprocessing, nonfactorization, and macro/fine continuity warnings
Claim boundary: not identity, not moral standing, not valuerhood, not Gradient Ethics, not Omega validation

## Purpose

This note records the coarse/fine nonreflection theorem added in:

```text
formal/lean/OmegaProper/Recovery/Nonreflection.lean
```

The core lesson is:

```text
Fine target preservation can certify coarse target preservation.
Coarse target preservation does not certify fine target preservation unless an
explicit reflection/reconstruction theorem is supplied.
```

This is the first small formal bridge from the effective-layer map to protected
plurality. It blocks a common erasure move:

```text
macro continuity
  therefore protected fine continuations persisted.
```

That inference is invalid when the macro target merges fine target states.

## Positive Direction Already Landed

`TargetPostprocessing.lean` proves the positive direction.

Given:

```text
fine : X -> D
map  : D -> E
coarse := map o fine
```

recovering the fine target entails recovering the coarse target:

```text
fine recovery -> coarse recovery.
```

Representative theorem names:

```text
success_le_targetPostprocess
declaredRecoveryAt_targetPostprocess
recoveryAt_targetPostprocess
recoveryInAt_targetPostprocess
exactDecoder_targetPostprocess
exactRecovery_targetPostprocess
```

This is the safe direction:

```text
personal continuity may imply some civilization-level continuity;
protected fine continuation may imply macro continuation;
joint target recovery may imply marginal recovery.
```

## Negative Direction

`Nonreflection.lean` records the generic negative pattern.

Define:

```text
FineDistinctionCollapsedBy fine map
```

when there are realized states `x` and `y` such that:

```text
fine x != fine y
map (fine x) = map (fine y).
```

Then the coarse target cannot determine the fine target:

```text
NonFactorization (map o fine) fine.
```

Representative theorem names:

```text
nonFactorization_of_postprocess_collision
collapsedFineDistinction_nonFactorization
collapsedFineDistinction_blocks_fiberConstant
collapsedFineDistinction_blocks_factorization
factorsThrough_blocks_postprocess_collision
```

So the unsafe direction fails:

```text
coarse recovery -/-> fine recovery
macro continuity -/-> protected fine continuity
marginal recovery -/-> joint recovery
```

unless a separate reflection, injectivity, or reconstruction condition is
proved.

## Protected-Plurality Interpretation

Suppose a fine target tracks a family of protected continuations:

```text
fine : X -> ProtectedJointState
```

and a macro target reports only a coarse summary:

```text
macro = map o fine.
```

If `map` merges two realized protected joint states, then preservation of the
macro target cannot certify preservation of the fine protected target.

In project terms:

```text
civilization persists
  does not by itself certify
constituent protected lineages persisted.
```

This is not a theorem about which lineages have standing. It is a theorem about
what coarse summaries are unable to certify once protected fine targets are
declared.

## Relation To Nonfactorization

The theorem is deliberately not new machinery. It is an instance of the
standard nonfactorization schema:

```text
same summary,
different target,
therefore target does not factor through summary.
```

The summary is the coarse target:

```text
map o fine
```

and the target is the fine target:

```text
fine.
```

This keeps the protected-plurality bridge tied to the existing anti-Goodhart
and anti-erasure spine.

## What This Does Not Claim

This theorem does not claim:

```text
personal identity;
moral standing;
which fine targets are protected;
that all macro targets are invalid;
that coarse summaries are useless;
that civilization-level continuity has no value;
that value or valuerhood has been derived;
Gradient Ethics;
Omega validation.
```

It claims only:

```text
a non-injective coarse target cannot certify the fine target it merges.
```

## Next Bridges

Useful follow-ups:

```text
1. Protected-family wrapper:
   instantiate the theorem for finite joint protected targets.

2. Temporal lineage version:
   local lineage-step witnesses do not imply one coherent lineage path.

3. Robust-kernel reflection:
   abstract robust viability certificates reflect to exact certificates only
   under requirement reflection, action realizability, and successor soundness.
```


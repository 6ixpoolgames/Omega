# Non-Factorization Witness Index v0

Status: standard-core compression note

This note indexes finite baseline witnesses that have been compressed into the
standard non-factorization schema:

```text
summary S1 = summary S2
target S1 != target S2
```

Therefore the declared target does not factor through the proposed baseline
summary.

The important upgrade is that the stronger entries below use computed finite
summaries, not merely shared predicate labels.

## Lean Schema

The shared schema is:

```text
NonFactorization f g :=
  exists x y, f x = f y and g x != g y
```

Lean location:

```text
formal/lean/OmegaProper/BaselineWitnesses/NonFactorization.lean
```

The fiber-constancy criterion is:

```text
NonFactorization f g <-> not FiberConstant f g
```

Lean location:

```text
formal/lean/OmegaProper/BaselineWitnesses/FactorizationCriterion.lean
```

## Shared Invariance Theorem

The converted witnesses also instantiate a more specific theorem:

```text
summary invariant under move
target changes under move
--------------------------------
NonFactorization summary target
```

In words:

```text
Any summary that forgets a transformation cannot determine a target that
changes under that transformation.
```

Lean location:

```text
formal/lean/OmegaProper/BaselineWitnesses/InvarianceNonFactorization.lean
```

Each computed witness below supplies:

```text
move      a finite swap between two presentations
summary   a computed baseline invariant under the swap
target    a declared target that changes under the swap
```

## Computed Instances

| Witness | Computed summary | Computed target | Lean theorem |
| --- | --- | --- | --- |
| Coordinate split | Four-state exposure profile counts: source count, outcome count, compatible ordered pairs, blocked ordered pairs. | Whether the exposure carries the declared first coordinate. | `coordinateSplit_countBaseline_nonFactorization` |
| Reachability / declared recovery | Per-source reach counts, per-target support counts, and reachable ordered-pair count. | Whether support preserves the declared first coordinate. | `reachability_computedSummary_nonFactorization` |
| Mutual-information proxy / declared recovery | Binary output fiber counts and same/different-output ordered-pair counts. | Whether equal outputs preserve the declared first coordinate. | `mutualInformationProxy_computedSummary_nonFactorization` |
| Compression score / merge soundness | Claimed same-class ordered-pair count and rejected ordered-pair count. | Whether claimed merges respect the declared first-coordinate consequence profile. | `compressionScore_computedSummary_nonFactorization` |
| Marginal coupling | Row counts, column counts, and total joint-table mass. | Whether the joint table factorizes by integer cross-multiplication. | `marginalSummary_jointFactorization_nonFactorization` |

## Why This Matters

The older shape was:

```text
S1 satisfies baseline predicate
S2 satisfies baseline predicate
S1 satisfies target
S2 does not satisfy target
```

That is useful, but a skeptical reader can ask whether the baseline was
actually computed or only named.

The stronger shape is:

```text
computed_summary S1 = computed_summary S2
computed_target S1 != computed_target S2
```

That makes the reduction failure sharper: the target is not a function of the
summary value.

## Not Yet Converted

The following retained witnesses still have useful predicate-level Lean or
Python evidence, but have not yet been converted into computed-summary
`NonFactorization` entries in this index:

```text
chain evidence / class soundness
coarse bisimulation / consequence profile
observation rank / declared recovery
control reach / declared recovery
entropy / recovery profile
intervention effect / declared recovery
frontier morphology / loss profile
marginal success / joint success
optimized success / declared recovery
viability kernel / declared recovery
```

Those should only be added here after the baseline summary and target are
explicit functions with finite computed values.

## Claim Boundary

This index does not validate value, agency, identity, recoverability, or Omega
proper. It only records finite failures of proposed summaries to determine
declared targets.

# RFS-MB0 Pairwise Compatibility Smoke Result

Date: 2026-05-23

Status: completed first machinery smoke; do not scale yet

Result directory:

```text
results/rfs_mb0_pairwise/20260523_pairwise_compatibility_smoke/
```

Primary summary:

```text
results/rfs_mb0_pairwise/20260523_pairwise_compatibility_smoke/summary.md
```

## Run Shape

Implemented a new exact finite pairwise compatibility smoke package:

```text
omega/rfs_mb0_pairwise/
```

The runner computes:

```text
F_H^A(x)
F_H^B(x)
F_H^{A,B}(x)
```

for horizons:

```text
H = 4, 8, 12, 16
```

The first full smoke used:

```text
systems: 315
rows: 1260
workers: 18
errors: 0
status: COMPLETED
elapsed: about 47 seconds
```

Partial-output salvage is implemented through repeated rewrites of:

```text
results.csv
summary.json
summary.md
status.json
systems.jsonl
errors.jsonl, if needed
```

## What Passed

The implementation path works.

The runner produced exact singleton and joint identity-preserving reachable-future counts across structured toy regimes and controls. It completed with no errors and uses the same general checkpoint/salvage pattern as the RFS0 runner.

The output is clear enough to diagnose generator and control behavior before attempting a larger run.

## Main Scientific Read

This is not a positive validation result.

The smoke shows that the first MB0 machinery is usable, but the first toy generator is too permissive for a serious scale-up.

At H16, structured mutual-support, independent-parallel, no-interaction, dead, and permissive controls mostly preserve:

```text
AB / min(A, B) = 1.0
```

This means the current continuity/generator combination overcalls compatibility in many regimes.

The structured `pairwise_incompatible` regime does show degradation:

```text
A = 27
B = 27
AB = 18
AB / min(A, B) = 0.667
```

but that is only a moderate reduction, not a clean incompatibility.

The structured capture regimes did not separate cleanly:

```text
capture_A_over_B:
  A = 42
  B = 30
  AB = 30
  AB / min(A, B) = 1.0

capture_B_over_A:
  A = 30
  B = 42
  AB = 30
  AB / min(A, B) = 1.0
```

So the first implementation does not yet cleanly expose local-preserving / joint-contracting capture.

## Control Read

The random-edge control is strong and partly mimics the intended readouts:

```text
random_edge_control:
  singleton_overcall rows at H16: 7
  local_A_joint_contracting rows at H16: 21
  local_B_joint_contracting rows at H16: 4
```

This is a useful warning. It means raw graph structure can generate apparent compatibility degradation under the current definitions.

The identity-shuffle control mostly breaks one or both singleton identities, which is directionally useful, but it also creates its own singleton-overcall cases. This should be refined before stronger claims.

## Interpretation

The smoke validates the workflow, not the object.

The main lesson is that `<= H` identity-preserving reachability plus broad token continuity makes joint futures hard to eliminate. Since the initial state preserves both identities, literal empty joint futures are usually the wrong first target. The useful early diagnostic is instead:

```text
AB_count / min(A_count, B_count)
```

plus transition-level joint-contraction diagnostics.

## Recommendation

Do not run a larger MB0 batch yet.

Next revision should:

1. Tighten the pairwise-incompatible generator so singleton continuations remain available while joint continuations sharply contract.
2. Make capture regimes produce clear asymmetric local-preserving / joint-contracting transitions.
3. Add exact-H or non-initial endpoint diagnostics alongside the current <=H sets.
4. Separate stasis and dead controls from mutual-support-like bins by reporting nontrivial continuation, not merely persistence.
5. Keep random-edge and identity-shuffle controls in the gate; they are currently doing useful adversarial work.

The current result is a good first smoke for the new branch: implementation works, hardware path works, outputs are salvageable, and the result tells us what to revise before scale.


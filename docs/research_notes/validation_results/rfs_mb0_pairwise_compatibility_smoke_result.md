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

## V2 Audit Revision

After an external Codex audit, the MB0 smoke was revised and rerun:

```text
results/rfs_mb0_pairwise/20260523_pairwise_compatibility_smoke_v2/
```

The audit diagnosis was accepted:

```text
asymmetry is not necessarily too weak;
the current semantics make asymmetry too easy to route around
```

The main mechanical problems were:

1. `<= H` reachability includes the start state and easy early persistence.
2. Token continuity was broad enough that `damaged` still counted as identity-preserving.
3. Every structured regime had a cheap status-preserving phase-advance edge.
4. `dead_control` only degraded identities to `damaged`, which remained continuous.
5. Transition deltas compared `reachable(initial, H)` to `reachable(target, H)` instead of the remaining horizon after the first step.

The v2 patch made four minimal changes:

1. Added exact-H frontier counts:

```text
exact_A_count
exact_B_count
exact_AB_count
exact_joint_gap_ratio
```

2. Added nontrivial endpoint diagnostics:

```text
nontrivial_AB_count
exact_nontrivial_AB_count
flatline_flag
```

3. Fixed dead control so identities eventually leave continuity:

```text
alive -> strained -> damaged -> lost
```

4. Removed the universal benign phase-advance bypass from capture and pairwise-incompatible structured regimes.

The revised smoke used:

```text
systems: 315
rows: 1260
workers: 18
errors: 0
status: COMPLETED
elapsed: about 45 seconds
```

## V2 Read

The revision improved diagnosis but did not produce a scale-ready substrate.

The dead control is now correctly exposed by exact-H metrics:

```text
dead_control:
  <=H AB = 3
  exact-H AB = 0
  readout = no_exact_joint_persistence
```

Stasis and clock-like cases are now separated by flatline diagnostics:

```text
flatline_joint_persistence
```

This confirms that exact-H/frontier and nontrivial-endpoint metrics are necessary for this branch.

However, structured capture remains too weak:

```text
structured capture_A_over_B:
  A = 30
  B = 18
  AB = 18
  exact AB = 4
  AB / min(A, B) = 1.0

structured capture_B_over_A:
  A = 18
  B = 30
  AB = 18
  exact AB = 4
  AB / min(A, B) = 1.0
```

These regimes reduce one singleton but still do not show a clean joint-compatibility contraction relative to the weaker singleton.

The structured pairwise-incompatible regime remains only moderately degraded:

```text
A = 25
B = 25
AB = 16
exact AB = 5
AB / min(A, B) = 0.640
exact AB / min(exact A, exact B) = 0.625
```

The random-edge control remains a serious fakeout:

```text
random_edge_control:
  local_A_joint_contracting: 10 H16 rows
  singleton_overcall: 3 H16 rows
  no_exact_joint_persistence: 31 H16 rows
```

This means raw graph randomization can still mimic several intended warnings under the current generator and continuity definitions.

## Updated Recommendation

The project should keep MB0, but it should not scale this generator.

The next revision should make the generator itself stricter rather than adding a heavy cost model:

1. Define conflict regimes where A-only and B-only continuations remain available, but joint continuations sharply shrink at exact H.
2. Make capture an asymmetric incompatibility of futures, not just degradation of one status coordinate.
3. Report horizon-filtration curves directly:

```text
H -> A_count
H -> B_count
H -> AB_count
H -> exact_AB_count
H -> AB/min
H -> exact_AB/min
```

4. Keep path geometry as the first cost-like diagnostic:

```text
first_nonempty_H_AB
joint_delay
exact_H_growth
flatline_flag
```

Do not add resource, reward, metabolism, or energy variables yet. The next mathematical object should be the horizon filtration of singleton and joint identity-preserving futures.

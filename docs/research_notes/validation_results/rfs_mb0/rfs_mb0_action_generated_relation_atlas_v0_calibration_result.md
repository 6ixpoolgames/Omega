# RFS-MB0 Action-Generated Relation Atlas v0 Calibration Result

Date: 2026-05-23

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_ACTION_GENERATED_RELATION_SUBSTRATE_SPEC.md
```

Primary result directory:

```text
results/rfs_mb0_relation_atlas/20260523_action_generated_v0_n5_calibration/
```

## Purpose

This pass replaced the hand-named RFS-MB0 relation families with neutral,
parameter-generated relation environments.

The goal was not to validate Omega. The goal was to test whether an
action-generated relation atlas can produce nontrivial middle-regime
environments that the existing future-landscape detector can interrogate
without named positive families.

## Implementation

Added:

```text
omega/rfs_mb0_future_landscape/relation_generator.py
omega/rfs_mb0_future_landscape/run_relation_atlas.py
```

The generator builds finite distinction spaces `X = A^n` and creates top-k
outgoing relations from neutral local transition scores over local change,
generated constraint violation, constraint-profile change, seeded directional
asymmetry, seeded roughness, controlled reversibility, and controlled rewiring.

No generated environment is named as structured, expanding, contracting,
viable, supportive, degrading, agentic, or Omega-like.

Generated nulls in this first implementation:

```text
degree_preserving_rewire
out_degree_preserving_random
constraint_shuffled
asymmetry_shuffled
roughness_resampled
```

## Runs

Debug smoke:

```text
results/rfs_mb0_relation_atlas/debug_action_generated_v0/
parameter_samples: 10
horizon_grid: dense_early
workers: 4
status: COMPLETED
errors: 0
elapsed: about 54 seconds
generated environments: 10
middle-regime environments: 7
atlas gate passes: 0
```

Initial mixed n5/n6 calibration:

```text
results/rfs_mb0_relation_atlas/20260523_action_generated_v0_calibration/
parameter_samples: 50
horizon_grid: long_10x
workers: 18
status: TIME_LIMIT_REACHED
errors: 0
elapsed: about 968 seconds
generated environments completed: 49 / 50
middle-regime environments: 30
atlas gate passes: 0
```

The mixed calibration exposed an operational issue: the pool was launched with
18 workers, but heterogeneous n=6 jobs created long stragglers. CPU utilization
dropped near the end as the worker pool drained.

Primary n=5 calibration:

```text
results/rfs_mb0_relation_atlas/20260523_action_generated_v0_n5_calibration/
parameter_samples: 50
coordinate_counts: 5
max_state_count: 300
horizon_grid: long_10x
workers: 18
status: COMPLETED
errors: 0
elapsed: about 289 seconds
generated environments: 50
middle-regime environments: 28
profiles: 8250
atlas gate passes: 0
```

## Primary Read

The environment generator works.

The neutral generator produced many middle-regime environments:

```text
middle_regime_environment: 28
fast_saturation_environment: 6
underconnected_environment: 7
underdetermined_environment: 7
cycle_dominated_environment: 2
```

The scientific gate remains not passed:

```text
atlas_gate_pass_count: 0
```

Aggregate detector classes in the n=5 calibration:

```text
underdetermined: 24
saturation_dominated: 23
local_only: 3
```

Window-level structured candidates do appear in some environments and probe
families, especially early and pre-saturation windows. They do not promote to
aggregate claims under the current matched-null discipline.

## Interpretation

This is a successful substrate-calibration pass and a negative detector pass.

The current result improves the project in three ways:

- it removes the hand-named positive family problem;
- it demonstrates that neutral generated relations can produce nontrivial
  middle-regime environments;
- it keeps the detector conservative: local/window candidates are visible, but
  they do not become aggregate positives.

The main blocker has moved from environment generation to:

```text
Which parameter regimes reliably produce middle-regime environments, and what
additional null or window-level criteria are needed before any local candidate
can be treated as more than a diagnostic?
```

## Recommendation

Keep the relation atlas branch.

Use n=5 batches for fast calibration and use n=6 only in targeted follow-up
runs after identifying parameter regimes that produce stable middle-regime
behavior.

Next useful steps:

- summarize parameter trends for middle-regime vs saturation/collapse classes;
- add a confirmatory split once a small set of parameter regions is selected;
- tighten window-level controls before promoting early/pre-saturation
  candidates;
- keep `atlas_gate_pass_count` as the headline scientific gate.

Do not claim Omega validation from this pass.

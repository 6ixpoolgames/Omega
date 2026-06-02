# RFS-MB0 Laptop Stage B Mechanism Smoke 30m Result

Date: 2026-05-28

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_FRONTIER_TRANSFORM_SYNDROME_AND_MECHANISM_CONTROL_AUDIT_SPEC.md
```

## Claim Boundary

This was a laptop-local Stage B mechanism-control dependency smoke over the
currently available laptop-regenerated one-group Phase B full-control output.
It was theory/instrumentation work, not historical desktop full-breadth
confirmation.

It was not holdout scoring, n=6 transfer, alphabet expansion, candidate
promotion, Omega detection, agency detection, identity detection, or value
detection.

## Hardware Boundary

This run used the laptop profile, not the desktop profile:

```text
machine class: laptop
cpu: Intel i7-1165G7 class, 8 logical processors
gpu: Intel Iris Xe, no CUDA path used
workers: 7
job_batch_size: 2
thread caps: OMP/OPENBLAS/MKL/NUMEXPR/NUMBA = 1
```

Desktop runs should not inherit this worker profile.

## Inputs

Stage A addendum:

```text
results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_a_addendum_laptop_full_control/
```

Phase B source:

```text
results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls/
```

Selected preregistered syndrome IDs:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag
SYN_B_high_turnover_high_offdiag_high_window_delta
SYN_C_low_growth_high_concentration_low_entropy
SYN_D_high_turnover_high_entropy_low_bottleneck_control
```

## Implementation

Added a scoped Stage B runner:

```text
omega/rfs_mb0_future_landscape/run_frontier_transform_stage_b_mechanism_smoke.py
```

The runner emits baseline and mechanism-control rows for roughness,
asymmetry, and constraint controls, then reuses the Stage A syndrome component
scoring path against the Phase B compact control values.

The Stage A syndrome audit runner now preserves mechanism metadata fields in
component-score rows so downstream dependency summaries can group by control
condition.

## Run Shape

Output path:

```text
results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_b_mechanism_smoke_30m/
```

Command shape:

```text
python -m omega.rfs_mb0_future_landscape.run_frontier_transform_stage_b_mechanism_smoke \
  --out results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_b_mechanism_smoke_30m \
  --groups 1 --design-groups 1 --fresh-seeds-per-group 2 \
  --start-samples-list 4,8 \
  --workers 7 --job-batch-size 2 \
  --max-runtime-seconds 1800 --shutdown-cushion-seconds 120
```

## Status

```text
status: COMPLETED
elapsed_seconds: 89.283
jobs_completed: 224 / 224
metric_rows: 18816
component_score_rows: 141120
syndrome_rate_rows: 224
dependency_score_rows: 52
decision_rows: 4
mechanism_control_systems_generated: 208
errors: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
new_systems_generated: 0
promotion_enabled: false
candidate_detection_enabled: false
```

All files in `output_manifest.json` were present.

## Decision Summary

```text
SYN_A_low_growth_high_bottleneck_low_offdiag
  decision_class: control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.026785714285714284
  max_mechanism_dependency_score: 1.0
  max_control_destructiveness_score: 1.0

SYN_B_high_turnover_high_offdiag_high_window_delta
  decision_class: no_measurable_syndrome
  baseline_syndrome_rate: 0.0

SYN_C_low_growth_high_concentration_low_entropy
  decision_class: control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.026785714285714284
  max_mechanism_dependency_score: 1.0
  max_control_destructiveness_score: 1.0

SYN_D_high_turnover_high_entropy_low_bottleneck_control
  decision_class: no_measurable_syndrome
  baseline_syndrome_rate: 0.0
```

## Non-Destructive Control Read

Only 12 dependency rows were non-destructive in this smoke. For the measurable
SYN_A and SYN_C rows:

```text
asymmetry p0.01: baseline 0.026785714285714284, control 0.026785714285714284, dependency 0.0
asymmetry p0.02: baseline 0.026785714285714284, control 0.026785714285714284, dependency 0.0
roughness p0.01: baseline 0.026785714285714284, control 0.013392857142857142, dependency 0.5
```

The stronger roughness, asymmetry, and constraint controls frequently crossed
the substrate-destructiveness threshold:

```text
control systems flagged too destructive: 160
```

## Interpretation

This is mildly promising as an instrumentation target, not as a validation
result. The measurable SYN_A and SYN_C syndromes show a weak roughness-sensitive
dependency profile under the gentlest non-destructive roughness control, while
gentle asymmetry leaves the rate unchanged.

The result is still underdetermined because stronger controls are too
destructive, and SYN_B/SYN_D have zero baseline syndrome rate in this limited
Stage B design. Stage B should stay in mechanism-profile calibration mode.

Holdout remains blocked.

## Next Step

Run a Stage B-2 targeted mechanism smoke that narrows to non-destructive
control ladders and increases baseline measurability:

```text
roughness: add gentler strengths below p0.01 and refine around p0.01
asymmetry: keep p0.01 and p0.02 as generic-phase comparators
constraint: introduce gentler preservation-first settings before weak/medium/strong
sampling: increase seeds only after the non-destructive ladder is calibrated
```

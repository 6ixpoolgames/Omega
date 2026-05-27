# RFS-MB0 Laptop Stage A Addendum Result

Date: 2026-05-28

## Claim Boundary

This was an addendum-complete read-only Stage A syndrome audit over the
laptop-regenerated full-control Phase B output:

```text
results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls/
```

It is theory/instrumentation work over the currently available laptop-local
Phase B data. It is not historical desktop full-breadth confirmation, holdout
validation, candidate promotion, mechanism-control confirmation, n=6 transfer,
Omega detection, agency detection, identity detection, or value detection.

The Phase B input remains laptop-local and one focused group only:

```text
jobs_completed: 192 / 192
control_rows: 1250183
historical full-breadth target: not satisfied
```

## Addendum Implementation

The Stage A runner now emits:

```text
syndrome_manifest.json
phase_b_syndrome_marginal_preserving_controls.csv
phase_b_syndrome_component_ablation.csv
```

The runner also uses metric-native syndrome IDs in scored decision outputs:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag
SYN_B_high_turnover_high_offdiag_high_window_delta
SYN_C_low_growth_high_concentration_low_entropy
SYN_D_high_turnover_high_entropy_low_bottleneck_control
SYN_E_transition_then_persistence_cascade
```

Informal syndrome names appear only as optional fields in the frozen manifest.

## Run Shape

Output path:

```text
results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_a_addendum_laptop_full_control/
```

Command shape:

```text
python -m omega.rfs_mb0_future_landscape.run_frontier_transform_syndrome_audit \
  --phase-b-dir results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls \
  --out results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_a_addendum_laptop_full_control \
  --marginal-control-replicates 500
```

## Status

```text
status: COMPLETED
elapsed_seconds: 26.587
metric_rows: 17920
control_rows: 1249988
control_source: phase_b_stage_a_control_values.csv
syndrome_component_rows: 94080
syndrome_manifest_rows: 5
marginal_preserving_control_rows: 24000
component_ablation_rows: 48
errors: 0
new_systems_generated: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

## Readiness Row

```text
decision_class: syndrome_smoke_joint_positive_above_marginal_controls
stage_b_allowed: 1
selection_mode: preregistered
selection_reason: joint_rate_above_marginal_preserving_controls_and_not_single_component_driven
apparent_positive_contexts: 14
single_component_driven_contexts: 0
insufficient_marginal_control_contexts: 4
marginal_control_minimum_replicates_met: 1
holdout_scoring_count: 0
```

Selected preregistered syndrome IDs:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag
SYN_B_high_turnover_high_offdiag_high_window_delta
SYN_C_low_growth_high_concentration_low_entropy
SYN_D_high_turnover_high_entropy_low_bottleneck_control
```

Excluded positive probes:

```text
existing_low
full_state_hash
```

## Marginal-Preserving Control Result

Strongest joint-rate excess contexts:

```text
SYN_B_high_turnover_high_offdiag_high_window_delta
  probe: constraint_profile_hash
  flow_mode: one_step_local_flow
  observed_joint_rate: 0.03571428571428571
  component_marginal_preserving_control_mean: 0.011767857142857142
  joint_rate_excess: 0.02394642857142857
  joint_rate_percentile: 1.0

SYN_B_high_turnover_high_offdiag_high_window_delta
  probe: constraint_profile_hash
  flow_mode: constrained_window_flow
  observed_joint_rate: 0.03125
  component_marginal_preserving_control_mean: 0.008895833333333334
  joint_rate_excess: 0.022354166666666668
  joint_rate_percentile: 1.0

SYN_D_high_turnover_high_entropy_low_bottleneck_control
  probe: constraint_profile_hash
  flow_mode: constrained_window_flow
  observed_joint_rate: 0.0548469387755102
  component_marginal_preserving_control_mean: 0.0335765306122449
  joint_rate_excess: 0.0212704081632653
  joint_rate_percentile: 1.0
```

## Component Ablation

All emitted ablation rows were classified as:

```text
joint_syndrome_not_single_component_driven: 48
```

No positive context was classified as:

```text
single_component_driven_not_joint_syndrome
```

## Remaining Uncertainty

Mechanism controls remain missing from this Stage A pass:

```text
asymmetry
constraint
roughness
```

That means the next Stage B mechanism-control rerun is warranted by the
addendum gate on this laptop-local theory branch, but its interpretation must be
dependency-profile oriented. It is not a holdout opening and not a historical
desktop full-breadth confirmation.

Holdout remains blocked.

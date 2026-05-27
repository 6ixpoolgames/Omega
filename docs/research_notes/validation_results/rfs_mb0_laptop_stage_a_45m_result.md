# RFS-MB0 Laptop Stage A 45m Result

Date: 2026-05-28

## Claim Boundary

This was a read-only Stage A syndrome audit over the laptop-regenerated
full-control Phase B output:

```text
results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls/
```

It was not a historical desktop full-breadth audit, holdout validation,
candidate promotion, mechanism-control confirmation, n=6 transfer, Omega
detection, agency detection, identity detection, or value detection.

The Phase B input was full-control but laptop-local and one focused group only:

```text
jobs_completed: 192 / 192
control_rows: 1250183
historical full-breadth target: not satisfied
```

## Run Shape

Output path:

```text
results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_a_laptop_full_control_45m/
```

Command shape:

```text
python -m omega.rfs_mb0_future_landscape.run_frontier_transform_syndrome_audit \
  --phase-b-dir results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls \
  --out results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_a_laptop_full_control_45m
```

The run was launched under a 45-minute outer wall-clock cap. It completed well
inside that cap.

## Status

```text
status: COMPLETED
elapsed_seconds: 10.078
metric_rows: 17920
control_rows: 1249988
control_source: phase_b_stage_a_control_values.csv
syndrome_component_rows: 137984
errors: 0
new_systems_generated: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

## Readiness Row

```text
decision_class: syndrome_smoke_positive_above_controls
stage_b_allowed: 1
selected_syndrome_ids:
  diffusive_noise_syndrome
  recurrence_cascade_syndrome
  stabilizing_boundary_syndrome
  transition_boundary_syndrome
selection_mode: preregistered
selection_reason: joint_pass_in_stage_a
excluded_positive_probes:
  existing_low
  full_state_hash
missing_mechanism_control_families:
  asymmetry
  constraint
  roughness
phase_b_prior_decision: phase_c_blocked_no_recurrence
holdout_scoring_count: 0
```

## Control Coverage

Computed controls were present for:

```text
start_shuffled_control
horizon_order_shuffled_control
neutral_generated_window_control
frontier_size_matched_window_control
```

`probe_marginal_window_control` remained a placeholder.

Mechanism controls remained missing, as expected for the current Stage A runner:

```text
asymmetry
constraint
roughness
```

## Addendum Gap

This run used the current Stage A runner. It does not yet satisfy the full
syndrome-audit addendum contract. Missing addendum outputs:

```text
syndrome_manifest.json
phase_b_syndrome_marginal_preserving_controls.csv
phase_b_syndrome_component_ablation.csv
```

Therefore the result is a useful fast Stage A smoke/postmortem over the
laptop-regenerated full-control CSV, but not an addendum-complete external
audit result.

## Decision

The 45-minute Stage A pass is viable on laptop hardware. It completed in about
10 seconds using the cached compact Stage A control-value table.

Recommended next step:

```text
Patch Stage A to emit the addendum-required manifest, marginal-preserving
controls, and component ablation before treating Stage A as externally
reviewable.
```

Holdout remains blocked.

# RFS-MB0 Frontier-Transform Phase B Design-Set Recurrence Result

Date: 2026-05-27

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_FRONTIER_TRANSFORM_PHASE_B_10H_DESIGN_RECURRENCE_SPEC.md
```

Runner:

```text
omega/rfs_mb0_future_landscape/run_frontier_transform_phase_b.py
```

Local output:

```text
results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_b_10h/
```

## Claim Boundary

This was a design-set Phase B recurrence run only. It was not holdout
validation, candidate promotion, transfer testing, identity detection, agency
detection, value detection, or a scientific gate pass.

Holdout remained listed only:

```text
holdout_scoring_count: 0
holdout_detection_enabled: false
promotion_enabled: false
```

## Smoke And Cleanup

Two smoke passes were run before the primary batch:

```text
results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_b_smoke/
results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_b_smoke_repaired/
```

The first smoke passed the technical contract, but it exposed an
interpretability weakness in the matched recurrence control summary: recurrence
controls were too descriptive and could make Phase C readiness look stronger
than warranted. The runner was repaired so matched recurrence controls are
computed from non-placeholder transform-control effects, with placeholder and
not-available controls excluded from positive readiness.

The repaired smoke completed cleanly:

```text
status: COMPLETED
jobs_completed: 16 / 16
metric_rows: 896
control_rows: 55283
errors: 0
holdout_scoring_count: 0
phase_b_design_recurrence_summary.csv: present
decision_class: phase_c_blocked_no_recurrence
```

## Primary Run Shape

```text
workers: 18
design_groups: 10
fresh_seeds_per_group: 8
start_samples_list: 4, 8, 16
flow_modes:
  constrained_window_flow
  one_step_local_flow
probes:
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple
  existing_low
  full_state_hash
windows: 7 canonical windows
max_runtime_seconds: 36000
shutdown_cushion_seconds: 900
```

The full primary run completed without hitting the time limit:

```text
status: COMPLETED
jobs_completed: 1120 / 1120
metric_rows: 134400
control_rows: 13165111
errors: 0
elapsed_seconds: 3100.015
holdout_scoring_count: 0
```

Graceful-exit behavior was added before the run. The runner now writes
`status.json` and `phase_b_progress_checkpoints.csv` during execution, stops
launching new work inside the shutdown cushion, handles interrupt signals, and
finalizes partial artifacts if interrupted.

## Metric-Family Recurrence

Mean recurrence by B0-viable family:

| metric_family | rows | observed_recurrence_rate_mean | seed_recurrence_rate_mean | start_recurrence_rate_mean | window_recurrence_rate_mean |
| --- | ---: | ---: | ---: | ---: | ---: |
| bottleneck | 16 | 0.2875 | 0.4375 | 0.4375 | 0.4375 |
| support_turnover | 40 | 0.2600 | 0.5000 | 0.5000 | 0.4714 |
| transition_matrix | 48 | 0.2417 | 0.5000 | 0.5000 | 0.4762 |
| window_stability | 17 | 0.1176 | 0.2353 | 0.2353 | 0.2017 |

These rates show some recurrent design-set transform effects, especially in
support-turnover, transition-matrix, and bottleneck families. They are not yet a
positive Phase C gate because the matched recurrence controls did not show
positive excess over computed controls.

## Matched Recurrence Controls

After repair, the strongest observed recurrence rows were control-equivalent:

```text
observed_recurrence_rate: up to 0.6
control_recurrence_mean: matched at 0.6 on the strongest rows
recurrence_excess: 0.0 on the strongest rows
weak_control_flag: 0 on those rows
```

Examples include:

```text
support_turnover / lost_signature_rate / constraint_profile_hash / both flows
support_turnover / signature_distribution_js_to_next_window / both constraint probes
transition_matrix / off_diagonal_transform_mass / constraint_profile_hash / one_step_local_flow
```

The correct interpretation is control-equivalent recurrence, not a positive
Phase C signal.

## Phase C Readiness

Final decision:

```text
decision_class: phase_c_blocked_no_recurrence
phase_c_ready: 0
supporting_metric_family_count: 0
supporting_probe_count: 0
supporting_rows: 0
holdout_scoring_count: 0
```

The name `phase_c_blocked_no_recurrence` should be read narrowly: recurrence was
not absent in raw design-set summaries, but no recurrence survived the repaired
matched recurrence-control gate with positive excess.

## Limitations

`probe_marginal_window_control` remains labeled `placeholder` and is excluded
from positive readiness.

The following controls remain explicitly unavailable:

```text
constraint_shuffled_transform_control
asymmetry_shuffled_transform_control
roughness_resampled_transform_control
```

`full_state_hash` and `existing_low` are diagnostic/control probes only and did
not drive readiness.

## Recommendation

Do not open frozen holdout Phase C from this result.

The branch remains useful technically: the frontier-transform runner now has
flow separation, computed controls, progress checkpoints, graceful partial
finalization, and a scalable Phase B output contract. Scientifically, the next
step should be either:

```text
1. implement stronger independent recurrence controls/null replicates, or
2. improve the transform probes so recurrence is not control-equivalent.
```

Scaling the same detector deeper without improving the recurrence-control basis
is unlikely to clarify the object.

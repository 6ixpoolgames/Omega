# RFS-MB0 Desktop Phase B / Stage A / Stage B Validation Result

Date: 2026-05-28

Specs:

```text
docs/RFS_MB0_REGENERATED_PHASE_B_FULL_CONTROL_STAGE_A_RUN_SPEC.md
docs/RFS_MB0_FRONTIER_TRANSFORM_SYNDROME_AND_MECHANISM_CONTROL_AUDIT_SPEC.md
docs/RFS_MB0_FRONTIER_TRANSFORM_SYNDROME_AUDIT_ADDENDUM.md
```

## Claim Boundary

This was a desktop validation of the regenerated Phase B full-control path,
read-only Stage A syndrome audit, and Stage B mechanism-control smoke.

It was not holdout validation, n=6 transfer, alphabet expansion, candidate
promotion, Omega detection, agency detection, identity detection, or value
detection.

## Hardware Boundary

This run used the desktop profile, not the laptop profile:

```text
cpu: Ryzen 5900X class
gpu: RTX 4070 Ti available, not needed for these CPU-bound runners
workers: 18
job_batch_size: 4
thread caps: OMP/OPENBLAS/MKL/NUMEXPR = 1
```

The laptop results remain useful for runner validation only. They should not be
used to infer desktop runtime or worker count.

## Performance And Graceful-Exit Notes

The regenerated Phase B runner used the optimized path:

```text
full control CSV written
compact Stage A control-value CSV written
duplicate row-level effect CSV skipped
periodic status/checkpoint writes enabled
shutdown cushion enabled
signal-aware partial finalization enabled
```

Stage B mechanism smoke was also updated before this run to emit:

```text
mechanism_control_progress_checkpoints.csv
partial status.json during execution
signal-aware partial interruption handling
shutdown-cushion finalization
```

Raw generated outputs are intentionally local and ignored. The public/lab repos
retain scripts, specs, and this result note rather than multi-GB CSVs.

## Stage 1: Regenerated Phase B Full Controls

Output:

```text
results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_phase_b_regenerated_full_controls/
```

Run shape:

```text
design_groups: 10
fresh_seeds_per_group: 8
start_samples_list: 4,8,16
probes:
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple
  existing_low
  full_state_hash
workers: 18
job_batch_size: 4
skip_row_level_effect_csv: true
skip_full_control_csv: false
```

Status:

```text
status: COMPLETED
elapsed_seconds: 3959.802
jobs_completed: 1120 / 1120
metric_rows: 134400
control_rows: 13165111
stage_a_control_value_rows: 13163988
errors: 0
full_control_csv_written: 1
row_level_effect_csv_written: 0
holdout_scoring_count: 0
phase_c_ready: 0
decision_class: phase_c_blocked_no_recurrence
```

Control completeness passed. The full control CSV was about 8.3 GB locally; the
compact Stage A control-value table was about 1.8 GB and was used by Stage A.

## Stage 2: Read-Only Stage A Syndrome Audit

Output:

```text
results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_stage_a_regenerated_full_controls/
```

Status:

```text
status: COMPLETED
elapsed_seconds: 178.609
metric_rows: 134400
control_source: phase_b_stage_a_control_values.csv
control_rows: 13163988
syndrome_component_rows: 940800
marginal_control_replicates: 500
marginal_preserving_control_rows: 24000
new_systems_generated: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

Stage A readiness:

```text
decision_class: syndrome_smoke_joint_positive_above_marginal_controls
stage_b_allowed: 1
selection_mode: preregistered
selected_syndrome_ids:
  SYN_A_low_growth_high_bottleneck_low_offdiag
  SYN_B_high_turnover_high_offdiag_high_window_delta
  SYN_C_low_growth_high_concentration_low_entropy
  SYN_D_high_turnover_high_entropy_low_bottleneck_control
excluded_positive_probes:
  existing_low
  full_state_hash
missing_mechanism_control_families:
  asymmetry
  constraint
  roughness
```

The strongest Stage A read is that preregistered metric-native joint syndromes
separate from marginal-preserving controls on the regenerated desktop Phase B
output. This supports a mechanism-control smoke, not holdout opening.

## Stage 3: Stage B Mechanism-Control Smoke

Output:

```text
results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_stage_b_mechanism_smoke/
```

Run shape:

```text
design_groups: 10
fresh_seeds_per_group: 4
start_samples_list: 4,8
workers: 18
job_batch_size: 4
selected_syndrome_count: 4
```

Status:

```text
status: COMPLETED
elapsed_seconds: 980.677
jobs_completed: 4480 / 4480
metric_rows: 376320
component_score_rows: 2822400
syndrome_rate_rows: 224
dependency_score_rows: 52
decision_rows: 4
mechanism_control_systems_generated: 4160
errors: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

Decision summary:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag:
  control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.02857142857142857
  max_mechanism_dependency_score: 1.0

SYN_B_high_turnover_high_offdiag_high_window_delta:
  control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.08684895833333334
  max_mechanism_dependency_score: 0.14242878560719646

SYN_C_low_growth_high_concentration_low_entropy:
  control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.03549107142857143
  max_mechanism_dependency_score: 1.0

SYN_D_high_turnover_high_entropy_low_bottleneck_control:
  control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.03850446428571429
  max_mechanism_dependency_score: 0.4753623188405797
```

Substrate preservation:

```text
non-destructive preservation rows: 960
too-destructive preservation rows: 3200
```

Non-destructive controls were limited to:

```text
roughness_resampled_transform_control p0.01
asymmetry_flip_sweep_control p0.01
asymmetry_flip_sweep_control p0.02
```

Within those non-destructive controls, the most informative dependency rows
were:

```text
SYN_C roughness p0.01:
  baseline 0.03549 -> control 0.02422
  dependency 0.31761

SYN_C asymmetry p0.02:
  baseline 0.03549 -> control 0.02467
  dependency 0.30503

SYN_A asymmetry p0.02:
  baseline 0.02857 -> control 0.01987
  dependency 0.30469

SYN_A roughness p0.01:
  baseline 0.02857 -> control 0.01998
  dependency 0.30078
```

## Interpretation

This is a real improvement over the earlier marginal-recurrence failure:
desktop Stage A found preregistered joint signed syndromes above
marginal-preserving controls on regenerated full-control Phase B rows.

Stage B then showed that some selected syndromes are sensitive to the gentlest
non-destructive roughness/asymmetry controls. However, the mechanism-control
ladder is still too destructive at many settings, so the correct class remains:

```text
control_too_destructive_underdetermined
```

This is not a negative result against the syndrome branch. It is an
instrumentation result: the next run should refine preservation-first mechanism
control ladders before increasing seeds or touching holdout.

## Recommendation

Do not open holdout Phase C.

Do run a smaller Stage B-2 calibration focused on non-destructive mechanism
controls:

```text
roughness: add gentler strengths below p0.01 and refine around p0.01
asymmetry: keep p0.01 and p0.02, optionally add below p0.01
constraint: redesign as preservation-first; current settings are too destructive
```

The upcoming gauge-hybrid branch should treat this as a useful warning: a
cross-view or mechanism-dependent shadow is only meaningful if the view/control
transforms preserve enough substrate for comparison.

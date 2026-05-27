# RFS-MB0 Frontier-Transform Phase B 10h Design-Set Recurrence Spec

Status: Codex implementation spec after successful Phase B0 control/flow repair

Purpose: run a larger but still disciplined Phase B design-set recurrence batch using the frontier-transform instrument that passed Phase A and B0. This is a 10-hour wall-clock design-set run. It is not holdout testing, not candidate promotion, not n=6 transfer, and not alphabet expansion.

This follows:

```text
docs/RFS_MB0_FRONTIER_TRANSFORM_INSTRUMENTATION_SPEC.md
docs/RFS_MB0_FRONTIER_TRANSFORM_PHASE_B0_CONTROL_FLOW_REPAIR_SPEC.md
results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_a/
results/rfs_mb0_relation_atlas/20260527_frontier_transform_b0/
```

B0 readiness result:

```text
decision_class: phase_b_ready
phase_b_ready: 1
silent_fallback_removed: 1
required_controls_present: 1
holdout_scoring_count: 0
viable metric families after B0:
  bottleneck
  support_turnover
  transition_matrix
  window_stability
```

## 0. Claim boundary

Phase B is design-set recurrence only.

It does not claim:

```text
Omega detected
agent detected
identity detected
valuer detected
viability proven
scientific gate passed
holdout passed
transfer passed
candidate promoted
```

Allowed claims:

```text
A frontier-transform metric family recurs or does not recur across design-set seeds/starts/windows above computed controls.
A transform effect direction is stable or unstable.
A metric family is or is not ready for frozen holdout Phase C.
```

## 1. Cleanup required before the 10h run

Do a small cleanup/smoke before spending the 10h budget.

### 1.1 Required code cleanup

Use the B0 runner as the base, but clean the following before Phase B:

```text
1. Rename B0-only fields to Phase B terminology where appropriate.
2. Keep flow_mode separation exactly as in B0.
3. Keep silent fallback removed.
4. Keep holdout scoring disabled.
5. Keep constraint_shuffled_transform_control explicitly marked not_available unless implemented.
6. Mark probe_marginal_window_control as placeholder unless true marginal re-pairing is implemented.
7. Preserve signed_effect_size and absolute_effect_size.
8. Preserve no_window_target_rate and skipped_state_count.
9. Preserve status finalization and shutdown cushion.
```

### 1.2 Preferred control cleanup

If feasible before the run, improve `probe_marginal_window_control` from placeholder to true marginal re-pairing.

Required behavior for true marginal control:

```text
Given source signature counts from F_a and target signature counts from F_b,
construct random source-target pairings preserving both marginals,
then recompute transition-matrix metrics.
```

If not implemented, retain the placeholder but label all rows:

```text
control_quality = placeholder
```

Do not let placeholder controls drive a positive conclusion.

### 1.3 Smoke test

Before 10h batch, run a small smoke:

```text
groups: 2 design groups
fresh_seeds_per_group: 2
start_samples: 4
probes: constraint_profile_hash, constraint_violation_count_plus_local_tuple
flow_modes: constrained_window_flow, one_step_local_flow
windows: canonical windows
controls: all required controls except optional constraint shuffle
max_runtime_seconds: 600
```

Smoke must pass:

```text
status COMPLETED
errors = 0
holdout_scoring_count = 0
metric_rows > 0
control_rows > 0
phase_b_design_recurrence_summary.csv exists
all required output files exist
```

If smoke fails, do not run the 10h batch.

## 2. 10-hour run shape

Wall-clock budget:

```text
max_runtime_seconds: 36000
shutdown_cushion_seconds: 900
```

Runner should stop launching new jobs when remaining time is below cushion and write a final status.

### 2.1 Primary batch

Use design set only:

```text
design groups: 10
holdout groups: listed only, not scored
fresh_seeds_per_group: 8
start_samples_list: 4,8,16
windows:
  0->1
  1->2
  2->4
  4->8
  8->16
  16->24
  24->32
flow_modes:
  constrained_window_flow
  one_step_local_flow
probes:
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple
  existing_low diagnostic only
  full_state_hash identity control only optional
workers: 18
promotion_enabled: false
holdout_detection_enabled: false
candidate_detection_enabled: false or provisional_design_only
```

The run should prioritize B0-viable metric families:

```text
bottleneck
support_turnover
transition_matrix
window_stability
```

Growth and branch/merge may be emitted as diagnostics but should not drive Phase B readiness because they did not survive B0 viability.

### 2.2 Adaptive queue order

Submit jobs in this order so partial results remain useful if time expires:

```text
1. all 10 groups, fresh_seeds_per_group=4, start_samples=4
2. all 10 groups, fresh_seeds_per_group=4 additional, start_samples=4
3. all 10 groups, all seeds, start_samples=8
4. top design groups by provisional recurrence/excess, start_samples=16
5. optional diagnostic full_state_hash / existing_low expansion
```

This ensures the run gets breadth over groups/seeds before deeper start sampling.

### 2.3 Optional budget use if run is much faster than expected

If the full primary batch completes with more than 2 hours remaining, use remaining time for design-set-only robustness, in this order:

```text
A. add fresh seeds up to 12 per design group
B. add start_samples=16 for all design groups
C. add repeated control replicates for horizon_order and probe_marginal controls
D. add asymmetry_shuffled_transform_control if implemented
E. add roughness_resampled_transform_control if implemented
```

Do not score holdout with leftover time.

Do not run n=6.

Do not expand alphabet.

## 3. Phase B recurrence questions

Primary question:

```text
Do frontier-transform profiles recur across seeds/starts/windows above computed controls?
```

Secondary questions:

```text
Which metric families recur?
Which flow modes carry recurrence?
Which horizon windows carry recurrence?
Are effects directionally stable?
Are effects above matched controls or control-equivalent?
Does recurrence depend on one probe/binning family?
Is recurrence path-dependent but above matched recurrence controls?
```

## 4. Recurrence definitions

Use fractional recurrence, not all-or-nothing recurrence.

Required recurrence rates:

```text
seed_recurrence_rate
start_recurrence_rate
window_recurrence_rate
metric_family_recurrence_rate
flow_mode_recurrence_rate
probe_recurrence_rate
control_excess_recurrence_rate
```

Suggested default gates:

```text
seed_recurrence_rate >= 0.60
start_recurrence_rate >= 0.50
window_recurrence_rate >= 0.40
control_excess_recurrence_rate >= 0.50
at least 2 metric families recurrent
at least 1 recurrent family must be one of:
  transition_matrix
  support_turnover
  bottleneck
```

Report exact rates even when gates fail.

## 5. Effect direction handling

Do not assume positive effects are better.

For every metric family and control comparison, report:

```text
signed_effect_size_mean
signed_effect_size_median
absolute_effect_size_mean
absolute_effect_size_median
effect_direction_mode
effect_direction_stability
percent_design_above_control
percent_design_below_control
percent_control_equivalent
```

Direction classes:

```text
stable_design_above_control
stable_design_below_control
mixed_direction
control_equivalent
```

A stable negative effect can count as recurrent if it exceeds controls and is stable across seeds/starts/windows.

## 6. Required controls

Phase B must compute at least:

```text
matched_fakeout_window_control
neutral_generated_window_control
frontier_size_matched_window_control
horizon_order_shuffled_control
start_shuffled_control
probe_marginal_window_control
```

Required explicit status:

```text
constraint_shuffled_transform_control: computed or not_available
asymmetry_shuffled_transform_control: computed or not_available
roughness_resampled_transform_control: computed or not_available
```

If `constraint_shuffled_transform_control` remains unavailable, the final report must say that constraint-mechanism causal claims remain blocked.

## 7. Matched recurrence controls

For recurrence itself, not only metric values, compute matched recurrence controls:

```text
matched_fakeout_recurrence
neutral_recurrence
start_shuffled_recurrence
horizon_order_shuffled_recurrence
frontier_size_matched_recurrence
probe_marginal_recurrence
```

Required metrics:

```text
observed_recurrence_rate
control_recurrence_mean
control_recurrence_std
recurrence_excess
recurrence_percentile_vs_controls
control_count
weak_control_flag
```

A design-set recurrence is interesting only if:

```text
recurrence_excess > 0
and recurrence_percentile_vs_controls is high enough under frozen thresholds
```

Suggested descriptive threshold:

```text
recurrence_percentile_vs_controls >= 0.80
```

This is not a discovery gate. It is a Phase C readiness indicator.

## 8. Output files

Required outputs:

```text
rfs_mb0_frontier_transform_phase_b_10h_report.md
phase_b_run_config.json
phase_b_job_manifest.csv
phase_b_progress_checkpoints.csv
phase_b_design_metric_rows.csv
phase_b_design_control_rows.csv
phase_b_directional_effects.csv
phase_b_metric_family_recurrence.csv
phase_b_flow_mode_recurrence.csv
phase_b_window_recurrence.csv
phase_b_seed_start_recurrence.csv
phase_b_matched_recurrence_controls.csv
phase_b_recurrence_excess.csv
phase_b_control_quality_audit.csv
phase_b_no_target_audit.csv
phase_b_holdout_status.csv
phase_b_phase_c_readiness.csv
errors.csv
status.json
output_manifest.json
```

## 9. Report sections

The final report must include:

```text
1. Claim boundary
2. Cleanup/smoke result
3. Run shape and wall-clock usage
4. Flow-mode and no-target audit
5. Metric family recurrence
6. Effect direction stability
7. Matched transform controls
8. Matched recurrence controls
9. Path-dependence profile
10. Phase C readiness decision
11. Holdout status
12. Limitations
13. Output manifest
```

## 10. Phase C readiness decision

Emit exactly one decision class:

```text
phase_c_ready
phase_c_blocked_no_recurrence
phase_c_blocked_control_equivalent
phase_c_blocked_direction_unstable
phase_c_blocked_window_fragile
phase_c_blocked_probe_dependent
phase_c_blocked_controls_weak
phase_c_blocked_incomplete_run
phase_c_blocked_holdout_contaminated
```

### 10.1 Phase C ready

Set `phase_c_ready` only if all are true:

```text
1. run status is COMPLETED or PARTIAL_TIME_LIMIT_REACHED with enough completed primary jobs
2. holdout_scoring_count = 0
3. at least two B0-viable metric families recur above matched recurrence controls
4. recurrence appears across at least two fresh seeds per group on average
5. recurrence appears across at least two start counts or start subsets
6. recurrence is not confined to a single horizon window unless explicitly classified window-local
7. direction stability is not mixed/noisy
8. control quality is not weak for the supporting metric families
9. identity-control/full_state_hash is not required for the signal
```

### 10.2 Phase C blocked

Block Phase C if:

```text
recurrence is control-equivalent
recurrence depends only on placeholder probe_marginal controls
recurrence appears only in diagnostic/identity probes
recurrence is single-window only and below controls
run is incomplete before primary breadth completes
holdout was scored or contaminated
```

## 11. Cleanup notes for Codex

Before implementing the large runner, inspect B0 code for these issues:

```text
1. control_names.add('frontier_size_matched_window_control') should not mask missing outputs.
   Phase B must derive present controls from actual emitted rows.

2. probe_marginal_window_control is currently placeholder-like.
   Either implement real marginal re-pairing or mark control_quality=placeholder.

3. branch_merge_metrics currently uses edge counts from audit rather than the original branch/merge distribution.
   Keep branch/merge diagnostic only unless repaired.

4. full_state_hash should remain identity control only.
   It must not support Phase C readiness.

5. constraint_shuffled_transform_control remains not_available.
   Do not make constraint-causal claims without it.
```

## 12. Budget rationale

The 10h budget should be spent on:

```text
more fresh seeds
more starts
more control replicates
matched recurrence controls
```

not on:

```text
larger substrate
alphabet expansion
holdout testing
n=6
new endpoint probes
path metrics
identity/agent classification
```

The goal is to determine whether the Phase A/B0 frontier-transform signal has design-set recurrence above controls.

## 13. Bottom line

This is the first large run after the frontier-transform instrument passed semantic repair.

Run big enough to answer the design-set recurrence question, but keep the epistemic gates intact:

```text
design set only
frozen windows
B0-viable metrics
matched controls
fractional recurrence
signed effects
holdout untouched
no promotion
```

If Phase B passes, the next run is frozen holdout Phase C.

If Phase B fails, write a frontier-transform measurement-limits note rather than scaling search.

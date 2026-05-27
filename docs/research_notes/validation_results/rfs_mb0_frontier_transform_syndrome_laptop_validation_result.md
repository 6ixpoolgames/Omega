# RFS-MB0 Frontier-Transform Syndrome Audit Laptop Validation Result

Date: 2026-05-28

Runner changes validated:

```text
omega/rfs_mb0_future_landscape/run_frontier_transform_phase_b.py
omega/rfs_mb0_future_landscape/run_frontier_transform_syndrome_audit.py
omega/rfs_mb0_future_landscape/run_focused_boundary_recurrence.py
```

Local outputs:

```text
results/local_runs/20260528_laptop_frontier_transform_phase_b_validation_192jobs/
results/local_runs/20260528_laptop_frontier_transform_stage_a_validation_192jobs/
```

## Claim Boundary

This was a laptop-local runner and output-contract validation. It was not a
scientific Phase B rerun, holdout validation, candidate promotion, mechanism
dependency result, Omega detection, agency detection, identity detection, or
value detection.

The historical Phase B/source CSV directories are not tracked in this clone.
Therefore this validation regenerated a small fixture-like input bundle under
`results/local_runs/` to exercise the Phase B and Stage A audit contracts.

## Hardware Boundary

This run used the current laptop profile, not the main desktop profile:

```text
machine role: laptop
hostname: DESKTOP-LVVT7H7
CPU: Intel i7-1165G7, 8 logical processors
GPU: Intel Iris Xe integrated; CUDA unavailable
workers: 7
job_batch_size: 2
BLAS/OpenMP-style thread caps: 1
```

Do not copy these settings to the main desktop instance.

## Run Shape

Phase B validation command shape:

```text
groups: 6
design_groups: 4
fakeout_groups: 2
neutral_anchors: 2
fresh_seeds_per_group: 4
start_samples_list: 4,8
probes:
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple
  existing_low
  full_state_hash
workers: 7
job_batch_size: 2
skip_row_level_effect_csv: true
skip_full_control_csv: false
```

`phase_b_row_level_control_effects.csv` was deliberately skipped because Stage
A currently consumes `phase_b_design_control_rows.csv`, and the row-level effect
CSV is a duplicate diagnostic table for this validation purpose.

## Phase B Validation Outcome

```text
status: COMPLETED
jobs_completed: 192 / 192
metric_rows: 14336
control_rows: 1245559
errors: 0
elapsed_seconds_in_status: 65.221
holdout_scoring_count: 0
phase_c_ready: 0
decision_class: phase_c_blocked_no_recurrence
```

The largest emitted artifact was:

```text
phase_b_design_control_rows.csv: about 745 MB
```

This confirms that final CSV materialization is now the dominant cost for this
local validation scale. Worker execution finished quickly; finalization and
Stage A CSV ingestion dominated wall time.

## Stage A Validation Outcome

```text
status: COMPLETED
metric_rows: 14336
control_rows: 1245559
syndrome_component_rows: 118272
errors: 0
elapsed_seconds: 470.003
new_systems_generated: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

Stage A emitted the required postmortem, syndrome scoring, syndrome smoke,
multiplicity, readiness, status, and manifest files.

Readiness row:

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
missing_mechanism_control_families:
  asymmetry
  constraint
  roughness
holdout_scoring_count: 0
```

This readiness result must be interpreted only as evidence that the Stage A
selection path executes on a nontrivial local fixture. It is not evidence that
the historical Phase B branch contains these syndromes.

## Control And Mechanism Status

Computed controls were emitted for:

```text
start_shuffled_control
horizon_order_shuffled_control
matched_fakeout_window_control
neutral_generated_window_control
frontier_size_matched_window_control
```

`probe_marginal_window_control` remained `placeholder`.

Mechanism controls remained unavailable in the Phase B runner outputs:

```text
constraint_shuffled_transform_control
asymmetry_shuffled_transform_control
roughness_resampled_transform_control
```

This is expected for the Phase B runner. The separate `mechanism_controls.py`
utility has smoke-tested constructors, but it is not yet integrated into a
Stage B mechanism-control rerun.

## Implementation Notes

This validation also exercised two CSV hardening changes:

```text
read_csv now tolerates UTF-8 BOM headers in the shared frontier-transform path
write_csv now uses csv.writer with a larger file buffer instead of DictWriter
```

The faster writer helps, but the full-control CSV remains large. The next
material speedup should be structural:

```text
stream large control rows to disk during worker collection, or
write a compact Stage A control-value table instead of a full debug control CSV
```

## Compact Stage A Control-Value Follow-Up

A follow-up implementation added:

```text
phase_b_stage_a_control_values.csv
```

This compact table carries only the fields Stage A needs for control-value
distributions:

```text
control_name
control_quality
control_status
metric_name
control_value
probe_key
flow_mode
true_window
window
```

Stage A now prefers this compact table when present, and falls back to
`phase_b_design_control_rows.csv` for older runs.

Validation on the same 192-job laptop Phase B output:

```text
full debug control CSV: 744725521 bytes
compact Stage A control CSV: 172520869 bytes
compact rows: 1245364
```

Equivalence check:

```text
phase_b_syndrome_readiness.csv: identical
phase_b_syndrome_smoke.csv: identical
phase_b_syndrome_vs_controls.csv: identical
phase_b_syndrome_component_scores.csv: identical
```

Stage A runtime on the same Phase B data:

```text
full-control source: 470.003 seconds
compact-control source: 403.329 seconds
```

A separate compact Phase B rerun with `--skip-full-control-csv` also completed:

```text
jobs_completed: 192 / 192
metric_rows: 14336
control_rows: 1245559
stage_a_control_value_rows: 1245364
full_control_csv_written: 0
phase_b_design_control_rows.csv: 46 bytes sentinel
phase_b_stage_a_control_values.csv: 172517680 bytes
errors: 0
```

The compact contract therefore does what it was intended to do: Stage A no
longer requires the full debug control CSV, and equivalent syndrome outputs can
be produced from a much smaller input. The single compact Phase B rerun was not
faster wall-clock than the earlier full-control run, so the next performance
target is Stage A scoring/grouping itself rather than only CSV emission.

## Cached Stage A Control Summaries

A second follow-up optimized Stage A scoring by summarizing each control bucket
once:

```text
control_count
control_mean
control_std
sorted control values for percentile lookup
```

Stage A also filters compact control rows to preregistered syndrome metrics
before building those summaries.

Validation on the same compact 192-job Phase B output:

```text
pre-cache compact Stage A elapsed: 456.399 seconds
cached compact Stage A elapsed: 8.400 seconds
syndrome_component_rows: 118272
```

Equivalence check:

```text
phase_b_syndrome_readiness.csv: identical
phase_b_syndrome_smoke.csv: identical
phase_b_syndrome_component_scores.csv: identical
```

This removes the main Stage A scoring bottleneck for laptop-scale validation.

## Recommendation

The implementation is ready for external audit and for a real Stage A read-only
audit when the historical Phase B CSV directory is available.

Do not treat this laptop validation as a substitute for the historical Phase B
postmortem. Do not open holdout Phase C from this result.

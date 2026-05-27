# RFS-MB0 Regenerated Phase B Full-Control + Stage A Syndrome Audit Run Spec

Status: immediate Codex run spec after Stage A syndrome audit optimization/laptop validation

Purpose: regenerate a clean optimized Phase B design-set output with full controls, then run the read-only Stage A syndrome/postmortem audit against that regenerated output. This replaces reliance on the historical unoptimized Phase B directory and avoids the laptop fixture caveat.

This follows:

```text
docs/RFS_MB0_FRONTIER_TRANSFORM_PHASE_B_10H_DESIGN_RECURRENCE_SPEC.md
docs/RFS_MB0_FRONTIER_TRANSFORM_SYNDROME_AND_MECHANISM_CONTROL_AUDIT_SPEC.md
docs/RFS_MB0_FRONTIER_TRANSFORM_SYNDROME_AUDIT_ADDENDUM.md
docs/research_notes/validation_results/rfs_mb0_frontier_transform_syndrome_laptop_validation_result.md
```

Recent validation result:

```text
The optimized Phase B and Stage A runners completed on a laptop-local fixture.
That validated the output contract and scoring path, but not the historical scientific result.
```

This run should now use the real design-set selection/source inputs and emit a regenerated Phase B directory with full controls.

## 0. Claim boundary

This run is not:

```text
holdout validation
candidate promotion
Omega detection
agency detection
identity detection
value detection
mechanism-dependency confirmation
n=6 transfer
alphabet expansion
```

Allowed claims:

```text
The optimized Phase B full-control output regenerated successfully.
The read-only Stage A syndrome audit did or did not find preregistered joint syndromes above marginal-preserving controls.
The next mechanism-control rerun is or is not warranted.
```

## 1. Run overview

Run two linked stages:

```text
Stage 1:
  regenerate optimized Phase B design-set output with full controls

Stage 2:
  run Stage A read-only postmortem + syndrome audit against the regenerated Phase B output
```

Stage 2 must consume Stage 1 output directly.

Do not generate new systems in Stage 2.

Do not score holdout in either stage.

## 2. Stage 1: regenerated optimized Phase B output

### 2.1 Output directory

Use a new output path:

```text
results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls/
```

Do not overwrite:

```text
results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_b_10h/
```

### 2.2 Required runner

Use:

```text
omega/rfs_mb0_future_landscape/run_frontier_transform_phase_b.py
```

with the optimized CSV path.

### 2.3 Required controls

Full controls means:

```text
phase_b_design_control_rows.csv must be fully written
```

Do not use:

```text
--skip-full-control-csv
```

It is acceptable and preferred to use:

```text
--skip-row-level-effect-csv
```

because Stage A consumes the full design control rows, not the duplicate diagnostic row-level effect table.

### 2.4 Recommended Phase B profile

Use the same primary design-set profile as the prior 10h run unless Codex finds a clear reason to reduce it:

```text
design_groups: 10
fresh_seeds_per_group: 8
start_samples_list: 4,8,16
flow_modes:
  constrained_window_flow
  one_step_local_flow
probes:
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple
  existing_low
  full_state_hash
windows:
  canonical 7 windows
workers: desktop profile, usually 18
job_batch_size: 4 unless profiling says otherwise
max_runtime_seconds: 36000
shutdown_cushion_seconds: 900
skip_row_level_effect_csv: true
skip_full_control_csv: false
```

Expected scale, based on prior run:

```text
jobs_requested: about 1120
metric_rows: about 134400
control_rows: about 13M
```

The optimized writer should make this practical within the time budget.

### 2.5 Required Stage 1 outputs

```text
phase_b_run_config.json
phase_b_job_manifest.csv
phase_b_progress_checkpoints.csv
phase_b_design_metric_rows.csv
phase_b_design_control_rows.csv
phase_b_row_level_control_effects.csv  # may be skipped marker, not full duplicate
phase_b_directional_effects.csv
phase_b_metric_family_recurrence.csv
phase_b_design_recurrence_summary.csv
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

### 2.6 Stage 1 acceptance criteria

```text
status: COMPLETED or PARTIAL_TIME_LIMIT_REACHED after primary breadth complete
errors: 0
holdout_scoring_count: 0
phase_b_design_metric_rows.csv row_count > 0
phase_b_design_control_rows.csv full control rows, not skipped marker
phase_b_directional_effects.csv row_count > 0
phase_b_matched_recurrence_controls.csv row_count > 0
output_manifest.json present
```

If `phase_b_design_control_rows.csv` is skipped, Stage 2 is blocked.

## 3. Stage 2: read-only Stage A syndrome audit

### 3.1 Output directory

Use:

```text
results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_a_regenerated_full_controls/
```

### 3.2 Required runner

Use:

```text
omega/rfs_mb0_future_landscape/run_frontier_transform_syndrome_audit.py
```

Input must be:

```text
results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls/
```

### 3.3 Stage A strict constraints

Stage A must be read-only over the regenerated Phase B rows.

Required status fields:

```text
new_systems_generated: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

Do not run mechanism controls in Stage A.

Do not run alphabet-shape diagnostics in Stage A.

### 3.4 Syndrome guardrails

Implement the addendum as binding.

Required:

```text
syndrome_manifest.json written before scoring
metric-native syndrome IDs
selection_mode = preregistered for readiness-eligible syndromes
exploratory syndromes, if any, readiness_allowed = false
component_marginal_preserving_syndrome_control emitted
component ablation emitted for apparent positives
full_state_hash and existing_low excluded from positive readiness
```

Do not let informal syndrome names appear as decision classes.

### 3.5 Marginal-preserving control replicates

Use:

```text
replicates: 500 preferred
minimum: 100
```

If runtime is unexpectedly heavy, 100 is acceptable for the first regenerated audit, but the report must say so.

### 3.6 Required Stage 2 outputs

```text
syndrome_manifest.json
phase_b_postmortem_report.md
phase_b_postmortem_control_match_decomposition.csv
phase_b_postmortem_top_control_equivalent_rows.csv
phase_b_postmortem_control_match_by_control_type.csv
phase_b_postmortem_flow_mode_decomposition.csv
phase_b_postmortem_window_decomposition.csv
phase_b_postmortem_probe_dependency.csv
phase_b_syndrome_component_scores.csv
phase_b_syndrome_smoke.csv
phase_b_syndrome_vs_controls.csv
phase_b_syndrome_marginal_preserving_controls.csv
phase_b_syndrome_component_ablation.csv
phase_b_syndrome_multiplicity_audit.csv
phase_b_syndrome_readiness.csv
status.json
output_manifest.json
errors.csv
```

### 3.7 Stage 2 acceptance criteria

```text
status: COMPLETED
errors: 0
new_systems_generated: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
syndrome_manifest.json exists
phase_b_syndrome_marginal_preserving_controls.csv exists and has rows
phase_b_syndrome_component_ablation.csv exists
phase_b_syndrome_readiness.csv exists
full_state_hash/existing_low excluded from readiness
```

## 4. Decision after Stage 2

### 4.1 Mechanism-control Stage B allowed

Allow a small Stage B mechanism-control smoke only if Stage A shows at least one preregistered metric-native syndrome with:

```text
observed_joint_rate > marginal_preserving_control_mean
joint_rate_percentile >= 0.80
not single-component-driven
not full_state_hash dependent
not existing_low dependent
not confined to placeholder controls
```

or if Stage A explicitly concludes:

```text
missing mechanism controls are the dominant uncertainty after marginal-preserving controls
```

### 4.2 Stage B blocked

Block mechanism-control rerun if:

```text
all preregistered syndromes are marginal-control-equivalent
or apparent positives are single-component-driven
or positives depend on full_state_hash/existing_low
or Stage A did not emit marginal-preserving controls
or Stage A used exploratory syndromes for readiness
```

### 4.3 Holdout remains blocked

Regardless of Stage A outcome:

```text
Do not open holdout Phase C from this run.
```

A holdout run would require a frozen syndrome definition and a separate spec.

## 5. Recommended command profile notes

Use desktop settings, not the laptop validation profile.

Laptop validation used:

```text
workers: 7
job_batch_size: 2
thread caps: 1
```

For desktop/main run, use the established desktop worker profile unless machine constraints say otherwise:

```text
workers: 18
job_batch_size: 4
thread caps: keep BLAS/OpenMP-style caps conservative if multiprocessing is used
```

## 6. Reporting note

Write a retained result note after both stages:

```text
docs/research_notes/validation_results/rfs_mb0_frontier_transform_regenerated_phase_b_stage_a_result.md
```

Required sections:

```text
1. Claim boundary
2. Regenerated Phase B run shape
3. Stage 1 output and control completeness
4. Stage A syndrome audit shape
5. Postmortem: which controls matched recurrence
6. Syndrome smoke result
7. Marginal-preserving control result
8. Component ablation result
9. Readiness decision for mechanism-control Stage B
10. Why holdout remains blocked
11. Output paths
```

## 7. Bottom line

Run the optimized full-control regeneration, then run read-only Stage A on that regenerated output.

The key question is:

```text
Do preregistered metric-native joint signed frontier-transform syndromes beat marginal-preserving controls on a real regenerated Phase B output?
```

If yes, run a small mechanism-control smoke next.

If no, do not mine more syndromes; write the measurement-limit interpretation.

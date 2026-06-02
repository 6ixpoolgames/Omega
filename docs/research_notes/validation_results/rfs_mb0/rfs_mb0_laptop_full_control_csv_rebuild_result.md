# RFS-MB0 Laptop Full-Control CSV Rebuild Result

Date: 2026-05-28

## Claim Boundary

This was a laptop-local upstream provenance rebuild followed by a full-control
Phase B CSV regeneration. It was not a historical desktop rerun, holdout
validation, candidate promotion, Omega detection, agency detection, identity
detection, value detection, n=6 transfer, or mechanism-dependency confirmation.

The original historical source CSVs were not present in this checkout, so the
laptop regenerated the prerequisite source chain from repo code. The resulting
Phase B output is therefore a real local regeneration with full controls, but it
is not the historical full-breadth design-set result.

## Hardware Boundary

Run profile:

```text
machine role: laptop
CPU: Intel Core i7-1165G7
logical processors: 8
GPU: Intel Iris Xe integrated
CUDA available: false
workers: 7
job_batch_size: 2
BLAS/OpenMP-style thread caps: 1
```

Do not copy these settings to the main desktop instance.

## Upstream Rebuild

Primary wrapper:

```text
scripts/run_laptop_full_csv_rebuild.py
```

Wrapper status:

```text
status: COMPLETED
elapsed_seconds: 3889.176
finalization_reason: phase_b_full_control_csv_written
```

Primary upstream outputs:

```text
results/rfs_mb0_relation_atlas/20260528_laptop_relation_atlas_batch_rebuild/
results/rfs_mb0_relation_atlas/20260528_laptop_relation_generator_phenotype_repair/
results/rfs_mb0_relation_atlas/20260528_laptop_support_distribution_taxonomy/
results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep/
results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/
results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/
```

The primary local source chain completed without runner errors, but selected
only one focused group:

```text
focused_groups_selected: 1
corrected_groups: 1
```

## Phase B Full-Control CSV

Output path:

```text
results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls/
```

Phase B status:

```text
status: COMPLETED
finalization_reason: all_jobs_completed
errors: 0
holdout_scoring_count: 0
jobs_completed: 192 / 192
metric_rows: 17920
control_rows: 1250183
stage_a_control_value_rows: 1249988
full_control_csv_written: 1
row_level_effect_csv_written: 0
elapsed_seconds: 176.960
```

Key file sizes:

```text
phase_b_design_control_rows.csv: 769877956 bytes
phase_b_stage_a_control_values.csv: 173078602 bytes
phase_b_design_metric_rows.csv: 53017950 bytes
```

SHA-256 hashes:

```text
phase_b_design_control_rows.csv:
  C1E39ACC403B279C1800492559A214C2407ACAFBB6251342A0991EF0CB40E8A3
phase_b_stage_a_control_values.csv:
  E4095BD2EEB093CE16415F6165486ABF3E14CF37457A40645AEF57473235D4E2
phase_b_design_metric_rows.csv:
  F616CFE8B5EE5067E8A31AE726862CCC3EDCAF623D78E6A0A94C4F3157CBF528
```

The full debug control CSV was written. `phase_b_row_level_control_effects.csv`
was intentionally emitted only as the skipped marker because Stage A consumes
the full design controls or compact Stage A control-value table, not the
duplicate row-level diagnostic table.

## Breadth Limitation

The regenerated laptop source did not reproduce the historical breadth implied
by the desktop Phase B spec. The intended historical-scale expectation was about
1120 jobs and about 13M control rows. The local rebuild produced a valid
full-control CSV for one focused group, yielding 192 jobs and about 1.25M
control rows.

This means:

```text
full-control CSV materialization: satisfied
historical full-breadth design-set regeneration: not satisfied
```

## Expanded Attempts

An expanded 24-anchor boundary sweep was run from the primary taxonomy output:

```text
results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep_laptop_expanded24/
```

It completed:

```text
anchors_selected: 24
sweep_jobs_completed: 576 / 576
errors: 0
fresh_seed_recurrence_class counts:
  seed_recurrent_fakeout_like: 23
  seed_mixed_or_boundary: 1
```

The associated extraction still selected only one focused group.

A larger upstream expansion was then attempted:

```text
results/rfs_mb0_relation_atlas/20260528_laptop_relation_generator_phenotype_repair_expanded80/
results/rfs_mb0_relation_atlas/20260528_laptop_support_distribution_taxonomy_expanded48/
results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep_laptop_expanded48/
```

The expanded taxonomy reached the time limit after useful partial output:

```text
status: TIME_LIMIT_REACHED
jobs_completed: 1259 / 1344
metric_rows_completed: 48384
errors: 0
```

The expanded boundary sweep also reached the time limit:

```text
status: TIME_LIMIT_REACHED
sweep_jobs_completed: 369 / 864
sweep_rows_completed: 16056
errors: 0
fresh_seed_recurrence_class counts:
  insufficient_fresh_seeds: 36
```

Because the expanded boundary sweep did not complete enough fresh seeds, its
focused extraction selected zero groups. No expanded Phase B was launched from
that partial source.

## Readiness Decision

The generated full-control CSV is suitable for auditing the optimized writer and
Stage A ingestion path on laptop-regenerated source data. It should not be used
as the scientific substitute for the missing historical desktop Phase B source
chain.

Recommended next step:

```text
Sync the original desktop source CSVs if the goal is historical full-breadth
Phase B regeneration.
```

If a self-contained laptop rebuild is still preferred, reserve a longer window
for the expanded upstream chain, especially completing the boundary sweep fresh
seeds before launching Phase B.

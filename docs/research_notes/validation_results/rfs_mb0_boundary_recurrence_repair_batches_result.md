# RFS-MB0 Boundary Recurrence Repair Batches Result

Date: 2026-05-27  
Spec: `docs/RFS_MB0_BOUNDARY_RECURRENCE_REPAIR_AND_FOCUSED_PASS_SPEC.md`

## Claim Boundary

This was a runner/reporting repair plus focused recurrence pass. It does not
claim Omega, agency, identity, value, viability, path-process detection, stable
candidate bands, n=6 transfer, or scientific-gate passage.

## Batch 1: Reporting Repair

Script:

```text
omega/rfs_mb0_future_landscape/run_boundary_recurrence_repair.py
```

Output:

```text
results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/
```

Purpose:

```text
Read the interrupted boundary sweep and produce explicit audit tables before
any new compute.
```

Result:

```text
status: COMPLETED
source_status: RUNNING
source_sweep_rows: 187560
focused_groups_selected: 20
local_pre_control_candidate_like_rows: 44388
local_candidate_like_rows_that_are_saturated: 0
probe_role_recurrence_summary rows: 96
```

The audit repaired the ambiguous terminology from the interrupted run:

```text
local/pre-control candidate-like rows are not stable candidates
matched-control candidate-like rows were not computed in the local sweep
band-level recurrence must be separated from row-level candidate-like labels
```

## Batch 2: Tiny Focused Smoke

Script:

```text
omega/rfs_mb0_future_landscape/run_focused_boundary_recurrence.py
```

Output:

```text
results/rfs_mb0_relation_atlas/20260527_focused_boundary_recurrence_smoke/
```

Run shape:

```text
groups: 4
fresh_seeds_per_group: 2
workers: 18
jobs_requested: 80
jobs_completed: 80
metric_rows: 3960
errors: 0
status: COMPLETED
wall_clock_seconds: 4.4
```

Result:

```text
evidence_probe_recurrent_groups: 4 / 4
non_saturation_evidence_probe_recurrent_groups: 4 / 4
```

This smoke validated the focused runner and justified a scaled focused pass.

## Batch 3: Scaled Focused Pass

Output:

```text
results/rfs_mb0_relation_atlas/20260527_focused_boundary_recurrence_scaled/
```

Run shape:

```text
groups: 20
fresh_seeds_per_group: 4
workers: 18
jobs_requested: 800
jobs_completed: 800
metric_rows: 39600
errors: 0
status: COMPLETED
wall_clock_seconds: 44.6
```

Result:

```text
evidence_probe_recurrent_groups: 20 / 20
non_saturation_evidence_probe_recurrent_groups: 20 / 20
clean recurrent boundary candidates: 0 / 20
recommended_group_class: evidence_probe_recurrent_but_probe_limited for all 20
measurement_limits_note_required: true
```

## Interpretation

The repair/focused workflow worked technically:

```text
no final status left RUNNING
workers set to 18 for compute batches
focused outputs written
candidate-like terminology split
probe roles separated
saturation decomposition written
focused group recurrence summarized
```

Scientifically, the result is narrower:

```text
fresh-seed recurrent boundary groups do show evidence-probe recurrence
the recurrence is non-saturation by the row-level saturation flag
but every scaled focused group remains probe-limited
clean recurrent boundary candidates remain zero
```

## Decision

Do not run n=6.

Do not run another broader atlas yet.

Write and use the measurement-limits note:

```text
docs/research_notes/validation_design/rfs_mb0_boundary_recurrence_measurement_limits.md
```

The current branch has found recurrence in selected boundary groups, but the
present probe/detector stack cannot yet establish clean cross-probe recurrent
support/distribution deformation.


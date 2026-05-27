# RFS-MB0 Detector Instrumentation Repair Result

Date: 2026-05-27  
Spec: `docs/RFS_MB0_DETECTOR_INSTRUMENTATION_REPAIR_SPEC.md`  
External audit: `C:\Users\paolo\Desktop\Echo\Omega\Handoff files\claude bug report.txt`

## Claim Boundary

This was an instrumentation repair and exact focused rerun. It does not claim
Omega, agency, identity, value, viability, path-process detection, n=6 transfer,
stable candidate bands, or scientific-gate passage.

## Repairs Implemented

Shared detector repairs:

```text
support_ceiling_flag now means support_fraction >= 0.90 only
support_floor_flag now captures support_fraction <= 0.05
support_extreme_flag remains diagnostic
support_regime_class added
support-aware deformation_score_csv added
```

Focused-run repairs:

```text
probe_limit_decomposition.csv
probe_limit_reason_summary.csv
probe_axis_recurrence_summary.csv
deformation_score_decomposition.csv
focused_group_selection_score_audit.csv
focused_matched_control_bundle.csv
focused_matched_control_rank_effect.csv
focused_margin_sensitivity.csv
corrected_group_classification.csv
corrected_measurement_limits_summary.csv
```

The recurrence gate now requires independent probe axes:

```text
coordinate_axis + constraint_axis
```

instead of merely two evidence probes.

## Smoke

Output:

```text
results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_smoke/
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
```

Corrected result:

```text
independent_axis_recurrent_but_collision_limited: 4
```

## Exact 20-Group Rerun

Output:

```text
results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/
```

Run shape:

```text
groups: same 20 focused groups
fresh_seeds_per_group: 4
workers: 18
jobs_requested: 800
jobs_completed: 800
metric_rows: 39600
errors: 0
status: COMPLETED
wall_clock_seconds: 48.1
```

Corrected group classes:

```text
independent_axis_recurrent_but_collision_limited: 16
weak_control_bundle_recurrence: 4
clean_recurrent_boundary_candidate: 0
sparse_regime_recurrent_candidate_pending_floor_audit: 0
```

Probe-limit reason rows:

```text
collision_limited: 22789
identity_like_limited: 1517
support_ceiling_limited: 5692
support_floor_limited: 5994
none: 14851
```

Matched-control rank/effect classes:

```text
matched_control_supported_local_candidate: 176
matched_control_equivalent: 367
weak_control_bundle: 12
```

## Interpretation

The bug audit was directionally correct: the prior generic
`evidence_probe_recurrent_but_probe_limited` label was too coarse. After repair,
the main limitation is not generic probe limitation. It is mostly:

```text
collision-limited recurrence
plus a smaller weak-control-bundle class
```

The support floor/ceiling split also matters for interpretability. Sparse rows
are no longer automatically counted as saturation ceiling rows.

However, the repair did not produce clean recurrent boundary candidates. The
same 20 focused groups remain measurement-limited after corrected
instrumentation.

## Decision

Measurement limit is confirmed, but now with a sharper diagnosis:

```text
do not run n=6
do not run broader breadth
repair evidence probes to reduce collision without becoming identity-like
then rerun a small focused pass only if probe collision is reduced
```


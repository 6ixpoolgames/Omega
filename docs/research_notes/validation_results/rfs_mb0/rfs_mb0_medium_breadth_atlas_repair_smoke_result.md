# RFS-MB0 Medium-Breadth Atlas Runner Repair Smoke Result

Date: 2026-05-26

Primary local output:

```text
results/rfs_mb0_relation_atlas/20260526_medium_breadth_atlas_repair_smoke/
```

Primary report:

```text
results/rfs_mb0_relation_atlas/20260526_medium_breadth_atlas_repair_smoke/medium_breadth_support_distribution_atlas_report.md
```

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_MEDIUM_BREADTH_ATLAS_RUNNER_REPAIR_SPEC.md
```

## Run Shape

```text
anchors selected: 6
fresh_seeds_per_variant: 2
start_samples: 3, 8
horizons: 0, 1, 2, 4, 8, 12, 16, 24, 32
workers requested: 18
sweep jobs requested: 720
sweep jobs completed: 720
sweep rows completed: 35640
rank/effect rows: 39424
errors: 0
wall_clock_seconds: 229.5
promotion_enabled: false
```

This was intentionally a smaller repair smoke, not a broadened atlas.

## n=6 Transfer

n=6 transfer was intentionally skipped for this small repair run.

```text
transfer_status: skipped_budget
jobs_requested: 0
jobs_completed: 0
n6_result_rows: 0
```

This should not be interpreted as a completed n=6 transfer check.

## Acceptance Check

The repair smoke satisfies the requested output-contract checks:

```text
errors = 0
output_manifest.json present
required_answer_provenance.csv present
n6_transfer_summary.csv explicit
atlas_band_classification_audit.csv present
transition_class_summary.csv present
stable_candidate_blocker_summary.csv present
saturation_boundary_audit.csv present
probe_resolution_boundary_audit.csv present
fresh_seed_recurrence_audit.csv present
candidate_blocker_summary.csv present
```

Output manifest row counts confirm all required files are present.

## Repair Readout

The fakeout-to-candidate inconsistency is now resolved by splitting concepts:

```text
fakeout_to_candidate_transition_graph_count: 1 / 30
fakeout_to_candidate_band_level_count: 4 / 6
fakeout_to_candidate_fresh_seed_recurrent_count: 0 / 30
fakeout_to_candidate_any_recurred: true
```

Stable candidate blockers:

```text
candidate_rate_below_threshold: 6
probe_recurrence_below_threshold: 6
probe_resolution_boundary_present: 1
saturation_boundary_present: 4
start_recurrence_below_threshold: 1
```

Boundary audits:

```text
saturation_boundary_audit rows: 17453
probe_resolution_boundary_audit rows: 17146
```

## Interpretation

This is a runner/reporting repair success. It is not a stronger science result.
The repair makes the medium-breadth atlas bundle auditable enough to support a
follow-up decision.

Recommended next step:

```text
second local sweep or measurement-limits note
```

Rationale: the repaired outputs show that candidate-like behavior exists in
some transition/band-level criteria, but stable candidate blockers are still
dominated by low candidate rate, weak probe recurrence, saturation, and
probe-resolution limits.

## Claim Boundary

Allowed conclusion:

```text
The atlas runner/reporting layer is now auditable, and n=6 transfer status is
explicitly represented.
```

Not allowed:

```text
Omega detected
agency detected
identity detected
valuer detected
viability detected
path-process object detected
scientific gate passed
```

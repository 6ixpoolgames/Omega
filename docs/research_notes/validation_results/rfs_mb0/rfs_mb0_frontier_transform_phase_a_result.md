# RFS-MB0 Frontier-Transform Phase A Result

Date: 2026-05-27

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_FRONTIER_TRANSFORM_INSTRUMENTATION_SPEC.md
```

Run folder:

```text
results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_a/
```

## Claim Boundary

This was frontier-transform Phase A preflight only.

No candidate detection, holdout detection, identity classification, agent classification, value claim, or discovery claim was made.

## Run Shape

```text
workers: 18
job_batch_size: 4
jobs_requested: 160
jobs_completed: 160
row_count: 4480
errors: 0
status: COMPLETED
elapsed_seconds: 3.302
```

The run evaluated canonical horizon windows:

```text
0->1
1->2
2->4
4->8
8->16
16->24
24->32
```

Coarse probes used as bins:

```text
constraint_profile_hash
constraint_violation_count_plus_local_tuple
existing_low
full_state_hash
```

`existing_low` is diagnostic and `full_state_hash` is an identity control. Neither counts toward detection eligibility.

## Main Result

Phase A passed the minimum instrumentation viability criterion.

Viable non-control design-set metric families:

```text
bottleneck
branch_merge
growth
support_turnover
transition_matrix
window_stability
```

The result allows a small Phase B design-set transform recurrence run under frozen metrics and windows.

## Important Caution

This is not a positive MB0 detection.

The design-vs-control descriptive effects are mostly modest. Phase A says the frontier-transform measurement layer is non-degenerate enough to test; it does not say recurrent boundary deformation has cleared controls.

The next run should therefore be small and disciplined:

```text
design set only
holdout untouched
frozen windows
frozen transform metric families
matched transform controls
no promotion beyond design-set recurrence summary
```

## Interpretation

This is the first instrumentation result in several passes that does not immediately collapse into endpoint-probe collision or single-axis constraint-only viability.

That updates the roadmap:

```text
Endpoint quotient repair remains blocked.
Frontier-transform instrumentation is viable enough for Phase B.
Holdout and scale remain blocked until Phase B succeeds.
```

## Decision

Proceed to a small Phase B design-set frontier-transform recurrence run.

Do not score holdout groups yet.

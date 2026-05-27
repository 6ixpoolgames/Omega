# RFS-MB0 Frontier-Transform B0 Control/Flow Repair Result

Date: 2026-05-27

Spec:

```text
docs/RFS_MB0_FRONTIER_TRANSFORM_PHASE_B0_CONTROL_FLOW_REPAIR_SPEC.md
```

Run folder:

```text
results/rfs_mb0_relation_atlas/20260527_frontier_transform_b0/
```

## Claim Boundary

B0 was a control/flow semantic repair pass.

It was not candidate detection, validation, holdout testing, n=6 transfer, identity classification, agent classification, or a value/viability claim.

## Run Shape

```text
workers: 18
job_batch_size: 4
jobs_requested: 160
jobs_completed: 160
metric_rows: 8960
control_rows: 643112
errors: 0
status: COMPLETED
holdout_scoring_count: 0
```

## Repairs Implemented

B0 repaired the main semantic issues identified after Phase A:

```text
silent transition-flow fallback removed
constrained_window_flow separated from one_step_local_flow
no-window-target and skipped-state rates reported
window stability moved away from four-integer sketch JS
metric-vector and real transition/signature distribution stability emitted
computed controls emitted rather than only listed
signed and absolute effects reported
constraint-shuffled control explicitly marked not_available
```

## Readiness Decision

Corrected B0 decision:

```text
decision_class: phase_b_ready
phase_b_ready: 1
silent_fallback_removed: 1
required_controls_present: 1
constraint_shuffled_transform_control_status: not_available
holdout_scoring_count: 0
```

Viable metric families after B0:

```text
bottleneck
support_turnover
transition_matrix
window_stability
```

The corrected branch/merge metrics did not survive viability after the bug fix. Growth also did not survive B0 controls.

## No-Target Audit

No-window-target rates were low and not catastrophic.

The only nonzero mean was:

```text
window 2->4: mean_no_window_target_rate ~= 0.0138
```

All canonical windows had `catastrophic_no_target_rate_flag = 0`.

## Interpretation

This is a positive instrumentation-control result, not a positive theory result.

B0 says the frontier-transform instrument is semantically clean enough to justify a small true Phase B design-set recurrence run. It does not say recurrent boundary deformation clears controls.

## Recommended Next Step

Proceed to Phase B with:

```text
design set only
holdout untouched
canonical windows frozen
flow modes separated
candidate_detection_enabled: false unless the Phase B spec explicitly defines detection rows
promotion_enabled: false
use B0-viable metric families first
```

Do not run Phase C or scale until Phase B design-set recurrence clears matched transform controls.

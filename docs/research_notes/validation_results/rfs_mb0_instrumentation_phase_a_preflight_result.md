# RFS-MB0 Instrumentation Phase A Preflight Result

Date: 2026-05-27

Spec:

```text
docs/RFS_MB0_INSTRUMENTATION_BRANCH_PIVOT_AND_PROBE_PANEL_SPEC.md
```

Run folder:

```text
results/rfs_mb0_relation_atlas/20260527_instrumentation_phase_a_preflight/
```

## Claim Boundary

This was Phase A preflight only.

No candidate detection, holdout detection, promotion, identity classification, agent classification, or discovery claim was made.

## Run Shape

```text
workers: 18
job_batch_size: 8
jobs_requested: 800
jobs_completed: 800
row_count: 39600
errors: 0
status: COMPLETED
elapsed_seconds: 71.768
```

The run included:

```text
10 design recurrent-boundary groups
10 frozen holdout groups
4 weak-control fakeout groups used as preflight controls
6 neutral generated-system anchors
```

## Instrument Panel

Pre-registered probes:

```text
constraint_profile_hash
constraint_violation_count_plus_local_tuple
constraint_gradient_class
degree_profile_rank
constraint_cross_degree_rank
horizon_growth_contrast_v2
self_recurrence_horizon_v2
wiring_role_class_v2
existing_low
full_state_hash
```

## Phase A Decision

Phase A does not justify Phase B.

Gate results:

```text
available_axis_gate: fail
new_quotient_axis_gate: fail
passing design-set axes: constraint_axis only
```

The only design-set probe that passed viability was:

```text
constraint_violation_count_plus_local_tuple
```

It remains on the already-known constraint axis. No new quotient axis passed preflight on the design set.

## Main Readout

Verdict counts across preflight contexts:

```text
fail_no_usable_quotient_rows: 24
fail_too_coarse: 3
pass_viability_preflight: 3
```

Design-set probe viability:

```text
constraint_violation_count_plus_local_tuple: pass_viability_preflight
constraint_profile_hash: fail_too_coarse
all new quotient probes: fail_no_usable_quotient_rows
```

The rank-normalized and dynamic probes improved the conceptual basis, but they still did not produce enough usable quotient rows under the current default guardrails.

## Sparse Frontier Handling

Sparse-frontier rows were reported separately and were not allowed to promote ordinary detection.

This matters because sparse rows are common at short horizons in boundary regimes. They may deserve a dedicated sparse-control analysis later, but Phase A treats them as non-promotable.

## Interpretation

This is a useful negative.

The substrate may still be fertile, but the instrument still cannot characterize the signal across independent non-identity axes. The result argues against Phase B/C detection and against scaled exploration until probe design improves.

## Recommended Next Step

Return to probe design.

The next probe repair should focus on increasing effective signature count without drifting toward identity:

```text
cross more than one system-relative feature
use quantile bins over actual state distributions
validate effective alphabet before recurrence scoring
keep sparse-frontier analysis separate
do not touch the holdout until Phase A passes
```

# RFS-MB0 Boundary Deformation Guardrail Result

Date: 2026-05-27

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_BOUNDARY_DEFORMATION_GUARDRAIL_AND_QUOTIENT_PROBE_SPEC.md
```

Primary run:

```text
results/rfs_mb0_relation_atlas/20260527_boundary_deformation_guardrail_focused/
```

Batched technical smoke:

```text
results/rfs_mb0_relation_atlas/20260527_boundary_deformation_guardrail_batched_smoke/
```

## Run Shape

The focused audit used:

```text
groups_selected: 20
fresh_seeds_per_group: 4
start_samples_list: 3,8
workers: 18
jobs_requested: 1760
jobs_completed: 1760
metric_rows: 87120
errors: 0
status: COMPLETED
elapsed_seconds: 235.772
```

The audit included existing repaired axes, new quotient probe families, diagnostic low projections, and identity-axis controls. Promotion and n=6 transfer were disabled.

## Outcome

No group passed as a clean quotient-resolved recurrent boundary deformation.

Corrected group classes:

```text
identity_leakage_dependent: 10
underdetermined_after_guardrail_audit: 10
```

Every group had:

```text
independent_probe_axis_gate_pass: 0
classification_status: classification_not_attempted
```

The strongest non-identity quotient signal was weak. Usable quotient candidate rates were sparse and matched recurrence excess was negative for all groups.

## Probe Family Behavior

Default usable quotient rates:

```text
constraint_profile_hash: 0.0256
constraint_violation_count_plus_local_tuple: 0.0236
all new quotient probe families: 0.0
coordinate_tuple_k3: 0.0
coordinate_tuple_k4: 0.0
existing_low: 0.0
full_state_hash control: 0.0
```

The new quotient families reduced identity-like behavior in some cases but remained collision-limited:

```text
relation_neighborhood_degree_asymmetry_histogram mean_collision_rate: 0.9827
frontier_response_bucket mean_collision_rate: 0.9936
motif_count_bucket mean_collision_rate: 0.9720
multi_scale_support_region_bucket mean_collision_rate: 0.9900
constraint_neighborhood_histogram mean_collision_rate: 0.9738
```

## Interpretation

This is a measurement-limit confirmation, not a theory confirmation.

The prior recurrent structure does not currently survive the new guardrails as usable quotient evidence. Candidate-looking signal is mostly:

```text
collision-limited
identity-leakage dependent
restricted to repaired constraint axes
below matched recurrence controls
not recurrent across independent usable quotient axes
```

The result supports the spec's caution: a probe can become more informative by becoming too close to a fingerprint, and that should not count as deformation evidence.

## Technical Note: CPU Utilization

The initial focused run used all 18 configured workers but underutilized CPU because each submitted job was small and returned many rows through multiprocessing IPC. The bottleneck was task granularity and process-result serialization, not the worker count.

The runner was updated to submit batches of jobs per worker task:

```text
--job-batch-size 8
```

Batched smoke completed cleanly:

```text
jobs_requested: 22
jobs_completed: 22
job_batches_requested: 3
metric_rows: 594
errors: 0
status: COMPLETED
```

Future medium or large guardrail runs should use batched submission and, if needed, larger per-worker chunks rather than simply increasing the worker count.

## Decision

Do not scale this exact branch as a confirmation run.

Recommended next move:

```text
Treat this as a real guardrail negative.
Document the measurement limit.
If continuing, redesign quotient probes around lower-collision but explicitly non-fingerprint summaries.
Keep identity and agent classification deferred.
```

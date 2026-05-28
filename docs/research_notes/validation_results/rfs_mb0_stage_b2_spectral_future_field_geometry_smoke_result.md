# RFS-MB0 Stage B-2 Spectral Future-Field Geometry Smoke Result

Date: 2026-05-29

Spec:

```text
docs/RFS_MB0_STAGE_B2_SPECTRAL_FUTURE_FIELD_GEOMETRY_SMOKE_SPEC.md
```

## 1. Claim Boundary

This was a structured future-field geometry smoke only.

It was not holdout validation, candidate promotion, Omega detection, agency
detection, identity detection, or value detection.

Run counters stayed inside the boundary:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

Important control caveat:

```text
control_comparison_scope: direct_stage_b2_controls_only
label_shuffled_controls_completed: false
context_shuffled_controls_completed: false
horizon_order_shuffled_controls_completed: false
frontier_size_matched_controls_completed: false
probe_marginal_controls_completed: false
```

This result is therefore a direct-control spectral audition, not a full pass of
the spectral migration criteria in the spec.

## 2. Implementation

Implemented:

```text
omega/rfs_mb0_future_landscape/run_stage_b2_spectral_future_field_geometry_smoke.py
```

The runner recomputes compact Stage B-2 samples and constructs two matrix
families from primitive frontier-transform observables:

- `cofrontier`: co-occurrence of future signatures in the reachable frontier
  at the downstream horizon;
- `coflow`: co-occurrence of observed signature-transition items in the
  transition distributions emitted by the existing frontier-transform runner.

Matrices are built by:

```text
matrix_family
condition_id
actual_control_name
proxy_level
probe_key
flow_mode
horizon_band
```

The normalization is a bounded independence residual:

```text
(P_ij - P_i P_j) / (0.5 * (P_ij + P_i P_j) + epsilon)
```

The runner emits matrix manifests, item coverage, spectral summaries,
top-k alignment summaries, syndrome-context summaries, topology-sensitivity
summaries, status/progress checkpoints, error logs, and a Markdown report.

It is signal-aware and writes salvageable partial status/checkpoints before
graceful shutdown when interrupted near the time cap.

## 3. Contract Smoke

Local output:

```text
results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_contract_smoke/
```

Status:

```text
status: COMPLETED
elapsed_seconds: 2.173
workers: 4
jobs_completed: 20 / 20
contexts_accumulated: 1680
matrix_count: 180
matrix_coverage_insufficient_count: 0
errors: 0
```

All required output files were produced.

## 4. Small Desktop Smoke

Local output:

```text
results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_small_smoke_v2/
```

Generated report:

```text
results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_small_smoke_v2/rfs_mb0_stage_b2_spectral_future_field_geometry_smoke_report.md
```

Status:

```text
status: COMPLETED
elapsed_seconds: 15.473
workers: 18
jobs_completed: 240 / 240
contexts_accumulated: 30240
matrix_count: 180
spectral_decompositions_completed: 180
matrix_coverage_insufficient_count: 0
errors: 0
control_summary_cache_status: loaded:stage_b2_control_summary_cache.pkl
decision_class: spectral_future_geometry_present
branch_recommendation: recommend_channel_edge_sensitivity_with_spectral_guidance
```

The run used both preregistered probes:

```text
constraint_profile_hash
constraint_violation_count_plus_local_tuple
```

and both flow views:

```text
one_step_local_flow
constrained_window_flow
```

## 5. Main Readout

The spectral matrices were well covered in this smoke. Top positive-mass
matrices were dominated by `coflow` under low-probability topology controls,
especially `asymmetric_edge_flip_control:p0.02` and
`small_edge_resample_control:p0.02`.

Top direct topology deltas against baseline were all `coflow` middle-horizon
rows:

```text
asymmetric_edge_flip_control:p0.02 / constraint_profile_hash / constrained_window_flow / middle:
  positive_spectral_mass_delta_vs_baseline: +218.982

asymmetric_edge_flip_control:p0.02 / constraint_profile_hash / one_step_local_flow / middle:
  positive_spectral_mass_delta_vs_baseline: +208.478

asymmetric_edge_flip_control:p0.02 / constraint_violation_count_plus_local_tuple / constrained_window_flow / middle:
  positive_spectral_mass_delta_vs_baseline: +166.739

asymmetric_edge_flip_control:p0.02 / constraint_violation_count_plus_local_tuple / one_step_local_flow / middle:
  positive_spectral_mass_delta_vs_baseline: +153.552
```

The lowest computed baseline-vs-control top-k alignments came from `cofrontier`
under asymmetric edge flips:

```text
asymmetric_edge_flip_control:p0.02 / constraint_violation_count_plus_local_tuple / frontier / middle:
  top_k_subspace_alignment: 0.489

asymmetric_edge_flip_control:p0.02 / constraint_violation_count_plus_local_tuple / frontier / downstream:
  top_k_subspace_alignment: 0.510
```

Interpretation:

```text
The smoke found a resolved spectral object in the direct-control Stage B-2 sample:
future-signature co-occurrence and transition-flow matrices are nonblank,
well-covered, and sensitive to topology-level edge perturbation.
```

What this does not show:

```text
It does not yet show that the spectral structure survives label shuffles,
context shuffles, horizon-order shuffles, frontier-size matching, or
probe-marginal matching. It also does not show agency, value, identity,
Omega compatibility, or holdout generalization.
```

## 6. Recommendation

Proceed with a channel-edge sensitivity follow-up, using spectral high-loading
items as exploratory guidance only.

Do not migrate the project to a spectral gauge interpretation until a repaired
spectral runner adds the missing shuffled and matched controls.

Minimum next repair for a serious spectral pass:

- label-shuffled spectral replicates;
- context-shuffled spectral replicates;
- horizon-order shuffled spectral replicates;
- frontier-size or support-size matched spectral controls;
- probe-marginal spectral controls;
- rank-based decision criteria over replicate distributions rather than
  direct-control thresholds.

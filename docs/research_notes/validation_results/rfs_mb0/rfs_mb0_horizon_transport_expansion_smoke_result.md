# RFS-MB0 Horizon-Transport Expansion Smoke Result

Date: 2026-05-30
Spec: `docs/specs/archive/rfs_mb0/RFS_MB0_HORIZON_TRANSPORT_EXPANSION_SMOKE_SPEC.md`
Runner: `omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair`
Runner commit: `a988989`
Local output: `results/local_runs/20260530_horizon_transport_expansion_smoke_desktop_scale_192_inputs/`

## 1. Executive Summary

The horizon-transport expansion smoke completed cleanly at the intended
desktop-shape run size on this laptop profile: `180 / 180` jobs completed,
`0` errors, `140` horizon-transport matrices, and `7` detector-null replicates.

The instrument stayed well covered, matched marginal detector nulls separated,
and perturbation-response profiles were interpretable. All emitted
perturbation-response rows classified as `transport_stable`, so the result is
best read as an instrument-scaleup pass with stable response geometry, not as a
new causal or candidate claim.

Best context by the current score was tied across many contexts; the first
reported context was:

```text
constraint_profile_hash | constrained_window_flow | 24->32
```

Recommended next action fork:

```text
expand_horizon_transport_scale
```

## 2. Claim Boundary

This is an empirical expansion smoke, not a validation run.

Allowed:

```text
horizon-transport matrices did or did not build with adequate coverage;
matched marginal detector nulls did or did not separate from observed transport;
tiny nonlethal perturbations did or did not produce interpretable response profiles;
contexts are or are not worth scaling.
```

Forbidden:

```text
Omega detected;
agent detected;
valuer detected;
identity detected;
candidate promoted;
holdout ready;
graph-channel causality shown.
```

Required counters remained clean:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## 3. Run Shape and Local Artifact Policy

The default committed focused selection currently contains only one runnable
group, so it can produce only a `60`-job expanded local smoke even with desktop
scale knobs. To make the proper smoke a proper desktop-shape smoke, this run
used the local rebuildable 192-input bundle:

```text
selection: results/local_runs/20260528_laptop_frontier_transform_validation_192_inputs/selection/focused_boundary_group_selection.csv
corrected: results/local_runs/20260528_laptop_frontier_transform_validation_192_inputs/corrected/corrected_group_classification.csv
source_run: results/local_runs/20260528_laptop_frontier_transform_validation_192_inputs/source
```

Run parameters:

```text
groups: 12
design_groups: 3
fresh_seeds_per_group: 3
start_samples_list: 2,4
probes: constraint_profile_hash,constraint_violation_count_plus_local_tuple
small_edge_resample_strengths: 0.0025,0.005
asymmetric_edge_flip_strengths: 0.0025,0.005
null_replicates: 7
workers: 7
max_runtime_seconds: 14400
shutdown_cushion_seconds: 1200
```

Completion:

```text
status: COMPLETED
finalization_reason: all_jobs_completed
jobs_requested: 180
jobs_completed: 180
elapsed_seconds: 15.293
errors: 0
```

Generated CSV/JSON artifacts remain local-only and should not be committed.

## 4. Matrix Coverage

```text
matrix_count: 140
coverage_rows: 140
minimum_context_coverage: 1.000
context_recommendation_rows: 28
```

The run covered both required probes and both imported flow modes:

```text
constraint_profile_hash
constraint_violation_count_plus_local_tuple

constrained_window_flow
one_step_local_flow
```

## 5. Detector-Null Results

| gate | passed | observed |
|---|---:|---|
| horizon_transport_matrix_coverage | 1 | 1.0 |
| detector_null_sections_separate | 1 | separate_outputs_written |
| structure_detector_null_separation | 1 | passed |
| detector_null_replicate_power | 1 | 7 |
| matched_marginal_detector_null_separation | 1 | 3/3 families_passed |
| synthetic_fixture_contract | 0 | not_run |

Fixture contract was not required in the empirical expansion run. It was already
covered by the prior matched-null fixture smoke.

## 6. Matched Marginal Null Results

Matched marginal separation passed for all three required families across all
reported contexts.

| null family | contexts | min pass fraction | mean pass fraction |
|---|---:|---:|---:|
| row_marginal_matched_transport_null | 28 | 1.000 | 1.000 |
| column_marginal_matched_transport_null | 28 | 1.000 | 1.000 |
| row_column_marginal_matched_transport_null | 28 | 1.000 | 1.000 |

## 7. Perturbation-Response Profile Results

```text
perturbation_response_rows: 112
perturbation_response_interpretable: 1
dominant_response_class: transport_stable
```

Response class counts:

| response class | count |
|---|---:|
| transport_stable | 112 |

Interpretation: the perturbation profiles are readable but conservative. This
smoke did not surface response diversity such as rerouting, weakening,
reopening, or collapse under the tiny nonlethal perturbations.

## 8. Probe / Flow / Horizon-Pair Context Summary

By probe:

| probe | contexts | full matched pass | response contexts | read |
|---|---:|---:|---:|---|
| constraint_profile_hash | 14 | 14 | 14 | matched_marginal_separates |
| constraint_violation_count_plus_local_tuple | 14 | 14 | 14 | matched_marginal_separates |

By flow mode:

| flow mode | contexts | full matched pass | response contexts | read |
|---|---:|---:|---:|---|
| constrained_window_flow | 14 | 14 | 14 | matched_marginal_separates |
| one_step_local_flow | 14 | 14 | 14 | matched_marginal_separates |

By horizon pair:

| horizon pair | contexts | full matched pass | response contexts | read |
|---|---:|---:|---:|---|
| 0->1 | 4 | 4 | 4 | matched_marginal_separates |
| 1->2 | 4 | 4 | 4 | matched_marginal_separates |
| 2->4 | 4 | 4 | 4 | matched_marginal_separates |
| 4->8 | 4 | 4 | 4 | matched_marginal_separates |
| 8->16 | 4 | 4 | 4 | matched_marginal_separates |
| 16->24 | 4 | 4 | 4 | matched_marginal_separates |
| 24->32 | 4 | 4 | 4 | matched_marginal_separates |

## 9. Readiness Levels

```text
readiness_level: ready_for_horizon_transport_scaleup
ready_for_horizon_transport_scaleup: 1
ready_for_horizon_transport_context_narrowing: 0
ready_for_horizon_transport_fixture_expansion: 0
ready_for_direct_channel_diagnostics: 0
not_ready_repair_required: 0
measurement_limits_note_recommended: 0
```

## 10. Next-Action Fork

```text
expand_horizon_transport_scale
```

Recommended interpretation:

```text
Proceed to a larger horizon-transport scaleup only within the same claim
boundary. Do not open holdout, graph perturbation, direct channel diagnostics,
candidate promotion, or Omega/agency/value claims from this smoke alone.
```

## 11. Output Manifest

Local output directory:

```text
results/local_runs/20260530_horizon_transport_expansion_smoke_desktop_scale_192_inputs/
```

Core generated outputs:

```text
horizon_transport_expansion_run_config.json
horizon_transport_expansion_status.json
horizon_transport_expansion_progress_checkpoints.csv
horizon_transport_expansion_errors.csv
horizon_transport_expansion_output_manifest.json
horizon_transport_matrix_manifest.csv
horizon_transport_row_item_manifest.csv
horizon_transport_column_item_manifest.csv
horizon_transport_coverage.csv
horizon_transport_matrix_summary.csv
horizon_transport_svd_summary.csv
horizon_transport_subspace_alignment.csv
horizon_transport_participation_summary.csv
horizon_transport_entropy_summary.csv
horizon_transport_detector_null_summary.csv
horizon_transport_detector_null_anatomy.csv
horizon_transport_detector_null_gate_results.csv
horizon_transport_matched_marginal_summary.csv
horizon_transport_perturbation_manifest.csv
horizon_transport_response_profile_summary.csv
horizon_transport_response_classification.csv
horizon_transport_by_probe_summary.csv
horizon_transport_by_flow_mode_summary.csv
horizon_transport_by_horizon_pair_summary.csv
horizon_transport_context_recommendation.csv
rfs_mb0_horizon_transport_expansion_smoke_result.md
```

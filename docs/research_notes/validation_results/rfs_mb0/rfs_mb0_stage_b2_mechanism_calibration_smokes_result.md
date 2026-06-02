# RFS-MB0 Stage B-2 Mechanism Calibration Smoke Result

Date: 2026-05-28

Specs:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_STAGE_B2_MECHANISM_CALIBRATION_AND_GAUGE_VIEW_OVERLAY_SPEC.md
docs/specs/archive/rfs_mb0/RFS_MB0_STAGE_B2_MECHANISM_CALIBRATION_AND_GAUGE_VIEW_OVERLAY_ADDENDUM.md
```

## Claim Boundary

This was an implementation and workflow smoke for Stage B-2 mechanism
calibration and entropy-flow-horizon gauge overlay reporting.

It was not holdout validation, n=6 transfer, alphabet expansion, candidate
promotion, Omega detection, agency detection, identity detection, or value
detection.

## Implementation Changes

Added a dedicated Stage B-2 runner:

```text
omega/rfs_mb0_future_landscape/run_frontier_transform_stage_b2_mechanism_calibration.py
```

The runner implements:

```text
dedicated background CSV writer thread for streamed large outputs
compact Stage A control-summary loading from phase_b_stage_a_control_values.csv
control identity / proxy discipline fields in every mechanism-control manifest row
post-preservation destructiveness interpretation gates
entropy / flow / horizon overlay summaries
corridor / trap / fakeout provisional summary
signal-aware partial status and checkpoint writes
hard runtime cap plus shutdown cushion
```

The runner also keeps the claim boundary explicit:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_detection_enabled: false
promotion_enabled: false
```

## Smoke Runs

Contract smoke:

```text
output: results/rfs_mb0_relation_atlas/20260528_stage_b2_contract_smoke/
status: COMPLETED
elapsed_seconds: 36.544
jobs_completed: 12 / 12
metric_rows: 672
component_score_rows: 4032
errors: 0
required outputs: present
```

Small desktop smoke after report-gate patch:

```text
output: results/rfs_mb0_relation_atlas/20260528_stage_b2_small_desktop_smoke_v2/
status: COMPLETED
elapsed_seconds: 53.334
workers: 18
job_batch_size: 4
jobs_completed: 288 / 288
metric_rows: 24192
component_score_rows: 290304
syndrome_rate_rows: 192
dependency_score_rows: 44
decision_rows: 4
mechanism_control_systems_generated: 264
errors: 0
required outputs: present
```

Timing note:

```text
control_summary_load_seconds: 37.667
active job execution and finalization: about 15.7 seconds
```

For this small smoke the dominant wall-clock cost was loading the compact Stage A
control summary, not worker execution.

## Control Identity Read

The corrected report now counts destructiveness after the preservation gate,
not just from nominal control identity.

Small smoke identity summary:

```text
exact mechanism control conditions: 3
near-mechanism proxy conditions: 0
generation-level proxy conditions: 1
topology-level proxy conditions: 7
presentation-level control conditions: 0
not-available/baseline conditions: 1
too-destructive/underdetermined conditions: 2
runtime-downgraded intended controls: 0
```

The two too-destructive/underdetermined conditions were:

```text
asymmetric_edge_flip_control:p0.02
constraint_resampled_generation_proxy:p0.0025
```

This is a useful smoke result because the runner now surfaces destructive
controls directly instead of allowing them to masquerade as mechanism evidence.

## Decision Summary

Small smoke decision table:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag:
  decision_class: edge_roughening_sensitive_syndrome
  baseline_syndrome_rate: 0.050595238095238096
  max_mechanism_dependency_score: 1.0

SYN_C_low_growth_high_concentration_low_entropy:
  decision_class: edge_roughening_sensitive_syndrome
  baseline_syndrome_rate: 0.05357142857142857
  max_mechanism_dependency_score: 1.0

SYN_B_high_turnover_high_offdiag_high_window_delta:
  decision_class: control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.0703125
  max_mechanism_dependency_score: 0.07407407407407401

SYN_D_high_turnover_high_entropy_low_bottleneck_control:
  decision_class: control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.028273809523809524
  max_mechanism_dependency_score: 1.2270886061646466e-16
```

Corridor / trap / fakeout provisional read:

```text
SYN_A: edge_fragile_deformation, low_smoke confidence
SYN_C: edge_fragile_deformation, low_smoke confidence
SYN_B: underpowered_or_unresolved, low_smoke confidence
SYN_D: underpowered_or_unresolved, low_smoke confidence
```

Interpretation should remain conservative. The smoke says the Stage B-2
mechanism-calibration workflow is live and the proxy discipline is working. It
does not validate a mechanism claim.

## Scaling Notes

The dedicated writer successfully decoupled large CSV writes from worker
completion, but the component score output is still large:

```text
stage_b2_component_scores.csv: 290304 rows, about 212 MB
stage_b2_metric_rows.csv: 24192 rows, about 23 MB
```

For a medium run this is manageable locally. For a long run, either keep a
strict wall-clock cap and enough disk headroom, or add a more aggressive
component-output reduction mode before scale.

The GPU was not used. This runner is currently CPU/process and CSV-I/O bound,
with the small smoke dominated by Stage A control-summary loading.

## Recommendation

Stage B-2 is ready for a medium smoke focused on the preservation-first
mechanism ladder.

Do not open holdout. Do not treat the edge-fragility read as a positive Omega
claim. The next technical improvement should be either:

```text
1. a more compact component-score retention mode for long runs; or
2. a cached binary/columnar Stage A control summary to reduce repeat startup
   cost.
```

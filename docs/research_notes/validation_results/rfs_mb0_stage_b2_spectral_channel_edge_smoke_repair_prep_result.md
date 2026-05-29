# RFS-MB0 Stage B-2 Spectral Channel-Edge Smoke Repair Prep Result

Date: 2026-05-29

Spec:

```text
docs/RFS_MB0_STAGE_B2_SPECTRAL_CHANNEL_EDGE_SMOKE_REPAIR_PREP_SPEC.md
```

## 1. Claim Boundary

This was an instrument-readiness smoke only.

It was not holdout validation, candidate promotion, Omega detection, agency
detection, identity detection, valuer detection, or value detection.

Run counters stayed inside the boundary:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## 2. Runtime And Hardware Profile

Implementation:

```text
omega/rfs_mb0_future_landscape/run_stage_b2_spectral_future_field_geometry_smoke.py
```

Local outputs:

```text
results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_channel_prep_contract_smoke_v5/
results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_channel_prep_small_smoke_v2/
```

Small smoke profile:

```text
workers: 18
jobs_completed: 80 / 80
elapsed_seconds: 10.059
contexts_accumulated: 6720
matrix_count: 180
spectral_decompositions_completed: 180
errors: 0
```

## 3. Priority Stages Completed

Completed:

- Priority 0 runner/output contract;
- Priority 1 cheap spectral shuffle controls;
- Priority 2 high-loading export and item-to-edge mapping;
- Priority 3 analysis-only high-loading ablation;
- Priority 4 tiny targeted-vs-random perturbation implementation check on the
  contract smoke.

The larger small smoke gated Priority 4 off because Priority 3 became
random-equivalent.

## 4. Runner / Output Contract Smoke

Contract output:

```text
results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_channel_prep_contract_smoke_v5/
```

Status:

```text
status: COMPLETED
jobs_completed: 20 / 20
workers: 4
errors: 0
manifest_rows: 51
missing_manifest_rows: 0
```

The contract smoke verified:

- split prep decision classes;
- duplicated prep status/config/progress/error outputs;
- high-loading item export;
- item-to-edge mapping export;
- shuffle-control outputs;
- analysis-only ablation outputs;
- tiny targeted-vs-random perturbation outputs;
- honest output manifest.

## 5. Spectral Shuffle-Control Smoke

Small smoke summary:

```text
label_shuffle:
  shuffle_control_equivalent: 12

context_shuffle:
  observed_above_shuffle: 6
  shuffle_control_equivalent: 6

horizon_order_shuffle:
  observed_above_shuffle: 10
  shuffle_control_equivalent: 2
```

Read:

```text
The cheap shuffle controls do not trivially erase the observed spectral object,
but label shuffles remain mostly control-equivalent. This is enough for a prep
smoke, not enough for a full spectral migration claim.
```

Still missing:

```text
frontier_size_matched_controls_completed: false
probe_marginal_controls_completed: false
```

## 6. High-Loading Export And Mapping Smoke

Small smoke mapping:

```text
high_loading_matrix_rows: 12
best_mapped_item_mass_fraction: 1.000
lowest_mapped_item_mass_fraction: 1.000
mapping_read: mapping_adequate
```

Read:

```text
High-loading coflow items can be exported and mapped back to realized edge
samples with enough coverage for perturbation plumbing.
```

This is an implementation-readiness result only. It does not mean those mapped
items are causal or theory-relevant.

## 7. Analysis-Only Ablation Smoke

Small smoke ablation decision:

```text
decision_class: high_loading_ablation_random_equivalent
high_loading_drop_fraction_mean: 0.1073
matched_random_drop_fraction_mean: 0.1261
matrix_count: 12
random_replicate_rows: 60
```

Read:

```text
The richer small smoke does not support treating high-loading spectral items as
specific load-bearing items. Matched random removal changed spectral summaries
at least as much as high-loading removal.
```

This blocks the 24h spectrally guided channel-edge run.

## 8. Tiny Targeted-Vs-Random Perturbation Smoke

The contract smoke proved the perturbation path is technically runnable:

```text
computed_perturbation_rows: 16
destructive_rows: 0
targeted_spectral_positive_mass_mean: 62.2477
random_spectral_positive_mass_mean: 62.5455
targeted_vs_random_spectral_relative_separation: 0.00476
targeted_ac_rate_mean: 0.0
random_ac_rate_mean: 0.0
```

Read:

```text
The graph-level perturbation implementation is non-destructive at tiny p, but
the targeted and matched-random responses are not distinguishable in the
contract smoke.
```

In the broader small smoke, targeted perturbation was not run because the
analysis-only ablation gate failed.

## 9. Readiness For 24h Run

Small smoke final decision:

```text
decision_classes:
  runner_contract_passed
  spectral_shuffle_controls_passed
  spectral_item_mapping_adequate
  high_loading_ablation_random_equivalent
  tiny_channel_perturbation_not_interpretable
  not_ready_repair_required

ready_for_24h_run: 0
branch_recommendation: recommend_spectral_channel_repair_before_large_run
```

Conclusion:

```text
Do not run the 24h spectral channel-edge pass yet.
```

## 10. Blockers / Repairs Required

Primary blocker:

```text
High-loading ablation is random-equivalent at the small-smoke scale.
```

Secondary blocker:

```text
Tiny targeted-vs-random graph perturbation is technically runnable and
non-destructive, but not distinguishable from matched random in the contract
smoke.
```

Recommended next repair:

```text
Tighten high-loading selection before perturbation scaling:
  use replicate-stable high-loading items;
  require cross-shuffle survival;
  require cross-seed recurrence;
  compare against degree/frequency/baseline-flow matched item sets;
  then rerun the ablation gate before any 24h channel-edge pass.
```

## 11. Output Manifest

The retained local small-smoke manifest reports:

```text
manifest_rows: 51
missing_rows: 0
```

Primary generated report:

```text
results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_channel_prep_small_smoke_v2/rfs_mb0_stage_b2_spectral_channel_edge_smoke_repair_prep_result.md
```

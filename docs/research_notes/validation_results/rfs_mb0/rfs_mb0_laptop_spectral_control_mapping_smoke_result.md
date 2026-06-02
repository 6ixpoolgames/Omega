# RFS-MB0 Laptop Spectral Control Mapping Smoke Result

Date: 2026-05-30

## Executive Summary

Instrumentation addendum: the laptop spectral control/mapping runner was
upgraded to instrument version `0.3.0` / schema `2026-05-30.3` to support the
GPT-requested triage view. The addendum splits label-shuffle controls from
required structure-destroying shuffles, emits matrix-level shuffle-failure
anatomy, reports coflow subspace distributedness, compares subspace transfer
against explicit controls, and emits one next-action fork.

Tiny local contract validation completed cleanly: 6/6 jobs, 0 errors, 44/44
manifest files present. The addendum does not change the scientific conclusion:
the current local read is still `not_ready_repair_required`, with
`structure_shuffle_controls_not_passed` and next action
`repair_shuffle_controls`.

Final status: `COMPLETED` with `all_jobs_completed`.

Decision class: `not_ready_repair_required`.

Blocking reason: `structure_shuffle_controls_not_passed`. Under the v0.3.0
contract, label shuffle is retained as a label-interpretation warning, while
context and horizon shuffles are the required structure-destroying controls.
The tiny contract smoke still failed the required structure gate.

The run does not justify a larger spectral-control run, analysis-only channel
run, tiny graph-channel perturbation, or larger graph-channel run.

Interpretation: item-to-edge mapping was adequate and the selection/evaluation
subspace transferred, but item-local high-loading ablation remained
random-equivalent against matched random controls. This points toward a
distributed spectral structure rather than a ready item-local channel
perturbation path.

Artifact policy: generated CSV/JSON outputs and the GPT forwarding bundle remain
local-only under `results/local_runs/` and should not be committed unless a
maintainer explicitly promotes them.

## Claim Boundary

This was a laptop-safe instrument-readiness and diagnostic smoke.

It was not holdout validation, candidate promotion, Omega detection, agency
detection, identity detection, valuer detection, value detection, or graph-level
causal evidence.

Run counters:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## Local Run

Local output:

```text
results/local_runs/20260530_laptop_spectral_gpt_diagnostic_smoke/
results/local_runs/20260530_laptop_spectral_triage_contract_smoke_v2/
results/local_runs/20260530_laptop_spectral_triage_missing_source_gate/
```

Local forwarding bundle for external audit:

```text
results/local_runs/20260530_laptop_spectral_gpt_forwarding_bundle/
results/local_runs/20260530_laptop_spectral_gpt_forwarding_bundle.zip
```

These paths are local-only and are not repository artifacts.

## Instrumentation Addendum

Implemented outputs:

```text
laptop_spectral_shuffle_failure_anatomy.csv
laptop_subspace_distributedness_diagnostic.csv
laptop_subspace_control_alignment.csv
laptop_spectral_next_action_fork.csv
```

Tiny contract smoke:

```text
status: COMPLETED
finalization_reason: all_jobs_completed
jobs_completed: 6 / 6
errors: 0
instrument_version: 0.3.0
schema_version: 2026-05-30.3
manifest: 44 / 44 present
spectral_shuffle_control_status: spectral_shuffle_controls_control_equivalent
blocking_reason: structure_shuffle_controls_not_passed
subspace_distributedness_read: diffuse_noise_like
subspace_control_alignment_status: subspace_transfer_control_equivalent
next_action_fork: repair_shuffle_controls
```

Addendum CSV row counts:

```text
laptop_spectral_shuffle_failure_anatomy.csv: 9
laptop_subspace_distributedness_diagnostic.csv: 3
laptop_subspace_control_alignment.csv: 12
laptop_spectral_next_action_fork.csv: 1
```

Graceful-exit guard:

```text
status: PARTIAL_CONTROL_SOURCE_MISSING
finalization_reason: missing_phase_b_control_summary_source
jobs_requested: 0
jobs_completed: 0
blocking_reason: missing_source
```

Read:

```text
The tool now produces the requested triage details without pushing generated
CSV/JSON artifacts into the repository. The smoke remains theory-work only:
repair structure-destroying shuffle controls before graph perturbation.
```

## Runtime And Contract

```text
status: COMPLETED
finalization_reason: all_jobs_completed
elapsed_seconds: 13.527
workers: 7
jobs_completed: 24 / 24
contexts_accumulated: 3024
matrix_count: 54
errors: 0
control_summary_cache_status: loaded:stage_b2_control_summary_cache.pkl
shuffle_replicates_completed: 90
high_loading_items_exported: 40
item_sets_mapped: 5
ablation_jobs_completed: 35
perturbation_jobs_completed: 0
```

The local manifest reported all expected forwarding-bundle artifacts present.

## Gate Results

```text
G0 control_source_available: passed
G1 output_contract_passed: passed
G2 structure_shuffle_family_thresholds: failed
G3 item_mapping_mass: passed
G4 selection_evaluation_ablation: failed
G5 tiny_perturbation_optional: not run / optional
```

First failed required gate:

```text
gate_id: G2
gate_name: structure_shuffle_family_thresholds
threshold: context and horizon structure controls pass; label shuffle reported separately
observed: 0/2 structure families; 0/1 label families in the tiny contract smoke
blocking_reason: primary_context_below_catastrophic_floor
```

## Shuffle-Family Read

```text
label_shuffle:
  family_passed: 0
  pass_fraction: 0.5
  median_observed_percentile: 0.5
  min_observed_percentile: 0.0
  catastrophic_fail_count: 3
  blocking_reason: primary_context_below_catastrophic_floor

context_shuffle:
  family_passed: 0
  pass_fraction: 0.6666666666666666
  median_observed_percentile: 0.8
  min_observed_percentile: 0.4
  catastrophic_fail_count: 1
  blocking_reason: primary_context_below_catastrophic_floor

horizon_order_shuffle:
  family_passed: 1
  pass_fraction: 0.6666666666666666
  median_observed_percentile: 0.8
  min_observed_percentile: 0.6
  catastrophic_fail_count: 0
```

Read:

```text
Only horizon-order shuffle cleared the stricter family gate. The spectral
control layer remains blocked before larger spectral-channel scaling.
```

## High-Loading And Mapping

```text
high_loading_items_exported: 40
stable_high_loading_matrix_count: 5
item_sets_mapped: 5
best_mapped_item_mass_fraction: 1.000
item_mapping_status: spectral_item_mapping_adequate
```

Read:

```text
The item-to-edge mapping machinery is adequate at this smoke scale. Mapping is
not the current blocker.
```

## Ablation And Subspace

Ablation decision:

```text
decision_class: high_loading_ablation_random_equivalent
ablation_failure_reason: high_loading_delta_le_random_max;insufficient_metric_specificity
high_loading_delta: 0.047743807987362004
random_delta_mean: 0.08715710311136862
random_delta_std: 0.019199590434986882
random_delta_max: 0.10902465909564239
high_loading_minus_random_mean: -0.03941329512400662
high_loading_over_random_ratio: 0.5477902119619025
metric_specificity_wins: 0
matching_quality: 0.9347372959774736
coverage_loss_after_ablation: 0.026033540290742976
subspace_transfer_status: subspace_transfers
subspace_item_read: subspace_transfers_but_items_not_specific
```

Read:

```text
The selection/evaluation top-k subspace transfers, but high-loading item
ablation does not beat matched random ablation on the quantitative gate. This
keeps graph perturbation gated and suggests the useful object may be distributed
at subspace level rather than localized to a small high-loading item set.
```

## Readiness Levels

```text
ready_for_larger_spectral_control_run: 0
ready_for_larger_analysis_only_channel_run: 0
ready_for_tiny_graph_channel_perturbation: 0
ready_for_larger_graph_channel_run: 0
```

Decision:

```text
not_ready_repair_required
```

Recommended next action:

```text
Repair the spectral-control layer and investigate subspace-level diagnostics
before any graph perturbation or larger spectral-channel run.
```

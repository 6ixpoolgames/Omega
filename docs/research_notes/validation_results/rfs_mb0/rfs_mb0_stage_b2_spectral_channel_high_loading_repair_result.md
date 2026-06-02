# RFS-MB0 Stage B-2 Spectral Channel High-Loading Repair Result

Date: 2026-05-29

Predecessor:

```text
docs/research_notes/validation_results/rfs_mb0/rfs_mb0_stage_b2_spectral_channel_edge_smoke_repair_prep_result.md
```

## 1. Claim Boundary

This was an instrument-repair smoke.

It was not holdout validation, candidate promotion, Omega detection, agency
detection, identity detection, valuer detection, or value detection.

Run counters:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## 2. Repair Implemented

The prior prep smoke blocked the 24h run because high-loading ablation was
random-equivalent.

The repair tightened high-loading selection by adding:

- explicit high-loading candidate pool export;
- seed and group recurrence fields;
- matrix-level shuffle-survival count;
- stable-selection gate:
  `seed_count >= 2`, `shuffle_survival_count >= 1`,
  `matrix_recurrence_count >= 1`;
- stable selection score using loading, seed recurrence, shuffle survival, and
  matrix recurrence;
- frequency / baseline-flow matched random item ablations instead of uniform
  random item ablations;
- matrix-level targeted perturbation over the stable item set rather than a
  single transition item.

New retained runner remains:

```text
omega/rfs_mb0_future_landscape/run_stage_b2_spectral_future_field_geometry_smoke.py
```

## 3. Small Smoke

Local output:

```text
results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_channel_high_loading_repair_small_smoke_v2/
```

Status:

```text
status: COMPLETED
workers: 18
jobs_completed: 80 / 80
elapsed_seconds: 24.965
contexts_accumulated: 6720
matrix_count: 180
errors: 0
manifest_rows: 52
missing_rows: 0
```

Claim-boundary counters remained zero.

## 4. Stable High-Loading Selection

Selection summary:

```text
candidate_pool_rows: 2275
stable_high_loading_selected_rows: 87
stable_high_loading_matrix_count: 10
```

The smoke selected stable items in 10 target matrices. Two target matrices had
no stable high-loading items under the repair rule.

## 5. Shuffle And Mapping Read

Shuffle-control summary:

```text
label_shuffle:
  shuffle_control_equivalent: 12

context_shuffle:
  observed_above_shuffle: 6
  shuffle_control_equivalent: 6

horizon_order_shuffle:
  observed_above_shuffle: 9
  shuffle_control_equivalent: 3
```

Mapping:

```text
mapped_item_mass_fraction_min: 1.000
mapped_item_mass_fraction_max: 1.000
mapped_item_mass_fraction_mean: 1.000
```

Read:

```text
The repair preserves adequate item-to-edge mapping coverage, but label shuffles
are still mostly control-equivalent and frontier-size / probe-marginal spectral
controls remain unimplemented.
```

## 6. Matched Ablation Read

Ablation decision:

```text
decision_class: high_loading_ablation_specific
high_loading_drop_fraction_mean: 0.05884
matched_random_drop_fraction_mean: 0.04504
matrix_count: 10
random_replicate_rows: 50
random_matching: item_count_and_baseline_flow_count_greedy
```

Read:

```text
After stable selection and stricter random matching, high-loading ablation is
no longer random-equivalent in this small smoke.
```

This is an instrument-readiness result, not a theory-positive result.

## 7. Tiny Targeted-Vs-Random Perturbation

The repair changed tiny perturbation from one transition item at a time to the
stable high-loading item set for each matrix.

Tiny perturbation summary:

```text
decision_class: tiny_channel_perturbation_implemented
computed_perturbation_rows: 32
destructive_rows: 0
targeted_spectral_positive_mass_mean: 45.6983
random_spectral_positive_mass_mean: 42.5753
targeted_vs_random_spectral_relative_separation: 0.06834
targeted_ac_rate_mean: 0.0
random_ac_rate_mean: 0.0
```

The perturbations remained non-destructive at `p = 0.0025` and `p = 0.005`.

Read:

```text
Tiny targeted perturbation is now implementable and distinguishable from
matched random at the spectral-response level in this small smoke. It does not
yet move A/C syndrome rates.
```

## 8. Readiness Decision

Final small-smoke decision:

```text
runner_contract_passed
spectral_shuffle_controls_passed
spectral_item_mapping_adequate
high_loading_ablation_specific
tiny_channel_perturbation_implemented
ready_for_24h_spectral_channel_run

ready_for_24h_run: 1
branch_recommendation: recommend_24h_spectral_channel_run
```

Interpretation:

```text
The instrument is ready for a larger spectral channel-edge run as an
exploratory readiness pass. It is not a scientific gate pass and it is not
evidence for Omega, agency, identity, valuerhood, or holdout readiness.
```

## 9. Remaining Caveats

Still missing:

```text
frontier_size_matched_controls_completed: false
probe_marginal_controls_completed: false
```

Substantive caveat:

```text
A/C syndrome rates did not separate in the tiny perturbation smoke. The larger
run should treat spectral response as the primary instrument-readiness readout
and A/C movement as an open question, not an assumed effect.
```

Recommended next run:

```text
Run a larger spectral channel-edge pass using the repaired stable-selection
and matched-ablation machinery, with no holdout, no n=6, no alphabet expansion,
and explicit frontier-size/probe-marginal caveats unless those controls are
implemented first.
```

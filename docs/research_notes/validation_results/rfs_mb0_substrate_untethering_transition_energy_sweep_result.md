# Executive Summary

Decision: `untethering_underpowered`.

Next action: `continue_transition_energy_substrates`.

Run kind: `substrate_untethering`.

Horizon-transport matrices built: `436`.

Detector-null gate passed: `1`.

Detector-null replicate powered: `1`.

Matched marginal null gate passed: `1`.

Synthetic fixture contract: `passed`.

Perturbation response interpretable: `1`.

Best context: `full_state_hash|constrained_window_flow|2->4`.

Detector-null controls and candidate perturbation responses were written to separate outputs.

## Claim Boundary

No holdout scoring, no n=6 transfer, no alphabet expansion, no candidate promotion, no Omega detection, no agent detection, no identity detection, no valuer detection, and no value detection.

## Run Shape and Local Artifact Policy

Jobs requested: `24`.
Jobs completed: `24`.
Workers: `4`.
Substrate families: `constraint_template_current, locality_only, smooth_random_potential, budget_conservation`.
Finalization reason: `all_jobs_completed`.
Compact transport matrix NPZ bytes: `23406`.
Raw substrate state sample rows: `0`.
Compact raw frontier NPZ bytes: `3355`.
Artifact policy: Generated CSV/JSON run artifacts are local-only and should not be committed unless explicitly promoted by a maintainer.

## Matrix Coverage

Matrix count: `436`.
Coverage rows: `436`.
Minimum context coverage: `0.181`.

## Substrate Family Summary

| substrate_family | matrices | capacity_read | aligned amplification rows | viscosity read |
|---|---:|---|---:|---|
| constraint_template_current | 120 | substrate_capacity_available | 15 | underpowered_or_unresolved |
| locality_only | 120 | substrate_capacity_available | 0 | underpowered_or_unresolved |
| smooth_random_potential | 114 | substrate_capacity_available | 10 | underpowered_or_unresolved |
| budget_conservation | 82 | substrate_capacity_available | 7 | high_viscosity_aligned_amplifier |

## Control Taxonomy Compliance

Every matrix and response row includes intervention class, family, name, strength, interpretation role, and allowed claim level.

## Horizon-Transport Matrix Construction

Matrix family: `horizon_transport`; spectral method: `SVD`.

## Detector-Null Results

| gate | passed | observed | blocker |
|---|---:|---|---|
| horizon_transport_matrix_coverage | 1 | 1.0 |  |
| detector_null_sections_separate | 1 | separate_outputs_written |  |
| structure_detector_null_separation | 1 | passed |  |
| detector_null_replicate_power | 1 | 3 |  |
| matched_marginal_detector_null_separation | 1 | 3/3 families_passed |  |
| synthetic_fixture_contract | 1 | 8/8 |  |

## Matched Marginal Null Results

| null_family | contexts | mean pass_fraction | min percentile |
|---|---:|---:|---:|
| row_marginal_matched_transport_null | 140 | 0.864 | 0.000 |
| column_marginal_matched_transport_null | 140 | 0.886 | 0.000 |
| row_column_marginal_matched_transport_null | 140 | 0.586 | 0.000 |

## Fixture Results

| fixture | passed | observed |
|---|---:|---|
| block_transport_signal | 1 | 1:3 |
| marginal_fakeout | 1 | 0:1 |
| corridor_stable_response | 1 | transport_stable:1 |
| trap_collapse_response | 1 | transport_collapses:1 |
| amplified_aligned_response | 1 | transport_amplified_aligned:1 |
| weakened_response | 1 | transport_weakened:1 |
| rerouted_response | 1 | transport_rerouted:1 |
| reopens_response | 1 | transport_reopens:1 |

## Perturbation-Response Results

| response_class | count |
|---|---:|
| transport_amplified_aligned | 32 |
| transport_reopens | 71 |
| transport_rerouted | 54 |
| transport_resolution_mismatch | 14 |
| transport_stable | 92 |
| transport_weakened | 33 |

## Terminal Saturation Diagnostics

| horizon_pair | matrices | terminal fraction | undercoverage fraction | normal fraction |
|---|---:|---:|---:|---:|
| 1->2 | 42 | 0.000 | 0.000 | 1.000 |
| 2->4 | 42 | 0.000 | 0.000 | 1.000 |
| 4->8 | 44 | 0.000 | 0.273 | 0.727 |
| 8->16 | 44 | 0.000 | 0.455 | 0.545 |
| 16->24 | 44 | 0.000 | 0.455 | 0.545 |
| 24->32 | 44 | 0.000 | 0.455 | 0.545 |
| 32->48 | 44 | 0.000 | 0.455 | 0.545 |
| 48->64 | 44 | 0.000 | 0.455 | 0.545 |
| 64->96 | 44 | 0.000 | 0.455 | 0.545 |
| 96->128 | 44 | 0.000 | 0.455 | 0.545 |

## Response Class by Strength and Horizon Pair

| perturbation | strength | probe | flow | horizon_pair | response_class | count |
|---|---:|---|---|---|---|---:|
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 1->2 | transport_resolution_mismatch | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 1->2 | transport_stable | 2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 1->2 | transport_weakened | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 2->4 | transport_stable | 2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 2->4 | transport_weakened | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 4->8 | transport_stable | 2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 4->8 | transport_weakened | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 8->16 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 8->16 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 8->16 | transport_weakened | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 16->24 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 16->24 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 16->24 | transport_weakened | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 24->32 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 24->32 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 24->32 | transport_weakened | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 32->48 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 32->48 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 32->48 | transport_weakened | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 48->64 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 48->64 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 48->64 | transport_weakened | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 64->96 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 64->96 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 64->96 | transport_weakened | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 96->128 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 96->128 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 96->128 | transport_weakened | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 1->2 | transport_resolution_mismatch | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 1->2 | transport_stable | 2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 1->2 | transport_weakened | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 2->4 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 2->4 | transport_stable | 3 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 4->8 | transport_reopens | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 4->8 | transport_rerouted | 2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 4->8 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 8->16 | transport_reopens | 2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 8->16 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 8->16 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 16->24 | transport_reopens | 2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 16->24 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 16->24 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 24->32 | transport_reopens | 2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 24->32 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 24->32 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 32->48 | transport_reopens | 2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 32->48 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 32->48 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 48->64 | transport_reopens | 2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 48->64 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 48->64 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 64->96 | transport_reopens | 2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 64->96 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 64->96 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 96->128 | transport_reopens | 2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 96->128 | transport_rerouted | 1 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 96->128 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 1->2 | transport_resolution_mismatch | 2 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 1->2 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 2->4 | transport_reopens | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 2->4 | transport_resolution_mismatch | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 2->4 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 4->8 | transport_reopens | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 4->8 | transport_stable | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 4->8 | transport_weakened | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 8->16 | transport_reopens | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 8->16 | transport_stable | 2 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 16->24 | transport_reopens | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 16->24 | transport_stable | 2 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 24->32 | transport_reopens | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 24->32 | transport_stable | 2 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 32->48 | transport_reopens | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 32->48 | transport_stable | 2 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 48->64 | transport_reopens | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 48->64 | transport_stable | 2 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 64->96 | transport_reopens | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 64->96 | transport_stable | 2 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 96->128 | transport_reopens | 1 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 96->128 | transport_stable | 2 |
| asymmetric_edge_flip_control | 0.006 | relation_role | one_step_local_flow | 1->2 | transport_resolution_mismatch | 2 |

## Horizon Response Threshold Table

| perturbation | strength | probe | flow | first nonstable | first amplified | first weakened | first rerouted | first reopened | first collapsed | terminal saturation | latest interpretable |
|---|---:|---|---|---|---|---|---|---|---|---|---|
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 1->2 |  | 1->2 | 8->16 |  |  |  | 4->8 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 1->2 |  | 1->2 | 2->4 | 4->8 |  |  | 4->8 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 1->2 |  | 4->8 |  | 2->4 |  |  | 96->128 |
| asymmetric_edge_flip_control | 0.006 | relation_role | one_step_local_flow | 1->2 | 2->4 |  | 2->4 | 2->4 |  |  | 96->128 |
| small_edge_resample_control | 0.006 | full_state_hash | constrained_window_flow | 1->2 |  | 1->2 | 4->8 |  |  |  | 4->8 |
| small_edge_resample_control | 0.006 | full_state_hash | one_step_local_flow | 1->2 |  | 1->2 | 4->8 | 2->4 |  |  | 4->8 |
| small_edge_resample_control | 0.006 | relation_role | constrained_window_flow | 1->2 |  | 4->8 | 16->24 | 2->4 |  |  | 96->128 |
| small_edge_resample_control | 0.006 | relation_role | one_step_local_flow | 1->2 | 2->4 |  | 2->4 | 2->4 |  |  | 96->128 |

## Transport Viscosity Summary

Dominant viscosity read: `underpowered_or_unresolved`.

Mean response diversity score: `0.656`.

| perturbation | strength | probe | flow | class diversity | diversity score | viscosity score | viscosity read | first non-amplified | latest interpretable |
|---|---:|---|---|---:|---:|---:|---|---|---|
| asymmetric_edge_flip_control | 0.006 | full_state_hash | constrained_window_flow | 3 | 0.500 | 0.626 | underpowered_or_unresolved | 1->2 | 1->2 |
| asymmetric_edge_flip_control | 0.006 | full_state_hash | one_step_local_flow | 4 | 0.750 | 0.504 | underpowered_or_unresolved | 1->2 | 4->8 |
| asymmetric_edge_flip_control | 0.006 | relation_role | constrained_window_flow | 3 | 0.500 | 0.710 | low_viscosity_unstable_response | 2->4 | 1->2 |
| asymmetric_edge_flip_control | 0.006 | relation_role | one_step_local_flow | 4 | 0.750 | 0.672 | medium_viscosity_response_threshold | 2->4 | 96->128 |
| small_edge_resample_control | 0.006 | full_state_hash | constrained_window_flow | 3 | 0.500 | 0.572 | underpowered_or_unresolved | 1->2 | 4->8 |
| small_edge_resample_control | 0.006 | full_state_hash | one_step_local_flow | 4 | 0.750 | 0.502 | underpowered_or_unresolved | 1->2 | 4->8 |
| small_edge_resample_control | 0.006 | relation_role | constrained_window_flow | 4 | 0.750 | 0.534 | low_viscosity_unstable_response | 2->4 | 96->128 |
| small_edge_resample_control | 0.006 | relation_role | one_step_local_flow | 4 | 0.750 | 0.587 | medium_viscosity_response_threshold | 2->4 | 96->128 |

## Probe / Flow / Horizon-Pair Context Summary

### By Probe

| probe | contexts | full matched pass | response contexts | read |
|---|---:|---:|---:|---|
| full_state_hash | 20 | 20 | 20 | matched_marginal_separates |
| relation_role | 20 | 7 | 20 | context_specific_separation |

### By Flow Mode

| flow_mode | contexts | full matched pass | response contexts | read |
|---|---:|---:|---:|---|
| constrained_window_flow | 20 | 15 | 20 | context_specific_separation |
| one_step_local_flow | 20 | 12 | 20 | context_specific_separation |

### By Horizon Pair

| horizon_pair | contexts | full matched pass | response contexts | read |
|---|---:|---:|---:|---|
| short\|middle\|2\|4 | 4 | 4 | 4 | matched_marginal_separates |
| middle\|middle\|4\|8 | 4 | 3 | 4 | context_specific_separation |
| middle\|middle\|8\|16 | 4 | 3 | 4 | context_specific_separation |
| downstream\|downstream\|96\|128 | 4 | 3 | 4 | context_specific_separation |
| middle\|downstream\|16\|24 | 4 | 3 | 4 | context_specific_separation |
| downstream\|downstream\|32\|48 | 4 | 3 | 4 | context_specific_separation |
| short\|short\|1\|2 | 4 | 2 | 4 | context_specific_separation |
| downstream\|downstream\|24\|32 | 4 | 2 | 4 | context_specific_separation |
| downstream\|downstream\|48\|64 | 4 | 2 | 4 | context_specific_separation |
| downstream\|downstream\|64\|96 | 4 | 2 | 4 | context_specific_separation |

## Context Recommendation

| context | read | recommendation | score |
|---|---|---|---:|
| full_state_hash\|constrained_window_flow\|2->4 | matched_marginal_separates_interpretable | candidate_for_context_narrowing | 14.500 |
| full_state_hash\|constrained_window_flow\|1->2 | matched_marginal_separates_interpretable | candidate_for_context_narrowing | 14.500 |
| full_state_hash\|one_step_local_flow\|2->4 | matched_marginal_separates_interpretable | candidate_for_context_narrowing | 14.500 |
| full_state_hash\|one_step_local_flow\|1->2 | matched_marginal_separates_interpretable | candidate_for_context_narrowing | 14.500 |
| relation_role\|constrained_window_flow\|96->128 | matched_marginal_separates_interpretable | candidate_for_context_narrowing | 14.500 |
| relation_role\|constrained_window_flow\|16->24 | matched_marginal_separates_interpretable | candidate_for_context_narrowing | 14.500 |
| relation_role\|constrained_window_flow\|4->8 | matched_marginal_separates_interpretable | candidate_for_context_narrowing | 14.500 |
| relation_role\|constrained_window_flow\|8->16 | matched_marginal_separates_interpretable | candidate_for_context_narrowing | 14.500 |
| relation_role\|one_step_local_flow\|32->48 | matched_marginal_separates_interpretable | candidate_for_context_narrowing | 14.500 |
| relation_role\|one_step_local_flow\|2->4 | matched_marginal_separates_interpretable | candidate_for_context_narrowing | 14.500 |

## Horizon-Pair Comparison

Subspace alignment rows: `2308`.

## Readiness Levels

- ready_for_horizon_transport_smoke_expansion: `0`
- ready_for_horizon_transport_scaleup: `0`
- ready_for_horizon_transport_context_narrowing: `0`
- ready_for_horizon_transport_fixture_expansion: `0`
- ready_for_response_fixture_repair: `0`
- ready_for_horizon_transport_theory_note: `0`
- measurement_limits_note_recommended: `0`
- fixture_contract_passed: `1`
- ready_for_fixture_horizon_transport_tests: `0`
- ready_for_direct_channel_diagnostics: `0`
- not_ready_repair_required: `0`

## Next-Action Fork

`continue_transition_energy_substrates`

## Output Manifest

See `substrate_untethering_output_manifest.json`.

## Retained Audit Scope

This note is the retained audit artifact for external review. The full local
run remains under:

```text
results/local_runs/20260531_substrate_untethering_tiny_smoke_v4/
```

The following generated artifacts were intentionally not committed:

```text
horizon_transport_matrix_entries.csv
horizon_transport_matrix_sparse.npz
horizon_transport_row_item_manifest.csv
horizon_transport_column_item_manifest.csv
horizon_transport_svd_summary.csv
horizon_transport_detector_null_anatomy.csv
other large local CSV/NPZ intermediates
```

Reason: this was a tiny implementation/prognostic smoke, not a retained raw
matrix result. The compact tables below are sufficient for GPT/Codex audit of
the branch direction without pushing raw matrix artifacts.

## Compact Audit Tables

### Transition-Energy Families

| substrate_family | transition_energy_form | hand-built constraint vocabulary removed | probabilistic sampling used |
|---|---|---:|---:|
| constraint_template_current | current_constraint_template_scored_relation | 0 | 0 |
| locality_only | hamming_distance_plus_seeded_roughness | 1 | 0 |
| smooth_random_potential | hamming_distance_plus_beta_potential_delta_plus_seeded_roughness | 1 | 0 |
| budget_conservation | hamming_distance_plus_budget_delta_penalty_plus_seeded_roughness | 1 | 0 |

### Substrate Generation Diagnostics

| substrate_family | metric rows | mean frontier A state count | mean frontier B state count | baseline rows | perturbation rows |
|---|---:|---:|---:|---:|---:|
| budget_conservation | 132 | 109.424 | 124.000 | 44 | 88 |
| constraint_template_current | 132 | 61.364 | 69.364 | 44 | 88 |
| locality_only | 132 | 168.242 | 190.242 | 44 | 88 |
| smooth_random_potential | 132 | 101.303 | 114.455 | 44 | 88 |

### Matched Null Pass By Substrate Family

| substrate_family | matched-null rows | mean pass fraction | mean min observed percentile |
|---|---:|---:|---:|
| budget_conservation | 66 | 0.788 | 0.848 |
| constraint_template_current | 120 | 0.867 | 0.936 |
| locality_only | 120 | 0.758 | 0.789 |
| smooth_random_potential | 114 | 0.702 | 0.795 |

### Response By Substrate Family

| substrate_family | response rows | aligned amplification rows | aligned amplification fraction | interpretable rows | dominant response class |
|---|---:|---:|---:|---:|---|
| budget_conservation | 60 | 7 | 0.117 | 60 | transport_stable |
| constraint_template_current | 80 | 15 | 0.188 | 72 | transport_rerouted |
| locality_only | 80 | 0 | 0.000 | 74 | transport_reopens |
| smooth_random_potential | 76 | 10 | 0.132 | 76 | transport_stable |

### Transport Viscosity By Substrate Family

| substrate_family | viscosity rows | mean viscosity score | modal viscosity read |
|---|---:|---:|---|
| budget_conservation | 60 | 0.761 | high_viscosity_aligned_amplifier |
| constraint_template_current | 80 | 0.636 | underpowered_or_unresolved |
| locality_only | 80 | 0.485 | underpowered_or_unresolved |
| smooth_random_potential | 76 | 0.726 | underpowered_or_unresolved |

## Audit Read

This run is only a plumbing and directionality check. It does not establish
substrate-general horizon transport. It does show that the transition-energy
substrate path runs end-to-end across four families, that grammar-neutral probes
can be used, and that smooth-potential / budget-conservation families produce
nonzero aligned-amplification rows in this tiny setting.

The locality-only family did not produce aligned-amplification rows here and
instead leaned toward reopen behavior. That is useful: it suggests the next
run should test whether generic smoothness or approximate conservation is doing
real work rather than mere bounded local branching.

## Max-Entropy Transition Ensemble Direction

The intended next substrate target is:

```text
max_entropy_local_transition
```

The point is to sample transition graphs from macro constraints only:

```text
state count
alphabet size
coordinate count
local proposal radius
out-degree distribution
reversibility fraction
roughness / energy marginal profile
optional smoothness or budget marginal
```

That would further reduce hand-picked law vocabulary. The immediate next step
should still be a small-medium E0/E1/E2 run to establish stable behavior and
calibrate capacity before implementing the max-entropy ensemble.

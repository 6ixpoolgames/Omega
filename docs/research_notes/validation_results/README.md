# Validation Results

Retained validation notes are grouped by empirical branch. This folder is for
human-readable retained notes, not raw run output. Large generated artifacts
belong under local `results/` and should only be pushed when they are explicitly
small, curated, and useful.

For the project pitch and current formalism, read:

- `../../../README.md`
- `../../OMEGA_FORMALISM_PRIMER.md`

## Current Branch

- `baseline_witnesses/` contains small baseline-controlled witnesses for
  reduction pressure.
- `future_field_atlas/` contains the current active empirical branch.
- `stochastic_distinction_channel/` contains the finite stochastic-channel
  bridge into the formal probabilistic channel presentation.
- Root-level `finite_relational_adapter_*` files are small adapter-pilot
  checkpoint summaries retained next to the validation docs while this branch
  stabilizes. If they grow, move them into a dedicated
  `finite_relational_adapter/` subfolder.

Start with:

- `future_field_atlas/future_field_atlas_formal_interface_distinction_panel_result.md`
- `future_field_atlas/future_field_atlas_rank_order_boundary_visualization_note.md`
- `future_field_atlas/future_field_atlas_rank_order_boundary_class_expansion_result.md`
- `future_field_atlas/future_field_atlas_rank_order_boundary_neighbor_observable_sweep_result.md`
- `future_field_atlas/future_field_atlas_rank_order_boundary_medium_sweep_result.md`
- `future_field_atlas/future_field_atlas_rank_order_boundary_h64_smoke_result.md`
- `future_field_atlas/future_field_atlas_substrate_morphology_atlas_result.md`
- `future_field_atlas/future_field_atlas_shared_capacity_h64_smoke_result.md`
- `future_field_atlas/future_field_atlas_coupled_h64_mechanism_resolution_result.md`
- `future_field_atlas/future_field_atlas_coupled_h64_ladder_result.md`
- `future_field_atlas/future_field_atlas_coupled_worker_spool_scale_validation_result.md`
- `future_field_atlas/future_field_atlas_h128_calibration_pass_result.md`
- `baseline_witnesses/same_reachability_different_recovery_v0.md`
- `baseline_witnesses/same_entropy_different_recovery_profile_v0.md`
- `baseline_witnesses/same_frontier_morphology_different_loss_profile_v0.md`
- `baseline_witnesses/same_mutual_information_different_declared_recovery_v0.md`
- `baseline_witnesses/same_optimized_success_different_declared_recovery_v0.md`
- `baseline_witnesses/same_marginal_success_different_joint_success_v0.md`
- `baseline_witnesses/same_compression_score_different_merge_soundness_v0.md`
- `stochastic_distinction_channel/stochastic_registry_first_probe_result.md`
- `stochastic_distinction_channel/stochastic_thresholded_prob_non_erasure_result.md`
- `stochastic_distinction_channel/stochastic_channel_theorem_transfer_audit_result.md`
- `stochastic_distinction_channel/stochastic_distinction_channel_fixed_policy_result.md`
- `finite_relational_adapter_validation_v0.md`
- `finite_relational_adapter_useful_information_v0.json`
- `finite_relational_adapter_empirical_pilot_v0.json`
- `finite_relational_grid_obstacle_pilot_v0.json`
- `finite_relational_deterministic_layer_v0.json`

## Archived Branches

- `rfs_mb0/` contains horizon-transport, transition-energy, top-m, and
  measurement-branch results that led into Future Field Atlas.
- `rfs_mb1/` contains the neutral coupled-landscape exploratory branch.
- `rfs0/` contains strict reachable-futures measurement-floor results.
- `val0/` contains early constructor-task and neutral grammar results.
- `val1/` contains early multifield compatibility/interference results.

## Figures

- `figures/` remains shared for retained curated images referenced by result
  notes. If figure volume grows, split it by branch using the same naming
  scheme as this folder.

## Policy

Do not add new result notes directly to this folder root unless they are small
cross-branch validation checkpoints like the current finite relational adapter
pilot files. Put active Future Field Atlas results in `future_field_atlas/`.
Put historical or branch-specific results under the matching archive folder.
Keep raw generated data out of the repo unless the result note explicitly
justifies retaining it.

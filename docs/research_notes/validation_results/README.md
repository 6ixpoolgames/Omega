# Validation Results

Retained validation notes are grouped by empirical branch. This folder is for
human-readable retained notes, not raw run output. Large generated artifacts
belong under local `results/` and should only be pushed when they are explicitly
small, curated, and useful.

## Current Branch

- `future_field_atlas/` contains the current active empirical branch.

Start with:

- `future_field_atlas/future_field_atlas_rank_order_boundary_neighbor_observable_sweep_result.md`
- `future_field_atlas/future_field_atlas_rank_order_boundary_medium_sweep_result.md`
- `future_field_atlas/future_field_atlas_rank_order_boundary_h64_smoke_result.md`
- `future_field_atlas/future_field_atlas_substrate_morphology_atlas_result.md`
- `future_field_atlas/future_field_atlas_shared_capacity_h64_smoke_result.md`
- `future_field_atlas/future_field_atlas_coupled_h64_mechanism_resolution_result.md`
- `future_field_atlas/future_field_atlas_coupled_h64_ladder_result.md`
- `future_field_atlas/future_field_atlas_coupled_worker_spool_scale_validation_result.md`
- `future_field_atlas/future_field_atlas_h128_calibration_pass_result.md`

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

Do not add new result notes directly to this folder root. Put active Future
Field Atlas results in `future_field_atlas/`. Put historical or branch-specific
results under the matching archive folder. Keep raw generated data out of the
repo unless the result note explicitly justifies retaining it.

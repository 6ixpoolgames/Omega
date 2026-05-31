# Future Field Atlas Phase 0/1 Smoke Result

Status: clean instrument-build smoke completed after operator-native repair  
Primary output: `results/future_field_atlas/20260601_phase0_1_operator_refactor_h32/`  
Runner: `omega.future_field_atlas.run_future_field_atlas`  
Spec: `docs/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md`

## Executive Summary

The Future Field Atlas Phase 0/1 smoke completed cleanly and demonstrates the
new raw-topology-first instrument path:

```text
status: COMPLETED
workers: 4
conditions: 8
scans_completed: 8 / 8
elapsed_seconds: 17.274
errors: 0
horizon_max: 32
frontier_node_rows: 30801
frontier_edge_rows: 107409
target_rank_core_distance_rows: 8
known_mechanism_recovery_rows: 8
```

This is not a science run and not an Omega validation result. It is a clean
instrumentation smoke showing that the new package can generate lawful
single-frontier conditions, unfold reachable-frontier topology, save raw
node/edge/profile/core-fringe artifacts, emit sparse transport matrices, and
measure distance to the known low-rank core boundary anatomy without using the
old response taxonomy.

## What Changed

The new package is:

```text
omega.future_field_atlas
```

The implementation separates:

```text
calibration generator:
  lawful substrate and selection-operator condition construction

scanner:
  frontier unfolding and raw node/edge recording

mapper:
  reconstructible profile, membership, and core/fringe geometry maps

transport:
  adjacent and multiscale sparse transport artifacts

analyzer:
  continuous distance-to-target-rank-core metrics from raw topology

runner:
  thin orchestration, manifests, graceful status/progress/error outputs
```

The scanner does not classify response. Labels remain downstream convenience
views only.

After audit, condition identity is no longer the legacy treatment-arm string.
The native object is now a selection operator inside explicit specs:

```text
StateSpaceSpec
TransformationLawSpec
SelectionOperatorSpec
ObservableSpec
```

Each condition records:

```text
selection_operator_id
selection_operator_family
base_out_degree
effective_out_degree
core_rank_k
retained_rank_set
removed_rank_set
stochastic_selection_flag
seed_policy
```

Legacy names such as `drop_weakest_m4_to_core3` remain only as human-readable
aliases.

## Known-Mechanism Recovery

The Phase 1 calibration target was the previous hard top-m result:

```text
known mechanism:
  retained top-3 low-energy successor core

expected raw anatomy:
  baseline m=3 identifies the retained core
  m=4 with one weakest selected edge removed identifies the retained core
  m=5 with two weakest selected edges removed identifies the retained core
  baseline m=4/m=5 contain fringe boundary edges
  random deletion and strongest-edge deletion do not cleanly identify the core
```

The smoke expressed that anatomy as near-zero target-core distance for the
expected deterministic operators:

| selection operator | base out-degree | effective out-degree | retained ranks | core fraction | fringe fraction | distance to target-core geometry |
|---|---:|---:|---|---:|---:|---:|
| rank_prefix | 3 | 3 | 1;2;3 | 1.000 | 0.000 | 0.000 |
| rank_prefix | 4 | 4 | 1;2;3;4 | 0.750 | 0.250 | 0.188 |
| rank_prefix | 5 | 5 | 1;2;3;4;5 | 0.600 | 0.400 | 0.300 |
| rank_subset | 4 | 3 | 1;2;3 | 1.000 | 0.000 | 0.000 |
| rank_subset | 5 | 3 | 1;2;3 | 1.000 | 0.000 | 0.000 |
| rank_subset | 4 | 3 | 2;3;4 | 0.667 | 0.333 | 0.375 |
| stochastic_rank_subset | 4 | 3 | sampled | 0.743 | 0.257 | sampled |
| stochastic_rank_subset | 5 | 3 | sampled | 0.628 | 0.372 | sampled |

This is the intended calibration split. It does not say the atlas has
validated the prior response result. It says the raw topology artifacts contain
enough rank/core/fringe structure to express the known mechanism as operator
geometry and continuous distances rather than response labels.

## Artifacts Emitted

Primary local artifacts:

```text
future_field_atlas_manifest.json
future_field_atlas_run_config.json
future_field_atlas_status.json
future_field_atlas_progress.csv
future_field_atlas_errors.csv
future_field_atlas_report.md
frontier_nodes_by_horizon.csv
frontier_edges_by_step.csv
frontier_profile_by_horizon.csv
frontier_membership_timeseries.csv
core_fringe_boundary_by_horizon.csv
raw_transport_matrices_adjacent.npz
raw_transport_matrices_adjacent_manifest.csv
raw_transport_matrices_multiscale.npz
raw_transport_matrices_multiscale_manifest.csv
transport_flow_composition_residuals.csv
target_rank_core_distance_summary.csv
known_mechanism_recovery_summary.csv
rank_core_recovery_by_horizon.csv
boundary_recovery_by_horizon_pair.csv
```

The raw CSV/NPZ artifacts are local generated outputs and should not be pushed
to the public repository.

The old `known_mechanism_recovery_summary.csv` file is retained as a
compatibility alias. The primary operator-native summary is now
`target_rank_core_distance_summary.csv`.

## Interpretation

The operator-native repair makes the clean build more principled:

```text
generate lawful substrates;
unfold reachable frontiers;
record topology;
map geometry;
contrast conditions;
label only as a derived view.
```

The first smoke supports continuing with the Future Field Atlas Phase 0/1
instrument rather than extending the old monolithic horizon-transport runner.

## Recommended Next Step

Do one more slightly larger Phase 1 calibration pass before coupled-frontier
implementation:

```text
horizon_max: 64 or 128
groups: 2 to 4
fresh_seeds_per_group: 1
start_samples: 1 to 2
workers: 8 to 18
keep labels off
keep raw artifacts local
```

Proceed to coupled future-field scans only if the raw-topology recovery split
persists and the emitted artifacts remain reconstructible from scanner output.

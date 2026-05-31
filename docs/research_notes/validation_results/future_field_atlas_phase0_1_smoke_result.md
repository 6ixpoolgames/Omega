# Future Field Atlas Phase 0/1 Smoke Result

Status: clean instrument-build smoke completed  
Primary output: `results/future_field_atlas/20260601_phase0_1_h32_smoke/`  
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
elapsed_seconds: 14.517
errors: 0
horizon_max: 32
frontier_node_rows: 30273
frontier_edge_rows: 105867
known_mechanism_recovery_rows: 8
```

This is not a science run and not an Omega validation result. It is a clean
instrumentation smoke showing that the new package can generate lawful
single-frontier conditions, unfold reachable-frontier topology, save raw
node/edge/profile/core-fringe artifacts, emit sparse transport matrices, and
recover the known low-rank core boundary anatomy without using the old response
taxonomy.

## What Changed

The new package is:

```text
omega.future_field_atlas
```

The implementation separates:

```text
generator:
  lawful substrate and boundary-control condition construction

scanner:
  frontier unfolding and raw node/edge recording

mapper:
  reconstructible profile, membership, and core/fringe geometry maps

transport:
  adjacent and multiscale sparse transport artifacts

analyzer:
  known-mechanism recovery from raw topology

runner:
  thin orchestration, manifests, graceful status/progress/error outputs
```

The scanner does not classify response. Labels remain downstream convenience
views only.

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

The smoke recovered that anatomy from raw core/fringe rank features:

| boundary control | base m | effective m | core fraction | fringe fraction | recovered top-3 core |
|---|---:|---:|---:|---:|---:|
| baseline_m3 | 3 | 3 | 1.000 | 0.000 | 1 |
| baseline_m4 | 4 | 4 | 0.750 | 0.250 | 0 |
| baseline_m5 | 5 | 5 | 0.600 | 0.400 | 0 |
| drop_weakest_m4_to_core3 | 4 | 3 | 1.000 | 0.000 | 1 |
| drop_two_weakest_m5_to_core3 | 5 | 3 | 1.000 | 0.000 | 1 |
| random_delete_one_m4_to_core3 | 4 | 3 | 0.755 | 0.245 | 0 |
| random_delete_two_m5_to_core3 | 5 | 3 | 0.584 | 0.416 | 0 |
| drop_strongest_m4_to_m3 | 4 | 3 | 0.667 | 0.333 | 0 |

This is the intended calibration split. It does not say the atlas has
validated the prior response result. It says the raw topology artifacts contain
enough rank/core/fringe structure to distinguish the known mechanism without
response labels.

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
known_mechanism_recovery_summary.csv
rank_core_recovery_by_horizon.csv
boundary_recovery_by_horizon_pair.csv
```

The raw CSV/NPZ artifacts are local generated outputs and should not be pushed
to the public repository.

## Interpretation

The clean build appears pointed in the right direction:

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

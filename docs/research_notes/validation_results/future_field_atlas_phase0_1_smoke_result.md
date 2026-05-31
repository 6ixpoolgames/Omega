# Future Field Atlas Phase 0/1 Clean Slate Smoke Result

Status: clean instrument-build smoke completed after schema teardown
Primary output: `results/future_field_atlas/20260601_phase0_1_clean_slate_h32/`
Runner: `omega.future_field_atlas.run_future_field_atlas`
Spec: `docs/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md`
Glossary: `docs/FUTURE_FIELD_ATLAS_GLOSSARY.md`

## Executive Summary

The Future Field Atlas Phase 0/1 smoke completed cleanly after removing the
legacy treatment-arm adapter surface from the runtime path.

```text
status: COMPLETED
instrument_version: 0.2.0
workers: 4
conditions: 8
scans_completed: 8 / 8
elapsed_seconds: 15.997
errors: 0
horizon_max: 32
frontier_node_rows: 30801
frontier_edge_rows: 107409
target_rank_core_distance_rows: 8
```

This remains an instrument smoke, not a science result and not an Omega
validation result. The purpose was to verify that the atlas can express the
calibration branch through mathematical operators rather than historical
treatment-arm names.

## What Changed

The clean atlas runtime now uses:

```text
StateSpaceSpec
TransformationLawSpec
SelectionOperatorSpec
ObservableSpec
```

Runtime outputs no longer emit:

```text
boundary_control
condition_role
human_label
legacy_boundary_control_alias
legacy_role_alias
base_m
effective_m
perturbation_family
perturbation_strength
known_mechanism_recovery_summary.csv
```

The historical translations were moved to
`docs/FUTURE_FIELD_ATLAS_GLOSSARY.md`. That document is for humans only and is
not imported by the runner.

## Native Operator Interface

The smoke used the clean operator syntax:

```text
rank_prefix:m=3
rank_prefix:m=4
rank_prefix:m=5
rank_subset:m=4:retain=1|2|3:remove=4
rank_subset:m=5:retain=1|2|3:remove=4|5
stochastic_rank_subset:m=4:effective=3
stochastic_rank_subset:m=5:effective=3
rank_subset:m=4:retain=2|3|4:remove=1
```

The runner no longer accepts `--boundary-controls`.

## Primary Artifacts

The clean smoke emitted:

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
rank_core_recovery_by_horizon.csv
boundary_recovery_by_horizon_pair.csv
```

Generated CSV/NPZ artifacts remain local and should not be pushed to the repos.

## Calibration Readout

The clean atlas expresses the known calibration split as continuous
rank-boundary geometry, not as a boolean recovery label.

```text
rank_prefix:m=3                            distance 0.000
rank_prefix:m=4                            distance 0.188
rank_prefix:m=5                            distance 0.300
rank_subset:m=4:retain=1|2|3:remove=4      distance 0.000
rank_subset:m=5:retain=1|2|3:remove=4|5    distance 0.000
rank_subset:m=4:retain=2|3|4:remove=1      distance 0.375
```

The stochastic rank-subset controls are retained as raw sampled operators with
blank target-rank distance where no deterministic retained-rank set exists.

## Interpretation

The teardown succeeded. The Future Field Atlas runtime is now much closer to
the intended formal layer:

```text
lawful finite state space
transformation law
selection operator
frontier scan
observable map
continuous distance readout
```

The next code extension should add new formal specs or operators directly.
Historical names should stay in the glossary and in old result notes only.

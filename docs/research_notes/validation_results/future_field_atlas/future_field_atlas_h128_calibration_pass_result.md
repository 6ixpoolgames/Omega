# Future Field Atlas H128 Calibration Pass Result

Status: medium calibration pass completed  
Primary output: `results/future_field_atlas/20260601_phase0_1_calibration_h128_g4_fresh2_start2/`  
Runner: `omega.future_field_atlas.run_future_field_atlas`

## Executive Summary

This was a medium Future Field Atlas calibration pass, not a science result.
The goal was to verify that the publication-schema atlas remains reconstructible
at H128 with broader groups, fresh seeds, start states, gzip output, and the
current selection-operator calibration fixture.

```text
status: COMPLETED
workers: 18
conditions: 64
scans_completed: 128 / 128
errors: 0
horizon_max: 128
horizon_schedule: 0..32, 48, 64, 96, 128
elapsed_seconds: 1762.763
frontier_node_rows: 564213
frontier_edge_rows: 7767333
csv_output_mode: gzip
reconstruction_audit_passed: 1
artifact_completeness_statuses: complete
```

All reconstruction audits passed:

```text
condition_identity_traceability: PASS, 8341082 checked, 0 failed
frontier_profile_reconstructs_from_node_and_edge_rows: PASS, 4736 checked, 0 failed
rank_boundary_geometry_reconstructs_from_edge_rows: PASS, 4736 checked, 0 failed
adjacent_transport_matrices_reconstruct_from_edge_rows: PASS, 4096 checked, 0 failed
selection_operator_geometry_reconstructs_from_rank_boundary_rows: PASS, 64 checked, 0 failed
```

## Output Manageability

Default gzip output kept the medium H128 run manageable:

```text
total output size: 172.7 MB
frontier_edges_by_step.csv.gz: 143.6 MB
raw_transport_matrices_multiscale.npz: 14.4 MB
frontier_nodes_by_horizon.csv.gz: 10.2 MB
raw_transport_matrices_adjacent.npz: 3.2 MB
all other files combined: about 1.4 MB
```

The raw edge artifact remains the dominant storage object, but gzip keeps this
run well below the uncompressed H64 compact-output footprint.

## Timing Read

The run exposed a finalization bottleneck:

```text
worker scan phase completed 128 / 128 scans by elapsed_seconds: 18.872
final status completed at elapsed_seconds: 1762.763
post-scan finalization time: about 1743.9 seconds
```

Interpretation:

```text
The calibration scan itself is cheap on the desktop hardware. The bottleneck is
post-scan artifact construction, matrix construction, compression, and final
manifest/report writing. Scaling beyond this point should focus on finalization
architecture, not simply increasing worker count.
```

## Calibration Geometry

Operator-level means across 8 condition instances per operator:

| selection operator | distance to prefix-3 | inside fraction | outside fraction | mean frontier states |
|---|---:|---:|---:|---:|
| `rank_prefix:m=3` | 0.000 | 1.000 | 0.000 | 60.70 |
| `rank_prefix:m=4` | 0.250 | 0.750 | 0.250 | 133.48 |
| `rank_prefix:m=5` | 0.400 | 0.600 | 0.400 | 210.33 |
| `rank_subset:m=4:retain=1|2|3:remove=4` | 0.000 | 1.000 | 0.000 | 60.70 |
| `rank_subset:m=5:retain=1|2|3:remove=4|5` | 0.000 | 1.000 | 0.000 | 60.70 |
| `rank_subset:m=4:retain=2|3|4:remove=1` | 0.389 | 0.667 | 0.333 | 123.13 |
| `stochastic_rank_subset:m=4:effective=3` | n/a | 0.747 | 0.253 | 121.66 |
| `stochastic_rank_subset:m=5:effective=3` | n/a | 0.605 | 0.395 | 182.37 |

The calibration fixture behaves as expected: deterministic operators retaining
the rank-1/2/3 prefix have zero distance to the prefix-3 observable; expansion,
strongest-edge deletion, and stochastic selections do not collapse into that
same operator geometry.

## Transport Composition

Transport composition residual rows:

```text
rows: 28160
composition_status: ok for all rows
support_composition_status: ok for all rows
path_count_composition_status: ok for all rows
weighted_mass_composition_status: not_defined_unit_edge_weights_only
```

This confirms the support/path-count residual instrumentation is behaving at
this scale. Weighted mass residuals remain intentionally undefined in the
current unit-edge-weight atlas.

## Claim Boundary

This result is an instrumentation and calibration result only. It does not
claim Omega validation, agency detection, valuer detection, identity detection,
candidate promotion, holdout readiness, or coupled-frontier behavior.

## Recommendation

The atlas is calibration-ready at medium H128 scale, but not yet scale-optimized
for substantially larger runs. Before a much larger pre-coupling or coupled
run, repair the finalization path:

```text
1. record scan-phase and finalization-phase timings separately;
2. stream or partition raw node/edge artifacts by scan or block;
3. make large matrix construction optionally deferred or chunked;
4. consider a columnar backend for raw topology;
5. keep gzip CSV as the default small/medium audit format.
```

The next engineering objective should be finalization throughput and output
architecture. The next science objective can then use the same calibration
fixture with less risk of spending wall time on artifact materialization.

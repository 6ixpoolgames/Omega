# RFS-MB0 Horizon-Transport Response Surface H128 Scaleup Result

Date: 2026-05-31 local / 2026-05-30 UTC  
Spec: `docs/RFS_MB0_HORIZON_TRANSPORT_RESPONSE_SURFACE_H128_SCALEUP_SPEC.md`  
Runner: `omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair`  
Local output: `results/local_runs/20260531_h128_response_surface_regenerated_scaleup/`

Generated CSV/JSON outputs remain local-only and should not be committed.

Note: the local status JSON records the pre-commit `git_commit` because the
instrumentation was implemented and run before this retained report commit. The
runner changes and retained report are committed together.

## 1. Executive Summary

The H128 response-surface scaleup completed cleanly on regenerated design-set
inputs. Horizon transport remained matched-marginal-separated out to `H=128`,
with no terminal-saturation or undercoverage flags in the emitted matrices.

The main empirical read is now sharper:

```text
stable at short horizons;
amplified-aligned at middle/deep horizons;
no full-run weakened/rerouted/reopened/collapsed empirical classes.
```

The new response taxonomy fixtures passed `8 / 8`, including the new
`transport_amplified_aligned`, `transport_weakened`, `transport_rerouted`, and
`transport_reopens` fixtures. In the full empirical scaleup, only
`transport_stable` and `transport_amplified_aligned` appeared:

```text
transport_stable: 235
transport_amplified_aligned: 381
```

The prior broad `transport_control_equivalent` bucket has therefore been
replaced for this branch by a more specific read: high-alignment spectral-mass
amplification.

Recommended next action:

```text
write_horizon_transport_theory_note
```

Do not open holdout, graph-channel diagnostics, direct channel causality,
candidate promotion, or Omega/agency/value claims from this result alone.

## 2. Claim Boundary

Allowed:

```text
horizon-transport matrices did or did not build with adequate coverage to H128;
matched marginal detector nulls did or did not separate;
response classes did or did not vary by perturbation strength and horizon;
terminal saturation did or did not dominate extended horizons.
```

Forbidden:

```text
Omega detected;
agent detected;
valuer detected;
identity detected;
candidate promoted;
holdout ready;
graph-channel causality shown.
```

Counters remained clean:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## 3. Run Shape and Local Artifact Policy

Scoped regeneration was used because the committed default selection had only
20 groups. A full substrate rebuild was not needed.

Regenerated inputs:

```text
selection: results/local_runs/20260531_h128_regenerated_boundary_selection_top64/focused_boundary_group_selection.csv
corrected: results/local_runs/20260531_h128_regenerated_detector_instrumentation_top28/corrected_group_classification.csv
source_run: results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep
```

Regeneration result:

```text
focused groups selected: 28
corrected groups: 28
corrected classes:
  independent_axis_recurrent_but_collision_limited: 24
  weak_control_bundle_recurrence: 4
upstream focused recurrence jobs: 1344 / 1344
upstream errors: 0
```

H128 run shape:

```text
groups: 28
design_groups: 16
holdout_groups: 12
fresh_seeds_per_group: 6
start_samples_list: 2,4,8,16
probes: constraint_profile_hash,constraint_violation_count_plus_local_tuple
workers: 18
job_batch_size: 4
null_replicates: 15
```

Perturbation ladder:

```text
small_edge_resample_control: 0.006,0.008,0.010,0.012,0.015,0.020,0.030
asymmetric_edge_flip_control: 0.006,0.008,0.010,0.012,0.015,0.020,0.030
```

Completion:

```text
status: COMPLETED
jobs_completed: 11520 / 11520
elapsed_seconds: 2196.206
errors: 0
matrix_count: 660
detector_null_rows: 1584
matched_marginal_summary_rows: 132
perturbation_response_rows: 616
```

## 4. Response Taxonomy Fixture Status

The expanded fixture contract passed:

| fixture | expected | observed | passed |
|---|---|---|---:|
| block_transport_signal | marginal_residual_fraction passes matched marginal null | `1:3` | 1 |
| marginal_fakeout | bimarginal matched null fails | `0:1` | 1 |
| corridor_stable_response | `transport_stable` | `transport_stable:1` | 1 |
| trap_collapse_response | `transport_collapses` | `transport_collapses:1` | 1 |
| amplified_aligned_response | `transport_amplified_aligned` | `transport_amplified_aligned:1` | 1 |
| weakened_response | `transport_weakened` | `transport_weakened:1` | 1 |
| rerouted_response | `transport_rerouted` | `transport_rerouted:1` | 1 |
| reopens_response | `transport_reopens` | `transport_reopens:1` | 1 |

This fixture pass calibrates response-class emission only. It is not empirical
evidence for Omega or any candidate.

## 5. Matrix Coverage and Horizon-Pair Coverage

Required H128 horizon pairs were emitted:

```text
0->1
1->2
2->4
4->8
8->16
16->24
24->32
32->48
48->64
64->96
96->128
```

Coverage gate:

```text
horizon_transport_matrix_coverage: passed
observed: 1.0
```

The run emitted `60` matrices per horizon pair:

```text
15 conditions x 2 probes x 2 flow modes = 60
```

## 6. Detector-Null and Matched-Marginal Results

Detector gates:

| gate | passed | observed |
|---|---:|---|
| horizon_transport_matrix_coverage | 1 | 1.0 |
| detector_null_sections_separate | 1 | separate outputs written |
| structure_detector_null_separation | 1 | passed |
| detector_null_replicate_power | 1 | 15 |
| matched_marginal_detector_null_separation | 1 | 3/3 families passed |
| synthetic_fixture_contract | 1 | 8/8 |

Matched marginal summaries:

| null family | contexts | read |
|---|---:|---|
| row_marginal_matched_transport_null | 44 | detector_null_separates |
| column_marginal_matched_transport_null | 44 | detector_null_separates |
| row_column_marginal_matched_transport_null | 44 | detector_null_separates |

## 7. Terminal Saturation Diagnostics

Terminal saturation did not dominate the extended horizons.

| horizon pair | terminal fraction | undercoverage fraction | normal interpretation fraction |
|---|---:|---:|---:|
| 0->1 | 0 | 0 | 1 |
| 1->2 | 0 | 0 | 1 |
| 2->4 | 0 | 0 | 1 |
| 4->8 | 0 | 0 | 1 |
| 8->16 | 0 | 0 | 1 |
| 16->24 | 0 | 0 | 1 |
| 24->32 | 0 | 0 | 1 |
| 32->48 | 0 | 0 | 1 |
| 48->64 | 0 | 0 | 1 |
| 64->96 | 0 | 0 | 1 |
| 96->128 | 0 | 0 | 1 |

Extended-horizon entropy and concentration were stable:

```text
largest_entry_mass_share_mean at 96->128: 0.0216069656
transport_entropy_mean at 96->128: 6.0661506181
terminal_saturation_flagged_rows: 0 / 660
```

Interpretation: H128 rows are not being treated as terminal-saturation-only or
undercovered diagnostics in this run.

## 8. Response Class by Strength and Horizon Pair

Global response counts:

| response class | count |
|---|---:|
| transport_stable | 235 |
| transport_amplified_aligned | 381 |

Class metric means:

| response class | mean alignment | mean mass delta | mean entropy delta | mean response magnitude |
|---|---:|---:|---:|---:|
| transport_stable | 0.997884 | 0.023931 | 0.028627 | 0.049845 |
| transport_amplified_aligned | 0.971027 | 0.381268 | 0.036334 | 0.386080 |

Simplified strength/horizon pattern:

```text
asymmetric_edge_flip_control:
  p0.006 first amplifies at 16->24
  p0.008 through p0.020 first amplify at 8->16
  p0.030 first amplifies at 4->8

small_edge_resample_control:
  p0.006 is mixed; some probe/flow contexts remain stable, some first amplify at 8->16
  p0.008 first amplifies at 8->16 or 16->24 depending on probe/flow
  p0.010 through p0.015 first amplify at 8->16
  p0.020 first amplifies at 4->8 or 8->16 depending on probe/flow
  p0.030 first amplifies at 4->8
```

No empirical full-run rows were classified as:

```text
transport_weakened
transport_rerouted
transport_reopens
transport_collapses
transport_control_equivalent
```

## 9. Horizon Response Threshold Table

First nonstable horizon equals first amplified-aligned horizon in the full
scaleup.

| family | strength | first nonstable/amplified horizon |
|---|---:|---|
| asymmetric_edge_flip_control | 0.006 | 16->24 |
| asymmetric_edge_flip_control | 0.008 | 8->16 |
| asymmetric_edge_flip_control | 0.010 | 8->16 |
| asymmetric_edge_flip_control | 0.012 | 8->16 |
| asymmetric_edge_flip_control | 0.015 | 8->16 |
| asymmetric_edge_flip_control | 0.020 | 8->16 |
| asymmetric_edge_flip_control | 0.030 | 4->8 |
| small_edge_resample_control | 0.006 | mixed: none or 8->16 |
| small_edge_resample_control | 0.008 | mixed: 8->16 or 16->24 |
| small_edge_resample_control | 0.010 | 8->16 |
| small_edge_resample_control | 0.012 | 8->16 |
| small_edge_resample_control | 0.015 | 8->16 |
| small_edge_resample_control | 0.020 | mixed: 4->8 or 8->16 |
| small_edge_resample_control | 0.030 | 4->8 |

Latest interpretable horizon:

```text
96->128 for all perturbation/probe/flow rows
```

Terminal saturation horizon:

```text
none emitted
```

## 10. Probe / Flow / Horizon Context Summary

All `44` probe/flow/horizon contexts passed all three matched marginal
families and had interpretable response rows.

The highest priority context rows were tied across many contexts. The first
reported context was:

```text
constraint_profile_hash | constrained_window_flow | 24->32
```

This should not be read as unique context selection yet. It is a tie-breaking
artifact of the current scoring.

## 11. Readiness Levels

```text
readiness_level: ready_for_horizon_transport_theory_note
ready_for_horizon_transport_theory_note: 1
ready_for_direct_channel_diagnostics: 0
ready_for_response_fixture_repair: 0
not_ready_repair_required: 0
measurement_limits_note_recommended: 0
```

## 12. Next-Action Fork

```text
write_horizon_transport_theory_note
```

Rationale:

```text
H128 exposes a clear horizon-dependent amplification surface:
  stable short horizons;
  amplified-aligned middle/deep horizons;
  response threshold moves earlier as perturbation strength rises;
  no terminal saturation dominance.
```

This deserves a theory/instrument note before further engineering.

## 13. Output Manifest

Core local output directory:

```text
results/local_runs/20260531_h128_response_surface_regenerated_scaleup/
```

Core generated outputs:

```text
horizon_transport_h128_run_config.json
horizon_transport_h128_status.json
horizon_transport_h128_progress_checkpoints.csv
horizon_transport_h128_errors.csv
horizon_transport_h128_output_manifest.json
horizon_transport_matrix_manifest.csv
horizon_transport_matrix_summary.csv
horizon_transport_coverage.csv
horizon_transport_svd_summary.csv
horizon_transport_subspace_alignment.csv
horizon_transport_participation_summary.csv
horizon_transport_entropy_summary.csv
horizon_transport_detector_null_summary.csv
horizon_transport_detector_null_anatomy.csv
horizon_transport_detector_null_gate_results.csv
horizon_transport_matched_marginal_summary.csv
horizon_transport_perturbation_manifest.csv
horizon_transport_response_profile_summary.csv
horizon_transport_response_classification.csv
horizon_transport_response_flags.csv
response_class_by_strength_and_horizon_pair.csv
horizon_response_threshold_table.csv
horizon_transport_terminal_saturation_summary.csv
horizon_transport_saturation_by_horizon_pair.csv
horizon_transport_by_probe_summary.csv
horizon_transport_by_flow_mode_summary.csv
horizon_transport_by_horizon_pair_summary.csv
horizon_transport_context_recommendation.csv
horizon_transport_fixture_results.csv
horizon_transport_response_fixture_summary.csv
rfs_mb0_horizon_transport_response_surface_h128_scaleup_result.md
```

Generated outputs stay local unless explicitly promoted.

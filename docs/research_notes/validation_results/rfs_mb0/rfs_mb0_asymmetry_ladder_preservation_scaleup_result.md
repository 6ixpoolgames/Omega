# RFS-MB0 Asymmetry-Ladder Preservation Scaleup Result

Date: 2026-05-31

Local output:

```text
results/local_runs/20260531_asymmetry_ladder_preservation_scaleup/
```

Promoted visualization bundle:

```text
docs/research_notes/validation_results/figures/20260531_asymmetry_ladder_preservation_scaleup/
```

Runner:

```text
omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair
```

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_ASYMMETRY_LADDER_TRANSITION_ENERGY_SUBSTRATE_SPEC.md
```

## Purpose

This was the first preservation-focused asymmetry-ladder scaleup after the
initial seed-scaled ladder batch reached `preservation_asymmetry_loadbearing`.

The run expanded:

```text
design_groups: 4
fresh_seeds_per_group: 4
start_samples_list: 2,4
perturbation strengths: 0.006,0.010,0.015,0.020
null_replicates: 9
```

It retained locality, directional asymmetry, combined asymmetry, and the
historical constraint-template substrate as comparators.

This remains design-set substrate characterization only. It is not holdout
validation, candidate promotion, graph causality, Omega detection, agency
detection, identity detection, value detection, or valuer detection.

## Run Shape

```text
status: COMPLETED
workers: 18
jobs_completed: 14976 / 14976
elapsed_seconds: 4304.994
errors: 0
matrix_count: 9846
substrate_family_variant_count: 26
null_replicates: 9
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
terminal_saturation_flagged_rows: 0
readiness_level: preservation_asymmetry_loadbearing
next_action_fork: expand_preservation_asymmetry_family
```

All detector gates passed:

```text
horizon_transport_matrix_coverage: passed
structure_detector_null_separation: passed
detector_null_replicate_power: passed
matched_marginal_detector_null_separation: passed
synthetic_fixture_contract: 8 / 8
```

## Visualization Outputs

The compact figure bundle contains:

```text
raw_transport_matrix_atlas.png
horizon_response_metric_rgb_spectrogram.png
horizon_response_class_spectrogram.png
transport_viscosity_score_spectrogram.png
alignment_mass_entropy_panels.png
saturation_coverage_profile.png
response_threshold_ladder.png
```

The raw transport atlas and RGB spectrogram are the most useful first-pass
views. They are diagnostics of measured transport outputs, not additional
claim status. The run did not include raw frontier state sampling, so there is
no raw substrate-state frontier heatmap for this batch.

## Family-Level Read

| substrate family | response rows | interpretable rows | measurement-limit rows | aligned fraction | stable | aligned | rerouted | reopened |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| locality_only | 352 | 352 | 0 | 0.000 | 329 | 0 | 23 | 0 |
| directional_asymmetry | 1056 | 1056 | 0 | 0.000 | 1011 | 0 | 37 | 8 |
| preservation_asymmetry | 4920 | 4560 | 360 | 0.174 | 3020 | 795 | 275 | 395 |
| combined_asymmetry | 2112 | 2112 | 0 | 0.000 | 2036 | 0 | 71 | 5 |
| constraint_template_current | 352 | 352 | 0 | 0.233 | 206 | 82 | 24 | 40 |

Matched-marginal pass fractions:

```text
locality_only:              0.826
directional_asymmetry:      0.788
preservation_asymmetry:     0.890
combined_asymmetry:         0.816
constraint_template_current:0.833
```

Interpretation:

```text
The preservation-asymmetry positive read strengthened rather than washed out.
Locality remained non-aligned. Directional and combined asymmetry remained
rerouting-bearing but not aligned-amplifying in this grid.
```

## Invariant-Level Read

| macro invariant | response rows | interpretable rows | baseline-missing rows | aligned fraction | aligned count | weakened | rerouted | reopened |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hamming_weight_or_nonzero_count | 2464 | 2464 | 0 | 0.057 | 140 | 0 | 12 | 155 |
| symbol_histogram_distance | 2464 | 2464 | 0 | 0.154 | 380 | 75 | 262 | 245 |
| total_coordinate_mass | 2104 | 1744 | 360 | 0.158 | 275 | 0 | 72 | 0 |

The important update is that `symbol_histogram_distance` moved from
differentiated-but-not-aligned in the smaller seed-scaled batch to a clean
aligned, rerouting, reopening, and weakening profile here, with no
baseline-missing rows.

Practical ordering after this run:

```text
symbol_histogram_distance:
  best current all-around preservation-asymmetry target;
  aligned response plus diversified response profile;
  no baseline-missing rows.

total_coordinate_mass:
  still strong aligned response;
  still paired-baseline limited.

hamming_weight_or_nonzero_count:
  clean low-complexity comparator;
  weaker aligned response but no baseline-missing rows.
```

## Beta-Ladder Read

The requested beta ladder did not produce a graded response across
`0.25,0.5,1.0,2.0,4.0`. Within each invariant kind, response summaries were
effectively identical across beta settings.

A spot edge-overlap audit showed the parameter is wired correctly but saturates
early:

```text
hamming_weight_or_nonzero_count:
  beta 0.01 already differs from beta 0;
  beta 0.05 through 16 share the same selected-edge plateau in the audited job.

symbol_histogram_distance:
  beta 0.01, 0.05, 0.1, and 0.25 move through distinct overlaps;
  beta 0.25 through 16 share the same audited plateau.

total_coordinate_mass:
  beta 0.01, 0.05, and 0.1 move through distinct overlaps;
  beta 0.25 through 16 share the same audited plateau.
```

Interpretation:

```text
Future beta sweeps should focus below 0.25, not above it.
The present beta ladder mostly tested the saturated preservation regime.
```

## Directional And Combined Read

Directional asymmetry:

```text
aligned rows: 0
rerouted rows: 37
reopened rows: 8
measurement-limit rows: 0
```

Combined asymmetry:

```text
aligned rows: 0
rerouted rows: 71
reopened rows: 5
measurement-limit rows: 0
```

The combined family remained clean but did not yet produce synergy. It should
not be abandoned, but the immediate empirical leverage is still in preservation
asymmetry.

## Interpretation

This run materially strengthens the asymmetry-ladder result:

```text
preservation asymmetry is robustly loadbearing under matched controls;
the positive read no longer depends only on total coordinate mass;
symbol-composition preservation is now the best clean next target;
beta values above 0.25 are too coarse for sensitivity mapping;
directional and combined asymmetry are useful for rerouting/threshold work, not
aligned-amplification claims in the current grid.
```

This remains below any Omega, agency, identity, value, holdout, or candidate
claim.

## Recommended Next Step

Do a low-beta preservation-asymmetry sensitivity run before moving to a
max-entropy ensemble:

```text
substrate families:
  preservation_asymmetry
  locality_only comparator
  constraint_template_current comparator

macro_invariant_kind:
  symbol_histogram_distance
  total_coordinate_mass
  hamming_weight_or_nonzero_count

macro_invariant_beta:
  0
  0.005
  0.01
  0.025
  0.05
  0.10
  0.15
  0.25

add:
  selected-edge overlap by beta
  response threshold by beta
  baseline availability by invariant and horizon pair
```

If that run confirms a stable low-beta phase transition, then the max-entropy
asymmetry ensemble has a clearer target: constrain symbol-composition and total
coordinate mass marginals, with nonzero support as the simple comparator.

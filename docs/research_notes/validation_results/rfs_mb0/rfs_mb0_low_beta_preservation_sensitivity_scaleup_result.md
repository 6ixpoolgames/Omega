# RFS-MB0 Low-Beta Preservation Sensitivity Scaleup Result

Date: 2026-05-31

Local output:

```text
results/local_runs/20260531_low_beta_preservation_sensitivity_scaleup/
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

This run repaired the missing beta-overlap instrumentation and then tested the
low-beta preservation-asymmetry ladder recommended by the prior preservation
scaleup.

The key question was:

```text
Does preservation-asymmetry response turn on gradually below beta 0.25, and is
that response backed by actual selected-edge movement rather than a parameter
labeling artifact?
```

This remains design-set substrate characterization only. It is not holdout
validation, candidate promotion, graph causality, Omega detection, agency
detection, identity detection, value detection, or valuer detection.

## Repair Added

The runner now emits:

```text
selected_edge_overlap_by_beta.csv
```

This table compares the selected transition graph for each sampled beta against
the beta-0 graph for the same substrate job.

The smoke check completed before the full run:

```text
results/local_runs/20260531_low_beta_overlap_repair_smoke_v2/
status: COMPLETED
jobs_completed: 78 / 78
errors: 0
selected_edge_overlap_by_beta_rows: 24
```

## Run Shape

```text
status: COMPLETED
workers: 18
jobs_completed: 14976 / 14976
elapsed_seconds: 4776.098
errors: 0
matrix_count: 10026
substrate_family_variant_count: 26
null_replicates: 9
selected_edge_overlap_sample_jobs: 96
selected_edge_overlap_by_beta_rows: 24
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

## Family-Level Read

| substrate family | response rows | interpretable rows | measurement-limit rows | aligned fraction | stable | aligned | rerouted | reopened |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| locality_only | 352 | 352 | 0 | 0.000 | 329 | 0 | 23 | 0 |
| preservation_asymmetry | 8232 | 8016 | 216 | 0.056 | 6873 | 445 | 331 | 330 |
| constraint_template_current | 352 | 352 | 0 | 0.233 | 206 | 82 | 24 | 40 |

Matched-marginal pass fractions:

```text
locality_only:               0.826
preservation_asymmetry:      0.854
constraint_template_current: 0.833
```

Interpretation:

```text
Preservation asymmetry remains loadbearing under the low-beta ladder.
Locality remains non-aligned. The historical constraint-template comparator
remains stronger per row, but is no longer the only source of aligned response.
```

## Beta Response Read

| beta | response rows | interpretable rows | baseline-missing rows | aligned fraction | aligned | weakened | rerouted | reopened |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 1056 | 1056 | 0 | 0.000 | 0 | 0 | 69 | 0 |
| 0.005 | 1056 | 1056 | 0 | 0.000 | 0 | 0 | 24 | 0 |
| 0.01 | 1056 | 1056 | 0 | 0.000 | 0 | 0 | 22 | 0 |
| 0.025 | 1056 | 1056 | 0 | 0.000 | 0 | 0 | 34 | 0 |
| 0.05 | 1056 | 1056 | 0 | 0.027 | 28 | 0 | 4 | 34 |
| 0.10 | 984 | 912 | 72 | 0.122 | 111 | 11 | 67 | 114 |
| 0.15 | 984 | 912 | 72 | 0.161 | 147 | 11 | 56 | 103 |
| 0.25 | 984 | 912 | 72 | 0.174 | 159 | 15 | 55 | 79 |

Interpretation:

```text
Aligned response does not appear at beta 0.005, 0.01, or 0.025.
The first aggregate aligned response appears at beta 0.05.
The response strengthens through beta 0.10, 0.15, and 0.25.
```

## Invariant-Level Read

| macro invariant | response rows | interpretable rows | baseline-missing rows | aligned fraction | aligned | weakened | rerouted | reopened |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hamming_weight_or_nonzero_count | 2816 | 2816 | 0 | 0.040 | 112 | 0 | 46 | 124 |
| symbol_histogram_distance | 2816 | 2816 | 0 | 0.060 | 168 | 37 | 217 | 206 |
| total_coordinate_mass | 2600 | 2384 | 216 | 0.069 | 165 | 0 | 68 | 0 |

Practical read:

```text
symbol_histogram_distance:
  cleanest all-around target;
  no baseline-missing rows;
  aligned response plus weakened/rerouted/reopened diversity.

total_coordinate_mass:
  strongest per-interpretable-row aligned fraction at beta >= 0.10;
  still paired-baseline limited.

hamming_weight_or_nonzero_count:
  clean low-complexity comparator;
  aligned response appears at beta 0.05 and plateaus in this grid.
```

## Selected-Edge Overlap Read

The selected-edge audit sampled 32 substrate jobs per invariant and had no
errors.

Mean Jaccard overlap versus beta 0:

| invariant | beta 0.005 | beta 0.01 | beta 0.025 | beta 0.05 | beta 0.10 | beta 0.15 | beta 0.25 |
|---|---:|---:|---:|---:|---:|---:|---:|
| hamming_weight_or_nonzero_count | 0.882 | 0.787 | 0.538 | 0.359 | 0.359 | 0.359 | 0.359 |
| symbol_histogram_distance | 0.866 | 0.783 | 0.593 | 0.417 | 0.355 | 0.342 | 0.342 |
| total_coordinate_mass | 0.932 | 0.882 | 0.755 | 0.597 | 0.506 | 0.506 | 0.506 |

Interpretation:

```text
The low-beta ladder is real at the substrate level: even beta 0.005 changes the
selected transition graph. The response threshold is therefore not caused by an
unwired beta parameter.

The graph-selection plateau begins around:

hamming_weight_or_nonzero_count: beta 0.05
symbol_histogram_distance:      beta 0.15
total_coordinate_mass:          beta 0.10
```

## Interpretation

This run strengthens the preservation-asymmetry branch, but narrows the live
question:

```text
Preservation asymmetry is loadbearing.
Low beta changes the transition graph before aligned response appears.
The first response threshold is around beta 0.05.
The strongest clean response family remains symbol-composition preservation.
Total-coordinate mass remains live but baseline-limited.
Hamming/nonzero count remains a simple comparator, not the main target.
```

This is still below any Omega, agency, value, candidate, or holdout claim.

## Recommended Next Step

Move toward a max-entropy local transition ensemble preflight, with this low
beta map as the calibration target.

For the next empirical pass:

```text
primary invariant:
  symbol_histogram_distance

comparators:
  hamming_weight_or_nonzero_count
  total_coordinate_mass only if paired-baseline availability is explicitly guarded

beta focus:
  0.04
  0.05
  0.075
  0.10
  0.15

required retained audits:
  selected_edge_overlap_by_beta
  paired_baseline_availability_by_invariant/horizon
  matched marginal nulls
  response threshold by beta
```

Do not return to high-beta expansion unless the question is deliberately about
saturated preservation regimes.

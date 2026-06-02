# RFS-MB0 Transition-Energy Substrate Characterization Result

Date: 2026-05-31

Spec: `docs/specs/archive/rfs_mb0/RFS_MB0_TRANSITION_ENERGY_SUBSTRATE_CHARACTERIZATION_RUN_SPEC.md`

Local output:

`results/local_runs/20260531_transition_energy_characterization_larger_smoke/`

## Executive Summary

Decision: `locality_only_baseline_confirmed`.

Next action: `write_transition_energy_substrate_atlas_note`.

The larger characterization smoke completed cleanly and produced a first substrate-response atlas over 22 transition-energy variants. The main result is not convergence across families. It is separation of response profiles:

```text
locality_only:
  remains a clean baseline in this grid, with no aligned amplification

smooth_random_potential:
  remains response-bearing but not aligned-amplifying under this smoothness/beta grid

budget_conservation:
  produces aligned amplification, especially total-coordinate-mass variants,
  but the strongest aligned rows are coverage-limited

constraint_template_current:
  remains a useful comparator, but no longer the only substrate with aligned response
```

This is a substrate-characterization result for the horizon-transport instrument. It is not Omega validation, holdout readiness, candidate promotion, agency detection, value detection, identity detection, life detection, or graph-channel causality.

## Implementation Repair Before Run

Before this run, the response baseline key was repaired.

The prior multi-family path keyed perturbation responses by:

```text
probe, flow, H_a, H_b
```

That was insufficient for multi-family substrate comparison because a perturbation matrix from one substrate family could be compared to a baseline matrix from another family/variant. The runner now keys response baselines by:

```text
substrate_family, substrate_variant, probe, flow, H_a, H_b
```

This repair is loadbearing for the characterization result.

## Run Shape

```text
status: completed
finalization_reason: all_jobs_completed
workers: 18
jobs_completed: 7744 / 7744
elapsed_seconds: 1378.371
errors: 0
null_replicates: 13
matrix_count: 10324
substrate_family_variant_count: 22
perturbation_response_rows: 9410
matched_marginal_detector_null_gate_passed: 1
detector_null_replicate_powered: 1
synthetic_fixture_contract: passed, 8 / 8
response_diversity_score_mean: 0.102557
```

The fixture smoke also passed `8 / 8` before the empirical run. A compact preflight completed `968 / 968` jobs with zero errors before the larger run.

## Claim Boundary

Forbidden claims remain forbidden:

```text
Omega detected
agent detected
valuer detected
identity detected
life detected
self-replication detected
candidate promoted
holdout ready
graph-channel causality shown
```

Required counters remained closed:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## Substrate Capacity and Matched Nulls

| substrate_family | matrices | coverage mean | matched pass mean | capacity read |
|---|---:|---:|---:|---|
| budget_conservation | 4032 | 0.776 | 0.888 | substrate_capacity_available |
| constraint_template_current | 484 | 0.791 | 0.856 | substrate_capacity_available |
| locality_only | 1452 | 0.725 | 0.831 | substrate_capacity_available |
| smooth_random_potential | 4356 | 0.755 | 0.801 | substrate_capacity_available |

The global matched-marginal gate passed. Coverage is adequate for a smoke, but not clean enough to rank substrate families by aligned amplification alone.

## Response Profiles By Family

| substrate_family | response rows | interpretable rows | dominant response | aligned fraction | stable | amplified | weakened | rerouted | reopens | resolution mismatch |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| budget_conservation | 3690 | 3420 | transport_stable | 0.109 | 2589 | 402 | 120 | 51 | 258 | 270 |
| constraint_template_current | 440 | 440 | transport_stable | 0.180 | 228 | 79 | 0 | 94 | 39 | 0 |
| locality_only | 1320 | 1320 | transport_stable | 0.000 | 1221 | 0 | 0 | 99 | 0 | 0 |
| smooth_random_potential | 3960 | 3960 | transport_stable | 0.000 | 3480 | 0 | 20 | 229 | 231 | 0 |

## Budget-Conservation Analysis

| budget_kind | response rows | dominant response | aligned fraction | note |
|---|---:|---|---:|---|
| total_coordinate_mass | 1050 | transport_stable | 0.203 | strongest aligned fraction, but 270 resolution-mismatch rows |
| hamming_weight_or_nonzero_count | 1320 | transport_stable | 0.084 | clean matched-null behavior, lower aligned fraction |
| symbol_histogram_distance | 1320 | transport_stable | 0.059 | more weakened/reopened response, lower aligned fraction |

Budget-conservation remains the most interesting non-template family, but the run does not justify calling total-coordinate-mass the winner without coverage repair.

## Smooth-Potential Analysis

| parameter | value | response rows | dominant response | aligned fraction |
|---|---|---:|---|---:|
| potential_smoothness | 0.25 | 1320 | transport_stable | 0.000 |
| potential_smoothness | 0.65 | 1320 | transport_stable | 0.000 |
| potential_smoothness | 0.9 | 1320 | transport_stable | 0.000 |
| potential_beta | 0.25 | 1320 | transport_stable | 0.000 |
| potential_beta | 0.5 | 1320 | transport_stable | 0.000 |
| potential_beta | 1 | 1320 | transport_stable | 0.000 |

Smooth-potential variants were not inert: they produced rerouting, reopening, and a small amount of weakening. But they did not produce aligned amplification in this grid.

## Locality-Only Baseline

All three locality-only roughness variants produced no aligned-amplification rows:

```text
roughness_low:     aligned fraction 0.000
roughness_current: aligned fraction 0.000
roughness_high:    aligned fraction 0.000
```

This supports using locality-only as a baseline for bounded local branching rather than treating locality by itself as the candidate object.

## Constraint-Template Comparator

The current constraint-template comparator still produced aligned amplification:

```text
aligned fraction: 0.180
dominant response: transport_stable
rerouted rows: 94
reopened rows: 39
```

The comparator remains useful, but the budget family shows that aligned response is not exclusive to the original hand-built constraint vocabulary.

## Interpretation

The instrument now behaves like a substrate-response atlas:

```text
locality alone:
  baseline, not enough for aligned amplification in this grid

smooth potential:
  response-bearing, mostly stable/rerouted/reopened, no aligned amplification here

budget conservation:
  aligned response is present, with total mass strongest but coverage-limited

constraint templates:
  still positive comparator, no longer unique
```

The practical next step is not max-entropy immediately. The immediate next step is to write the transition-energy substrate atlas note and decide whether to repair coverage around budget-conservation or move to a deliberately constrained max-entropy local transition ensemble with budget-like marginal constraints.

## Local Artifact Policy

Raw run artifacts remain local-only and were not committed. The largest local files are:

| artifact | size |
|---|---:|
| `horizon_transport_column_item_manifest.csv` | 252.290 MB |
| `horizon_transport_row_item_manifest.csv` | 237.099 MB |
| `horizon_transport_matrix_entries.csv` | 162.354 MB |
| `horizon_transport_subspace_alignment.csv` | 43.743 MB |
| `horizon_transport_detector_null_anatomy.csv` | 21.715 MB |

Only this retained note, code changes, and project documentation updates should be committed.

## Next Action

Recommended next action:

```text
write_transition_energy_substrate_atlas_note
```

Then choose between:

```text
repair_budget_coverage
implement_max_entropy_local_transition
```

The max-entropy path should preserve the lesson from this run: do not erase substrate-law differences by forcing all families into one response curve.

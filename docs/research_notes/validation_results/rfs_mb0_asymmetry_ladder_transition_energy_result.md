# RFS-MB0 Asymmetry-Ladder Transition-Energy Result

Date: 2026-05-31

Local output:

```text
results/local_runs/20260531_asymmetry_ladder_seed_scaled/
```

Runner:

```text
omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair
```

Spec:

```text
docs/RFS_MB0_ASYMMETRY_LADDER_TRANSITION_ENERGY_SUBSTRATE_SPEC.md
```

## Purpose

This was the first implemented asymmetry-ladder run after the baseline-symmetry
guard repair. It tested whether minimal transition-energy ingredients produce
different horizon-transport response regimes:

```text
E0 locality_only
E1 directional_asymmetry
E2 preservation_asymmetry
E3 combined_asymmetry
constraint_template_current comparator
```

This remains a design-set substrate-characterization run. It is not holdout
validation, candidate promotion, graph causality, Omega detection, agency
detection, identity detection, value detection, or valuer detection.

## Implementation Repairs

The runner now supports first-class asymmetry-ladder families:

```text
directional_asymmetry:
  E(s,t) = d(s,t) + alpha * (A(t) - A(s)) + roughness

preservation_asymmetry:
  E(s,t) = d(s,t) + beta * |I(t) - I(s)| + roughness

combined_asymmetry:
  E(s,t) = d(s,t) + alpha * (A(t) - A(s))
         + beta * |I(t) - I(s)| + roughness
```

The older raw family `budget_conservation` remains reproducible, but the
current ladder uses `preservation_asymmetry` for the public/theory-facing
macro-invariant substrate.

The response summaries also retain the baseline-symmetry guard:

```text
transport_baseline_missing rows are measurement-limit rows.
They remain counted, but they do not determine dominant response class or
interpretable aligned-amplification fractions.
```

## Run Shape

```text
status: COMPLETED
workers: 18
jobs_completed: 640 / 640
elapsed_seconds: 829.711
errors: 0
matrix_count: 3402
substrate_family_variant_count: 16
null_replicates: 7
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

## Family-Level Response Read

| substrate family | response rows | interpretable rows | measurement-limit rows | aligned fraction | stable | aligned | rerouted | reopened |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| locality_only | 176 | 176 | 0 | 0.000 | 176 | 0 | 0 | 0 |
| directional_asymmetry | 352 | 352 | 0 | 0.000 | 336 | 0 | 16 | 0 |
| preservation_asymmetry | 976 | 904 | 72 | 0.084 | 762 | 76 | 50 | 12 |
| combined_asymmetry | 1056 | 1056 | 0 | 0.000 | 1001 | 0 | 55 | 0 |
| constraint_template_current | 176 | 176 | 0 | 0.080 | 106 | 14 | 56 | 0 |

Matched-marginal pass fractions:

```text
locality_only:              0.856
directional_asymmetry:      0.723
preservation_asymmetry:     0.872
combined_asymmetry:         0.775
constraint_template_current:0.826
```

## Invariant Read

| macro invariant | response rows | interpretable rows | baseline-missing rows | aligned fraction | aligned count | rerouted | reopened |
|---|---:|---:|---:|---:|---:|---:|---:|
| hamming_weight_or_nonzero_count | 704 | 704 | 0 | 0.051 | 36 | 8 | 12 |
| symbol_histogram_distance | 702 | 696 | 6 | 0.000 | 0 | 49 | 0 |
| total_coordinate_mass | 626 | 560 | 66 | 0.071 | 40 | 48 | 0 |

Interpretation:

```text
preservation_asymmetry is the first loadbearing family in this ladder pass;
total coordinate mass still carries aligned response but keeps paired-baseline
availability limits;
nonzero support now also shows weaker aligned response with no baseline-missing
rows;
symbol composition remains differentiated but not aligned-amplifying here.
```

## Directional And Combined Read

Directional asymmetry produced differentiated response without aligned
amplification:

```text
alpha 0.25:
  rerouted rows: 20
  aligned rows: 0

alpha 0.75:
  rerouted rows: 51
  aligned rows: 0
```

Combined asymmetry passed matched marginal nulls and produced rerouting, but it
did not yet outperform preservation asymmetry:

```text
combined_asymmetry:
  response_rows: 1056
  interpretable_rows: 1056
  aligned rows: 0
  rerouted rows: 55
  baseline_missing rows: 0
```

This may be a parameterization issue rather than a negative result. The sparse
combined grid only tested two alpha/beta pairs.

## Interpretation

This run gives a clean first positive read for the new substrate posture:

```text
locality_only behaves as a baseline;
directional_asymmetry contributes rerouting/differentiated response;
preservation_asymmetry carries aligned amplification under matched controls;
combined_asymmetry is clean but not yet synergistic in the tested grid.
```

The result strengthens the case that the next empirical object is not the old
hand-built constraint vocabulary. The live object is the response profile of
reachable-future transport under minimally specified transition-energy
ingredients, with macro-invariant preservation currently the strongest hook.

## Next

Recommended next action:

```text
expand_preservation_asymmetry_family
```

Concrete next run:

```text
increase seed and start diversity;
keep matched marginal nulls mandatory;
keep baseline-missing rows gated as measurement limits;
expand preservation beta and invariant variants before widening combined
asymmetry;
use directional/combined runs to map rerouting thresholds, not aligned response
alone.
```

Max-entropy transition ensembles remain the likely next substrate architecture
after this ladder branch has enough resolution to specify which marginals should
be constrained.

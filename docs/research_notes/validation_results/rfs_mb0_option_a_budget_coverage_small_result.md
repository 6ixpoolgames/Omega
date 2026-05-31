# RFS-MB0 Option A Budget-Coverage Small Smoke Result

Date: 2026-05-31

Local output:

```text
results/local_runs/20260531_option_a_budget_coverage_small/
```

Runner:

```text
omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair
```

## Purpose

This was a deliberately small Option A follow-up to the transition-energy
substrate atlas note. It tested whether the budget-conservation coverage caveat
from the larger substrate-characterization run was mainly a retained-matrix
resolution issue.

This is not a theory-validation run, not a candidate-promotion gate, and not a
claim about Omega, agency, identity, value, or valuerhood.

## Run Shape

```text
status: COMPLETED
workers: 18
jobs_completed: 396 / 396
elapsed_seconds: 463.18
errors: 0
matrix_count: 3915
substrate_family_variant_count: 9
null_replicates: 13
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
readiness_level: substrate_characterization_underpowered
next_action_fork: continue_transition_energy_characterization
```

The formal readiness label is underpowered because the characterization decision
guard expects a much larger run. That label is expected for this small smoke.

## Tested Variants

Only `budget_conservation` substrates were tested, with:

```text
budget kind:
  total_coordinate_mass
  hamming_weight_or_nonzero_count
  symbol_histogram_distance

budget weight:
  0.25
  1
  2
```

## Coverage Result

The retained-matrix coverage repair worked mechanically.

```text
hamming_weight_or_nonzero_count:
  matrix_count: 484 per weight
  coverage_mean: 0.9898
  coverage_min: 0.8693

symbol_histogram_distance:
  matrix_count: 453 per weight
  coverage_mean: 0.9994
  coverage_min: 0.9926

total_coordinate_mass:
  matrix_count: 368 per weight
  coverage_mean: 0.9627
  coverage_min: 0.8722
```

Compared with the larger characterization run, the budget-conservation coverage
caveat is substantially repaired. The remaining limitation is no longer simple
matrix-retention loss.

## Response Read

```text
hamming_weight_or_nonzero_count:
  response_rows: 440 per weight
  interpretable_rows: 440
  aligned_amplification_fraction: 0.0432
  dominant_response: transport_stable
  resolution_mismatch_rows: 0
  matched_marginal_pass_fraction: 0.9924 to 1.0000

symbol_histogram_distance:
  response_rows: 414 per weight
  interpretable_rows: 390
  aligned_amplification_fraction: 0.1498
  dominant_response: transport_stable
  response mix: stable, amplified-aligned, rerouted, reopened, weakened
  resolution_mismatch_rows: 24
  matched_marginal_pass_fraction: 0.8034 to 0.8291

total_coordinate_mass:
  response_rows: 342 per weight
  interpretable_rows: 260
  aligned_amplification_fraction: 0.2018
  dominant_response: transport_stable
  response mix: stable, amplified-aligned, rerouted
  resolution_mismatch_rows: 82
  matched_marginal_pass_fraction: 0.8333 to 0.8590
```

The weight ladder did not materially change the profile in this small run.

## Baseline-Mismatch Audit

The remaining `total_coordinate_mass` mismatch is concentrated in:

```text
actual_control_name: small_edge_resample_control
flow_mode: constrained_window_flow
status: baseline_missing
```

For `budget_total_coordinate_mass`, constrained-window baseline matrices were
present only for:

```text
0->1
1->2
```

but constrained-window `small_edge_resample_control` perturbation matrices were
present through:

```text
96->128
```

So the late-horizon mismatch rows are not negative evidence against
`total_coordinate_mass`. They are an instrumentation/baseline-availability
limit: perturbation matrices were emitted for contexts where the paired
baseline matrix was not available.

## Interpretation

Option A succeeded at its narrow purpose: budget-conservation matrix coverage can
be repaired without changing the substrate family.

The ranking after repair is more nuanced:

```text
hamming_weight_or_nonzero_count:
  cleanest matched-null and response support;
  weakest aligned-amplification signal

symbol_histogram_distance:
  best current middle path;
  near-complete coverage, nontrivial response diversity, moderate aligned response

total_coordinate_mass:
  strongest aligned-amplification fraction;
  still instrument-limited by missing late-horizon constrained-window baselines
```

The most conservative next read is:

```text
budget conservation remains live;
symbol-histogram budget distance deserves a widened characterization run;
total-coordinate mass should not be promoted or demoted until baseline symmetry
is repaired or response summaries filter contexts without paired baselines.
```

## Recommended Next Step

Before another large budget-conservation run, repair or explicitly gate response
classification so baseline/perturbation matrix availability is symmetric across:

```text
substrate variant
probe
flow mode
horizon pair
perturbation family
```

Then rerun a small targeted check on `total_coordinate_mass` and
`symbol_histogram_distance`.

If the goal is only to proceed pragmatically, the next larger smoke should favor:

```text
budget kind:
  symbol_histogram_distance
  total_coordinate_mass

keep:
  hamming_weight_or_nonzero_count as the clean low-signal comparator
```

Claim boundary remains unchanged:

```text
No holdout scoring.
No candidate promotion.
No Omega detection.
No agency/value/identity/valuerhood claim.
No graph-channel causality claim.
```

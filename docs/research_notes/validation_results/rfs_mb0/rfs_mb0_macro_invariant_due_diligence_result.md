# RFS-MB0 Macro-Invariant Due-Diligence Result

Date: 2026-05-31

Public-facing substrate name:

```text
macro-invariant transition substrate
```

Theory-facing substrate name:

```text
asymmetry-constrained transition energy
```

Implementation/raw-output name retained for compatibility:

```text
budget_conservation
budget_kind
budget_weight
budget_delta
```

Local output:

```text
results/local_runs/20260531_option_a_budget_due_diligence_guarded/
```

Runner:

```text
omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair
```

## Purpose

This was the larger-but-not-large due-diligence run for Option A before moving
to Option B, the max-entropy local transition ensemble.

The run asked whether the macro-invariant / asymmetry-constrained substrate
remains loadbearing after:

```text
full retained-matrix coverage repair;
clear separation of baseline-missing rows from true resolution mismatch;
larger breadth across invariant definitions and invariant weights;
matched-marginal detector nulls with 13 replicates.
```

This remains an instrument/substrate-characterization run. It is not holdout
validation, candidate promotion, Omega detection, agency detection, value
detection, identity detection, or valuerhood detection.

## Implementation Repairs

Two small instrumentation repairs were made before retaining the result.

First, response classes now distinguish:

```text
transport_baseline_missing:
  paired baseline matrix was unavailable

transport_insufficient_common_items:
  baseline and perturbation shared too little row/column support

transport_resolution_mismatch:
  other non-computed resolution mismatch
```

This matters because the earlier small smoke collapsed all non-computed
responses into `transport_resolution_mismatch`, which hid the fact that the
total-coordinate-mass limitation was mainly paired-baseline availability.

Second, the runner now accepts public/theory aliases:

```text
macro_invariant
asymmetry_constrained
asymmetry_constrained_transition_energy
macro_asymmetry_constrained
conserved_distinction
invariant_constrained
```

These canonicalize to the retained implementation name `budget_conservation` so
older result files and scripts remain reproducible.

## Run Shape

```text
status: COMPLETED
workers: 18
jobs_completed: 4620 / 4620
elapsed_seconds: 1658.146
errors: 0
matrix_count: 6720
substrate_family_variant_count: 15
null_replicates: 13
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
terminal_saturation_flagged_rows: 0
readiness_level: budget_conservation_loadbearing
next_action_fork: expand_budget_conservation_family
```

Translated read:

```text
readiness_level:
  macro_invariant_loadbearing

next_action_fork:
  expand_macro_invariant_family
```

## Tested Invariant Variants

Raw implementation names:

```text
total_coordinate_mass
hamming_weight_or_nonzero_count
symbol_histogram_distance
```

Public/theory translations:

```text
total_coordinate_mass:
  total coordinate-mass invariant

hamming_weight_or_nonzero_count:
  nonzero-support invariant

symbol_histogram_distance:
  symbol-composition invariant
```

Invariant weights:

```text
0.1
0.25
1
2
4
```

## Coverage Result

The coverage caveat is repaired.

Every tested variant had:

```text
coverage_mean: 1.0
coverage_min: 1.0
capacity_read: substrate_capacity_available
```

This means the due-diligence result is no longer limited by retained transport
matrix resolution.

## Response Summary

By invariant definition:

```text
nonzero-support invariant:
  response_rows: 2200
  interpretable_response_rows: 2200
  aligned_amplification_fraction: 0.061
  dominant_response: transport_stable
  baseline_missing: 0
  matched_null_pass_fraction: 0.985-1.000

symbol-composition invariant:
  response_rows: 2200
  interpretable_response_rows: 2200
  aligned_amplification_fraction: 0.106
  dominant_response: transport_stable
  response diversity: stable, amplified, weakened, rerouted, reopened
  baseline_missing: 0
  matched_null_pass_fraction: 0.780-0.811

total coordinate-mass invariant:
  response_rows: 1750
  interpretable_response_rows: 1300
  aligned_amplification_fraction: 0.203
  interpretable-only aligned fraction: 0.273
  dominant_response: transport_stable
  baseline_missing: 450
  matched_null_pass_fraction: 0.795-0.833
```

The total coordinate-mass invariant still has the strongest aligned response.
After taxonomy repair, its limitation is explicit:

```text
450 transport_baseline_missing rows
0 transport_resolution_mismatch rows
0 transport_insufficient_common_items rows
```

The missing rows are concentrated entirely in:

```text
invariant: total_coordinate_mass
perturbation: small_edge_resample_control
flow_mode: constrained_window_flow
```

So the remaining issue is paired-baseline availability for one response context,
not matrix coverage and not shared-support failure.

## Matched-Null Read

At family level:

```text
matched_null_rows: 1710
pass_fraction_mean: 0.866
min_observed_percentile_mean: 0.918
```

By invariant definition:

```text
nonzero-support invariant:
  strongest matched-null behavior;
  weakest aligned response

symbol-composition invariant:
  moderate matched-null behavior;
  best response diversity;
  no baseline-missing rows

total coordinate-mass invariant:
  strongest aligned response;
  acceptable family-level matched-null pass;
  still has paired-baseline availability limitation
```

## Interpretation

The due-diligence result supports continuing this path before Option B only in a
targeted way.

Conservative read:

```text
macro-invariant / asymmetry-constrained transition energy is loadbearing;
total coordinate mass is the strongest aligned-amplification invariant;
symbol composition is the cleanest diversified invariant;
nonzero support is the cleanest low-signal comparator.
```

What changed from the previous smoke:

```text
coverage is no longer the blocker;
resolution mismatch is no longer the right diagnosis;
baseline availability is now the remaining total-coordinate-mass caveat;
the formal characterization guard now passes as loadbearing.
```

## Recommendation

Do not spend a large run only repeating this exact Option A grid.

The next empirical move should be one of:

```text
1. one narrow total-coordinate-mass baseline-availability repair, if we want
   the cleanest possible Option A closure;

2. proceed to Option B, using macro-invariant constraints as explicit
   max-entropy macro constraints rather than treating them as hand-picked
   symbolic laws.
```

My recommendation:

```text
Proceed to Option B after noting this due diligence.
```

Postscript guard update:

```text
Before the asymmetry-ladder run, response summaries were patched so
transport_baseline_missing and other measurement-limit rows remain counted but
are excluded from dominant response class and aligned-amplification fractions.
The runner now also emits aligned_amplification_fraction_all_rows as an audit
denominator.
```

Tiny targeted guard check:

```text
jobs_completed: 84 / 84
errors: 0
fixture_contract: passed

total coordinate-mass:
  response_rows: 206
  interpretable_response_rows: 156
  measurement_limit_response_rows: 50
  aligned_amplification_fraction: 0.269
  aligned_amplification_fraction_all_rows: 0.204

symbol-composition:
  response_rows: 248
  interpretable_response_rows: 234
  measurement_limit_response_rows: 14
  aligned_amplification_fraction: 0.214
  aligned_amplification_fraction_all_rows: 0.202
```

Read:

```text
Baseline-missing rows are now auditable measurement limits rather than response
evidence. The asymmetry-ladder spec should use this guard.
```

Reason:

```text
Option A has done its job: it identified macro-invariant/asymmetry-constrained
transition energy as loadbearing and narrowed the residual issue to one
instrumentation context. The stronger scientific next step is to see whether a
max-entropy local transition ensemble can reproduce the useful response without
smuggling in a named substrate vocabulary.
```

## Claim Boundary

Closed:

```text
No holdout scoring.
No candidate promotion.
No Omega detection.
No agency detection.
No value detection.
No identity detection.
No valuerhood detection.
No graph-channel causality claim.
```

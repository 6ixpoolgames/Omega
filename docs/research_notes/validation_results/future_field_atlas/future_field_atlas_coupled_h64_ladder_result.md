# Future Field Atlas Coupled H64 Ladder Result

Status: completed cleanly  
Runner: `omega.future_field_atlas.run_coupled_future_field_atlas`  
Instrument version: `0.4.1`

## Summary

This was the first constrained coupled Future Field Atlas science pass after
the worker-spool and compact-retention repairs. It tests whether the current
coupled operator produces measurable product-vs-coupled future-field geometry
as coupling strength changes.

This is not an Omega validation result and does not claim interaction,
compatibility, support, capture, erasure, agency, identity, value, or
valuerhood.

Allowed claim:

```text
Under the current H64 pair8 design, the coupled rank-boundary mismatch penalty
shows a threshold-like transition from zero penalty to positive penalty. The
positive values 0.05, 0.10, 0.25, and 0.50 produce identical topology-derived
summary geometry at this resolution.
```

Blocked claims:

```text
Omega validation
coupled fields interact
compatibility detection
support / capture / erasure
agency
identity
value
valuerhood
```

## Design

Common configuration:

```text
horizon_max: 64
horizon_schedule: dense
pair_count: 8
groups: 8
workers: 4
raw_topology_output_mode: worker_spool
csv_output_mode: gzip
gzip_compresslevel: 1
selection_operator_a: rank_prefix:m=3
selection_operator_b: rank_subset:m=4:retain=1|2|3:remove=4
macro_invariant_kind: symbol_histogram_distance
macro_invariant_beta: 0.10
rank_boundary_k: 3
joint_effective_out_degree: 4
```

Coupled operator:

```text
joint candidate set:
  product successor candidates

joint energy:
  A candidate energy
  + B candidate energy
  + coupling_strength * abs(A rank-boundary offset - B rank-boundary offset)

joint selection:
  rank prefix over joint energy
```

Strength ladder:

```text
0.00
0.05
0.10
0.25
0.50
```

Important interpretation detail:

```text
coupling_strength = 0.00 is not a product-equivalence control.
It is the additive-energy joint rank-prefix selector with zero mismatch
penalty. The product baseline remains explicit in every run and is compared
against the coupled selector by the residual/marginal artifacts.
```

## Run Outputs

Local compact run folders:

```text
results/future_field_atlas/20260602_coupled_ladder_h64_pair8_c000/
results/future_field_atlas/20260602_coupled_ladder_h64_pair8_c005/
results/future_field_atlas/20260602_coupled_ladder_h64_pair8_c010/
results/future_field_atlas/20260602_coupled_ladder_h64_pair8_c025/
results/future_field_atlas/20260602_coupled_ladder_h64_pair8_c050/
```

Each run emitted `_retention_summary/` and then pruned raw
`coupled_pair_spool/` after the deletion plan returned:

```text
delete_raw_spools_allowed
```

Cross-run compact summary:

```text
results/future_field_atlas/20260602_coupled_ladder_h64_pair8_summary/
```

## Gate Results

All five ladder stages reported:

```text
status: COMPLETED
coupled_pairs_completed: 8 / 8
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS 3
medium_sweep_interpretation_allowed: 1
raw_spools_deleted: 1
```

## Run-Level Summary

| coupling | edges | nodes | mean residual | max residual | mean joint retention | min joint retention | mean A marginal retention | mean B marginal retention |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 22866722 | 3419750 | 0.191149 | 0.927172 | 0.808851 | 0.072828 | 0.980608 | 0.972859 |
| 0.05 | 22127782 | 3231039 | 0.183363 | 0.881137 | 0.816637 | 0.118863 | 1.000000 | 1.000000 |
| 0.10 | 22127782 | 3231039 | 0.183363 | 0.881137 | 0.816637 | 0.118863 | 1.000000 | 1.000000 |
| 0.25 | 22127782 | 3231039 | 0.183363 | 0.881137 | 0.816637 | 0.118863 | 1.000000 | 1.000000 |
| 0.50 | 22127782 | 3231039 | 0.183363 | 0.881137 | 0.816637 | 0.118863 | 1.000000 | 1.000000 |

Read:

```text
The tested positive strengths are not producing a smooth response ladder.
At this H64 pair8 resolution, the operator appears thresholded: zero penalty
differs from positive penalty, while 0.05 through 0.50 are numerically
identical after sorting rows and ignoring coupled-operator identity fields.
```

## Final-Horizon Pair Readout

At horizon 64, positive mismatch penalty improved joint support retention for
seven of eight pairs but sharply worsened one heavy pair.

| pair | residual H64 at 0.00 | residual H64 at 0.05+ | read |
|---|---:|---:|---|
| pair000 | 0.060000 | 0.030000 | lower residual |
| pair001 | 0.117497 | 0.048647 | lower residual |
| pair002 | 0.128000 | 0.061000 | lower residual |
| pair003 | 0.156292 | 0.066517 | lower residual |
| pair004 | 0.101136 | 0.026136 | lower residual |
| pair005 | 0.244091 | 0.752364 | much higher residual |
| pair006 | 0.087778 | 0.050000 | lower residual |
| pair007 | 0.098889 | 0.040000 | lower residual |

For positive strengths, A and B marginal retention means were both exactly
`1.0` in this design. The deformation is therefore not marginal erasure in the
primary readout. It is a restriction/reorganization of joint combinations
relative to the product baseline, with one heavy pair showing a much stronger
joint narrowing at H64.

## Mechanism Read

Current live interpretation:

```text
The rank-boundary mismatch term acts like a positive/zero switch in this
design, not a graded continuous control over the tested range.
```

The strongest instrument-native observation is:

```text
Positive mismatch penalty preserves component marginals while changing joint
support geometry.
```

The main caveat is pair heterogeneity:

```text
pair005 dominates the high-residual positive-penalty tail and should be
inspected before using aggregate residuals as a broad coupled-field read.
```

## Recommendation

Do not jump to H128 broad sweeps yet. The next best pass is a narrow
mechanism-resolution run:

```text
1. Add finer near-zero strengths:
   0.000, 0.005, 0.010, 0.020, 0.050

2. Add a true product-selector sanity run:
   joint_selection_family = product

3. Split pair005 from the other pairs:
   pair005 targeted H64/H128
   non-pair005 aggregate H64

4. Report pair-level, not only aggregate, residual/marginal geometry.
```

If the near-zero ladder still collapses into the same positive-penalty
geometry, treat the operator as rank-order thresholded and move the next design
toward rank-boundary ordering rather than scalar-strength tuning.

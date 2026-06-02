# Future Field Atlas Rank-Order Boundary Neighbor / Observable Sweep Result

Status: completed cleanly; rank-order class expansion target opened

Runner: `omega.future_field_atlas.run_coupled_future_field_atlas`

Spec: `docs/specs/current/FUTURE_FIELD_ATLAS_RANK_ORDER_BOUNDARY_NEIGHBOR_OBSERVABLE_SWEEP_SPEC.md`

## Summary

This pass executed the next rank-order-boundary coupled atlas step:

```text
Study A:
  H64 neighbor search over pair indexes 0,1,2,5,8-23

Study B:
  targeted H128 depth for new high-yield H64 neighbors

Study C:
  small H64 observable-extension smoke over hamming_weight_or_nonzero_count
  and total_coordinate_mass
```

The run changes the empirical read:

```text
pair005 is no longer the only high-residual marginal-preserving exemplar.
pair012 and pair014 reproduce the rank_order_boundary signature at H64.
pair012 and pair014 remain stable at targeted H128.
```

The observable-extension read is narrower:

```text
hamming_weight_or_nonzero_count:
  did not reproduce pair005-like high residual

total_coordinate_mass:
  did not reproduce pair005-like high residual

current high-yield rank_order_boundary signature:
  still specific to symbol_histogram_distance in the tested observable smokes
```

Allowed claim:

```text
Rank-order-boundary marginal-preserving joint restriction recurs in newly
sampled neighboring pairs under symbol_histogram_distance, with H128 stability
for pair012 and pair014.
```

Blocked claims:

```text
Omega validation
pre-proto-valuer / proto-valuer / valuer detection
agency / identity / value
compatibility detection
support / capture / erasure
interaction detection
holdout claim
broad substrate-general claim
```

## Preflight Repair

The uploaded spec required one implementation/spec correction before running.

Problem:

```text
Study A requested pair indexes 8-23 with groups: 8.
The current runner resolves pair_indexes against generated condition indexes.
With one operator and one beta, groups: 8 only creates indexes 0-7.
```

Repair:

```text
Study A was run with groups: 24.
The spec now states this explicitly.
```

A second preflight repair added an explicit supported macro-invariant list so
observable-extension smokes cannot silently alias an unknown observable name.

Supported atlas macro-invariant kinds at this revision:

```text
symbol_histogram_distance
symbol_histogram_l2
hamming_weight_or_nonzero_count
hamming_weight
nonzero_count
total_coordinate_mass
```

Validation:

```text
tests: 19 passed
```

Repair commit:

```text
2c70a8bfe366165a4e6a6e2b63106693e598d067
```

## Study A: H64 Neighbor Search

### Batch A

Run directory:

```text
results/future_field_atlas/20260602_rank_order_boundary_h64_neighbor_batch_a/
```

Pair indexes:

```text
0,1,2,5,8,9,10,11,12,13,14,15
```

Gate results:

```text
status: COMPLETED
horizon_max: 64
pair_count_realized: 12 / 12
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS 3
medium_sweep_interpretation_allowed: 1
elapsed_seconds: 858.244
source_git_commit: 2c70a8bfe366165a4e6a6e2b63106693e598d067
source_git_dirty: false
```

Artifact rows:

```text
joint edge rows: 44,252,061
joint node rows: 6,322,649
profile rows: 1,560
residual rows: 780
marginal rows: 780
```

Retention:

```text
total output GiB before raw-spool deletion: 2.390617
raw delete candidate GiB: 2.390488
raw spools deleted: yes
heaviest pair: pair010
heaviest pair edge share: 0.178479
```

Final-H64 pair table:

| pair | residual | joint retention | A retention | B retention | product support | coupled support |
|---|---:|---:|---:|---:|---:|---:|
| pair000 | 0.040000 | 0.960000 | 1.000000 | 1.000000 | 100 | 96 |
| pair001 | 0.050853 | 0.949147 | 1.000000 | 1.000000 | 8613 | 8175 |
| pair002 | 0.084000 | 0.916000 | 1.000000 | 1.000000 | 1000 | 916 |
| pair005 | 0.753455 | 0.246545 | 1.000000 | 1.000000 | 11000 | 2712 |
| pair008 | 0.062247 | 0.937753 | 1.000000 | 1.000000 | 7920 | 7427 |
| pair009 | 0.022472 | 0.977528 | 1.000000 | 1.000000 | 890 | 870 |
| pair010 | 0.338524 | 0.661476 | 1.000000 | 1.000000 | 11881 | 7859 |
| pair011 | 0.043333 | 0.956667 | 1.000000 | 1.000000 | 900 | 861 |
| pair012 | 0.842202 | 0.157798 | 1.000000 | 1.000000 | 11990 | 1892 |
| pair013 | 0.009524 | 0.990476 | 1.000000 | 1.000000 | 210 | 208 |
| pair014 | 0.512554 | 0.487446 | 1.000000 | 1.000000 | 2310 | 1126 |
| pair015 | 0.050101 | 0.949899 | 1.000000 | 1.000000 | 9900 | 9404 |

New high-yield H64 neighbors:

```text
pair012
pair014
```

### Batch B

Run directory:

```text
results/future_field_atlas/20260602_rank_order_boundary_h64_neighbor_batch_b/
```

Pair indexes:

```text
0,1,2,5,16,17,18,19,20,21,22,23
```

Gate results:

```text
status: COMPLETED
horizon_max: 64
pair_count_realized: 12 / 12
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS 3
medium_sweep_interpretation_allowed: 1
elapsed_seconds: 308.174
source_git_commit: 2c70a8bfe366165a4e6a6e2b63106693e598d067
source_git_dirty: false
```

Artifact rows:

```text
joint edge rows: 17,448,543
joint node rows: 2,513,241
profile rows: 1,560
residual rows: 780
marginal rows: 780
```

Retention:

```text
total output GiB before raw-spool deletion: 0.944264
raw delete candidate GiB: 0.944138
raw spools deleted: yes
heaviest pair: pair005
heaviest pair edge share: 0.365626
```

Final-H64 pair table:

| pair | residual | joint retention | A retention | B retention | product support | coupled support |
|---|---:|---:|---:|---:|---:|---:|
| pair000 | 0.040000 | 0.960000 | 1.000000 | 1.000000 | 100 | 96 |
| pair001 | 0.050853 | 0.949147 | 1.000000 | 1.000000 | 8613 | 8175 |
| pair002 | 0.084000 | 0.916000 | 1.000000 | 1.000000 | 1000 | 916 |
| pair005 | 0.753455 | 0.246545 | 1.000000 | 1.000000 | 11000 | 2712 |
| pair016 | 0.072222 | 0.927778 | 1.000000 | 1.000000 | 900 | 835 |
| pair017 | 0.045455 | 0.954545 | 1.000000 | 1.000000 | 1100 | 1050 |
| pair018 | 0.086168 | 0.913832 | 1.000000 | 1.000000 | 441 | 403 |
| pair019 | 0.020225 | 0.979775 | 1.000000 | 1.000000 | 890 | 872 |
| pair020 | 0.071818 | 0.928182 | 1.000000 | 1.000000 | 1100 | 1021 |
| pair021 | 0.020000 | 0.980000 | 1.000000 | 1.000000 | 100 | 98 |
| pair022 | 0.100000 | 0.900000 | 1.000000 | 1.000000 | 430 | 387 |
| pair023 | 0.047619 | 0.952381 | 1.000000 | 1.000000 | 210 | 200 |

New high-yield H64 neighbors:

```text
none
```

## Study B: Targeted H128 Neighbor Depth

Only `pair012` and `pair014` qualified for H128:

```text
joint_support_residual_final >= 0.4
A_marginal_retention_final >= 0.99
B_marginal_retention_final >= 0.99
new qualifying pair besides pair005
```

Run directory:

```text
results/future_field_atlas/20260602_rank_order_boundary_h128_neighbor_targets/
```

Gate results:

```text
status: COMPLETED
horizon_max: 128
pair_count_realized: 2 / 2
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS 3
medium_sweep_interpretation_allowed: 1
elapsed_seconds: 632.427
source_git_commit: 2c70a8bfe366165a4e6a6e2b63106693e598d067
source_git_dirty: false
```

Artifact rows:

```text
joint edge rows: 17,177,855
joint node rows: 2,130,038
profile rows: 516
residual rows: 258
marginal rows: 258
```

Retention:

```text
total output GiB before raw-spool deletion: 0.912512
raw delete candidate GiB: 0.912466
raw spools deleted: yes
heaviest pair: pair012
heaviest pair edge share: 0.819223
```

Final-H128 pair table:

| pair | residual | joint retention | A retention | B retention | product support | coupled support |
|---|---:|---:|---:|---:|---:|---:|
| pair012 | 0.842202 | 0.157798 | 1.000000 | 1.000000 | 11990 | 1892 |
| pair014 | 0.512554 | 0.487446 | 1.000000 | 1.000000 | 2310 | 1126 |

Read:

```text
pair012 and pair014 final H128 geometry matches final H64 geometry.
The new rank_order_boundary neighbors are horizon-stable at this depth.
```

## Study C: Observable-Extension Smoke

### Supported Observable List

The runner now exposes supported macro-invariant kinds:

```text
symbol_histogram_distance
symbol_histogram_l2
hamming_weight_or_nonzero_count
hamming_weight
nonzero_count
total_coordinate_mass
```

Two non-semantic alternates were tested:

```text
hamming_weight_or_nonzero_count
total_coordinate_mass
```

### Hamming Weight / Nonzero Count

Run directory:

```text
results/future_field_atlas/20260602_rank_order_boundary_h64_observable_hamming_weight_or_nonzero_count/
```

Gate results:

```text
status: COMPLETED
horizon_max: 64
pair_count_realized: 4 / 4
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS 3
elapsed_seconds: 70.912
source_git_commit: 2c70a8bfe366165a4e6a6e2b63106693e598d067
source_git_dirty: false
```

Final-H64 table:

| pair | residual | joint retention | A retention | B retention | product support | coupled support |
|---|---:|---:|---:|---:|---:|---:|
| pair000 | 0.056997 | 0.943003 | 1.000000 | 1.000000 | 1965 | 1853 |
| pair001 | 0.025000 | 0.975000 | 1.000000 | 1.000000 | 80 | 78 |
| pair002 | 0.050000 | 0.950000 | 1.000000 | 1.000000 | 920 | 874 |
| pair005 | 0.040138 | 0.959862 | 1.000000 | 1.000000 | 872 | 837 |

Read:

```text
hamming_weight_or_nonzero_count does not reproduce the pair005-like signature.
No H128 observable depth was warranted.
```

### Total Coordinate Mass

Run directory:

```text
results/future_field_atlas/20260602_rank_order_boundary_h64_observable_total_coordinate_mass/
```

Gate results:

```text
status: COMPLETED
horizon_max: 64
pair_count_realized: 4 / 4
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS 3
elapsed_seconds: 1298.441
source_git_commit: 2c70a8bfe366165a4e6a6e2b63106693e598d067
source_git_dirty: false
```

Final-H64 table:

| pair | residual | joint retention | A retention | B retention | product support | coupled support |
|---|---:|---:|---:|---:|---:|---:|
| pair000 | 0.106247 | 0.893753 | 1.000000 | 1.000000 | 14278 | 12761 |
| pair001 | 0.075499 | 0.924501 | 1.000000 | 1.000000 | 14040 | 12980 |
| pair002 | 0.097928 | 0.902072 | 1.000000 | 1.000000 | 13806 | 12454 |
| pair005 | 0.109172 | 0.890828 | 1.000000 | 1.000000 | 13923 | 12403 |

Read:

```text
total_coordinate_mass does not reproduce the pair005-like signature.
No H128 observable depth was warranted.
```

## Updated Morphology Atlas

The substrate morphology atlas was regenerated after all interpretable runs:

```text
source_run_count: 35
source_summary_dir_count: 0
manifest_digest: 4ee4a299c59439319c61d1d2
```

Output counts:

```text
field_morphology_summary.csv: 370
pair_morphology_summary.csv: 185
operator_sensitivity_summary.csv: 133742
horizon_onset_summary.csv: 2030
observable_geometry_summary.csv: 926
pair_class_exemplar_summary.csv: 6
morphology_next_targets.csv: 4
frontier_growth_regime_summary.csv: 370
```

Pair morphology class counts:

```text
pair_size_class:
  light: 62
  medium: 62
  heavy: 61

joint_residual_class:
  low_residual: 124
  medium_residual: 36
  high_residual: 25

marginal_retention_class:
  marginal_preserving: 167
  marginal_loss_B: 12
  marginal_loss_both: 6

joint_density_class:
  product_dense: 136
  product_sparse: 24
  joint_restrictive: 25
```

Observable coverage:

```text
multi_observable_smoke:
  hamming_weight_or_nonzero_count
  symbol_histogram_distance
  total_coordinate_mass

high-yield rank_order_boundary signature:
  still symbol_histogram_distance-specific in the tested alternates
```

Updated next target:

```text
rank_order_boundary_class_expansion:
  rank_order_boundary at targeted_H128_then_medium_plus_H64
  pairs: pair005;pair012;pair014
```

## Mechanism Read

Current read:

```text
The rank_order_boundary coupled selector is no longer a pair005-only curiosity.
It has at least three high-residual marginal-preserving exemplars in the current
symbol_histogram_distance branch: pair005, pair012, and pair014.

pair012 is now the strongest retained exemplar:
  final residual 0.842202
  final joint retention 0.157798
  A/B retention 1.0 / 1.0

The tested alternate observables do not reproduce the signature, so the result
is not yet substrate-general across observables.
```

This updates the roadmap:

```text
move from pair005-neighbor search to rank_order_boundary class expansion;
retain pair005, pair012, and pair014 as high-yield representatives;
keep low/medium controls;
continue observable design before stronger substrate-general claims;
do not promote to semantic interaction or compatibility language.
```

## Recommendation

Next run should be a bounded class-expansion pass, not broad H128 for every
pair:

```text
rank_order_boundary_class_expansion:
  include pair005, pair012, pair014;
  add low/medium controls;
  run H64 class breadth first;
  use targeted H128 only for new high-yield representatives;
  keep product, zero-penalty joint rank-prefix, scalar 0.020, and
  shared_capacity v1 controls.

observable_extension:
  keep as an active design target, but the two tested alternates are negative
  for the current signature.
```

## Claim Boundary

This is a coupled-instrument mechanism-resolution result only. It shows that
rank-order-boundary marginal-preserving joint restriction recurs in additional
symbol_histogram_distance pairs and is stable under targeted H128 for pair012
and pair014. It does not detect interaction, compatibility, support, capture,
erasure, agency, identity, value, proto-valuerhood, valuerhood, or Omega.

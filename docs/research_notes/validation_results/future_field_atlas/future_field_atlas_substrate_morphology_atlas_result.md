# Future Field Atlas Substrate Morphology Atlas Result

Status: completed as a retained-output postprocess

Runner: `omega.future_field_atlas.substrate_morphology_summary`

Spec: `docs/specs/current/FUTURE_FIELD_ATLAS_SUBSTRATE_MORPHOLOGY_SWEEP_SPEC.md`

Latest update: regenerated after the rank-order-boundary neighbor / observable
sweep with 35 clean coupled run directories.

## Summary

The substrate morphology atlas maps retained coupled Future Field Atlas outputs
into pair-aware morphology, operator sensitivity, horizon-onset, observable
coverage, and next-target tables. It is a postprocess over retained run
artifacts, not a new scan and not an Omega result.

Allowed claim:

```text
The current finite Future Field Atlas substrate has a usable morphology map over
retained coupled outputs. The map separates product-selector behavior,
zero-penalty joint rank-prefix behavior, positive scalar penalties,
rank-order-boundary pair classes, horizon onset, and observable coverage.
```

Blocked claims:

```text
Omega validation
agency / identity / valuerhood / value
compatibility detection
support / capture / erasure
interaction detection
```

## Inputs

Latest local output bundle:

```text
results/future_field_atlas/20260602_substrate_morphology_atlas_summary/
```

Latest manifest:

```text
source_run_count: 35
source_summary_dir_count: 0
manifest_digest: 4ee4a299c59439319c61d1d2
```

All 35 coupled run directories used here passed the clean infrastructure gates:

```text
status: COMPLETED
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction_audit_clean_pass: 1
```

## Output Tables

The postprocessor emitted:

```text
field_morphology_summary.csv                 370 rows
pair_morphology_summary.csv                  185 rows
operator_sensitivity_summary.csv          133742 rows
horizon_onset_summary.csv                   2030 rows
observable_geometry_summary.csv              926 rows
pair_class_exemplar_summary.csv                6 rows
morphology_next_targets.csv                    4 rows
frontier_growth_regime_summary.csv           370 rows
joint_candidate_crossing_morphology.csv        2 rows
rank_boundary_offset_morphology.csv            2 rows
composition_residual_morphology.csv            1 status row
substrate_morphology_manifest.json
substrate_morphology_report.md
```

Generated CSV artifacts remain local under `results/future_field_atlas/` and
are not committed.

## Pair Morphology

Pair-level descriptive classes across retained rows:

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

The high-residual / joint-restrictive rank-order-boundary rows are no longer
pair005-only. The current high-yield symbol_histogram_distance representatives
are:

```text
pair005
pair012
pair014
```

Current strongest retained exemplar:

```text
pair012:
  final residual: 0.842202
  final joint retention: 0.157798
  A/B marginal retention: 1.0 / 1.0
  confirmed at targeted H128
```

## Operator Sensitivity

The atlas keeps the product selector as the true product-equivalence reference.
Zero-penalty joint rank-prefix selection remains a distinct coupled selector and
should not be treated as product-neutral.

Current operator read:

```text
product selector:
  true product reference

joint rank-prefix at 0.000:
  already distinct from product behavior

positive scalar penalty:
  near-zero changes are detectable
  tested topology saturates by 0.020 / 0.050 in the pair8 design

shared_capacity v1:
  operational but prunes component marginals

rank_order_boundary:
  produces a high-residual marginal-preserving class under symbol_histogram_distance
```

## Observable Coverage

The retained coupled morphology now includes smoke-level outputs for:

```text
hamming_weight_or_nonzero_count
symbol_histogram_distance
total_coordinate_mass
```

The atlas emits:

```text
observable_coverage: multi_observable_smoke
```

The high-yield rank-order-boundary signature remains specific to
`symbol_histogram_distance` in the tested alternate-observable smokes:

```text
hamming_weight_or_nonzero_count:
  pair005 final residual: 0.040138

total_coordinate_mass:
  pair005 final residual: 0.109172
```

Therefore substrate-general observable language remains blocked.

## Recommendation

Current most useful next target:

```text
rank_order_boundary_class_expansion
```

Recommended shape:

```text
rank_order_boundary_class_expansion:
  carry pair005, pair012, and pair014 as high-yield representatives;
  keep low/medium controls;
  preserve product-selector, zero-penalty joint rank-prefix, scalar 0.020, and
  shared_capacity v1 controls;
  run H64 breadth first;
  use targeted H128 only for new high-yield representatives.

observable_extension:
  continue observable design; the two tested alternates did not reproduce the
  high-yield signature.

shared_capacity_v2_marginal_coverage_repair:
  only if the theory side specifically needs finite shared capacity as the next
  primitive.
```

## Claim Boundary

This is an atlas/postprocessing result. It maps retained future-field
morphology and recommends target pairs/operators. It does not validate Omega,
detect interaction, or establish compatibility-like semantics.

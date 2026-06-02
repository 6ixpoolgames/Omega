# Future Field Atlas Substrate Morphology Atlas Result

Status: completed as a retained-output postprocess

Runner: `omega.future_field_atlas.substrate_morphology_summary`

Spec: `docs/specs/current/FUTURE_FIELD_ATLAS_SUBSTRATE_MORPHOLOGY_SWEEP_SPEC.md`

Update after rank-order-boundary medium sweep: regenerated with 29 coupled run
directories and 2 compact summary directories. The earlier shared-capacity
target was tested cleanly but should not be scaled as v1. The
rank-order-boundary medium sweep completed cleanly and isolated pair005 as the
only high-residual marginal-preserving exemplar in the H64 pair8 set.

## Summary

This pass built the first compact substrate morphology atlas over existing
Future Field Atlas outputs. It did not launch a new broad scan. The regenerated
bundle ingests 29 retained coupled run directories plus 2 compact summary
directories and emits
pair-aware morphology, operator sensitivity, horizon-onset, observable-coverage,
and next-target tables.

Allowed claim:

```text
The current finite Future Field Atlas substrate has a usable morphology map over
retained coupled outputs. The map separates product-selector behavior,
zero-penalty joint rank-prefix behavior, positive scalar penalties, pair-level
residual structure, horizon onset, and observable coverage.
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

Primary inputs were existing compact coupled outputs:

```text
broad H64/H128 worker-spool runs
H64 coupling ladder runs
H64 mechanism-resolution runs
true product-selector H64 run
pair005 H64 near-zero forensics
pair005 H128 targeted depth checks
H64 ladder and mechanism compact summary directories
```

After the rank-order-boundary medium sweep, the regenerated local morphology bundle
ingests 29 coupled run directories plus 2 compact summary directories. All 29
coupled run directories used here passed the clean infrastructure gates:

```text
status: COMPLETED
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction_audit_clean_pass: 1
```

Local retained output bundle:

```text
results/future_field_atlas/20260602_substrate_morphology_atlas_summary/
```

## Output Tables

The postprocessor emitted:

```text
field_morphology_summary.csv                 294 rows
pair_morphology_summary.csv                  147 rows
operator_sensitivity_summary.csv          115542 rows
horizon_onset_summary.csv                   1750 rows
observable_geometry_summary.csv              736 rows
pair_class_exemplar_summary.csv                6 rows
morphology_next_targets.csv                    4 rows
joint_candidate_crossing_morphology.csv        2 rows
rank_boundary_offset_morphology.csv            2 rows
frontier_growth_regime_summary.csv           294 rows
composition_residual_morphology.csv            1 status row
substrate_morphology_manifest.json
substrate_morphology_report.md
```

The large `operator_sensitivity_summary.csv` is still manageable locally, but it
is not a public retained artifact in Git because `results/future_field_atlas/`
remains ignored.

## Pair Morphology

Pair-level descriptive classes across retained rows:

```text
pair_size_class:
  light: 50
  medium: 54
  heavy: 43

joint_residual_class:
  low_residual: 100
  medium_residual: 28
  high_residual: 19

marginal_retention_class:
  marginal_preserving: 133
  marginal_loss_B: 11
  marginal_loss_both: 3

joint_density_class:
  product_dense: 107
  product_sparse: 21
  joint_restrictive: 19
```

The high-residual / joint-restrictive rows are currently pair005-only in the
retained set. That makes pair005 a high-yield exemplar and stress case, not a
sound basis for a whole branch by itself.

Representative high pair005 rows:

```text
mech_c0005:
  final residual: 0.755909
  final joint retention: 0.244091
  A/B marginal retention: 1.0 / 1.0

mech_c0020 and mech_c0050:
  final residual: 0.752364
  final joint retention: 0.247636
  A/B marginal retention: 1.0 / 1.0
```

This preserves the earlier read: the current operator can sharply reduce joint
combinations while preserving component marginals in the retained readout.

## Operator Sensitivity

The atlas keeps the product selector as the true product-equivalence reference.
Zero-penalty joint rank-prefix selection remains a distinct coupled selector and
should not be treated as a product-neutral baseline.

The morphology pass reinforces the mechanism-resolution read:

```text
product selector:
  true product reference

joint rank-prefix at 0.000:
  already distinct from product behavior

positive scalar penalty:
  near-zero changes are detectable
  tested topology saturates by 0.020 / 0.050 in this design
```

## Horizon Onset

The horizon-onset table records first metric divergence from the selected
comparison reference. It is descriptive timing metadata only. It should be used
to pick efficient follow-up horizons, not as a semantic detector.

## Observable Coverage

The retained coupled morphology is still single-observable:

```text
symbol_histogram_distance
```

The atlas explicitly emits `observable_coverage: single_observable_only`. This
blocks any invariant-robustness claim until at least one additional observable is
carried through comparable coupled scans or postprocessing.

## Exemplar And Target Selection

Pair005 is retained as:

```text
heaviest_pair
highest_joint_residual
lowest_joint_retention
marginal_preserving_joint_restrictive
pair005_like
```

The next-target table deliberately paired it with controls:

```text
shared_capacity_marginal_preserving_high_residual:
  recommended_operator: shared_capacity_coupling
  recommended_horizon: H64
  recommended_pairs: pair005;pair000;pair001;pair002
  required_controls: product_selector; zero_penalty_joint_selector; matched_pair_set
```

That target has now been tested as `shared_capacity` v1. The result was
operationally clean but mechanism-negative:

```text
shared_capacity_h64:
  pair000: medium_residual / marginal_loss_B / product_dense
  pair001: medium_residual / marginal_loss_both / product_dense
  pair002: medium_residual / marginal_loss_both / product_dense
  pair005: medium_residual / marginal_loss_both / product_dense
```

The rank-order-native target has also been tested:

```text
rank_order_boundary_h64:
  pair000: low_residual / marginal_preserving / product_dense
  pair001: low_residual / marginal_preserving / product_dense
  pair002: low_residual / marginal_preserving / product_dense
  pair005: high_residual / marginal_preserving / joint_restrictive
```

The medium rank-order-boundary sweep has now completed:

```text
rank_order_boundary_h64_pair8:
  pair000, pair001, pair002, pair003, pair004, pair006, pair007:
    low_residual / marginal_preserving
  pair005:
    high_residual / marginal_preserving / joint_restrictive

rank_order_boundary_h128_pair005:
  final residual: 0.753455
  final joint retention: 0.246545
  A/B marginal retention: 1.0 / 1.0
```

## Recommendation

Do not scale `shared_capacity` v1. It prunes component marginal support and then
becomes dense over the surviving marginals, which is not the desired
pair005-like scalar-mismatch signature.

The medium pair-aware `rank_order_boundary` sweep is complete. Do not broaden
H128 just for scale yet; the current result is pair005-only. Proceed to a
targeted neighbor/observable pass:

```text
rank_order_boundary_pair005_neighbor_search:
  find whether pair005 has nearby high-yield neighbors;
  keep low/medium controls;
  preserve product-selector, zero-penalty joint rank-prefix, scalar 0.020, and
  shared_capacity v1 controls.

observable_extension:
  add at least one additional observable before stronger invariant-robustness
  language.

shared_capacity_v2_marginal_coverage_repair:
  only if the theory side specifically needs finite shared capacity as the next
  primitive.
```

Also plan an observable-extension pass. The current morphology is useful, but it
is still too tied to `symbol_histogram_distance` to support stronger
substrate-general language.

## Claim Boundary

This is an atlas/postprocessing result. It maps retained future-field
morphology and recommends target pairs/operators. It does not validate Omega,
detect interaction, or establish compatibility-like semantics.

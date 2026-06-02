# Future Field Atlas Rank-Order Boundary H64 Smoke Result

Status: completed cleanly; promising mechanism smoke

Runner: `omega.future_field_atlas.run_coupled_future_field_atlas`

Spec: `docs/specs/current/FUTURE_FIELD_ATLAS_RANK_ORDER_NATIVE_SMOKE_SPEC.md`

## Summary

This pass implemented and smoked the first rank-order-native coupled selector:

```text
joint_selection_family: rank_order_boundary
```

The infrastructure result is clean:

```text
no caps
no pair failures
complete artifacts
all reconstruction audits PASS
source_git_dirty: false
```

The mechanism result is materially better than shared-capacity v1. The
rank-order boundary selector preserves A/B marginals on all four tested pairs
while reproducing the pair005 high joint-restriction signature seen under
scalar mismatch `0.020`.

Allowed claim:

```text
The rank-order boundary selector is operational inside the coupled Future Field
Atlas and recovers the pair005-like marginal-preserving joint-restriction
pattern on the small H64 pair set, while low/medium controls remain
marginal-preserving and low-residual.
```

Blocked claims:

```text
Omega validation
agency / identity / valuerhood / value
support / capture / erasure
compatibility detection
interaction detection
broad substrate-general claim
```

## Design

Common design:

```text
horizon_max: 64
horizon_schedule: dense
pair indexes: 0, 1, 2, 5
workers: 4
raw_topology_output_mode: worker_spool
csv_output_mode: gzip
gzip_compresslevel: 1
selection_operator_a: rank_prefix:m=3
selection_operator_b: rank_subset:m=4:retain=1|2|3:remove=4
macro_invariant_kind: symbol_histogram_distance
macro_invariant_beta: 0.10
rank_boundary_k: 3
joint_selection_family: rank_order_boundary
joint_effective_out_degree: 4
coupling_strength: 0.000
```

Operator rule:

```text
candidate set:
  Cartesian product of component selected successors

selection:
  lexicographic rank-boundary tuple:
    abs(A_rank_offset_from_boundary - B_rank_offset_from_boundary)
    A_candidate_rank + B_candidate_rank
    max(A_candidate_rank, B_candidate_rank)
    min(A_candidate_rank, B_candidate_rank)
    abs(A_rank_offset_from_boundary) + abs(B_rank_offset_from_boundary)
    target_joint_state_id
```

The selector does not use scalar `coupling_strength` as a tuning control.

## Local Outputs

Run directory:

```text
results/future_field_atlas/20260602_rank_order_boundary_h64_pairset_smoke/
```

Retained summary bundle:

```text
results/future_field_atlas/20260602_rank_order_boundary_h64_pairset_smoke/_retention_summary/
```

Updated morphology atlas:

```text
results/future_field_atlas/20260602_substrate_morphology_atlas_summary/
```

Raw worker spools were pruned after the deletion guard allowed deletion.

## Rebuild Contract

```text
source_git_commit: ff7bff2176727d05f6339871a7c308cff5ae0bda
source_git_dirty: false
instrument_version: 0.4.1
runner_version: 0.1.0
python_version: 3.13.13
numpy_version: 2.4.4
rebuild_status: exact_rebuild_supported
```

## Gate Results

```text
status: COMPLETED
horizon_max: 64
pair_count_realized: 4 / 4
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS 3
medium_sweep_interpretation_allowed: 1
elapsed_seconds: 304.784
```

Artifact rows:

```text
joint edge rows: 13,550,314
joint node rows: 1,912,068
profile rows: 520
residual rows: 260
marginal rows: 260
marginal projection rows: 520
```

Retention:

```text
total output GiB before raw-spool deletion: 0.729025
raw delete candidate GiB: 0.728970
raw spools deleted: yes
```

## Operator Manifest

```text
coupled_operator_family: rank_order_boundary_alignment_joint_selector
coupled_operator_id: coupled_operator__rank_order_boundary__k4__426dc884bbd3
coupled_operator_digest: 6408a6931f95ab4bf7ec
joint_energy_function_id: rank_boundary_offset_alignment_tuple
coupling_term_id: rank_boundary_offset_ordinal_alignment
joint_effective_out_degree: 4
seed_policy: deterministic_rank_order_boundary_tuple
```

## Final-Horizon Pair Readout

At H64:

| pair | residual | joint retention | A retention | B retention | density vs marginal product | product support | coupled support |
|---|---:|---:|---:|---:|---:|---:|---:|
| pair000 | 0.040000 | 0.960000 | 1.000000 | 1.000000 | 0.960000 | 100 | 96 |
| pair001 | 0.050853 | 0.949147 | 1.000000 | 1.000000 | 0.949147 | 8613 | 8175 |
| pair002 | 0.084000 | 0.916000 | 1.000000 | 1.000000 | 0.916000 | 1000 | 916 |
| pair005 | 0.753455 | 0.246545 | 1.000000 | 1.000000 | 0.246545 | 11000 | 2712 |

Read:

```text
pair000, pair001, and pair002 remain low-residual and marginal-preserving.
pair005 becomes high-residual and joint-restrictive while preserving both
component marginals.
```

## Comparison To Prior Operators

Final-H64 summary:

| run | pair000 residual | pair001 residual | pair002 residual | pair005 residual | pair005 A/B retention |
|---|---:|---:|---:|---:|---:|
| product selector | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 / 1.000000 |
| zero-penalty joint rank-prefix | 0.060000 | 0.117497 | 0.128000 | 0.244091 | 1.000000 / 1.000000 |
| scalar mismatch 0.020 | 0.030000 | 0.048647 | 0.061000 | 0.752364 | 1.000000 / 1.000000 |
| shared_capacity v1 | 0.200000 | 0.266342 | 0.289000 | 0.249455 | 0.860000 / 0.872727 |
| rank_order_boundary | 0.040000 | 0.050853 | 0.084000 | 0.753455 | 1.000000 / 1.000000 |

Interpretation:

```text
rank_order_boundary is much closer to scalar mismatch 0.020 than to
shared_capacity v1.

The useful pattern is not generic capacity pressure. It is compatible with an
ordinal rank-boundary alignment mechanism.
```

## Updated Morphology Atlas

The substrate morphology atlas was regenerated after the run:

```text
source_run_count: 27
source_summary_dir_count: 2
manifest_digest: ef790cd946257a48ccb61f75
```

Rank-order pair classifications:

```text
pair000:
  low_residual / marginal_preserving / product_dense

pair001:
  low_residual / marginal_preserving / product_dense

pair002:
  low_residual / marginal_preserving / product_dense

pair005:
  high_residual / marginal_preserving / joint_restrictive
```

Updated morphology target:

```text
rank_order_boundary_medium_pair_sweep
```

Follow-up status:

```text
The medium pair-aware rank_order_boundary sweep has now completed cleanly.
Only pair005 was high-residual and marginal-preserving in the H64 pair8 set.
Targeted H128 pair005 reproduced the same final geometry.
```

## Mechanism Read

The result is the strongest coupled-operator smoke so far.

It does not validate Omega or prove interaction. It does show that a minimal
ordinal selector can reproduce the pair005 marginal-preserving joint restriction
without scalar tuning and without the marginal loss produced by
shared-capacity v1.

Working interpretation:

```text
The current coupled object is better described as ordinal rank-boundary
alignment than as scalar mismatch strength or generic shared capacity.
```

## Recommendation

The medium pair-aware rank-order-boundary sweep is complete. The next job is
not broad H128 for its own sake; it is pair005-neighbor search and observable
extension.

Suggested next shape:

```text
operator:
  rank_order_boundary

horizon:
  H64 neighbor search first
  targeted H128 only if new high-yield exemplars appear

pairs:
  include pair005
  include low/medium controls
  add neighboring high-residual or heavy-pair candidates if morphology can
  identify them

controls:
  product selector
  zero-penalty joint rank-prefix
  scalar mismatch 0.020
  shared_capacity v1 reference

also:
  plan observable extension beyond symbol_histogram_distance
```

Do not move to Omega, agency, value, compatibility, support, capture, or erasure
language. The next job is still mechanism resolution and morphology-class
testing.

## Claim Boundary

This is an infrastructure and mechanism-diagnostic result only. It shows that a
rank-order-native coupled selector can be added cleanly to Future Field Atlas
and can reproduce the pair005-like marginal-preserving joint-restriction pattern
on a small H64 pair set. It does not detect interaction, compatibility, support,
capture, erasure, agency, identity, value, or Omega.

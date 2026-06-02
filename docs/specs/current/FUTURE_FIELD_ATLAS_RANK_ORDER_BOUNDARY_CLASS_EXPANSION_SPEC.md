# Future Field Atlas Rank-Order Boundary Class Expansion Spec

Status: completed cleanly

Runner target: `omega.future_field_atlas.run_coupled_future_field_atlas`

Retained result:
`docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_class_expansion_result.md`

## Purpose

Expand the rank-order-boundary high-yield class after the neighbor /
observable sweep found `pair012` and `pair014` in addition to `pair005`.

This is not broad H128 scale expansion. It is H64 breadth over new pair indexes
with targeted H128 only for new high-yield marginal-preserving exemplars.

## Claim Boundary

Blocked claims:

```text
Omega validation
agency / identity / valuerhood / value
compatibility detection
support / capture / erasure
interaction detection
holdout readiness
substrate-general theory claim
```

Allowed claim:

```text
This pass tests whether the rank-order-boundary coupled selector has additional
symbol_histogram_distance high-yield representatives in the current finite
Future Field Atlas substrate.
```

## Run A: H64 Class Expansion

```text
out:
  results/future_field_atlas/20260602_rank_order_boundary_h64_class_expansion_p24_47

horizon_max: 64
horizon_schedule: dense
groups: 48
fresh_seeds_per_group: 1
pair_indexes: 24-47
start_samples: 1

selection_operator_a: rank_prefix:m=3
selection_operator_b: rank_subset:m=4:retain=1|2|3:remove=4
macro_invariant_kind: symbol_histogram_distance
macro_invariant_beta_list: 0.10
rank_boundary_k: 3

joint_selection_family: rank_order_boundary
joint_effective_out_degree: 4
coupling_strength: 0.000

raw_topology_output_mode: worker_spool
csv_output_mode: gzip
gzip_compresslevel: 1
workers: 6
artifact_write_workers: 4
checkpoint_every_pairs: 1
max_runtime_seconds: 7200
shutdown_cushion_seconds: 120
```

## Run B: Conditional H128 Depth

If Run A finds a new high-residual marginal-preserving pair, run targeted H128
for the new representative only.

Executed target:

```text
out:
  results/future_field_atlas/20260602_rank_order_boundary_h128_pair026_depth

horizon_max: 128
groups: 48
pair_indexes: 26
workers: 1
same substrate and operator config as Run A
```

## Gates

Every interpretable run must satisfy:

```text
status: COMPLETED
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS
medium_sweep_interpretation_allowed: 1
```

## Outcome

Run A found `pair026` as a new high-yield marginal-preserving representative.
Run B confirmed the same final geometry at H128.

Current high-yield representative set:

```text
pair005
pair012
pair014
pair026
```

Next recommended pass:

```text
rank_order_boundary representative-control panel
  pair005;pair012;pair014;pair026
  low/medium controls
  product selector
  zero-penalty joint rank-prefix
  scalar mismatch 0.020
  shared_capacity v1 reference
```

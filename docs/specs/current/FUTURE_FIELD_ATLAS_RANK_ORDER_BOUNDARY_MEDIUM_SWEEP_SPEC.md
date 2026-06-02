# Future Field Atlas Rank-Order Boundary Medium Sweep Spec

Status: completed cleanly

Target runner: `omega.future_field_atlas.run_coupled_future_field_atlas`

Selector: `joint_selection_family = rank_order_boundary`

## Purpose

Run the first medium pair-aware rank-order-boundary pass after the successful
small H64 smoke.

This is still mechanism resolution, not Omega validation and not a broad H128
survey.

The previous small smoke showed:

```text
pair000, pair001, pair002:
  low residual
  A/B marginal retention 1.0 / 1.0

pair005:
  high residual
  A/B marginal retention 1.0 / 1.0
```

The live question is whether ordinal rank-boundary alignment defines a broader
pair morphology class, or whether pair005 remains a single critical-pair
exemplar.

Outcome:

```text
H64 pair8 completed cleanly.
Only pair005 was high-residual and marginal-preserving.
Targeted H128 pair005 completed cleanly and reproduced the same final geometry.
```

Retained result:

```text
docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_medium_sweep_result.md
```

## Claim Boundary

Allowed:

```text
The run tests whether rank-order-boundary alignment remains clean across the
full H64 pair8 design and identifies which pairs, if any, deserve targeted H128
depth checks.
```

Blocked:

```text
Omega validation
agency / identity / valuerhood / value
compatibility detection
support / capture / erasure
interaction detection
holdout claim
broad substrate-general claim
```

## Run A: H64 Pair8 Medium Sweep

Config:

```text
horizon_max: 64
horizon_schedule: dense
groups: 8
fresh_seeds_per_group: 1
pair_count: 8
start_samples: 1
workers: 4
artifact_write_workers: 4
raw_topology_output_mode: worker_spool
csv_output_mode: gzip
gzip_compresslevel: 1

selection_operator_a: rank_prefix:m=3
selection_operator_b: rank_subset:m=4:retain=1|2|3:remove=4
macro_invariant_kind: symbol_histogram_distance
macro_invariant_beta_list: 0.10
rank_boundary_k: 3

joint_selection_family: rank_order_boundary
joint_effective_out_degree: 4
coupling_strength: 0.000

max_internal_joint_frontier_states: 100000
max_joint_frontier_nodes_per_horizon: 100000
max_joint_edges_per_step: 1000000
max_runtime_seconds: 7200
shutdown_cushion_seconds: 120
```

Output:

```text
results/future_field_atlas/20260602_rank_order_boundary_h64_pair8_medium/
```

After run:

```text
run retention_summary with --delete-raw-spools if allowed;
regenerate substrate morphology atlas with this run included;
summarize final-H64 pair morphology.
```

## Run B: Conditional Targeted H128 Depth

Only run targeted H128 if Run A is clean and yields at least one high-residual,
marginal-preserving pair:

```text
joint_support_residual_final >= 0.4
A_marginal_retention_final >= 0.99
B_marginal_retention_final >= 0.99
```

Run H128 only for qualifying high-yield pairs. Cap the first depth pass at three
pairs. If only pair005 qualifies, run pair005 only.

Config:

```text
horizon_max: 128
horizon_schedule: dense
same substrate and operator config as Run A
pair_indexes: qualifying H64 high-yield pair indexes
workers: min(3, qualifying_pair_count)
raw_topology_output_mode: worker_spool
csv_output_mode: gzip
gzip_compresslevel: 1
max_runtime_seconds: 14400
shutdown_cushion_seconds: 180
```

Suggested output:

```text
results/future_field_atlas/20260602_rank_order_boundary_h128_targets/
```

Do not run broad H128.

## Required Gates

Every interpretable run must satisfy:

```text
status: COMPLETED
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS
medium_sweep_interpretation_allowed: 1
source_git_dirty: false
```

If any run has caps, errors, or audit skips, mark it operational only and do not
use it for mechanism interpretation.

## Required Readout

For H64 and any targeted H128 run:

```text
run status
source commit and dirty flag
artifact counts
retention/deletion summary
final-horizon pair table:
  joint_support_residual_fraction
  joint_retention_fraction
  A_marginal_retention_fraction
  B_marginal_retention_fraction
  joint_density_vs_marginal_product
  product_joint_support_count
  coupled_joint_support_count

pair class:
  low / medium / high residual
  marginal preserving / marginal loss
  product dense / joint restrictive
```

Compare H64 against:

```text
product_h64
ladder_c000
mech_c0020
shared_capacity_h64
rank_order_boundary_h64 small smoke
```

## Decision Logic

### If only pair005 is high-residual and marginal-preserving

```text
Treat pair005 as the current critical-pair exemplar.
Run or retain targeted H128 for pair005 only.
Do not claim a broad morphology class yet.
Next branch should search for pair005-like neighbors or vary observable.
```

### If multiple pairs are high-residual and marginal-preserving

```text
Define the descriptive morphology class.
Run targeted H128 for up to three representatives.
Prepare a medium-plus sweep only after H128 confirms stability.
```

### If H64 rank-order collapses into marginal loss

```text
Do not scale.
Inspect whether the small smoke overfit the selected pair set.
```

### If all pairs are low-residual

```text
Rank-order boundary is too weak at pair8 breadth.
Return to scalar pair005 bracket or alternate ordinal boundary rules.
```

## Deliverable

Retained result note:

```text
docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_medium_sweep_result.md
```

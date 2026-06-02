# Future Field Atlas Rank-Order-Native Coupled Smoke Spec

Status: active small smoke

Target runner: `omega.future_field_atlas.run_coupled_future_field_atlas`

New selector: `joint_selection_family = rank_order_boundary`

## Purpose

Run the next coupled-operator probe after the shared-capacity v1 smoke. This is
an operator-smoke and mechanism-resolution pass, not a broad scale expansion and
not an Omega validation run.

The prior branch established:

```text
product selector:
  true product-equivalence reference

zero-penalty joint rank-prefix:
  already a coupled constraint

scalar rank-boundary mismatch:
  near-zero effects are visible and saturate by 0.020 in the tested H64 design

shared_capacity v1:
  operational but prunes component marginals and should not be scaled as-is
```

This smoke tests whether the useful coupled deformation is better represented
by ordinal rank-boundary geometry than by scalar strength or shared marginal
capacity.

## Claim Boundary

Allowed:

```text
The run tests whether an ordinal rank-boundary alignment selector is
operationally well-formed and whether its raw joint-vs-product morphology
resembles the current scalar mismatch reference on a small pair set.
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

## Operator Definition

For each joint source, construct the same product successor candidates used by
the existing coupled runner:

```text
A selected successors x B selected successors
```

Then select at most:

```text
joint_effective_out_degree = 4
```

using deterministic rank-order boundary alignment:

```text
lexicographic key:
  abs(A_rank_offset_from_boundary - B_rank_offset_from_boundary)
  A_candidate_rank + B_candidate_rank
  max(A_candidate_rank, B_candidate_rank)
  min(A_candidate_rank, B_candidate_rank)
  abs(A_rank_offset_from_boundary) + abs(B_rank_offset_from_boundary)
  target_joint_state_id
```

Important:

```text
rank_order_boundary does not use coupling_strength as a scalar tuning control.
It reports ordinal mismatch as coupling_penalty for continuity with existing
edge rows, but selection is by the rank tuple above.
```

## Pair Set

Use the same four-pair set as the shared-capacity smoke:

```text
pair indexes: 0,1,2,5
```

Rationale:

```text
pair005:
  current heavy-pair / critical-pair clue

pair000, pair001, pair002:
  low/medium controls from retained morphology
```

## Run Config

```text
horizon_max: 64
horizon_schedule: dense
groups: 8
fresh_seeds_per_group: 1
pair_indexes: 0,1,2,5
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

Suggested output:

```text
results/future_field_atlas/20260602_rank_order_boundary_h64_pairset_smoke/
```

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
include it in mechanism interpretation.

## Required Readout

At minimum report:

```text
run status
source commit and dirty flag
artifact counts
retention/deletion summary
final-H64 pair table:
  joint_support_residual_fraction
  joint_retention_fraction
  A_marginal_retention_fraction
  B_marginal_retention_fraction
  joint_density_vs_marginal_product

comparison to:
  product selector
  zero-penalty joint rank-prefix
  scalar mismatch 0.020 where available
  shared_capacity v1
```

Regenerate the substrate morphology atlas after the run so the new operator is
available in `operator_sensitivity_summary.csv`.

## Decision Logic

### If rank-order boundary preserves marginals and restricts joint combinations

```text
Treat rank-order-native geometry as the better next coupled primitive.
Design a medium pair-aware H64/H128 run after adding any needed compact
operator diagnostics.
```

### If it prunes marginals like shared-capacity v1

```text
Do not scale.
Either redesign toward marginal-coverage preservation or return to scalar
pair005 bracketing.
```

### If it is product-like or too weak

```text
Rank-order boundary alignment alone is insufficient.
Inspect whether scalar energy magnitude or a different ordinal boundary rule is
load-bearing.
```

### If it is pair005-only

```text
Keep pair005 as a critical-pair clue, but do not branch without finding a
broader morphology class.
```

## Deliverable

Retained result note:

```text
docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_h64_smoke_result.md
```

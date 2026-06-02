# Future Field Atlas Rank-Order Boundary Neighbor / Observable Sweep Spec

Status: current spec / pending implementation

Target runner: `omega.future_field_atlas.run_coupled_future_field_atlas`

Selector: `joint_selection_family = rank_order_boundary`

Expected retained result:
`docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_neighbor_observable_sweep_result.md`

## Purpose

Run the next targeted coupled Future Field Atlas pass after the completed
rank-order-boundary medium sweep.

This is a morphology-discovery and mechanism-resolution run, not broad H128
scale expansion and not an Omega validation run.

The completed medium sweep established:

```text
H64 pair8:
  clean, complete, reconstruction-passing

rank_order_boundary:
  reproduces the pair005 marginal-preserving joint-restriction signature

pair005:
  only high-residual marginal-preserving pair in the current pair8 set

H128 pair005 depth:
  clean, complete, same final geometry as H64
```

The next live question is:

```text
Does pair005 belong to a broader rank-order-boundary morphology family, or is it
currently an isolated critical-pair exemplar under symbol_histogram_distance?
```

Secondary live question:

```text
Is the retained rank-order-boundary morphology specific to symbol_histogram_distance,
or does it survive an observable-extension smoke?
```

## Claim Boundary

Allowed:

```text
The run tests whether rank-order-boundary marginal-preserving joint restriction
recurs in nearby / newly sampled pairs and whether the signature is observable-
specific in a small controlled observable-extension smoke.
```

Blocked:

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

## Operator Definition

Use the same rank-order-boundary selector as the completed smoke and medium
sweep.

For each joint source, construct product successor candidates:

```text
A selected successors x B selected successors
```

Select at most:

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
Set coupling_strength = 0.000.
```

## Study A: H64 Pair005 Neighbor Search

### Design

Run bounded H64 rank-order-boundary breadth over new pair indexes while retaining
pair005 and low/medium controls in every batch.

Do not run broad H128.

Use two H64 batches so output stays operationally manageable and so controls are
repeated across batches.

### Batch A

```text
pair_indexes:
  0,1,2,5,8,9,10,11,12,13,14,15
```

Suggested output:

```text
results/future_field_atlas/20260602_rank_order_boundary_h64_neighbor_batch_a/
```

### Batch B

```text
pair_indexes:
  0,1,2,5,16,17,18,19,20,21,22,23
```

Suggested output:

```text
results/future_field_atlas/20260602_rank_order_boundary_h64_neighbor_batch_b/
```

### Common config

```text
horizon_max: 64
horizon_schedule: dense
groups: 24
fresh_seeds_per_group: 1
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

Implementation note:

```text
The explicit pair indexes 8-23 require at least 24 generated paired conditions
in the current runner because pair indexes address generated condition indexes
directly. Run Study A with groups: 24, not groups: 8, unless the runner is later
changed to use a separate pair-neighbor generator.
```

### After each batch

```text
run retention_summary with --delete-raw-spools if allowed;
verify source_git_dirty = false;
record artifact counts and deletion summary;
do not interpret capped or incomplete topology.
```

## Study B: Conditional H128 Depth

Only run targeted H128 if Study A finds at least one new high-yield pair besides
pair005.

A pair qualifies for H128 if at final H64:

```text
joint_support_residual_final >= 0.4
A_marginal_retention_final >= 0.99
B_marginal_retention_final >= 0.99
```

Run targeted H128 for at most three new qualifying pairs.

Do not rerun pair005 H128 unless the retained pair005 H128 reference is missing,
non-interpretable, or produced under incompatible code/spec identity.

Config:

```text
horizon_max: 128
horizon_schedule: dense
same substrate and operator config as Study A
pair_indexes: new H64 high-yield qualifying pairs only
workers: min(3, qualifying_pair_count)
raw_topology_output_mode: worker_spool
csv_output_mode: gzip
gzip_compresslevel: 1
max_runtime_seconds: 14400
shutdown_cushion_seconds: 180
```

Suggested output:

```text
results/future_field_atlas/20260602_rank_order_boundary_h128_neighbor_targets/
```

## Study C: Observable-Extension Smoke

The retained coupled morphology is still `symbol_histogram_distance` only. This
blocks stronger substrate-general claims.

Run a small observable-extension smoke only after Study A is clean, or in
parallel if runtime is available.

### Observable discovery

Before running, inspect the runner/registry for currently supported
`macro_invariant_kind` values.

If no non-`symbol_histogram_distance` observable is supported, emit a short
blocked-result note instead of inventing one:

```text
observable_extension_status: blocked_no_supported_alternate_observable
supported_macro_invariant_kinds: <reported list>
```

If supported, choose up to two non-semantic alternate observables from the
available registry. Prefer observables that do not introduce valuer/agent/identity
semantics.

Supported atlas macro-invariant kinds at this spec revision:

```text
symbol_histogram_distance
symbol_histogram_l2
hamming_weight_or_nonzero_count
hamming_weight
nonzero_count
total_coordinate_mass
```

Preferred alternate observables for this smoke:

```text
hamming_weight_or_nonzero_count
total_coordinate_mass
```

### Pair set

Use the small pairset:

```text
pair_indexes:
  0,1,2,5
```

Rationale:

```text
pair005:
  current critical-pair exemplar

pair000, pair001, pair002:
  low/medium controls
```

### Config per alternate observable

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
macro_invariant_kind: <alternate observable>
macro_invariant_beta_list: 0.10
rank_boundary_k: 3

joint_selection_family: rank_order_boundary
joint_effective_out_degree: 4
coupling_strength: 0.000

max_runtime_seconds: 7200
shutdown_cushion_seconds: 120
```

Suggested output pattern:

```text
results/future_field_atlas/20260602_rank_order_boundary_h64_observable_<observable_id>/
```

### Conditional observable H128

If an alternate observable reproduces pair005-like geometry at H64:

```text
pair005 joint_support_residual_final >= 0.4
pair005 A_marginal_retention_final >= 0.99
pair005 B_marginal_retention_final >= 0.99
controls stay low or medium residual
```

then run targeted H128 for pair005 under that observable only.

Do not run broad H128 for observable extension.

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

If any run has caps, errors, incomplete artifacts, or skipped-only audits, mark
it operational only and do not use it for mechanism interpretation.

## Required Readout

For every H64 and conditional H128 run, report:

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

horizon onset:
  first horizon crossing vs product
  first horizon crossing vs zero-penalty joint rank-prefix if reference exists
  max delta horizon
```

Compare Study A against retained references:

```text
product_h64
ladder_c000 / zero-penalty joint rank-prefix
scalar mismatch 0.020
shared_capacity_h64
rank_order_boundary_h64_pair8_medium
rank_order_boundary_h128_pair005_depth
```

Regenerate the substrate morphology atlas after all interpretable runs so new
pairs/observables appear in:

```text
pair_morphology_summary.csv
operator_sensitivity_summary.csv
horizon_onset_summary.csv
observable_geometry_summary.csv
morphology_next_targets.csv
```

## Decision Logic

### If new high-yield rank-order neighbors appear

```text
Define a descriptive pair005-like morphology class.
Run targeted H128 for up to three new representatives.
Do not claim compatibility/support/capture/erasure.
Next: design a medium-plus H64 class sweep or an observable-extension pass over
class representatives.
```

### If only pair005 remains high-yield

```text
Treat pair005 as the current isolated critical-pair exemplar.
Do not broaden H128.
Prioritize observable extension and alternate ordinal-boundary rules.
```

### If controls become high-residual unexpectedly

```text
Do not treat the operator as selective.
Inspect pair generation, control duplication, condition identity, and morphology
atlas comparison before expanding.
```

### If an alternate observable reproduces pair005-like geometry

```text
Mark rank_order_boundary as multi-observable-supported at smoke level.
Run targeted H128 for pair005 under that observable.
Next: design a small multi-observable class sweep.
```

### If only symbol_histogram_distance supports the signature

```text
Keep observable_coverage = single_observable_only.
Block substrate-general claims.
Search for neighbor families under symbol_histogram_distance or design additional
admissible observables before theory promotion.
```

### If no alternate observable is supported by the runner

```text
Record observable_extension_blocked_no_supported_alternate_observable.
Do not silently omit the observable limitation.
Open a follow-up implementation spec for admissible observable extension.
```

## Deliverable

Retained result note:

```text
docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_neighbor_observable_sweep_result.md
```

Suggested report structure:

```text
1. Summary
2. Claim boundary
3. Inputs and retained references
4. Study A H64 neighbor search gates and pair tables
5. Study B conditional H128 depth gates and pair tables, if any
6. Study C observable-extension status and pair tables, if any
7. Horizon-onset readout
8. Updated substrate morphology atlas
9. Decision outcome
10. Next recommendation
```

## Summary Instruction to Codex

Use rank_order_boundary as the live coupled operator.

Search for pair005-like neighbors at H64 before any broad H128.

Treat pair005 as a stress exemplar, not as a branch by itself.

Preserve product, zero-penalty joint rank-prefix, scalar 0.020, and shared_capacity
v1 references.

Add or report observable-extension status because current retained morphology is
symbol_histogram_distance-only.

Do not promote any result to Omega, valuerhood, compatibility, support, capture,
erasure, agency, identity, or value.

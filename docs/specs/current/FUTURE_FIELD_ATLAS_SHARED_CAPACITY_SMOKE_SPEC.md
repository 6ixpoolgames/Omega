# Future Field Atlas Shared-Capacity Coupled Smoke Spec

Status: active small smoke

Target runner: `omega.future_field_atlas.run_coupled_future_field_atlas`

New selector: `joint_selection_family = shared_capacity`

## Purpose

Run the first small coupled probe after the substrate morphology atlas. This is
an operator-smoke and morphology-followup pass, not a broad scale expansion and
not an Omega validation run.

The morphology atlas identified pair005 as the current high-residual /
joint-restrictive exemplar, but also warned against letting one pair define the
branch. This smoke therefore tests pair005 with low/medium controls.

## Claim Boundary

Allowed:

```text
The run tests whether a balanced shared-capacity joint selector is operationally
well-formed and whether its raw joint-vs-product morphology differs from the
current scalar mismatch reference on a small pair set.
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

using deterministic component-energy order while limiting repeated use of the
same A or B marginal successor. The per-marginal capacity is derived, not tuned:

```text
capacity_per_A_successor = ceil(joint_effective_out_degree / A_marginal_successor_count)
capacity_per_B_successor = ceil(joint_effective_out_degree / B_marginal_successor_count)
```

If the balanced pass under-fills the joint capacity, fill remaining slots by the
same deterministic component-energy order. This keeps the operator total,
auditable, and reconstruction-compatible.

Important:

```text
shared_capacity ignores scalar rank-boundary mismatch penalty.
coupling_strength should be 0.000 for this smoke.
```

## Pair Set

Use the morphology-selected four-pair set:

```text
pair indexes: 0,1,2,5

pair005:
  high-residual / joint-restrictive exemplar

pair000:
  low-residual control

pair001:
  low/medium-scale control

pair002:
  additional control
```

## Required Runs

Run the shared-capacity smoke:

```text
horizon_max: 64
horizon_schedule: dense
groups: 8
fresh_seeds_per_group: 1
pair_indexes: 0,1,2,5
start_samples: 1
selection_operator_a: rank_prefix:m=3
selection_operator_b: rank_subset:m=4:retain=1|2|3:remove=4
macro_invariant_kind: symbol_histogram_distance
macro_invariant_beta_list: 0.10
rank_boundary_k: 3
joint_selection_family: shared_capacity
joint_effective_out_degree: 4
coupling_strength: 0.000
raw_topology_output_mode: worker_spool
csv_output_mode: gzip
gzip_compresslevel: 1
workers: 4
artifact_write_workers: 4
```

Suggested output:

```text
results/future_field_atlas/20260602_shared_capacity_h64_pairset_smoke/
```

Comparison references are already retained locally:

```text
product selector H64 pair8
zero-penalty joint rank-prefix H64 pair8
scalar mismatch H64 pair8 at 0.020
substrate morphology atlas summary
```

Do not rerun references unless retained outputs are missing or non-interpretable.

## Gates

The smoke is interpretable only if:

```text
status: COMPLETED
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction_audit_clean_pass: 1
medium_sweep_interpretation_allowed: 1
```

If caps or skipped-only audits occur, mark the run operational only.

## Required Retained Outputs

After the run:

```text
1. Run retention summary.
2. Delete raw worker spools only if retention summary allows it.
3. Re-run substrate morphology summary including the shared-capacity run.
4. Write a retained result note.
5. Update README/manual/running log/changelog as needed.
6. Push both repos.
```

Expected retained note:

```text
docs/research_notes/validation_results/future_field_atlas/future_field_atlas_shared_capacity_h64_smoke_result.md
```

## Decision Logic

If shared capacity preserves component marginals while producing pair005-style
joint restriction:

```text
carry shared-capacity coupling forward as the next operator family;
run a small observable-extension pass before broad H128 scale.
```

If shared capacity behaves like product selector:

```text
shared capacity is too weak in this substrate setting;
prefer rank-order-native operator design next.
```

If shared capacity behaves like zero-penalty joint rank-prefix:

```text
the operator may not be adding a distinct morphology;
compare selected-edge/rank-order diagnostics before expanding.
```

If shared capacity destroys component marginals:

```text
do not scale it;
treat it as a destructive capacity control, not a promising coupled operator.
```

If only pair005 responds:

```text
retain pair005 as a stress exemplar;
do not generalize until neighboring/high-residual examples are found.
```

## Report Structure

```text
1. Summary
2. Spec and operator definition
3. Gate results
4. Pair-level morphology
5. Comparison against product / zero-joint / scalar 0.020 references
6. Morphology-atlas update
7. Claim boundary
8. Next recommendation
```

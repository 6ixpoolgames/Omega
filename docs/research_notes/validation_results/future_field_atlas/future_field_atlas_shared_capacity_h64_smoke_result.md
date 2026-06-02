# Future Field Atlas Shared-Capacity H64 Smoke Result

Status: completed cleanly; diagnostic negative for shared-capacity v1

Runner: `omega.future_field_atlas.run_coupled_future_field_atlas`

Spec: `docs/specs/current/FUTURE_FIELD_ATLAS_SHARED_CAPACITY_SMOKE_SPEC.md`

Follow-up: the rank-order-boundary smoke has now completed and is the current
medium-sweep candidate. See
`docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_h64_smoke_result.md`.

## Summary

This pass implemented and smoked the first `shared_capacity` coupled selector.
The infrastructure result is clean: formal coupled-operator identity is
manifest-backed, the run completed without caps, all topology-derived artifacts
were complete, and reconstruction audits passed.

The mechanism read is not favorable for this operator as currently written:

```text
shared_capacity v1 prunes component marginal support and then becomes dense
over the surviving marginals.
```

That is not the desired pair005-like behavior from the scalar mismatch operator,
where joint combinations became restricted while A/B marginals were preserved.

Allowed claim:

```text
The shared-capacity v1 selector is operational inside the coupled Future Field
Atlas, but it is a marginal-pruning capacity control rather than the desired
marginal-preserving joint-combination restriction operator.
```

Blocked claims:

```text
Omega validation
agency / identity / valuerhood / value
support / capture / erasure
compatibility detection
interaction detection
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
joint_selection_family: shared_capacity
joint_effective_out_degree: 4
coupling_strength: 0.000
```

The operator is intentionally mechanical:

```text
product baseline:
  Cartesian product of component selected successors

joint candidate set:
  same product successors

shared-capacity selector:
  order candidates by component-energy sum
  select up to joint_effective_out_degree
  limit repeated use of the same A/B marginal successor
  deterministically fill if the balanced pass underfills
```

It is not named as support, capture, compatibility, or interaction.

## Local Outputs

Clean run:

```text
results/future_field_atlas/20260602_shared_capacity_h64_pairset_smoke_clean/
```

Retained summary bundle:

```text
results/future_field_atlas/20260602_shared_capacity_h64_pairset_smoke_clean/_retention_summary/
```

Updated morphology atlas:

```text
results/future_field_atlas/20260602_substrate_morphology_atlas_summary/
```

Raw worker spools were pruned after the deletion guard allowed deletion. Compact
manifests, profiles, residuals, marginal summaries, audits, retained summaries,
and rebuild metadata remain local.

## Rebuild Contract

```text
source_git_commit: f8b778129269b2b561d1f60b464b5a95d56b71d5
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
elapsed_seconds: 349.824
```

Artifact rows:

```text
joint edge rows: 14,173,926
joint node rows: 2,071,438
profile rows: 520
residual rows: 260
marginal rows: 260
marginal projection rows: 520
```

Retention:

```text
total output GiB before raw-spool deletion: 0.754356
raw delete candidate GiB: 0.754297
raw spools deleted: yes
```

## Operator Manifest

The run emitted a first-class coupled operator:

```text
coupled_operator_family: shared_capacity_joint_selector
coupled_operator_id: coupled_operator__shared_capacity__k4__57bd1663ba48
coupled_operator_digest: a72157e52a35eeacd13e
product_baseline_definition: cartesian_product_of_component_selected_successors
joint_candidate_set_definition: cartesian_product_of_component_selected_successors
joint_energy_function_id: component_energy_sum_with_balanced_marginal_capacity_filter
coupling_term_id: balanced_marginal_successor_capacity
joint_effective_out_degree: 4
stochastic_flag: 0
```

## Final-Horizon Pair Readout

At H64:

| pair | residual | joint retention | A retention | B retention | density vs marginal product | product support | coupled support |
|---|---:|---:|---:|---:|---:|---:|---:|
| pair000 | 0.200000 | 0.800000 | 1.000000 | 0.800000 | 1.000000 | 100 | 80 |
| pair001 | 0.266342 | 0.733658 | 0.898990 | 0.816092 | 1.000000 | 8613 | 6319 |
| pair002 | 0.289000 | 0.711000 | 0.900000 | 0.790000 | 1.000000 | 1000 | 711 |
| pair005 | 0.249455 | 0.750545 | 0.860000 | 0.872727 | 1.000000 | 11000 | 8256 |

Read:

```text
All four pairs are product-dense over the marginals they retain.
The residual comes from marginal loss, not from sparse joint recombination over
preserved marginals.
```

## Comparison To Product And Zero-Penalty Joint Rank-Prefix

Final-H64 deltas against true product:

| pair | residual delta | joint retention delta | A retention delta | B retention delta |
|---|---:|---:|---:|---:|
| pair000 | 0.200000 | -0.200000 | 0.000000 | -0.200000 |
| pair001 | 0.266342 | -0.266342 | -0.101010 | -0.183908 |
| pair002 | 0.289000 | -0.289000 | -0.100000 | -0.210000 |
| pair005 | 0.249455 | -0.249455 | -0.140000 | -0.127273 |

Final-H64 deltas against zero-penalty joint rank-prefix:

| pair | residual delta | joint retention delta | A retention delta | B retention delta |
|---|---:|---:|---:|---:|
| pair000 | 0.140000 | -0.140000 | 0.000000 | -0.200000 |
| pair001 | 0.148845 | -0.148845 | -0.101010 | -0.172414 |
| pair002 | 0.161000 | -0.161000 | -0.100000 | -0.210000 |
| pair005 | 0.005364 | -0.005364 | -0.140000 | -0.127273 |

The small residual delta for pair005 against zero-penalty joint rank-prefix is
not a recovery of the earlier pair005 mechanism. Shared-capacity pair005 loses
A/B marginals, while scalar `0.020` preserved both A and B marginals and drove
joint retention down to about `0.247636`.

## Mechanism Read

Shared-capacity v1 does not reproduce the useful scalar-mismatch signature:

```text
scalar mismatch 0.020, pair005:
  final residual: 0.752364
  final joint retention: 0.247636
  A/B marginal retention: 1.0 / 1.0

shared_capacity v1, pair005:
  final residual: 0.249455
  final joint retention: 0.750545
  A/B marginal retention: 0.860000 / 0.872727
```

So the current shared-capacity operator is not a clean coupling primitive for
the retained object. It acts like marginal pruning followed by dense product
closure over surviving marginals.

## Updated Morphology Atlas

After this run, the substrate morphology atlas was regenerated:

```text
source_run_count: 26
manifest_digest: 931b661ab7702a38d9d147a9
```

Shared-capacity rows classify as:

```text
pair000:
  medium_residual / marginal_loss_B / product_dense

pair001, pair002, pair005:
  medium_residual / marginal_loss_both / product_dense
```

This directly answers the morphology recommendation that proposed a
shared-capacity smoke: the v1 implementation is operational, but it should not
be scaled as the next mechanism branch.

## Recommendation

Do not scale `shared_capacity` v1.

The next empirical move should be one of:

```text
rank-order-native coupled operator:
  use ordinal candidate geometry directly, since scalar mismatch saturates and
  product-vs-zero showed joint rank-prefix is already a constraint;

or:

marginal-coverage-preserving shared-capacity v2:
  if capacity remains theoretically important, redesign the operator so marginal
  coverage is preserved first and joint-combination restriction is measured
  second.
```

The rank-order-native branch is the cleaner next step unless theory work
specifically requires finite shared capacity.

## Claim Boundary

This is an infrastructure and mechanism-diagnostic result only. It shows that a
new coupled operator can be added cleanly to Future Field Atlas, smoked under
H64, retained compactly, and compared to product/zero/scalar references. It does
not detect interaction, compatibility, support, capture, erasure, agency,
identity, value, or Omega.

# Future Field Atlas Coupled Probe Result

Status: coupled infrastructure probe completed  
Runner: `omega.future_field_atlas.run_coupled_future_field_atlas`

Superseded operationally by:

```text
docs/research_notes/validation_results/future_field_atlas_coupled_hardening_result.md
```

## Summary

This was a coupled Future Field Atlas infrastructure probe, not a science run.
The goal was to test whether the clean atlas can move from one frontier to two
interacting future fields while preserving raw topology, product baselines, and
marginal traces.

The public/runtime term is now:

```text
coupled
```

Do not use `comField` for this branch.

## Implemented Shape

The coupled probe compares:

```text
product_baseline:
  cartesian product of A and B selected successors

coupled:
  joint energy rank-prefix selection over the same product successors
```

The joint energy is explicit and mechanical:

```text
joint_transition_energy =
  A_candidate_energy
  + B_candidate_energy
  + coupling_strength * abs(A_rank_offset_from_boundary - B_rank_offset_from_boundary)
```

This is deliberately narrow. It is a substrate/instrument test, not a claim that
this coupling is the correct theory object.

Primary outputs:

```text
coupled_condition_manifest.csv.gz
coupled_scan_manifest.csv.gz
coupled_joint_frontier_nodes_by_horizon.csv.gz
coupled_joint_frontier_edges_by_step.csv.gz
coupled_joint_frontier_profile_by_horizon.csv.gz
coupled_marginal_retention_by_horizon.csv.gz
coupled_joint_vs_product_residual_by_horizon.csv.gz
coupled_cross_projection_delta_by_horizon.csv.gz
coupled_reconstruction_audit_summary.csv.gz
coupled_artifact_completeness_summary.csv.gz
```

Claim boundary:

```text
coupled infrastructure probe only; no Omega, agency, identity, valuerhood,
value, candidate-promotion, holdout, or causal claim
```

## Smoke Results

Three single-pair smokes completed.

### H8

Local output:

```text
results/future_field_atlas/20260601_coupled_h8_smoke/
```

Readout:

```text
status: COMPLETED
elapsed_seconds: 0.331
joint_node_rows: 1169
joint_edge_rows: 6588
profile_rows: 18
marginal_rows: 9
residual_rows: 9
cross_projection_rows: 18
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction_audit_passed: 1
total output size: about 0.40 MB
```

### H16

Local output:

```text
results/future_field_atlas/20260601_coupled_h16_probe/
```

Readout:

```text
status: COMPLETED
elapsed_seconds: 0.746
joint_node_rows: 2749
joint_edge_rows: 16908
profile_rows: 34
marginal_rows: 17
residual_rows: 17
cross_projection_rows: 34
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction_audit_passed: 1
total output size: about 1.00 MB
```

### H32

Local output:

```text
results/future_field_atlas/20260601_coupled_h32_probe_v2/
```

Readout:

```text
status: COMPLETED
elapsed_seconds: 1.566
joint_node_rows: 5909
joint_edge_rows: 37548
profile_rows: 66
marginal_rows: 33
residual_rows: 33
cross_projection_rows: 66
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction_audit_passed: 1
total output size: about 2.20 MB
```

Final H32 horizon:

```text
product_joint_support_count: 100
coupled_joint_support_count: 97
joint_support_intersection_count: 97
joint_support_residual_fraction: 0.03
A_marginal_retention_fraction: 1.0
B_marginal_retention_fraction: 1.0
```

## Reconstruction Audits

All three smokes passed:

```text
coupled_profile_reconstructs_from_node_rows
coupled_marginal_retention_reconstructs_from_node_rows
coupled_joint_residual_reconstructs_from_node_rows
```

The H32 pass checked:

```text
profile rows: 66 checked, 0 failed
marginal rows: 33 checked, 0 failed
residual rows: 33 checked, 0 failed
```

## Parallel / Completeness Repair Smoke

A two-pair H16 parallel smoke was run to test process-pool execution and expose
first-order output growth under multiple coupled pairs.

Local output:

```text
results/future_field_atlas/20260601_coupled_h16_pair2_parallel_smoke_v2/
```

Readout:

```text
status: COMPLETED
elapsed_seconds: 15.834
workers: 2
coupled_pairs_completed: 2 / 2
joint_node_rows: 51924
joint_edge_rows: 202406
profile_rows: 68
marginal_rows: 34
residual_rows: 34
cross_projection_rows: 68
internal_cap_events: 0
artifact_completeness_statuses: complete,truncated_noninterpretable
reconstruction_audit_passed: 1
total output size: about 12.50 MB
```

This smoke intentionally surfaced a publication-schema issue: once emitted raw
node rows are truncated, marginal-retention and joint-residual summaries are no
longer reconstructible from emitted node rows at those horizons. The runner now
marks these derived rows with `feature_status` and reconstruction audits skip
non-complete topology instead of treating it as a failed reconstruction.

Parallel-smoke reconstruction audit:

```text
coupled_profile_reconstructs_from_node_rows:
  PASS, 46 checked, 0 failed, 22 skipped

coupled_marginal_retention_reconstructs_from_node_rows:
  PASS, 22 checked, 0 failed, 12 skipped

coupled_joint_residual_reconstructs_from_node_rows:
  PASS, 22 checked, 0 failed, 12 skipped
```

This means the coupled branch is preserving the completeness semantics we want:
complete derived rows must reconstruct from raw topology; non-complete rows
remain visible and noninterpretable rather than silently masquerading as
complete measurements.

## Read

This is a clean go for a larger coupled infrastructure smoke.

The important operational result is that coupled output is currently
manageable at single-pair H32 scale:

```text
H8:  about 0.40 MB
H16: about 1.00 MB
H32: about 2.20 MB
```

Growth was tame in this first shape because the component frontiers saturated
small and the coupled selector retained almost all marginal support. That should
not be assumed for broader design sets.

## Next Recommendation

Before a medium coupled infrastructure sweep, decide whether the next pass is
allowed to contain `truncated_noninterpretable` raw topology rows. The two-pair
H16 smoke already hit raw node/edge row limits under the protective defaults.

If the next pass needs complete topology, first add sharded coupled raw topology
or deliberately raise coupled raw row limits for a bounded design. Then run:

```text
horizon_max: 32 or 64
groups: 4-8
fresh_seeds_per_group: 1-2
pair_count: 4-8
workers: 8-18
joint_effective_out_degree: 3, 4, 6
coupling_strength: 0.0, 0.1, 0.25, 0.5
```

Required gates:

```text
reconstruction audits pass
artifact completeness remains complete, or explicitly noninterpretable rows are excluded from interpretation
internal cap events remain rare and visible
product baseline remains explicit
marginal retention reconstructs from raw joint node rows
no Omega / agency / value labels enter primary artifacts
```

The next engineering target is sharding coupled raw topology before expanding
to many pairs or H64/H128.

# Future Field Atlas Coupled Worker-Spool Scale Validation Result

Status: completed cleanly  
Runner: `omega.future_field_atlas.run_coupled_future_field_atlas`  
Instrument version: `0.4.1`

## Summary

This pass validates worker-side spooling as the coupled atlas data-plane repair
for larger H64/H128 scans. It is an infrastructure and manageability result,
not a science result.

Allowed claim:

```text
The coupled atlas can now complete H64 pair8 and H128 pair8 worker-spooled
runs with complete raw topology, no internal caps, no pair failures, and clean
reconstruction audits.
```

Blocked claims:

```text
interaction
compatibility
support
capture
erasure
agency
identity
value
valuerhood
Omega validation
```

## Data-Plane Change Under Test

Mode:

```text
--raw-topology-output-mode worker_spool
```

Each worker writes pair-local raw topology and compact summaries under:

```text
coupled_pair_spool/<pair_id>/
```

The parent process receives only compact descriptors and emits spool manifests.
This avoids returning huge raw node/edge lists through Windows multiprocessing
IPC, which caused the earlier H128 pair4 parallel failure.

## Runs

Common configuration:

```text
horizon_schedule: dense
fresh_seeds_per_group: 1
start_samples: 1
selection_operator_a: rank_prefix:m=3
selection_operator_b: rank_subset:m=4:retain=1|2|3:remove=4
macro_invariant_kind: symbol_histogram_distance
macro_invariant_beta: 0.10
rank_boundary_k: 3
joint_effective_out_degree: 4
coupling_strength: 0.25
max_internal_joint_frontier_states: 100000
max_joint_frontier_nodes_per_horizon: 100000
max_joint_edges_per_step: 1000000
csv_output_mode: gzip
gzip_compresslevel: 1
```

### H64 Pair2 Equivalence

Local output:

```text
results/future_field_atlas/20260601_coupled_worker_spool_h64_pair2_equivalence_v2/
```

Readout:

```text
status: COMPLETED
elapsed_seconds: 286.943
workers: 2
coupled_pairs_completed: 2 / 2
coupled_pairs_failed: 0
joint_node_rows: 989903
joint_edge_rows: 6427266
internal_cap_events: 0
artifact_completeness_statuses: complete
audit status counts: PASS 3
medium_sweep_interpretation_allowed: 1
finalization_seconds: 0.102
total_output_size: 379325820 bytes
```

Equivalence check against the earlier sharded H64 pair2 run:

```text
node rows: exact match
edge rows: exact match
pair000 edge rows: 78828
pair001 edge rows: 6348438
```

### H64 Pair8 Breadth

Local output:

```text
results/future_field_atlas/20260601_coupled_worker_spool_h64_pair8_broad/
```

Readout:

```text
status: COMPLETED
elapsed_seconds: 372.369
workers: 4
coupled_pairs_completed: 8 / 8
coupled_pairs_failed: 0
joint_node_rows: 3231039
joint_edge_rows: 22127782
internal_cap_events: 0
artifact_completeness_statuses: complete
audit status counts: PASS 3
medium_sweep_interpretation_allowed: 1
finalization_seconds: 0.561
total_output_size: 1295150487 bytes
```

Pair edge rows:

```text
pair000:    78828
pair002:   755316
pair004:   665609
pair006:   679489
pair007:   676574
pair001:  6348438
pair003:  6543832
pair005:  6379696
```

Compared with the earlier sharded H64 pair8 baseline:

```text
logical rows: exact match
elapsed_seconds: 1182.177 -> 372.369
finalization_seconds: 799.430 -> 0.561
```

### H128 Pair4 Retry

Local output:

```text
results/future_field_atlas/20260601_coupled_worker_spool_h128_pair4_retry/
```

Readout:

```text
status: COMPLETED
elapsed_seconds: 960.732
workers: 4
coupled_pairs_completed: 4 / 4
coupled_pairs_failed: 0
joint_node_rows: 4426138
joint_edge_rows: 28945038
internal_cap_events: 0
artifact_completeness_statuses: complete
audit status counts: PASS 3
medium_sweep_interpretation_allowed: 1
finalization_seconds: 0.317
total_output_size: 1706908962 bytes
```

Pair edge rows:

```text
pair000:    161388
pair002:   1576436
pair001:  13409366
pair003:  13797848
```

This repairs the prior H128 pair4 parallel attempt, where two heavy pairs
failed during multiprocessing result transfer.

### H128 Pair8 Breadth

Local output:

```text
results/future_field_atlas/20260601_coupled_worker_spool_h128_pair8_breadth/
```

Readout:

```text
status: COMPLETED
elapsed_seconds: 1226.621
workers: 4
coupled_pairs_completed: 8 / 8
coupled_pairs_failed: 0
joint_node_rows: 6757727
joint_edge_rows: 46568294
internal_cap_events: 0
artifact_completeness_statuses: complete
audit status counts: PASS 3
medium_sweep_interpretation_allowed: 1
finalization_seconds: 0.644
total_output_size: 2724341761 bytes
```

Pair edge rows:

```text
pair000:    161388
pair004:   1389065
pair002:   1576436
pair006:   1418945
pair007:   1409502
pair001:  13409366
pair005:  13405744
pair003:  13797848
```

## Reconstruction Audits

All four scale runs reported:

```text
coupled_profile_reconstructs_from_node_rows: PASS
coupled_marginal_retention_reconstructs_from_node_rows: PASS
coupled_joint_residual_reconstructs_from_node_rows: PASS
```

No run produced:

```text
pair failures
run errors
internal cap events
sampled rows
truncated_noninterpretable rows
NO_COMPLETE_ROWS audits
FAIL audits
```

## Read

Worker-side spooling solves the immediate coupled H128 Windows IPC failure and
collapses parent finalization time from minutes to less than a second at these
scales. It does not reduce raw topology volume. The limiting factor is now
plain data volume and worker-side write time.

The broad H128 pair8 run emitted about:

```text
46.6M edge rows
6.8M node rows
2.72 GB compressed output
20.4 min wall clock
```

This is manageable on the desktop for bounded calibration and infrastructure
runs, but not yet a comfortable default for broad exploratory sweeps. Pair
skew remains strong: three heavy pairs dominate H128 output.

## Recommendation

Use worker-spooled raw topology as the coupled atlas default for medium and
larger coupled runs.

Near-term operating envelope:

```text
H64 pair8:
  safe default breadth check
  about 1.30 GB compressed output
  about 6.2 min wall clock on this desktop

H128 pair4:
  safe depth check
  about 1.71 GB compressed output
  about 16.0 min wall clock

H128 pair8:
  feasible upper breadth check
  about 2.72 GB compressed output
  about 20.4 min wall clock
```

Next engineering step:

```text
add a compact retention/summarizer path that keeps manifests, profiles,
residuals, marginal summaries, and per-pair row counts while allowing raw
pair spool files to be archived or discarded after a rebuild contract is
emitted.
```

Next empirical step:

```text
run coupled parameter sweeps only after deciding which raw topology retention
level is required for the question being asked.
```

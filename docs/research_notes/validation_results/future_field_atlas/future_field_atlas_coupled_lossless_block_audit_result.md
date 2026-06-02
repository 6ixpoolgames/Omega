# Future Field Atlas Coupled Lossless-Block Audit Result

Status: optional compressor implemented; exact-repeat compression did not help  
Runner: `omega.future_field_atlas.run_coupled_future_field_atlas`

## Summary

This pass tested the next proposed storage repair after the coupled H64 staged
sweep: a lossless repeated-horizon block compressor for coupled raw topology.

The implementation was kept modular:

```text
omega/future_field_atlas/lossless_blocks.py
```

The coupled runner only wires this module into the output path.

This was an infrastructure audit, not a science run. It makes no claim about
Omega, agency, identity, value, valuerhood, support, capture, erasure,
compatibility, or interaction.

## Implemented Output Mode

Added optional mode:

```text
--raw-topology-output-mode lossless_blocks
```

Logical raw artifacts remain:

```text
coupled_joint_frontier_nodes_by_horizon.csv
coupled_joint_frontier_edges_by_step.csv
```

Physical optional artifacts:

```text
coupled_joint_frontier_nodes_by_horizon_lossless_blocks.csv.gz
coupled_joint_frontier_nodes_by_horizon_lossless_block_manifest.csv.gz
coupled_joint_frontier_edges_by_step_lossless_blocks.csv.gz
coupled_joint_frontier_edges_by_step_lossless_block_manifest.csv.gz
```

The compressor groups consecutive horizons only when the row content is exactly
identical after removing horizon fields:

```text
nodes:
  horizon is reconstructed over [horizon_start, horizon_end]

edges:
  source_horizon is reconstructed over [horizon_start, horizon_end]
  target_horizon = source_horizon + 1
```

This is intentionally strict and lossless. It does not merge by count, shape,
state histogram, or interpretation.

Default coupled raw topology output remains:

```text
--raw-topology-output-mode sharded
```

Confirmed by a default-mode H4 smoke:

```text
results/future_field_atlas/20260601_coupled_default_sharded_h4_smoke/

raw_topology_output_mode: sharded
shard manifest emitted: yes
lossless block artifact emitted: no
status: COMPLETED
audit status counts: PASS 3
```

## Validation

Passed:

```text
ruff check omega/future_field_atlas tests/test_coupled_atlas_hardening.py
compileall omega/future_field_atlas tests
pytest tests/test_coupled_atlas_hardening.py -q
```

Unit tests:

```text
7 passed
```

The added test constructs repeated node/edge rows, compresses them into
lossless blocks, and expands them back to the exact logical rows.

## H8 Smoke

Local output:

```text
results/future_field_atlas/20260601_coupled_lossless_blocks_h8_smoke/
```

Readout:

```text
status: COMPLETED
elapsed_seconds: 0.551
coupled_pairs_completed: 1 / 1
joint_node_rows: 1169
joint_edge_rows: 6588
artifact_completeness_statuses: complete,lossless_compressed
audit status counts: PASS 3
medium_sweep_interpretation_allowed: 1
total_output_size: about 0.44 MB
```

Compression:

```text
raw_topology_node_compression_ratio: 1.0
raw_topology_edge_compression_ratio: 1.0
```

Read: the schema and status path worked, but H8 had no repeated exact topology.

## H32 Pair2 Audit

Local output:

```text
results/future_field_atlas/20260601_coupled_lossless_blocks_h32_pair2/
```

Readout:

```text
status: COMPLETED
elapsed_seconds: 230.923
coupled_pairs_completed: 2 / 2
joint_node_rows: 445487
joint_edge_rows: 2855522
artifact_completeness_statuses: complete,lossless_compressed
audit status counts: PASS 3
medium_sweep_interpretation_allowed: 1
total_output_size: about 182.46 MB
```

Compression:

```text
node blocks: 132
node stored rows: 445487
node logical rows: 445487
node max horizon_count: 1
node compression ratio: 1.0

edge blocks: 128
edge stored rows: 2855522
edge logical rows: 2855522
edge max horizon_count: 1
edge compression ratio: 1.0
```

Timing:

```text
flatten_rows: 0.101s
summaries_manifests_audits: 1.686s
raw_topology_lossless_block_build: 49.298s
parallel_artifact_writes: 112.858s
finalization_seconds: 163.943
```

Comparison to the earlier H32 sharded pair2 run:

```text
sharded H32 total output: about 160.83 MB
lossless-block H32 total output: about 182.46 MB

sharded H32 finalization: about 80.94s
lossless-block H32 finalization: about 163.94s
```

## Read

The previous staged sweep showed stable frontier counts after roughly H16, but
this audit shows that the exact raw topology is not repeating. State and edge
identities continue changing even while counts stabilize.

Therefore:

```text
exact repeated-block compression is not the right default compressor
```

The mode remains useful as an audit tool because it can prove whether exact
repeated topology exists in a future run. It should not be used as the default
for current coupled scaling.

## Recommendation

Keep:

```text
--raw-topology-output-mode sharded
```

as the coupled default.

If more compression is needed, the next candidate should be a different
lossless representation:

```text
dictionary/factorized topology:
  store state dictionary once
  store edge endpoints as integer ids
  store per-horizon edge tables as compact id arrays

or delta topology:
  store horizon-to-horizon additions/removals relative to a previous frontier
  only if reconstruction tests prove exact recovery
```

Do not use a shape-only or count-only compressor for primary raw topology. That
would be useful for summaries, but not as a replacement for reconstructible raw
artifacts.

## Claim Boundary

Allowed:

```text
An optional exact repeated-horizon compressor was implemented and audited. It
preserves reconstruction semantics, but found no repeated exact topology in the
H32 pair2 coupled design and should not become the default output mode.
```

Not allowed:

```text
The result implies anything about interaction, compatibility, support, capture,
erasure, agency, identity, value, valuerhood, or Omega.
```

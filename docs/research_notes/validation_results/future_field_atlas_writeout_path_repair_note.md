# Future Field Atlas Write-Out Path Repair Note

Status: operational write-path repair completed  
Runner: `omega.future_field_atlas.run_future_field_atlas`

## Summary

This was an engineering repair, not a science result. The prior H128 calibration
pass showed that scan workers finished quickly while final artifact production
dominated wall time. The repair keeps the atlas instrument flexible while
reducing pressure from large raw topology writes.

Implemented changes:

```text
gzip compression level default: 1
raw topology output default: sharded
artifact write path: parallelized across independent artifacts
finalization timings: recorded in status, manifest, and report
```

The logical raw topology artifacts remain:

```text
frontier_nodes_by_horizon.csv
frontier_edges_by_step.csv
```

In default physical storage, they are emitted as shard directories plus shard
manifests:

```text
frontier_nodes_by_horizon_shard_manifest.csv.gz
frontier_nodes_by_horizon_shards/part-*.csv.gz
frontier_edges_by_step_shard_manifest.csv.gz
frontier_edges_by_step_shards/part-*.csv.gz
```

The consolidated CSV form remains available:

```text
--raw-topology-output-mode consolidated
--raw-topology-output-mode both
```

## Smoke Check

A tiny H4 traceability smoke completed with:

```text
status: COMPLETED
scans_completed: 8 / 8
reconstruction_audit_passed: 1
artifact_completeness_statuses: complete
raw_topology_output_mode: sharded
gzip_compresslevel: 1
frontier_node_rows: 720
frontier_edge_rows: 1158
```

The manifest listed both shard manifests and the physical shard files with row
counts. The local smoke output was deleted after verification.

## Local Data Policy

Large local calibration outputs from this iteration were deleted to avoid
storage creep. Retain compact documentation and committed code; do not retain
bulky local raw topology outputs unless a run carries strong evidence or is
explicitly promoted.

Deleted local directories:

```text
results/future_field_atlas/20260601_phase0_1_calibration_h128_g4_fresh2_start2/
results/future_field_atlas/20260601_phase0_1_writeout_opt_h32_smoke/
results/future_field_atlas/20260601_phase0_1_writeout_opt_h128_g4_fresh2_start2/
results/future_field_atlas/20260601_writeout_opt_traceability_tiny_delete_me/
```

## Interpretation

The repair does not change the measured topology. It changes physical artifact
layout and compression settings. The instrument remains in flux, so this is a
minimal storage-path repair rather than a deep I/O subsystem rewrite.

The H32 writeout smoke before deletion suggested raw topology writing was not
the dominant small-run bottleneck; multiscale matrix construction and residual
construction dominated at that scale. The new finalization timing fields should
make the true large-run bottleneck explicit before further optimization.

Follow-up update:

```text
omega.future_field_atlas.cleanup_runs
```

was added as an age-based dry-run-first cleanup utility. The standing policy is
to retain recent calibration outputs for a short review grace period, then clean
older unpromoted run directories unless a run is explicitly promoted.

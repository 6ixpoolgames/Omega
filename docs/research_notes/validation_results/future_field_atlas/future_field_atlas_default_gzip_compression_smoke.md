# Future Field Atlas Default-Gzip Compression Smoke

Status: operational compression smoke completed  
Primary output: `results/future_field_atlas/20260601_phase0_1_default_gzip_h32_rerun/`  
Runner: `omega.future_field_atlas.run_future_field_atlas`

## Executive Summary

This was a storage/manageability smoke, not a science result. The goal was to
make lossless gzip CSV output the default for primary Future Field Atlas CSV
artifacts and verify that the default path still produces reconstructible atlas
outputs.

```text
status: COMPLETED
workers: 4
conditions: 8
scans_completed: 8 / 8
elapsed_seconds: 16.274
frontier_node_rows: 30671
frontier_edge_rows: 107034
csv_output_mode: gzip
reconstruction_audit_passed: 1
artifact_completeness_statuses: complete
```

All reconstruction audits passed:

```text
condition_identity_traceability: PASS
frontier_profile_reconstructs_from_node_and_edge_rows: PASS
rank_boundary_geometry_reconstructs_from_edge_rows: PASS
adjacent_transport_matrices_reconstruct_from_edge_rows: PASS
selection_operator_geometry_reconstructs_from_rank_boundary_rows: PASS
```

## Compression Read

Manual gzip compression on the compact H32 CSV artifacts showed the easy win:

```text
selected compact CSV total: 58.946 MB
selected gzip CSV total: 2.504 MB
compression ratio: about 23.5x

frontier_edges_by_step.csv: 42.754 MB -> 1.926 MB, about 22.2x
frontier_nodes_by_horizon.csv: 11.442 MB -> 0.517 MB, about 22.1x
frontier_membership_timeseries.csv: 3.100 MB -> 0.031 MB, about 101.6x
```

Default gzip H32 smoke output:

```text
total output size: 3.111 MB
frontier_edges_by_step.csv.gz: 1.983 MB
frontier_nodes_by_horizon.csv.gz: 0.536 MB
raw_transport_matrices_multiscale.npz: 0.302 MB
raw_transport_matrices_adjacent.npz: 0.205 MB
```

Comparison against prior H32 outputs:

```text
publication-schema H32 output: about 370.7 MB
compact plain H32 output: about 59.7 MB
default-gzip H32 output: about 3.1 MB
reduction vs publication-schema H32: about 119x
reduction vs compact plain H32: about 19x
```

## Implementation Note

The runner now defaults to:

```text
--csv-output-mode gzip
```

The mode can be overridden:

```text
--csv-output-mode plain
--csv-output-mode both
```

Logical artifact names remain the schema names, such as
`frontier_edges_by_step.csv`. In default physical output, those primary CSV
artifacts appear on disk as `frontier_edges_by_step.csv.gz`. The run manifest
records `csv_output_mode` and points manifest fields to the physical artifact
names.

Manifest row counts for primary atlas CSV artifacts are taken from the rows
already produced during finalization, so large gzip artifacts do not need to be
decompressed just to populate `output_files`.

## Recommendation

Keep gzip as the default for small and medium atlas runs. It is lossless,
simple, reconstructible, stream-readable, and gives most of the immediate
storage relief without changing the measured topology.

For larger coupled or long-horizon runs, the next storage step should be a
schema-native columnar artifact such as Parquet or Arrow, or a deduplicated
edge-block store keyed by scan and horizon. That should be a second storage
backend, not a semantic filter.

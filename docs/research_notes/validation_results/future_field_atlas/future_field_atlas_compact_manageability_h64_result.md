# Future Field Atlas Compact Manageability H64 Result

Status: operational scale/manageability run completed
Primary output: `results/future_field_atlas/20260601_phase0_1_compact_manageability_h64_g4_start2/`
Runner: `omega.future_field_atlas.run_future_field_atlas`

## Executive Summary

This was a pre-coupling operational run, not a science result. The goal was to
check whether normalized atlas output remains reconstructible while reducing
redundant raw CSV size.

```text
status: COMPLETED
workers: 18
conditions: 32
scans_completed: 64 / 64
elapsed_seconds: 314.261
frontier_node_rows: 264567
frontier_edge_rows: 1866167
selection_operator_geometry_rows: 32
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

## Output Manageability

The compact schema moved repeated formal metadata out of high-volume raw
node/edge rows and into:

```text
formal_spec_manifest.csv
condition_identity_manifest.csv
scan_manifest.csv
```

H32 comparison:

```text
previous publication-audit H32 output: about 370.7 MB
compact H32 output: about 59.7 MB
reduction: about 6.2x
```

H64 manageability output:

```text
total output: about 907.2 MB
frontier_edges_by_step.csv: about 758.0 MB
frontier_nodes_by_horizon.csv: about 100.2 MB
frontier_membership_timeseries.csv: about 25.1 MB
all other files combined: about 24 MB
```

The dominant remaining storage pressure is still the raw edge CSV. The matrix
artifacts are compact by comparison.

## Recommendation

The compact schema is good enough for the next pre-coupling scale step, but
larger runs should add a second, principled storage layer before going long:

```text
primary raw topology:
  keep compact CSV for small/medium audit runs

larger raw topology:
  write node/edge tables as compressed columnar artifacts
  preserve CSV manifests and summaries
  keep reconstruction audits against the emitted primary artifact

publication-facing record:
  commit docs and compact summaries only
  keep raw topology local unless explicitly promoted
```

The next compressor should be lossless and schema-native, not a semantic
filter. Good candidates are gzipped CSV for immediate simplicity or Parquet /
Arrow for columnar scale. The scientific rule should remain:

```text
compression may change representation;
it must not change the measured topology.
```

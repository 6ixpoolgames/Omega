# Future Field Atlas Changelog

This changelog records implementation and data-plane changes that do not need
a full retained result note.

Use this file for tooling, schema, retention, and runner polish. Use
`docs/OMEGA_RUNNING_LOG.md` and `docs/research_notes/validation_results/` only
when a run or decision changes the project state.

## 2026-06-01

### Coupled Worker-Side Spooling

Added coupled runner output mode:

```text
--raw-topology-output-mode worker_spool
```

Each worker writes pair-local raw and summary artifacts under:

```text
coupled_pair_spool/<pair_id>/
```

The parent process receives only a compact descriptor and later aggregates:

```text
coupled_pair_spool_manifest.csv.gz
coupled_joint_frontier_nodes_by_horizon_spool_manifest.csv.gz
coupled_joint_frontier_edges_by_step_spool_manifest.csv.gz
```

This is the first repair for the H128 Windows multiprocessing result-transfer
failure. It avoids returning huge raw node/edge row lists through IPC.

Validation smokes:

```text
H8 pair2 worker_spool:
  status: COMPLETED
  pairs: 2 / 2
  errors: 0
  caps: 0
  edge rows: 201743
  finalization_seconds: 0.079

H16 pair2 worker_spool:
  status: COMPLETED
  pairs: 2 / 2
  errors: 0
  caps: 0
  edge rows: 1069650
  finalization_seconds: 0.084
```

### Rebuild Contract Metadata

Added a run-level rebuild contract emitted by current Future Field Atlas
runners:

```text
future_field_atlas_rebuild_contract.json
```

The contract records:

```text
instrument_version
artifact_schema_version
runner_version
protocol_version
runner_module
command_line
Python version
platform
dependency versions
git commit / branch / dirty flag
config digest
raw data retention posture
```

New runs can now distinguish:

```text
exact_rebuild_supported
logical_rebuild_only
```

This does not make older runs fully rebuildable. It defines the target posture
for future runs so raw topology can be retained, archived, or discarded with a
clear audit trail.

Tiny verification smoke:

```text
results/future_field_atlas/20260601_rebuild_contract_triadic_h1_smoke/
status: COMPLETED
future_field_atlas_rebuild_contract.json emitted
```

# Future Field Atlas Changelog

This changelog records implementation and data-plane changes that do not need
a full retained result note.

Use this file for tooling, schema, retention, and runner polish. Use
`docs/OMEGA_RUNNING_LOG.md` and `docs/research_notes/validation_results/` only
when a run or decision changes the project state.

## 2026-06-01

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

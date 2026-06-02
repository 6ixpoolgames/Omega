# Future Field Atlas Changelog

This changelog records implementation and data-plane changes that do not need
a full retained result note.

Use this file for tooling, schema, retention, and runner polish. Use
`docs/OMEGA_RUNNING_LOG.md` and `docs/research_notes/validation_results/` only
when a run or decision changes the project state.

## 2026-06-02

### Rank-Order Boundary Coupled Selector

Added a new coupled selector family:

```text
joint_selection_family = rank_order_boundary
```

For each joint source, the selector constructs the same product successors used
by the coupled runner and selects up to `joint_effective_out_degree` by an
ordinal rank-boundary tuple:

```text
abs(A_rank_offset_from_boundary - B_rank_offset_from_boundary)
A_candidate_rank + B_candidate_rank
max(A_candidate_rank, B_candidate_rank)
min(A_candidate_rank, B_candidate_rank)
abs(A_rank_offset_from_boundary) + abs(B_rank_offset_from_boundary)
target_joint_state_id
```

The selector does not use scalar `coupling_strength` as a tuning control. It is
intended as the clean next mechanism probe after scalar mismatch saturation and
the negative shared-capacity v1 smoke.

Tests:

```text
tests/test_coupled_atlas_hardening.py
```

### Shared-Capacity Coupled Selector

Added a new coupled selector family:

```text
joint_selection_family = shared_capacity
```

For each joint source, the selector constructs the same product successors used
by the coupled runner, orders them by component energy, and selects up to
`joint_effective_out_degree` while limiting repeated use of the same A/B
marginal successor. The per-marginal cap is derived from the joint effective
out-degree and candidate marginal counts; no extra tuned capacity parameter was
introduced.

The shared-capacity selector ignores the scalar rank-boundary mismatch penalty
so it remains a distinct operator-family smoke, not a scalar-mismatch variant.

The H64 smoke completed cleanly, but `shared_capacity` v1 should not be scaled
as-is: it prunes marginal support and then becomes product-dense over surviving
marginals. See
`docs/research_notes/validation_results/future_field_atlas/future_field_atlas_shared_capacity_h64_smoke_result.md`.

Tests:

```text
tests/test_coupled_atlas_hardening.py
```

### Substrate Morphology Summary Utility

Added:

```text
omega.future_field_atlas.substrate_morphology_summary
```

The utility postprocesses retained Future Field Atlas coupled outputs into a
compact morphology atlas:

```text
field_morphology_summary.csv
pair_morphology_summary.csv
operator_sensitivity_summary.csv
horizon_onset_summary.csv
observable_geometry_summary.csv
pair_class_exemplar_summary.csv
morphology_next_targets.csv
substrate_morphology_manifest.json
substrate_morphology_report.md
```

It also emits optional/status morphology tables when retained inputs support
them:

```text
rank_boundary_offset_morphology.csv
joint_candidate_crossing_morphology.csv
composition_residual_morphology.csv
frontier_growth_regime_summary.csv
```

Validated on the retained coupled H64/H128 broad runs, scalar ladders,
mechanism-resolution runs, pair005 forensics, and the shared-capacity H64
smoke. The regenerated atlas pass ingests 26 clean coupled run directories and
2 compact summary directories.

Tests:

```text
tests/test_substrate_morphology_summary.py
```

### Documentation Directory Cleanup

Reorganized repository-facing documentation to reduce root-folder clutter:

```text
docs/specs/current/
  active instrument specs

docs/specs/archive/<branch>/
  historical branch specs, handoffs, addenda, and runbooks

docs/research_notes/validation_results/future_field_atlas/
  current retained Future Field Atlas result notes

docs/research_notes/validation_results/<archived_branch>/
  retained historical branch result notes
```

Added README policy files for `docs/specs/` and
`docs/research_notes/validation_results/`. Future specs and retained result
notes should use those branch folders rather than returning to the flat
`docs/` and `validation_results/` roots.

### Coupled Mechanism Summary Utility

Added:

```text
omega.future_field_atlas.coupled_mechanism_summary
```

The utility postprocesses coupled Future Field Atlas mechanism-resolution runs
into compact CSV summaries:

```text
run_gate_summary.csv
coupling_ladder_summary.csv
near_zero_threshold_summary.csv
pair_level_residual_summary.csv
pair005_forensic_summary.csv
product_selector_sanity_summary.csv
horizon_of_divergence_summary.csv
joint_candidate_crossing_summary.csv
mechanism_summary_manifest.json
```

Also added `--pair-indexes` to the coupled runner so targeted forensic passes
can run a specific pair without pretending that a pair-count slice is the same
object.

Tests:

```text
tests/test_coupled_atlas_hardening.py
```

### Compact Retention Summarizer

Added:

```text
omega.future_field_atlas.retention_summary
```

The utility builds compact retained bundles for Future Field Atlas run
directories:

```text
_retention_summary/
  retained_run_summary.json
  retained_run_summary.md
  retained_deletion_plan.json
  retained_pair_skew.csv.gz
  retained_metric_summary.csv.gz
  retained_artifact_inventory.csv.gz
  compact_artifacts/
```

It reads run status/config, rebuild contract, manifests, spool summaries,
readiness rows, reconstruction audits, completeness rows, residuals, marginal
summaries, and profiles. It then emits a deletion recommendation. For clean
worker-spooled coupled runs, `--delete-raw-spools` deletes only
`coupled_pair_spool/` and writes `RAW_TOPOLOGY_DELETED.json`.

Validated on the retained H64/H128 worker-spool scale runs:

```text
H64 pair8:
  raw spool deleted: 1.206111 GiB
  retained folder size after pruning: about 0.19 MB

H128 pair8:
  raw spool deleted: 2.537121 GiB
  retained folder size after pruning: about 0.25 MB
```

Tests:

```text
tests/test_retention_summary.py
```

## 2026-06-01

### Worker-Spool Scale Validation

Validated `worker_spool` beyond smoke scale:

```text
H64 pair2 equivalence:
  exact logical row match with prior sharded baseline
  finalization_seconds: 0.102

H64 pair8 breadth:
  status: COMPLETED
  edge rows: 22127782
  elapsed_seconds: 372.369
  finalization_seconds: 0.561

H128 pair4 retry:
  status: COMPLETED
  edge rows: 28945038
  elapsed_seconds: 960.732
  finalization_seconds: 0.317

H128 pair8 breadth:
  status: COMPLETED
  edge rows: 46568294
  elapsed_seconds: 1226.621
  finalization_seconds: 0.644
```

All scale runs completed with zero pair failures, zero internal caps, complete
artifact status, and reconstruction audits `PASS 3`. This validates the spool
path as the coupled default for medium and larger raw-topology runs. Remaining
pressure is output retention and summarization, not parent-process IPC.

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

# Omega Running Log

This is the living operational log for the Omega validation workspace. Update it
after every meaningful theory-side decision, probe implementation, or compute
run.

Entries are organized in rough reverse chronological order, with the most recent
patch notes at the top.

## 2026-06-02

### Future Field Atlas Coupled H64 Ladder

Ran the first constrained coupled Future Field Atlas science pass after the
worker-spool and compact-retention repairs:

```text
horizon_max: 64
pair_count: 8
workers: 4
coupling_strength ladder:
  0.00
  0.05
  0.10
  0.25
  0.50
```

All five stages completed cleanly:

```text
coupled_pairs_completed: 8 / 8
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS 3
medium_sweep_interpretation_allowed: 1
raw spools pruned after compact retention summary: yes
```

Run-level read:

```text
0.00:
  edge rows: 22866722
  node rows: 3419750
  mean joint-vs-product residual: 0.191149
  mean joint retention: 0.808851
  A/B marginal retention means: 0.980608 / 0.972859

0.05 through 0.50:
  edge rows: 22127782
  node rows: 3231039
  mean joint-vs-product residual: 0.183363
  mean joint retention: 0.816637
  A/B marginal retention means: 1.0 / 1.0
```

Interpretation:

```text
The tested positive mismatch penalties are numerically identical after sorting
rows and ignoring operator identity fields. This looks thresholded at the
current resolution: zero penalty differs from positive penalty, but 0.05,
0.10, 0.25, and 0.50 do not form a graded ladder.
```

Pair-level caveat:

```text
At horizon 64, positive penalty lowers residual for seven of eight pairs, but
pair005 jumps from 0.244091 residual at 0.00 to 0.752364 at positive strengths.
Aggregate summaries must be pair-aware.
```

Retained note:

```text
docs/research_notes/validation_results/future_field_atlas_coupled_h64_ladder_result.md
```

### Future Field Atlas Compact Retention Utility

Implemented a compact retention utility:

```text
python -m omega.future_field_atlas.retention_summary --run <run_dir>
```

It writes:

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

For clean worker-spooled coupled runs, it can prune raw pair spools:

```text
python -m omega.future_field_atlas.retention_summary --run <run_dir> --delete-raw-spools
```

The deletion path removes only `coupled_pair_spool/` and leaves root manifests,
profiles, residuals, marginal summaries, readiness rows, rebuild contract, and
the retention bundle intact.

Applied to the retained scale runs:

```text
H64 pair8 worker_spool:
  deleted raw spool estimate: 1.206111 GiB
  retained run folder after pruning: about 0.19 MB

H128 pair8 worker_spool:
  deleted raw spool estimate: 2.537121 GiB
  retained run folder after pruning: about 0.25 MB
```

Read:

```text
The project can now run multi-GB coupled raw topology passes, retain compact
auditable summaries, and discard raw spools when the run is complete, uncapped,
and reconstruction-clean. This makes coupled parameter sweeps operationally
safe from a storage-management perspective.
```

## 2026-06-01

### Future Field Atlas Coupled Worker-Spool Scale Validation

Validated worker-side spooling across H64/H128 coupled breadth and depth runs:

```text
H64 pair2 equivalence:
  status: COMPLETED
  edge rows: 6427266
  node rows: 989903
  audits: PASS 3
  finalization_seconds: 0.102
  logical rows matched prior sharded baseline exactly

H64 pair8 breadth:
  status: COMPLETED
  edge rows: 22127782
  node rows: 3231039
  audits: PASS 3
  finalization_seconds: 0.561
  elapsed_seconds: 372.369
  output size: 1295150487 bytes

H128 pair4 retry:
  status: COMPLETED
  edge rows: 28945038
  node rows: 4426138
  audits: PASS 3
  finalization_seconds: 0.317
  elapsed_seconds: 960.732
  output size: 1706908962 bytes

H128 pair8 breadth:
  status: COMPLETED
  edge rows: 46568294
  node rows: 6757727
  audits: PASS 3
  finalization_seconds: 0.644
  elapsed_seconds: 1226.621
  output size: 2724341761 bytes
```

Read:

```text
Worker-side spooling fixes the H128 Windows IPC failure and makes parent
finalization negligible. It does not reduce raw topology volume. The next
scaling problem is retention policy and compact summarization, not IPC.
```

Retained note:

```text
docs/research_notes/validation_results/future_field_atlas_coupled_worker_spool_scale_validation_result.md
```

### Future Field Atlas Coupled Worker-Side Spooling

Implemented the first data-plane repair for H128 coupled scaling:

```text
--raw-topology-output-mode worker_spool
```

In this mode each worker writes pair-local raw topology and compact summaries:

```text
coupled_pair_spool/<pair_id>/
  coupled_joint_frontier_nodes_by_horizon.csv.gz
  coupled_joint_frontier_edges_by_step.csv.gz
  coupled_joint_frontier_profile_by_horizon.csv.gz
  coupled_reconstruction_audit_summary.csv.gz
  coupled_artifact_completeness_summary.csv.gz
  pair_spool_manifest.json
```

The parent process receives compact pair descriptors, then merges summary
tables and spool manifests. This avoids the Windows multiprocessing result
transfer failure observed in the H128 pair4 attempt.

Validation:

```text
unit tests: coupled spool path covered

H8 pair2 worker_spool:
  status: COMPLETED
  errors: 0
  internal_cap_events: 0
  edge rows: 201743
  finalization_seconds: 0.079

H16 pair2 worker_spool:
  status: COMPLETED
  errors: 0
  internal_cap_events: 0
  edge rows: 1069650
  finalization_seconds: 0.084
```

Read:

```text
Spooling does not reduce raw data volume. It removes the parent-process IPC
payload bottleneck and collapses finalization time for raw topology because
workers already wrote the heavy artifacts.
```

### Future Field Atlas Rebuild And Retention Metadata

Added a small data-plane metadata layer for future runs:

```text
omega/future_field_atlas/rebuild.py
future_field_atlas_rebuild_contract.json
```

New Future Field Atlas runners now emit a rebuild contract with:

```text
source commit
dirty-worktree flag
runner module
command line
Python/platform/dependency versions
artifact schema version
runner version
protocol version
config digest
raw data retention posture
```

Added implementation docs:

- `docs/implementation/FUTURE_FIELD_ATLAS_CHANGELOG.md`
- `docs/implementation/RUN_RETENTION_POLICY.md`

Read:

```text
Old local runs can still be discarded when redundant or irrelevant. The new
contract is the target posture for future runs, so deletion decisions can be
made against explicit retained metadata rather than ad hoc memory.
```

Verification smoke:

```text
results/future_field_atlas/20260601_rebuild_contract_triadic_h1_smoke/
status: COMPLETED
rebuild_contract emitted: yes
rebuild_status during local dirty-worktree smoke: logical_rebuild_only
```

### Future Field Atlas Coupled H64 Broad Sweep

Ran the missing broad H64 coupled breadth gate after the H128 depth pass.

Retained note:

- `docs/research_notes/validation_results/future_field_atlas_coupled_h64_broad_sweep_result.md`

Readout:

```text
horizon_max: 64
pair_count: 8
workers: 4
status: COMPLETED
elapsed_seconds: 1182.177
coupled_pairs_completed: 8 / 8
coupled_pairs_failed: 0
joint_node_rows: 3231039
joint_edge_rows: 22127782
internal_cap_events: 0
artifact_completeness_statuses: complete
audit status counts: PASS 3
medium_sweep_interpretation_allowed: 1
total_output_size: about 1.21 GiB
```

Read:

```text
Broad H64 is clean and operationally manageable at pair8. The output is highly
skewed: three heavy pairs account for most of the 22.1M edge rows and most of
the compressed output. Finalization/write-out still dominates wall time.
```

Next:

```text
Use H64 pair8 as the current breadth baseline. For broader H64 or any broad
H128, add worker-side spooling or pair-indexed heavy-pair handling.
```

### Future Field Atlas H128 Coupled Depth Gate And Triadic Profile Smoke

Ran a bounded H128 coupled depth gate and a short three-frontier profile-only
smoke.

Retained note:

- `docs/research_notes/validation_results/future_field_atlas_coupled_h128_and_triadic_profile_smoke_result.md`

H128 pair4 parallel attempt:

```text
workers: 4
coupled_pairs_requested: 4
coupled_pairs_completed: 2
coupled_pairs_failed: 2
elapsed_seconds: 651.267
joint_node_rows: 266977
joint_edge_rows: 1737824
total_output_size: about 0.096 GiB
```

Read:

```text
The pair4 attempt exposed a Windows multiprocessing result-transfer limit on
heavy H128 pairs. The partial output is an engineering signal, not a clean
scale result. The runner now distinguishes completed-with-errors from clean
completion and blocks medium-sweep interpretation readiness when run errors
are present.
```

H128 pair2 serial depth gate:

```text
workers: 1
coupled_pairs_completed: 2 / 2
elapsed_seconds: 624.553
finalization_seconds: 402.605
joint_node_rows: 2078735
joint_edge_rows: 13570754
internal_cap_events: 0
artifact_completeness_statuses: complete
audit status counts: PASS 3
total_output_size: about 0.746 GiB
```

Read:

```text
H128 coupled depth is feasible for small pair counts. The bottleneck is skewed
raw topology size, worker result transfer, and shard write-out time, not CPU
arithmetic.
```

Triadic H6 profile-only smoke:

```text
status: COMPLETED
elapsed_seconds: 6.277
triple_count_completed: 1 / 1
internal_cap_events: 0
artifact_completeness_statuses: complete
product_baseline H6: 60830 joint states
triadic H6: 9101 joint states
terminal residual: 0.8504
raw_topology_retention: not_emitted_profile_only_smoke
```

Validation:

```text
ruff check omega/future_field_atlas tests/test_coupled_atlas_hardening.py tests/test_triadic_future_field_smoke.py
python -m compileall omega/future_field_atlas tests
python -m pytest tests/test_coupled_atlas_hardening.py tests/test_triadic_future_field_smoke.py -q
git diff --check

tests: 10 passed
```

Next:

```text
Before broad H128 coupled surveys, add worker-side spooling or pair-indexed
heavy-pair handling. Keep triadic profile-only until the coupled two-frontier
path has a stable high-volume output strategy.
```

### Future Field Atlas Coupled Lossless-Block Audit

Implemented an optional, modular exact repeated-horizon block compressor for
coupled raw topology:

```text
omega/future_field_atlas/lossless_blocks.py
```

Retained note:

- `docs/research_notes/validation_results/future_field_atlas_coupled_lossless_block_audit_result.md`

Validation:

```text
ruff check omega/future_field_atlas tests/test_coupled_atlas_hardening.py
compileall omega/future_field_atlas tests
pytest tests/test_coupled_atlas_hardening.py -q

tests: 7 passed
```

H32 pair2 lossless-block audit:

```text
status: COMPLETED
elapsed_seconds: 230.923
joint_node_rows: 445487
joint_edge_rows: 2855522
artifact_completeness_statuses: complete,lossless_compressed
audit status counts: PASS 3
total_output_size: about 182.46 MB

node compression ratio: 1.0
edge compression ratio: 1.0
max node block horizon_count: 1
max edge block horizon_count: 1
```

Read:

```text
Frontier counts stabilized in the earlier H32/H64 runs, but exact raw topology
did not repeat. State and edge identities continued changing. Therefore exact
repeated-block compression is not useful as a default and is slower/larger than
the sharded output path at H32.

Keep coupled raw topology default as sharded. If we need more compression, move
toward dictionary/factorized topology or exact delta topology with
reconstruction tests.
```

Default-mode H4 smoke confirmed:

```text
raw_topology_output_mode: sharded
shard manifest emitted: yes
lossless block artifact emitted: no
audit status counts: PASS 3
```

### Future Field Atlas Coupled Sharded Staged Sweep

Implemented sharded physical output for coupled raw topology and ran staged
H8 -> H16 -> H32 -> H64 coupled infrastructure gates.

Retained note:

- `docs/research_notes/validation_results/future_field_atlas_coupled_sharded_staged_sweep_result.md`

Implementation:

```text
raw_topology_output_mode default: sharded
raw_topology_shard_pair_count: pair scans per shard
artifact_write_workers: parallel artifact writer count

default coupled raw topology layout:
  coupled_joint_frontier_nodes_by_horizon_shard_manifest.csv.gz
  coupled_joint_frontier_nodes_by_horizon_shards/part-*.csv.gz
  coupled_joint_frontier_edges_by_step_shard_manifest.csv.gz
  coupled_joint_frontier_edges_by_step_shards/part-*.csv.gz
```

Validation:

```text
ruff check omega/future_field_atlas tests/test_coupled_atlas_hardening.py
compileall omega/future_field_atlas tests
pytest tests/test_coupled_atlas_hardening.py -q
git diff --check

tests: 6 passed
```

Staged run readout:

```text
H8 pair1:
  elapsed_seconds: 0.363
  joint_node_rows: 1169
  joint_edge_rows: 6588
  total_output_size: about 0.40 MB
  audits: PASS 3

H16 pair2:
  elapsed_seconds: 55.248
  joint_node_rows: 173279
  joint_edge_rows: 1069650
  total_output_size: about 60.39 MB
  audits: PASS 3

H32 pair2:
  elapsed_seconds: 146.745
  joint_node_rows: 445487
  joint_edge_rows: 2855522
  total_output_size: about 160.83 MB
  audits: PASS 3

H64 pair2:
  elapsed_seconds: 331.432
  joint_node_rows: 989903
  joint_edge_rows: 6427266
  total_output_size: about 361.72 MB
  audits: PASS 3
```

Read:

```text
The coupled runner is infrastructure-clean through bounded H64 pair2: no caps,
complete artifacts, all reconstruction audits PASS, explicit product baseline,
and manifest-backed coupled operator identity.

The frontier saturated by about H16 in this design, but the runner still emits
full repeated step-edge topology through H64. Before many-pair H64/H128 coupled
runs, add a lossless steady-state or repeated-block topology compressor that
marks compressed artifacts as lossless_compressed and preserves reconstruction
semantics.
```

### Future Field Atlas Coupled Hardening

Implemented coupled-runner infrastructure hardening before any medium coupled
sweep.

Retained note:

- `docs/research_notes/validation_results/future_field_atlas_coupled_hardening_result.md`

Repair contents:

```text
persistent cap poisoning
audit statuses: PASS, PASS_WITH_SKIPS, NO_COMPLETE_ROWS, FAIL
run-level reconstruction_audit_clean_pass and reconstruction_audit_interpretable_pass
first-class coupled_operator_manifest.csv.gz
pairing policy manifest fields
renamed marginal projection artifact:
  coupled_marginal_projection_delta_by_horizon.csv.gz
projection_semantics: product_vs_coupled_marginal_set_delta
causal_interpretation: none
medium-scale readiness guard
```

Unit tests:

```text
tests/test_coupled_atlas_hardening.py
5 passed
```

Forced low-cap H16 pair2:

```text
status: COMPLETED
elapsed_seconds: 0.322
internal_cap_events: 64
artifact_completeness_statuses: complete,truncated_noninterpretable
audit status counts: PASS_WITH_SKIPS 3
reconstruction_audit_clean_pass: 0
reconstruction_audit_interpretable_pass: 1
medium_sweep_interpretation_allowed: 0
```

High-limit complete H16 pair2:

```text
status: COMPLETED
elapsed_seconds: 55.696
joint_node_rows: 173279
joint_edge_rows: 1069650
artifact_completeness_statuses: complete
audit status counts: PASS 3
reconstruction_audit_clean_pass: 1
reconstruction_audit_interpretable_pass: 1
medium_sweep_interpretation_allowed: 1
output: about 63.3 MB
```

Read:

```text
The coupled infrastructure is now hardened enough for a medium infrastructure
sweep. The next engineering risk is output growth: before many-pair H64/H128,
add sharded coupled raw topology or run explicitly bounded high-limit complete
designs.
```

### Future Field Atlas Coupled Probe

Implemented and smoked the first clean coupled Future Field Atlas infrastructure
layer.

Runtime/public term:

```text
coupled
```

Do not use `comField` for this branch.

Retained note:

- `docs/research_notes/validation_results/future_field_atlas_coupled_probe_result.md`

Implemented shape:

```text
product_baseline:
  cartesian product of A and B selected successors

coupled:
  joint energy rank-prefix selection over product successors

joint_transition_energy:
  A_candidate_energy
  + B_candidate_energy
  + coupling_strength * abs(A_rank_offset_from_boundary - B_rank_offset_from_boundary)
```

Smokes:

```text
H8:
  status: COMPLETED
  elapsed_seconds: 0.331
  joint_node_rows: 1169
  joint_edge_rows: 6588
  output: about 0.40 MB
  reconstruction_audit_passed: 1
  artifact_completeness_statuses: complete

H16:
  status: COMPLETED
  elapsed_seconds: 0.746
  joint_node_rows: 2749
  joint_edge_rows: 16908
  output: about 1.00 MB
  reconstruction_audit_passed: 1
  artifact_completeness_statuses: complete

H32:
  status: COMPLETED
  elapsed_seconds: 1.566
  joint_node_rows: 5909
  joint_edge_rows: 37548
  output: about 2.20 MB
  reconstruction_audit_passed: 1
  artifact_completeness_statuses: complete

H16 pair2 parallel:
  status: COMPLETED
  elapsed_seconds: 15.834
  workers: 2
  joint_node_rows: 51924
  joint_edge_rows: 202406
  output: about 12.50 MB
  reconstruction_audit_passed: 1
  artifact_completeness_statuses: complete,truncated_noninterpretable
```

Final H32 readout:

```text
product_joint_support_count: 100
coupled_joint_support_count: 97
joint_support_residual_fraction: 0.03
A_marginal_retention_fraction: 1.0
B_marginal_retention_fraction: 1.0
internal_cap_events: 0
```

Completeness repair:

```text
The two-pair parallel smoke showed that marginal-retention and joint-residual
rows must inherit raw topology completeness. The runner now marks coupled
derived comparison rows with feature_status and reconstruction audits skip
truncated_noninterpretable rows instead of failing or treating them as complete.
```

Read:

```text
Go for a medium coupled infrastructure sweep. Not yet a coupled science run.
Before scaling pair count, either add sharded coupled raw topology or decide
that truncated_noninterpretable horizons are acceptable as operational probes.
First medium pass should vary pair count, coupling strength, and joint effective
out-degree while keeping product baselines, feature_status, and reconstruction
audits mandatory.
```

### Future Field Atlas Transport Mode Timing

Added explicit transport and residual modes:

```text
--transport-output-mode adjacent_only | selected_multiscale | full
--composition-residual-mode none | selected | full
```

Default mode is now:

```text
transport_output_mode: selected_multiscale
composition_residual_mode: selected
```

Retained note:

- `docs/research_notes/validation_results/future_field_atlas_transport_mode_timing_result.md`

Validation:

```text
H8 default selected smoke: COMPLETED, reconstruction_audit_passed: 1
H8 adjacent-only smoke: COMPLETED, reconstruction_audit_passed: 1
```

H128 timing comparison on the same 32-scan shape:

```text
selected_multiscale + selected:
  elapsed_seconds: 119.445
  scan phase completed by: 5.643s
  multiscale_transport_pair_count: 21
  composition_residual_triple_count: 10
  total output: about 66.6 MB
  multiscale_transport_matrices: 75.394s
  composition_residuals: 6.091s

adjacent_only + none:
  elapsed_seconds: 33.948
  scan phase completed by: 5.565s
  multiscale_transport_pair_count: 0
  composition_residual_triple_count: 0
  total output: about 64.8 MB
  multiscale_transport_matrices: 0.000s
  composition_residuals: 0.000s
```

Read:

```text
The next runtime lever is transport materialization, not CSV writing.
Adjacent-only mode is the right fast calibration mode. Selected multiscale is
the right default for medium pre-coupling checks. Full/full should be reserved
for targeted audits.
```

Local data policy update:

```text
Keep recent calibration outputs for a short review grace period; clean older
unpromoted run directories by age. Do not immediately purge every calibration
run unless storage pressure requires it.
```

### Future Field Atlas Write-Out Path Repair

Implemented a minimal write-out repair after the H128 calibration pass exposed
post-scan finalization as the dominant wall-clock cost.

Retained note:

- `docs/research_notes/validation_results/future_field_atlas_writeout_path_repair_note.md`

Repair contents:

```text
gzip_compresslevel default: 1
raw_topology_output_mode default: sharded
artifact write path: parallelized across independent artifacts
finalization timings: recorded in status, manifest, and report
```

Default raw topology physical layout:

```text
frontier_nodes_by_horizon_shard_manifest.csv.gz
frontier_nodes_by_horizon_shards/part-*.csv.gz
frontier_edges_by_step_shard_manifest.csv.gz
frontier_edges_by_step_shards/part-*.csv.gz
```

Verification:

```text
tiny H4 traceability smoke: COMPLETED
scans_completed: 8 / 8
reconstruction_audit_passed: 1
artifact_completeness_statuses: complete
manifest listed physical shard files with row counts
```

Local data disposal:

```text
Deleted bulky local calibration/writeout directories after verification.
No generated raw topology from these calibration iterations was retained.
Docs and code changes are the retained record.
```

### Future Field Atlas H128 Calibration Pass

Ran a medium H128 Future Field Atlas calibration pass using the default gzip
CSV storage mode.

Retained note:

- `docs/research_notes/validation_results/future_field_atlas_h128_calibration_pass_result.md`

Local validation output:

- `results/future_field_atlas/20260601_phase0_1_calibration_h128_g4_fresh2_start2/`

Run shape:

```text
status: COMPLETED
workers: 18
conditions: 64
scans_completed: 128 / 128
errors: 0
elapsed_seconds: 1762.763
frontier_node_rows: 564213
frontier_edge_rows: 7767333
csv_output_mode: gzip
reconstruction_audit_passed: 1
artifact_completeness_statuses: complete
```

Output manageability:

```text
total output size: about 172.7 MB
frontier_edges_by_step.csv.gz: about 143.6 MB
raw_transport_matrices_multiscale.npz: about 14.4 MB
frontier_nodes_by_horizon.csv.gz: about 10.2 MB
```

Key operational read:

```text
worker scan phase completed all 128 scans by elapsed_seconds: 18.872
final status completed at elapsed_seconds: 1762.763
post-scan finalization time: about 1743.9 seconds
```

Interpretation:

```text
The medium calibration pass is clean: all reconstruction audits passed and all
topology-derived artifacts are complete. The scaling bottleneck is no longer
the scan workers; it is post-scan artifact construction, matrix construction,
compression, and final manifest/report writing. Before much larger atlas runs,
repair finalization with phase timing, chunked/streamed raw topology, optional
deferred matrix construction, or a columnar backend.
```

### Future Field Atlas Default-Gzip Compression Smoke

Patched the atlas runner so primary CSV artifacts default to gzip output:

```text
--csv-output-mode gzip
```

The runner still supports:

```text
--csv-output-mode plain
--csv-output-mode both
```

Retained note:

- `docs/research_notes/validation_results/future_field_atlas_default_gzip_compression_smoke.md`

Local validation output:

- `results/future_field_atlas/20260601_phase0_1_default_gzip_h32_rerun/`

Run shape:

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

Compression read:

```text
compact plain H32 output: about 59.7 MB
default-gzip H32 output: about 3.1 MB
reduction: about 19x
manual selected-CSV gzip ratio: about 23.5x
```

Interpretation:

```text
Gzip is now the default storage posture for atlas CSV artifacts. It is lossless
and preserves reconstruction audits while cutting the compact H32 footprint by
roughly one order of magnitude again. Larger atlas runs may still need a
columnar backend, but gzip is the correct default for current smoke and medium
scale work.
```

### Future Field Atlas Compact Manageability H64 Run

Patched the atlas raw topology output to remove repeated formal spec metadata
from high-volume node and edge rows. The normalized output now keeps formal
identity in:

- `formal_spec_manifest.csv`
- `condition_identity_manifest.csv`
- `scan_manifest.csv`

Retained note:

- `docs/research_notes/validation_results/future_field_atlas_compact_manageability_h64_result.md`

Local validation output:

- `results/future_field_atlas/20260601_phase0_1_compact_manageability_h64_g4_start2/`

Run shape:

```text
status: COMPLETED
workers: 18
conditions: 32
scans_completed: 64 / 64
elapsed_seconds: 314.261
frontier_node_rows: 264567
frontier_edge_rows: 1866167
reconstruction_audit_passed: 1
artifact_completeness_statuses: complete
```

Manageability read:

```text
compact H32 output: about 59.7 MB
prior publication-audit H32 output: about 370.7 MB
compact H64 manageability output: about 907.2 MB
dominant remaining file: frontier_edges_by_step.csv at about 758.0 MB
```

Interpretation:

```text
Normalized manifests reduce redundant raw topology output by about 6x at H32
without breaking reconstruction audits. This is good enough for the next
pre-coupling scale step, but long/large atlas runs should add a lossless
columnar or compressed raw topology artifact before scaling much further.
```

### Future Field Atlas Phase 0/1 Publication-Schema Audit Smoke

Implemented the first clean Future Field Atlas package as an instrumentation
reset. The new package separates substrate generation, frontier scanning,
geometry mapping, transport matrix construction, and operator-geometry analysis.
The scanner records raw topology and does not classify responses.

After audit, tore down the remaining compatibility adapter surface and then
demoted rank-core recovery from the center of the instrument into a calibration
fixture. Condition identity is mathematical: `StateSpaceSpec`,
`TransformationLawSpec`, `SelectionOperatorSpec`, `ObservableSpec`, and
`FrontierScanSpec`. Historical treatment-arm names live only in the Future Field
Atlas glossary. Runtime package search returns zero hits for historical
treatment-arm and response terms. Boolean recovery labels were replaced by
continuous operator and rank-boundary geometry metrics. The final audit pass
added formal spec manifests, condition-identity manifests,
artifact-completeness summaries, and reconstruction audits proving that the
primary derived artifacts reconstruct from raw rows and specs.

Retained note:

- `docs/research_notes/validation_results/future_field_atlas_phase0_1_smoke_result.md`

Spec:

- `docs/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md`
- `docs/FUTURE_FIELD_ATLAS_GLOSSARY.md`

Local validation output:

- `results/future_field_atlas/20260601_phase0_1_publication_audit_h32/`

Run shape:

```text
status: COMPLETED
workers: 4
conditions: 8
scans_completed: 8 / 8
elapsed_seconds: 20.551
errors: 0
horizon_max: 32
frontier_node_rows: 30671
frontier_edge_rows: 107034
selection_operator_geometry_rows: 8
reconstruction_audit_passed: 1
artifact_completeness_statuses: complete
```

Reconstruction audit:

```text
condition_identity_traceability: PASS
frontier_profile_reconstructs_from_node_and_edge_rows: PASS
rank_boundary_geometry_reconstructs_from_edge_rows: PASS
adjacent_transport_matrices_reconstruct_from_edge_rows: PASS
selection_operator_geometry_reconstructs_from_rank_boundary_rows: PASS
```

Main read:

```text
near-zero operator rank-boundary distance:
  rank_prefix:m=3
  rank_subset:m=4:retain=1|2|3:remove=4
  rank_subset:m=5:retain=1|2|3:remove=4|5

nonzero operator rank-boundary distance:
  rank_prefix:m=4 and rank_prefix:m=5 with outside-boundary ranks present
  rank_subset:m=4:retain=2|3|4:remove=1

sampled stochastic controls:
  emitted boundary fractions but no deterministic rank-set distance
```

Interpretation:

```text
This is an instrument-build smoke, not a validation result. It supports moving
from the old response-classifier-first runner toward a raw-geometry-first atlas.
The atlas object now leads; the rank-boundary split is documented as a
calibration fixture.
```

### RFS-MB0 Hard Top-m Boundary Resolution Medium Sweep

Ran the final narrow single-frontier mechanism pass before moving to coupled
frontier interaction. The pass varied base `m` / out-degree over `3,4,5` and
compared one-edge weakest deletion, two-edge weakest deletion, random deletion,
strongest-edge deletion, and one-edge expansion.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_top_m_mechanism_audit_result.md`

Local validation output:

- `results/local_runs/20260601_top_m_boundary_resolution_medium_v2/`

Run shape:

```text
status: COMPLETED
workers: 18
jobs_completed: 20160 / 20160
elapsed_seconds: 346.340
errors: 0
matrix_count: 6655
null_replicates: 9
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
paired_baseline_missing_rows: 0
terminal_saturation_flagged_rows: 0
readiness_level: top_m_fixed_low_rank_core_loadbearing
next_action_fork: carry_shared_low_rank_core_boundary_forward
```

Main read:

```text
response-bearing:
  baseline m=3
  m=4 with one weakest selected edge removed
  m=5 with two weakest selected edges removed

stable:
  baseline m=4/m=5
  m+1 expansion
  random one-edge deletion
  random two-edge deletion
  strongest-edge deletion
```

Interpretation:

```text
The current coupling primitive should be shared low-rank successor-core /
core-fringe boundary pressure, not generic lower out-degree and not weakest-edge
deletion by itself. Stop single-frontier mechanism work unless coupled-frontier
results contradict this read.
```

### RFS-MB0 Hard Top-m Pruning Resolution Upper-Medium Sweep

Expanded the hard-top-m mechanism audit with pruning-resolution controls after
the medium sweep pointed to strict `m-1` pruning.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_top_m_mechanism_audit_result.md`

Local validation output:

- `results/local_runs/20260601_top_m_pruning_resolution_upper_medium/`
- `results/local_runs/20260601_top_m_pruning_resolution_smoke/`

Run shape:

```text
status: COMPLETED
workers: 18
jobs_completed: 38400 / 38400
elapsed_seconds: 748.307
errors: 0
matrix_count: 6600
null_replicates: 9
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
paired_baseline_missing_rows: 0
readiness_level: top_m_weakest_edge_pruning_loadbearing
next_action_fork: expand_core_fringe_boundary_pruning_controls
```

Main read:

```text
deterministic_top_m, m+1, m+2, random deletion, all-local random m-1,
near-tie jitter, and strongest-edge deletion stayed stable;
m-1 / weakest-edge deletion was response-bearing;
m-2 produced a weaker aligned-amplification echo.
```

Interpretation:

```text
The live mechanism is now weakest selected-edge pruning / core-fringe boundary
pressure, not generic lower out-degree. Random deletion at the same effective
degree stayed stable.
```

### RFS-MB0 Hard Top-m Mechanism Medium Sweep

Implemented the hard-top-m mechanism audit branch and advanced it from tiny
smoke to a corrected medium design-group sweep after the top-m geometry audit
forked to `audit_hard_top_m_mechanism`.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_top_m_mechanism_audit_result.md`

Spec:

- `docs/RFS_MB0_TOP_M_MECHANISM_AUDIT_SPEC.md`

Local validation output:

- `results/local_runs/20260601_top_m_mechanism_medium_dg12_v2/`
- `results/local_runs/20260601_top_m_mechanism_smoke/`

Medium run shape:

```text
status: COMPLETED
workers: 18
jobs_completed: 8640 / 8640
elapsed_seconds: 213.430
errors: 0
matrix_count: 1980
null_replicates: 7
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
paired_baseline_missing_rows: 0
readiness_level: top_m_pruning_variant_response_bearing
next_action_fork: expand_strict_pruning_controls_and_inspect_deterministic_reproducibility
```

Main read:

```text
deterministic_top_m went stable on broader design groups;
top_m_m_minus_1 remained response-bearing across all tested betas and was
strongest at beta 0.10;
top_m_boundary_jitter, core/fringe randomization, and top_m_m_plus_1 stayed stable.
```

Interpretation:

```text
This is not a theory validation result. The current mechanism fork is strict
pruning / low-rank edge pressure, not deterministic top-m edge identity by
itself. The earlier deterministic-top-m positive is design-set sensitive until
reproduced or explained.
```

## 2026-05-31

### RFS-MB0 Top-m Geometry Code Tightening

Audited the top-m geometry implementation against the formal-core false
positive class `deterministic substrate artifact`.

Code tightening:

```text
top-m audit jobs now force no reversibility/no rewire post-processing;
sampler diagnostics expose the applied post-processing policy;
response tables now include sampler-family-by-invariant outputs;
paired-baseline availability is emitted by sampler/probe/flow/horizon/perturbation context;
top-m geometry readiness fails closed when required sampler families or primary invariant rows are missing;
rank-conditioned comparator is documented as a top-rank-window local sampler, not full rank-bucket MaxEnt.
```

Smoke:

```text
local output: results/local_runs/20260601_top_m_geometry_tightening_smoke/
jobs_completed: 40 / 40
errors: 0
matrix_count: 120
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
paired_baseline_availability_by_sampler_context_rows: 96
top_m_geometry_spec_incomplete: 0
readiness_level: top_m_geometry_audit_underpowered
```

### RFS-MB0 Top-m Geometry Audit

Ran the narrow sampler-geometry audit requested after the MaxEnt Phase 1
preflight.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_top_m_geometry_audit_result.md`

Local validation output:

- `results/local_runs/20260601_top_m_geometry_audit/`

Run shape:

```text
status: COMPLETED
workers: 18
jobs_completed: 2240 / 2240
elapsed_seconds: 228.005
errors: 0
matrix_count: 5600
null_replicates: 9
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
terminal_saturation_flagged_rows: 0
readiness_level: algorithmically_narrow_top_m_geometry
next_action_fork: audit_hard_top_m_mechanism
```

Main read:

```text
deterministic preservation_asymmetry top-m reproduced the symbol-histogram
response at beta 0.075, 0.10, and 0.15;
softmax/Gibbs energy sampling did not recover it;
rank-conditioned local sampling did not recover it;
MaxEnt macro-marginal sampling did not recover it.
```

Interpretation:

```text
The current preservation-asymmetry aligned response appears algorithmically
narrow to hard deterministic top-m edge selection in this audit. Do not expand
broad MaxEnt yet; audit the hard top-m mechanism next.
```

### RFS-MB0 MaxEnt Local Transition Phase 1 Preflight

Ran the first real MaxEnt comparator pass after Phase 0 plumbing.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_max_entropy_local_transition_phase1_preflight_result.md`

Local validation output:

- `results/local_runs/20260531_max_entropy_local_transition_phase1_preflight_v2/`

Run shape:

```text
status: COMPLETED
workers: 18
jobs_completed: 1280 / 1280
elapsed_seconds: 146.650
errors: 0
matrix_count: 3320
null_replicates: 9
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
terminal_saturation_flagged_rows: 0
readiness_level: deterministic_top_m_geometry_loadbearing
next_action_fork: audit_top_m_geometry_or_refine_max_entropy_sampler
```

Main read:

```text
deterministic preservation_asymmetry reproduced the symbol-histogram response;
MaxEnt local and MaxEnt macro-invariant comparators stayed stable;
the next required move was a narrow top-m geometry audit, not a broad MaxEnt
expansion.
```

### RFS-MB0 Low-Beta Preservation Sensitivity Scaleup

Ran the repaired low-beta preservation-asymmetry sensitivity scaleup.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_low_beta_preservation_sensitivity_scaleup_result.md`

Local validation output:

- `results/local_runs/20260531_low_beta_preservation_sensitivity_scaleup/`

Run shape:

```text
status: COMPLETED
workers: 18
jobs_completed: 14976 / 14976
elapsed_seconds: 4776.098
errors: 0
matrix_count: 10026
null_replicates: 9
selected_edge_overlap_by_beta_rows: 24
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
terminal_saturation_flagged_rows: 0
readiness_level: preservation_asymmetry_loadbearing
next_action_fork: expand_preservation_asymmetry_family
```

Main read:

```text
beta is wired and changes selected transition edges at 0.005;
aligned response first appears around beta 0.05;
symbol_histogram_distance remains the cleanest preservation target;
total_coordinate_mass remains live but paired-baseline limited.
```

### RFS-MB0 Asymmetry-Ladder Preservation Scaleup

Ran the preservation-focused asymmetry-ladder scaleup recommended after the
first implementation batch.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_asymmetry_ladder_preservation_scaleup_result.md`

Local validation output:

- `results/local_runs/20260531_asymmetry_ladder_preservation_scaleup/`

Run shape:

```text
status: COMPLETED
workers: 18
jobs_completed: 14976 / 14976
elapsed_seconds: 4304.994
errors: 0
matrix_count: 9846
substrate_family_variant_count: 26
null_replicates: 9
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
terminal_saturation_flagged_rows: 0
readiness_level: preservation_asymmetry_loadbearing
next_action_fork: expand_preservation_asymmetry_family
```

Compact family read:

```text
locality_only:
  aligned fraction: 0.000

directional_asymmetry:
  aligned fraction: 0.000
  rerouted rows: 37
  reopened rows: 8

preservation_asymmetry:
  aligned fraction over interpretable rows: 0.174
  aligned rows: 795
  rerouted rows: 275
  reopened rows: 395
  baseline-missing rows: 360

combined_asymmetry:
  aligned fraction: 0.000
  rerouted rows: 71
  reopened rows: 5

constraint_template_current:
  aligned fraction: 0.233
  aligned rows: 82
```

Invariant read:

```text
hamming_weight_or_nonzero_count:
  aligned fraction: 0.057
  aligned rows: 140
  baseline-missing rows: 0

symbol_histogram_distance:
  aligned fraction: 0.154
  aligned rows: 380
  rerouted rows: 262
  reopened rows: 245
  weakened rows: 75
  baseline-missing rows: 0

total_coordinate_mass:
  aligned fraction: 0.158
  aligned rows: 275
  baseline-missing rows: 360
```

Beta-ladder audit:

```text
The runner is applying beta, but the tested beta range 0.25-4.0 is mostly on a
saturated selected-edge plateau. A spot edge-overlap audit showed meaningful
changes below 0.25.
```

Interpretation:

```text
Preservation asymmetry strengthened as the live hook. The positive read no
longer depends only on total coordinate mass: symbol-composition preservation
is now the best clean all-around target because it has aligned response,
rerouting, reopening, weakening, and no baseline-missing rows.
```

Next recommendation:

```text
Run a low-beta preservation-asymmetry sensitivity pass before max-entropy:
beta values 0, 0.005, 0.01, 0.025, 0.05, 0.10, 0.15, 0.25, with selected-edge
overlap by beta and baseline availability by invariant/horizon pair.
```

### RFS-MB0 Asymmetry-Ladder First Implementation Run

Implemented the asymmetry-ladder transition-energy families and ran the first
seed-scaled design-set batch.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_asymmetry_ladder_transition_energy_result.md`

Local validation outputs:

- `results/local_runs/20260531_asymmetry_ladder_fixture_smoke/`
- `results/local_runs/20260531_asymmetry_ladder_tiny_smoke/`
- `results/local_runs/20260531_asymmetry_ladder_seed_scaled/`

Implementation change:

```text
directional_asymmetry:
  E(s,t) = d(s,t) + alpha * (A(t) - A(s)) + roughness

preservation_asymmetry:
  E(s,t) = d(s,t) + beta * |I(t) - I(s)| + roughness

combined_asymmetry:
  E(s,t) = d(s,t) + alpha * (A(t) - A(s))
         + beta * |I(t) - I(s)| + roughness
```

Run shape:

```text
status: COMPLETED
workers: 18
jobs_completed: 640 / 640
elapsed_seconds: 829.711
errors: 0
matrix_count: 3402
substrate_family_variant_count: 16
null_replicates: 7
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
terminal_saturation_flagged_rows: 0
readiness_level: preservation_asymmetry_loadbearing
next_action_fork: expand_preservation_asymmetry_family
```

Compact result:

```text
locality_only:
  aligned fraction: 0.000
  read: clean baseline in this batch

directional_asymmetry:
  aligned fraction: 0.000
  rerouted rows: 16
  read: differentiated/rerouting response without aligned amplification

preservation_asymmetry:
  aligned fraction over interpretable rows: 0.084
  aligned rows: 76
  baseline-missing rows: 72
  read: first loadbearing ladder family

combined_asymmetry:
  aligned fraction: 0.000
  rerouted rows: 55
  read: clean but not yet synergistic in the sparse tested grid
```

Interpretation:

```text
The live object is increasingly the response profile of reachable-future
transport under minimal transition-energy ingredients. Macro-invariant /
preservation asymmetry is the current strongest hook; directional and combined
families are useful for rerouting/threshold mapping but did not carry aligned
response in this pass.
```

### RFS-MB0 Baseline Symmetry Guard Patch

Patched the response summaries before running the asymmetry-ladder spec.

Reason:

```text
The macro-invariant due-diligence run showed that total coordinate mass still
has paired-baseline availability limits in constrained-window flow. Those rows
must remain auditable, but must not depress or dominate interpretable response
summaries.
```

Implementation change:

```text
response_by_* summaries now compute dominant_response_class and
aligned_amplification_fraction over interpretable response rows only.

measurement-limit rows remain counted separately as:
  measurement_limit_response_rows
  transport_baseline_missing_count
  transport_insufficient_common_items_count
  transport_resolution_mismatch_count

aligned_amplification_fraction_all_rows remains available as an audit value.
```

Spec update:

- `docs/RFS_MB0_ASYMMETRY_LADDER_TRANSITION_ENERGY_SUBSTRATE_SPEC.md`

Local validation outputs:

- `results/local_runs/20260531_baseline_guard_fixture_smoke/`
- `results/local_runs/20260531_baseline_guard_macro_invariant_tiny/`

Tiny targeted check:

```text
status: COMPLETED
workers: 18
jobs_completed: 84 / 84
elapsed_seconds: 79.607
errors: 0
matrix_count: 827
null_replicates: 7
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
```

Response summary after guard:

```text
nonzero-support invariant:
  response_rows: 264
  interpretable_rows: 264
  measurement_limit_rows: 0
  aligned_fraction_interpretable: 0.0265
  aligned_fraction_all_rows: 0.0265

symbol-composition invariant:
  response_rows: 248
  interpretable_rows: 234
  measurement_limit_rows: 14
  aligned_fraction_interpretable: 0.2137
  aligned_fraction_all_rows: 0.2016

total coordinate-mass invariant:
  response_rows: 206
  interpretable_rows: 156
  measurement_limit_rows: 50
  aligned_fraction_interpretable: 0.2692
  aligned_fraction_all_rows: 0.2039
```

Row-level response classes:

```text
computed transport_stable: 425
computed transport_amplified_aligned: 99
computed transport_rerouted: 65
baseline_missing transport_baseline_missing: 64
computed transport_reopens: 56
computed transport_weakened: 9
transport_resolution_mismatch: 0
transport_insufficient_common_items: 0
```

Interpretation:

```text
Baseline-missing rows are now measurement-limit counts, not response evidence.
The asymmetry-ladder spec should proceed only with this guard active.
```

### RFS-MB0 Macro-Invariant Due-Diligence Run

Ran the guarded Option A due-diligence follow-up before moving to the
max-entropy local transition preflight.

Terminology update:

```text
public-facing:
  macro-invariant transition substrate

theory-facing:
  asymmetry-constrained transition energy

raw implementation/output compatibility:
  budget_conservation
  budget_kind
  budget_weight
  budget_delta
```

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_macro_invariant_due_diligence_result.md`

Local validation output:

- `results/local_runs/20260531_option_a_budget_due_diligence_guarded/`

Implementation repair:

```text
Response taxonomy now separates transport_baseline_missing from true
transport_resolution_mismatch and insufficient common row/column support.
The runner also accepts macro_invariant / asymmetry_constrained aliases while
canonicalizing to the retained implementation family name budget_conservation.
```

Run shape:

```text
status: COMPLETED
workers: 18
jobs_completed: 4620 / 4620
elapsed_seconds: 1658.146
errors: 0
matrix_count: 6720
substrate_family_variant_count: 15
null_replicates: 13
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
terminal_saturation_flagged_rows: 0
readiness_level: budget_conservation_loadbearing
next_action_fork: expand_budget_conservation_family
```

Translated read:

```text
readiness_level:
  macro_invariant_loadbearing

next action:
  proceed to Option B unless doing a very narrow total-coordinate-mass
  baseline-availability repair
```

Compact result:

```text
all variants:
  coverage_mean: 1.0
  coverage_min: 1.0

nonzero-support invariant:
  aligned fraction: 0.061
  matched-null pass: 0.985-1.000
  clean low-signal comparator

symbol-composition invariant:
  aligned fraction: 0.106
  matched-null pass: 0.780-0.811
  best response diversity with no baseline-missing rows

total coordinate-mass invariant:
  aligned fraction: 0.203 overall, 0.273 among interpretable rows
  matched-null pass: 0.795-0.833
  strongest aligned response, still limited by paired-baseline availability
```

Interpretation:

```text
Option A is sufficiently resolved for project direction. Macro-invariant /
asymmetry-constrained transition energy is loadbearing under the current
instrument, but the next stronger substrate test is Option B: a max-entropy
local transition ensemble using explicit macro constraints rather than named
symbolic law templates.
```

### RFS-MB0 Option A Macro-Invariant Coverage Small Smoke

Ran the small Option A follow-up from
`docs/research_notes/omega_theory/transition_energy_substrate_atlas.md`.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_option_a_budget_coverage_small_result.md`

Local validation output:

- `results/local_runs/20260531_option_a_budget_coverage_small/`

Run shape:

```text
status: COMPLETED
workers: 18
jobs_completed: 396 / 396
elapsed_seconds: 463.18
errors: 0
matrix_count: 3915
substrate_family_variant_count: 9
null_replicates: 13
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
readiness_level: substrate_characterization_underpowered
next_action_fork: continue_transition_energy_characterization
```

Compact read:

```text
budget coverage repair:
  succeeded mechanically

hamming_weight_or_nonzero_count:
  cleanest support and matched-null behavior;
  weak aligned-amplification fraction

symbol_histogram_distance:
  near-complete matrix coverage;
  moderate aligned response and response diversity;
  best current middle path

total_coordinate_mass:
  strongest aligned-amplification fraction;
  still limited by missing late-horizon constrained-window baseline matrices
```

Interpretation:

```text
The earlier macro-invariant coverage caveat is mostly repaired. The
remaining total-coordinate-mass caveat is an instrumentation/baseline-availability
issue, not simple retained-matrix loss. Next repair should enforce or gate
paired baseline availability before using late-horizon constrained-window
response rows for total-coordinate-mass ranking.
```

### RFS-MB0 Transition-Energy Substrate Characterization Larger Smoke

Pulled and implemented `docs/RFS_MB0_TRANSITION_ENERGY_SUBSTRATE_CHARACTERIZATION_RUN_SPEC.md`.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_transition_energy_substrate_characterization_result.md`

Local validation outputs:

- `results/local_runs/20260531_transition_energy_characterization_fixture_smoke/`
- `results/local_runs/20260531_transition_energy_characterization_preflight/`
- `results/local_runs/20260531_transition_energy_characterization_larger_smoke/`

Implementation repair:

```text
Response baselines are now keyed by substrate_family + substrate_variant +
probe + flow + horizon pair. This prevents multi-family perturbation matrices
from being compared against a baseline from a different substrate family or
variant.
```

Run shape:

```text
status: COMPLETED
workers: 18
jobs_completed: 7744 / 7744
elapsed_seconds: 1378.371
errors: 0
matrix_count: 10324
substrate_family_variant_count: 22
null_replicates: 13
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: 8 / 8
decision: locality_only_baseline_confirmed
next_action_fork: write_transition_energy_substrate_atlas_note
```

Compact read:

```text
locality_only:
  no aligned amplification across low/current/high roughness variants;
  keep as bounded-locality baseline

smooth_random_potential:
  response-bearing but not aligned-amplifying in the tested smoothness/beta grid;
  mostly stable with rerouted/reopened rows

macro-invariant / asymmetry-constrained transition energy:
  aligned response present;
  total-coordinate-mass strongest but coverage-limited;
  hamming-weight/nonzero variants have cleaner matched-null behavior

constraint_template_current:
  still positive comparator, but not unique
```

Interpretation:

```text
This is a substrate-response atlas result for the instrument, not a theory
validation gate. It supports writing a transition-energy substrate atlas note
and deciding between macro-invariant coverage repair and a more principled
max-entropy-local-transition substrate.
```

### RFS-MB0 Substrate Untethering Transition-Energy Larger Smoke

Ran the larger transition-energy substrate untethering smoke from
`docs/RFS_MB0_SUBSTRATE_UNTETHERING_TRANSITION_ENERGY_SWEEP_SPEC.md` after the
initial tiny implementation smoke and decision-guard audit.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_substrate_untethering_transition_energy_sweep_result.md`

Local validation output:

- `results/local_runs/20260531_substrate_untethering_larger_smoke_powered_v2/`

Run shape:

```text
status: COMPLETED
workers: 18
jobs_completed: 896 / 896
elapsed_seconds: 142.856
errors: 0
matrix_count: 1160
null_replicates: 13
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: 8 / 8
decision: horizon_transport_generalizes_beyond_constraint_vocabulary
next_action_fork: continue_transition_energy_substrates
```

Substrate families:

```text
constraint_template_current
locality_only
smooth_random_potential
macro-invariant / asymmetry-constrained transition energy
```

Compact result:

```text
macro-invariant / asymmetry-constrained transition energy: 42 aligned-amplification rows, modal stable, high-viscosity aligned amplifier
smooth_random_potential: 19 aligned-amplification rows, modal rerouted
constraint_template_current: 17 aligned-amplification rows, modal rerouted
locality_only: 0 aligned-amplification rows, modal reopens
```

Interpretation:

```text
This is a powered instrument smoke, not a theory validation gate. It shows
horizon transport remains measurable outside the original hand-built
constraint-template vocabulary, with different response profiles across
transition-energy families. It does not establish Omega, agency, value,
identity, holdout readiness, graph-channel causality, or candidate promotion.
```

Next direction:

```text
Continue transition-energy substrate untethering with grammar-neutral probes,
then transition toward a max-entropy local transition ensemble once capacity
and matched-null behavior are stable.
```

### RFS-MB0 Horizon-Transport Response Surface H128 Scaleup

Implemented the H128 response-surface instrumentation requested by
`docs/RFS_MB0_HORIZON_TRANSPORT_RESPONSE_SURFACE_H128_SCALEUP_SPEC.md`.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_horizon_transport_response_surface_h128_scaleup_result.md`

Local validation outputs:

- `results/local_runs/20260531_h128_response_fixture_smoke_v4_status_field/`
- `results/local_runs/20260531_h128_regenerated_boundary_selection_top64/`
- `results/local_runs/20260531_h128_regenerated_detector_instrumentation_top28/`
- `results/local_runs/20260531_h128_response_surface_tiny_smoke/`
- `results/local_runs/20260531_h128_response_surface_regenerated_scaleup/`

Instrumentation added:

```text
H128 horizon-pair support
transport_amplified_aligned response class
expanded response fixtures for amplified/weakened/rerouted/reopened classes
response flags output
response class by strength/horizon output
horizon response threshold table
terminal saturation diagnostics
H128-specific run/status/report filenames
```

Fixture status:

```text
8 / 8 passed
```

Scoped input regeneration:

```text
focused groups selected: 28
corrected groups: 28
upstream focused recurrence jobs: 1344 / 1344
upstream errors: 0
```

H128 scaleup:

```text
status: COMPLETED
workers: 18
jobs_completed: 11520 / 11520
elapsed_seconds: 2196.206
errors: 0
matrix_count: 660
null_replicates: 15
matched marginal detector-null separation: passed, 3/3 families
terminal_saturation_flagged_rows: 0 / 660
```

Response read:

```text
transport_stable: 235
transport_amplified_aligned: 381
```

Interpretation:

```text
H128 exposes a clean horizon-dependent amplification surface. Short horizons
remain stable; middle/deep horizons become amplified-aligned; the first
nonstable horizon moves earlier as perturbation strength rises. The full
scaleup did not produce weakened, rerouted, reopened, collapsed, or
control-equivalent empirical rows. The next action fork is
write_horizon_transport_theory_note, still without holdout, graph-channel
diagnostics, candidate promotion, or Omega/agency/value claims.
```

## 2026-05-30

### RFS-MB0 Horizon-Transport Response-Resolution Scaleup

Audited the horizon-transport runner, repaired small instrumentation issues,
and ran two committed-input design-set scaleups for response-profile
resolution.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_horizon_transport_response_resolution_scaleup_result.md`

Local validation outputs:

- `results/local_runs/20260531_horizon_transport_response_resolution_scaleup_v2/`
- `results/local_runs/20260531_horizon_transport_response_ladder_p015_p02/`

Code audit repairs:

```text
Windows SIGBREAK handler added
future-level worker exceptions now count affected jobs with errors
cancelled job accounting now counts jobs, not batches
pending_jobs_remaining now updates during progress checkpoints
response rows now include actual_control_name, mechanism_control_strength, horizon_pair
response_flags added
response classifier now checks collapse/weakening/reopening before stable
```

Fixture contract after repair:

```text
4 / 4 passed
```

Primary scaleup:

```text
status: COMPLETED
workers: 18
jobs_completed: 1008 / 1008
elapsed_seconds: 58.420
errors: 0
matrix_count: 196
null_replicates: 9
matched marginal detector-null separation: passed, 3/3 families
response classes:
  transport_stable: 144
  transport_control_equivalent: 24
```

Focused p0.015/p0.02 ladder:

```text
status: COMPLETED
workers: 18
jobs_completed: 720 / 720
elapsed_seconds: 48.371
errors: 0
matrix_count: 140
matched marginal detector-null separation: passed, 3/3 families
response classes:
  transport_stable: 62
  transport_control_equivalent: 50
```

Interpretation:

```text
Matched-marginal-separated horizon transport persists at larger design-set
scale. Response profiles are no longer uniformly stable: stronger nonlethal
p0.015/p0.02 perturbations produce high-alignment mass-growth departures,
especially across 8->16, 16->24, and 24->32. The run still did not produce
transport_weakened, transport_rerouted, transport_reopens, or
transport_collapses, so the next step is response-profile fixture expansion and
compact reporting, not holdout, graph-channel diagnostics, candidate promotion,
or Omega/agency/value claims.
```

### RFS-MB0 Horizon-Transport Expansion Smoke

Implemented expansion-smoke reporting for the horizon-transport runner and ran
the proper desktop-shape smoke requested by
`docs/RFS_MB0_HORIZON_TRANSPORT_EXPANSION_SMOKE_SPEC.md`.

Retained spec and note:

- `docs/RFS_MB0_HORIZON_TRANSPORT_EXPANSION_SMOKE_SPEC.md`
- `docs/research_notes/validation_results/rfs_mb0_horizon_transport_expansion_smoke_result.md`

Local validation output:

- `results/local_runs/20260530_horizon_transport_expansion_smoke_desktop_scale_192_inputs/`

Local generated CSV/JSON outputs are not committed.

Run-shape note:

```text
The committed default focused selection currently yields one runnable group and
only a 60-job expanded local smoke. The proper desktop-shape smoke therefore
used the local rebuildable 192-input bundle to exercise 3 design groups.
```

Desktop-shape smoke:

```text
status: COMPLETED
git_commit: a988989
workers: 7
jobs_completed: 180 / 180
elapsed_seconds: 15.293
errors: 0
matrix_count: 140
detector_null_rows: 672
matched_marginal_summary_rows: 84
perturbation_response_rows: 112
```

Gate read:

```text
matrix coverage: passed, observed 1.0
structure detector-null separation: passed
null replicate power: passed, null_replicates 7
matched marginal detector-null separation: passed, 3/3 families
fixture contract: not required in empirical expansion run
```

Context/response read:

```text
both required probes: matched_marginal_separates
both required flow modes: matched_marginal_separates
all 7 emitted horizon pairs: matched_marginal_separates
response classes: transport_stable 112 / 112
```

Decision:

```text
readiness_level: ready_for_horizon_transport_scaleup
next_action_fork: expand_horizon_transport_scale
```

Interpretation:

```text
This is a clean instrument-scaleup smoke. Horizon transport remained covered,
matched marginal detector nulls separated, and perturbation responses were
interpretable but uniformly stable. It does not authorize holdout, graph
perturbation, direct channel diagnostics, candidate promotion, or
Omega/agency/value claims.
```

### RFS-MB0 Horizon-Transport Matched Null and Fixture Repair

Implemented the small repair recommended before any larger horizon-transport
smoke. The runner now includes row/column/bimarginal matched detector nulls,
adds `marginal_residual_fraction`, and supports a fixture-only smoke mode for
known transport-association, marginal-fakeout, corridor, and trap cases.

Retained spec and note:

- `docs/RFS_MB0_HORIZON_TRANSPORT_MATCHED_NULL_AND_FIXTURE_SMOKE_SPEC.md`
- `docs/research_notes/validation_results/rfs_mb0_horizon_transport_matched_null_fixture_smoke_result.md`

Local validation outputs:

- `results/local_runs/20260530_horizon_transport_matched_null_fixture_smoke/`
- `results/local_runs/20260530_horizon_transport_matched_null_empirical_tiny_smoke/`
- `results/local_runs/20260530_horizon_transport_matched_null_fixture_underpowered_guard/`

Local outputs are generated CSV/JSON artifacts and are not committed.

Fixture smoke:

```text
status: COMPLETED
elapsed_seconds: 0.904
matrix_count: 6
detector_null_rows: 96
fixture_result_rows: 4
perturbation_response_rows: 2
errors: 0
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract_passed: 1
fixture contract: 4 / 4 passed
readiness_level: fixture_contract_passed
next_action_fork: run_empirical_matched_null_plumbing_smoke
```

Tiny empirical plumbing smoke:

```text
status: COMPLETED
elapsed_seconds: 0.936
jobs_completed: 2
errors: 0
matrix_count: 28
detector_null_rows: 336
perturbation_response_rows: 14
matched_marginal_detector_null_gate_passed: 1
readiness_level: ready_for_horizon_transport_smoke_expansion
```

Underpowered guard:

```text
null_replicates: 2
detector_null_gate_passed: 0
detector_null_replicate_powered: 0
matched_marginal_detector_null_gate_passed: 0
readiness_level: not_ready_repair_required
blocking_reason: detector_null_replicates_underpowered
```

Decision:

```text
Matched-null and fixture repair is complete enough for a slightly larger
horizon-transport smoke. This remains instrumentation readiness only: no graph
perturbation, no direct-channel claim, no candidate promotion, and no
Omega/agency/value claim.
```

### RFS-MB0 Horizon-Transport Spectral Response Repair

Implemented the first horizon-transport spectral response repair instrument.
This is a conceptual reorientation rather than a large theoretical pivot:
directional `horizon_transport` matrices are built from existing
frontier-transform transition rows, using SVD, with detector null controls kept
separate from candidate perturbation-response profiles.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_horizon_transport_spectral_response_repair_result.md`

Local validation outputs:

- `results/local_runs/20260530_horizon_transport_repair_contract_smoke_v4_underpowered/`
- `results/local_runs/20260530_horizon_transport_repair_contract_smoke_v5_powered/`

Local outputs are generated CSV/JSON artifacts and are not committed.

Repair validation:

```text
underpowered-null contract:
  jobs_completed: 10
  errors: 0
  matrix_count: 140
  manifest: 21 / 21 present
  null_replicates: 2
  readiness_level: not_ready_repair_required
  next_action_fork: repair_transport_null_controls
  blocking_reason: detector_null_replicates_underpowered

powered contract:
  jobs_completed: 10
  errors: 0
  matrix_count: 140
  detector_null_rows: 252
  perturbation_response_rows: 112
  manifest: 21 / 21 present
  null_replicates: 3
  readiness_level: ready_for_horizon_transport_smoke_expansion
  next_action_fork: expand_horizon_transport_smoke
```

Perturbation response classes in the powered contract:

```text
transport_stable: 109
transport_control_equivalent: 3
```

Decision:

```text
Small repairs validated. The next empirical step can be a slightly larger
horizon-transport smoke, still without graph perturbation or candidate claims.
```

### RFS-MB0 Laptop Spectral Subspace Control Repair Sweeps

Ran the new spectral subspace control repair smoke as a laptop-safe targeted
sweep. This was an instrument-building pass: the goal was to widen the aperture
on where/how the controls fail, not to rescue the data into a favorable claim.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_laptop_spectral_subspace_control_repair_smoke_result.md`

Local outputs:

- `results/local_runs/20260530_laptop_spectral_subspace_control_repair_sweeps_v2/`

Local outputs are generated CSV/JSON artifacts and are not committed.

Sweep status:

```text
status: COMPLETED
elapsed_seconds: 39.009
cases_completed: 9 / 9
cases_failed: 0
errors: 0
manifest: 20 / 20 present
```

Aggregate read:

```text
decision_class: not_ready_repair_required
next_action_fork: repair_shuffle_controls
structure_shuffle_matrix_pass_fraction: 0.3925
structure_shuffle_catastrophic_fraction: 0.51
subspace_above_control_fraction: 0.53
```

Most important instrumentation result:

```text
Scalar structure statistics mostly failed:
  positive_spectral_mass, effective_rank, participation_ratio

Baseline-alignment separated almost everywhere:
  top_k_subspace_alignment_to_baseline

Interpretation:
  statistic mismatch / over-permissive alignment statistic, not a pass.
```

Distributedness v2:

```text
control_equivalent: 28
distributed: 8
diffuse_noise_like: 8
cluster_local: 5
item_local: 1
```

Decision:

```text
Do not run graph perturbation or subspace ablation yet. Repair the
shuffle/statistic instrument so baseline-alignment cannot override failed
structure-destroying scalar controls.
```

### RFS-MB0 Laptop Spectral Triage/Subspace Diagnostic Repair

Tightened the laptop spectral control/mapping smoke per external audit comments.
The runner now distinguishes label-interpretation controls from required
structure-destroying shuffles, emits matrix-level shuffle-failure anatomy,
reports subspace distributedness, compares transfer against subspace controls,
and writes an explicit next-action fork.

Instrument metadata:

```text
instrument_version: 0.3.0
schema_version: 2026-05-30.3
```

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_laptop_spectral_control_mapping_smoke_result.md`

Local validation outputs:

- `results/local_runs/20260530_laptop_spectral_triage_contract_smoke_v2/`
- `results/local_runs/20260530_laptop_spectral_triage_missing_source_gate/`

Local outputs remain generated artifacts and are not committed.

Contract smoke status:

```text
status: COMPLETED
jobs_completed: 6 / 6
errors: 0
manifest: 44 / 44 present
spectral_shuffle_control_status: spectral_shuffle_controls_control_equivalent
blocking_reason: structure_shuffle_controls_not_passed
subspace_distributedness_read: diffuse_noise_like
subspace_control_alignment_status: subspace_transfer_control_equivalent
next_action_fork: repair_shuffle_controls
```

New diagnostic row counts:

```text
laptop_spectral_shuffle_failure_anatomy.csv: 9
laptop_subspace_distributedness_diagnostic.csv: 3
laptop_subspace_control_alignment.csv: 12
laptop_spectral_next_action_fork.csv: 1
```

Graceful exit guard:

```text
status: PARTIAL_CONTROL_SOURCE_MISSING
jobs_requested: 0
jobs_completed: 0
blocking_reason: missing_source
```

Decision:

```text
Tooling repaired and smoke-validated. Scientific next action remains
repair_shuffle_controls; do not run graph perturbation from this state.
```

### RFS-MB0 Laptop Spectral Control Mapping Diagnostic Smoke

Implemented the laptop-safe spectral control/mapping smoke wrapper and tightened
the spectral channel-prep gates:

```text
per-family shuffle pass fractions and catastrophic floors
mandatory selection/evaluation split for ablation readiness
quantitative high-loading vs matched-random ablation fields
subspace-transfer diagnostics
readiness split into spectral-control, analysis-only, tiny graph, and larger graph levels
```

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_laptop_spectral_control_mapping_smoke_result.md`

Local outputs:

- `results/local_runs/20260530_laptop_spectral_gpt_diagnostic_smoke/`
- `results/local_runs/20260530_laptop_spectral_gpt_forwarding_bundle/`
- `results/local_runs/20260530_laptop_spectral_gpt_forwarding_bundle.zip`

Local outputs are forwarding/audit artifacts only and are not committed.

Diagnostic smoke status:

```text
status: COMPLETED
elapsed_seconds: 13.527
workers: 7
jobs_completed: 24 / 24
contexts_accumulated: 3024
matrix_count: 54
errors: 0
control_summary_cache_status: loaded:stage_b2_control_summary_cache.pkl
shuffle_replicates_completed: 90
high_loading_items_exported: 40
item_sets_mapped: 5
ablation_jobs_completed: 35
perturbation_jobs_completed: 0
```

Gate read:

```text
G0 control_source_available: passed
G1 output_contract_passed: passed
G2 shuffle_family_thresholds: failed
G3 item_mapping_mass: passed
G4 selection_evaluation_ablation: failed
G5 tiny_perturbation_optional: not run
```

Decision:

```text
runner_contract_passed
spectral_shuffle_controls_control_equivalent
spectral_item_mapping_adequate
high_loading_ablation_random_equivalent
subspace_transfers_but_items_not_specific
tiny_channel_perturbation_not_interpretable
not_ready_repair_required

ready_for_larger_spectral_control_run: 0
ready_for_larger_analysis_only_channel_run: 0
ready_for_tiny_graph_channel_perturbation: 0
ready_for_larger_graph_channel_run: 0
```

Key readout:

```text
shuffle families:
  label_shuffle: failed, catastrophic_fail_count 3
  context_shuffle: failed, catastrophic_fail_count 1
  horizon_order_shuffle: passed

mapping:
  best_mapped_item_mass_fraction: 1.000

matched ablation:
  high_loading_delta: 0.047743807987362004
  random_delta_mean: 0.08715710311136862
  random_delta_max: 0.10902465909564239
  metric_specificity_wins: 0

subspace:
  subspace_transfer_status: subspace_transfers
  subspace_item_read: subspace_transfers_but_items_not_specific
```

Interpretation:

```text
The laptop diagnostic smoke blocks larger spectral/channel scaling. Mapping is
adequate, and a selection/evaluation subspace transfers, but item-local
high-loading ablation is random-equivalent to matched random controls. The next
repair should address the spectral-control layer and test subspace-level
diagnostics before graph perturbation.
```

Tool-tightening addendum:

```text
schema_version: 2026-05-30.2
instrument_version: 0.2.1

Added direct external-audit field names:
  matched_random_drop_fraction_std
  matched_random_drop_fraction_max
  effect_metric_count
  random_matching_quality
  replicate_count
  catastrophic_fail_flag
  mapped_realized_edge_count

Added compact forwarding outputs:
  laptop_gpt_requested_status_key_fields.csv
  laptop_mapping_status_counts.csv
  laptop_spectral_forwarding_summary.md
```

Contract checks:

```text
tiny complete-path smoke:
  status: COMPLETED
  jobs_completed: 6 / 6
  manifest_rows: 40
  missing_manifest_rows: 0

missing-source guard:
  status: PARTIAL_CONTROL_SOURCE_MISSING
  jobs_requested: 0
  compact audit files present
```

## 2026-05-29

### RFS-MB0 Stage B-2 Spectral Channel High-Loading Repair

Implemented the next repair after the channel-edge prep block:

```text
stable high-loading selection
frequency / baseline-flow matched random ablation
matrix-level stable-item-set perturbation
```

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_stage_b2_spectral_channel_high_loading_repair_result.md`

Local output:

- `results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_channel_high_loading_repair_small_smoke_v2/`

Small smoke status:

```text
status: COMPLETED
elapsed_seconds: 24.965
workers: 18
jobs_completed: 80 / 80
contexts_accumulated: 6720
matrix_count: 180
errors: 0
manifest_rows: 52
missing_manifest_rows: 0
```

Repair read:

```text
candidate_pool_rows: 2275
stable_high_loading_selected_rows: 87
stable_high_loading_matrix_count: 10
ablation_random_matching: item_count_and_baseline_flow_count_greedy
```

Decision:

```text
runner_contract_passed
spectral_shuffle_controls_passed
spectral_item_mapping_adequate
high_loading_ablation_specific
tiny_channel_perturbation_implemented
ready_for_24h_spectral_channel_run
ready_for_24h_run: 1
```

Key readout:

```text
matched ablation:
  high_loading_drop_fraction_mean: 0.05884
  matched_random_drop_fraction_mean: 0.04504

tiny perturbation:
  targeted_spectral_positive_mass_mean: 45.6983
  random_spectral_positive_mass_mean: 42.5753
  targeted_vs_random_spectral_relative_separation: 0.06834
  destructive_rows: 0
  targeted_ac_rate_mean: 0.0
  random_ac_rate_mean: 0.0
```

Interpretation:

```text
The instrument is now ready for a larger spectral channel-edge exploratory run.
This is not a scientific gate pass. Frontier-size/probe-marginal spectral
controls remain missing, and A/C syndrome rates did not move in the tiny
perturbation smoke.
```

### RFS-MB0 Stage B-2 Spectral Channel-Edge Smoke Repair Prep

Implemented the repair-prep layer requested by
`docs/RFS_MB0_STAGE_B2_SPECTRAL_CHANNEL_EDGE_SMOKE_REPAIR_PREP_SPEC.md`.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_stage_b2_spectral_channel_edge_smoke_repair_prep_result.md`

Local outputs:

- `results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_channel_prep_contract_smoke_v5/`
- `results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_channel_prep_small_smoke_v2/`

Implementation changes:

```text
prep output contract files: added
label/context/horizon shuffle controls: added
high-loading item export: added
item-to-edge mapping export: added
analysis-only high-loading ablation: added
tiny targeted-vs-random perturbation plumbing: added
frontier-size/probe-marginal spectral controls: still not implemented
```

Small smoke status:

```text
status: COMPLETED
elapsed_seconds: 10.059
workers: 18
jobs_completed: 80 / 80
contexts_accumulated: 6720
matrix_count: 180
errors: 0
manifest_rows: 51
missing_manifest_rows: 0
```

Decision:

```text
runner_contract_passed
spectral_shuffle_controls_passed
spectral_item_mapping_adequate
high_loading_ablation_random_equivalent
tiny_channel_perturbation_not_interpretable
not_ready_repair_required
ready_for_24h_run: 0
```

Interpretation:

```text
The instrument is tighter and the data paths work, but the 24h spectral
channel-edge run is blocked. High-loading item ablation became
random-equivalent in the broader small smoke: high-loading removal changed
positive spectral mass less than matched random removal on average
(`0.1073` vs `0.1261` drop fraction).
```

Next recommendation:

```text
Repair high-loading selection before scaling: require replicate-stable,
cross-shuffle-surviving, cross-seed recurrent high-loading items and compare
against frequency/degree/baseline-flow matched item sets.
```

### RFS-MB0 Stage B-2 Spectral Future-Field Geometry Smoke

Implemented and smoked the optional Stage B-2 spectral future-field geometry
branch requested by
`docs/RFS_MB0_STAGE_B2_SPECTRAL_FUTURE_FIELD_GEOMETRY_SMOKE_SPEC.md`.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_stage_b2_spectral_future_field_geometry_smoke_result.md`

Local outputs:

- `results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_contract_smoke/`
- `results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_small_smoke_v2/`

Implementation:

```text
new runner: omega/rfs_mb0_future_landscape/run_stage_b2_spectral_future_field_geometry_smoke.py
matrix families: cofrontier, coflow
normalization: bounded independence residual
signal-aware partial finalization: enabled
direct Stage B-2 controls: enabled
full shuffled/matched spectral controls: not implemented yet
```

Small desktop smoke:

```text
status: COMPLETED
elapsed_seconds: 15.473
workers: 18
jobs_completed: 240 / 240
contexts_accumulated: 30240
matrix_count: 180
spectral_decompositions_completed: 180
matrix_coverage_insufficient_count: 0
errors: 0
decision_class: spectral_future_geometry_present
branch_recommendation: recommend_channel_edge_sensitivity_with_spectral_guidance
```

Claim boundary:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
control_comparison_scope: direct_stage_b2_controls_only
label/context/horizon/frontier-size/probe-marginal spectral controls: not completed
```

Interpretation:

```text
The smoke found nonblank, well-covered spectral structure in future-signature
co-occurrence and transition-flow matrices. The strongest direct-control
effects were coflow middle-horizon positive-mass deltas under low-probability
edge/topology perturbations, especially asymmetric edge flips.
```

Caveat:

```text
This is a direct-control spectral audition only. It does not satisfy the full
spectral migration criteria and should not be read as Omega, agency, identity,
value, or holdout evidence.
```

Next recommendation:

```text
Use spectral high-loading structures as exploratory guidance for the
channel-edge sensitivity branch, or repair the spectral runner with shuffled
and matched controls before any stronger spectral-gauge interpretation.
```

## 2026-05-28

### RFS-MB0 Stage B-2 Exploratory Iteration Pass

Implemented the Stage B-2 long-run I/O path and completed the exploratory
iteration pass requested by `docs/RFS_MB0_STAGE_B2_EXPLORATORY_ITERATION_PASS_SPEC.md`.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_stage_b2_exploratory_iteration_pass_result.md`

Local outputs:

- `results/rfs_mb0_relation_atlas/20260528_stage_b2_existing_output_triage/`
- `results/rfs_mb0_relation_atlas/20260528_stage_b2_optimized_count_contract_smoke_notrack/`
- `results/rfs_mb0_relation_atlas/20260528_stage_b2_exploratory_iteration_8h_gentle_mechanism/`

Optimization changes:

```text
Stage A control-summary cache: enabled
metric raw output: audit sample
component raw output: audit sample
marginal controls: summary mode
syndrome aggregation: online count-based aggregation
```

Main run status:

```text
status: COMPLETED
elapsed_seconds: 28653.366
workers: 18
jobs_completed: 576000 / 576000
metric_rows_scored: 48384000
component_score_rows_scored: 580608000
errors: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

Performance:

```text
control_summary_load_seconds: 0.134
throughput: about 20.1 jobs / second
previous desktop Stage B smoke throughput: about 4.6 jobs / second
```

Decision read:

```text
SYN_A: edge_roughening_sensitive_syndrome
SYN_C: edge_roughening_sensitive_syndrome
SYN_B: no_resolved_residual
SYN_D: no_resolved_residual
```

Interpretation:

```text
The large design-set run supports A/C edge/topology sensitivity, not clean
exact generator-mechanism sensitivity. Roughness-seed and asymmetry-strength
exact controls stayed near baseline. The next best branch is channel-specific
edge sensitivity: high-flow/signature-transition perturbation versus matched
random edge perturbation.
```

Caveat:

```text
track_frontier_preservation_metrics: false
track_saturation_timing: false
```

The long run uses graph-level preservation/destructiveness only. Keep the
p0.02 topology reads conservative until a smaller frontier-preservation audit
checks them directly.

### RFS-MB0 Stage B-2 Mechanism Calibration Smokes

Implemented and smoked the Stage B-2 mechanism-calibration / entropy-flow-
horizon overlay runner after the desktop Stage B addendum tightened control
identity and proxy discipline.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_stage_b2_mechanism_calibration_smokes_result.md`

Local outputs:

- `results/rfs_mb0_relation_atlas/20260528_stage_b2_contract_smoke/`
- `results/rfs_mb0_relation_atlas/20260528_stage_b2_small_desktop_smoke_v2/`

Implementation:

```text
new runner: omega/rfs_mb0_future_landscape/run_frontier_transform_stage_b2_mechanism_calibration.py
dedicated background CSV writer: enabled
compact Stage A control-summary loading: enabled
signal-aware partial checkpoint/status writes: enabled
control identity / proxy discipline fields: enabled
post-preservation destructiveness gates: enabled
```

Small desktop smoke:

```text
status: COMPLETED
elapsed_seconds: 53.334
workers: 18
jobs_completed: 288 / 288
metric_rows: 24192
component_score_rows: 290304
syndrome_rate_rows: 192
dependency_score_rows: 44
decision_rows: 4
errors: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

Control identity read:

```text
exact mechanism controls: 3
generation-level proxies: 1
topology-level proxies: 7
too-destructive/underdetermined conditions: 2
runtime-downgraded intended controls: 0
```

Decision read:

```text
SYN_A / SYN_C: edge_roughening_sensitive_syndrome at low smoke confidence
SYN_B / SYN_D: control_too_destructive_underdetermined
```

Interpretation:

```text
The Stage B-2 workflow is live and catches destructive/proxy conditions.
This is a mechanism-calibration smoke, not a validation claim.
Do not open holdout.
```

Scaling warning:

```text
For this small smoke, control summary loading dominated wall clock:
  control_summary_load_seconds: 37.667

Component score output remains large even with the dedicated writer:
  290304 rows, about 212 MB
```

Medium scale is reasonable with a wall-clock cap and local disk headroom. A
long run should either add a more compact component-score mode or cache the
Stage A control summary in a faster read format.

### RFS-MB0 Desktop Phase B / Stage A / Stage B Validation

Ran the desktop validation of the regenerated Phase B full-control path,
read-only Stage A syndrome audit, and Stage B mechanism-control smoke.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_desktop_phase_b_stage_a_b_validation_result.md`

Local outputs:

- `results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_phase_b_regenerated_full_controls/`
- `results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_stage_a_regenerated_full_controls/`
- `results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_stage_b_mechanism_smoke/`

Hardware boundary:

```text
desktop profile
Ryzen 5900X class CPU
RTX 4070 Ti available, not needed for this CPU-bound pass
workers: 18
job_batch_size: 4
thread caps: OMP/OPENBLAS/MKL/NUMEXPR = 1
```

Stage 1 regenerated Phase B full controls:

```text
status: COMPLETED
elapsed_seconds: 3959.802
jobs_completed: 1120 / 1120
metric_rows: 134400
control_rows: 13165111
stage_a_control_value_rows: 13163988
errors: 0
full_control_csv_written: 1
row_level_effect_csv_written: 0
holdout_scoring_count: 0
decision_class: phase_c_blocked_no_recurrence
```

Stage A syndrome audit:

```text
status: COMPLETED
elapsed_seconds: 178.609
control_source: phase_b_stage_a_control_values.csv
syndrome_component_rows: 940800
marginal_control_replicates: 500
decision_class: syndrome_smoke_joint_positive_above_marginal_controls
stage_b_allowed: 1
selected_syndrome_ids:
  SYN_A_low_growth_high_bottleneck_low_offdiag
  SYN_B_high_turnover_high_offdiag_high_window_delta
  SYN_C_low_growth_high_concentration_low_entropy
  SYN_D_high_turnover_high_entropy_low_bottleneck_control
```

Stage B mechanism smoke:

```text
status: COMPLETED
elapsed_seconds: 980.677
jobs_completed: 4480 / 4480
metric_rows: 376320
component_score_rows: 2822400
errors: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

Decision read:

```text
All four selected syndromes remain control_too_destructive_underdetermined.
Non-destructive dependency signal appears mainly in SYN_A/SYN_C under
roughness p0.01 and asymmetry p0.01/p0.02.
Most stronger mechanism controls are too destructive for negative
interpretation.
```

Interpretation:

```text
The syndrome branch is now more promising than marginal recurrence, because
Stage A separates preregistered joint signed syndromes from marginal-preserving
controls on regenerated desktop Phase B rows.

The mechanism-control ladder is not yet clean enough. Do not open holdout.
Next work should calibrate gentler preservation-first controls before scaling.
```

### RFS-MB0 Frontier-Transform Stage B Mechanism Smoke on Laptop

Implemented and ran a laptop-local Stage B mechanism-control dependency smoke
after the Stage A addendum gate allowed a mechanism-profile pass.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_laptop_stage_b_mechanism_smoke_30m_result.md`

Primary output:

- `results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_b_mechanism_smoke_30m/`

Input Stage A addendum:

- `results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_a_addendum_laptop_full_control/`

Input Phase B full-control rebuild:

- `results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls/`

Hardware boundary:

```text
laptop profile only
workers: 7
job_batch_size: 2
thread caps: OMP/OPENBLAS/MKL/NUMEXPR/NUMBA = 1
desktop runs should not inherit this profile
```

Claim boundary:

```text
Mechanism-control dependency smoke only.
Not historical desktop full-breadth confirmation.
No holdout scoring, n=6 transfer, alphabet expansion, candidate promotion,
Omega detection, agency detection, identity detection, or value detection.
```

Run status:

```text
status: COMPLETED
elapsed_seconds: 89.283
jobs_completed: 224 / 224
metric_rows: 18816
component_score_rows: 141120
syndrome_rate_rows: 224
dependency_score_rows: 52
decision_rows: 4
errors: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

Decision read:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag:
  control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.026785714285714284

SYN_B_high_turnover_high_offdiag_high_window_delta:
  no_measurable_syndrome
  baseline_syndrome_rate: 0.0

SYN_C_low_growth_high_concentration_low_entropy:
  control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.026785714285714284

SYN_D_high_turnover_high_entropy_low_bottleneck_control:
  no_measurable_syndrome
  baseline_syndrome_rate: 0.0
```

Interpretation:

```text
Mildly promising as an instrumentation target, not a validation result.
SYN_A and SYN_C are measurable and show weak roughness sensitivity under the
gentlest non-destructive roughness control, while gentle asymmetry is generic.
The stronger controls are often substrate-destructive, so negative reads remain
underdetermined. SYN_B and SYN_D were not measurable in this limited Stage B
design.
```

Next step:

```text
Run a Stage B-2 targeted mechanism smoke with gentler preservation-first
control ladders before spending more seeds or opening any holdout path.
```

### RFS-MB0 Frontier-Transform Syndrome Audit Laptop Validation

Ran a laptop-local validation of the new frontier-transform Phase B / Stage A
syndrome audit path.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_frontier_transform_syndrome_laptop_validation_result.md`

Local outputs:

- `results/local_runs/20260528_laptop_frontier_transform_phase_b_validation_192jobs/`
- `results/local_runs/20260528_laptop_frontier_transform_stage_a_validation_192jobs/`

Claim boundary:

```text
This was a local runner/output-contract validation, not a scientific Phase B
rerun and not a holdout, candidate-promotion, mechanism-dependency, Omega,
agency, identity, or value result.
```

Reason:

```text
The historical Phase B/source CSV directories are ignored and not present in
this laptop clone, so the run regenerated a small fixture-like input bundle
under results/local_runs/ to exercise the implementation path.
```

Laptop profile:

```text
workers: 7
job_batch_size: 2
thread caps: OMP/OPENBLAS/MKL/NUMEXPR/NUMBA = 1
machine: laptop DESKTOP-LVVT7H7, Intel i7-1165G7, Intel Iris Xe, no CUDA
```

Phase B local validation completed:

```text
jobs_completed: 192 / 192
metric_rows: 14336
control_rows: 1245559
errors: 0
holdout_scoring_count: 0
decision_class: phase_c_blocked_no_recurrence
phase_c_ready: 0
```

Stage A syndrome audit completed:

```text
metric_rows: 14336
control_rows: 1245559
syndrome_component_rows: 118272
errors: 0
new_systems_generated: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

Stage A emitted a positive preregistered-syndrome readiness row on the local
fixture, selecting:

```text
diffusive_noise_syndrome
recurrence_cascade_syndrome
stabilizing_boundary_syndrome
transition_boundary_syndrome
```

Interpretation:

```text
This validates that the Stage A scoring/readiness path executes on nontrivial
rows. It does not establish that the historical Phase B run contains these
syndromes.
```

CSV hardening added during the validation:

```text
shared frontier-transform read_csv tolerates UTF-8 BOM headers
shared write_csv uses csv.writer with larger buffering instead of DictWriter
Phase B can skip duplicate row-level effect CSVs during validation runs
```

Main observed bottleneck:

```text
phase_b_design_control_rows.csv was about 745 MB.
Worker execution finished quickly; final CSV materialization and Stage A CSV
ingestion dominated wall time.
```

Follow-up compact Stage A control-value contract:

```text
Phase B now emits phase_b_stage_a_control_values.csv.
Stage A prefers that compact table and falls back to phase_b_design_control_rows.csv.
```

Validation on the same 192-job laptop Phase B output:

```text
full debug control CSV: 744725521 bytes
compact Stage A control CSV: 172520869 bytes
phase_b_syndrome_readiness.csv: identical
phase_b_syndrome_smoke.csv: identical
phase_b_syndrome_vs_controls.csv: identical
phase_b_syndrome_component_scores.csv: identical
Stage A elapsed, full source: 470.003 seconds
Stage A elapsed, compact source: 403.329 seconds
```

A compact Phase B rerun with `--skip-full-control-csv` completed cleanly:

```text
jobs_completed: 192 / 192
stage_a_control_value_rows: 1245364
full_control_csv_written: 0
phase_b_design_control_rows.csv: 46 byte sentinel
phase_b_stage_a_control_values.csv: about 172.5 MB
errors: 0
```

Interpretation:

```text
The compact contract removes Stage A's dependency on the full debug control CSV
and preserves syndrome outputs. The next bottleneck is Stage A control-value
grouping/scoring, not just raw CSV emission.
```

Follow-up Stage A scoring optimization:

```text
control buckets are now summarized once
control_mean/control_std are cached per metric/probe/flow/window
percentiles use sorted control values and binary search
control rows are filtered to preregistered syndrome metrics before scoring
```

Validation on the same compact 192-job Phase B output:

```text
pre-cache compact Stage A elapsed: 456.399 seconds
cached compact Stage A elapsed: 8.400 seconds
phase_b_syndrome_readiness.csv: identical
phase_b_syndrome_smoke.csv: identical
phase_b_syndrome_component_scores.csv: identical
```

## 2026-05-27

### RFS-MB0 Frontier-Transform Syndrome and Mechanism-Control Audit Spec

Added the next audit spec after Phase B showed control-equivalent marginal recurrence:

- `docs/RFS_MB0_FRONTIER_TRANSFORM_SYNDROME_AND_MECHANISM_CONTROL_AUDIT_SPEC.md`

Reason:

```text
Phase B did not show absence of all recurrence.
It showed that marginal frontier-transform recurrence is too generic:
raw design-set recurrence appeared, but matched recurrence controls reached the same strongest rate.
```

Core change:

```text
Stop asking only:
  does metric M recur above threshold T?

Ask instead:
  does a preregistered joint signed frontier-transform syndrome recur above controls,
  and does it show the expected dependency profile under constraint/asymmetry/roughness perturbations?
```

The spec defines two stages:

```text
Stage A:
  read-only Phase B postmortem and syndrome smoke on existing rows

Stage B:
  small design-set mechanism-control rerun with roughness/asymmetry/constraint controls where implementable
```

Important interpretation update:

```text
Mechanism controls are dependency tests, not survival tests.
A syndrome killed by constraint/asymmetry perturbation may be mechanism-dependent, not falsified.
```

Still blocked:

```text
holdout Phase C
n=6 transfer
alphabet expansion except optional tiny diagnostic
agent / identity / value labels
Omega-positive claims
```

### RFS-MB0 Frontier-Transform Phase B Design-Set Recurrence

Implemented and ran the larger design-set recurrence pass requested by:

- `docs/RFS_MB0_FRONTIER_TRANSFORM_PHASE_B_10H_DESIGN_RECURRENCE_SPEC.md`

Runner:

- `omega/rfs_mb0_future_landscape/run_frontier_transform_phase_b.py`

Primary retained note:

- `docs/research_notes/validation_results/rfs_mb0_frontier_transform_phase_b_10h_result.md`

Primary output:

- `results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_b_10h/`

Before the primary run, the runner was updated for:

```text
periodic status.json writes
phase_b_progress_checkpoints.csv during execution
SIGINT/SIGTERM/SIGBREAK stop requests
shutdown cushion before wall-clock expiry
normal final artifact generation from completed rows after interruption
```

The repaired smoke completed cleanly:

```text
jobs_completed: 16 / 16
metric_rows: 896
control_rows: 55283
errors: 0
holdout_scoring_count: 0
phase_b_design_recurrence_summary.csv: present
decision_class: phase_c_blocked_no_recurrence
```

Primary Phase B completed cleanly:

```text
jobs_completed: 1120 / 1120
metric_rows: 134400
control_rows: 13165111
errors: 0
elapsed_seconds: 3100.015
holdout_scoring_count: 0
```

Raw design-set recurrence appeared in B0-viable families:

```text
bottleneck observed recurrence mean: 0.2875
support_turnover observed recurrence mean: 0.2600
transition_matrix observed recurrence mean: 0.2417
window_stability observed recurrence mean: 0.1176
```

However, after repairing the matched recurrence-control summary, the strongest rows were control-equivalent:

```text
observed_recurrence_rate: up to 0.6
control_recurrence_mean: matched at 0.6 on strongest rows
recurrence_excess: 0.0
```

Final decision:

```text
decision_class: phase_c_blocked_no_recurrence
phase_c_ready: 0
supporting_metric_family_count: 0
supporting_probe_count: 0
holdout_scoring_count: 0
```

Interpretation:

```text
Do not open frozen holdout Phase C from this result.
Frontier-transform instrumentation remains technically healthy.
The limiting issue is not runtime or workflow; it is control-equivalent recurrence.
Next work should test preregistered joint syndromes and mechanism-dependency controls.
```

### RFS-MB0 Frontier-Transform B0 Control/Flow Repair

Implemented the control/flow semantic repair pass requested by:

- `docs/RFS_MB0_FRONTIER_TRANSFORM_PHASE_B0_CONTROL_FLOW_REPAIR_SPEC.md`

Primary output:

- `results/rfs_mb0_relation_atlas/20260527_frontier_transform_b0/`

B0 changes:

```text
separated constrained_window_flow from one_step_local_flow
removed silent fallback from frontier-window transition flow
reported no-window-target and skipped-state rates
replaced four-integer sketch stability with metric-vector and real distribution stability
computed transform controls rather than only listing them
reported signed and absolute effect directions
kept holdout scoring at zero
```

B0 completed cleanly:

```text
jobs_completed: 160 / 160
metric_rows: 8960
control_rows: 643112
errors: 0
decision_class: phase_b_ready
holdout_scoring_count: 0
```

Viable metric families after B0:

```text
support_turnover
transition_matrix
bottleneck
window_stability
```

Interpretation:

```text
B0 permitted a design-set Phase B recurrence run.
B0 was still not detection or validation.
Holdout Phase C remained frozen.
```

### RFS-MB0 Frontier-Transform Phase A Instrumentation Preflight

After endpoint/quotient probe instrumentation failed to produce adequate independent non-identity axes, the branch pivoted from endpoint-state signatures to frontier-transform metrics.

Spec:

- `docs/RFS_MB0_FRONTIER_TRANSFORM_INSTRUMENTATION_SPEC.md`

Primary output:

- `results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_a/`

New measurement object:

```text
frontier-transform window F_Ha -> F_Hb
```

rather than:

```text
endpoint signature distribution at H
```

Phase A completed cleanly:

```text
jobs_completed: 160 / 160
row_count: 4480
errors: 0
holdout_detection_enabled: false
candidate_detection_enabled: false
```

Viable non-control transform metric families:

```text
growth
support_turnover
transition_matrix
branch_merge
bottleneck
window_stability
```

Interpretation:

```text
Frontier-transform instrumentation was viable enough for B0 control/flow repair.
This was not a detection claim.
```

### RFS-MB0 Instrumentation Branch Pivot

Added and implemented documentation for the instrumentation pivot:

- `docs/RFS_MB0_INSTRUMENTATION_BRANCH_PIVOT_AND_PROBE_PANEL_SPEC.md`
- `docs/RFS_MB0_BOUNDARY_DEFORMATION_GUARDRAIL_AND_QUOTIENT_PROBE_SPEC.md`

Current read at that point:

```text
The substrate is potentially fertile, but the instrumentation is flawed or underpowered.
```

The branch stopped treating the next task as broader search and reframed it as measurement-basis construction.

Important discipline added:

```text
probe preflight before candidate scoring
design/holdout split
threshold selection audit
multiplicity audit
identity leakage reporting
holdout freeze until instrument readiness
```

### RFS-MB0 Detector Instrumentation Repair and Boundary Recurrence

The detector instrumentation repair pass sharpened earlier boundary recurrence results.

Corrected group classes:

```text
independent_axis_recurrent_but_collision_limited: 16
weak_control_bundle_recurrence: 4
clean_recurrent_boundary_candidate: 0
sparse_regime_recurrent_candidate_pending_floor_audit: 0
```

Interpretation:

```text
Recurrent boundary structure is visible.
The main limit is collision/probe resolution, not no signal.
Clean quotient-level deformation was not established.
```

This motivated the instrumentation branch and ultimately the frontier-transform pivot.

## 2026-05-22

### RFS0 Strict Reachable Futures Small Smoke

Implemented the first RFS0 exact finite reachable-futures substrate batch from
`docs/RFS0_STRICT_REACHABLE_FUTURES_BATCH_SPEC.md`.

Code changes:

- added `omega/rfs0/substrate.py`;
- added `omega/rfs0/exact.py`;
- added `omega/rfs0/run_strict_batch.py`;
- added exact reachable sets, finite-horizon viability kernels, capture basins,
  perturbation recovery rates, and strict-future contraction metrics;
- added checkpointed JSONL/CSV/status/summary output after completed jobs;
- added hard-cap timeout salvage that cancels unfinished work and writes partial
  summaries.

Primary result:

- `docs/research_notes/validation_results/rfs0_strict_reachable_futures_small_smoke_result.md`
- `results/rfs0/20260522_strict_reachable_futures_small_smoke/summary.md`

Run shape:

```text
systems:
  108

regimes:
  balanced, permissive, harsh, repair_rich, commit_rich, capacity_tight

controls:
  structured
  dense_permissive_control
  dead_control
  random_edge_control
  shuffled_admissibility_control
  no_perturbation_control

workers:
  18

elapsed:
  about 6 seconds

errors:
  0
```

Timeout salvage test:

```text
cap:
  1 second

completed rows:
  13

status:
  TIMED_OUT

artifact status:
  systems.jsonl, results.csv, summaries, status.json, and summary.md retained
```

Interpretation:

- exact computation is cheap at this scale;
- structured substrate produced sparse nonzero strict kernels in balanced,
  repair-rich, and commit-rich regimes;
- permissive regime and dense control are too large/trivial;
- harsh and capacity-tight regimes collapse to zero strict viability;
- random-edge and shuffled-admissibility controls remain too strong, so control
  separation is not yet adequate;
- contraction events exist, but expansion events are absent under the current
  metric.

Current read:

```text
RFS0 is promising as a measurement floor, but not ready for a longer validation
run as-is. Next small probe should improve control separation, contraction
geometry, and parameter resolution without loosening K_strict just to get more
positives.
```

## 2026-05-21

### VAL1-MF Interference Audit Smoke

Implemented the sampled counterfactual interference audit requested by
`docs/VAL1_MF_INTERFERENCE_AUDIT_SPEC.md`.

Code changes:

- added `omega/val1_mf/run_interference_audit.py`;
- reused the existing two-field generator;
- added coupling masks for uncoupled, full, enable-only, obstruct-only,
  restore-only, commit-only, and shared-capacity-only modes;
- made sampled alive / terminal deltas primary;
- retained raw joint enumeration only as a diagnostic.

Primary result:

- `docs/research_notes/validation_results/val1_mf_interference_audit_smoke_result.md`
- `results/val1_mf/20260521_interference_audit_smoke/summary.md`

Run shape:

```text
paired worlds:
  100

rollout_samples:
  256

horizon:
  d16

workers:
  18

elapsed:
  17.0 seconds

errors:
  0
```

Interpretation:

- sampled counterfactual measurement worked cleanly;
- full coupling improved mean joint alive probability from 0.734 to 0.816;
- `constructive_delta_bin` appeared in 22/100 rows;
- one provisional `A_local_dominance_bin` row appeared;
- no robust destructive or commit/obstruct-driven interference appeared;
- diagnostic enumeration still capped often, but it was no longer the primary
  evidence path.

Current read:

```text
VAL1-MF now has a viable sampled interference measurement pattern.
The visible object is constructive support/recovery, not yet destructive
pseudo-Omega-like interference. The next probe should target destructive
hazards with stricter alive/hazard metrics before scaling.
```

### VAL1-MF Two-Field Compatibility Smoke

Implemented the first minimal multifield compatibility smoke on top of VAL0-G.

Code changes:

- added `omega/val1_mf/coupled_grammar.py`;
- added `omega/val1_mf/metrics.py`;
- added `omega/val1_mf/run_smoke.py`;
- added joint-state enumeration, rollout terminal estimates, compatibility
  ratios, cap-hit reporting, and neutral compatibility bins.

Primary result:

- `docs/research_notes/validation_results/val1_mf_two_field_compatibility_smoke_result.md`
- `results/val1_mf/20260521_two_field_compatibility_smoke_cap4096/summary.md`

Run shape:

```text
paired worlds:
  150

workers:
  18

max_states_per_depth:
  4096

rollout_samples:
  128

elapsed:
  about 79 seconds

errors:
  0
```

Interpretation:

- the smoke completed cleanly and produced nondegenerate bins;
- `mutual_collapse_bin`, `joint_viable_bin`, and `uncoupled_parallel_bin`
  appeared in small non-censored counts;
- the dominant outcome was still `mixed_or_censored_bin`: 142/150 rows;
- aggregate joint cap hit rate was 0.947;
- naive two-field enumeration did not solve the cap problem and likely worsened
  it by multiplying reachable combinations.

Current read:

```text
Do not scale this exact two-field enumerator.
Multifield compatibility remains relevant, but the next probe should switch to
sampled or cap-aware compatibility estimates before a long run.
```

### VAL0-G Neutral Grammar Stability Probe

Implemented the second small VAL0-G forced-fit audit.

Code changes:

- added cap-hit fields through depth 32;
- added `coarse` and `full` signature modes;
- added downstream cut sensitivity alongside initial cut sensitivity;
- added neutral bin labels alongside interpretive class names;
- added signature, cap-hit, and cut-sensitivity summary outputs.

Primary result:

- `docs/research_notes/validation_results/val0_g_neutral_grammar_stability_probe_result.md`
- `results/val0_g/20260521_neutral_grammar_stability_probe_cap2048/summary.md`

Run shape:

```text
neutral_grammar_v1:
  250 seeds

guardrails:
  low_resolution_dense: 50 seeds
  brittle_peak: 50 seeds

signature modes:
  coarse
  full

rows:
  700

errors:
  0

max_states_per_depth:
  2048
```

Interpretation:

- multiple neutral bins appeared again;
- coarse/full signatures agreed at `0.996` for neutral rows;
- cap 512 vs 2048 did not collapse the neutral bin structure;
- high-mass classes remain heavily cap-censored at d16/d32;
- dense and brittle guardrails are cap-saturated and not semantically clean
  under the current classifier;
- downstream cut sensitivity adds useful information but should not yet be
  treated as an ontology-level metric.

Current read:

```text
VAL0-G remains on the right substrate.
The main risk is measurement censoring, not obvious generator fine-tuning.
Do not scale to a full atlas until cap-aware or sampled survival metrics are
added.
```

### VAL0-G Neutral Grammar Geometry Smoke

Implemented the first VAL0-G smoke substrate:

- `omega/val0_g/grammar.py`
- `omega/val0_g/metrics.py`
- `omega/val0_g/run_smoke.py`

Primary result:

- `docs/research_notes/validation_results/val0_g_neutral_grammar_smoke_result.md`
- `results/val0_g/20260521_neutral_grammar_smoke_v2/summary.md`

Run shape:

```text
neutral_grammar_v1:
  50 seeds

guardrails:
  low_resolution_dense: 12 seeds
  brittle_peak: 12 seeds

rows:
  74

errors:
  0
```

Interpretation:

- initial calibration was too expansion-heavy and saturated depth-16 descendant
  mass;
- a minimal v2 calibration broadened lower-enable, higher-obstruction, decay,
  and capacity-pressure regimes;
- v2 produced multiple post-hoc measured geometry classes:
  - `recoverable_basin_like`: 26 / 50 neutral rows;
  - `self_terminating`: 16 / 50 neutral rows;
  - `thin_ridge`: 6 / 50 neutral rows;
  - `deep_corridor_like`: 2 / 50 neutral rows.

Current read:

```text
VAL0-G passed minimal smoke.
It does not validate Omega.
It does justify a slightly larger stability probe with cap-hit reporting,
depth 32 if cheap, and a better brittle/thin-ridge guardrail.
```

### Public Reorientation Around VAL0-G

The public-facing repository orientation was updated after the VAL0-CT geometry
battery.

Current interpretation:

```text
VAL0-CT:
  useful first task-space calibration layer
  R1 anchor advantages reproduced
  dense controls remained clean
  broad held-out / unlabeled generalization not established

VAL0-G:
  current front edge
  neutral grammar geometry atlas
  asks whether recoverable-continuation geometries emerge without outcome labels
```

Reason for pivot:

- the 12h unlabeled geometry battery completed cleanly and preserved guardrails;
- corridor d8 did not survive scale as a robust predictor;
- candidate future-R0 variance was the best surviving weak hook;
- the project should now study geometry emergence directly rather than treating
  R1 victory as the object.

Updated entry points:

- `README.md`
- `docs/roadmaps/OMEGA_EXPERIMENTAL_ROADMAP.md`
- `docs/PUBLIC_RESULTS_INDEX.md`
- `docs/OMEGA_PROJECT_MANUAL.md`
- `docs/research_notes/validation_design/README.md`
- `results/val0_ct/README.md`
- `results/val0_g/README.md`

Next implementation target:

```text
Implement neutral_grammar_v1 smoke:
  survival curves
  descendant mass
  branching reproduction
  terminal probability
  cut sensitivity k=1
  dense/flat guardrail
```

## 2026-05-17

### Root Script Cleanup

Moved historical root-level Python probe scripts into:

- `scripts/historical_probes/`

Added:

- `scripts/historical_probes/README.md`

Reason:

- keep the repository front page clean for public readers;
- make VAL0-CT docs the obvious entry point;
- preserve old scripts for provenance, reproducibility, and failure analysis.

Historical report and log references were updated to point at the new script
paths.

### Root Result Folder Cleanup

Moved tracked historical result folders into:

- `results/historical_probes/`

Moved ignored local smoke, calibration, stress, and scratch result folders into:

- `results/local_runs/`

Added:

- `results/README.md`
- `results/historical_probes/README.md`
- `results/val0_ct/README.md`

Future VAL0-CT outputs should be written under:

```text
results/val0_ct/<timestamp-or-run-id>/
```

Do not add new root-level `*_results` folders.

### Public Reorientation Around VAL0-CT

The public-facing repository orientation was updated to make the Constructor
Theory / VAL0-CT pivot explicit.

Updated entry points:

- `README.md`
- `docs/roadmaps/OMEGA_EXPERIMENTAL_ROADMAP.md`
- `docs/PUBLIC_RESULTS_INDEX.md`
- `docs/OMEGA_PROJECT_MANUAL.md`
- `docs/current_theory/README.md`
- `docs/research_notes/validation_design/README.md`

Current front-door statement:

```text
VAL0-CT is the current validation target.
It tests whether persistence-conditioned reachability, R1, predicts
long-horizon reachability retention better than raw reachability, R0, and
equal-budget R0-lookahead controls in structured task algebras.
```

Public framing decision:

- COM/fiber work is historical evidence for viable propagation and
  coarse-graining discipline, not the current validation center.
- Trajectory-space probes are negative constraints and fakeout anatomy.
- CA/DAR/DAX probes calibrate the primitive floor rather than validating Omega
  proper.
- DAX-G5's failed held-out prediction is one of the reasons the project moved
  to task-space validation.

Next implementation target:

```text
Implement VAL0-CT smoke, CPU-first, using:
  low_resolution_dense
  structured_asymmetric
  lock_in_seeded

Compare:
  random
  R0
  R0_lookahead
  R1
  pseudo_omega
```

## 2026-05-16

### Formal-Stack Recenter: Primitive Floor to Valuer-Level Omega

New theory notes were added under:

- `docs/research_notes/omega_theory/`
- `docs/research_notes/primitive_branch/`

New canonical entry points:

- `docs/research_notes/omega_theory/formal_stack_v0.md`
- `docs/research_notes/omega_theory/omega_glossary.md`
- `docs/research_notes/omega_theory/omega_as_viable_value_bearing_trajectory_space.md`
- `docs/research_notes/omega_theory/regenerative_filtering_slack_and_parasitic_modes.md`
- `docs/research_notes/primitive_branch/relation_as_historical_binding.md`
- `docs/research_notes/primitive_branch/omega_meets_fep.md`
- `docs/research_notes/primitive_branch/valuerhood_as_recoverable_historical_identity.md`

Current working stack:

```text
distinction
-> asymmetry
-> relation / causal continuity
-> identity
-> recoverability
-> valuerhood
-> viability
-> Omega-compatible viability
-> lushness of value-bearing trajectory space
```

Core thesis now tracked in the manual:

```text
Omega is the asymptotic compatibility structure of value-bearing trajectory
space.
```

Interpretive update:

- Relation is now treated as causal continuity through transformation, not
  merely graph adjacency, neighbor dependence, coupling, or social relation.
- Identity is organized causal continuity through change.
- Recoverability is perturbation-continuability, not exact restoration.
- A valuer is a bounded historical identity for which different continuations
  asymmetrically affect recoverable continuability.
- Viability is a gate; nested, compatible, value-bearing trajectory richness is
  the target.

Consequence for prior executable work:

- COM fiber transport remains the strongest toy-substrate witness for viable
  propagation and coarse-graining discipline.
- Trajectory-space probes remain useful negative constraints and fakeout
  anatomy.
- CA, DAR, and DAX probes are now explicitly primitive-floor calibration unless
  they include minimal valuerhood and recoverable continuability.
- DAX-G5's failed held-out prediction is consistent with this boundary: it
  describes motif ecology in a primitive rule space, not a validation-ready
  Omega detector.

Roadmap decision:

```text
The next Omega-proper validation family should be a minimal valuer-world
benchmark, not another bare cellular or field-dynamics scale-up.
```

Probe V0 target:

- construct minimal self-maintaining valuers;
- include perturbation recovery, path consequence, and action or interaction
  channels;
- measure Omega-level predictors against survival, reward, reachability,
  empowerment, and local-viability baselines;
- include fakeout controls for stasis, clocks, lock-in, externally maintained
  persistence, and high reachability without self-maintenance.

## 2026-05-11

### Progenitor Drafts Added

Added the early theory-side papers to:

- `docs/progenitor_drafts/`

Status:

- drafts only;
- early theoretical provenance;
- not current validation results;
- not final claims about the formal object.

Included PDFs:

- `intelligent_agency_under_computational_irreducibility.pdf`
- `scaling_paper_v2.pdf`
- `telos_2_0_draft.pdf`
- `echo_rosetta_version.pdf`
- `gradient_ethics.pdf`
- `gradient_field_theory_of_value_v51.pdf`

### Current Theory And Trajectory-Space Notes Added

Added the current theory/status draft to:

- `docs/current_theory/omega_signature_v0_1.pdf`

Status:

- current draft artifact;
- not peer reviewed;
- not a validation result by itself;
- best current written entry point into the Omega claim ladder and COM witness.

Added trajectory-space branch notes to:

- `docs/research_notes/trajectory_space/trajectory_space_omega_research_note.pdf`
- `docs/research_notes/trajectory_space/trajectory_space_omega_triage_note.pdf`

Status:

- draft research notes;
- branch-selection/planning artifacts;
- not replacements for the current COM fiber-transport witness.

Framing decision:

- `Project_Omega.pdf` is treated as a current theory/status draft.
- The trajectory-space PDFs are treated as active research branch notes.
- The earlier PDFs remain under `docs/progenitor_drafts/` as historical
  provenance.

### Repository Setup

- Local repo pushed to GitHub:
  - https://github.com/6ixpoolgames/Omega
- Current pushed baseline before this log:
  - `cd0fe04 Initial Omega validation workspace`
  - `88d0fa3 Add Probe 10 COM robustness results`

### Current State

The strongest current toy-substrate object is:

```text
F,T attractive coupling
kappa = center_of_mass
alpha = 0.45, 0.50, 0.525
T = 900, 1500, 2400
```

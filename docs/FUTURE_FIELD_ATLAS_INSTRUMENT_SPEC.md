# Future Field Atlas Instrument Spec

Status: draft / pre-scientific instrument build
Branch: `instrument/future-field-atlas`
Package target: `omega.future_field_atlas`
Runner target: `omega.future_field_atlas.run_future_field_atlas`
Artifact prefix: `future_field_atlas`

## 0. Purpose

Build a clean instrument for scanning, saving, and mapping future-field topology under lawful substrate transformations.

This is not a science run. It is not a validation run. It is not a coupled-frontier result. It is an instrumentation reset intended to replace the old response-classifier-first workflow with a raw-geometry-first atlas workflow.

The old horizon-transport runner was useful and should remain available for continuity. But the next phase needs a different separation of concerns:

```text
old workflow:
  generate substrate
  build selected horizon-pair transport matrices
  compute summaries
  classify response
  aggregate labels

new workflow:
  generate lawful substrate
  scan frontier evolution
  preserve topology
  map raw features
  analyze downstream
  label last, if useful
```

The atlas should make future topology the primary data product.

## 1. Claim boundary

This instrument does not test or validate Omega.

It must not emit claims about:

```text
Omega
agency
identity
valuerhood
value
moral relevance
candidate promotion
holdout readiness
graph-channel causality
```

Allowed claim language:

```text
The instrument scanned future-field topology for a specified finite substrate.
The instrument emitted raw frontier, transition, rank-boundary, and transport-flow artifacts.
A downstream analysis may map features of those artifacts.
```

Disallowed claim language:

```text
The instrument detected Omega.
The instrument detected agents or valuers.
The instrument found value-bearing substrates.
The instrument validated coupled frontier compatibility.
```

## 2. 3P posture

### Principled

The measured object is future-field topology under lawful transformation.

The instrument should make explicit:

```text
state space
transformation rule
frontier expansion rule
horizon schedule
observable rank-boundary rule
perturbation rule
raw topology emitted
feature maps derived
```

### Minimal

Do not rebuild the full empirical program. Keep the first implementation narrow enough to audit:

```text
single-frontier scanner smoke
rank-boundary calibration recovery from raw topology
then coupled-frontier scan
```

Do not add rich semantic labels, agents, values, or boundary ontology.

### Revelatory

The instrument should reveal topology, not force-fit a response class.

Primary questions:

```text
What frontier shape emerges over horizon?
Where do boundaries, bottlenecks, splits, merges, and corridors appear?
How does perturbation deform the topology?
Can known relation-geometry signals be recovered without response labels?
How do two future fields later compose, interfere, capture, erase, or support each other?
```

## 3. Architectural separation

The instrument must separate four layers.

### 3.0 Clean operator-native condition identity

Implementation must treat mathematical specs as the condition primitives.
Historical treatment-arm names belong in `docs/FUTURE_FIELD_ATLAS_GLOSSARY.md`,
not in the runtime schema. Native condition identity is expressed through:

```text
StateSpaceSpec
TransformationLawSpec
SelectionOperatorSpec
ObservableSpec
FrontierScanSpec
```

For rank-based calibration, the selection operator should record:

```text
selection_operator_id
selection_operator_family
base_out_degree
effective_out_degree
retained_rank_set
removed_rank_set
stochastic_flag
seed_policy
selection_operator_params_json
```

The runner should not emit `boundary_control`, `condition_role`, `human_label`,
or `legacy_*` columns. Human-readable historical translation is documentation,
not runtime identity.

Each formal spec must be serializable and manifest-backed:

```text
canonical JSON serialization
stable deterministic digest
explicit params JSON
manifest entry
condition identity traceability
```

`TransformationLawSpec` owns the invariant/asymmetry engine:

```text
candidate successor rule
admissibility predicate
energy / scoring function
invariant observable used by the law
asymmetry or preservation term
roughness / noise term
deterministic or stochastic status
seed policy
```

### 3.1 Scanner

Generates lawful frontier evolution and saves topology.

The scanner should not classify. It should record.

### 3.2 Mapper

Computes raw and semi-raw geometric features from the scanned topology.

Examples:

```text
frontier size
frontier support count
component count
branching factor
edge rank statistics
inside-rank-boundary selected fraction
outside-rank-boundary selected fraction
transport matrix value totals
transport concentration
support and path-count composition residuals
```

### 3.3 Analyzer

Compares maps across baselines, perturbations, product controls, and coupled runs.

Examples:

```text
baseline vs perturbation raw difference
joint vs product residual
cross-perturbation effect
rank-boundary deformation
component collapse / recovery
```

### 3.4 Labeler

Optional downstream convenience layer.

Labels are allowed only if:

```text
every label is reconstructible from raw columns;
raw fields are emitted first;
labels are not the primary evidence;
labels do not use Omega / agency / value language.
```

## 4. Phase plan

### Phase 0: instrument smoke

Goal: prove that the scanner can unfold frontier evolution and save raw topology without relying on the old response taxonomy.

Scope:

```text
single frontier
small design set
H128 or smaller if needed for smoke
no coupled frontiers
no semantic labels
```

### Phase 1: rank-boundary calibration recovery

Goal: recover a fixed low-rank boundary calibration pattern from raw topology.

Calibration target from prior branch:

```text
primary invariant:
  symbol_histogram_distance

live calibration pattern:
  fixed low-rank successor prefix / rank-boundary pressure

calibration condition:
  retained low-energy prefix under a rank-boundary observable
```

The recovery should be argued from raw atlas features, not from `transport_amplified_aligned` labels.

### Phase 2: coupled future-field scan

Goal: scan two interacting frontier fields under shared low-rank successor-core pressure.

Scope:

```text
two future fields
joint frontier topology
product baseline
cross-perturbation
marginal retention
joint-vs-product residual
support / capture / erasure features as downstream analysis only
```

Initial coupled implementation status:

```text
runner: omega.future_field_atlas.run_coupled_future_field_atlas
module: omega.future_field_atlas.coupled
public/runtime term: coupled
deprecated working term: comField
```

The initial coupled probe is infrastructure only. It compares a product
baseline against a coupled joint selector over the same product successors:

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

This joint selector is a first probe operator, not a theory conclusion.

Coupled hardening requirements:

```text
CoupledOperatorSpec / coupled_operator_manifest.csv
condition_pairing_policy
start_pairing_policy
persistent cap poisoning
audit statuses:
  PASS
  PASS_WITH_SKIPS
  NO_COMPLETE_ROWS
  FAIL
reconstruction_audit_clean_pass
reconstruction_audit_interpretable_pass
coupled_medium_scale_readiness_summary.csv
```

Coupled marginal projection rows are non-causal product-vs-coupled marginal-set
deltas:

```text
artifact:
  coupled_marginal_projection_delta_by_horizon.csv
required fields:
  projection_semantics = product_vs_coupled_marginal_set_delta
  causal_interpretation = none
```

If a product or coupled frontier is internally capped at horizon `h`, all
descendant topology for that mode must be marked `truncated_noninterpretable`.
Any comparison row depending on a poisoned mode must inherit the worst status.

### Phase 3: interaction feature mapping

Goal: map candidate interaction patterns from raw data.

Candidate downstream reads:

```text
product-equivalent
constructive support
capture
component erasure
destructive interference
recovery after perturbation
```

These are feature reads, not Omega claims.

## 5. Minimal substrate contract

The first implementation may reuse existing substrate-generation machinery, but it should not depend on the old runner's response-classification path.

A scanned substrate instance should record:

```text
substrate_id
state_space_id
coordinate_set_id
symbol_domain_id
state_id_schema
metric_id
adjacency_rule_id
state_space_params_json
start_state_id
seed
law_id
law_family
candidate_successor_rule_id
candidate_successor_params_json
energy_function_id
energy_params_json
admissibility_predicate_id
invariant_observable_id
invariant_params_json
asymmetry_term_id
roughness_term_id
transformation_law_seed_policy
observable_set_id
observable_family
observable_params_json
selection_operator_id
selection_operator_family
selection_operator_params_json
base_out_degree
effective_out_degree
retained_rank_set
removed_rank_set
stochastic_selection_flag
seed_policy
frontier_scan_id
frontier_expansion_rule_id
horizon_schedule_id
frontier_scan_params_json
frontier_artifact_status_domain
```

## 6. Horizon schedule

The atlas should treat horizon as a time series, not only as selected pair chunks.

Primary smoke schedule:

```text
H = 0..128 if affordable
```

Acceptable minimal smoke schedule:

```text
H = 0..32 dense
plus H = 48, 64, 96, 128
```

Compatibility with old H128 pairs should be preserved as a derived view, not as the primary evidence.

Derived H128 pairs:

```text
0->1
1->2
2->4
4->8
8->16
16->24
24->32
32->48
48->64
64->96
96->128
```

Known active region to emphasize in diagnostics:

```text
16->24 through 96->128
```

But the scanner should save enough per-horizon data to permit finer analysis around onset.

## 7. Rank-boundary observable contract

The first calibration target should preserve the low-rank boundary primitive as
one observable, not as the whole atlas.

For each source state and candidate successor set, record edge rank information:

```text
source_state_id
target_state_id
candidate_rank
candidate_energy
selected_flag
rank_offset_from_boundary
selection_operator_id
selection_operator_family
base_out_degree
effective_out_degree
retained_rank_set
removed_rank_set
```

Default calibration observable:

```text
inside rank boundary = candidate ranks <= rank_boundary_k
outside rank boundary = candidate ranks > rank_boundary_k
```

Do not hard-code the default rank boundary as theory. Treat it as the current
calibration observable.

## 8. Primary raw artifacts

These are mandatory for Phase 0 / Phase 1 unless explicitly marked optional.
Artifact names in this spec are logical schema names. The runner writes primary
CSV artifacts as `.csv.gz` by default for lossless storage efficiency and records
the physical names in `future_field_atlas_manifest.json`. Use
`--csv-output-mode plain` for plain CSV debugging or `--csv-output-mode both`
when compatibility copies are needed.

Default physical storage for high-volume raw topology is sharded:

```text
frontier_nodes_by_horizon_shard_manifest.csv.gz
frontier_nodes_by_horizon_shards/part-*.csv.gz
frontier_edges_by_step_shard_manifest.csv.gz
frontier_edges_by_step_shards/part-*.csv.gz
```

The logical artifact names remain `frontier_nodes_by_horizon.csv` and
`frontier_edges_by_step.csv`. Shards are a storage layout, not a semantic
filter. Consolidated raw topology output remains available with
`--raw-topology-output-mode consolidated` or `--raw-topology-output-mode both`.

The coupled atlas runner uses the same logical/physical rule for joint
topology. Its default physical layout is:

```text
coupled_joint_frontier_nodes_by_horizon_shard_manifest.csv.gz
coupled_joint_frontier_nodes_by_horizon_shards/part-*.csv.gz
coupled_joint_frontier_edges_by_step_shard_manifest.csv.gz
coupled_joint_frontier_edges_by_step_shards/part-*.csv.gz
```

The logical coupled raw artifacts remain
`coupled_joint_frontier_nodes_by_horizon.csv` and
`coupled_joint_frontier_edges_by_step.csv`.

The coupled runner also has an optional audit mode:

```text
--raw-topology-output-mode lossless_blocks
```

This stores exact repeated-horizon raw topology blocks with interval metadata
and marks the logical node/edge artifacts as `lossless_compressed`. It must stay
optional unless a run demonstrates real compression benefit. The H32 pair2 audit
found no exact repeated topology, so sharded remains the default coupled output
mode.

For heavy coupled runs, especially H128 breadth, use worker-side spooling:

```text
--raw-topology-output-mode worker_spool
```

In this mode each worker writes its own pair-local artifacts:

```text
coupled_pair_spool/<pair_id>/coupled_joint_frontier_nodes_by_horizon.csv.gz
coupled_pair_spool/<pair_id>/coupled_joint_frontier_edges_by_step.csv.gz
coupled_pair_spool/<pair_id>/coupled_joint_frontier_profile_by_horizon.csv.gz
coupled_pair_spool/<pair_id>/coupled_reconstruction_audit_summary.csv.gz
coupled_pair_spool/<pair_id>/coupled_artifact_completeness_summary.csv.gz
coupled_pair_spool/<pair_id>/pair_spool_manifest.json
```

The parent process receives only pair-local descriptors, then merges compact
summaries and spool manifests. This avoids returning large raw topology payloads
through Windows multiprocessing IPC. Logical artifact identity remains
`coupled_joint_frontier_nodes_by_horizon.csv` and
`coupled_joint_frontier_edges_by_step.csv`; `worker_spool` is a physical
storage and process-isolation layout.

Default transport retention is selected rather than full closure:

```text
--transport-output-mode selected_multiscale
--composition-residual-mode selected
```

This retains adjacent transport, selected milestone multiscale transport, and
selected consecutive-milestone composition residuals. Use
`--transport-output-mode full --composition-residual-mode full` only for
targeted audits. Use `--transport-output-mode adjacent_only
--composition-residual-mode none` for fast raw-topology calibration.

### 8.1 Manifest

`future_field_atlas_manifest.json`

Should include:

```text
instrument_version
artifact_schema_version
runner_version
protocol_version
runner_module
run_status
rebuild_contract
started_utc
completed_utc
seed_policy
csv_output_mode
gzip_compresslevel
raw_topology_output_mode
transport_output_mode
composition_residual_mode
multiscale_transport_pair_count
composition_residual_triple_count
artifact_write_workers
raw_topology_shard_scan_count or raw_topology_shard_pair_count
finalization_timings_json
substrate_count
frontier_count
horizon_schedule
output_files
claim_boundary
```

`future_field_atlas_rebuild_contract.json`

One row-equivalent JSON object describing whether discarded raw data can be
regenerated from retained metadata and source state.

Required fields:

```text
rebuild_contract_version
rebuild_status: exact_rebuild_supported | logical_rebuild_only
raw_data_retention
instrument_version
artifact_schema_version
runner_version
protocol_version
runner_module
command_line
python_executable
python_version
platform
config_digest
git.source_commit
git.source_branch
git.source_dirty
dependency_versions
exact_rebuild_requirements
raw_discard_policy
```

`exact_rebuild_supported` requires a source commit and clean worktree at run
start. `logical_rebuild_only` is still acceptable for exploratory/calibration
runs, but raw topology deletion should then be treated as a practical
verification downgrade.

`formal_spec_manifest.csv`

One row per formal spec object needed to reconstruct a scan.

Required columns:

```text
spec_type
spec_id
spec_digest
params_json
canonical_json
```

`condition_identity_manifest.csv`

One row per scan condition, tying runtime condition identity to formal specs.

Required columns:

```text
condition_id
group_id
seed
seed_policy
substrate_id
state_space_id
state_space_digest
law_id
law_digest
selection_operator_id
selection_operator_digest
observable_set_id
observable_digest
frontier_scan_id
frontier_scan_digest
condition_identity_digest
condition_identity_json
```

`scan_manifest.csv`

One row per scan/start-state instance. High-volume raw topology rows should
refer to this manifest instead of repeating full formal spec metadata.

Required columns:

```text
scan_id
condition_id
group_id
seed
seed_policy
substrate_id
start_index
start_state_id
state_space_id
state_space_digest
law_id
law_digest
selection_operator_id
selection_operator_digest
observable_set_id
observable_digest
frontier_scan_id
frontier_scan_digest
```

### 8.2 Run config

`future_field_atlas_run_config.json`

Should include all CLI arguments and derived defaults.

### 8.3 Frontier nodes

`frontier_nodes_by_horizon.csv`

One row per state occurrence in a frontier.

Required columns:

```text
scan_id
condition_id
frontier_scan_id
start_index
horizon
state_id
state_payload_hash
frontier_membership_weight
first_seen_horizon
incoming_inside_rank_boundary_flag
incoming_outside_rank_boundary_flag
component_id
```

If full state payloads are too large, emit hashes and a separate optional sampled payload file.

### 8.4 Frontier edges

`frontier_edges_by_step.csv`

One row per observed transition between adjacent frontier layers.

Required columns:

```text
scan_id
condition_id
frontier_scan_id
start_index
source_horizon
target_horizon
source_state_id
target_state_id
edge_weight
candidate_rank
candidate_energy
selected_flag
inside_rank_boundary_flag
outside_rank_boundary_flag
rank_offset_from_boundary
perturbation_changed_flag
reference_selected_flag
```

### 8.5 Frontier profile

`frontier_profile_by_horizon.csv`

One row per scan / horizon.

Required columns:

```text
scan_id
condition_id
horizon
frontier_state_count
frontier_edge_count
frontier_component_count
largest_component_fraction
frontier_entropy
inside_rank_boundary_state_count
outside_rank_boundary_state_count
inside_rank_boundary_edge_count
outside_rank_boundary_edge_count
inside_outside_rank_boundary_ratio
new_state_count
extinct_state_count
returning_state_count
```

### 8.6 Membership time series

`frontier_membership_timeseries.csv`

One row per tracked state across horizon, or compressed sparse encoding if needed.

Required columns:

```text
scan_id
condition_id
state_id
first_seen_horizon
last_seen_horizon
horizon_presence_bitset_or_sparse_list
inside_rank_boundary_presence_count
outside_rank_boundary_presence_count
```

### 8.7 Rank-boundary geometry by horizon

`rank_boundary_geometry_by_horizon.csv`

Required columns:

```text
scan_id
condition_id
horizon
base_out_degree
effective_out_degree
rank_boundary_k
inside_rank_boundary_edge_count
outside_rank_boundary_edge_count
rank_boundary_edge_count
weakest_inside_rank_boundary_energy
strongest_outside_rank_boundary_energy
rank_boundary_energy_gap
selected_inside_rank_boundary_fraction
selected_outside_rank_boundary_fraction
```

### 8.8 Adjacent transport matrices

`raw_transport_matrices_adjacent.npz`

Transport matrices for adjacent or dense horizon steps.

Required companion manifest:

`raw_transport_matrices_adjacent_manifest.csv`

Required manifest columns:

```text
matrix_id
scan_id
condition_id
source_horizon
target_horizon
row_item_count
column_item_count
nonzero_count
matrix_value_semantics
matrix_value_total
dropped_entry_count_due_to_artifact_policy
```

### 8.9 Multiscale transport matrices

`raw_transport_matrices_multiscale.npz`

Derived multiscale matrices compatible with prior H128 pairs.

Required companion manifest:

`raw_transport_matrices_multiscale_manifest.csv`

### 8.10 Flow compositionality residuals

`transport_flow_composition_residuals.csv`

For horizons `a < b < c`, compare direct and composed transport.

Required columns:

```text
scan_id
condition_id
source_horizon
mid_horizon
target_horizon
direct_matrix_id
left_matrix_id
right_matrix_id
composition_status
composition_kind
composition_alignment_policy
support_composition_status
support_composition_residual_l1
support_composition_residual_frobenius
support_composition_residual_fraction
support_rank_direct
support_rank_composed
path_count_composition_status
path_count_composition_residual_l1
path_count_composition_residual_frobenius
path_count_composition_residual_fraction
path_count_rank_direct
path_count_rank_composed
weighted_mass_composition_status
weighted_mass_composition_residual_l1
weighted_mass_composition_residual_frobenius
weighted_mass_composition_residual_fraction
```

This is a primary atlas feature, not a label.

`composition_status` and the per-kind status fields must use explicit
mathematical semantics:

```text
ok
label_mismatch
projection_required
not_comparable
```

Zero residual means actual agreement. It must not mean a skipped comparison.

### 8.11 Reconstruction and completeness audits

`reconstruction_audit_summary.csv`

Required audits:

```text
condition_identity_traceability
frontier_profile_reconstructs_from_node_and_edge_rows
rank_boundary_geometry_reconstructs_from_edge_rows
adjacent_transport_matrices_reconstruct_from_edge_rows
selection_operator_geometry_reconstructs_from_rank_boundary_rows
```

`artifact_completeness_summary.csv`

Every topology-derived artifact must carry or inherit one of:

```text
complete
lossless_compressed
sampled
truncated_noninterpretable
```

No downstream topology feature may masquerade as complete if it came from
sampled or truncated topology.

## 9. Phase 1 calibration outputs

The operator-native calibration pass should additionally emit:

```text
selection_operator_geometry_summary.csv
rank_boundary_geometry_by_horizon_summary.csv
rank_boundary_geometry_by_horizon_pair.csv
```

The primary artifact uses continuous operator and rank-boundary geometry metrics
rather than boolean recovery labels. Do not emit historical recovery aliases in
the clean runtime path.

Required recovery comparisons:

```text
rank_prefix:m=3
rank_prefix:m=4
rank_prefix:m=5
rank_subset:m=4:retain=1|2|3:remove=4
rank_subset:m=5:retain=1|2|3:remove=4|5
stochastic_rank_subset controls if cheap
```

Calibration criterion for instrument smoke:

```text
The raw topology features distinguish selected operators by rank-boundary
geometry without relying on response labels.
```

Failure criterion:

```text
If raw topology features cannot distinguish the calibration pattern,
repair the scanner/mapper before building coupled-frontier scan.
```

## 10. Coupled-frontier phase outputs

Do not implement Phase 2 until Phase 0/1 pass, unless explicitly requested.

When implemented, mandatory primary outputs are:

```text
A_frontier_profile_by_horizon.csv
B_frontier_profile_by_horizon.csv
joint_frontier_profile_by_horizon.csv
joint_vs_product_residual_by_horizon.csv
cross_perturbation_A_to_B_by_horizon.csv
cross_perturbation_B_to_A_by_horizon.csv
marginal_retention_by_horizon.csv
joint_rank_boundary_geometry_by_horizon.csv
```

Coupled phase must include product baselines.

Required raw coupled features:

```text
A_marginal_retention
B_marginal_retention
joint_support_count
product_expected_support_count
joint_minus_product_support
joint_vs_product_residual
A_to_B_cross_perturbation_delta
B_to_A_cross_perturbation_delta
A_inside_rank_boundary_retention
B_inside_rank_boundary_retention
joint_inside_rank_boundary_retention
A_outside_rank_boundary_loss
B_outside_rank_boundary_loss
```

Candidate labels are secondary only.

## 11. Nulls and controls

The atlas must preserve the prior discipline around controls, but raw data should come first.

Required gates for all phases:

```text
paired baseline availability
matched marginal nulls
fixture contract
error manifest
run manifest
no holdout
```

Null outputs should include raw anatomy, not only pass/fail flags.

## 12. Label policy

The atlas may emit labels only after raw artifacts are written.

Rules:

```text
1. Labels are optional convenience outputs.
2. Every label must be reconstructible from raw columns.
3. Labels must be downstream of scanner and mapper outputs.
4. Labels must not drive artifact retention.
5. Labels must not use Omega / agency / value language.
```

Preferred optional label files:

```text
candidate_feature_summary.csv
candidate_pattern_label_summary.csv
```

Avoid building a large new taxonomy in Phase 0/1.

## 13. CLI sketch

Initial runner options:

```text
--out
--groups
--design-groups
--fresh-seeds-per-group
--start-samples-list
--horizon-max
--horizon-schedule
--substrate-families
--macro-invariant-kind
--macro-invariant-beta-list
--frontier-scan-mode
--rank-boundary-k
--selection-operators
--raw-state-payload-sample-limit
--max-frontier-nodes-per-horizon
--max-frontier-edges-per-step
--workers
--fixture-smoke
```

Suggested defaults for first smoke:

```text
horizon_max: 128
horizon_schedule: dense_to_32_plus_h128
macro_invariant_kind: symbol_histogram_distance
rank_boundary_k: 3
selection_operators: rank_prefix:m=3,rank_prefix:m=4,rank_prefix:m=5,rank_subset:m=4:retain=1|2|3:remove=4,rank_subset:m=5:retain=1|2|3:remove=4|5
```

## 14. Implementation notes

Prefer a new package:

```text
omega/future_field_atlas/
```

Suggested modules:

```text
__init__.py
contracts.py
scanner.py
mapper.py
transport.py
controls.py
schemas.py
run_future_field_atlas.py
```

Do not import the old heavy runner into the core scanner. Reuse small substrate-generation utilities only where they are clean and auditable.

Default CSV storage should stay gzip:

```powershell
.\.venv\Scripts\python.exe -m omega.future_field_atlas.run_future_field_atlas `
  --out results\future_field_atlas\<run_id> `
  --workers 18
```

Only override it when needed:

```powershell
--csv-output-mode plain
--csv-output-mode both
--raw-topology-output-mode consolidated
--raw-topology-output-mode both
--transport-output-mode adjacent_only
--composition-residual-mode none
--transport-output-mode full
--composition-residual-mode full
```

The current default gzip compression level is `1`. This trades a modest amount
of compressed size for materially faster artifact writing while retaining
lossless CSV semantics.

## 15. Stop conditions

Stop and repair if:

```text
raw frontier artifacts are not sufficient to reconstruct derived summaries;
labels are needed to decide whether Phase 1 recovered the rank-boundary calibration pattern;
frontier truncation hides rank-boundary or topology structure;
matched nulls cannot be computed from raw artifacts;
run output is dominated by response-class tables;
Phase 2 coupled-frontier implementation begins before Phase 1 scanner recovery passes.
```

## 16. Handoff target for Codex

Build the Phase 0/1 instrument smoke first.

Minimal Codex task:

```text
Create `omega.future_field_atlas` with a runner that scans single-frontier topology,
writes raw frontier node/edge/profile/rank-boundary artifacts, and demonstrates
rank-boundary calibration recovery without using response labels.
```

Do not implement coupled-frontier interaction until the atlas artifacts are adequate.

## 17. Success statement

The instrument build succeeds when we can say:

```text
Future Field Atlas scans lawful frontier evolution, preserves the topology needed
for downstream mapping, and expresses calibration patterns as continuous
operator and rank-boundary geometry rather than response labels.
```

At that point, coupled future-field scanning can be specced or implemented as the next phase.

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
The instrument emitted raw frontier, transition, core/fringe, and transport-flow artifacts.
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
core/fringe rule
perturbation rule
raw topology emitted
feature maps derived
```

### Minimal

Do not rebuild the full empirical program. Keep the first implementation narrow enough to audit:

```text
single-frontier scanner smoke
known-mechanism recovery from raw topology
then coupled-frontier scan
```

Do not add rich semantic labels, agents, values, or boundary ontology.

### Revelatory

The instrument should reveal topology, not force-fit a response class.

Primary questions:

```text
What frontier shape emerges over horizon?
Where do boundaries, cores, fringes, bottlenecks, splits, merges, and corridors appear?
How does perturbation deform the topology?
Can known relation-geometry signals be recovered without response labels?
How do two future fields later compose, interfere, capture, erase, or support each other?
```

## 3. Architectural separation

The instrument must separate four layers.

### 3.0 Operator-native condition identity

Implementation should treat human-readable treatment names as aliases, not
condition primitives. Native condition identity should be expressed through:

```text
StateSpaceSpec
TransformationLawSpec
SelectionOperatorSpec
ObservableSpec
```

For rank-based calibration, the selection operator should record:

```text
selection_operator_id
selection_operator_family
base_out_degree
effective_out_degree
core_rank_k
retained_rank_set
removed_rank_set
stochastic_flag
seed_policy
selection_operator_params_json
```

Legacy labels such as `baseline_m3` or `drop_weakest_m4_to_core3` may remain in
manifests as `human_label` or `legacy_boundary_control_alias`, but they should
not be the primary mathematical identity of a condition.

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
core retention
fringe retention
transport mass
transport concentration
composition residual
```

### 3.3 Analyzer

Compares maps across baselines, perturbations, product controls, and coupled runs.

Examples:

```text
baseline vs perturbation raw difference
joint vs product residual
cross-perturbation effect
core/fringe deformation
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

### Phase 1: known-mechanism recovery

Goal: recover the known fixed low-rank core boundary pattern from raw topology.

Calibration target from prior branch:

```text
primary invariant:
  symbol_histogram_distance

live mechanism:
  fixed low-rank successor core / core-fringe boundary pressure

known response-bearing condition:
  retained top-3 low-energy successor core
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
substrate_family
substrate_variant
state_space_descriptor
start_state_id
seed
transformation_rule_id
frontier_expansion_rule_id
core_fringe_rule_id
horizon_schedule_id
perturbation_family
perturbation_strength
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

## 7. Core/fringe boundary contract

The first calibration target should preserve the known low-rank core boundary primitive.

For each source state and candidate successor set, record edge rank information:

```text
source_state_id
target_state_id
candidate_rank
candidate_energy
selected_flag
rank_offset_from_core_boundary
selection_operator_id
selection_operator_family
base_out_degree
effective_out_degree
retained_rank_set
removed_rank_set
```

Default calibration rule:

```text
core = retained top-3 low-energy successor set
fringe = candidate successors outside retained top-3 but near the selected boundary
```

Do not hard-code top-3 as theory. Treat it as the current calibration primitive.

## 8. Primary raw artifacts

These are mandatory for Phase 0 / Phase 1 unless explicitly marked optional.

### 8.1 Manifest

`future_field_atlas_manifest.json`

Should include:

```text
instrument_version
runner_module
run_status
started_utc
completed_utc
seed_policy
substrate_count
frontier_count
horizon_schedule
output_files
claim_boundary
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
substrate_id
condition_id
start_state_id
horizon
state_id
state_payload_hash
frontier_membership_weight
first_seen_horizon
core_membership_flag
fringe_membership_flag
component_id
```

If full state payloads are too large, emit hashes and a separate optional sampled payload file.

### 8.4 Frontier edges

`frontier_edges_by_step.csv`

One row per observed transition between adjacent frontier layers.

Required columns:

```text
scan_id
substrate_id
condition_id
source_horizon
target_horizon
source_state_id
target_state_id
edge_weight
candidate_rank
candidate_energy
selected_flag
core_flag
fringe_flag
perturbation_changed_flag
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
core_state_count
fringe_state_count
core_edge_count
fringe_edge_count
core_fringe_ratio
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
core_presence_count
fringe_presence_count
```

### 8.7 Core/fringe boundary by horizon

`core_fringe_boundary_by_horizon.csv`

Required columns:

```text
scan_id
condition_id
horizon
base_m
effective_m
core_edge_count
fringe_edge_count
boundary_edge_count
weakest_core_energy_mean
strongest_fringe_energy_mean
core_fringe_energy_gap_mean
core_retention_fraction_vs_baseline
fringe_retention_fraction_vs_baseline
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
transport_mass_total
retained_transport_mass
dropped_transport_mass
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
support_composition_residual_l1
support_composition_residual_frobenius
support_composition_residual_mass_fraction
support_rank_direct
support_rank_composed
path_count_composition_residual_l1
path_count_composition_residual_frobenius
path_count_composition_residual_mass_fraction
path_count_rank_direct
path_count_rank_composed
```

This is a primary atlas feature, not a label.

## 9. Phase 1 recovery outputs

The operator-native calibration pass should additionally emit:

```text
target_rank_core_distance_summary.csv
rank_core_recovery_by_horizon.csv
boundary_recovery_by_horizon_pair.csv
```

`known_mechanism_recovery_summary.csv` may be retained as a compatibility alias
for early Phase 0/1 output, but the primary artifact should use continuous
rank-core distance metrics rather than boolean recovery labels.

Required recovery comparisons:

```text
baseline m=3
baseline m=4
baseline m=5
drop weakest from m=4 to retained top-3 core
drop two weakest from m=5 to retained top-3 core
random deletion controls if cheap
```

Success criterion for instrument smoke:

```text
The raw topology features distinguish retained top-3 low-rank core conditions
from baseline m=4/m=5 and random deletion controls without relying on response labels.
```

Failure criterion:

```text
If raw topology features cannot distinguish the known response-bearing mechanism,
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
joint_core_fringe_boundary_by_horizon.csv
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
A_core_retention
B_core_retention
joint_core_retention
A_fringe_loss
B_fringe_loss
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
--core-rank-k
--selection-operators
--boundary-controls  # legacy alias for calibration presets
--perturbation-families
--perturbation-strengths
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
core_rank_k: 3
selection_operators: rank_prefix_m3,rank_prefix_m4,rank_prefix_m5,rank_subset_m4_keep_1_2_3,rank_subset_m5_keep_1_2_3
perturbation_families: small_edge_resample_control,asymmetric_edge_flip_control
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

## 15. Stop conditions

Stop and repair if:

```text
raw frontier artifacts are not sufficient to reconstruct derived summaries;
labels are needed to decide whether Phase 1 recovered the known mechanism;
frontier truncation hides core/fringe structure;
matched nulls cannot be computed from raw artifacts;
run output is dominated by response-class tables;
Phase 2 coupled-frontier implementation begins before Phase 1 scanner recovery passes.
```

## 16. Handoff target for Codex

Build the Phase 0/1 instrument smoke first.

Minimal Codex task:

```text
Create `omega.future_field_atlas` with a runner that scans single-frontier topology,
writes raw frontier node/edge/profile/core-fringe artifacts, and demonstrates known-mechanism
recovery for retained top-3 low-rank successor-core boundary pressure without using response labels.
```

Do not implement coupled-frontier interaction until the atlas artifacts are adequate.

## 17. Success statement

The instrument build succeeds when we can say:

```text
Future Field Atlas scans lawful frontier evolution, preserves the topology needed
for downstream mapping, and recovers the known low-rank-core boundary signal from
raw geometry rather than response labels.
```

At that point, coupled future-field scanning can be specced or implemented as the next phase.

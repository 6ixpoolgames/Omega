# RFS-MB0 Stage B-2 Laptop Spectral Control and Mapping Smoke Spec

Status: laptop-safe implementation spec / small-smoke calibration  
Scope: next sequential smoke for spectral controls, high-loading item export, item-to-edge mapping, and optional tiny perturbation  
Claim boundary: no holdout, no candidate promotion, no Omega detection, no agent detection, no identity detection, no valuer detection

Implementation addendum, 2026-05-30:

```text
This spec is binding with these guardrails:

1. retained result notes must begin with a short human-readable executive summary;
2. generated CSV/JSON run artifacts are local-only and must not be committed unless explicitly promoted by a maintainer;
3. the runner must hard-gate missing Phase B / Stage A control-summary inputs before launching jobs;
4. shuffled-control pass/fail must be reported by shuffle family, not only as one aggregate status;
5. high-loading selection and high-loading ablation evaluation must use separate deterministic partitions where feasible.
6. readiness must be split into spectral-control, analysis-only channel, tiny graph-channel, and larger graph-channel levels;
7. same-sample high-loading ablation is exploratory only and cannot support readiness;
8. high-loading ablation specificity must be quantitative, matched-random controlled, and multi-metric;
9. subspace transfer must be reported separately from item-local ablation specificity.
10. compact audit fields must use external-review names directly, not only internal aliases.
11. label-shuffle controls are label-interpretation controls; context and horizon shuffles are the required structure-destroying controls.
12. shuffle failures must be anatomized by matrix/probe/flow/horizon/condition before proposing graph perturbations.
13. coflow subspace distributedness and transfer against explicit subspace controls must be reported before choosing the next fork.
```

## 0. Purpose

Run a laptop-safe smoke to answer:

```text
Can the repaired spectral runner produce shuffled spectral controls,
export high-loading coflow items,
and map those items back to realized edge structures well enough
to justify a later targeted channel-edge perturbation run?
```

This is not the 24-hour run.  
This is not a full channel-edge sensitivity run.  
This is not a spectral migration pass.

## 1. Background

The Stage B-2 exploratory iteration pass produced weak but non-null topology-sensitive residues:

```text
SYN_A:
  edge_roughening_sensitive_syndrome

SYN_C:
  edge_roughening_sensitive_syndrome

SYN_B/SYN_D:
  measurable but no resolved residual
```

The spectral future-field geometry smoke produced well-covered cofrontier/coflow matrices and found that the strongest direct-control spectral signal was in coflow under topology-level controls.

However, the first spectral smoke did not complete the missing spectral controls:

```text
label-shuffled controls
context-shuffled controls
horizon-order shuffled controls
frontier-size/support-size matched controls
probe-marginal controls
```

This laptop smoke should sharpen the instrument before any larger desktop or long unsupervised run.

## 2. Claim boundary

Allowed claims:

```text
spectral shuffled controls work or fail;
high-loading coflow item export works or fails;
item-to-edge mapping has adequate or inadequate coverage;
analysis-only high-loading ablation is specific or random-equivalent;
tiny targeted-vs-random perturbation is ready or blocked.
```

Forbidden claims:

```text
Omega detected;
agent detected;
identity detected;
valuer detected;
gauge-coherent shadow validated;
future-shaping source identified;
candidate promoted;
holdout ready.
```

Required counters:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

Artifact policy:

```text
All generated CSV/JSON outputs from this smoke are local run artifacts.
Default output root:
  results/local_runs/

Do not commit generated smoke CSVs, status JSONs, manifests, or raw matrix
tables to Git. Commit only code changes, spec/addendum changes, and compact
retained result notes under docs/research_notes/validation_results/ when a run
is worth retaining.
```

## 3. Laptop profile

Use laptop settings only:

```text
workers: 7
job_batch_size: 2
thread caps:
  OMP_NUM_THREADS=1
  OPENBLAS_NUM_THREADS=1
  MKL_NUM_THREADS=1
  NUMEXPR_NUM_THREADS=1
  NUMBA_NUM_THREADS=1
```

Suggested wall clock:

```text
target_runtime: 45 to 90 minutes
max_runtime_seconds: 7200
shutdown_cushion_seconds: 900
```

If the smoke is still running inside the shutdown cushion, stop launching new work and finalize partial outputs.

## 4. Minimal run shape

Suggested defaults:

```text
design_groups: 1
fresh_seeds_per_group: 1
start_samples_list: 4
```

Primary syndromes:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag
SYN_C_low_growth_high_concentration_low_entropy
```

Secondary syndromes:

```text
Skip by default.
Include SYN_B/SYN_D only if cheap.
```

Probes:

```text
constraint_profile_hash
constraint_violation_count_plus_local_tuple
```

Matrix families:

```text
coflow:
  primary

cofrontier:
  diagnostic only
```

Flow modes:

```text
one_step_local_flow
constrained_window_flow
```

Horizon bands:

```text
short
middle
downstream
```

Primary condition families:

```text
baseline_unperturbed
small_edge_resample_control:p0.02
asymmetric_edge_flip_control:p0.02
```

Optional if cheap:

```text
small_edge_resample_control:p0.01
asymmetric_edge_flip_control:p0.01
```

Do not run broad mechanism ladders in this smoke.

## 5. Stage order

Run stages sequentially.

Do not proceed if a gate fails.

### Stage 0: output contract and decision-class smoke

Purpose:

```text
Make sure the runner emits clean files, does not overstate the spectral decision,
and supports graceful exit.
```

Required repairs/checks:

```text
split decision classes:
  spectral_matrix_coverage_passed
  spectral_direct_topology_sensitivity_present
  spectral_controls_incomplete
  spectral_migration_criteria_not_yet_met
  spectral_future_geometry_above_full_controls
```

Required files:

```text
laptop_spectral_smoke_run_config.json
laptop_spectral_smoke_status.json
laptop_spectral_smoke_progress_checkpoints.csv
laptop_spectral_smoke_errors.csv
laptop_spectral_smoke_output_manifest.json
laptop_spectral_output_contract_report.md
laptop_gpt_requested_status_key_fields.csv
laptop_mapping_status_counts.csv
laptop_spectral_forwarding_summary.md
```

Gate:

```text
status.json exists;
errors.csv exists even if empty;
output_manifest exists;
decision class does not imply full spectral migration;
claim-boundary counters are present.
```

Additional input gate:

```text
control_summary_cache_status must not be missing_source;
phase_b_stage_a_control_values.csv or phase_b_design_control_rows.csv must be present;
if the control source is missing, emit PARTIAL_CONTROL_SOURCE_MISSING,
write the contract/status/manifest/error/report files, and stop before launching jobs.
```

If this fails, stop and repair runner plumbing.

### Stage 1: cheap spectral shuffled-control smoke

Purpose:

```text
Test whether the coflow structure survives the easiest missing spectral nulls.
```

Required controls:

```text
label_shuffled_spectral_replicates
context_shuffled_spectral_replicates
horizon_order_shuffled_spectral_replicates
```

Replicates:

```text
minimum: 3
preferred: 5 if cheap
```

Outputs:

```text
laptop_label_shuffle_spectral_smoke.csv
laptop_context_shuffle_spectral_smoke.csv
laptop_horizon_shuffle_spectral_smoke.csv
laptop_spectral_shuffle_control_summary.csv
laptop_spectral_shuffle_family_gate_summary.csv
laptop_spectral_shuffle_failure_anatomy.csv
laptop_spectral_shuffle_control_report.md
```

Required fields:

```text
matrix_id
matrix_family
condition_id
probe_key
flow_mode
horizon_band
shuffle_type
replicate_id
observed_positive_spectral_mass
shuffle_positive_spectral_mass
observed_effective_rank
shuffle_effective_rank
observed_topk_alignment
shuffle_topk_alignment
observed_percentile_vs_shuffle
```

Default family thresholds:

```text
label_shuffle:
  observed_percentile_vs_shuffle >= 0.80
  category: label_interpretation_control
  required_for_structure_gate: false

context_shuffle:
  observed_percentile_vs_shuffle >= 0.80
  category: structure_destroying_control
  required_for_structure_gate: true

horizon_order_shuffle:
  observed_percentile_vs_shuffle >= 0.80
  category: structure_destroying_control
  required_for_structure_gate: true

label shuffle is reported for interpretive sanity but must not be treated as
equivalent to structure-destroying context or horizon shuffles.
```

The report must show a row per shuffle family:

```text
shuffle_family
shuffle_control_category
family_required_for_control_gate
threshold
replicate_count
primary_context_count
passed_context_count
pass_fraction
median_observed_percentile
min_observed_percentile
catastrophic_floor
catastrophic_fail_count
catastrophic_fail_flag
family_passed
blocking_reason
```

Laptop family pass rule:

```text
family passes if:
  pass_fraction >= 0.50
  median_observed_percentile >= 0.80
  catastrophic_fail_count == 0

overall shuffle smoke passes if:
  context_shuffle passes
  horizon_order_shuffle passes
  no required structure-destroying family has a primary context below the catastrophic floor

label_shuffle failure does not by itself block the structure gate, but it must
remain visible as a label-interpretation warning.
```

Failure anatomy output:

```text
laptop_spectral_shuffle_failure_anatomy.csv
```

Required anatomy fields:

```text
matrix_id
matrix_family
condition_id
probe_key
flow_mode
horizon_band
shuffle_family
shuffle_control_category
family_required_for_control_gate
observed_percentile_vs_shuffle
matrix_shuffle_passed
catastrophic_fail_flag
item_count
coverage
positive_spectral_mass
effective_rank
blocking_reason
```

Gate:

```text
all three shuffle types complete;
observed coflow matrices are compared to shuffle distributions;
percentile/rank versus shuffle controls is emitted;
controls do not overwrite direct-control summaries.
```

If fewer than two shuffle families pass the family threshold, stop and recommend spectral-control repair or measurement-limits note.

### Stage 2: high-loading coflow item export

Purpose:

```text
Export the spectral items that would later guide targeted channel-edge sensitivity.
```

Use coflow only for the primary smoke.

Selection:

```text
select high-loading coflow items from top positive spectral modes;
top_k_items: 16 by default;
optional top_k_items: 32 if cheap;
min_item_count: 2 or higher;
exclude diagnostic probes from positive interpretation.
```

Default loading score:

```text
loading_i = sum over top positive modes of eigenvalue * eigenvector_i^2
```

If SVD is used, replace eigenvalue/eigenvector with singular value and singular vector.

Outputs:

```text
laptop_spectral_high_loading_items.csv
laptop_spectral_item_loading_summary.csv
laptop_spectral_item_vocab_manifest.csv
laptop_spectral_high_loading_export_report.md
```

Required fields:

```text
spectral_item_id
matrix_id
matrix_family
condition_id
probe_key
flow_mode
horizon_band
signature_transition
loading_score
mode_index
item_count
item_mass
loading_rank
selection_status
```

Gate:

```text
high-loading items are exported for coflow middle horizon;
items include both primary probes if available;
item counts and item mass are reported;
selection does not use syndrome labels.
```

If export fails, stop and repair item manifest or mode export.

### Stage 3: item-to-edge mapping smoke

Purpose:

```text
Determine whether high-loading signature transitions can be mapped back to realized state-level edges.
```

For each selected item:

```text
signature transition:
  left_signature -> right_signature

map to realized edge:
  source_state -> target_state
  probe(source_state) = left_signature
  probe(target_state) = right_signature
  edge participates in the relevant frontier-transform context
```

Outputs:

```text
laptop_spectral_item_to_edge_mapping.csv
laptop_spectral_mapping_coverage.csv
laptop_spectral_mapping_report.md
```

Required fields:

```text
spectral_item_id
signature_transition
matrix_id
probe_key
flow_mode
horizon_band
condition_id
loading_score
item_count
item_mass
realized_edge_count
mapped_realized_edge_count
realized_edge_sample_json
mapped_item_mass
mapping_status
```

Mapping statuses:

```text
mapped_to_realized_edges
mapped_to_signature_transition_only
insufficient_context_to_map
mapping_failed
```

Gate:

```text
mapped_item_fraction reported;
mapped_item_mass_fraction reported;
mapping coverage adequate for at least one tiny targeted perturbation later.
```

Minimum to proceed later:

```text
mapped_item_mass_fraction >= 0.30
```

Preferred:

```text
mapped_item_mass_fraction >= 0.50
```

If mapping coverage is below 0.30, do not run graph-level perturbation. Recommend context export repair or signature-transition-only analysis.

### Stage 4: analysis-only high-loading ablation smoke

Purpose:

```text
Before changing the graph, test whether high-loading items carry spectral structure more than matched random items.
```

Method:

```text
remove or downweight high-loading coflow items in matrix/count analysis;
compare to matched random item removal;
optionally compare to low-loading item removal.
```

Selection/evaluation split:

```text
High-loading item selection must use a deterministic selection partition.
Ablation evaluation must use a separate deterministic evaluation partition.

Default:
  partition_rule: stable hash of context_id
  selection_partition_fraction: 0.50
  partition_seed: recorded in status/config/report

If the evaluation partition has insufficient contexts, emit
selection_evaluation_split_insufficient and stop before claiming
high_loading_ablation_specific.

This split is not holdout Phase C. It is within-smoke anti-overfit hygiene.
```

Allowed interpretation:

```text
spectral dependence only;
not causal topology dependence.
```

Outputs:

```text
laptop_selection_evaluation_partition_summary.csv
laptop_subspace_transfer_diagnostic.csv
laptop_subspace_distributedness_diagnostic.csv
laptop_subspace_control_alignment.csv
laptop_spectral_next_action_fork.csv
laptop_spectral_readiness_levels.csv
laptop_spectral_item_ablation_manifest.csv
laptop_high_loading_ablation_summary.csv
laptop_random_item_ablation_summary.csv
laptop_low_loading_ablation_summary.csv
laptop_item_ablation_decision.csv
laptop_item_ablation_report.md
```

Gate:

```text
same-sample ablation may only be reported as same_sample_ablation_exploratory;
selection/evaluation split must be available for readiness;
high_loading_delta > random_delta_max, or high_loading_delta >= random_delta_mean + 1.0 * random_delta_std;
the high-loading effect appears in at least 2 of:
  positive spectral mass;
  effective rank;
  participation/top-subspace proxy;
random matching quality is adequate;
coverage remains adequate after ablation;
result is not driven by one diagnostic probe.
```

If high-loading ablation is random-equivalent, single-metric-only, weakly matched,
or split-insufficient, stop. Do not run targeted graph perturbation next.

The decision row must explain the blocker with fields including:

```text
high_loading_delta
random_delta_mean
random_delta_std
random_delta_max
low_loading_delta
high_loading_minus_random_mean
high_loading_over_random_ratio
ablation_direction_match
coverage_loss_after_ablation
matching_quality
random_matching_quality
metric_specificity_wins
effect_metric_count
matched_random_drop_fraction_std
matched_random_drop_fraction_max
ablation_failure_reason
subspace_transfer_status
subspace_item_read
```

Subspace diagnostic:

```text
select top-k subspace on selection partition;
compare alignment to top-k subspace on evaluation partition;
report subspace_transfers, subspace_does_not_transfer, or subspace_transfer_not_computed.
```

Distributedness diagnostic:

```text
Measure whether the apparent object is item-local, cluster-local, distributed,
or diffuse/noise-like before deciding that item ablation failure closes the
spectral route.
```

Required distributedness fields:

```text
matrix_id
matrix_family
condition_id
probe_key
flow_mode
horizon_band
item_count
positive_spectral_mass
participation_ratio
top_item_mass_share
top_5_item_mass_share
top_20_item_mass_share
effective_contributing_items
loading_entropy
loading_entropy_fraction
distributedness_read
```

Allowed distributedness reads:

```text
item_local
cluster_local
distributed
diffuse_noise_like
```

Subspace control alignment:

```text
Compare selection/evaluation top-k subspace transfer against:
  context-shuffled evaluation subspace;
  horizon-shuffled evaluation subspace;
  random subspace baseline;
  label-shuffled mapping baseline.
```

Required subspace-control fields:

```text
matrix_id
matrix_family
condition_id
probe_key
flow_mode
horizon_band
control_family
control_category
actual_selection_evaluation_alignment
actual_alignment_status
control_alignment_mean
control_alignment_std
control_alignment_max
control_computed_replicates
subspace_transfer_above_control
subspace_control_read
control_statuses
```

Allowed subspace-control reads:

```text
subspace_transfer_above_controls
subspace_transfer_control_equivalent
subspace_control_alignment_not_computed
```

Next-action fork:

```text
The smoke must emit one explicit next-action fork so later theory work does not
quietly slide from a failed item-local channel into a graph perturbation claim.
```

Allowed forks:

```text
repair_shuffle_controls
run_item_ablation_repair
run_subspace_ablation_smoke
write_spectral_measurement_limits_note
prepare_graph_perturbation_spec
```

### Stage 5: optional tiny targeted-vs-random perturbation

Default:

```text
Do not run this unless Stages 1 through 4 pass and there is time remaining.
```

Purpose:

```text
Only prove implementability, not science.
```

Perturbation conditions:

```text
spectral_high_loading_targeted_edge_perturbation
matched_random_edge_perturbation
```

Strengths:

```text
p = 0.0025
p = 0.005 only if p0.0025 is non-destructive
```

Required matching fields where feasible:

```text
number of perturbed edges
source out-degree bin
target in-degree bin
probe_key
flow_mode
horizon_band
signature-transition frequency
baseline flow mass
```

Outputs:

```text
laptop_tiny_channel_perturbation_manifest.csv
laptop_tiny_channel_matching_quality.csv
laptop_tiny_channel_substrate_preservation.csv
laptop_tiny_channel_syndrome_rates.csv
laptop_tiny_channel_spectral_response.csv
laptop_tiny_channel_target_vs_random_summary.csv
laptop_tiny_channel_smoke_report.md
```

Gate:

```text
targeted and matched random perturbations both run;
substrate preservation is non-destructive or mildly destructive;
matching quality is reported;
A/C syndrome response and spectral response are emitted;
no interpretation relies on targeted-only comparison to baseline.
```

## 6. Stop rules

Stop immediately if:

```text
runner/output contract fails;
shuffle controls reproduce observed coflow structure;
high-loading item export fails;
item-to-edge mapping coverage is too low;
high-loading ablation is random-equivalent.
```

Do not push through to graph perturbation if a prior gate fails.

## 7. Decision classes

Allowed:

```text
laptop_output_contract_passed
laptop_output_contract_failed
spectral_shuffle_controls_passed
spectral_shuffle_controls_control_equivalent
high_loading_item_export_passed
high_loading_item_export_failed
item_to_edge_mapping_adequate
item_to_edge_mapping_insufficient
high_loading_ablation_specific
high_loading_ablation_random_equivalent
single_metric_ablation_hint
same_sample_ablation_exploratory
selection_evaluation_split_insufficient
random_matching_weak_underdetermined
subspace_transfers_but_items_not_specific
subspace_does_not_transfer
subspace_transfer_above_controls
subspace_transfer_control_equivalent
item_local
cluster_local
distributed
diffuse_noise_like
repair_shuffle_controls
run_item_ablation_repair
run_subspace_ablation_smoke
write_spectral_measurement_limits_note
prepare_graph_perturbation_spec
item_specific_and_subspace_transfers
tiny_targeted_random_perturbation_implemented
tiny_targeted_random_perturbation_not_interpretable
ready_for_larger_spectral_control_run
ready_for_larger_analysis_only_channel_run
ready_for_tiny_graph_channel_perturbation
ready_for_larger_graph_channel_run
PARTIAL_CONTROL_SOURCE_MISSING
not_ready_repair_required
```

Forbidden:

```text
Omega_positive
agent_detected
identity_detected
valuer_detected
gauge_shadow_validated
candidate_promoted
holdout_ready
```

## 8. Final report

Retain a result note:

```text
docs/research_notes/validation_results/rfs_mb0/rfs_mb0_laptop_spectral_control_mapping_smoke_result.md
```

Required sections:

```text
0. Executive summary
1. Claim boundary
2. Laptop runtime profile
3. Output contract smoke
4. Shuffled spectral controls
5. Shuffle failure anatomy
6. High-loading coflow item export
7. Item-to-edge mapping
8. Analysis-only ablation
9. Distributedness and subspace-control alignment
10. Optional tiny perturbation, if run
11. Readiness levels
12. Next-action fork and repairs required
13. Output manifest
```

The result note must explicitly answer:

```text
Which readiness levels, if any, are open?
If not, what exactly blocks it?
```

Executive summary must be readable without opening raw CSVs and must include:

```text
decision;
one-sentence interpretation;
blocking caveats;
next recommended action;
artifact policy: generated CSVs stayed local.
```

## 9. Graceful exit requirements

Runner must support:

```text
status.json at start;
periodic status.json updates;
progress checkpoint CSV;
SIGINT/SIGTERM handling;
shutdown cushion;
partial item export finalization;
partial mapping finalization;
partial ablation finalization;
partial perturbation finalization;
errors.csv;
output_manifest.json;
partial final report.
```

Required status fields:

```text
status
phase
started_utc
finished_utc
elapsed_seconds
max_runtime_seconds
shutdown_cushion_seconds
finalization_reason
jobs_requested
jobs_completed
shuffle_replicates_completed
high_loading_items_exported
item_sets_mapped
ablation_jobs_completed
perturbation_jobs_completed
errors
holdout_scoring_count
n6_run_count
alphabet_expansion_count
candidate_promotion_enabled
```

Allowed final statuses:

```text
COMPLETED
PARTIAL_CONTROL_SOURCE_MISSING
PARTIAL_TIME_LIMIT_REACHED
PARTIAL_INTERRUPTED
PARTIAL_SHUFFLE_CONTROLS_FAILED
PARTIAL_ITEM_EXPORT_FAILED
PARTIAL_MAPPING_INSUFFICIENT
PARTIAL_SELECTION_EVALUATION_SPLIT_INSUFFICIENT
PARTIAL_ABLATION_RANDOM_EQUIVALENT
PARTIAL_NO_INTERPRETABLE_PERTURBATIONS
FAILED_WITH_ERRORS
```

If partial, report which outputs are safe to interpret and which are exploratory-only.

## 10. Recommended command shape

Approximate laptop command shape:

```text
python -m omega.rfs_mb0_future_landscape.run_stage_b2_laptop_spectral_control_mapping_smoke \
  --out results/local_runs/20260529_laptop_spectral_control_mapping_smoke \
  --design-groups 1 \
  --fresh-seeds-per-group 1 \
  --start-samples-list 4 \
  --probes constraint_profile_hash,constraint_violation_count_plus_local_tuple \
  --matrix-families coflow \
  --include-cofrontier-diagnostic \
  --shuffle-replicates 3 \
  --top-k-items 16 \
  --workers 7 \
  --job-batch-size 2 \
  --max-runtime-seconds 7200 \
  --shutdown-cushion-seconds 900
```

If Codex extends the existing spectral runner rather than creating a new module, that is acceptable. The output contract and stage gates remain mandatory.

## 11. 3P check

### Principled

The smoke tests spectral structures derived from future-field relations, not semantic labels.

### Parsimonious

The smoke validates the smallest spectral-to-channel path before building a larger detector.

### Predictive

High-loading spectral structures must predict ablation or perturbation sensitivity better than matched random structures.

If they do not, the spectral path is not ready for a larger run.

## 12. Bottom line

This laptop smoke should not try to prove the channel hypothesis.

It should answer a narrow readiness ladder:

```text
Are larger spectral controls ready?
Are larger analysis-only channel diagnostics ready?
Is tiny graph-channel perturbation ready?
Is a larger graph-channel run ready?
```

Only the highest passed readiness level is justified.

If no, repair the instrument before spending desktop-scale time.

# RFS-MB0 Stage B-2 Spectral Subspace Control Repair Smoke Spec

Status: laptop-safe repair spec / spectral-control and subspace diagnostic  
Scope: next small smoke after laptop spectral control/mapping smoke v0.3.0  
Claim boundary: no holdout, no candidate promotion, no Omega detection, no agent detection, no identity detection, no valuer detection

## 0. Purpose

This smoke repairs the current spectral-control blocker and clarifies whether the live spectral object is:

```text
1. a real transferable coflow subspace above structure-destroying controls;
2. control-equivalent spectral geometry;
3. a distributed subspace that is not item-local;
4. a shuffle-gate/statistic mismatch;
5. too weak or diffuse to pursue.
```

This run is not a graph perturbation run.

It does not test agency, value, identity, or Omega.

## 1. Background

The laptop spectral control/mapping smoke v0.3.0 completed cleanly and validated the instrument plumbing:

```text
jobs_completed: 24 / 24
errors: 0
control_summary_cache_status: loaded
high_loading_items_exported: 40
item_sets_mapped: 5
best_mapped_item_mass_fraction: 1.000
```

But the scientific gates remained blocked:

```text
decision_class: not_ready_repair_required
blocking_reason: structure_shuffle_controls_not_passed
```

The required structure-destroying controls did not pass the current family gate:

```text
context_shuffle: failed
horizon_order_shuffle: passed
required structure families passed: 0 / 2 in the tiny contract smoke gate summary
```

Label shuffle is now correctly treated as a label-interpretation control, not as a structure-destroying control.

The ablation result also blocked graph perturbation:

```text
high_loading_ablation_random_equivalent
subspace_transfers_but_items_not_specific
```

The current live hypothesis is therefore:

```text
The useful spectral object, if present, may be a distributed coflow subspace
rather than a small set of high-loading channel items.
```

## 2. Key clarification: what a structure-destroying shuffle means

A structure-destroying shuffle is supposed to be ablative.

The question is not:

```text
Did the shuffle change or destroy structure?
```

It should.

The question is:

```text
Does the observed spectral structure separate from the structure-destroyed null
in the expected statistic, direction, and primary contexts?
```

A failed shuffle gate can mean several different things:

```text
true_control_equivalence:
  the observed spectral geometry is not stronger than the destroyed null

statistic_mismatch:
  the tested statistic is not the right statistic for this shuffle family

gate_too_coarse:
  the family-level gate hides matrix/probe/flow/horizon heterogeneity

primary_context_mismatch:
  the chosen primary contexts are too broad, too sparse, or not the live contexts

shuffle_semantics_mismatch:
  the shuffle does not destroy the intended structure or destroys more than intended
```

This smoke exists to disambiguate those cases.

## 3. Claim boundary

Allowed claims:

```text
structure-destroying shuffle controls separate or do not separate by matrix/probe/flow/horizon;
subspace transfer is above or equivalent to explicit subspace controls;
coflow spectral structure appears item-local, cluster-local, distributed, diffuse, or control-equivalent;
the next action is repair, subspace ablation, item-ablation repair, graph perturbation prep, or measurement-limits note.
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

## 4. Run posture

This is a laptop-safe diagnostic smoke.

Suggested defaults:

```text
workers: 7
job_batch_size: 2
design_groups: 1
fresh_seeds_per_group: 1
start_samples_list: 4
shuffle_replicates: 5 preferred, 3 minimum
max_runtime_seconds: 7200
shutdown_cushion_seconds: 900
```

Primary probes:

```text
constraint_profile_hash
constraint_violation_count_plus_local_tuple
```

Primary matrix family:

```text
coflow
```

Diagnostic matrix family:

```text
cofrontier
```

Primary horizon band:

```text
middle
```

Secondary horizon bands:

```text
short
downstream
```

Primary conditions:

```text
baseline_unperturbed
small_edge_resample_control:p0.02
asymmetric_edge_flip_control:p0.02
```

## 5. Stage 0: output contract

Required outputs:

```text
spectral_subspace_repair_run_config.json
spectral_subspace_repair_status.json
spectral_subspace_repair_progress_checkpoints.csv
spectral_subspace_repair_errors.csv
spectral_subspace_repair_output_manifest.json
spectral_subspace_repair_report.md
```

Acceptance gate:

```text
status and manifest present;
errors.csv present even if empty;
claim boundary counters present;
no generated CSV/JSON outputs are marked for commit;
final report begins with executive summary.
```

## 6. Stage 1: shuffle failure anatomy v2

Purpose:

```text
Explain why the structure-destroying shuffle gate failed.
```

Emit one row per matrix/context/shuffle family.

Required fields:

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
observed_statistic_name
observed_statistic_value
shuffle_mean
shuffle_std
shuffle_min
shuffle_max
observed_percentile_vs_shuffle
expected_direction
separation_margin
matrix_shuffle_passed
catastrophic_fail_flag
item_count
coverage
positive_spectral_mass
effective_rank
participation_ratio
blocking_reason
failure_interpretation
```

Allowed `failure_interpretation` values:

```text
true_control_equivalence
statistic_mismatch
gate_too_coarse
primary_context_mismatch
shuffle_semantics_mismatch
underpowered_replicates
insufficient_matrix_coverage
passed
```

### 6.1 Statistic families

For each shuffle family, test more than one statistic.

Required statistics:

```text
positive_spectral_mass
effective_rank
participation_ratio
top_k_subspace_alignment_to_baseline
selection_evaluation_subspace_alignment
```

Reason:

```text
A shuffle may destroy item identity, subspace transfer, or loading localization
without strongly changing positive spectral mass.
```

### 6.2 Control categories

Use separate interpretation categories:

```text
label_interpretation_control:
  label shuffle; not required to change eigenvalues / positive spectral mass

structure_destroying_control:
  context shuffle, horizon shuffle, within-context reassignment

presentation_control:
  probe or matrix presentation changes if implemented
```

Label shuffle should not be the primary blocker for spectral mass.

Context and horizon shuffles are the required structure-destroying controls for this smoke.

## 7. Stage 2: primary-context refinement

Purpose:

```text
Check whether shuffle failure is global or concentrated in a few contexts.
```

Emit summaries by:

```text
probe_key
flow_mode
condition_id
horizon_band
matrix_family
shuffle_family
```

Required outputs:

```text
spectral_shuffle_failure_by_probe.csv
spectral_shuffle_failure_by_flow_mode.csv
spectral_shuffle_failure_by_condition.csv
spectral_shuffle_failure_by_horizon.csv
spectral_shuffle_failure_by_matrix_family.csv
spectral_primary_context_recommendation.csv
```

The primary-context recommendation should classify contexts as:

```text
keep_primary
make_secondary
drop_for_now_due_to_control_equivalence
drop_for_now_due_to_undercoverage
needs_more_replicates
```

If a failure is concentrated in one probe/flow/horizon context, later smokes may narrow rather than abandon spectra.

If failures are global across primary contexts, the spectral-control layer is likely genuinely blocked.

## 8. Stage 3: subspace transfer against controls

Purpose:

```text
Test whether the transferred coflow subspace is above explicit subspace controls.
```

Required comparisons:

```text
selection -> evaluation actual alignment
selection -> context-shuffled evaluation alignment
selection -> horizon-shuffled evaluation alignment
selection -> random subspace baseline
selection -> label-shuffled mapping baseline
```

Required fields:

```text
matrix_id
matrix_family
condition_id
probe_key
flow_mode
horizon_band
actual_selection_evaluation_alignment
actual_alignment_status
control_family
control_category
control_alignment_mean
control_alignment_std
control_alignment_max
control_computed_replicates
alignment_margin_vs_control_mean
alignment_margin_vs_control_max
subspace_transfer_above_control
subspace_control_read
```

Allowed reads:

```text
subspace_transfer_above_controls
subspace_transfer_control_equivalent
subspace_transfer_underpowered
subspace_control_alignment_not_computed
```

Pass condition for subspace transfer:

```text
actual alignment > control max
```

or, with enough replicates:

```text
actual alignment >= control mean + 1.0 * control std
```

and no catastrophic structure-control failure in the same context.

## 9. Stage 4: distributedness diagnostic v2

Purpose:

```text
Determine whether the coflow spectral object is item-local, cluster-local,
distributed, diffuse/noise-like, or control-equivalent.
```

Required metrics:

```text
participation_ratio
top_item_mass_share
top_5_item_mass_share
top_20_item_mass_share
effective_contributing_items
loading_entropy
loading_entropy_fraction
subspace_transfer_status
subspace_control_read
item_ablation_specificity_status
```

Allowed reads:

```text
item_local
cluster_local
distributed
diffuse_noise_like
control_equivalent
underpowered
```

Interpretation rules:

```text
item_local:
  top item or tiny item set carries large mode mass and item ablation is specific

cluster_local:
  a moderate item cluster carries mode mass and cluster/subspace ablation is promising

distributed:
  participation is broad, subspace transfers above controls, item ablation not specific

diffuse_noise_like:
  broad participation but subspace is control-equivalent

control_equivalent:
  structure-destroying controls reproduce the same transfer/geometry
```

## 10. Stage 5: optional subspace-level ablation design smoke

Only run if:

```text
subspace_transfer_above_controls OR distributed read is plausible;
structure controls are not globally control-equivalent;
time remains.
```

Do not run graph perturbation.

Ablation variants:

```text
mode_support_ablation:
  remove/downweight items contributing cumulatively to top X percent of mode mass

spectral_cluster_ablation:
  cluster items in top-k spectral coordinates, ablate one cluster

stratified_subspace_ablation:
  ablate small fractions across high-contribution strata

matched_subspace_random_ablation:
  random controls matched on loading distribution and item mass
```

Outputs:

```text
spectral_subspace_ablation_design_manifest.csv
spectral_subspace_ablation_feasibility.csv
spectral_subspace_ablation_smoke_summary.csv
```

This stage is feasibility-only unless enough controls are available.

## 11. Decision classes

Allowed decision classes:

```text
structure_shuffle_controls_passed
structure_shuffle_controls_control_equivalent
shuffle_gate_statistic_mismatch
shuffle_gate_too_coarse
primary_context_refinement_needed
subspace_transfer_above_controls
subspace_transfer_control_equivalent
distributed_subspace_candidate
diffuse_noise_like_subspace
item_localization_not_supported
subspace_ablation_design_ready
not_ready_repair_required
measurement_limits_note_recommended
```

Forbidden decision classes:

```text
Omega_positive
agent_detected
identity_detected
valuer_detected
gauge_shadow_validated
future_shaping_source_identified
candidate_promoted
holdout_ready
```

## 12. Next-action fork

Emit exactly one next-action fork:

```text
repair_shuffle_controls
run_primary_context_narrowing_smoke
run_subspace_ablation_smoke
run_item_ablation_repair
write_spectral_measurement_limits_note
prepare_graph_perturbation_spec
```

Fork rules:

```text
repair_shuffle_controls:
  if structure-control failure is global or statistics are mismatched

run_primary_context_narrowing_smoke:
  if failures are concentrated in specific probe/flow/horizon contexts

run_subspace_ablation_smoke:
  if subspace transfer is above controls and distributed/cluster-local read is plausible

run_item_ablation_repair:
  only if item-local read is plausible but ablation matching was weak

write_spectral_measurement_limits_note:
  if subspace transfer and structure controls are control-equivalent

prepare_graph_perturbation_spec:
  only if subspace/item localization and controls both pass; unlikely for this smoke
```

## 13. Required final report

Retain a result note under:

```text
docs/research_notes/validation_results/
```

Suggested name:

```text
rfs_mb0_laptop_spectral_subspace_control_repair_smoke_result.md
```

Required sections:

```text
1. Executive summary
2. Claim boundary
3. Runtime and hardware profile
4. Shuffle failure anatomy
5. Primary-context refinement
6. Subspace transfer against controls
7. Distributedness diagnostic
8. Optional subspace ablation design smoke
9. Decision class
10. Next-action fork
11. Output manifest
```

The executive summary must answer:

```text
Did structure-destroying controls pass?
If not, why not?
Did subspace transfer beat controls?
Is the spectral object item-local, cluster-local, distributed, diffuse/noise-like, or control-equivalent?
What is the next action?
```

## 14. Graceful exit requirements

Runner must support:

```text
status.json at start;
periodic status.json updates;
progress checkpoint CSV;
SIGINT/SIGTERM handling;
shutdown cushion;
partial shuffle-anatomy output;
partial subspace-control output;
partial distributedness output;
errors.csv;
output_manifest.json;
partial final report.
```

Allowed partial statuses:

```text
COMPLETED
PARTIAL_TIME_LIMIT_REACHED
PARTIAL_INTERRUPTED
PARTIAL_CONTROL_SOURCE_MISSING
PARTIAL_SHUFFLE_ANALYSIS_INCOMPLETE
PARTIAL_SUBSPACE_CONTROL_INCOMPLETE
FAILED_WITH_ERRORS
```

## 15. Bottom line

This smoke should not try to rescue the high-loading item-channel hypothesis.

It should answer the current truth-seeking fork:

```text
Is the coflow spectral object a transferable distributed subspace above
structure-destroying controls, or is it control-equivalent / too diffuse?
```

No graph perturbation should run until that is answered.

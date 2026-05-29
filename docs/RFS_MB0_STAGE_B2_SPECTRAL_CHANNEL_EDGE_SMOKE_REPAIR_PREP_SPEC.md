# RFS-MB0 Stage B-2 Spectral Channel-Edge Smoke Repair Prep Spec

Status: small-smoke implementation spec / preparation for later 24h run  
Scope: repair and sharpen the spectral/channel instrument before any large unsupervised pass  
Claim boundary: no holdout, no candidate promotion, no Omega detection, no agent detection, no identity detection, no valuer detection

## 0. One-sentence purpose

Run small, repair-focused smokes that determine whether spectrally guided channel-edge sensitivity is implementable and interpretable before spending a 24-hour unsupervised block.

Plainly:

```text
Do not run the big channel experiment yet.
First prove the spectral controls, high-loading item export, item-to-edge mapping,
and targeted-vs-random perturbation path work on small runs.
```

## 1. Background

The Stage B-2 exploratory iteration pass found weak but non-null topology-sensitive residues:

```text
SYN_A:
  edge_roughening_sensitive_syndrome

SYN_C:
  edge_roughening_sensitive_syndrome

SYN_B/SYN_D:
  measurable but no resolved residual
```

The strongest effects were topology-level edge perturbations. Exact generator roughness/asymmetry controls were near baseline. This suggests the current weak object is more likely edge/topology/channel sensitive than clean generator-mechanism sensitive.

The Stage B-2 spectral future-field geometry smoke then found:

```text
cofrontier and coflow matrices were well-covered;
coflow dominated the strongest positive spectral mass;
topology-level controls produced large coflow spectral changes;
control comparison scope was direct_stage_b2_controls_only;
missing controls prevented full spectral migration criteria.
```

This spec prepares the next instrument step:

```text
spectrally guided channel-edge sensitivity
```

but only after small smokes prove the required repairs and data paths.

## 2. Claim boundary

Allowed claims from this prep run:

```text
spectral control repairs work or fail;
high-loading spectral item export works or fails;
item-to-edge mapping has enough coverage or fails;
analysis-only high-loading ablation shows or does not show dependence;
tiny targeted-vs-random perturbation smoke is or is not implementable;
the 24h run is or is not ready.
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

## 3. Overall run posture

This is a small-smoke prep pass, not the 24h pass.

Recommended total wall clock:

```text
2 to 4 hours
```

Hard cap if run unattended:

```text
max_runtime_seconds: 14400
shutdown_cushion_seconds: 1200
```

Use fewer groups/seeds than the earlier spectral smoke unless a smoke is very cheap.

Suggested default:

```text
design_groups: 1 to 2
fresh_seeds_per_group: 1 to 2
start_samples_list: 4
probes:
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple
flow_modes:
  one_step_local_flow
  constrained_window_flow
horizon_bands:
  short, middle, downstream
selected syndromes:
  SYN_A and SYN_C primary
  SYN_B and SYN_D secondary contrast only if cheap
```

## 4. Priority queue

Run stages in order. Do not proceed to later stages if earlier safety gates fail.

### Priority 0: runner/output repair smoke

Purpose:

```text
Verify that the runner emits the new spectral/channel outputs, clean decision classes,
and graceful-exit artifacts before scientific interpretation.
```

Required repairs before or during this smoke:

```text
split decision classes:
  spectral_matrix_coverage_passed
  spectral_direct_topology_sensitivity_present
  spectral_controls_incomplete
  spectral_migration_criteria_not_yet_met
  spectral_future_geometry_above_full_controls

export high-loading spectral items;
export high-loading item loadings and mode indices;
export matrix item vocabularies;
export context manifests sufficient for item-to-edge mapping;
write progress checkpoints;
write partial outputs on interruption.
```

Required outputs:

```text
spectral_channel_prep_run_config.json
spectral_channel_prep_status.json
spectral_channel_prep_progress_checkpoints.csv
spectral_channel_prep_output_manifest.json
spectral_channel_prep_errors.csv
runner_output_contract_smoke_report.md
```

Acceptance gate:

```text
all required output files present;
status.json contains counters and claim-boundary fields;
output_manifest marks missing files honestly;
decision classes are not overstated;
errors.csv exists even if empty.
```

If this fails, stop and repair runner plumbing.

### Priority 1: cheap spectral-control repair smoke

Purpose:

```text
Add the cheapest missing controls from the spectral smoke before interpreting high-loading structures.
```

Required controls for this small smoke:

```text
label_shuffled_spectral_replicates;
context_shuffled_spectral_replicates;
horizon_order_shuffled_spectral_replicates.
```

Optional if cheap:

```text
frontier_size_or_support_size_matched_spectral_control;
probe_marginal_spectral_control or honest not_implemented flag.
```

Replicate count:

```text
minimum: 3
preferred smoke: 5
```

Required outputs:

```text
spectral_label_shuffle_smoke.csv
spectral_context_shuffle_smoke.csv
spectral_horizon_shuffle_smoke.csv
spectral_control_repair_smoke_summary.csv
spectral_control_repair_smoke_report.md
```

Acceptance gate:

```text
label/context/horizon shuffle controls complete;
observed coflow spectral summaries are compared to shuffle distributions;
rank/percentile versus shuffle controls is emitted;
controls do not silently overwrite direct-control summaries.
```

If shuffled controls reproduce observed coflow structure, block channel-edge sensitivity and recommend spectral measurement-limits or control repair.

### Priority 2: high-loading item export and item-to-edge mapping smoke

Purpose:

```text
Determine whether high-loading coflow spectral items can be mapped to realized edge structures with enough coverage for perturbation.
```

Primary matrix family:

```text
coflow
```

Primary conditions:

```text
baseline_unperturbed;
small_edge_resample_control:p0.02;
asymmetric_edge_flip_control:p0.02.
```

Primary horizon band:

```text
middle
```

Selection method:

```text
select high-loading coflow items from top-k positive spectral modes;
use fixed top_k_items before seeing perturbation outcomes;
start with top_k_items: 16 or 32;
apply min_item_count and item mass filters;
exclude diagnostic probes from positive interpretation.
```

Required mapping fields:

```text
spectral_item_id
matrix_id
probe_key
flow_mode
horizon_band
condition_id
signature_transition
loading_score
mode_index
item_count
item_mass
realized_edge_count
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

Required outputs:

```text
spectral_high_loading_items_smoke.csv
spectral_item_loading_summary_smoke.csv
spectral_item_to_edge_mapping_smoke.csv
spectral_mapping_coverage_smoke.csv
spectral_item_mapping_smoke_report.md
```

Acceptance gate:

```text
mapped_item_fraction and mapped_item_mass_fraction are reported;
coverage is high enough to run at least one targeted perturbation smoke;
if realized-edge mapping is insufficient, signature-transition-only status is reported honestly.
```

Suggested minimum to proceed:

```text
mapped_item_mass_fraction >= 0.30
```

Preferred:

```text
mapped_item_mass_fraction >= 0.50
```

If mapping fails, do not run graph-level targeted perturbation. Run analysis-only ablation or repair context export.

### Priority 3: analysis-only spectral item ablation smoke

Purpose:

```text
Cheaply test whether high-loading coflow items actually carry the observed spectral geometry before perturbing graph edges.
```

Method:

```text
remove or downweight high-loading coflow items in the matrix/count analysis;
compare to matched random item removal;
compare to low-loading or mid-loading item removal if cheap.
```

Allowed interpretation:

```text
spectral dependence only;
not causal topology dependence.
```

Required outputs:

```text
spectral_item_ablation_manifest.csv
spectral_high_loading_ablation_summary.csv
spectral_random_item_ablation_summary.csv
spectral_low_mid_loading_ablation_summary.csv
spectral_item_ablation_decision.csv
spectral_item_ablation_report.md
```

Acceptance gate:

```text
high-loading ablation changes spectral summaries more than matched random ablation;
coverage remains adequate after ablation;
result does not depend only on one diagnostic probe.
```

If high-loading ablation is random-equivalent, do not run graph-level channel perturbation in the small-smoke block.

### Priority 4: tiny targeted-vs-random perturbation smoke

Purpose:

```text
Prove graph-level targeted channel perturbation is implementable and distinguishable from matched random perturbation on a tiny sample.
```

Use only if Priority 2 and Priority 3 pass.

Perturbation classes:

```text
spectral_high_loading_targeted_edge_perturbation;
matched_random_edge_perturbation;
optional low_loading_edge_perturbation.
```

Strengths:

```text
p = 0.0025
p = 0.005
```

Do not run p0.01 or p0.02 in the small smoke unless p0.005 is non-destructive and time remains.

Matching fields to preserve as feasible:

```text
number of perturbed edges;
source out-degree bin;
target in-degree bin;
probe_key;
flow_mode;
horizon_band;
signature-transition frequency;
baseline flow mass.
```

Required outputs:

```text
spectral_channel_tiny_perturbation_manifest.csv
spectral_channel_tiny_matching_quality.csv
spectral_channel_tiny_substrate_preservation.csv
spectral_channel_tiny_syndrome_rates.csv
spectral_channel_tiny_spectral_response.csv
spectral_channel_tiny_entropy_flow_horizon_response.csv
spectral_channel_tiny_target_vs_random_summary.csv
spectral_channel_tiny_smoke_report.md
```

Acceptance gate:

```text
targeted and matched random perturbations both run;
substrate preservation is non-destructive or mildly destructive;
matching quality is reported;
A/C syndrome response and spectral response are both emitted;
no interpretation relies on targeted-only comparison to baseline.
```

## 5. Readiness for 24h run

The 24h run is not ready unless all of the following hold:

```text
1. runner/output contract passes;
2. shuffled spectral controls complete and do not trivially erase the observed coflow object;
3. high-loading item export works;
4. item-to-edge mapping has adequate mass coverage, or signature-transition perturbation is explicitly chosen instead;
5. analysis-only high-loading ablation differs from matched random ablation;
6. tiny targeted-vs-random perturbation completes without destructive controls;
7. final report emits a clear branch recommendation.
```

If any condition fails, the next 24h block should be postponed or redirected toward repair.

## 6. Recommended 24h run only if smokes pass

If the smokes pass, the later 24h run should scale only the validated path.

Possible 24h focus:

```text
spectrally guided channel-edge sensitivity with full matched random controls;
expanded shuffled spectral controls;
A/C primary, B/D contrast;
channel/corridor/trap horizon read;
no holdout;
no n=6;
no alphabet expansion unless separately approved as diagnostic.
```

Do not use the 24h block to combine too many unvalidated extensions.

## 7. Decision classes

Allowed small-smoke decision classes:

```text
runner_contract_passed
runner_contract_failed
spectral_shuffle_controls_passed
spectral_shuffle_controls_control_equivalent
spectral_item_mapping_adequate
spectral_item_mapping_insufficient
high_loading_ablation_specific
high_loading_ablation_random_equivalent
tiny_channel_perturbation_implemented
tiny_channel_perturbation_not_interpretable
ready_for_24h_spectral_channel_run
not_ready_repair_required
```

Forbidden decision classes:

```text
Omega_positive
agent_detected
valuer_detected
identity_detected
gauge_shadow_validated
candidate_promoted
holdout_ready
```

## 8. Final report requirements

Retain a result note under:

```text
docs/research_notes/validation_results/
```

Suggested name:

```text
rfs_mb0_stage_b2_spectral_channel_edge_smoke_repair_prep_result.md
```

Required sections:

```text
1. Claim boundary
2. Runtime and hardware profile
3. Priority stages completed
4. Runner/output contract smoke
5. Spectral shuffle-control smoke
6. High-loading item export and mapping smoke
7. Analysis-only ablation smoke
8. Tiny targeted-vs-random perturbation smoke, if run
9. Readiness for 24h run
10. Blockers / repairs required
11. Output manifest
```

The result note must explicitly state whether the 24h run is ready or blocked.

## 9. Graceful exit requirements

All runners must support:

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

Suggested small-smoke time cap:

```text
max_runtime_seconds: 14400
shutdown_cushion_seconds: 1200
```

Allowed final statuses:

```text
COMPLETED
PARTIAL_TIME_LIMIT_REACHED
PARTIAL_INTERRUPTED
PARTIAL_MAPPING_INSUFFICIENT
PARTIAL_SHUFFLE_CONTROLS_FAILED
PARTIAL_NO_INTERPRETABLE_PERTURBATIONS
FAILED_WITH_ERRORS
```

If partial, report which outputs are safe to interpret and which are exploratory-only.

## 10. 3P check

### Principled

The run tests whether spectral structures derived from future-field relations can guide perturbation, rather than adding hand-built agent/channel labels.

### Parsimonious

The run validates the minimal spectral-to-channel path before building a larger detector.

### Predictive

High-loading spectral structures must predict ablation or perturbation sensitivity better than matched random structures.

If they do not, the spectral path is not ready for a 24h run.

## 11. Bottom line

This prep run should sharpen the instrument, not scale it.

Clean fork:

```text
if smokes pass:
  run a 24h spectrally guided channel-edge sensitivity pass later

if smokes fail:
  repair spectral controls, item mapping, or perturbation matching before scaling
```

No positive claim should be made from this prep run beyond instrument readiness.

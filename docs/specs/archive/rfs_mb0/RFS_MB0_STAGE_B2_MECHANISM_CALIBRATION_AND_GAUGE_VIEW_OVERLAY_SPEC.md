# RFS-MB0 Stage B-2 Mechanism Calibration and Gauge-View Overlay Spec

Status: implementation spec / theory-instrumentation bridge  
Scope: RFS-MB0 frontier-transform syndrome branch after weak Stage B mechanism smoke  
Claim boundary: no holdout, no candidate promotion, no Omega detection, no agent detection, no identity detection, no valuer detection

## 0. One-sentence purpose

Stage B-2 tests whether the weak SYN_A/SYN_C residues from Stage B are real mechanism-sensitive future-field deformation signals or artifacts of destructive controls, single-view fragility, probe collision, or generic finite-frontier behavior.

The run has two linked aims:

```text
1. Calibrate preservation-first mechanism controls.
2. Add a small entropy-flow-horizon gauge-view overlay.
```

This is not a full gauge-coherent shadow validation branch. It is a bridge run that decides whether such a branch is worth building.

## 1. Background

Stage B mechanism smoke produced a weak but non-null result.

The measurable syndromes were:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag
SYN_C_low_growth_high_concentration_low_entropy
```

Their baseline rate was low but nonzero:

```text
baseline_syndrome_rate: 0.026785714285714284
```

The other selected syndromes were not measurable in the limited Stage B design:

```text
SYN_B_high_turnover_high_offdiag_high_window_delta
SYN_D_high_turnover_high_entropy_low_bottleneck_control
```

The most interesting Stage B read was:

```text
asymmetry p0.01:
  baseline unchanged

asymmetry p0.02:
  baseline unchanged

roughness p0.01:
  baseline rate reduced by about half
```

However, the interpretation is underdetermined.

The current roughness control is post-hoc edge resampling on the realized graph, not only resampling the generator's tiny roughness score term. The current asymmetry control is post-hoc reversal of a fraction of asymmetric realized edges, not a clean generator-level asymmetry sweep.

Therefore Stage B did not yet establish:

```text
roughness-term dependence
asymmetry independence
mechanism-specific syndrome structure
agent-like deformation
Omega-compatible structure
```

It established only:

```text
weak measurable SYN_A/SYN_C residues exist in a limited local run;
these residues are sensitive to one gentle edge-roughening control;
stronger controls are often too destructive;
mechanism attribution is not yet clean.
```

## 2. Guiding interpretation

The leading weak hypothesis is:

```text
The first measurable future-deformation residues may be channel-like:
low growth, high bottleneck/concentration, low entropy or low off-diagonal spread.
```

This is only a hypothesis.

Channel-like deformation is ambiguous:

```text
corridor:
  local narrowing that preserves or reopens downstream recoverability

trap:
  local narrowing that collapses downstream recoverability

fakeout:
  apparent narrowing explained by controls, saturation, probe collision, or finite-frontier phase behavior
```

Stage B-2 should not install channels into the substrate. It should only add readings that can distinguish corridor-like, trap-like, and fakeout-like deformation if the data support it.

## 3. Claim boundary

Allowed claims:

```text
Stage B-2 calibrates mechanism controls.
Stage B-2 measures weak residual deformation under entropy, flow, and horizon views.
Stage B-2 can classify observed residues as underdetermined, artifact-like, corridor-like, trap-like, or worth further gauge testing.
Stage B-2 can recommend or block a full RFS-MB0G gauge-coherent shadow branch.
```

Not allowed:

```text
Omega detected.
Agent detected.
Identity detected.
Valuer detected.
Gauge-coherent shadow validated.
Future-shaping source identified.
Holdout passed.
Candidate promoted.
```

Holdout remains untouched.

No n=6 transfer.

No alphabet expansion in the main run.

Any representation-resolution diagnostic is optional, tiny, and non-promotional.

## 4. Stage B-2 core question

Primary question:

```text
Are SYN_A/SYN_C weak residues robust enough, mechanism-specific enough,
and cross-view coherent enough to justify a fuller gauge-coherent shadow branch?
```

Subquestions:

```text
1. Are SYN_A/SYN_C sensitive to the actual generator roughness term, or only to post-hoc edge resampling?
2. Are they insensitive to generator-level asymmetry, or only to post-hoc edge flipping?
3. Are they dependent on a small set of high-flow / bottleneck edges?
4. Do entropy, flow, and horizon views tell a coherent story?
5. Do these residues look corridor-like, trap-like, or fakeout-like?
6. Can controls be made gentle enough to support interpretation?
```

## 5. Mechanism-control repair

Stage B-2 separates generator-level mechanism controls from post-hoc graph perturbation controls.

### 5.1 Roughness controls

Current Stage B roughness control should be treated as:

```text
small_edge_resample_control
```

or, if the old name is retained for compatibility, every report must state:

```text
roughness_resampled_transform_control is post-hoc edge resampling,
not a pure generator-roughness control.
```

Add a generator-level roughness control:

```text
roughness_seed_resample_generation_control
```

Behavior:

```text
same RelationParams;
same constraints;
same asymmetry weights if feasible;
same base seed where feasible;
new roughness seed only;
regenerate scored top-k edges;
report edge overlap and substrate preservation.
```

If same constraints and asymmetry weights cannot be cleanly preserved with current generator interfaces, implement the closest honest proxy and name it accordingly.

Suggested strengths / variants:

```text
roughness_seed_resample:
  seeds: 3 small replicates

small_edge_resample:
  p = 0.001, 0.0025, 0.005, 0.01, 0.02
```

Do not begin with p0.05, p0.10, or p0.20 as primary interpretive controls; those were too destructive too often in Stage B.

### 5.2 Asymmetry controls

Current Stage B asymmetry control should be treated as:

```text
asymmetric_edge_flip_control
```

This is a topology perturbation, not a clean generator-asymmetry intervention.

Add generator-level asymmetry controls:

```text
asymmetry_strength_sweep_control
bias_weight_resample_generation_control
```

Behavior:

```text
asymmetry_strength_sweep_control:
  regenerate with asymmetry_strength scaled around baseline

bias_weight_resample_generation_control:
  regenerate with fresh bias weights while preserving other parameters where feasible
```

Suggested asymmetry multipliers:

```text
0.0
0.25x
0.5x
1.0x baseline
1.5x
2.0x
```

If baseline asymmetry_strength is zero, skip positive multipliers that do not change the system and report `baseline_asymmetry_zero`.

Keep small edge-flip controls as topology diagnostics:

```text
asymmetric_edge_flip_control:
  p = 0.005, 0.01, 0.02
```

### 5.3 Constraint controls

The prior constraint control was generation-level and often destructive.

Stage B-2 should add gentler preservation-first constraint controls before broader resampling.

Preferred ladder:

```text
constraint_residue_jitter_control:
  change a tiny fraction of preferred residues, preserving count/type/arity

constraint_weight_jitter_control:
  multiply weights by small factors near 1.0

constraint_assignment_local_shuffle_control:
  local coordinate reassignment within neighborhood if available

constraint_resampled_generation_control:
  retain as stronger underdetermined control, not first-line interpretation
```

Suggested strengths:

```text
very_gentle: 0.0025
p0.005
p0.01
p0.02
```

Every constraint control must report whether it is:

```text
assignment-level
weight-level
residue-level
generation-level proxy
```

Do not call a generation-level proxy a shuffle.

## 6. Substrate preservation criteria

Every mechanism-control system must emit a preservation audit.

Required fields:

```text
control_name
control_variant
control_strength
baseline_system_id
control_system_id
state_count_delta
edge_count_delta
mean_out_degree_delta
mean_in_degree_delta
reciprocity_delta
edge_jaccard_vs_baseline
frontier_size_profile_delta
saturation_timing_delta
control_destructiveness_score
control_too_destructive
constraint_count_delta_if_available
constraint_strength_distribution_delta_if_available
```

Interpretation bands:

```text
non_destructive:
  control_destructiveness_score <= 0.20

mildly_destructive:
  0.20 < score <= 0.35

destructive_underdetermined:
  0.35 < score <= 0.50

control_too_destructive:
  score > 0.50
```

Only non-destructive and mildly destructive controls can support positive mechanism interpretation.

Destructive controls can only support:

```text
underdetermined
control_too_destructive
needs gentler ladder
```

## 7. Gauge-view overlay

Stage B-2 adds a small diagnostic overlay, not a full gauge-coherent shadow branch.

The overlay uses three view families:

```text
entropy view:
  shape of future possibility

flow view:
  transport / routing of future possibility

horizon view:
  consequence over time
```

Working compression:

```text
entropy:
  shape

flow:
  transport

horizon:
  consequence
```

The overlay asks:

```text
Does the same weak residual deformation tell a coherent story as shape,
transport, and temporal consequence?
```

## 8. Entropy view

Purpose:

```text
Measure whether future possibility is spreading, concentrating, flattening,
collapsing, or structured rather than noise-like.
```

Candidate metrics:

```text
signature_distribution_entropy
transition_matrix_entropy
row_entropy_mean
column_entropy_mean
entropy_delta_to_previous_window
entropy_delta_to_next_window
normalized_entropy_by_support_size
```

Required controls:

```text
support-size matched entropy control
frontier-size matched entropy control
probe-marginal entropy control or honest exclusion
```

Interpretation cautions:

```text
high entropy can mean lush branching or noise;
low entropy can mean coherent channeling or lock-in;
entropy is a shape view, not a value metric.
```

## 9. Flow view

Purpose:

```text
Measure how future possibility is routed through the transition structure.
```

Candidate metrics:

```text
top_k_flow_concentration
frontier_bottleneck_index
max_signature_flow_fraction
diagonal_persistence_mass
off_diagonal_transform_mass
edge_into_fb_rate
states_without_window_target
flow_channel_stability_across_windows
high_flow_edge_sensitivity
```

Add optional channel diagnostics:

```text
high_flow_edge_set:
  top-k source-target or signature-transition edges carrying flow

channel_edge_removal_sensitivity:
  change in syndrome / frontier profile after removing or perturbing high-flow edges

random_edge_removal_sensitivity:
  matched control for channel-edge removal
```

Do not install channels into the generator. Only read them from observed flow.

Interpretation cautions:

```text
channels can be corridors;
channels can be traps;
channels can be finite-graph fakeouts.
```

## 10. Horizon view

Purpose:

```text
Distinguish local compression from downstream consequence.
```

Candidate horizon bands:

```text
short:
  0->1, 1->2, 2->4

middle:
  4->8, 8->16

downstream:
  16->24, 24->32
```

If runtime permits, add a very small long-horizon diagnostic only after the main outputs are healthy.

Horizon classifications:

```text
corridor_like:
  local concentration or bottleneck followed by downstream reopening,
  persistence, or recoverability

trap_like:
  local concentration followed by downstream collapse or terminal narrowing

generic_phase_like:
  same pattern appears in matched controls or saturation timing controls

horizon_fragile:
  pattern appears in one window band only and does not predict adjacent bands
```

Important:

```text
horizon defines the consequence axis of Omega.
A local bottleneck is not meaningful until its downstream profile is known.
```

## 11. Corridor, trap, fakeout classifier

Stage B-2 should emit a cautious read for SYN_A/SYN_C and any measurable related residues.

Decision fields:

```text
syndrome_id
baseline_rate
best_non_destructive_control_rate
roughness_term_sensitivity
edge_roughening_sensitivity
asymmetry_strength_sensitivity
asymmetric_edge_flip_sensitivity
constraint_gentle_sensitivity
entropy_profile_class
flow_profile_class
horizon_profile_class
corridor_trap_fakeout_class
interpretation_confidence
```

Classes:

```text
corridor_like_deformation:
  local narrowing/concentration with downstream reopening or recoverability signal

trap_like_deformation:
  local narrowing/concentration with downstream collapse or no re-entry

fakeout_like_deformation:
  pattern matched by controls, probe collision, frontier size, or saturation timing

edge_fragile_deformation:
  weak residue destroyed by tiny edge perturbation without clear corridor/trap read

mechanism_sensitive_weak_residue:
  weak but nonzero residue changes under gentle mechanism controls

underpowered_or_unresolved:
  baseline rate too low or controls too destructive
```

No class implies agent detection.

## 12. Optional representation-resolution diagnostic

The main Stage B-2 run must remain on the current minimal substrate unless explicitly configured otherwise.

Optional tiny diagnostic:

```text
representation_resolution_shape_diagnostic
```

Purpose:

```text
Test whether the instrument is alphabet-shape or resolution limited,
not whether a larger substrate produces stronger positives.
```

Recommended first comparison:

```text
current shape:
  3^5

same-size neighboring shape:
  4^4
```

This is preferred before true state-space expansion.

Rules:

```text
No promotion from representation-resolution diagnostic.
No holdout.
No n=6.
No new labels.
No changing syndrome definitions after seeing the diagnostic.
```

Interpretation:

```text
same deformation class appears across shapes:
  possible representation-stable signal; still not validation

signal appears only in larger/richer shape:
  resolution-sensitive instrumentation clue

signal disappears:
  frame-fragile or shape-dependent; do not promote
```

## 13. Inputs

Required inputs:

```text
Stage A addendum output with selected syndromes
Phase B compact control-value table
Phase B metric rows
source relation atlas / group selection
corrected group classification
source run atlas band selection
```

Required selected syndrome IDs:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag
SYN_C_low_growth_high_concentration_low_entropy
```

Optional diagnostic selected syndrome IDs:

```text
SYN_B_high_turnover_high_offdiag_high_window_delta
SYN_D_high_turnover_high_entropy_low_bottleneck_control
```

SYN_B/SYN_D should not dominate runtime unless baseline measurability improves.

## 14. Suggested run shape

Stage B-2 should stay smaller than a full recurrence run.

Suggested laptop-safe shape:

```text
design_groups: 1 or 2
fresh_seeds_per_group: 2 to 4
start_samples_list: 4,8
probes:
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple
  optional channel/transition-role view if implemented
workers:
  machine-specific
```

Suggested desktop shape after laptop validation:

```text
design_groups: 3 to 5
fresh_seeds_per_group: 4
start_samples_list: 4,8
keep full holdout frozen
```

Do not increase seeds until:

```text
non-destructive control ladders are calibrated;
output contracts are stable;
gauge overlay emits interpretable tables;
control destructiveness is summarized clearly.
```

## 15. Required outputs

Core mechanism outputs:

```text
stage_b2_run_config.json
stage_b2_job_manifest.csv
stage_b2_mechanism_control_system_manifest.csv
stage_b2_substrate_preservation.csv
stage_b2_metric_rows.csv
stage_b2_component_scores.csv
stage_b2_syndrome_rates.csv
stage_b2_dependency_scores.csv
stage_b2_decision_summary.csv
```

Gauge overlay outputs:

```text
stage_b2_entropy_view_summary.csv
stage_b2_flow_view_summary.csv
stage_b2_horizon_view_summary.csv
stage_b2_entropy_flow_horizon_overlay.csv
stage_b2_corridor_trap_fakeout_summary.csv
```

Optional diagnostic outputs:

```text
stage_b2_representation_resolution_diagnostic.csv
stage_b2_channel_edge_sensitivity.csv
```

Final report:

```text
rfs_mb0_stage_b2_mechanism_calibration_and_gauge_overlay_report.md
```

Run hygiene:

```text
errors.csv
status.json
output_manifest.json
```

## 16. Final report requirements

Required report sections:

```text
1. Claim boundary
2. Why Stage B-2 exists
3. Stage B weak-result recap
4. Mechanism-control repair overview
5. Substrate preservation/destructiveness audit
6. SYN_A/SYN_C mechanism dependency read
7. Entropy view results
8. Flow view results
9. Horizon view results
10. Corridor / trap / fakeout interpretation
11. Representation-resolution diagnostic, if run
12. Whether a full gauge-coherent shadow branch is warranted
13. Output manifest
```

## 17. Decision classes

Allowed decision classes:

```text
mechanism_calibration_positive_weak
roughness_term_sensitive_syndrome
edge_roughening_sensitive_syndrome
asymmetry_strength_sensitive_syndrome
asymmetric_edge_flip_sensitive_syndrome
constraint_sensitive_weak_syndrome
edge_fragile_syndrome
corridor_like_deformation
trap_like_deformation
fakeout_like_deformation
gauge_overlay_inconclusive
control_too_destructive_underdetermined
baseline_too_sparse_underdetermined
no_resolved_residual
```

Branch recommendation classes:

```text
recommend_stage_b3_more_seeds:
  only if non-destructive controls and overlay are interpretable

recommend_full_gauge_shadow_spec:
  only if cross-view residual coherence appears above controls

recommend_mechanism_control_repair:
  if controls remain destructive or mechanism attribution unclear

recommend_measurement_limits_note:
  if SYN_A/SYN_C collapse into fakeout or no resolved residual
```

Forbidden decision classes:

```text
Omega_positive
agent_detected
valuer_detected
identity_detected
holdout_ready
candidate_promoted
```

## 18. Acceptance criteria

Stage B-2 implementation accepted only if:

```text
roughness-term and edge-roughening controls are distinguished;
generator-level and post-hoc asymmetry controls are distinguished;
constraint controls are honestly named by intervention type;
substrate preservation audit is emitted for every control;
entropy, flow, and horizon overlay tables are emitted;
SYN_A/SYN_C are reported separately from SYN_B/SYN_D;
control destructiveness gates positive interpretation;
no holdout scoring occurs;
no n=6 transfer occurs;
no alphabet expansion occurs in the main run;
representation-resolution diagnostic, if run, is marked non-promotional.
```

Scientific interpretation accepted only if:

```text
raw rates are not used without control-relative residuals;
no result is promoted from destructive controls;
no single view is treated as agent evidence;
corridor/trap/fakeout classes are explicitly marked provisional;
claim boundary is repeated in the final report.
```

## 19. 3P check

### Principled

Stage B-2 follows from observed failure modes:

```text
raw recurrence was control-equivalent;
Stage B weak residues were underdetermined;
boundary-first identity is not available;
future deformation remains the measurable target.
```

### Parsimonious

The run adds no new ontology.

Entropy, flow, and horizon are views on future-field deformation, not new primitives.

Channel readings are diagnostics, not substrate labels.

### Predictive

The run must answer risky questions:

```text
Does generator roughness matter, or only edge roughening?
Does generator asymmetry matter, or only edge flipping?
Does a weak bottleneck/concentration residue persist across entropy, flow, and horizon views?
Does local narrowing reopen downstream or collapse?
Do controls explain the same pattern?
```

## 20. Bottom line

Stage B-2 should determine whether the current weak residues are worth carrying forward.

The desired outcome is not a positive claim. The desired outcome is a cleaner fork:

```text
if weak residues become mechanism-specific and cross-view coherent:
  write a full RFS-MB0G gauge-coherent shadow spec

if weak residues are edge-fragile or fakeout-like:
  write the measurement-limits note and stop scaling this detector

if controls remain too destructive:
  repair mechanism controls before more seeds
```

The immediate object remains:

```text
control-relative deformation of reachable futures
```

not agency, not value, and not Omega.

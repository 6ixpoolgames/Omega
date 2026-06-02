# RFS-MB0 Stage B-2 Exploratory Iteration Pass Spec

Status: exploratory implementation spec / Codex priority queue  
Scope: 6-8 hour wall-clock block using Stage B-2 machinery and related small extensions  
Claim boundary: no holdout, no candidate promotion, no Omega detection, no agent detection, no identity detection, no valuer detection

## 0. Purpose

This spec defines a priority-ordered exploratory pass for a limited unsupervised compute window.

The validated desktop Phase B / Stage A / Stage B result gives a useful fork:

```text
Stage A:
  preregistered joint signed syndromes separate from marginal-preserving controls

Stage B:
  all four selected syndromes are measurable, but the mechanism-control ladder is
  still control_too_destructive_underdetermined
```

The purpose of this iteration pass is not to validate Omega or open holdout. It is to learn which next branch is worth formalizing.

Primary goals:

```text
1. Protect interpretation with strict control naming and preservation audits.
2. Calibrate gentler mechanism controls.
3. Test whether entropy, flow, and horizon views tell a coherent story.
4. Explore whether channel-like residues are corridor-like, trap-like, or fakeout-like.
5. Decide whether the next step should be Stage B-3, full RFS-MB0G gauge-shadow spec,
   mechanism-control repair, representation-resolution diagnostic, or measurement-limits note.
```

## 1. Hard wall-clock constraint

Total wall-clock budget:

```text
8 hours maximum
```

The orchestrating runner or script must use:

```text
max_runtime_seconds: 28800
shutdown_cushion_seconds: at least 1200
```

Preferred:

```text
shutdown_cushion_seconds: 1800
```

No new large jobs should be launched inside the shutdown cushion.

All runners must support graceful exit:

```text
SIGINT/SIGTERM handling;
periodic status.json writes;
progress checkpoint CSVs;
partial artifact finalization;
output_manifest.json even on partial completion;
errors.csv even if empty;
clear finalization_reason.
```

If time expires, partial outputs are useful. Do not discard completed rows because the full plan did not finish.

## 2. Global claim boundary

Allowed outputs:

```text
control calibration;
proxy naming audit;
preservation/destructiveness audit;
weak residual deformation read;
entropy-flow-horizon diagnostic;
channel/corridor/trap/fakeout provisional classification;
recommendation for next branch.
```

Forbidden outputs:

```text
Omega_positive
agent_detected
identity_detected
valuer_detected
candidate_promoted
holdout_ready
holdout_scored
n6_transfer_claim
alphabet_expansion_claim
```

Run counters must remain:

```text
holdout_scoring_count: 0
n6_run_count: 0
candidate_promotion_enabled: false
```

If any optional representation-resolution diagnostic is run, report:

```text
alphabet_expansion_count:
  diagnostic only, non-promotional
```

Do not mix optional representation-resolution diagnostic rows with main Stage B-2 mechanism rows without explicit labels.

## 3. Priority ordering

The run should follow this priority queue.

If a higher-priority stage fails its acceptance gate, later stages should either be skipped or marked exploratory-only.

### Priority 0: Control identity smoke

Purpose:

```text
Ensure the machinery reports what each control actually does.
```

Required before interpretation.

Outputs:

```text
control_identity_contract_smoke.csv
control_preservation_smoke.csv
status.json
errors.csv
```

Must include:

```text
intended_control_name
actual_control_name
proxy_level
intended_mechanism
actual_intervention
preserved_fields_json
changed_fields_json
unpreserved_fields_json
preservation_failure_reason
allowed_interpretation_level
```

Acceptance gate:

```text
all mechanism-control rows have actual_control_name;
all mechanism-control rows have proxy_level;
all mechanism-control rows have allowed_interpretation_level;
no exact mechanism control is silently emitted if preservation failed.
```

If this fails:

```text
stop mechanism interpretation;
repair control identity reporting;
do not run large passes except optional fixture/unit tests.
```

### Priority 1: Existing-output triage

Purpose:

```text
Mine existing desktop Phase B / Stage A / Stage B outputs before generating more systems.
```

Questions:

```text
Where do SYN_A/B/C/D concentrate by window, probe, flow mode, start, seed,
parameter group, and control condition?

Are SYN_A and SYN_C genuinely similar, or only superficially similar?

Do SYN_B and SYN_D act as useful turnover/diffusion contrast syndromes?

Are selected syndromes concentrated in a few parameter families?

Are positive Stage A rows driven by one component, one window, or one probe?
```

Outputs:

```text
existing_stage_ab_syndrome_concentration.csv
existing_stage_ab_syndrome_by_window.csv
existing_stage_ab_syndrome_by_probe.csv
existing_stage_ab_syndrome_by_flow_mode.csv
existing_stage_ab_syndrome_by_start_seed.csv
existing_stage_ab_parameter_family_summary.csv
existing_stage_a_component_driver_audit.csv
existing_stage_ab_triage_report.md
```

Acceptance gate:

```text
report identifies whether Stage B-2 should prioritize:
  A/C stabilizing-channel syndromes;
  B/D turnover/diffusion contrast syndromes;
  mechanism controls;
  gauge overlay;
  measurement-limits note.
```

If this stage finds the signal is one-component or one-window brittle, later runs should be more conservative.

### Priority 2: Gentle mechanism ladder

Purpose:

```text
Find non-destructive or mildly destructive mechanism-control ranges.
```

This is the main Stage B-2 continuation.

Run smaller than full Stage B.

Suggested shape:

```text
design_groups: 3 to 5
fresh_seeds_per_group: 2 to 4
start_samples_list: 4,8
selected_syndromes:
  SYN_A
  SYN_C
  SYN_B and SYN_D as secondary contrast
```

Controls to attempt, subject to honest naming:

```text
small_edge_resample_control:
  p = 0.001, 0.0025, 0.005, 0.01, 0.02

roughness_seed_resample_generation_control:
  only if preservation is clean enough;
  otherwise downgrade to roughness_generation_proxy_control

asymmetric_edge_flip_control:
  p = 0.0025, 0.005, 0.01, 0.02

asymmetry_strength_sweep_control:
  only if generator-level preservation is clean enough;
  otherwise downgrade to asymmetry_generation_proxy_control

bias_weight_resample_generation_control:
  only if other generator components are preserved/reportable

constraint_residue_jitter_control:
  very gentle, if implementable

constraint_weight_jitter_control:
  very gentle, if implementable

constraint_resampled_generation_proxy:
  retain only as stronger underdetermined control
```

Required outputs:

```text
stage_b2_gentle_mechanism_run_config.json
stage_b2_gentle_mechanism_job_manifest.csv
stage_b2_gentle_mechanism_control_identity.csv
stage_b2_gentle_mechanism_substrate_preservation.csv
stage_b2_gentle_mechanism_metric_rows.csv
stage_b2_gentle_mechanism_component_scores.csv
stage_b2_gentle_mechanism_syndrome_rates.csv
stage_b2_gentle_mechanism_dependency_scores.csv
stage_b2_gentle_mechanism_decision_summary.csv
stage_b2_gentle_mechanism_report.md
```

Acceptance gate:

```text
at least one non-destructive or mildly destructive control ladder is populated;
actual/proxy naming is complete;
SYN_A/C are reported separately from SYN_B/D;
destructive controls are not used for positive or negative mechanism conclusions.
```

If most controls remain destructive:

```text
stop increasing seeds;
recommend mechanism-control repair.
```

### Priority 3: Entropy-flow-horizon overlay

Purpose:

```text
Test whether selected residuals tell a coherent story as shape, transport, and consequence.
```

This is diagnostic, not full gauge-coherent shadow validation.

Views:

```text
entropy:
  shape of future possibility

flow:
  transport / routing of future possibility

horizon:
  consequence over time
```

Required questions:

```text
Do SYN_A/C show local concentration or low-entropy narrowing?
Do flow metrics indicate routing through bottlenecks or high-flow channels?
Do downstream horizons reopen, remain stable, or collapse?
Do SYN_B/D provide a useful turnover/diffusion contrast?
Do controls show the same entropy-flow-horizon profile?
```

Candidate outputs:

```text
stage_b2_entropy_view_summary.csv
stage_b2_flow_view_summary.csv
stage_b2_horizon_view_summary.csv
stage_b2_entropy_flow_horizon_overlay.csv
stage_b2_corridor_trap_fakeout_summary.csv
stage_b2_overlay_report.md
```

Classification:

```text
corridor_like:
  local narrowing/concentration followed by downstream reopening, persistence,
  or recoverability

trap_like:
  local narrowing/concentration followed by downstream collapse or terminal narrowing

fakeout_like:
  pattern matched by controls, saturation timing, frontier size, or probe collision

horizon_fragile:
  pattern appears in one horizon band only and does not predict adjacent/downstream bands

unresolved:
  insufficient signal or controls too destructive
```

Acceptance gate:

```text
overlay emits tables for entropy, flow, and horizon;
classifications are provisional;
no corridor/trap/fakeout class implies agent or Omega detection;
controls are included in every read.
```

### Priority 4: Branch-selective exploratory extension

Run at most one of the following, based on earlier outputs and remaining time.

#### 4A. Channel-edge sensitivity

Choose if:

```text
SYN_A/C survive gentle controls;
entropy-flow-horizon overlay suggests channel/corridor-like deformation;
flow metrics identify candidate high-flow edges or signature transitions.
```

Purpose:

```text
Distinguish maintained channel structure from generic edge fragility.
```

Test:

```text
identify high-flow edge/signature-transition set;
perturb high-flow set gently;
perturb matched random edge set;
compare syndrome rate and horizon profile.
```

Outputs:

```text
stage_b2_channel_edge_set.csv
stage_b2_channel_edge_sensitivity.csv
stage_b2_random_edge_sensitivity_control.csv
stage_b2_channel_sensitivity_report.md
```

Allowed reads:

```text
channel_specific_sensitivity
random_edge_fragility
bottleneck_fakeout
unresolved
```

#### 4B. Representation-resolution diagnostic

Choose if:

```text
signals are weak but coherent;
probe collision or resolution starvation is suspected;
mechanism controls are interpretable enough to justify a diagnostic.
```

Purpose:

```text
Test whether the current distinction-space shape starves the instrument.
```

Preferred first diagnostic:

```text
current-like shape: 3^5
neighboring same-size shape: 4^4
```

Rules:

```text
non-promotional;
no holdout;
no n=6;
do not change syndrome definitions after seeing diagnostic;
report as representation-resolution evidence only.
```

Outputs:

```text
stage_b2_representation_resolution_diagnostic.csv
stage_b2_representation_resolution_report.md
```

Allowed reads:

```text
representation_stable_residue
resolution_sensitive_residue
shape_fragile_residue
unresolved
```

#### 4C. Synthetic fixture sanity check

Choose if:

```text
entropy-flow-horizon classifier is new or ambiguous;
channel/corridor/trap language needs validation;
mechanism data are too noisy for another generated-substrate pass.
```

Purpose:

```text
Check whether the analysis can distinguish known cases before interpreting generated substrates.
```

Fixture types:

```text
obvious_corridor
obvious_trap
noisy_branching
bottleneck_fakeout
saturation_artifact
```

Outputs:

```text
stage_b2_fixture_manifest.csv
stage_b2_fixture_overlay_results.csv
stage_b2_fixture_classifier_report.md
```

Allowed reads:

```text
classifier_passed_fixture_smoke
classifier_failed_fixture_smoke
fixture_inconclusive
```

If fixture smoke fails, do not trust corridor/trap/fakeout classifications from generated substrates.

#### 4D. Parameter-neighborhood sweep

Choose if:

```text
existing-output triage identifies specific parameter families where syndromes concentrate;
mechanism controls are not entirely destructive;
remaining time is enough for a small local sweep.
```

Purpose:

```text
Test whether the weak residues live in a local mechanism neighborhood rather than isolated seeds.
```

Possible sweep axes:

```text
asymmetry_strength:
  small multipliers around baseline, if cleanly implementable

roughness_strength or roughness_seed path:
  only with honest proxy naming

constraint_strength:
  very small local multipliers

constraint_density:
  tiny local perturbations only if not destructive

out_degree_target:
  optional, high risk of changing substrate regime

rewire_probability:
  optional, treat as topology-noise axis

reversibility_fraction:
  optional, useful if flow/horizon reads suggest corridor versus trap dependence
```

Rules:

```text
small local neighborhoods only;
no broad atlas;
no new labels;
report substrate preservation and shape class changes;
separate parameter-sweep rows from mechanism-control rows.
```

Outputs:

```text
stage_b2_parameter_neighborhood_manifest.csv
stage_b2_parameter_neighborhood_syndrome_rates.csv
stage_b2_parameter_neighborhood_preservation.csv
stage_b2_parameter_neighborhood_report.md
```

Allowed reads:

```text
local_parameter_stable_residue
parameter_boundary_residue
parameter_fragile_residue
shape_regime_shift_underdetermined
unresolved
```

## 4. Scheduling under 8 hours

The orchestrating run should be adaptive.

Recommended schedule:

```text
0:00-0:30
  Priority 0 control identity smoke

0:30-1:15
  Priority 1 existing-output triage

1:15-3:15
  Priority 2 gentle mechanism ladder

3:15-4:30
  Priority 3 entropy-flow-horizon overlay

4:30-6:30
  Priority 4 one selected exploratory extension

6:30-7:30
  synthesis, final report, manifest checks

7:30-8:00
  shutdown cushion / partial finalization / no new jobs
```

If a large pass takes longer than expected, skip lower-priority stages rather than running past the shutdown cushion.

Minimum useful completed package:

```text
Priority 0 + Priority 1 + Priority 2 + final report
```

Preferred completed package:

```text
Priority 0 + Priority 1 + Priority 2 + Priority 3 + one Priority 4 extension + final report
```

## 5. Graceful exit requirements

Every runner used in this block must support:

```text
status.json written at start;
status.json updated periodically;
progress checkpoint CSV;
SIGINT/SIGTERM handler;
shutdown cushion before max wall clock;
partial output finalization;
errors.csv;
output_manifest.json;
final report even if partial.
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
jobs_submitted
jobs_completed
jobs_cancelled
pending_jobs_remaining
metric_rows
control_rows
errors
holdout_scoring_count
n6_run_count
alphabet_expansion_count
candidate_promotion_enabled
```

Allowed final statuses:

```text
COMPLETED
PARTIAL_TIME_LIMIT_REACHED
PARTIAL_INTERRUPTED
PARTIAL_CONTROL_IDENTITY_FAILED
PARTIAL_NO_INTERPRETABLE_CONTROLS
FAILED_WITH_ERRORS
```

If final status is partial, the final report must include:

```text
what completed;
what did not run;
which outputs are safe to interpret;
which outputs are exploratory-only;
recommended next action.
```

## 6. Decision tree

At the end of the block, emit one branch recommendation.

### 6.1 Recommend mechanism-control repair

If:

```text
control identity contract fails;
most controls remain destructive;
proxy naming is incomplete;
mechanism attribution is impossible.
```

Then:

```text
Do not scale.
Repair controls.
```

### 6.2 Recommend Stage B-3 more seeds

If:

```text
non-destructive controls are calibrated;
SYN_A/C or selected syndromes remain measurable;
entropy-flow-horizon overlay is interpretable;
no major proxy/naming failures remain.
```

Then:

```text
Run a larger but still design-set-only Stage B-3.
Holdout remains blocked.
```

### 6.3 Recommend full RFS-MB0G gauge-shadow spec

If:

```text
cross-view residual coherence appears above controls;
multiple view families contribute;
mechanism controls are non-destructive enough;
channel/corridor/trap reads are not single-view artifacts.
```

Then:

```text
Write a full gauge-coherent shadow spec.
Do not treat this iteration as validation.
```

### 6.4 Recommend channel-specific follow-up

If:

```text
high-flow channel-edge perturbations differ from random edge perturbations;
horizon read suggests corridor-like or trap-like consequence;
controls do not explain the same pattern.
```

Then:

```text
Write a targeted channel/corridor/trap audit spec.
```

### 6.5 Recommend representation-resolution diagnostic expansion

If:

```text
signals are coherent but weak;
probe collision or resolution starvation is the main blocker;
same-size shape diagnostic is not yet run.
```

Then:

```text
Run representation-resolution shape diagnostic.
No promotion.
```

### 6.6 Recommend measurement-limits note

If:

```text
syndromes collapse under non-destructive controls;
entropy-flow-horizon overlay is control-equivalent;
fixture smoke fails;
parameter sweeps show only fragile isolated points;
```

Then:

```text
Write a measurement-limits note for this detector.
Stop scaling this branch until the instrument changes.
```

## 7. Required final synthesis note

Retain a public result note under:

```text
docs/research_notes/validation_results/
```

Suggested name:

```text
rfs_mb0_stage_b2_exploratory_iteration_pass_result.md
```

Required sections:

```text
1. Claim boundary
2. Hardware / runtime profile
3. Priority queue actually executed
4. Graceful-exit status
5. Control identity and proxy discipline
6. Existing-output triage summary
7. Gentle mechanism ladder result
8. Entropy-flow-horizon overlay result
9. Exploratory extension result, if any
10. Corridor / trap / fakeout read
11. Parameter-sweep read, if run
12. Representation-resolution read, if run
13. Decision tree outcome
14. Output manifest
```

The note must say explicitly:

```text
This was an exploratory iteration pass.
It was not holdout validation, candidate promotion, Omega detection, agency detection,
identity detection, or value detection.
```

## 8. Bottom line

This 6-8 hour block should not attempt to win the theory.

It should answer:

```text
What kind of weak object are we seeing?
Is the current signal mechanism-calibratable?
Does entropy-flow-horizon make the signal more intelligible or expose it as fakeout?
Which next branch is worth formalizing?
```

The most useful outcome is a clean fork, not a positive claim.

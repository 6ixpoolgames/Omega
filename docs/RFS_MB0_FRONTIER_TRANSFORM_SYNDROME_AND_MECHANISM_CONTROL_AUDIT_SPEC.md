# RFS-MB0 Frontier-Transform Syndrome and Mechanism-Control Audit Spec

Status: Codex implementation spec after Phase B design-set recurrence returned control-equivalent recurrence

Purpose: determine whether the Phase B frontier-transform recurrence failure is caused by marginal/generic finite-frontier phase behavior, or whether preregistered joint signed transform syndromes reveal mechanism-dependent structure tied to constraint/asymmetry dynamics.

This follows:

```text
docs/RFS_MB0_FRONTIER_TRANSFORM_PHASE_B_10H_DESIGN_RECURRENCE_SPEC.md
results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_b_10h/
docs/research_notes/validation_results/rfs_mb0_frontier_transform_phase_b_10h_result.md
```

Phase B result:

```text
raw design-set recurrence existed
strongest observed recurrence rows reached about 0.6
matched recurrence controls also reached about 0.6
recurrence_excess: 0.0
phase_c_ready: 0
holdout_scoring_count: 0
```

Interpretation:

```text
Marginal frontier-transform recurrence is control-equivalent.
The next question is whether joint signed transform syndromes are control-resistant and mechanism-dependent.
```

## 0. Claim boundary

This audit makes no claim of:

```text
Omega detection
agent detection
identity detection
valuer detection
viability proof
scientific gate pass
holdout pass
candidate promotion
```

Allowed claims:

```text
A preregistered frontier-transform syndrome is or is not present in existing Phase B rows.
A syndrome is or is not above generic controls.
A syndrome is or is not dependent on constraint/asymmetry perturbations.
A syndrome is or is not robust to roughness perturbation.
```

No holdout scoring.

No n=6.

No alphabet expansion in the main audit.

## 1. Why this audit exists

The Phase B recurrence gate asked a marginal question:

```text
Does metric M recur above threshold T across seeds/starts/windows?
```

Controls passed because bounded frontier metrics in finite deterministic graphs naturally show recurring phases:

```text
growth slows
support turnover spikes
bottlenecks appear
diagonal/off-diagonal mass changes
window stability changes
saturation or stabilization occurs
```

The next detector must ask a sharper question:

```text
Does a specific joint signed pattern recur in a way controls do not match?
```

This is a syndrome question, not a marginal metric question.

## 2. Stage A: read-only Phase B postmortem

Stage A uses existing Phase B outputs only. It must not generate new systems.

Inputs:

```text
phase_b_design_metric_rows.csv
phase_b_design_control_rows.csv
phase_b_directional_effects.csv
phase_b_metric_family_recurrence.csv
phase_b_matched_recurrence_controls.csv
phase_b_recurrence_excess.csv
phase_b_control_quality_audit.csv
phase_b_no_target_audit.csv
phase_b_phase_c_readiness.csv
```

Required questions:

```text
Which controls matched the strongest recurrence rows?
Did neutral controls alone match the 0.6 recurrence?
Did fakeout controls alone match the 0.6 recurrence?
Did frontier-size controls erase the effect?
Did horizon-order controls match the effect?
Was recurrence mostly constrained_window_flow or one_step_local_flow?
Was recurrence concentrated in absolute windows or spread across phase-like windows?
Did full_state_hash or existing_low contribute to any readiness-like rows?
Which metric/probe/flow/window combinations were control-equivalent?
```

Required outputs:

```text
phase_b_postmortem_control_match_decomposition.csv
phase_b_postmortem_top_control_equivalent_rows.csv
phase_b_postmortem_control_match_by_control_type.csv
phase_b_postmortem_flow_mode_decomposition.csv
phase_b_postmortem_window_decomposition.csv
phase_b_postmortem_probe_dependency.csv
phase_b_postmortem_report.md
```

## 3. Preregistered syndrome library

Do not mine arbitrary syndromes until one separates.

Stage A/B must score a small preregistered library first.

Each syndrome is a signed vector over metric families, windows, and directions.

### 3.1 stabilizing_boundary_syndrome

Hypothesis:

```text
Boundary structure stabilizes the frontier and reduces open-ended transform noise.
```

Pattern:

```text
growth: frontier_growth_ratio decreases or remains low
support_turnover: support_turnover_rate decreases or stabilizes
transition_matrix: off_diagonal_transform_mass decreases
bottleneck: frontier_bottleneck_index increases
window_stability: window_metric_vector_l2_distance decreases or stays low
```

### 3.2 transition_boundary_syndrome

Hypothesis:

```text
Boundary structure appears as a transition event between frontier regimes.
```

Pattern:

```text
support_turnover: support_turnover_rate increases
transition_matrix: off_diagonal_transform_mass increases
window_stability: window_metric_vector_l2_distance increases
bottleneck: frontier_bottleneck_index changes in same or adjacent window
```

### 3.3 compression_funnel_syndrome

Hypothesis:

```text
Boundary structure funnels many possible futures through a narrower channel.
```

Pattern:

```text
growth: frontier_growth_ratio decreases
transition_matrix: transition_matrix_entropy decreases
bottleneck: frontier_bottleneck_index increases
support_turnover: lost_signature_rate increases or new_signature_rate decreases
```

### 3.4 diffusive_noise_syndrome

Hypothesis:

```text
Generic noise-like frontier mixing produces high turnover and high transition spread.
```

This is primarily a negative/control syndrome.

Pattern:

```text
support_turnover: support_turnover_rate increases
transition_matrix: off_diagonal_transform_mass increases
transition_matrix: transition_matrix_entropy increases
bottleneck: frontier_bottleneck_index decreases
window_stability: window_metric_vector_l2_distance increases
```

### 3.5 recurrence_cascade_syndrome

Hypothesis:

```text
Frontier structure cycles or returns through related signatures across windows.
```

Pattern:

```text
signature_distribution_js_to_next_window decreases after a high-turnover window
transition_matrix: diagonal_persistence_mass increases after off-diagonal transition
bottleneck: top_k_flow_concentration increases after transition
```

If `diagonal_persistence_mass` is not emitted in Phase B rows, compute it from available transition rows or mark component unavailable.

## 4. Syndrome scoring rules

For each syndrome component, compute a signed z-score or signed percentile relative to controls.

Required fields:

```text
syndrome_id
syndrome_component_id
metric_family
metric_name
window
flow_mode
probe_key
direction
observed_value
control_mean
control_std
signed_z
control_percentile
component_pass
```

A component passes if:

```text
signed direction matches the syndrome
and absolute signed_z >= configured threshold
```

Suggested initial threshold:

```text
abs(signed_z) >= 0.5
```

For syndrome-level score:

```text
syndrome_component_pass_fraction
syndrome_joint_pass_rate
syndrome_signed_score_mean
syndrome_signed_score_min
syndrome_window_coherence_score
syndrome_direction_stability
```

Primary syndrome recurrence:

```text
fraction of seeds/starts where required components pass simultaneously or within allowed adjacent windows
```

Do not let a syndrome pass based on one metric alone.

## 5. Syndrome multiplicity guardrail

Every output must record:

```text
syndrome_selection_mode: preregistered or exploratory
syndrome_multiplicity_count
component_count
window_pattern_count
false_discovery_risk_note
```

Only preregistered syndromes can support readiness for a new run.

Exploratory discovered syndromes must be marked:

```text
exploratory_only_not_for_readiness
```

## 6. Stage A syndrome smoke on existing rows

Compute syndrome scores from existing Phase B rows.

Required outputs:

```text
phase_b_syndrome_component_scores.csv
phase_b_syndrome_smoke.csv
phase_b_syndrome_vs_controls.csv
phase_b_syndrome_multiplicity_audit.csv
phase_b_syndrome_readiness.csv
```

Decision classes for Stage A:

```text
syndrome_smoke_positive_above_controls
syndrome_smoke_control_equivalent
syndrome_smoke_probe_dependent
syndrome_smoke_flow_mode_dependent
syndrome_smoke_window_fragile
syndrome_smoke_insufficient_data
```

Stage B is allowed only if at least one preregistered syndrome is not control-equivalent in Stage A, or if Stage A shows that missing mechanism controls are the dominant uncertainty.

## 7. Stage B: mechanism-control design-set rerun

Stage B is a small design-set-only rerun using the strongest preregistered syndromes from Stage A.

No holdout.

No alphabet expansion.

No n=6.

Suggested run shape:

```text
design groups: 10
fresh_seeds_per_group: 3 or 4
start_samples: 4 and 8
windows: canonical windows
flow_modes:
  constrained_window_flow
  one_step_local_flow
probes:
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple
  existing_low diagnostic only
  full_state_hash identity control only
mechanism controls:
  roughness_resampled_transform_control
  asymmetry_flip_sweep_control
  constraint_shuffle_or_resample_control if implementable
```

Stage B should be smaller than Phase B 10h. It is a mechanism-dependency audit, not a broader recurrence run.

## 8. Mechanism controls are dependency tests, not survival tests

Do not require syndrome survival under constraint/asymmetry perturbation.

Interpretation:

```text
baseline syndrome present + constraint/asymmetry perturbation degrades syndrome:
  mechanism-dependent signal

baseline syndrome present + perturbation preserves syndrome:
  likely generic phase signal

baseline syndrome present + tiny roughness kills syndrome:
  roughness-brittle artifact

baseline syndrome absent:
  no measurable syndrome
```

## 9. Mechanism-control implementation plan

Add a utility module:

```text
omega/rfs_mb0_future_landscape/mechanism_controls.py
```

Core API:

```text
make_mechanism_control_system(system, control_name, seed, strength, params=None)
```

It should return a system-like object with the same interface used by frontier-transform runners:

```text
states
edges
metadata
```

### 9.1 roughness_resampled_transform_control

Implement first.

Suggested method:

```text
copy relation graph
for fraction p of states or edges, resample outgoing targets
preserve out-degree if feasible
use same state set
```

Sweep:

```text
p = 0.01, 0.02, 0.05, 0.10, 0.20
```

Report:

```text
roughness_p
edge_resample_count
out_degree_preserved_flag
mean_out_degree_delta
edge_jaccard_vs_baseline
```

### 9.2 asymmetry_flip_sweep_control

Implement second.

Suggested method:

```text
identify directed edges without reverse counterpart
for fraction p, reverse direction or swap asymmetric edge target/source
preserve edge count
use same state set
```

Sweep:

```text
p = 0.01, 0.02, 0.05, 0.10, 0.20
```

Report:

```text
asymmetry_p
flipped_edge_count
edge_count_delta
mean_in_degree_delta
mean_out_degree_delta
reciprocity_delta
edge_jaccard_vs_baseline
```

### 9.3 constraint control

Before implementing, inspect relation generator/system metadata.

If explicit constraint metadata exists, implement:

```text
constraint_assignment_shuffle_control
```

Preferred behavior:

```text
preserve constraint counts/types/strength distribution
shuffle assignment to coordinates/relations/states
regenerate affected relation edges if necessary
```

If explicit constraint metadata does not exist, implement honestly named proxy:

```text
constraint_resampled_generation_control
```

Behavior:

```text
regenerate system with same non-constraint parameters
resample constraint seed or constraint assignment seed
preserve broad density/strength/out-degree targets where possible
```

Do not call this `constraint_shuffled_transform_control` unless the actual constraint assignments are shuffled.

Report:

```text
constraint_control_type
constraint_metadata_available
constraint_count_delta
constraint_strength_distribution_delta
edge_count_delta
mean_out_degree_delta
frontier_size_profile_delta
saturation_timing_delta
```

## 10. Gross substrate preservation audit

For every mechanism-control system, report:

```text
state_count_delta
edge_count_delta
mean_out_degree_delta
mean_in_degree_delta
reciprocity_delta
constraint_count_delta_if_available
frontier_size_profile_delta
support_growth_baseline_delta
saturation_timing_delta
control_destructiveness_score
```

If destructiveness is too high, mark:

```text
control_too_destructive
```

Suggested interpretation:

```text
control_too_destructive means the mechanism dependency result is underdetermined, not negative.
```

## 11. Mechanism dependency scoring

For each syndrome:

```text
baseline_syndrome_rate
fakeout_syndrome_rate
neutral_syndrome_rate
roughness_p01_rate
roughness_p02_rate
roughness_p05_rate
roughness_p10_rate
roughness_p20_rate
asymmetry_p01_rate
asymmetry_p02_rate
asymmetry_p05_rate
asymmetry_p10_rate
asymmetry_p20_rate
constraint_control_rate
```

Scores:

```text
generic_phase_score
mechanism_dependency_score
roughness_robustness_score
roughness_brittleness_score
control_destructiveness_score
```

Decision classes:

```text
mechanism_dependent_candidate_syndrome
generic_phase_syndrome
roughness_brittle_syndrome
control_equivalent_syndrome
constraint_control_missing_underdetermined
control_too_destructive_underdetermined
no_measurable_syndrome
```

Still do not emit candidate/Omega/agent/identity labels.

## 12. Optional Stage C: alphabet-shape diagnostic

Do not run Stage C unless Stage A/B are clean enough to justify it.

If allowed, run a tiny diagnostic only:

```text
3^5 baseline vs 4^4 same-state-count alphabet-shape transfer
```

Use knobs suggested in prior review:

```text
horizon_growth_contrast
wiring_role_class
self_recurrence_horizon
```

Purpose:

```text
Test whether alphabet=3/n=5 is too compressed and causes generic phase recurrence.
```

This is not scale-up, not holdout, and not candidate promotion.

Required output:

```text
alphabet_shape_syndrome_diagnostic.csv
```

## 13. Required outputs

Stage A outputs:

```text
phase_b_postmortem_report.md
phase_b_postmortem_control_match_decomposition.csv
phase_b_postmortem_top_control_equivalent_rows.csv
phase_b_postmortem_control_match_by_control_type.csv
phase_b_postmortem_flow_mode_decomposition.csv
phase_b_postmortem_window_decomposition.csv
phase_b_postmortem_probe_dependency.csv
phase_b_syndrome_component_scores.csv
phase_b_syndrome_smoke.csv
phase_b_syndrome_vs_controls.csv
phase_b_syndrome_multiplicity_audit.csv
phase_b_syndrome_readiness.csv
```

Stage B outputs:

```text
mechanism_control_system_manifest.csv
mechanism_control_substrate_preservation.csv
mechanism_control_syndrome_rates.csv
mechanism_control_dependency_scores.csv
mechanism_control_decision_summary.csv
frontier_transform_syndrome_mechanism_audit_report.md
errors.csv
status.json
output_manifest.json
```

Optional Stage C output:

```text
alphabet_shape_syndrome_diagnostic.csv
```

## 14. Final report requirements

Final report:

```text
frontier_transform_syndrome_mechanism_audit_report.md
```

Required sections:

```text
1. Claim boundary
2. Why marginal recurrence failed
3. Phase B postmortem: which controls matched 0.6 recurrence
4. Preregistered syndrome library
5. Syndrome smoke results from existing rows
6. Mechanism-control implementation status
7. Substrate preservation/destructiveness audit
8. Syndrome dependency curves
9. Decision summary
10. Whether alphabet-shape diagnostic is warranted
11. Output manifest
```

## 15. Acceptance criteria

Stage A accepted only if:

```text
no new systems generated
control match decomposition emitted
syndrome multiplicity audit emitted
preregistered syndromes marked separately from exploratory syndromes
full_state_hash/existing_low excluded from positive readiness
```

Stage B accepted only if:

```text
roughness sweep implemented or explicitly failed with error
asymmetry sweep implemented or explicitly failed with error
constraint control implemented or honestly marked proxy/unavailable
substrate preservation audit emitted
mechanism controls treated as dependency tests, not survival tests
no holdout scoring
no n=6
no alphabet expansion in main audit
```

## 16. Bottom line

The Phase B result does not say frontier transforms are useless.

It says marginal frontier-transform recurrence is too generic.

The next test is:

```text
Do preregistered joint signed frontier-transform syndromes separate from controls,
and do they show the expected dependency profile under constraint/asymmetry/roughness perturbations?
```

If yes, freeze the syndrome definition and consider holdout.

If no, write a frontier-transform measurement-limits note and stop scaling this detector.

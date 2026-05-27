# RFS-MB0 Frontier-Transform Syndrome Audit Addendum

Status: addendum to `docs/RFS_MB0_FRONTIER_TRANSFORM_SYNDROME_AND_MECHANISM_CONTROL_AUDIT_SPEC.md`

Purpose: tighten the next syndrome/mechanism-control run against overfitting, semantic smuggling, and marginal-rate false positives before Codex implements it.

The base spec is directionally correct. This addendum should be treated as binding for implementation.

## 0. Reason for addendum

The Phase B result showed that marginal frontier-transform recurrence is control-equivalent:

```text
observed recurrence up to about 0.6
control recurrence also about 0.6
recurrence_excess: 0.0
```

The next run must not simply search for a more elaborate combination that happens to separate in the same data.

The core risk is:

```text
syndrome overfit
```

and:

```text
semantic smuggling by metric-vector nickname
```

## 1. Metric-native syndrome IDs required

The implementation must use neutral syndrome IDs in code and outputs.

Preferred names:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag
SYN_B_high_turnover_high_offdiag_high_window_delta
SYN_C_low_growth_high_concentration_low_entropy
SYN_D_high_turnover_high_entropy_low_bottleneck_control
SYN_E_transition_then_persistence_cascade
```

Semantic names may appear only as optional informal descriptions:

```text
informal_name
informal_interpretation
```

Do not use the informal names as decision classes.

Do not emit labels such as:

```text
agent_like
identity_like_structure
valuer_like
future_interested_object
Omega_adjacent
```

## 2. Freeze the preregistered syndrome library before scoring

Before reading or scoring Phase B rows, write:

```text
syndrome_manifest.json
```

Required fields:

```text
syndrome_id
selection_mode: preregistered
component_count
metric_components
allowed_windows
allowed_window_relation
allowed_flow_modes
allowed_probes
component_signs
component_threshold_rule
minimum_component_pass_count
joint_pass_rule
informal_name_optional
```

The runner may also emit exploratory syndromes, but they must be marked:

```text
selection_mode: exploratory
readiness_allowed: false
```

Only preregistered syndromes can support a decision to proceed to mechanism-control rerun.

## 3. Existing Phase B rows are postmortem/hypothesis-generation only

Stage A uses existing Phase B data.

It may support:

```text
postmortem
sanity check
implementation debugging
hypothesis generation
```

It may not support:

```text
confirmation
candidate promotion
holdout readiness by itself
```

If a syndrome is designed or adjusted after looking at Phase B rows, it must be marked exploratory and cannot support readiness without a fresh frozen rerun.

## 4. Marginal-preserving joint controls are required

A syndrome is only interesting if its joint co-occurrence exceeds controls that preserve marginal component rates.

Add a control family:

```text
component_marginal_preserving_syndrome_control
```

Purpose:

```text
Given the observed marginal pass rates of individual syndrome components,
randomly permute component pass indicators across seeds/starts/windows while preserving each component marginal rate,
then compute expected joint syndrome pass rate.
```

Required outputs:

```text
phase_b_syndrome_marginal_preserving_controls.csv
```

Required fields:

```text
syndrome_id
replicate_id
component_id
component_marginal_rate
observed_joint_rate
control_joint_rate
joint_rate_excess
joint_rate_percentile
replicate_count
```

Suggested replicate count:

```text
replicates >= 100
```

If this control is not implemented, mark all syndrome positives:

```text
underdetermined_missing_marginal_preserving_control
```

## 5. Component ablation required for any positive syndrome

For any preregistered syndrome with apparent positive separation, compute:

```text
full_syndrome_score
leave_one_component_out_scores
best_single_component_score
best_pair_score
```

Required output:

```text
phase_b_syndrome_component_ablation.csv
```

A syndrome should not be treated as a joint syndrome if:

```text
one component explains nearly all separation
```

Suggested decision class:

```text
single_component_driven_not_joint_syndrome
```

## 6. Readiness requires joint separation, not marginal recurrence

Stage A readiness for mechanism-control rerun requires at least one preregistered syndrome with:

```text
observed_joint_rate > component_marginal_preserving_control_mean
joint_rate_percentile >= 0.80
not single-component-driven
not full_state_hash dependent
not existing_low dependent
not confined to placeholder controls
```

If no syndrome meets this, Stage B should not run unless the report explicitly says:

```text
Stage B is being run only to test missing mechanism-control uncertainty,
not because Stage A found a positive syndrome.
```

## 7. Control-match decomposition must identify which controls match 0.6

The Stage A postmortem must decompose recurrence/control equivalence by control family:

```text
matched_fakeout_window_control
neutral_generated_window_control
frontier_size_matched_window_control
horizon_order_shuffled_control
start_shuffled_control
probe_marginal_window_control
```

Required output:

```text
phase_b_postmortem_control_match_by_control_type.csv
```

Required fields:

```text
metric_family
metric_name
probe_key
flow_mode
window
observed_recurrence_rate
control_name
control_recurrence_mean
recurrence_excess_vs_this_control
control_match_flag
```

This table must answer:

```text
Do neutral controls alone match the strongest recurrence?
Do fakeout controls alone match it?
Does frontier-size matching erase it?
Does horizon-order shuffling erase it?
```

## 8. Mechanism controls are dependency profiles, not survival gates

The base spec already says this, but implementation must preserve it in decision logic.

Do not classify as failure merely because:

```text
constraint perturbation reduces syndrome rate
asymmetry perturbation reduces syndrome rate
```

Preferred interpretation:

```text
baseline present + generic controls low + constraint/asymmetry perturbation degrades:
  mechanism-dependent syndrome

baseline present + generic controls high + mechanism perturbations preserve:
  generic phase syndrome

baseline present + tiny roughness perturbation kills completely:
  roughness-brittle syndrome
```

## 9. Perturbation severity ladder is required

Do not run a single perturbation strength.

Required strengths for roughness/asymmetry where feasible:

```text
0.01
0.02
0.05
0.10
0.20
```

For constraint controls, if fractional perturbation is not meaningful, use:

```text
weak
medium
strong
```

and report exact implementation semantics.

## 10. Substrate preservation audit is required for mechanism controls

For every perturbed system, report:

```text
state_count_delta
edge_count_delta
mean_out_degree_delta
mean_in_degree_delta
reciprocity_delta
frontier_size_profile_delta
saturation_timing_delta
control_destructiveness_score
control_too_destructive_flag
```

If the control is too destructive, classify dependency result as:

```text
control_too_destructive_underdetermined
```

not negative.

## 11. Stage ordering is binding

Run in this order:

```text
1. Read-only Phase B postmortem.
2. Preregistered syndrome smoke on existing rows.
3. Marginal-preserving joint controls.
4. Component ablation for apparent positives.
5. Only then decide whether Stage B mechanism-control rerun is warranted.
```

Do not generate new systems before Stage A outputs are written.

## 12. Updated decision classes

Stage A decision classes:

```text
syndrome_smoke_joint_positive_above_marginal_controls
syndrome_smoke_control_equivalent
syndrome_smoke_single_component_driven
syndrome_smoke_probe_dependent
syndrome_smoke_flow_mode_dependent
syndrome_smoke_window_fragile
syndrome_smoke_insufficient_data
syndrome_smoke_exploratory_only
```

Stage B decision classes:

```text
mechanism_dependent_syndrome
mechanism_independent_generic_phase_syndrome
roughness_brittle_syndrome
constraint_control_missing_underdetermined
control_too_destructive_underdetermined
no_measurable_syndrome
```

Do not use:

```text
candidate_syndrome
```

unless explicitly defined as a non-Omega, non-agent, non-identity internal shorthand. Prefer `mechanism_dependent_syndrome`.

## 13. Bottom line

The next run is acceptable only if it treats syndrome detection as a guardrailed statistical/control problem, not a semantic ontology search.

The core question is:

```text
Can a small frozen set of metric-native joint signed frontier-transform syndromes beat marginal-preserving controls and show a coherent mechanism-dependency profile?
```

If not, the correct result is a clean measurement-limit note, not more syndrome mining.

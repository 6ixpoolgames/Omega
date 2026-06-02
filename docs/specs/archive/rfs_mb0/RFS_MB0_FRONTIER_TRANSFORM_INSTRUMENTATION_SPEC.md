# RFS-MB0 Frontier-Transform Instrumentation Spec

Status: branch-pivot implementation spec after endpoint/quotient probe instrumentation failure

Purpose: pivot MB0 instrumentation from endpoint/state-signature probes to horizon-window/frontier-transform probes. The current best read is that recurrent boundary structure may live in how reachable frontiers transform across horizons, not in the static labels of endpoint states.

This follows:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_INSTRUMENTATION_BRANCH_PIVOT_AND_PROBE_PANEL_SPEC.md
results/rfs_mb0_relation_atlas/20260527_instrumentation_phase_a_preflight/
```

Key Phase A outcome:

```text
available_axis_gate: fail
new_quotient_axis_gate: fail
passing design-set axes: constraint_axis only
all new endpoint/quotient probes failed to provide adequate usable quotient coverage
```

## 0. Conceptual correction

The previous detector over-weighted terminus observations:

```text
What does the reachable frontier look like at horizon H?
```

But the object of interest is likely defined by continuation structure:

```text
How does F_H become F_{H+1}, F_{H+2}, ... ?
```

Therefore horizons should not be treated only as separate endpoint snapshots. Each horizon plays into the next. Structure across horizons/time is part of the object definition.

New framing:

```text
future profile = horizon-indexed frontier transformation process
```

not merely:

```text
future profile = horizon-indexed endpoint signature distribution
```

## 1. Claim boundary

This branch does not claim:

```text
Omega detected
agent detected
identity detected
valuer detected
self detected
viability proven
scientific gate passed
```

Allowed claims:

```text
A frontier-transform metric is or is not instrumentally viable.
A recurrent boundary group shows or does not show transform-level recurrence above matched controls.
The endpoint-probe bottleneck is or is not bypassed by operator/window metrics.
```

Classification remains deferred.

## 2. Why endpoint probes failed

Endpoint/state probes ask:

```text
What kind of states are present in F_H?
```

The last instrumentation panel tried better state quotients:

```text
constraint_gradient_class
degree_profile_rank
constraint_cross_degree_rank
horizon_growth_contrast_v2
self_recurrence_horizon_v2
wiring_role_class_v2
```

But Phase A found only the constraint axis viable; new quotient axes were too collision-limited or otherwise not usable.

Interpretation:

```text
The recurrent structure may not be a static class of frontier states.
It may be a recurring transformation pattern in the evolution of reachable frontiers.
```

## 3. New measurement object

Define exact frontiers from a start state:

```text
F_H(start) = exact frontier at horizon H
```

Define a frontier-transform window:

```text
W = (start, H_a, H_b)
T_W = transform summary of F_Ha -> F_Hb
```

The instrument now measures properties of `T_W`, not only properties of `F_Hb`.

Canonical window set:

```text
0 -> 1
1 -> 2
2 -> 4
4 -> 8
8 -> 16
16 -> 24
24 -> 32
```

Optional adjacent windows when cheap:

```text
H -> H+1 for H <= 8
```

## 4. First frontier-transform metrics

### 4.1 Growth metrics

```text
frontier_growth_ratio = |F_b| / max(1, |F_a|)
frontier_growth_delta = |F_b| - |F_a|
log_frontier_growth_ratio
pre_saturation_growth_ratio
```

Purpose:

```text
measure expansion/contraction of reachable support across the window
```

### 4.2 Support turnover metrics

Use a coarse probe only to compare support classes across windows.

```text
support_turnover_rate = 1 - Jaccard(support(F_a), support(F_b))
support_persistence_rate = Jaccard(support(F_a), support(F_b))
new_signature_rate
lost_signature_rate
```

Purpose:

```text
measure whether the frontier preserves, replaces, or transforms its support basis
```

### 4.3 Transition matrix metrics

For a coarse quotient probe `q`, build a transition matrix from frontier states at `H_a` to next-reachable states at `H_b` or via one-step expansion inside the window.

```text
M_q[i,j] = mass from q-class i in F_a to q-class j in F_b
```

Metrics:

```text
transition_matrix_entropy
row_entropy_mean
column_entropy_mean
transition_matrix_sparsity
transition_matrix_rank_proxy
diagonal_persistence_mass
off_diagonal_transform_mass
```

Purpose:

```text
measure how frontier classes flow into future classes
```

### 4.4 Branch/merge metrics

```text
branching_factor_mean
branching_factor_std
merge_factor_mean
merge_factor_std
branch_merge_asymmetry
```

Purpose:

```text
separate expanding, converging, bottleneck, and diffuse transform regimes
```

### 4.5 Bottleneck metrics

```text
frontier_bottleneck_index
max_signature_flow_fraction
top_k_flow_concentration
min_cut_proxy_optional
```

Purpose:

```text
detect whether many possible futures pass through a narrow transform channel
```

### 4.6 Window stability metrics

```text
transform_profile_JS_to_previous_window
transform_profile_JS_to_next_window
window_persistence_length
transform_regime_change_score
```

Purpose:

```text
detect horizon-local regime changes rather than static endpoint differences
```

### 4.7 Perturbation-response metrics, optional Phase B

Apply small neutral perturbations to starts/frontiers/edges/constraints and compare transforms:

```text
transform_response_JS
support_recovery_rate
growth_recovery_rate
bottleneck_recovery_rate
```

Purpose:

```text
measure whether transform structure is robust or fragile
```

Do not include perturbation-response metrics in Phase A unless cheap and isolated.

## 5. Controls and nulls

Frontier-transform metrics need their own controls. Endpoint controls are not sufficient.

Required controls:

```text
frontier_size_matched_window_control
probe_marginal_window_control
horizon_order_shuffled_control
start_shuffled_control
matched_fakeout_window_control
neutral_generated_window_control
window_local_random_flow_control
constraint_shuffled_transform_control
asymmetry_shuffled_transform_control
roughness_resampled_transform_control
```

Critical null question:

```text
Does F_Ha -> F_Hb contain structure beyond what is expected from |F_Ha|, |F_Hb|, probe marginals, and horizon timing?
```

## 6. Anti-noise / fine-tuning guardrails

The previous branch already identified the risk of promoting better-looking noise.

This branch must preserve:

```text
pre-registered metrics
Phase A preflight before detection
Design/holdout split
frozen thresholds before holdout
multiplicity audit
matched controls
promotion disabled
```

Additional transform-specific guardrails:

```text
window_count_reported
metric_count_reported
control_count_reported
horizon_window_multiplicity_reported
```

Do not select windows after seeing candidate counts without marking the result exploratory.

## 7. Phase A: transform metric viability preflight

Goal:

```text
Determine whether frontier-transform metrics produce non-degenerate, non-saturated, non-noise-dominated measurements before candidate detection.
```

Inputs:

```text
10 design recurrent-boundary groups
matched fakeout groups
neutral generated systems
holdout groups listed but not scored
```

Do not score holdout groups in Phase A.

Evaluate metrics across canonical windows using existing coarse probes only as bins:

```text
constraint_profile_hash
constraint_violation_count_plus_local_tuple
existing_low diagnostic
full_state_hash control only, optional
```

Do not depend on failed new endpoint quotient probes.

Required outputs:

```text
frontier_transform_metric_manifest.json
frontier_transform_viability_preflight.csv
frontier_transform_metric_summary.md
frontier_transform_window_multiplicity_audit.csv
frontier_transform_control_manifest.csv
frontier_transform_holdout_split.csv
status.json
output_manifest.json
```

Preflight viability criteria:

```text
metric not constant across windows
metric not saturated in >80% rows
metric not support-floor-only
metric differs between recurrent-boundary design groups and matched fakeout/neutral controls in at least descriptive effect-size form
metric stable enough across seeds/starts to estimate recurrence
```

Phase A does not promote candidates.

## 8. Phase B: design-set transform recurrence

Only run if Phase A finds at least two viable transform metrics from different metric families.

Inputs:

```text
10 design groups
frozen transform metrics
frozen windows or pre-registered window set
matched transform controls
```

Metrics:

```text
transform_recurrence_rate_by_seed
transform_recurrence_rate_by_start
transform_recurrence_rate_by_window
transform_excess_vs_controls
transform_percentile_vs_controls
```

Required outputs:

```text
design_frontier_transform_detection.csv
design_frontier_transform_controls.csv
design_frontier_transform_recurrence_summary.md
```

No holdout scoring yet.

## 9. Phase C: holdout transform recurrence

Only run if Phase B shows recurrence above controls under frozen metrics and windows.

Inputs:

```text
10 holdout groups
same metrics
same thresholds
same windows
same controls
```

Required outputs:

```text
holdout_frontier_transform_detection.csv
holdout_frontier_transform_controls.csv
holdout_frontier_transform_recurrence_summary.md
```

Pass condition:

```text
holdout transform recurrence exceeds matched controls under frozen metrics and windows
```

## 10. Detection classes

Use detection classes only. Do not classify identity or agency.

```text
transform_metric_not_viable
transform_measurement_limited
frontier_transform_recurrent_above_controls
frontier_transform_recurrent_but_control_equivalent
frontier_transform_sparse_regime_only
frontier_transform_saturation_limited
frontier_transform_window_fragile
frontier_transform_seed_fragile
frontier_transform_holdout_failed
frontier_transform_holdout_supported
```

## 11. Scale and alphabet policy

Do not expand alphabet or state size during Phase A/B/C.

The purpose is to validate the instrument, not the substrate scale.

If Phase C passes, then and only then consider transfer ladder:

```text
3^5 baseline
4^4 same-state-count alphabet-shape transfer
3^6 dimension transfer
4^5 mild expanded transfer
```

No n=6 or alphabet expansion until transform instrumentation passes holdout.

## 12. Why this is not path metrics revival

This branch is not the parked path-metric program.

Difference:

```text
path metrics:
  sequence/bigram/trigram-like structure along sampled paths

frontier-transform metrics:
  operator-like summaries of how reachable sets transform across horizon windows
```

The object is not path language. It is the transformation of future possibility surfaces.

## 13. Report requirements

Final Phase A report:

```text
rfs_mb0_frontier_transform_instrumentation_phase_a_report.md
```

Required sections:

```text
1. Claim boundary
2. Why endpoint probes failed
3. Frontier-transform measurement definition
4. Metric manifest
5. Window set and multiplicity audit
6. Control manifest
7. Viability preflight results
8. Design/fakeout/neutral descriptive comparison
9. Decision: Phase B allowed or blocked
10. Output manifest
```

If Phase B/C run later, write:

```text
rfs_mb0_frontier_transform_detection_report.md
```

## 14. Acceptance criteria for Phase A

Phase A accepted only if:

```text
no holdout scoring occurred
metric manifest exists
window multiplicity audit exists
control manifest exists
at least two transform metric families are evaluated
controls are generated for every reported metric/window
status.json final and not RUNNING
```

Phase B allowed only if:

```text
at least two transform metric families are viable
at least one metric family differs from controls descriptively on design groups
metrics are not dominated by support floor or support ceiling
```

## 15. Bottom line

The next MB0 question is not:

```text
Can we label endpoint states better?
```

It is:

```text
Can we measure how reachable-future frontiers transform across horizons?
```

If the recurrent structure lives in the temporal/operator profile of frontiers, this is the missing instrumentation layer.

# RFS-MB0 Frontier-Transform Phase B0 Control/Flow Repair Spec

Status: immediate Codex implementation spec after frontier-transform Phase A and external review

Purpose: repair the semantic interpretation of frontier-transform metrics before running true Phase B recurrence. Phase A showed that horizon-window/frontier-transform metrics are non-degenerate and worth pursuing, but several implementation/control issues must be fixed before recurrence testing can be trusted.

This follows:

```text
docs/RFS_MB0_FRONTIER_TRANSFORM_INSTRUMENTATION_SPEC.md
results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_a/
```

Phase A result:

```text
jobs_completed: 160 / 160
row_count: 4480
errors: 0
status: COMPLETED
viable non-control metric families:
  bottleneck
  branch_merge
  growth
  support_turnover
  transition_matrix
  window_stability
```

Claim boundary:

```text
Phase A was not candidate detection.
Phase B0 is not candidate detection.
No holdout scoring.
No n=6.
No alphabet expansion.
No agent/identity/value claims.
```

## 0. Why B0 exists

Phase A proved that frontier-transform instrumentation is worth pursuing. It did not prove that the current transform metrics are semantically clean enough for recurrence testing.

External review identified four issues:

```text
1. Viability did not report effect direction as a first-class object.
2. transition_counts silently fell back from frontier-constrained flow to all outgoing edges.
3. window stability used JS on a coarse four-integer sketch rather than a real distribution or vector distance.
4. control manifest listed controls that were not actually computed.
```

Therefore do not run true Phase B yet.

Run B0 first.

B0 asks:

```text
Can the frontier-transform measurement be made semantically clean enough for recurrence testing?
```

not:

```text
Do recurrent boundary candidates pass?
```

## 1. Fix transition-flow semantics

### 1.1 Remove silent fallback

Current issue:

```text
If a state in F_a has no immediate outgoing target in F_b,
the code falls back to all outgoing edges.
```

This mixes two different objects:

```text
frontier-constrained window flow
one-step local outgoing flow
```

Required change:

Do not silently fallback.

Emit separate flow modes:

```text
constrained_window_flow:
  count only outgoing edges from F_a states whose targets are in F_b
  skip F_a states with no target in F_b

one_step_local_flow:
  count all outgoing edges from F_a states, regardless of F_b membership

window_reach_flow_optional:
  approximate or exact bounded reachability from F_a to F_b through intermediate steps when feasible
```

For every transform row, report:

```text
flow_mode
fa_state_count
fb_state_count
states_with_window_target
states_without_window_target
no_window_target_rate
edge_count_total_from_fa
edge_count_into_fb
edge_into_fb_rate
skipped_state_count
```

### 1.2 Metrics by flow mode

Transition-matrix metrics must be namespaced by flow mode or emitted as separate rows.

Required columns:

```text
flow_mode
transition_matrix_entropy
row_entropy_mean
column_entropy_mean
transition_matrix_sparsity
transition_matrix_rank_proxy
diagonal_persistence_mass
off_diagonal_transform_mass
```

Do not compare a constrained metric to an unconstrained metric without labeling the flow mode.

## 2. Fix window-stability metrics

### 2.1 Do not use JS on four-integer sketches

Current issue:

```text
profile_counts builds a four-key dictionary from integer-bucketed scalar metrics,
then JS divergence is applied as if this were a meaningful distribution.
```

Required change:

Use two stability families:

```text
metric_vector_stability:
  normalized real-valued metric vector distance between adjacent windows

transition_distribution_stability:
  JS divergence only on actual transition matrices or signature distributions
```

### 2.2 Required window-stability metrics

For metric vectors:

```text
window_metric_vector_l2_distance_to_previous
window_metric_vector_l2_distance_to_next
window_metric_vector_cosine_distance_to_previous
window_metric_vector_cosine_distance_to_next
window_metric_vector_max_abs_delta_to_previous
window_metric_vector_max_abs_delta_to_next
```

For real distributions:

```text
transition_matrix_js_to_previous_window
transition_matrix_js_to_next_window
signature_distribution_js_to_previous_window
signature_distribution_js_to_next_window
```

Report which stability family is used in each row:

```text
stability_metric_family
```

## 3. Directional effects are first-class

Phase A viable metrics were mostly negative in design-vs-control effect direction. That is not automatically bad.

Boundary regimes may genuinely show:

```text
lower growth
lower turnover
lower off-diagonal transform mass
lower branching
higher bottlenecking
more stabilization
```

So B0 must report both signed and absolute effects.

For every metric/control comparison, report:

```text
design_mean
control_mean
signed_effect_size
absolute_effect_size
effect_direction
control_percentile
extremeness_percentile
```

Effect direction values:

```text
design_above_control
design_below_control
control_equivalent
```

Do not require positive effects. Require interpretable effects.

Viability after B0 should consider:

```text
absolute_effect_size >= configured threshold
OR extremeness_percentile above configured threshold
```

while preserving signed direction separately.

Suggested initial descriptive threshold:

```text
absolute_effect_size >= 0.10
```

This is descriptive only. It is not a promotion gate.

## 4. Compute real transform controls

The Phase A control manifest was acceptable for preflight, but B0 must compute real controls.

Minimum required controls:

```text
matched_fakeout_window_control
neutral_generated_window_control
frontier_size_matched_window_control
probe_marginal_window_control
horizon_order_shuffled_control
start_shuffled_control
constraint_shuffled_transform_control
```

Strongly recommended if cheap:

```text
asymmetry_shuffled_transform_control
roughness_resampled_transform_control
window_local_random_flow_control
```

### 4.1 horizon_order_shuffled_control

Purpose:

```text
test whether sequential horizon order matters
```

Implementation:

```text
shuffle or permute window labels/order within a start/seed context
compare transform profile recurrence to true ordered windows
```

Required output fields:

```text
control_name = horizon_order_shuffled_control
shuffle_seed
true_window
shuffled_window
metric_name
true_value
control_value
signed_delta
absolute_delta
```

### 4.2 constraint_shuffled_transform_control

Purpose:

```text
test whether observed transform effects depend on constraint geometry rather than parameter confounding
```

Implementation:

```text
preserve broad constraint counts/density where possible
shuffle constraint assignments, targets, or constraint labels according to existing constraint representation
recompute frontier transforms
```

If exact constraint shuffle is not available, implement a conservative placeholder with explicit status:

```text
constraint_shuffled_transform_control_status = not_available
```

Do not silently substitute neutral controls for constraint-shuffled controls.

### 4.3 start_shuffled_control

Purpose:

```text
test start sensitivity and path-dependence
```

Implementation:

```text
sample starts from same generated system but outside selected start set
match start count
compare transform profiles
```

### 4.4 frontier_size_matched_window_control

Purpose:

```text
test whether effect is explained by |F_a| and |F_b| only
```

Implementation:

```text
select windows from neutral/fakeout/design contexts with similar frontier_size_a and frontier_size_b
match within tolerance or nearest-neighbor match
```

Report:

```text
frontier_size_match_distance
frontier_size_match_quality
```

### 4.5 probe_marginal_window_control

Purpose:

```text
test whether transition profile is explained by marginal signature distributions at F_a and F_b
```

Implementation:

```text
shuffle source/target pairings while preserving q(F_a) and q(F_b) marginal counts
recompute transition-matrix metrics
```

## 5. B0 run shape

Use design set only.

```text
design groups: 10
holdout groups: listed only, not scored
fresh_seeds_per_group: 2 initially
start_samples: 4 initially
windows: same canonical windows as Phase A
probes used as bins:
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple
  existing_low diagnostic only
  full_state_hash identity control only optional
promotion_enabled: false
candidate_detection_enabled: false
holdout_detection_enabled: false
```

No n=6.

No alphabet expansion.

No endpoint-probe redesign in this run.

## 6. Required outputs

```text
rfs_mb0_frontier_transform_phase_b0_control_flow_report.md
frontier_transform_b0_metric_rows.csv
frontier_transform_b0_flow_mode_summary.csv
frontier_transform_b0_no_target_audit.csv
frontier_transform_b0_window_stability.csv
frontier_transform_b0_control_manifest.csv
frontier_transform_b0_computed_controls.csv
frontier_transform_b0_control_effects.csv
frontier_transform_b0_directional_effects.csv
frontier_transform_b0_metric_viability.csv
frontier_transform_b0_phase_b_readiness.csv
frontier_transform_b0_holdout_status.csv
errors.csv
status.json
output_manifest.json
```

## 7. Required report sections

The B0 report must include:

```text
1. Claim boundary
2. What B0 fixes relative to Phase A
3. Flow-mode separation
4. No-window-target / skipped-state audit
5. Window-stability metric repair
6. Computed transform controls
7. Signed and absolute effect directions
8. Metric viability after flow/control repair
9. Phase B readiness decision
10. Holdout status
11. Output manifest
```

## 8. Phase B readiness criteria

True Phase B design-set recurrence is allowed only if all are true:

```text
1. No silent fallback remains in transition flow.
2. constrained_window_flow and one_step_local_flow are separated.
3. no_window_target_rate is reported and not catastrophic for all key windows.
4. window stability no longer depends on four-integer JS sketches.
5. horizon_order_shuffled_control is computed.
6. start_shuffled_control is computed.
7. frontier_size_matched_window_control is computed.
8. probe_marginal_window_control is computed for transition-matrix metrics.
9. constraint_shuffled_transform_control is computed or explicitly marked unavailable.
10. at least two metric families remain viable after the flow/control fix.
11. signed and absolute effects are reported for every metric family.
12. holdout scoring count remains zero.
```

If fewer than two metric families remain viable after fixes, Phase B is blocked.

## 9. Decision classes

B0 should emit exactly one decision class:

```text
phase_b_ready
phase_b_blocked_flow_semantics
phase_b_blocked_controls_missing
phase_b_blocked_metric_collapse
phase_b_blocked_effects_control_equivalent
phase_b_blocked_holdout_contaminated
```

## 10. Important interpretation rules

### Negative effects can be signal

Do not treat negative design-vs-control effects as failure.

A boundary regime may be characterized by reduced growth, reduced turnover, increased bottlenecking, or stabilization.

Use:

```text
signed effect for interpretation
absolute effect / percentile extremeness for detection viability
```

### Phase B is still not validation

Even if B0 passes, Phase B will only test design-set recurrence.

Holdout Phase C remains separate and frozen.

### Do not retune windows after B0

If B0 suggests only some windows are informative, report that descriptively. Do not silently select windows for Phase B after seeing design effects unless the run is labeled exploratory.

Preferred:

```text
carry canonical windows forward
or pre-register a reduced window set with explicit reason before Phase B
```

## 11. Bottom line

Phase A showed that frontier-transform instrumentation is viable enough to pursue.

B0 must now clean the semantics:

```text
separate actual frontier-window flow from local flow
compute real controls
repair window-stability metrics
report signed effects honestly
```

Only after B0 passes should true Phase B recurrence run.

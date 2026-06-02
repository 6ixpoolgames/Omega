# RFS-MB0 Detector Instrumentation Repair Spec

Status: immediate Codex implementation spec after boundary recurrence measurement-limits result and external bug audit

Purpose: repair detector instrumentation before treating the RFS-MB0 boundary recurrence measurement-limits result as final. The previous focused pass found reproducible boundary structure, but all selected groups were classified as probe-limited. Several bugs and design issues may be making that result harder to escape than it should be.

Relevant artifacts:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_BOUNDARY_RECURRENCE_REPAIR_AND_FOCUSED_PASS_SPEC.md
results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/
results/rfs_mb0_relation_atlas/20260527_focused_boundary_recurrence_scaled/
docs/research_notes/validation_design/rfs_mb0_boundary_recurrence_measurement_limits.md
```

Observed focused-pass result:

```text
20 / 20 selected groups were evidence-probe recurrent
20 / 20 were non-saturation recurrent by row-level saturation flag
0 / 20 were clean recurrent boundary candidates
20 / 20 were classified as evidence_probe_recurrent_but_probe_limited
```

## 0. Strategic interpretation

Treat the current measurement-limits result as provisional.

Before the audit, the read was:

```text
We have recurrent boundary structure, but all of it remains probe-limited.
```

Revised read:

```text
We have recurrent boundary structure, but the runner may overlabel it as saturation/probe-limited because sparse rows, correlated probes, coarse probe-limit labels, support-insensitive scoring, and missing focused matched controls distort the gate.
```

Do not run n=6. Do not run a broader atlas. Do not pivot substrate yet. First repair instrumentation and rerun the same 20 focused groups.

## 1. Claim boundary

Allowed after repair:

```text
instrumentation was corrected
the same 20 focused groups were rerun under corrected logic
the prior 20/20 probe-limited result was confirmed, weakened, or partially overturned
```

Not allowed:

```text
Omega detected
agency detected
identity detected
valuer detected
viability detected
path-process object detected
scientific gate passed
n=6 transfer completed unless actually run
stable candidate band promoted without matched controls and probe repair
```

## 2. Repair support ceiling vs support floor

### Problem

The current detector sets `support_ceiling_flag` for both high support and sparse support:

```text
support_fraction >= 0.90 OR support_fraction <= 0.05
```

These are opposite regimes. Sparse frontier support is not saturation.

### Required change

Split the flags:

```text
support_ceiling_flag: support_fraction >= 0.90
support_floor_flag: support_fraction <= 0.05
support_extreme_flag: ceiling OR floor
```

`support_ceiling_flag` means saturation/ceiling only. `support_floor_flag` means sparse/floor only. `support_extreme_flag` is diagnostic only and must not be treated as saturation.

### Downstream updates

Update all saturation/blocker logic to stop treating floor as ceiling:

```text
saturation_flag
saturation_decomposition
saturation_boundary_audit_rows
stable_candidate_blockers
candidate_blocker_summary_rows
classification_if_saturation_rows_excluded
```

Do not let support floor automatically block stable candidate status. Report it separately as `support_floor_limited` or `sparse_frontier_limited`.

### Required outputs

Add row fields:

```text
support_ceiling_flag
support_floor_flag
support_extreme_flag
support_regime_class
```

where support_regime_class is one of:

```text
support_floor_sparse
middle_support_regime
support_ceiling_saturated
```

Add `support_regime_summary.csv` with row counts, candidate-like counts, probe-limited counts, and matched-control-supported counts by support regime.

## 3. Decompose probe-limited labels

### Problem

Current probe-limited logic collapses at least two different issues:

```text
collision-limited: probe too coarse
identity-like-limited: probe too close to full-state identity
```

These require opposite repairs.

### Required row fields

Add:

```text
collision_limited_flag
identity_like_limited_flag
probe_floor_limited_flag
probe_ceiling_limited_flag
probe_local_only_flag
probe_limited_flag
probe_limit_reason
```

`probe_limit_reason` should be a semicolon-separated list from:

```text
collision_limited
identity_like_limited
support_floor_limited
support_ceiling_limited
probe_local_only
```

### Required outputs

Add:

```text
probe_limit_decomposition.csv
probe_limit_reason_summary.csv
```

The final report must state whether the prior 20/20 probe-limited result was dominated by collision, identity-like behavior, support floor, support ceiling, probe-local recurrence, or mixed reasons.

## 4. Redefine cross-probe recurrence by independent probe axes

### Problem

The current recurrence gate treats any two evidence probes as independent. But `coordinate_tuple_k3` and `coordinate_tuple_k4` are correlated; k4 extends k3.

### Required probe roles and axes

Define roles:

```text
coordinate_tuple_k3: evidence
coordinate_tuple_k4: evidence
constraint_profile_hash: evidence
constraint_violation_count_plus_local_tuple: evidence
existing_low: diagnostic
relation_role: diagnostic
full_state_hash: control
full_state_strict: control
```

Define axes:

```text
coordinate_tuple_k3: coordinate_axis
coordinate_tuple_k4: coordinate_axis
constraint_profile_hash: constraint_axis
constraint_violation_count_plus_local_tuple: constraint_axis
existing_low: low_projection_axis
relation_role: relation_role_axis
full_state_hash: identity_axis
full_state_strict: identity_axis
```

Unknown probes should be `unknown_diagnostic` / `unknown_axis` and excluded from evidence recurrence gates.

### New recurrence gates

For each group report:

```text
coordinate_axis_hit
constraint_axis_hit
any_evidence_probe_recurrent_flag
same_axis_multi_probe_recurrent_flag
independent_axis_recurrent_flag
independent_axis_non_saturation_recurrent_flag
independent_axis_clean_recurrent_flag
```

`independent_axis_recurrent_flag` requires coordinate-axis evidence and constraint-axis evidence. It is not equivalent to evidence probe count >= 2.

### Required output

Add:

```text
probe_axis_recurrence_summary.csv
```

Suggested classes:

```text
no_evidence_recurrence
same_axis_only_coordinate
same_axis_only_constraint
independent_axis_recurrent_but_limited
independent_axis_clean_recurrent
unknown_axis_only
```

## 5. Add support-aware deformation scoring

### Problem

Current helper scoring effectively uses only JS-to-null terms and ignores set-level support metrics. This can undersort support-deformation groups with strong support-set differences but weak distributional JS.

### Required score decomposition

Add scores:

```text
js_distribution_score
support_set_score
mass_concentration_score
support_growth_score
combined_deformation_score
```

Initial weighting:

```text
combined = 0.40 * js_distribution_score
         + 0.35 * support_set_score
         + 0.15 * mass_concentration_score
         + 0.10 * support_growth_score
```

If support_growth_score is not robust, set it to 0 and report that explicitly. Do not silently omit support-set effects.

### Required outputs

Add:

```text
deformation_score_decomposition.csv
focused_group_selection_score_audit.csv
```

The score audit should show whether the same 20 groups would still be selected under the support-aware score and which support-heavy groups were previously undersorted.

## 6. Compute matched controls for focused generated systems

### Problem

The focused recurrence pass did not compute matched-control bundles for newly generated focused systems. Without matched controls, positive rows remain local/pre-control.

### Required control bundle

For each focused generated row, compute controls at the same group, parameter variant, probe family/axis, start count, start index, and horizon where possible.

Minimum controls:

```text
triviality null bundle
support null bundle
frontier-size matched diagnostic null
probe-marginal diagnostic null
same-parameter fresh-seed noncandidate controls where available
same-group shuffled-start controls where available
```

If full controls are too expensive, compute a small bundle but report `control_count` and `weak_control_bundle_flag`.

### Required metrics

For each candidate-like focused row:

```text
candidate_metric
control_mean
control_std
candidate_minus_control_mean
candidate_control_percentile
control_count
weak_control_bundle_flag
support_jaccard_vs_matched_control
TV_distance_to_matched_control
JS_to_matched_control
combined_score_vs_matched_control
```

### Required outputs

Add:

```text
focused_matched_control_bundle.csv
focused_matched_control_rank_effect.csv
focused_margin_sensitivity.csv
```

Classify rows as:

```text
matched_control_supported_local_candidate
matched_control_equivalent
weak_control_bundle
margin_fragile
underdetermined_missing_controls
```

No row can be called clean recurrent candidate unless it has matched-control support.

## 7. Corrected clean recurrent candidate definition

A group can be `clean_recurrent_boundary_candidate` only if all are true:

```text
fresh_seed_count >= 3
independent_axis_clean_recurrent_flag = true
matched-control-supported rows exist in coordinate_axis and constraint_axis
support_ceiling_flag = false for supporting rows
collision_limited_flag = false for supporting rows
identity_like_limited_flag = false for supporting rows
weak_control_bundle_flag = false
margin stability is moderate or strong, not fragile-only
```

If support floor is present but otherwise clean, classify separately:

```text
sparse_regime_recurrent_candidate_pending_floor_audit
```

Do not merge sparse/floor cases into saturation.

## 8. Rerun plan: exact same 20 focused groups

After implementing the repairs, rerun the same 20 groups from the scaled focused pass.

Input:

```text
results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv
```

Run shape:

```text
groups: same 20
fresh_seeds_per_group: 4
start_samples: same as previous focused pass
horizons: same as previous focused pass
probe families:
  coordinate_tuple_k3
  coordinate_tuple_k4
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple
  existing_low diagnostic only
  full_state_hash control only, optional
workers: 18
promotion_enabled: false
matched_controls_enabled: true
support_floor_split_enabled: true
probe_limit_decomposition_enabled: true
axis_recurrence_enabled: true
support_aware_scoring_enabled: true
```

Do not change substrate, relation generator, or parameter selection in this rerun. The goal is to isolate instrumentation effects.

## 9. Required final report

Name:

```text
rfs_mb0_detector_instrumentation_repair_report.md
```

Sections:

```text
1. Claim boundary
2. What changed in instrumentation
3. Support ceiling/floor split result
4. Probe limitation decomposition result
5. Independent probe-axis recurrence result
6. Support-aware score selection audit
7. Focused matched-control result
8. Reclassification of the original 20 groups
9. Comparison to prior measurement-limits result
10. Decision: confirmed measurement limit / partial rescue / continue focused repair
11. Output manifest
```

## 10. Required outputs

```text
rfs_mb0_detector_instrumentation_repair_report.md
support_regime_summary.csv
probe_limit_decomposition.csv
probe_limit_reason_summary.csv
probe_axis_recurrence_summary.csv
deformation_score_decomposition.csv
focused_group_selection_score_audit.csv
focused_matched_control_bundle.csv
focused_matched_control_rank_effect.csv
focused_margin_sensitivity.csv
corrected_group_classification.csv
corrected_measurement_limits_summary.csv
output_manifest.json
status.json
```

## 11. Corrected group classifications

Classify each of the 20 groups as one of:

```text
clean_recurrent_boundary_candidate
sparse_regime_recurrent_candidate_pending_floor_audit
independent_axis_recurrent_but_collision_limited
independent_axis_recurrent_but_identity_like_limited
same_axis_only_recurrence
matched_control_equivalent_recurrence
weak_control_bundle_recurrence
support_floor_limited_recurrence
support_ceiling_limited_recurrence
measurement_limited_recurrence_confirmed
underdetermined_after_repair
```

The old class `evidence_probe_recurrent_but_probe_limited` may appear only as a legacy comparison field, not as a final class.

## 12. Decision gates after rerun

### Measurement limit confirmed

If all 20 remain limited after corrected instrumentation and matched controls, finalize the measurement-limits note and pause scaling.

### Partial rescue

If 1-3 groups become clean or sparse-regime pending candidates, run one tiny confirmation pass on only those groups, still n=5, with matched controls.

### Strong rescue

If more than 3 groups become clean recurrent boundary candidates, run a small n=5 confirmation atlas around those groups. Still no n=6 until confirmation passes.

### Probe design failure

If groups are independently recurrent but mostly collision-limited, design richer non-identity probes.

If groups are independently recurrent but mostly identity-like-limited, design coarser mechanistic probes.

If groups are mostly same-axis only, design more independent probe axes before further runs.

## 13. Acceptance criteria

Do not accept the repair unless all are true:

```text
support_ceiling_flag no longer fires on support_fraction <= 0.05
support_floor_flag exists and is reported
probe_limit_decomposition.csv exists
probe_limit_reason_summary.csv exists
probe_axis_recurrence_summary.csv exists
cross-probe recurrence is axis-based, not count >= 2 only
deformation_score_decomposition.csv includes support-set terms
focused matched controls are computed or explicitly marked weak/missing per row
corrected_group_classification.csv contains all 20 original groups
final report compares old vs corrected classifications
status.json is final and not RUNNING
```

## 14. Bottom line

The current MB0 state is not `no signal`.

It is:

```text
recurrent boundary signal under a flawed measurement stack
```

The next action is detector instrumentation repair and exact rerun of the same 20 groups. Only after that can we decide whether MB0 is truly at a measurement limit or whether recurrent boundary structure was hidden by detector bugs.

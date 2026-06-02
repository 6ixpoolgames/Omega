# RFS-MB0 Boundary Deformation Guardrail and Quotient Probe Spec

Status: immediate Codex implementation spec after detector instrumentation repair

Purpose: tighten detection around recurrent boundary structures without drifting into raw-state identity detection or premature agent/identity classification.

This spec follows:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_DETECTOR_INSTRUMENTATION_REPAIR_SPEC.md
results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/
```

Recent corrected result:

```text
independent_axis_recurrent_but_collision_limited: 16
weak_control_bundle_recurrence: 4
clean_recurrent_boundary_candidate: 0
sparse_regime_recurrent_candidate_pending_floor_audit: 0
```

Probe-limit reason rows:

```text
collision_limited: 22789
identity_like_limited: 1517
support_ceiling_limited: 5692
support_floor_limited: 5994
none: 14851
```

Interpretation:

```text
Recurrent boundary structure exists.
The main current limit is collision, not identity-like overresolution.
The next task is to reduce collision while preserving explicit anti-fingerprint guardrails.
```

## 0. Conceptual frame

The active target is not agent classification or identity theory.

The active target is:

```text
recurrent boundary deformation detection
```

The detected structures may sit near what later theories would call identity-like or agent-like, but this branch is not trying to classify them yet.

This is not a retreat from tightening detection. It is a separation of tasks:

```text
detect recurrent boundary deformation now
classify structures later, maybe in a different theory layer
```

Use neutral language in code and reports:

```text
boundary_structure
recurrent_boundary_structure
quotient_resolved_deformation
collision_limited_deformation
path_dependent_recurrent_structure
identity_leakage_probe
identity_like_control_probe
```

Avoid positive classes such as:

```text
agent_like
valuer_like
self_like
identity_detected
```

except as explicitly deferred/non-active labels in documentation.

## 1. Guardrail principle

A probe may become more informative, but it cannot become evidence merely by becoming a fingerprint.

The goal is not to avoid all identity-adjacent resolution. The goal is to prevent raw-state fingerprinting from masquerading as deformation evidence.

Therefore every proposed evidence probe must report its resolution envelope:

```text
how much it compresses
how close it is to identity
how much collision remains
whether it is stable under threshold settings
whether recurrence exceeds matched recurrence controls
```

## 2. Configurable probe-resolution thresholds

Do not hard-code bucket thresholds as final constants.

Implement them as configuration from the start.

Suggested config name:

```text
probe_resolution_thresholds.json
```

Default initial values:

```text
identity_like:
  singleton_bucket_fraction: 0.50
  average_bucket_size: 1.50
  entropy_ceiling_fraction: 0.90

high_resolution_watch:
  singleton_bucket_fraction: 0.25
  average_bucket_size: 3.00
  entropy_ceiling_fraction: 0.75

too_coarse_collision:
  collision_rate: 0.90
  effective_signature_count_min_fraction: 0.05
```

These values are start points, not claims.

## 3. Threshold sweep

Run a small threshold sweep in every guardrail audit.

Minimum threshold profiles:

```text
strict
default
lenient
```

Suggested profile values:

```text
strict:
  identity_like.singleton_bucket_fraction: 0.35
  high_resolution_watch.singleton_bucket_fraction: 0.20
  too_coarse_collision.collision_rate: 0.85

default:
  identity_like.singleton_bucket_fraction: 0.50
  high_resolution_watch.singleton_bucket_fraction: 0.25
  too_coarse_collision.collision_rate: 0.90

lenient:
  identity_like.singleton_bucket_fraction: 0.65
  high_resolution_watch.singleton_bucket_fraction: 0.35
  too_coarse_collision.collision_rate: 0.95
```

Report for every group/probe:

```text
probe_regime_under_strict
probe_regime_under_default
probe_regime_under_lenient
threshold_stability_class
```

Suggested classes:

```text
stable_usable_quotient
strict_watch_default_usable
lenient_only_usable
stable_collision_limited
stable_identity_like
threshold_fragile
```

A result that only becomes usable under lenient thresholds is not a clean pass.

## 4. Probe-resolution regimes

Classify every probe row into one regime:

```text
too_coarse_collision
usable_quotient
high_resolution_watch
identity_like_control
support_extreme_limited
```

Only `usable_quotient` can serve as ordinary evidence.

`high_resolution_watch` may be reported, but cannot promote a group unless corroborated by usable quotient probes.

`identity_like_control` is diagnostic/control only.

`support_extreme_limited` must be split by floor/ceiling:

```text
support_floor_sparse
support_ceiling_saturated
```

Do not merge floor into ceiling.

## 5. Required probe-resolution columns

For every probe row, report:

```text
signature_entropy
signature_entropy_ceiling_fraction
effective_signature_count
average_bucket_size
median_bucket_size
min_bucket_size
singleton_bucket_fraction
probe_collision_rate
support_fraction
support_floor_flag
support_ceiling_flag
identity_like_score
probe_resolution_regime
threshold_profile
```

These fields are guardrails. They should appear in both detailed row outputs and aggregate summaries.

## 6. Candidate quotient probe families

Try a small number of principled quotient probes. Do not open-endedly add detail.

Initial probe families:

```text
constraint_neighborhood_histogram
relation_neighborhood_degree_asymmetry_histogram
frontier_response_bucket
motif_count_bucket
multi_scale_support_region_bucket
```

Brief definitions:

```text
constraint_neighborhood_histogram:
  coarse histogram of local satisfied/violated constraints around a state

relation_neighborhood_degree_asymmetry_histogram:
  coarse local relation geometry: out-degree/in-degree/reciprocity/asymmetry buckets

frontier_response_bucket:
  coarse class of how local frontier support changes under one-step neutral perturbations

motif_count_bucket:
  coarse counts of small directed relation motifs in local neighborhood

multi_scale_support_region_bucket:
  coarse bucket combining local support and horizon growth regime
```

Each probe must be many-to-one in normal use. If a probe becomes near-identity under the threshold sweep, demote it to diagnostic/control.

## 7. Fractional recurrence, not all-or-nothing recurrence

Boundary deformation does not need to recur in every seed/start/horizon/probe.

Path dependence is expected. Universal recurrence would likely select for trivial, rigid structures.

Use fractional recurrence gates, all configurable.

Suggested defaults:

```text
seed_recurrence_rate_min: 0.60
start_recurrence_rate_min: 0.50
horizon_window_recurrence_rate_min: 0.40
independent_probe_axis_required: true
matched_control_excess_required: true
```

Report exact recurrence rates. Do not report only booleans.

## 8. Path-dependence profile

Classify path dependence rather than rejecting it.

Required recurrence profile fields:

```text
start_recurrence_rate
seed_recurrence_rate
parameter_variant_recurrence_rate
horizon_window_recurrence_rate
probe_axis_recurrence_rate
matched_recurrence_excess
recurrence_percentile_vs_controls
```

Suggested path-dependence classes:

```text
single_start_lucky
start_local
basin_local
seed_recurrent
parameter_recurrent
horizon_window_recurrent
probe_axis_recurrent
multi_axis_recurrent
```

A path-dependent structure can remain interesting if it is:

```text
basin_local + seed_recurrent + horizon_window_recurrent + probe_axis_recurrent
```

It should be treated as likely luck if it is:

```text
single_start + single_seed + single_horizon + single_probe
```

## 9. Distinguishing path dependence from luck

Use matched recurrence controls.

For each candidate group, compute recurrence profiles for:

```text
matched non-candidate parameter variants
matched fakeout groups
shuffled starts
shuffled seed labels
probe-marginal controls
frontier-size matched controls
random boundary groups
```

Required metrics:

```text
observed_recurrence_rate
matched_control_recurrence_mean
matched_control_recurrence_std
matched_recurrence_excess
recurrence_percentile_vs_controls
control_count
weak_recurrence_control_flag
```

A path-dependent structure is interesting if:

```text
observed recurrence is fractional but above matched controls
```

A lucky structure is likely if:

```text
observed recurrence falls within matched-control recurrence distribution
```

## 10. Independent probe axes

Do not count correlated probes as independent.

Maintain probe axis mapping:

```text
coordinate_tuple_k3: coordinate_axis
coordinate_tuple_k4: coordinate_axis
constraint_profile_hash: constraint_axis
constraint_violation_count_plus_local_tuple: constraint_axis
constraint_neighborhood_histogram: constraint_neighborhood_axis
relation_neighborhood_degree_asymmetry_histogram: relation_geometry_axis
frontier_response_bucket: frontier_response_axis
motif_count_bucket: relation_motif_axis
multi_scale_support_region_bucket: support_growth_axis
existing_low: low_projection_axis
full_state_hash: identity_axis
full_state_strict: identity_axis
```

A cleaner detection should require recurrence across at least two independent usable quotient axes.

For this audit, require:

```text
at least one existing repaired axis
and at least one new quotient axis
```

or, if no existing axis clears:

```text
at least two new quotient axes from different families
```

## 11. Identity-like versus agent-like language

Do not use `identity_like` and `agent_like` as positive MB0 classes.

For this branch:

```text
identity-like probe:
  a measurement that behaves like a raw-state or near-raw-state fingerprint

identity-like structure:
  deferred; a many-state equivalence class that persists across transformation

agent-like structure:
  deferred; would require future-sensitive control-loop evidence such as uptake/transformation/emission, perturbation response, or maintenance of future-shaping capacity
```

Difference:

```text
identity-like = persistence / boundary continuity
agent-like = future-sensitive control loop
```

MB0 does not classify agent-like structures.

Reports should include:

```text
detection_status
classification_status
```

Detection status examples:

```text
recurrent_boundary_deformation_detected
measurement_limited_collision
quotient_resolved_pending_controls
not_detected
```

Classification status should normally be:

```text
classification_not_attempted
unclassified_boundary_structure
```

## 12. Identity leakage audit

For every group, report:

```text
identity_leakage_score
identity_like_probe_dependency
usable_quotient_probe_dependency
classification_if_identity_like_probes_excluded
classification_if_high_resolution_watch_excluded
classification_using_only_usable_quotient_probes
```

Demote groups that only appear under high-resolution or identity-like probes.

## 13. Suggested run shape

This is a small focused audit, not a broad run.

Input groups:

```text
16 independent_axis_recurrent_but_collision_limited groups
```

Optional:

```text
include 4 weak_control_bundle_recurrence groups as diagnostic controls
```

Suggested shape:

```text
groups: 16 primary, optionally 20 total
fresh_seeds_per_group: 4
start_samples: same as previous focused pass
horizons: same as previous focused pass
probe families:
  coordinate_tuple_k3
  coordinate_tuple_k4
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple
  constraint_neighborhood_histogram
  relation_neighborhood_degree_asymmetry_histogram
  frontier_response_bucket
  motif_count_bucket
  multi_scale_support_region_bucket
  existing_low diagnostic only
  full_state_hash control only
threshold_profiles: strict, default, lenient
matched_recursion_controls_enabled: true
matched_control_bundle_enabled: true
promotion_enabled: false
n6_transfer: false
```

## 14. Required outputs

```text
boundary_deformation_guardrail_report.md
probe_resolution_threshold_config.json
probe_resolution_threshold_sweep.csv
probe_resolution_guardrail_rows.csv
probe_resolution_regime_summary.csv
quotient_probe_metric_rows.csv
quotient_probe_family_summary.csv
identity_leakage_audit.csv
path_dependence_profile.csv
matched_recurrence_controls.csv
matched_recurrence_excess.csv
fractional_recurrence_summary.csv
independent_probe_axis_summary.csv
corrected_boundary_detection_summary.csv
output_manifest.json
status.json
```

## 15. Final report sections

The report must include:

```text
1. Claim boundary
2. Why this is detection improvement, not identity/agent classification
3. Threshold configuration and sweep results
4. Probe-resolution regime summary
5. Quotient probe family performance
6. Identity leakage audit
7. Fractional recurrence and path-dependence profile
8. Matched recurrence controls: luck versus recurrence
9. Matched-control separation
10. Group reclassification
11. Decision: continue probe repair / confirmed measurement limit / small confirmation
12. Output manifest
```

## 16. Group classification after this audit

Classify each group as one of:

```text
quotient_resolved_recurrent_boundary_deformation
quotient_resolved_but_matched_control_equivalent
fractional_recurrent_above_controls
path_dependent_recurrent_above_controls
collision_limited_under_all_quotient_probes
identity_leakage_dependent
threshold_fragile_detection
weak_recurrence_controls
support_floor_limited_recurrence
support_ceiling_limited_recurrence
measurement_limited_confirmed
underdetermined_after_guardrail_audit
```

No group should be classified as agent-like or identity-detected.

## 17. Decision gates

### Continue with small confirmation

Continue only if at least one group is:

```text
quotient_resolved_recurrent_boundary_deformation
```

or:

```text
fractional_recurrent_above_controls
```

with:

```text
usable quotient probes
low identity leakage
matched recurrence excess above controls
matched-control separation not weak
```

### Confirm measurement limit

Stop and write/update measurement-limits note if:

```text
all non-identity quotient probes remain collision-limited
OR recurrence falls within matched recurrence controls
OR only identity-like/high-resolution-watch probes resolve the signal
OR matched controls erase the signal under usable quotient probes
```

### Probe design failure

If probes reduce collision but become identity-like, do not count as success. Mark:

```text
identity_leakage_dependent
```

and do not scale.

## 18. Acceptance criteria

The audit is accepted only if:

```text
thresholds are configurable
strict/default/lenient threshold sweep is run
bucket size metrics are emitted
identity leakage audit is emitted
recurrence is fractional, not all-or-nothing
path dependence is classified
matched recurrence controls are computed
independent probe axes are enforced
agent-like and identity-detected labels are not emitted
status.json is final and not RUNNING
```

## 19. Bottom line

Proceed with improvement, but tighten guardrails.

The branch is not trying to classify identities or agents. It is trying to resolve recurrent boundary deformation without letting raw-state fingerprints count as evidence.

The next question is:

```text
Can principled non-identity quotient probes reduce collision and preserve recurrent boundary deformation above matched recurrence controls?
```

If yes, MB0 earns a small confirmation pass.

If no, the measurement limit is real and should be documented rather than chased indefinitely.

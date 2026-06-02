# RFS-MB0 Medium-Breadth Atlas Runner Repair Spec

Status: immediate implementation repair spec after the first medium-breadth support/distribution atlas

Purpose: fix reporting, classification, transfer, and audit issues in the current medium-breadth atlas runner before any larger support/distribution run.

This is not a new science run. It is a runner and reporting repair pass.

Inputs motivating this repair:

```text
results/rfs_mb0_relation_atlas/20260525_medium_breadth_support_distribution_atlas_10h/
results/rfs_mb0_relation_atlas/20260525_medium_breadth_support_distribution_atlas_10h/medium_breadth_support_distribution_atlas_report.md
docs/research_notes/validation_results/rfs_mb0/rfs_mb0_medium_breadth_support_distribution_atlas_10h_result.md
```

The first atlas was technically successful but scientifically conservative:

```text
sweep_jobs_completed: 21840 / 21840
sweep_rows_completed: 1769040
rank_effect_rows: 39424
errors: 0
promotion_enabled: false
```

However, it exposed runner/reporting issues that must be fixed before scaling.

## 0. Core repair goal

Make the runner produce an internally consistent, auditable result bundle.

The next successful repair run should let us answer:

```text
What exactly produced each band class?
What table/criterion supports each required-answer boolean?
Were fakeout-to-candidate transitions present or absent?
Was n=6 transfer actually run?
Which candidate-like rows failed because of saturation, probe limits, matched controls, or margin fragility?
```

Do not broaden the atlas until these are fixed.

## 1. Blocker: fakeout-to-candidate inconsistency

The current report has an inconsistency:

```text
Required Answers:
  Fakeout-to-candidate transitions recurred: True

Transition Classes:
  fakeout_to_candidate_transition: 0 in the transition graph
```

This must be resolved.

### Required fix

Add explicit provenance for each required-answer boolean.

For every required answer, report:

```text
required_answer_name
value
source_table
source_column
source_filter
numerator
denominator
threshold
example_row_ids
```

Required output:

```text
required_answer_provenance.csv
```

The report must not emit any boolean such as:

```text
Fakeout-to-candidate transitions recurred: True
```

unless the supporting table and counts are printed directly below it.

### Specific fakeout-to-candidate logic

Disambiguate at least two concepts:

```text
transition_graph_fakeout_to_candidate_count:
  count of explicit transition graph edges classified as fakeout_to_candidate_transition

band_level_fakeout_to_candidate_recurrence_count:
  count of bands where any anchor/variant/fresh-seed row crosses from fakeout class to candidate-like class under the detector
```

Do not collapse these into one boolean.

Report both:

```text
fakeout_to_candidate_transition_graph_count
fakeout_to_candidate_band_level_count
fakeout_to_candidate_fresh_seed_recurrent_count
fakeout_to_candidate_any_recurred
```

If graph count is 0 but band-level count is positive, the report should say:

```text
No explicit fakeout_to_candidate transition graph edges were emitted,
but band-level fakeout-to-candidate recurrence was observed under [criterion].
```

If both are 0, say so.

## 2. Blocker: n=6 transfer not actually run

The 10h spec requested limited n=6 transfer. The runner emitted `n6_transfer_summary.csv`, but the transfer was not run.

This is acceptable only if status is explicit and non-ambiguous.

### Required fix

Add an explicit transfer stage state machine:

```text
not_requested
requested_not_run
skipped_budget
skipped_no_eligible_bands
run_completed
run_failed
```

Required output:

```text
n6_transfer_summary.csv
```

with columns:

```text
transfer_status
reason
eligible_band_count
selected_band_count
jobs_requested
jobs_completed
errors
n5_source_band_ids
n6_result_rows
n6_recurrent_count
n6_control_equivalent_count
n6_probe_limited_count
n6_saturation_limited_count
```

If transfer is not run, all job counts must be zero and the report must say:

```text
n=6 transfer was not run and should not be interpreted as completed.
```

### Optional implementation

For repair smoke, either:

```text
A. implement and run a tiny n=6 transfer on 2-3 eligible bands
```

or:

```text
B. explicitly mark transfer_status = requested_not_run or skipped_no_eligible_bands
```

Do not silently write an empty or placeholder `n6_transfer_summary.csv` that looks like a completed result.

## 3. Band class definitions must be explicit

The current atlas emitted:

```text
near_miss_transition_band: 10
stable_fakeout_band: 6
stable_candidate_band: 0
```

But the report does not sufficiently expose why each band received its class.

### Required fix

Create:

```text
atlas_band_classification_audit.csv
```

Columns:

```text
band_id
anchor_id
anchor_class
band_class
band_class_reason
candidate_rate
fakeout_rate
candidate_rate_threshold
fresh_seed_recurrent_count
fresh_seed_recurrent_threshold
probe_recurrence_score
probe_recurrence_threshold
start_recurrence_score
start_recurrence_threshold
margin_stability_summary
matched_control_equivalent_rate
saturation_boundary_count
probe_resolution_boundary_count
candidate_to_fakeout_count
fakeout_to_candidate_count
eligible_for_stable_candidate_band
stable_candidate_blockers
```

### Stable candidate definition

Define `stable_candidate_band` only if all are true:

```text
candidate_rate >= configured threshold
fresh_seed_recurrent_count >= configured threshold
probe_recurrence_score >= configured threshold
matched_control_equivalent_rate below configured ceiling
saturation/probe-limit rates below configured ceilings
margin stability not fragile-only
```

If zero stable candidate bands are found, print the blocker histogram:

```text
stable_candidate_blocker_summary.csv
```

## 4. Candidate/fakeout transition graph repair

The transition graph should be auditable.

Required output:

```text
phenotype_transition_graph.csv
```

with columns:

```text
anchor_id
band_id
source_row_id
target_row_id
source_class
target_class
transition_class
sweep_parameter
sweep_value
fresh_seed
probe_family
start_samples
horizon
margin_level
classification_before
classification_after
transition_reason
```

Also output:

```text
transition_class_summary.csv
```

The report must use `transition_class_summary.csv` as the source of transition counts, not recompute ad hoc counts separately.

## 5. Saturation boundary audit

The atlas was dominated by saturation boundaries:

```text
saturation_boundary: 124
```

Before a bigger run, we need to know what that means.

Required output:

```text
saturation_boundary_audit.csv
```

Columns:

```text
row_id
band_id
anchor_id
probe_family
horizon
start_samples
support_fraction
support_ceiling_flag
state_space_saturation_flag
probe_alphabet_saturation_flag
frontier_growth_slope
frontier_growth_curvature
saturation_H
pre_saturation_candidate_score
near_saturation_candidate_score
post_saturation_candidate_score
classification_if_pre_saturation_only
classification_if_saturation_excluded
```

The final report must distinguish:

```text
true state-space saturation
probe alphabet/support ceiling saturation
frontier/horizon saturation
classification artifact from including saturated windows
```

## 6. Probe-resolution boundary audit

The atlas found probe-resolution boundaries but weak probe recurrence.

Required output:

```text
probe_resolution_boundary_audit.csv
```

Columns:

```text
row_id
band_id
probe_family
probe_resolution_class
probe_collision_rate
observed_signature_support_fraction
support_ceiling_flag
candidate_score
matched_control_score
candidate_minus_control
class_under_probe
same_band_classes_other_probes
cross_probe_recurrence_flag
probe_local_only_flag
```

Report:

```text
probe_family_candidate_rate
probe_family_fakeout_rate
probe_family_probe_limited_rate
probe_family_matched_control_equivalent_rate
```

in:

```text
probe_family_outcome_summary.csv
```

## 7. Rank/effect and margin sensitivity repair

The atlas emitted many rank/effect rows and margin classes, but report-level interpretation needs clearer aggregation.

Required outputs:

```text
atlas_rank_effect_summary.csv
atlas_margin_sensitivity.csv
margin_stability_by_band.csv
```

Add columns:

```text
band_id
anchor_id
row_id
metric_name
candidate_value
control_mean
control_std
candidate_minus_control
candidate_control_percentile
control_count
weak_control_bundle_flag
margin_0_00_class
margin_0_01_class
margin_0_02_class
margin_0_05_class
margin_0_10_class
margin_stability_class
```

Report blocker counts for candidate-like rows that fail:

```text
matched_control_equivalent
weak_control_bundle
fragile_margin_only
probe_limited
support_ceiling_limited
saturation_limited
start_fragile
probe_local_only
```

Output:

```text
candidate_blocker_summary.csv
```

## 8. Fresh-seed recurrence repair

The report says:

```text
Fresh-seed recurrent band rows: 198
```

This needs provenance and recurrence definition.

Required output:

```text
fresh_seed_recurrence_audit.csv
```

Columns:

```text
band_id
anchor_id
parameter_variant_id
fresh_seed_count
fresh_seed_candidate_count
fresh_seed_fakeout_count
fresh_seed_control_equivalent_count
fresh_seed_probe_limited_count
fresh_seed_saturation_limited_count
fresh_seed_recurrence_score
fresh_seed_recurrence_class
recurrence_threshold
example_seed_ids
```

Define recurrence classes:

```text
seed_recurrent_candidate_like
seed_recurrent_fakeout_like
seed_mixed_or_boundary
seed_fragile_or_absent
insufficient_fresh_seeds
```

## 9. Report structure repair

The final markdown report must be structured in this order:

```text
1. Run shape and integrity
2. Promotion/claim boundary
3. Required-answer provenance table
4. Band class summary
5. Stable-candidate blocker summary
6. Transition graph summary
7. Saturation boundary audit
8. Probe-resolution boundary audit
9. Fresh-seed recurrence audit
10. Margin/rank-effect summary
11. n=6 transfer status
12. Recommended next step
13. Machine-readable output manifest
```

The report must include a machine-readable manifest:

```text
output_manifest.json
```

listing every expected output file, whether it exists, row counts, and status.

## 10. Repair smoke run shape

Run a small repair smoke before any larger atlas.

Suggested:

```text
anchors: 4-6
fresh_seeds_per_variant: 2
start_samples: 3,8
horizons: 0,1,2,4,8,12,16,24,32
probe families: same as previous run
workers: 18
wall clock: 30-90 minutes
promotion_enabled: false
```

The smoke should emphasize correctness of output contracts, not breadth.

## 11. Acceptance criteria

The repair is accepted only if all are true:

```text
errors = 0
output_manifest.json exists and marks all required files present
required_answer_provenance.csv exists and explains every report boolean
fakeout-to-candidate inconsistency is resolved
n6_transfer_summary.csv has explicit transfer_status
atlas_band_classification_audit.csv exists and explains every band class
transition_class_summary.csv matches report transition counts
stable_candidate_blocker_summary.csv exists, especially if stable_candidate_band = 0
saturation_boundary_audit.csv exists
probe_resolution_boundary_audit.csv exists
fresh_seed_recurrence_audit.csv exists
candidate_blocker_summary.csv exists
```

If any acceptance criterion fails, do not run a larger atlas.

## 12. Recommended interpretation after repair

The repair smoke should not be interpreted as a science result unless it unexpectedly discovers a major bug that changes previous conclusions.

Expected outputs:

```text
runner repaired
reporting consistent
n=6 transfer status explicit
band classes auditable
boundary causes clearer
```

Only after this should we decide between:

```text
second local sweep around saturation/probe-resolution boundaries
measurement-limits note
or a properly instrumented broader atlas
```

## 13. Bottom line

Before scaling, fix the runner.

The first medium-breadth atlas taught us that the branch is currently dominated by near-miss, saturation-boundary, probe-resolution-boundary, and candidate-to-fakeout behavior.

That may be real transition geometry, or it may be detector/probe/saturation artifact.

The current runner must make that distinction auditable before any bigger run.

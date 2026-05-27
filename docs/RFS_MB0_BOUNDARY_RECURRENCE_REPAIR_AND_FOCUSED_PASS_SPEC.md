# RFS-MB0 Boundary Recurrence Repair and Focused Pass Spec

Status: immediate Codex implementation spec after partial boundary-resolution sweep

Purpose: repair the boundary-resolution runner issues exposed by the partial run, then run a small focused recurrence pass on the fresh-seed recurrent boundary groups. This is not a broader atlas, not n=6 transfer, and not a science-gate run.

This spec follows:

```text
docs/RFS_MB0_MEDIUM_BREADTH_ATLAS_RUNNER_REPAIR_SPEC.md
results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep/
```

and the partial result:

```text
status in status.json: RUNNING
workers requested: 18
anchors selected: 6
sweep jobs requested: 5440
sweep jobs completed at checkpoint: 3790
sweep rows completed: 187560
rank/effect rows: 39424
errors: 0
wall clock at checkpoint: 14114.8 seconds
```

The partial run found boundary structure but did not resolve the main blocker:

```text
candidate-like rows: 44388
non-saturation candidate-like rows: 44388
fresh-seed recurrent variant groups: 28
stable candidate bands: 0
probe-recurrent bands: 0
saturation audit rows: 76467
probe-resolution audit rows: 78427
```

## 0. Strategic interpretation

The boundary-resolution sweep kept MB0 alive but narrowed the problem.

The live question is no longer:

```text
Can breadth find candidates?
```

It is:

```text
Can fresh-seed recurrent boundary groups become cross-probe recurrent once probe recurrence is measured correctly and saturation is disentangled?
```

Do not run n=6 yet.

Do not run a broader atlas yet.

Do not return to path metrics.

Do not treat local/pre-control candidate-like rows as stable candidates.

## 1. Claim boundary

Allowed:

```text
The runner was repaired.
The partial boundary run contains fresh-seed recurrent boundary groups.
A focused pass did or did not find evidence-probe recurrence in those groups.
A band is boundary-like, near-miss, probe-local, saturation-contaminated, or measurement-limited.
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
stable candidate band established without explicit gates
n=6 transfer completed unless actually run
```

## 2. Immediate code repairs

Implement these before the focused pass.

### 2.1 Runtime cushion and graceful partial finalization

The partial run was interrupted externally before final status could be marked complete.

Add:

```text
--shutdown-cushion-seconds default 600
```

Behavior:

```text
if remaining_runtime <= shutdown_cushion_seconds:
  stop submitting new jobs
  allow currently running jobs to finish until a smaller drain timeout
  cancel remaining futures if needed
  write final outputs
  set status = PARTIAL_TIME_LIMIT_REACHED
```

Also catch:

```text
KeyboardInterrupt
SIGTERM where platform permits
```

and write final partial outputs with:

```text
status = INTERRUPTED_PARTIAL
```

Required status fields:

```text
status
finalization_reason
wall_clock_seconds
max_runtime_seconds
shutdown_cushion_seconds
jobs_requested
jobs_submitted
jobs_completed
jobs_cancelled
pending_jobs_remaining
errors
last_checkpoint_utc
final_outputs_written: true/false
```

### 2.2 Robust checkpointing

Current checkpointing is too brittle if it depends on row-count modulo.

Add checkpoint triggers based on both completed jobs and elapsed time:

```text
--checkpoint-every-jobs default 36
--checkpoint-every-seconds default 300
```

Checkpoint if either is exceeded since last checkpoint.

Required status fields:

```text
checkpoint_count
last_checkpoint_completed_jobs
last_checkpoint_elapsed_seconds
last_checkpoint_utc
```

### 2.3 Anchor selection shortfall reporting

The run requested 10 anchors but selected only 6 because the source repair-smoke atlas exposed six boundary anchors.

Make this machine-readable.

Required output:

```text
anchor_selection_audit.csv
```

Columns:

```text
anchors_requested
anchors_available
anchors_selected
selection_source
selection_mode
shortfall_flag
shortfall_reason
candidate_boundary_anchor_count
near_miss_anchor_count
saturation_boundary_anchor_count
probe_resolution_boundary_anchor_count
stable_fakeout_anchor_count
selected_anchor_ids
```

Also include these fields in `status.json`.

### 2.4 Rename candidate-like row counts

The runner currently reports many rows as candidate-like even though they are local/pre-control classifications from `classify_pre_control`.

Rename report fields:

```text
candidate_like_rows -> local_pre_control_candidate_like_rows
non_saturation_candidate_like_rows -> non_saturation_local_pre_control_candidate_like_rows
```

Add explicit separated counts:

```text
local_pre_control_candidate_like_rows
matched_control_candidate_like_rows
band_level_candidate_like_rows
stable_candidate_band_count
```

If matched-control candidate-like rows are not computed in the sweep, set:

```text
matched_control_candidate_like_rows = not_computed_in_local_sweep
```

Do not leave this ambiguous.

### 2.5 Split probe recurrence into evidence and diagnostic recurrence

Current `probe_recurrence_rate` appears to use the minimum candidate rate across all probe families. This is too blunt for exploratory triage because a strict-state or diagnostic probe can zero out a band.

Add probe role classification:

```text
evidence_probe:
  coordinate_tuple_k3
  coordinate_tuple_k4
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple

diagnostic_probe:
  existing_low
  relation_role if present

control_probe:
  full_state_hash
  full_state_strict
```

For every band/variant, compute:

```text
probe_recurrence_all_probes_min
probe_recurrence_evidence_probe_min
probe_recurrence_evidence_probe_fraction
probe_recurrence_evidence_probe_count
probe_recurrence_diagnostic_probe_fraction
probe_recurrence_control_probe_fraction
probe_local_only_flag
cross_probe_recurrent_evidence_flag
```

Definitions:

```text
probe_recurrence_evidence_probe_fraction =
  evidence probes with candidate-like class / evidence probes evaluated

cross_probe_recurrent_evidence_flag =
  evidence_probe_count_with_candidate_like >= 2
  and candidate-like rows are not all from one probe family
```

Use `cross_probe_recurrent_evidence_flag`, not all-probe minimum, for exploratory focused-pass triage.

Still report all-probe minimum as a conservative diagnostic.

### 2.6 Split saturation into row/band/probe/horizon levels

The partial result says non-saturation candidate-like rows exist, while saturation/probe-resolution boundaries still dominate the audit surface. The runner must distinguish these.

Add:

```text
saturation_decomposition.csv
```

Columns:

```text
row_id
band_id
anchor_id
variant_dimension
variant_value
probe_family
probe_role
horizon
start_samples
local_primary_class
is_local_pre_control_candidate_like
row_support_ceiling_flag
row_state_space_saturation_flag
row_probe_alphabet_saturation_flag
band_has_saturation_boundary
probe_family_saturation_rate
horizon_saturation_rate
candidate_row_saturation_flag
candidate_band_saturation_contamination_flag
classification_if_saturation_rows_excluded
```

Add report counts:

```text
local_candidate_like_rows_that_are_saturated
local_candidate_like_rows_non_saturated
bands_with_saturation_boundary
bands_with_candidate_like_rows_but_saturation_boundary
probe_families_with_saturation_rate_above_threshold
horizons_with_saturation_rate_above_threshold
```

### 2.7 Add focused-group extraction

The next pass should target only the fresh-seed recurrent boundary groups.

Add output from the partial/focused source run:

```text
focused_boundary_group_selection.csv
```

Selection criteria:

```text
fresh_seed_recurrence_class in {
  seed_recurrent_candidate_like,
  seed_mixed_or_boundary
}
AND fakeout_to_candidate or candidate_stable_region or non_saturation candidate-like evidence present
AND not already stable candidate band
```

Columns:

```text
group_id
source_band_id
source_anchor_id
parameter_variant_id
variant_dimension
variant_value
fresh_seed_count
fresh_seed_candidate_count
fresh_seed_recurrence_class
transition_class_counts
local_pre_control_candidate_like_count
non_saturation_local_candidate_like_count
probe_families_with_candidate_like
horizons_with_candidate_like
saturation_contamination_summary
probe_resolution_contamination_summary
selection_reason
```

If there are more than 28 groups, select the top 12-20 for the focused pass.

If exactly 28 groups exist and runtime allows, run all 28.

## 3. Focused cross-probe recurrence pass

After the repairs, run a small focused pass on fresh-seed recurrent boundary groups.

### 3.1 Purpose

Ask:

```text
Do fresh-seed recurrent boundary groups become cross-probe recurrent under evidence probes when saturation and diagnostic/control probes are separated?
```

Do not ask:

```text
Do we have a stable candidate band?
Does n=5 transfer to n=6?
```

### 3.2 Input groups

Use:

```text
focused_boundary_group_selection.csv
```

Preferred groups:

```text
fakeout_to_candidate_transition groups
candidate_stable_region groups from partial run
seed_mixed_or_boundary groups
non-saturation local candidate-like groups
```

Exclude or down-rank groups where:

```text
all candidate-like rows are from control probes
all candidate-like rows are from saturated horizons
all candidate-like rows are from one diagnostic low-resolution probe
```

### 3.3 Run shape

Suggested focused pass:

```text
groups: 12-28
fresh_seeds_per_group: 3-5 total, including prior seeds where possible
start_samples: 3, 8, optional 16 only for top groups
horizons: 0,1,2,4,8,12,16,24,32
probe families:
  coordinate_tuple_k3
  coordinate_tuple_k4
  constraint_profile_hash
  constraint_violation_count_plus_local_tuple
  existing_low as diagnostic only
  full_state_hash as control only, optional
workers: 18
max_runtime_seconds: set at least 10 minutes below wrapper timeout
shutdown_cushion_seconds: 600
promotion_enabled: false
```

Do not include n=6.

Do not include path metrics.

### 3.4 Probe panel logic

For each selected group, evaluate the same parameter variant across all evidence probes.

Output:

```text
focused_cross_probe_recurrence.csv
```

Columns:

```text
group_id
band_id
anchor_id
variant_dimension
variant_value
seed
start_samples
horizon
probe_family
probe_role
local_primary_class
is_local_pre_control_candidate_like
row_saturation_flag
probe_resolution_class
probe_collision_rate
support_fraction
mixed_deformation_score
support_deformation_score
distribution_deformation_score
```

Aggregate output:

```text
focused_group_recurrence_summary.csv
```

Columns:

```text
group_id
source_band_id
variant_dimension
variant_value
fresh_seed_count
evidence_probe_count
evidence_probe_candidate_count
evidence_probe_candidate_fraction
evidence_probe_recurrent_flag
evidence_probe_recurrent_non_saturation_flag
start_recurrence_score
horizon_recurrence_score
probe_local_only_flag
saturation_contamination_rate
probe_resolution_contamination_rate
recommended_group_class
```

Suggested group classes:

```text
evidence_probe_recurrent_boundary_candidate
evidence_probe_recurrent_but_saturation_contaminated
evidence_probe_recurrent_but_probe_limited
probe_local_near_miss
fresh_seed_recurrent_but_not_cross_probe
measurement_limited_group
stable_fakeout_group
```

## 4. Revised decision gate

After the focused pass, decide among three outcomes.

### 4.1 Continue MB0 with a small confirmation pass

Only if at least one group satisfies:

```text
evidence_probe_recurrent_flag = true
evidence_probe_recurrent_non_saturation_flag = true
fresh_seed_count >= 3
candidate-like evidence appears in >= 2 evidence probe families
saturation_contamination_rate below configured ceiling
probe_resolution_contamination_rate below configured ceiling
```

Then run one small confirmation pass, still n=5, before n=6.

### 4.2 Write measurement-limits note

If:

```text
probe_recurrent bands remain zero under evidence-probe recurrence
OR all apparent recurrence is probe-local, saturated, or diagnostic/control-probe driven
```

Then write a measurement-limits note.

The note should say the current relation generator produces local/pre-control and fresh-seed boundary transitions, but the current probe/detector stack cannot establish cross-probe recurrent support/distribution deformation.

### 4.3 Reconsider substrate/probe design

If:

```text
candidate-like behavior is consistently non-saturated but always probe-local
```

then do not run bigger breadth. Instead reassess probe design or relation-generator observables.

## 5. Required outputs

### 5.1 Runner repair outputs

```text
anchor_selection_audit.csv
runtime_finalization_audit.csv
checkpoint_audit.csv
saturation_decomposition.csv
probe_role_recurrence_summary.csv
focused_boundary_group_selection.csv
output_manifest.json
status.json
```

### 5.2 Focused pass outputs

```text
boundary_recurrence_repair_report.md
focused_cross_probe_recurrence.csv
focused_group_recurrence_summary.csv
focused_probe_role_summary.csv
focused_saturation_decomposition.csv
focused_candidate_like_terminology_audit.csv
focused_required_answer_provenance.csv
focused_measurement_limit_flags.csv
status.json
```

## 6. Final report structure

The final report should be named:

```text
boundary_recurrence_repair_report.md
```

Required sections:

```text
1. Run status and partial/final handling
2. Anchor selection audit
3. Candidate-like terminology audit
4. Fresh-seed recurrent group selection
5. Probe-role recurrence summary
6. Cross-probe recurrence results
7. Saturation decomposition
8. Probe-resolution decomposition
9. Stable candidate blockers
10. Decision gate result
11. Claim boundary
12. Output manifest
```

## 7. Acceptance criteria

Do not run a larger atlas until all are true:

```text
final status is not left as RUNNING after wrapper interruption or internal timeout
anchor_selection_audit.csv exists
runtime_finalization_audit.csv exists
checkpoint_audit.csv exists
candidate-like terminology is split into local/pre-control vs band-level vs matched-control
probe recurrence is split into all/evidence/diagnostic/control recurrence
saturation is split into row/band/probe/horizon decomposition
focused_boundary_group_selection.csv exists
focused_group_recurrence_summary.csv exists after focused pass
output_manifest.json marks all required files present
```

Scientific acceptance for continuing MB0 requires at least one:

```text
evidence_probe_recurrent_boundary_candidate
```

that is also:

```text
non-saturation recurrent
fresh-seed recurrent
not only diagnostic/control-probe driven
```

If none exist, stop and write measurement-limits note.

## 8. Implementation notes

### 8.1 Source-run rank/effect rows

The runner continues to emit `rank_effect_rows = 39424` even in smaller sweeps because rank/effect rows come from the source taxonomy output rather than only the current sweep.

Rename or annotate:

```text
source_rank_effect_rows
current_sweep_rank_effect_rows
```

Do not report `rank_effect_rows` without provenance.

### 8.2 Matched controls

The focused pass is still mostly local/pre-control unless matched controls are recomputed for the new generated systems.

If matched controls are not recomputed, mark:

```text
matched_control_candidate_like_rows = not_computed_in_focused_pass
```

and do not call any result stable.

### 8.3 Probe role table

Define probe role table in code, not only in docs:

```text
PROBE_ROLES = {
  "coordinate_tuple_k3": "evidence",
  "coordinate_tuple_k4": "evidence",
  "constraint_profile_hash": "evidence",
  "constraint_violation_count_plus_local_tuple": "evidence",
  "existing_low": "diagnostic",
  "full_state_hash": "control",
  "full_state_strict": "control",
}
```

If a probe is unknown, assign:

```text
unknown_diagnostic
```

and exclude it from evidence-probe recurrence gates.

### 8.4 Runtime finalization

Use final statuses:

```text
COMPLETED
PARTIAL_TIME_LIMIT_REACHED
INTERRUPTED_PARTIAL
FAILED_WITH_ERRORS
```

Never leave final status as `RUNNING` if the runner exits through its own code path.

## 9. Bottom line

The partial boundary-resolution sweep found real local transition structure:

```text
fakeout-to-candidate transitions recur
fresh-seed recurrent boundary groups exist
local/pre-control candidate-like behavior appears outside simple saturation labels
```

But it did not resolve the main blocker:

```text
stable candidate bands remain zero
probe recurrence remains zero
saturation/probe-resolution boundaries still dominate
```

The next pass should not be broader.

It should repair runtime/reporting and test only the fresh-seed recurrent boundary groups for evidence-probe cross-probe recurrence.

If cross-probe recurrence remains zero after this repair, the next artifact should be a measurement-limits note, not another atlas.

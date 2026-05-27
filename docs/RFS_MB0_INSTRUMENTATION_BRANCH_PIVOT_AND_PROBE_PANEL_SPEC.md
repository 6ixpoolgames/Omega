# RFS-MB0 Instrumentation Branch Pivot and Probe Panel Spec

Status: branch-pivot documentation and Codex implementation spec

Purpose: explicitly pivot the current MB0 work from broader deformation search to instrumentation. The substrate remains potentially fertile, but the measurement basis is not yet adequate. This branch should repair and validate the probe/statistical instrumentation before any scaled exploration, n=6 transfer, or substrate pivot.

This follows:

```text
docs/RFS_MB0_DETECTOR_INSTRUMENTATION_REPAIR_SPEC.md
docs/RFS_MB0_BOUNDARY_DEFORMATION_GUARDRAIL_AND_QUOTIENT_PROBE_SPEC.md
results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/
results/rfs_mb0_relation_atlas/20260527_boundary_deformation_guardrail_focused/
```

External audit inputs:

```text
claude bug report 2.txt
claude upgrade recommendations.txt
```

## 0. Branch pivot summary

The current best read is:

```text
The substrate is potentially fertile, but the instrumentation is flawed or underpowered.
```

More precisely:

```text
RFS-MB0 repeatedly finds recurrent boundary structure.
The detector can rediscover that structure.
But the current probe panel cannot characterize it as clean quotient-level support/distribution deformation above controls.
```

Therefore the next branch is not a search branch. It is an instrumentation branch.

Preferred name:

```text
RFS-MB0 Instrumentation
```

or:

```text
RFS-MB0Q Quotient Instrumentation
```

Avoid naming it `repair` unless referring to a specific code defect. The branch goal is broader than patching bugs: it is to construct, validate, and calibrate the measurement basis.

## 1. Why this pivot is justified

Evidence for substrate fertility:

```text
fresh-seed recurrent boundary groups
independent-axis recurrent-but-collision-limited groups
recurrent boundary structure after detector repair
weak but nonzero constraint-axis usable signal
```

Evidence for instrumentation failure:

```text
new quotient probes had usable_quotient_rate = 0.0
new quotient probes had collision rates around 0.97-0.99
independent-axis gate was partly unwinnable because it required new quotient axes that never became usable
matched recurrence excess was negative under available probes
identity leakage and support-floor/ceiling handling still affect interpretation
```

This is not enough to claim a candidate.

It is enough to justify better instrumentation.

## 2. Statistical framing and fine-tuning risk

The project has used Shannon entropy, JS/KL divergence, support fractions, collision rates, and matched controls. That is a statistical measurement posture, but it creates a real risk:

```text
If we search over many probes, thresholds, and recurrence gates,
we may promote noise simply because one probe made the noise look structured.
```

This branch must therefore treat probe development like model/instrument selection.

The key failure mode is:

```text
better-looking noise
```

not only:

```text
raw false positive
```

A probe panel can overfit the 20 known boundary groups even if every individual metric looks reasonable.

## 3. Anti-overfitting guardrails

### 3.1 Pre-register probe families before candidate scoring

For each instrumentation run, define the candidate probe panel before looking at candidate classifications.

Required output:

```text
probe_panel_manifest.json
```

Fields:

```text
probe_key
probe_axis
probe_family
intended_alphabet_size
expected_alphabet_range_for_n
expected_resolution_regime
reason_for_inclusion
known_failure_risk
```

### 3.2 Probe viability preflight before deformation scoring

Before running candidate recurrence/deformation scoring, compute probe viability on neutral systems and held-out noncandidate systems.

Required output:

```text
probe_viability_preflight.csv
```

Metrics:

```text
theoretical_alphabet_size
observed_effective_signature_count
usable_quotient_rate
collision_rate
average_bucket_size
median_bucket_size
singleton_bucket_fraction
entropy_ceiling_fraction
identity_like_score
support_floor_rate
support_ceiling_rate
```

Only probes that pass the preflight enter candidate scoring.

### 3.3 Holdout groups

Split the known recurrent boundary groups into:

```text
design_set
holdout_set
```

Suggested:

```text
design_set: 10 groups
holdout_set: 10 groups
```

Probe thresholds and inclusion decisions may be made using the design set and neutral preflight only. Holdout groups are used once for confirmation.

Required output:

```text
instrumentation_holdout_split.csv
```

### 3.4 Threshold sweeps are diagnostic, not optimization targets

Thresholds must remain configurable, but the runner must not choose thresholds that maximize candidate count.

Report strict/default/lenient behavior, but define a primary default configuration before running the holdout.

Required output:

```text
threshold_selection_audit.csv
```

Fields:

```text
threshold_profile
candidate_count_design
candidate_count_holdout
usable_rate_design
usable_rate_holdout
identity_leakage_design
identity_leakage_holdout
selected_as_primary
selection_reason
```

### 3.5 Multiple-comparison accounting

Report the number of probes, axes, threshold profiles, recurrence gates, and candidate groups tested.

Required output:

```text
instrumentation_multiplicity_audit.csv
```

Fields:

```text
probe_count
axis_count
threshold_profile_count
recurrence_gate_count
group_count
candidate_decision_count
matched_control_decision_count
```

Do not claim a discovery without showing the multiplicity context.

## 4. Fix known implementation defects before preflight

### 4.1 Missing bucket stats must not default to zero

Never let missing `average_bucket_size`, `median_bucket_size`, `min_bucket_size`, or `singleton_bucket_fraction` silently become zero.

Use explicit NA/null values.

Identity-like gates must skip unavailable dimensions, not treat missing as identity evidence.

Required fields:

```text
bucket_stats_available
average_bucket_size
median_bucket_size
min_bucket_size
singleton_bucket_fraction
bucket_stats_missing_reason
```

### 4.2 Compute bucket stats from actual signature counts

For each observed signature distribution, compute:

```text
bucket sizes = counts per signature
average_bucket_size = mean(counts)
median_bucket_size = median(counts)
min_bucket_size = min(counts)
singleton_bucket_fraction = count(count == 1) / signature_count
```

Do not infer singleton fraction from support size alone.

### 4.3 Split sparse-frontier analysis from saturation

`support_floor_sparse` rows should not automatically disappear from usable analysis.

Add a separate sparse-frontier analysis path with matched sparse controls.

Required outputs:

```text
sparse_frontier_probe_viability.csv
sparse_frontier_recurrence_controls.csv
sparse_frontier_detection_summary.csv
```

Sparse-frontier results may not promote to ordinary clean detection unless they clear matched sparse controls and are explicitly classified as sparse-regime detection.

### 4.4 Gate must not depend on unusable probes

The independent-axis gate must distinguish:

```text
available_axis_gate
new_quotient_axis_gate
aspirational_axis_gate
```

Do not require a new quotient axis until at least one new quotient probe has a nonzero usable quotient rate in preflight.

## 5. Why the last quotient probes failed

The prior new quotient probes failed because they used absolute structural values with fixed buckets in small systems.

Failure pattern:

```text
fixed absolute bucket scale
small system with limited variation
most states collapse into the same few buckets
usable_quotient_rate = 0.0
collision_rate around 0.97-0.99
```

Adding more probes with the same fixed-bucket design will not solve this.

The next panel should use:

```text
rank-normalized features
system-relative thresholds
crossed independent axes
dynamic horizon contrasts
mechanistic role classes
```

## 6. New probe panel candidates

### 6.1 degree_profile_rank

System-relative rank-normalized in/out degree profile.

Purpose:

```text
replace fixed degree buckets with quartile/rank buckets over the actual system distribution
```

Expected alphabet:

```text
4 x 4 = 16
```

For n=5/alphabet=3 systems with about 243 states, this is in the expected usable range.

### 6.2 constraint_cross_degree_rank

Cross working constraint variation with rank-normalized degree.

Purpose:

```text
combine an already-partly-working constraint axis with an independent relation-geometry axis
```

Expected alphabet:

```text
12-16 depending on constraint levels
```

### 6.3 constraint_gradient_class

Constraint violation plus local outgoing-neighbor constraint gradient.

Purpose:

```text
enrich the working constraint axis with local directionality
```

Expected alphabet:

```text
approximately 12
```

### 6.4 horizon_growth_contrast_v2

Dynamic contrast of local frontier growth, not absolute frontier size.

Purpose:

```text
measure boundary-regime role by how future support changes from short horizon to next horizon
```

Upgrade over previous frontier bucket:

```text
use more than 6 classes if needed
include multiple contrasts such as H1->H2 and H2->H4
use system-relative quantile bins for growth ratios
```

### 6.5 wiring_role_class_v2

Mechanistic role class based on system-relative in/out degree, reciprocity, and balance.

Purpose:

```text
classify wiring role without using raw state identity
```

Upgrade:

```text
increase alphabet from 6 if preflight says too coarse
use quantile thresholds rather than fixed mean multipliers only
```

### 6.6 self_recurrence_horizon_v2

Cycle/return structure over multiple horizons.

Purpose:

```text
measure local cycle role independent of constraint and degree axes
```

Upgrade:

```text
extend to H=1,2,4,8 and include return-count bucket or earliest-return horizon plus recurrence multiplicity
```

## 7. Expected alphabet range preflight

For each probe and system, compute:

```text
N = number of states
A_theoretical = theoretical alphabet size
A_effective = observed effective signature count
```

Initial target:

```text
0.05 * N <= A_effective <= 0.30 * N
```

If:

```text
A_effective < 0.05 * N
```

class as likely too coarse.

If:

```text
A_effective > 0.50 * N
```

class as identity-risk.

These thresholds should be configurable and reported.

## 8. Updated probe axes

Suggested axes:

```text
constraint_profile_hash: constraint_axis
constraint_violation_count_plus_local_tuple: constraint_axis
constraint_gradient_class: constraint_gradient_axis
degree_profile_rank: degree_rank_axis
constraint_cross_degree_rank: cross_constraint_degree_axis
horizon_growth_contrast_v2: frontier_dynamics_axis
self_recurrence_horizon_v2: cycle_structure_axis
wiring_role_class_v2: wiring_role_axis
existing_low: low_projection_axis
full_state_hash: identity_axis
```

For detection:

```text
identity_axis: control only
low_projection_axis: diagnostic only
```

## 9. Revised axis gates

Report all three gates:

```text
available_axis_gate:
  at least two non-identity usable axes from currently viable probes

new_quotient_axis_gate:
  at least one existing repaired usable axis plus one viable new quotient axis
  OR two viable new quotient axes

aspirational_axis_gate:
  stricter future gate requiring recurrence across constraint, geometry/dynamics, and support/distribution axes
```

Do not use `aspirational_axis_gate` as current pass/fail.

## 10. Run plan

### 10.1 Phase A: instrumentation preflight

Run probe viability on:

```text
neutral generated systems
matched fakeout groups
known recurrent boundary design-set groups
```

No candidate promotion.

Outputs:

```text
probe_panel_manifest.json
probe_viability_preflight.csv
probe_viability_summary.md
instrumentation_holdout_split.csv
```

### 10.2 Phase B: design-set focused detection

Run only probes that pass preflight.

Use:

```text
10 design-set recurrent boundary groups
```

Outputs:

```text
design_set_boundary_detection.csv
design_set_matched_recurrence_controls.csv
design_set_detection_summary.md
```

### 10.3 Phase C: holdout focused detection

Freeze probe panel and thresholds.

Run on:

```text
10 holdout recurrent boundary groups
```

Outputs:

```text
holdout_boundary_detection.csv
holdout_matched_recurrence_controls.csv
holdout_detection_summary.md
```

### 10.4 Phase D: decision report

Write:

```text
rfs_mb0_instrumentation_branch_pivot_report.md
```

## 11. Required final outputs

```text
rfs_mb0_instrumentation_branch_pivot_report.md
probe_panel_manifest.json
probe_viability_preflight.csv
probe_viability_summary.md
instrumentation_holdout_split.csv
threshold_selection_audit.csv
instrumentation_multiplicity_audit.csv
available_axis_gate_summary.csv
new_quotient_axis_gate_summary.csv
sparse_frontier_probe_viability.csv
sparse_frontier_detection_summary.csv
design_set_boundary_detection.csv
design_set_matched_recurrence_controls.csv
holdout_boundary_detection.csv
holdout_matched_recurrence_controls.csv
holdout_detection_summary.md
output_manifest.json
status.json
```

## 12. Decision gates

### Continue MB0 instrumentation

Continue only if:

```text
at least two non-identity usable axes pass preflight
and design-set recurrence clears matched controls
and holdout recurrence remains above controls under frozen thresholds
and identity leakage remains below configured ceiling
```

### Return to probe design

If:

```text
new probes remain too coarse
or all usable signal is constraint-axis only
or available-axis signal fails controls
```

then continue instrumentation design, not scaled exploration.

### Pause MB0 deformation search

If after this branch:

```text
rank-normalized and dynamic probes still fail preflight
or holdout recurrence remains below controls
or usable signals require identity-like probes
```

then write a measurement-limits note and pause MB0 search.

### Do not scale

Do not run scaled exploration unless Phase C holdout passes.

## 13. Documentation requirement

This pivot is important and should be documented as a branch evolution note.

Add or update:

```text
docs/RFS_MB0_BRANCH_EVOLUTION_UPDATE_NOTE.md
```

with:

```text
1. Why the substrate remains potentially fertile
2. Why the current bottleneck is instrumentation
3. Why broader search and n=6 transfer are paused
4. Why the next branch is called instrumentation, not repair
5. How the workflow avoids probe overfitting / better-looking noise
6. How identity and agent classification remain deferred
```

## 14. Bottom line

The next branch should not ask:

```text
Is there anything here?
```

It should ask:

```text
Can we build an instrument that would be capable of telling whether anything here is real?
```

Only after the instrument passes preflight, design-set, and holdout checks should MB0 return to scaled exploration.

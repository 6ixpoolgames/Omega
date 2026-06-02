# RFS-MB0 Deformation Detector Upgrade and Local Parameter Sweep Spec

Status: next-run spec after support/distribution taxonomy smoke

Purpose: upgrade the support/distribution deformation detector from smoke heuristics into rank/effect-size/margin-sensitive scoring, then run local parameter sweeps around both candidate residues and fakeout anchors.

This spec follows:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_SUPPORT_DISTRIBUTION_DEFORMATION_TAXONOMY_SPEC.md
```

and the smoke result:

```text
support/distribution workflow operational
matched-control equivalence dominates
small candidate residue remains
path-process remains parked
```

## 0. Strategic framing

The support/distribution branch is now the active empirical lane.

The smoke produced mostly control-typing rather than strong candidates:

```text
matched_control_equivalent dominated
probe_collision_limited and support_ceiling_limited remain common
small residue of mixed_support_distribution_candidate and support_deformation_candidate rows remains
```

Given the rarity expectation, this is not surprising. Potentially interesting deformation regimes may be narrow and may appear first as fakeouts, near misses, or boundary cases.

Therefore the next step is not a blind large atlas.

The next step is:

```text
1. upgrade deformation scoring;
2. sweep locally around candidate and fakeout anchors;
3. map phenotype transitions and stability;
4. use that to decide what a medium-breadth atlas should sample.
```

## 1. Do not return to path metrics yet

Path metrics remain parked.

Do not add new path-process claims or path-process candidate classes in this run.

Optional path columns may be preserved only as diagnostics if already cheap, but they must not drive classification.

## 2. Deformation detector upgrade

The current smoke uses simple heuristics such as:

```text
JS_to_triviality_nulls >= 0.05
JS_to_support_nulls >= 0.05
candidate_deformation_score > matched_control_deformation_score + 0.02
```

These are acceptable for smoke testing but too brittle for scaling.

Upgrade the detector to report rank/effect-size/margin-sensitive evidence.

### 2.1 Multiple matched controls per candidate

For every candidate row, attach multiple matched controls where possible:

```text
matched_control_count_target: 3 to 5
minimum: 1, but mark rows with fewer than 3 controls
```

Matched controls should include:

```text
matched non-candidate middle-regime environments
same-environment non-candidate windows
same parameter-region fresh-seed controls if available
```

Matching dimensions:

```text
parameter region
out-degree target
constraint density
constraint strength
constraint_change_weight
constraint_arity
asymmetry strength
reversibility fraction
roughness strength
probe family
horizon window
start_samples
```

Required output:

```text
matched_control_bundle.csv
```

### 2.2 Candidate-control ranks

For each support/distribution metric, report candidate rank against its matched-control bundle.

Metrics:

```text
support_deformation_score
distribution_deformation_score
mixed_deformation_score
JS_to_triviality_nulls
JS_to_support_nulls
TV_distance_to_matched_control
mass_shift_vs_control
support_symmetric_difference_fraction
support_growth_slope_delta
support_stabilization_delta
```

Required columns:

```text
candidate_metric
control_mean
control_std
candidate_minus_control_mean
candidate_control_rank
candidate_control_percentile
control_count
```

### 2.3 Margin sensitivity

Compute class stability under multiple candidate-control margins:

```text
margin_grid: 0.00, 0.01, 0.02, 0.05, 0.10
```

Required output:

```text
deformation_margin_sensitivity.csv
```

Report:

```text
class_at_margin_0_00
class_at_margin_0_01
class_at_margin_0_02
class_at_margin_0_05
class_at_margin_0_10
margin_stability_class
```

Suggested margin stability classes:

```text
fragile_margin_candidate
moderate_margin_candidate
strong_margin_candidate
control_equivalent_all_margins
margin_sensitive_fakeout
```

### 2.4 Support-vs-distribution separation

Separate:

```text
support deformation:
  reachable signature support differs from controls/nulls

distribution beyond support:
  signature mass distribution differs after support effects are controlled
```

Required columns:

```text
support_only_score
distribution_given_support_score
mixed_score
support_explains_distribution_flag
distribution_beyond_support_flag
```

### 2.5 Recurrence scoring

Do not require exact candidate recurrence.

Score phenotype-level recurrence across:

```text
starts
probe families
fresh seeds
horizon windows
nearby parameter variants
```

Required columns:

```text
start_recurrence_score
probe_recurrence_score
fresh_seed_recurrence_score
horizon_recurrence_score
parameter_neighborhood_recurrence_score
phenotype_recurrence_score
```

### 2.6 Fakeout penalties/demotions

Retain fakeout classes, but make them explicit scoring dimensions:

```text
probe_collision_penalty
support_ceiling_penalty
identity_like_penalty
matched_control_equivalence_penalty
low_outdegree_or_path_count_penalty
fast_saturation_penalty
collapse_or_cycle_penalty
```

Do not discard rows only because they are fakeouts. Preserve them for sweep analysis.

## 3. Local parameter sweep around candidate and fakeout anchors

Run local sweeps around selected anchor rows.

The goal is to determine whether each phenotype is:

```text
stable
knife-edge
transitional
fakeout basin
near miss
collapse/saturation boundary
probe-resolution boundary
matched-control boundary
```

## 4. Anchor selection

Select anchors from the latest support/distribution taxonomy smoke.

Suggested target anchors:

```text
3 mixed_support_distribution_candidate anchors
2 support_deformation_candidate anchors
3 matched_control_equivalent anchors
3 support_ceiling_limited anchors
3 probe_collision_limited anchors
2 underdetermined anchors
```

If exact counts are unavailable, sample proportionally but ensure both candidate residues and fakeouts are included.

Do not select only the strongest candidate rows.

Required output:

```text
local_sweep_anchor_selection.csv
```

Columns:

```text
anchor_id
environment_id
parameter_set_id
anchor_primary_class
anchor_probe_family
anchor_start_samples
anchor_horizon_window
selection_reason
anchor_deformation_scores
anchor_fakeout_tags
```

## 5. Sweep dimensions

Run local one-factor-at-a-time sweeps around each anchor.

Primary dimensions:

```text
constraint_density
constraint_strength
constraint_change_weight
asymmetry_strength
out_degree_target
reversibility_fraction
```

Secondary dimensions if cheap:

```text
update_footprint
rewire_probability
roughness_strength
constraint_arity
```

### 5.1 Sweep values

Use adjacent values around the anchor, not full factorial explosion.

Examples:

```text
constraint_density: 0.10, 0.25, 0.40
constraint_strength: 0.25, 0.5, 1.0, 2.0, 4.0
constraint_change_weight: 0.0, 0.1, 0.35, 0.75, 1.5
asymmetry_strength: 0.0, 0.125, 0.25, 0.5, 0.75
out_degree_target: 2, 3, 4, 6
reversibility_fraction: 0.0, 0.25, 0.5, 0.75
roughness_strength: 0.0, 0.001, 0.003, 0.01, 0.03, 0.05
```

For each anchor, include:

```text
baseline
one-step-down where possible
one-step-up where possible
```

### 5.2 Pair interactions

Run only a small number of pairwise sweeps:

```text
constraint_density x constraint_strength
constraint_strength x constraint_change_weight
asymmetry_strength x reversibility_fraction
out_degree_target x constraint_density
```

Do not run a full factorial unless the run is explicitly upgraded later.

## 6. Fresh seeds per local variant

For each local parameter variant, run fresh environment seeds.

Suggested:

```text
fresh_seeds_per_variant: 3
minimum: 2
```

This is necessary to distinguish local parameter effects from one seed realization.

## 7. Start/probe/horizon settings

Use:

```text
start_samples: 3 and 8
horizons: 0, 1, 2, 4, 8, 12, 16, 24
```

Probe families:

```text
coordinate_tuple_k3
coordinate_tuple_k4
constraint_profile_hash
constraint_violation_count_plus_local_tuple
existing low probes for continuity
strict-state controls as resolution controls only
```

Do not let strict-state controls drive candidate classification.

## 8. Outputs

Required outputs:

```text
deformation_detector_upgrade_report.md
matched_control_bundle.csv
deformation_rank_effect_summary.csv
deformation_margin_sensitivity.csv
support_vs_distribution_separation.csv
local_sweep_anchor_selection.csv
local_parameter_sweep_results.csv
phenotype_transition_graph.csv
local_parameter_sensitivity.csv
fakeout_transition_summary.csv
candidate_stability_summary.csv
near_miss_summary.csv
regime_boundary_summary.csv
status.json
```

Optional:

```text
anchor_case_studies.md
sweep_heatmap_data.csv
parameter_interaction_summary.csv
```

## 9. Phenotype transition classes

For each anchor and sweep neighborhood, classify:

```text
candidate_stable_region
candidate_knife_edge
fakeout_stable_artifact
fakeout_to_candidate_transition
candidate_to_fakeout_transition
collapse_boundary
saturation_boundary
probe_resolution_boundary
matched_control_boundary
roughness_boundary
asymmetry_lockin_boundary
constraint_conflict_boundary
underdetermined_transition
```

## 10. Candidate stability summary

For candidate anchors, report:

```text
baseline_class
variant_classes
candidate_retention_rate
candidate_retention_rate_by_parameter
fresh_seed_recurrence_rate
start_recurrence_rate
probe_recurrence_rate
margin_stability_class
transition_class
```

Interpretation:

```text
stable across local parameter variants:
  more interesting

appears only at exact anchor:
  knife-edge or seed artifact

becomes fakeout under nearby variants:
  boundary case

strengthens under nearby variants:
  near-miss / candidate basin edge
```

## 11. Fakeout transition summary

For fakeout anchors, report whether fakeout class is stable or transitional.

Examples:

```text
matched_control_equivalent -> mixed_support_distribution_candidate
support_ceiling_limited -> support_deformation_candidate
probe_collision_limited -> distribution_deformation_candidate
underdetermined -> support_deformation_candidate
```

This is important because rare interesting regimes may first appear as fakeouts or near misses.

## 12. Regime boundary summary

Summarize which parameters move rows between classes.

Report:

```text
most_sensitive_parameter
least_sensitive_parameter
candidate_promoting_parameter_changes
fakeout_promoting_parameter_changes
collapse_promoting_parameter_changes
saturation_promoting_parameter_changes
probe_limitation_promoting_parameter_changes
```

Examples of useful findings:

```text
increasing constraint_change_weight turns matched_control_equivalent into support_deformation_candidate
reducing constraint_density resolves support_ceiling_limited into mixed_support_distribution_candidate
increasing asymmetry_strength creates lock-in / support ceiling
increasing out_degree_target collapses candidate into saturation/matched-control equivalence
```

## 13. Suggested run shape

Medium diagnostic, not massive atlas.

Suggested:

```text
anchors: 12-16
local variants per anchor: 20-40
fresh seeds per variant: 2-3
start_samples: 3 and 8
horizons: 0,1,2,4,8,12,16,24
probe families: 5-7
workers: 18
wall clock: 2-6 hours
```

If runtime is high, priority order:

```text
1. detector upgrade on existing smoke outputs
2. one-factor sweeps for constraint_density, constraint_strength, constraint_change_weight, asymmetry_strength
3. fresh seeds for candidate anchors
4. fakeout anchor sweeps
5. pairwise interactions
```

## 14. Final report requirements

The final report must answer:

```text
Do candidate residues remain candidates under upgraded scoring?
Are they stable across local parameter variants?
Which fakeouts are stable artifacts and which are near-miss transitions?
Which parameters most strongly govern support/distribution phenotype transitions?
Are matched-control-equivalent rows hiding candidate regimes nearby?
Does support_ceiling_limited sometimes resolve into real deformation under parameter changes?
Do probe_collision_limited rows remain measurement artifacts or become interpretable with selected probes?
Should the next run be medium-breadth atlas, another local sweep, or measurement-limits note?
```

## 15. Decision outcomes

### 15.1 Proceed to medium-breadth atlas

If:

```text
candidate or near-miss phenotypes recur across fresh seeds and local neighborhoods
fakeout-to-candidate transitions identify sensitive parameter directions
matched controls no longer explain the most stable candidates
```

Then:

```text
run a medium-breadth support/distribution atlas concentrated around promising parameter bands
```

### 15.2 Continue local sweeps

If:

```text
candidate/fakeout transitions are observed but parameter boundaries are unclear
```

Then:

```text
run a second local sweep with fewer anchors and more parameter resolution
```

### 15.3 Write measurement-limits note / pause

If:

```text
candidate residues vanish under upgraded scoring
fakeouts remain stable artifacts
matched controls explain all nearby variants
```

Then:

```text
write measurement-limits note and reassess detector/generator design
```

## 16. Claim boundary

Allowed:

```text
A local parameter neighborhood produces stable support/distribution deformation under specified controls.
A fakeout class transitions into a candidate class under specified parameter changes.
A candidate is margin-stable or margin-fragile.
A parameter appears sensitivity-linked to support/distribution phenotype transitions.
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
```

## 17. Bottom line

Rare-regime search needs breadth, but not blind breadth.

First make the detector less brittle, then sweep locally around both candidates and fakeouts to learn the phenotype transition geometry.

Then scale the atlas where the transition geometry says to look.

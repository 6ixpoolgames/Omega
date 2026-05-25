# RFS-MB0 Medium-Breadth Support/Distribution Atlas 10h Spec

Status: next-run spec after deformation detector upgrade and local sweep small result

Purpose: use a 10-hour wall-clock window to run a guided medium-breadth support/distribution atlas. The run should scale breadth around locally promising transition bands, while preserving the upgraded detector, matched controls, margin sensitivity, fakeout taxonomy, and strict claim boundary.

This follows:

```text
docs/RFS_MB0_SUPPORT_DISTRIBUTION_DEFORMATION_TAXONOMY_SPEC.md
docs/RFS_MB0_DEFORMATION_DETECTOR_AND_LOCAL_SWEEP_SPEC.md
```

and the latest result:

```text
candidate residues remain under upgraded scoring: true
fakeout-to-candidate transitions observed: true
local support/distribution transition geometry present
recommended next step: proceed_to_medium_breadth_atlas
```

## 0. Strategic framing

We have enough evidence to scale one level:

```text
the support/distribution workflow is operational
the detector upgrade produced rank/effect/margin-sensitive outputs
local parameter sweeps found candidate-stable and fakeout-to-candidate transitions
path metrics remain parked and should not drive classification
```

The goal is not to find Omega.

The goal is to map whether support/distribution deformation phenotypes recur across a broader but still guided parameter atlas.

Use the 10-hour budget for:

```text
breadth across parameter neighborhoods
fresh seeds
matched-control bundles
start recurrence
probe-family recurrence
margin sensitivity
small n=6 transfer checks for stable regions
```

Do not spend the main budget on:

```text
path metrics
large n=7/n=8 state spaces
new substrate machinery
agent/value/identity labels
```

## 1. Main question

Ask:

```text
Do locally observed support/distribution deformation and fakeout-to-candidate transition bands recur across broader parameter neighborhoods, fresh seeds, starts, and probe families?
```

Secondary question:

```text
Which parameter bands produce stable candidate regions, near-miss transitions, matched-control equivalence, saturation boundaries, or probe-resolution boundaries?
```

## 2. Budget allocation

Use the 10-hour wall clock in stages.

Suggested allocation:

```text
Stage A: integrity/preflight and anchor-band extraction        10-20 min
Stage B: guided n=5 medium-breadth atlas                       4-5 h
Stage C: fresh-seed confirmation on promising bands            2-3 h
Stage D: matched-control bundle expansion and margin audit     1 h
Stage E: limited n=6 transfer check                            1 h
Stage F: final synthesis/regime map                            20-40 min
```

If runtime is much faster than expected, spend surplus on more fresh seeds and matched controls, not larger state spaces.

## 3. Input anchors

Use anchor classes from the deformation detector sweep result.

Priority anchors:

```text
candidate_stable_region
fakeout_to_candidate_transition
candidate_to_fakeout_transition
saturation_boundary
probe_resolution_boundary
```

Do not ignore fakeouts. Some fakeouts transitioned into candidate classes under nearby parameter variants, so they should seed parts of the atlas.

Required input outputs from previous run:

```text
phenotype_transition_graph.csv
local_parameter_sensitivity.csv
fakeout_transition_summary.csv
candidate_stability_summary.csv
near_miss_summary.csv
regime_boundary_summary.csv
```

## 4. Parameter bands to sample

Use the local sweep to construct guided parameter bands.

Core dimensions:

```text
constraint_density
constraint_strength
constraint_change_weight
asymmetry_strength
out_degree_target
reversibility_fraction
```

Include baseline values and nearby values around transition boundaries.

Suggested default grid, pruned around observed local bands:

```text
constraint_density: 0.10, 0.25, 0.40
constraint_strength: 0.5, 1.0, 2.0
constraint_change_weight: 0.0, 0.35, 0.75
asymmetry_strength: 0.0, 0.25, 0.5
out_degree_target: 2, 3, 4
reversibility_fraction: 0.0, 0.25, 0.5
```

If local sweep identifies specific promoting values, oversample those bands.

Do not use a full Cartesian grid blindly. Use stratified sampling with quotas.

## 5. Sampling quotas

Recommended 10h quotas, adjustable by runtime:

```text
n=5 guided parameter sets: 300-800
fresh seeds per parameter set: 2-5
starts: 3 and 8
probe families: 5-7
matched controls per candidate: target 3-5
null/control replicates: 5 where applicable
```

If jobs are cheap, increase in this order:

```text
1. fresh seeds per promising parameter band
2. matched controls per candidate
3. number of parameter sets around fakeout-to-candidate bands
4. n=6 transfer checks
5. additional starts, e.g. start_samples=16
```

Do not increase path horizons or path metrics.

## 6. Probe families

Use calibrated support/distribution probes, not path-focused probes.

Recommended:

```text
coordinate_tuple_k3
coordinate_tuple_k4
constraint_profile_hash
constraint_violation_count_plus_local_tuple
existing_low for continuity
relation_role as diagnostic only
full_state_hash / full_state_strict as identity-like controls only
```

For classification, strict-state controls must not drive candidate promotion.

Rows should report:

```text
probe_collision_rate
support_ceiling_flag
probe_resolution_class
probe_family_local vs cross_probe_recurrent
```

## 7. Horizons and starts

Use:

```text
horizons: 0,1,2,4,8,12,16,24,32
start_samples: 3,8
```

If runtime permits:

```text
start_samples: 16 for promising bands only
```

Report recurrence across starts as a score, not an exact-match requirement.

## 8. Detector requirements

Use the upgraded detector from the local sweep.

Required scoring:

```text
rank/effect-size vs matched-control bundle
margin sensitivity over 0.00, 0.01, 0.02, 0.05, 0.10
support-vs-distribution separation
recurrence scoring across starts/probes/seeds/horizons
explicit fakeout penalties
```

Candidate classes should remain diagnostic:

```text
support_deformation_candidate
distribution_deformation_candidate
mixed_support_distribution_candidate
matched_control_equivalent
probe_collision_limited
support_ceiling_limited
identity_like_control
underdetermined
```

Add atlas-level classes:

```text
stable_candidate_band
near_miss_transition_band
stable_fakeout_band
saturation_boundary_band
probe_resolution_boundary_band
matched_control_boundary_band
```

## 9. Matched controls

Matched controls are mandatory.

For every candidate-like row, attach a bundle of controls:

```text
matched non-candidate middle-regime environments
same-environment non-candidate windows
same parameter-neighborhood fresh-seed controls where available
```

Target:

```text
3-5 controls per candidate-like row
```

Rows with fewer than 3 controls should be marked:

```text
weak_control_bundle
```

and should not be promoted to stable-band status.

## 10. Stage plan

### Stage A: Preflight and band extraction

Read the local sweep outputs and identify:

```text
candidate-stable anchors
fakeout-to-candidate anchors
candidate-to-fakeout boundaries
saturation/probe-resolution boundaries
most sensitive parameters
candidate-promoting parameter changes
```

Output:

```text
atlas_band_selection.csv
atlas_sampling_plan.csv
```

### Stage B: Guided n=5 medium-breadth atlas

Run stratified parameter sampling around selected bands.

Output ordinary support/distribution taxonomy artifacts plus:

```text
atlas_raw_metric_rows.csv
atlas_candidate_rows.csv
atlas_fakeout_rows.csv
```

### Stage C: Fresh-seed confirmation

For top bands from Stage B, rerun fresh seeds.

Criteria for top bands:

```text
candidate rate above matched controls
margin-stable candidate rows
not dominated by probe collision/support ceiling
recurs across start_samples 3 and 8
```

Output:

```text
fresh_seed_band_confirmation.csv
```

### Stage D: Matched-control and margin audit

Expand matched-control bundles for candidate-like bands.

Output:

```text
atlas_matched_control_bundle.csv
atlas_margin_sensitivity.csv
atlas_rank_effect_summary.csv
```

### Stage E: Limited n=6 transfer

Only for the strongest n=5 bands.

Use n=6 as a transfer check, not a primary search space.

Output:

```text
n6_transfer_summary.csv
```

### Stage F: Final synthesis

Output final report and regime map.

## 11. Outputs

Required outputs:

```text
medium_breadth_support_distribution_atlas_report.md
atlas_band_selection.csv
atlas_sampling_plan.csv
atlas_rank_effect_summary.csv
atlas_margin_sensitivity.csv
atlas_support_vs_distribution_separation.csv
atlas_matched_control_bundle.csv
atlas_regime_map.csv
atlas_band_summary.csv
atlas_fakeout_transition_summary.csv
atlas_candidate_stability_summary.csv
fresh_seed_band_confirmation.csv
n6_transfer_summary.csv
status.json
```

Optional:

```text
atlas_heatmap_data.csv
atlas_anchor_case_studies.md
atlas_band_examples.json
```

## 12. Final report requirements

The report must answer:

```text
Do candidate-stable local neighborhoods generalize to broader parameter bands?
Do fakeout-to-candidate transitions recur under fresh seeds?
Which parameter bands produce stable support/distribution deformation?
Which bands collapse into matched-control equivalence?
Which bands are saturation/probe-resolution boundaries?
Which support/distribution effects remain after matched-control bundles and margin sensitivity?
Which candidate bands transfer from n=5 to n=6?
Should the next step be broader atlas, second local sweep, path revisit, or measurement-limits note?
```

## 13. Decision outcomes

### 13.1 Broader atlas

Proceed if:

```text
multiple bands show stable candidate rates across fresh seeds
matched controls are lower or qualitatively different
margin-stable candidates recur across starts and probes
some n=6 transfer is observed or failure is interpretable
```

### 13.2 Second local sweep

Proceed if:

```text
candidate/fakeout transitions recur but boundaries remain narrow or unclear
```

### 13.3 Support/distribution theory note

Proceed if:

```text
support/distribution deformation is stable enough to describe but not yet broad enough for stronger empirical claims
```

### 13.4 Measurement-limits note / pause

Proceed if:

```text
candidate bands vanish under breadth
matched controls explain all bands
fakeout classes dominate all fresh seeds
```

## 14. Claim boundary

Allowed:

```text
A parameter band reproducibly produces support/distribution deformation under specified controls.
A fakeout-to-candidate transition band recurs under fresh seeds.
A deformation phenotype is stable, near-miss, matched-control-equivalent, saturation-boundary, or probe-resolution-boundary.
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

## 15. Bottom line

Use the full 10-hour window, but spend it on breadth that tests the local transition geometry.

Do not scale blindly.

Do not return to path metrics yet.

Run a guided medium-breadth support/distribution atlas with fresh seeds, matched-control bundles, margin sensitivity, and limited n=6 transfer.

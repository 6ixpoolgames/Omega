# RFS-MB1 Neutral Coupled Landscape Audit Spec

Status: future-branch design spec / VAL1-MF salvage note

Purpose: preserve the useful measurement pattern from VAL1-MF while discarding the hand-crafted grammar action space. This spec defines a neutral coupled-landscape audit to revisit coupling, interference, and absorption/emission-like structure after RFS-MB0 support/distribution deformation is stable.

This is not the current active branch. The current active branch remains:

```text
RFS-MB0 support/distribution deformation taxonomy and guided medium-breadth atlas
```

This spec should not interrupt the 10h support/distribution atlas.

## 0. Motivation

VAL1-MF was moved away from partly because the action space was too hand-crafted:

```text
enable
obstruct
restore
commit
shared capacity
```

Those verbs are too semantically loaded. They encode many of the effects we would prefer to discover downstream.

However, VAL1-MF also contained a useful measurement pattern:

```text
same substrate pair
multiple coupling masks
counterfactual ablations
sampled deltas rather than raw joint enumeration
mode-wise comparison against uncoupled controls
```

That pattern is worth preserving.

The salvage move is:

```text
discard the grammar action-space substrate
keep the counterfactual coupling audit pattern
translate it into neutral relation-landscape coupling
```

## 1. Claim boundary

This branch must not claim:

```text
agency detected
consciousness detected
identity detected
valuer detected
Omega detected
path-process object detected
scientific gate passed
```

Allowed claims, if earned:

```text
Neutral relation-generated landscapes can produce coupled support/distribution deformation.
A coupling map produces deformation beyond magnitude-matched or shuffled controls.
A coupling effect is directional, symmetric, lagged, or control-equivalent.
A coupled deformation phenotype is stable, transitional, or fakeout-like.
```

## 2. What we salvage from VAL1-MF

Keep:

```text
counterfactual coupling masks
same-pair mode comparison
sampled support/distribution deltas
constructive/recovery effects as legitimate phenotypes
horizon-lag analysis
matched coupling controls
mode-wise ablations
neutral bins as primary, interpretive labels secondary
```

Discard or quarantine:

```text
hand-coded enable/obstruct/restore/commit action verbs
shared capacity as semantic resource
valid-action count as primary survival metric
pseudo-Omega labels
raw joint enumeration as primary evidence
agency or vortex language in code/classes
```

## 3. Core question

Ask:

```text
Given two neutral relation-generated future landscapes A and B,
does a mechanically derived coupling from A to B produce support/distribution
deformation in B or in the joint landscape beyond matched coupling controls?
```

Secondary exploratory question:

```text
Are some coupled-deformation effects directional, lagged, mechanism-specific,
or recurring across seeds/starts/probe families?
```

Do not ask yet:

```text
Is this agency?
Is this absorption/emission coupling?
Is this identity or valuerhood?
```

## 4. Substrate

Use current or future neutral relation-generated substrates, not VAL1-MF grammar actions.

Each landscape is:

```text
A = (X_A, ->_A)
B = (X_B, ->_B)
```

where each relation is generated from primitive parameters such as:

```text
finite distinction space
local update candidates
constraint profile
constraint/change penalty
asymmetry term
roughness/noise term
out-degree target
reversibility/asymmetry settings
```

The coupled system should be mechanically generated from two independently generated landscapes plus a neutral coupling map.

## 5. Coupling maps

Replace hand-crafted action verbs with neutral coupling maps derived from relation or future-profile structure.

Candidate maps:

### 5.1 Frontier-signature coupling

A's frontier signature distribution at horizon H perturbs B's transition relation or probe-facing future profile.

Examples:

```text
A frontier support mask selects a matched subset of B candidate transitions
A frontier distribution weights a neutral B edge-scoring perturbation
```

### 5.2 Constraint-profile coupling

A's generated constraint profile perturbs B's constraint weights or local compatibility scores.

Examples:

```text
A constraint violation vector -> small deterministic shift in B constraint weights
A satisfied/violated constraint pattern -> matched neutral perturbation in B relation scoring
```

### 5.3 Asymmetry-profile coupling

A's directed asymmetry profile perturbs B's directed relation scores.

Examples:

```text
A out/in asymmetry histogram -> B asymmetry-score bias
A directionality motif -> B directed edge perturbation
```

### 5.4 Motif-transfer coupling

Relation motifs detected in A are transferred into B through mechanically matched perturbations.

Examples:

```text
small directed motif in A -> matched directed perturbation in B
local relation pattern in A -> same-size randomized target pattern in B
```

### 5.5 Support-mask coupling

A's reachable support mask gates or perturbs a matched subset of B's relation candidates.

Examples:

```text
A reachable signature bucket -> B candidate edge subset
A support boundary -> B local relation perturbation
```

### 5.6 Noise/magnitude control coupling

Same perturbation magnitude, but source structure shuffled or replaced with random noise.

This is a required control, not a primary coupling map.

## 6. Coupling modes

For each generated pair and coupling map, evaluate multiple modes.

Required:

```text
uncoupled
full_coupling_A_to_B
full_coupling_B_to_A
bidirectional_full_coupling
source_shuffled_coupling
magnitude_matched_random_coupling
target_shuffled_coupling
direction_reversed_coupling
A_B_swapped_control
```

Optional:

```text
coupling_strength_sweep
coupling_lag_sweep
coupling_map_component_isolation
```

The old VAL1-MF modes `enable_only`, `restore_only`, etc. should not be used.

## 7. Primary measurements

Use support/distribution deformation metrics from RFS-MB0.

For each mode, horizon, start group, and probe family, measure:

```text
reachable_signature_support_size
reachable_signature_support_fraction
support_symmetric_difference_fraction
support_jaccard_vs_uncoupled
support_jaccard_vs_matched_random
distribution_JS_vs_uncoupled
distribution_JS_vs_matched_random
TV_distance_vs_uncoupled
mass_shift_vs_uncoupled
support_growth_curve_delta
distribution_entropy_delta
```

For B under A->B coupling:

```text
B_support_deformation_delta
B_distribution_deformation_delta
B_mixed_deformation_delta
```

For joint landscape, if computed:

```text
joint_support_deformation_delta
joint_distribution_deformation_delta
joint_cap_or_censoring_flag
```

Raw joint enumeration must not be primary. If joint enumeration is used, it is diagnostic only.

## 8. Core coupling-specific scores

Compute:

```text
coupled_deformation_delta = deformation(full_coupling) - deformation(uncoupled)

specific_coupling_excess =
  deformation(full_coupling)
  - deformation(magnitude_matched_random_coupling)

source_structure_excess =
  deformation(full_coupling)
  - deformation(source_shuffled_coupling)

target_specificity_excess =
  deformation(full_coupling)
  - deformation(target_shuffled_coupling)

directionality_delta =
  deformation(A_to_B) - deformation(B_to_A)
```

Report rank/effect-size rather than only threshold passes.

## 9. Lag/horizon profile

Use a horizon grid rather than a single horizon.

Suggested:

```text
H = 4, 8, 16, 24, 32
```

If cheap:

```text
H = 48, 64
```

Classify lag profiles:

```text
immediate_spillover
short_lag_coupling
delayed_coupling
late_saturation_only
no_detectable_coupling
```

Immediate-only effects should be treated cautiously because they may be direct spillover or magnitude artifacts.

## 10. Phenotype classes

Use neutral descriptive classes.

Primary classes:

```text
no_detectable_coupling
magnitude_only_deformation
source_structure_specific_deformation
target_specific_deformation
directional_coupling
symmetric_coupling
bidirectional_coupling
lagged_coupling
support_expansion_coupling
support_contraction_coupling
distribution_shift_coupling
mixed_support_distribution_coupling
cap_or_censoring_limited
probe_limited_coupling
control_equivalent_coupling
underdetermined_coupling
```

Exploratory later-use classes, still non-agentic:

```text
absorption_emission_proxy_candidate
capture_like_coupling
symbiotic_like_coupling
```

These last classes are allowed only in reports as speculative descriptors, not code-level positive claims.

## 11. Fakeout taxonomy

Classify common fakeouts:

```text
magnitude_only_fakeout
source_shuffle_equivalent
target_shuffle_equivalent
probe_collision_fakeout
support_ceiling_fakeout
saturation_fakeout
low_outdegree_fakeout
joint_enumeration_cap_fakeout
shared_parameter_common_cause_fakeout
seed_pair_idiosyncrasy
```

Do not discard fakeouts. They are useful for mapping coupled-landscape failure modes.

## 12. Matched controls

Every candidate-like coupling row must have matched controls.

Required controls:

```text
uncoupled same pair
magnitude-matched random coupling
source-shuffled coupling
target-shuffled coupling
direction-reversed coupling
A/B swapped control
fresh-seed matched pair where available
```

If a row lacks controls, mark:

```text
descriptive_only_missing_controls
```

and do not promote it beyond descriptive phenotype status.

## 13. Starts and probe families

Use multiple starts.

Suggested:

```text
start_samples: 3 and 8
optional: 16 for promising rows
```

Use multiple probe families:

```text
coordinate_tuple_k3
coordinate_tuple_k4
constraint_profile_hash
constraint_violation_count_plus_local_tuple
relation_role diagnostic probes
strict-state controls as resolution ceilings only
```

Report:

```text
start_recurrence_score
probe_recurrence_score
seed_recurrence_score
horizon_recurrence_score
```

## 14. Suggested first run shape

This is a future exploratory audit, not a validation atlas.

Suggested:

```text
paired landscapes: 50-150
fresh seeds per promising pair: 2-3
coupling maps: 3-5
coupling modes: required controls above
horizons: 4,8,16,24,32
start_samples: 3 and 8
probe families: 4-6
workers: 18
wall clock: 1-4 hours
```

If cheap, expand by:

```text
more fresh seeds
more matched controls
more coupling-map diversity
longer horizon grid
```

Do not expand by:

```text
hand-coded action verbs
large n state spaces
path-process metrics as primary evidence
agency labels
```

## 15. Outputs

Required outputs:

```text
neutral_coupled_landscape_audit_report.md
coupled_landscape_sampling_plan.csv
coupling_map_summary.csv
coupling_mode_metric_rows.csv
coupling_specificity_summary.csv
coupling_horizon_lag_profile.csv
coupling_matched_controls.csv
coupling_fakeout_summary.csv
coupling_phenotype_summary.csv
coupling_start_probe_recurrence.csv
coupling_case_studies.md
status.json
```

Optional:

```text
coupling_heatmap_data.csv
coupling_map_examples.json
joint_landscape_diagnostic_summary.csv
```

## 16. Final report requirements

The report must answer:

```text
Do neutral coupling maps produce support/distribution deformation beyond uncoupled controls?
Are effects explained by perturbation magnitude alone?
Does source structure matter after source-shuffled controls?
Does target specificity matter after target-shuffled controls?
Are effects directional or symmetric?
Are effects immediate-only or lagged?
Do effects recur across starts, probes, seeds, and horizons?
Which coupling maps are mostly fakeouts?
Which coupling maps are promising for later agency-assessment probes?
Should this become RFS-MB1, remain a sandbox, or be deferred?
```

## 17. Relation to agency assessment

This audit does not assess agency directly.

It can later support agency assessment by providing a neutral coupled-landscape layer:

```text
single-landscape deformation
-> coupled-landscape deformation
-> directional cross-landscape deformation
-> lagged source-structure-specific deformation
-> later self-future or absorption/emission-style probes
```

The vortical/absorption-emission idea should remain quarantined as probe-design context.

Do not implement consciousness, qualia, agency, identity, or valuer labels here.

## 18. Decision outcomes

### 18.1 Promote to RFS-MB1 coupled landscape branch

If:

```text
source-structure-specific or target-specific coupling survives matched controls
coupled deformation recurs across starts/probes/seeds/horizons
fakeouts are classifiable
lag/directionality profiles are interpretable
```

Then:

```text
run a broader neutral coupled-landscape atlas
```

### 18.2 Keep as exploratory sandbox

If:

```text
some coupling-specific effects appear but boundaries are narrow or unstable
```

Then:

```text
run a smaller local coupling-map sweep
```

### 18.3 Defer

If:

```text
all effects collapse to magnitude-only, source-shuffle equivalence,
probe limits, or saturation artifacts
```

Then:

```text
archive as measurement lesson and do not pursue until single-landscape deformation is stronger
```

## 19. Bottom line

VAL1-MF should not be revived as a grammar-action experiment.

Its useful legacy is the counterfactual coupling audit pattern.

The future branch should test neutral relation-landscape coupling:

```text
Does one future landscape mechanically perturb another in a way that creates
specific support/distribution deformation beyond shuffled and magnitude-matched controls?
```

That is the salvageable general form.

# RFS-MB0 Asymmetry-Ladder Transition-Energy Substrate Spec

Status: implemented design-set substrate-law characterization spec
Builds on: `docs/research_notes/omega_theory/transition_energy_and_constraint_untethering.md`, `docs/research_notes/omega_theory/transition_energy_substrate_atlas.md`, and `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_transition_energy_substrate_characterization_result.md`
Claim boundary: no holdout scoring, no candidate promotion, no Omega detection, no agency detection, no identity detection, no valuer detection

Implementation results: see `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_asymmetry_ladder_transition_energy_result.md` and `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_asymmetry_ladder_preservation_scaleup_result.md`. The first seed-scaled batch and preservation-focused scaleup reached `preservation_asymmetry_loadbearing`; this is substrate characterization only.

## 0. One-sentence purpose

Test which minimal asymmetry ingredient produces which horizon-transport response profile: locality alone, directional asymmetry, preservation asymmetry, or the combined directional-plus-preservation substrate.

Plainly:

```text
How do directional asymmetry and preservation asymmetry, separately and jointly,
shape reachable futures under the horizon-transport instrument?
```

## 1. Why this spec exists

The transition-energy substrate atlas established that the instrument is no longer only detecting a pattern inside the original hand-built constraint-template substrate.

It showed:

```text
locality-only:
  clean baseline; no aligned amplification in the tested grid

smooth directional field:
  response-bearing; rerouting/reopening/weakening appear, but no aligned amplification in the tested grid

macro-invariant / asymmetry-preservation:
  aligned response appears; total-coordinate-mass strongest but coverage-limited

constraint-template comparator:
  still positive; no longer unique
```

The theory terminology has also been tightened:

```text
Do not call the invariant-preserving family budget.
The theory concept is macro-invariant / asymmetry-preservation.
```

The next empirical question is therefore not whether a single substrate family wins. It is:

```text
Which minimal asymmetry ingredient causes which transport response regime?
```

## 2. Claim boundary

Allowed claims:

```text
locality-only, directional-asymmetry, preservation-asymmetry, and combined-asymmetry substrates produce different horizon-transport response profiles;
matched marginal detector-null separation does or does not hold by substrate family;
aligned amplification, rerouting, reopening, weakening, collapse, stability, and control-equivalence appear or do not appear under each family;
which asymmetry ingredients deserve further scaleup, repair, or max-entropy treatment.
```

Forbidden claims:

```text
Omega detected;
agent detected;
valuer detected;
identity detected;
life detected;
self-replication detected;
candidate promoted;
holdout ready;
graph-channel causality shown.
```

Required counters:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## 3. Core substrate ladder

Use explicit transition-energy families.

Let:

```text
X:
  finite distinction space

Q(s -> t):
  local proposal neighborhood

d(s,t):
  locality distance, normally Hamming distance

A(s):
  directional asymmetry field

I(s):
  macro-invariant / coarse asymmetry coordinate

R(s,t):
  deterministic seeded roughness term

E(s,t):
  transition energy / edge-selection score
```

A transition exists when the edge-selection rule selects a low-energy candidate:

```text
edges(s) = top_m candidates t in Q(s) by lowest E(s,t)
```

No term in `E(s,t)` is value, reward, utility, fitness, or Omega.

## 4. Required substrate families

### 4.1 E0: locality only

```text
substrate_family: locality_only

E_0(s,t) = d(s,t) + epsilon * R(s,t)
```

Purpose:

```text
baseline for bounded local branching without additional lawlike asymmetry.
```

Expected tendency:

```text
mostly stable / diffusion-like / possible reopening;
no aligned amplification unless locality alone is sufficient under the tested grid.
```

### 4.2 E1: directional asymmetry

```text
substrate_family: directional_asymmetry

E_1(s,t) = d(s,t) + alpha * (A(t) - A(s)) + epsilon * R(s,t)
```

Purpose:

```text
test whether a minimal directional field produces rerouting, horizon-threshold shifts,
or aligned amplification.
```

Expected tendency:

```text
rerouting;
horizon-threshold shifts;
gradient-sensitive transport;
possibly weakening at stronger alpha or perturbation.
```

Required metadata:

```text
asymmetry_field_seed
asymmetry_field_smoothness
asymmetry_alpha
asymmetry_delta_distribution
asymmetry_neighbor_correlation
```

### 4.3 E2: preservation asymmetry

```text
substrate_family: preservation_asymmetry

E_2(s,t) = d(s,t) + beta * |I(t) - I(s)| + epsilon * R(s,t)
```

Purpose:

```text
test whether preserving coarse asymmetry structure supports aligned amplification
or high-viscosity coherent transport.
```

Expected tendency:

```text
aligned amplification;
high-viscosity coherent transport;
stable-to-amplified response surfaces;
possible weakening/reopening depending on invariant kind.
```

Required invariant kinds:

```text
total_coordinate_mass
hamming_weight_or_nonzero_count
symbol_histogram_distance
```

Required metadata:

```text
macro_invariant_kind
macro_invariant_beta
macro_invariant_delta_distribution
macro_invariant_value_distribution
coverage_by_invariant_kind
paired_baseline_availability_by_invariant_kind
baseline_missing_by_invariant_kind
resolution_mismatch_by_invariant_kind
```

### 4.4 E3: combined asymmetry

```text
substrate_family: combined_asymmetry

E_3(s,t) = d(s,t) + alpha * (A(t) - A(s)) + beta * |I(t) - I(s)| + epsilon * R(s,t)
```

Purpose:

```text
test whether direction and preservation together produce richer response surfaces
than either asymmetry ingredient alone.
```

Expected tendency:

```text
amplification plus rerouting;
response thresholds that move with alpha/beta;
possible weakening, reopening, or collapse at stronger settings;
more structured horizon-dependent phase profile than E1 or E2 alone.
```

Required metadata:

```text
asymmetry_alpha
macro_invariant_beta
alpha_beta_pair
asymmetry_delta_distribution
macro_invariant_delta_distribution
interaction_read
```

### 4.5 Comparator: constraint-template current

```text
substrate_family: constraint_template_current
```

Purpose:

```text
historical comparator only.
```

Do not add new hand-built symbolic constraint templates.

## 5. Required parameter grid

### 5.1 Shared state/proposal settings

Use current comparable defaults first:

```text
coordinate_count: current default
alphabet_size: current default
update_footprint: current comparator
out_degree_target: current comparator
roughness_strength: current comparator plus optional low/high diagnostic
```

Use the same local proposal kernel for E0/E1/E2/E3:

```text
Q(s): all states within Hamming distance <= update_footprint
```

### 5.2 Directional asymmetry parameters

Sweep:

```text
asymmetry_alpha:
  low
  medium
  high

asymmetry_field_smoothness:
  low
  medium
  high
```

If compute is constrained, use:

```text
alpha: low, medium, high
smoothness: medium
```

### 5.3 Preservation asymmetry parameters

Sweep:

```text
macro_invariant_kind:
  total_coordinate_mass
  hamming_weight_or_nonzero_count
  symbol_histogram_distance

macro_invariant_beta:
  low
  medium
  high
```

If compute is constrained, prioritize:

```text
hamming_weight_or_nonzero_count:
  cleaner behavior in prior atlas

total_coordinate_mass:
  strongest aligned fraction, but needs paired-baseline availability audit

symbol_histogram_distance:
  differentiated response / reopening signal
```

### 5.4 Combined asymmetry parameters

Use a sparse alpha/beta grid first:

```text
alpha_beta_pairs:
  low_alpha_low_beta
  low_alpha_medium_beta
  medium_alpha_low_beta
  medium_alpha_medium_beta
  high_alpha_medium_beta
  medium_alpha_high_beta
```

For each pair, run at least two macro-invariant kinds:

```text
hamming_weight_or_nonzero_count
total_coordinate_mass
```

Add `symbol_histogram_distance` if compute allows.

## 6. Run shape

This should be a moderate design-set run, not a giant validation pass.

Suggested default:

```text
substrate_families:
  locality_only
  directional_asymmetry
  preservation_asymmetry
  combined_asymmetry
  constraint_template_current comparator

family_parameter_variants:
  locality_only: 1 to 3
  directional_asymmetry: 3 to 9
  preservation_asymmetry: 9
  combined_asymmetry: 12 to 18
  constraint_template_current: 1

groups_per_family_variant: 24 to 48
design_groups_per_family_variant: 8 to 16
fresh_seeds_per_group: 6
start_samples_list: 2,4,8,16
null_replicates: 13 or 15
workers: machine appropriate
max_runtime_seconds: 28800
shutdown_cushion_seconds: 1800
```

If runtime is too large, prioritize:

```text
1. E0 locality baseline
2. E2 preservation asymmetry grid
3. E1 directional asymmetry medium-smoothness grid
4. E3 sparse combined grid
5. constraint-template comparator
```

If runtime is cheap, increase seeds before adding new substrate concepts.

## 7. Horizon pairs

Use the H128-compatible horizon set:

```text
1->2
2->4
4->8
8->16
16->24
24->32
32->48
48->64
64->96
96->128
```

Optional if coverage is strong across all asymmetry families:

```text
128->256
256->512
```

Do not run H1280 in this spec. The goal is asymmetry-family characterization, not horizon extension.

## 8. Perturbation ladder

Required perturbation families:

```text
small_edge_resample_control
asymmetric_edge_flip_control
```

Required strengths:

```text
0.006
0.010
0.015
0.020
0.030
```

Optional boundary strengths:

```text
0.040
0.060
```

If boundary strengths are included, label them:

```text
intervention_class: boundary_probe
interpretation_role: viability_boundary_mapping
allowed_claim_level: viability_boundary_only
```

## 9. Probes and flow modes

Use grammar-neutral probes as primary:

```text
full_state_hash
relation_role
```

Optional diagnostic probes:

```text
constraint_profile_hash only for constraint_template_current comparator
constraint_violation_count_plus_local_tuple only for constraint_template_current comparator
```

Do not use constraint-template-specific probes to compare transition-energy families.

Required flow modes:

```text
window_transport_flow
one_step_transport_flow
```

Backward-compatible aliases may be emitted if the runner currently uses:

```text
constrained_window_flow
one_step_local_flow
```

## 10. Detector and response requirements

Required detector-null families:

```text
context_shuffle_transport_null
horizon_pair_shuffle_transport_null
row_marginal_matched_transport_null
column_marginal_matched_transport_null
row_column_marginal_matched_transport_null
```

Required statistic:

```text
marginal_residual_fraction
```

Required response classes:

```text
transport_stable
transport_amplified_aligned
transport_weakened
transport_rerouted
transport_reopens
transport_collapses
transport_control_equivalent
transport_baseline_missing
transport_insufficient_common_items
transport_resolution_mismatch
transport_response_underpowered
```

Baseline-symmetry guard:

```text
Response classification must require paired baseline and perturbation matrix
availability across substrate variant, probe, flow mode, horizon pair, and
perturbation family.

If a perturbation matrix exists without its paired baseline, the runner must
emit transport_baseline_missing and exclude that row from response-class
dominance, aligned-amplification fractions, and other interpretable response
summaries.

The row should remain present as an auditable measurement-limit count.
```

Required fixture contract:

```text
8 / 8 response fixtures must pass before empirical response classes support interpretation.
```

## 11. Coverage and interpretability requirements

Report by substrate family and parameter variant:

```text
matched_interpretable_context_fraction
matrix_coverage_min
matrix_coverage_mean
undercoverage_fraction_by_horizon
normal_interpretation_fraction_by_horizon
resolution_mismatch_fraction
baseline_missing_fraction
insufficient_common_items_fraction
paired_baseline_available_fraction
frontier_source_state_count_mean
frontier_target_state_count_mean
row_support_mean
column_support_mean
transport_entropy_mean
largest_entry_mass_share_mean
```

Do not rank an asymmetry family by aligned amplification alone.

Use a two-axis read:

```text
response strength
coverage / interpretability
```

## 12. Required outputs

Core outputs:

```text
asymmetry_ladder_run_config.json
asymmetry_ladder_status.json
asymmetry_ladder_progress_checkpoints.csv
asymmetry_ladder_errors.csv
asymmetry_ladder_output_manifest.json
```

Substrate outputs:

```text
asymmetry_ladder_substrate_manifest.csv
transition_energy_family_summary.csv
asymmetry_field_summary.csv
macro_invariant_summary.csv
combined_asymmetry_parameter_summary.csv
substrate_capacity_by_family.csv
substrate_capacity_by_variant.csv
```

Detector outputs:

```text
horizon_transport_matrix_manifest.csv
horizon_transport_coverage.csv
horizon_transport_detector_null_gate_results.csv
horizon_transport_matched_marginal_summary.csv
matched_null_pass_by_asymmetry_family.csv
matched_null_pass_by_asymmetry_variant.csv
```

Response outputs:

```text
horizon_transport_response_classification.csv
response_by_asymmetry_family.csv
response_by_asymmetry_variant.csv
response_by_directional_alpha.csv
response_by_asymmetry_field_smoothness.csv
response_by_macro_invariant_kind.csv
response_by_macro_invariant_beta.csv
selected_edge_overlap_by_beta.csv
response_by_alpha_beta_pair.csv
response_class_by_strength_and_horizon_pair.csv
horizon_response_threshold_table.csv
```

`selected_edge_overlap_by_beta.csv` must compare the selected transition graph
for each sampled preservation-asymmetry beta value against the beta-0 graph for
the same substrate job. It is an instrumentation guard: a beta response ladder
should not be interpreted as graded unless this table shows that the selected
edge set is actually moving across the tested beta range.

Viscosity/diversity outputs:

```text
transport_viscosity_by_asymmetry_family.csv
transport_viscosity_by_asymmetry_variant.csv
response_diversity_by_asymmetry_family.csv
response_diversity_by_asymmetry_variant.csv
```

Final report:

```text
rfs_mb0_asymmetry_ladder_transition_energy_result.md
```

## 13. Final report requirements

Retain under:

```text
docs/research_notes/validation_results/rfs_mb0/rfs_mb0_asymmetry_ladder_transition_energy_result.md
```

Required sections:

```text
1. Executive summary
2. Claim boundary
3. Run shape and artifact policy
4. Asymmetry-family definitions and parameter variants
5. Substrate capacity and coverage
6. Matched marginal detector results by family and variant
7. Response profiles by family and variant
8. Directional asymmetry analysis
9. Preservation asymmetry analysis
10. Combined asymmetry analysis
11. Locality-only baseline analysis
12. Constraint-template comparator analysis
13. Transport viscosity / response diversity atlas
14. Interpretation: which asymmetry ingredients produce which response regimes
15. Next-action fork
16. Output manifest
```

Executive summary must answer:

```text
Which asymmetry families generated interpretable horizon transport?
Which families passed matched marginal nulls?
Which families produced aligned amplification, rerouting, reopening, weakening, or collapse?
Did preservation asymmetry continue to support aligned amplification after terminology and coverage cleanup?
Did directional asymmetry support differentiated response?
Did combined asymmetry produce richer response than E1 or E2 alone?
Did locality-only remain a baseline?
What should run next?
```

## 14. Decision classes

Allowed:

```text
asymmetry_ladder_characterized
locality_only_baseline_confirmed
directional_asymmetry_loadbearing
preservation_asymmetry_loadbearing
combined_asymmetry_loadbearing
combined_asymmetry_not_yet_clean
max_entropy_asymmetry_ready
coverage_repair_required
asymmetry_ladder_underpowered
not_ready_repair_required
```

Forbidden:

```text
Omega_positive
agent_detected
valuer_detected
identity_detected
life_detected
self_replication_detected
candidate_promoted
holdout_ready
```

## 15. Next-action forks

Emit exactly one:

```text
implement_max_entropy_asymmetry_ensemble
expand_preservation_asymmetry_family
expand_directional_asymmetry_family
expand_combined_asymmetry_family
repair_preservation_asymmetry_coverage
repair_directional_asymmetry_resolution
continue_asymmetry_ladder_characterization
write_asymmetry_ladder_theory_note
pause_transition_energy_branch
```

No fork may directly open holdout, graph perturbation, candidate promotion, or Omega/agency/value claims.

## 16. Interpretation guide

### 16.1 E0 locality-only remains baseline

Interpretation:

```text
bounded local branching alone is not the aligned-amplification object.
```

Next:

```text
keep E0 as a null-like baseline.
```

### 16.2 E1 directional asymmetry produces rerouting/reopening

Interpretation:

```text
directional asymmetry supports differentiated response but not necessarily aligned amplification.
```

Next:

```text
sweep alpha and field smoothness more finely;
consider max-entropy directional-field marginal constraints.
```

### 16.3 E2 preservation asymmetry produces aligned amplification

Interpretation:

```text
preservation of coarse asymmetry structure may be the main non-template route to aligned amplification.
```

Next:

```text
repair coverage if needed;
use macro-invariant marginals in max-entropy design.
```

### 16.4 E3 combined asymmetry produces richer response

Interpretation:

```text
direction and preservation are complementary asymmetry ingredients.
```

Next:

```text
expand combined grid;
map response thresholds in alpha/beta space.
```

### 16.5 E3 does not outperform E1/E2

Interpretation:

```text
combined asymmetry may be underpowered, badly parameterized, or genuinely not synergistic in this substrate shape.
```

Next:

```text
narrow parameter grid;
inspect coverage and response thresholds before abandoning combined family.
```

## 17. 3P check

### Principled

The run directly maps the primitive asymmetry question into transition energy: direction, preservation, and their combination.

### Parsimonious

The run uses one instrument, one matched-null suite, and four minimal substrate families without adding semantic labels.

### Predictive

The expected tendencies are preregistered:

```text
E0:
  baseline / stable / possible reopening

E1:
  directional rerouting or threshold shifts

E2:
  aligned amplification / high-viscosity transport

E3:
  richer response surface if direction and preservation are complementary
```

## 18. Bottom line

This run should answer:

```text
Which minimal asymmetry ingredient produces which horizon-transport response profile?
```

A successful result earns an asymmetry-ladder theory note and may justify a max-entropy asymmetry ensemble.

It does not earn holdout, graph perturbation, candidate promotion, or Omega claims.

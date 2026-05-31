# RFS-MB0 Transition-Energy Substrate Characterization Run Spec

Status: larger design-set substrate-characterization spec  
Builds on: `docs/research_notes/validation_results/rfs_mb0_substrate_untethering_transition_energy_sweep_result.md` and `docs/RFS_MB0_SUBSTRATE_UNTETHERING_TRANSITION_ENERGY_SWEEP_SPEC.md`  
Claim boundary: no holdout scoring, no candidate promotion, no Omega detection, no agency detection, no identity detection, no valuer detection

## 0. One-sentence purpose

Run a larger transition-energy substrate characterization pass that lets each substrate family show its own horizon-transport response profile, rather than treating cross-family differences as noise or trying to force convergence.

Plainly:

```text
The question is no longer whether every substrate family behaves the same.
The question is what each substrate law can express under the same horizon-transport instrument.
```

## 1. Why this run exists

The powered substrate-untethering smoke produced an important instrument result:

```text
decision:
  horizon_transport_generalizes_beyond_constraint_vocabulary

next_action:
  continue_transition_energy_substrates
```

It showed that horizon transport remains measurable beyond the original hand-built modular/equality/difference constraint templates.

It also showed that substrate families differ meaningfully:

```text
budget_conservation:
  strongest aligned-amplification fraction;
  high-viscosity aligned-amplifier read;
  but weaker matched/interpretable context coverage in the larger smoke.

smooth_random_potential:
  nonzero aligned amplification;
  mostly rerouted / unresolved response profile;
  promising but needs parameter sweep.

locality_only:
  no aligned amplification in the smoke;
  leaned toward reopening;
  useful baseline showing locality alone is not equivalent to all structure.

constraint_template_current:
  still useful comparator;
  no longer the only substrate where aligned amplification appears.
```

The larger characterization run should now treat these differences as the object of study.

## 2. Claim boundary

Allowed claims:

```text
transition-energy substrate families produce different horizon-transport response profiles;
budget / smooth-potential / locality-only families are more or less generative under the current instrument;
matched marginal detector-null separation does or does not hold by substrate family;
response diversity, viscosity, and horizon thresholds differ by substrate family;
which substrate families deserve further scaling or repair.
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

## 3. Core posture

Do not require substrate families to converge.

Do not penalize a family for having a different response mode if matched-null and coverage gates remain interpretable.

A good run may show:

```text
budget_conservation:
  stable / amplified-aligned / high-viscosity profile

smooth_random_potential:
  rerouted or mixed profile

locality_only:
  reopening / diffusion-like baseline

constraint_template_current:
  comparator response profile
```

The goal is a substrate-response atlas, not one universal response curve.

## 4. Substrate families

Required families:

```text
constraint_template_current
locality_only
smooth_random_potential
budget_conservation
```

Optional if already implemented cleanly:

```text
smooth_random_potential_high_smoothness
smooth_random_potential_low_smoothness
budget_conservation_histogram
budget_conservation_total_mass
budget_conservation_hamming_weight
```

Do not implement max-entropy in this run unless the four required families remain clean and the run finishes very early.

Max-entropy is the next substrate target, but this run should characterize E0/E1/E2 first.

## 5. Substrate-family parameters

### 5.1 Locality-only

Purpose:

```text
baseline for bounded local branching without extra lawlike structure.
```

Required sweeps:

```text
roughness_strength: low, current, high
out_degree_target: current comparator
update_footprint: current comparator
```

Decision interest:

```text
Does locality-only remain reopen/diffuse, or can it produce aligned amplification under changed roughness?
```

### 5.2 Smooth random potential

Purpose:

```text
test whether generic smooth landscape structure is sufficient for aligned amplification or richer response.
```

Required sweeps:

```text
potential_smoothness: low, medium, high
potential_scale / beta: low, medium, high
roughness_strength: current comparator
```

Required diagnostics:

```text
potential_neighbor_correlation
potential_gradient_distribution
potential_delta_distribution
response_by_potential_smoothness
response_by_beta
```

Decision interest:

```text
Does aligned amplification depend on smoothness or potential strength?
Does rerouting become stable under higher/lower smoothness?
```

### 5.3 Budget / conservation

Purpose:

```text
test whether approximate invariants support high-viscosity aligned amplification.
```

Required sweeps:

```text
budget_kind:
  total_coordinate_mass
  symbol_histogram_distance
  hamming_weight_or_nonzero_count, if meaningful for alphabet

budget_weight / lambda:
  low, medium, high
```

Required diagnostics:

```text
budget_delta_distribution
budget_violation_distribution
frontier_support_by_budget_kind
matched_interpretable_contexts_by_budget_kind
aligned_amplification_by_budget_kind
```

Decision interest:

```text
Does budget-conservation remain the strongest aligned-amplification family after coverage repair?
Which invariant, if any, is loadbearing?
```

### 5.4 Constraint-template comparator

Purpose:

```text
baseline comparator only; not the target substrate family.
```

Do not add new hand-built constraint templates.

## 6. Run shape

This should be larger than the powered smoke but still design-set only.

Suggested baseline:

```text
substrate_families: 4 required families
family_parameter_variants: 1 to 9 per family depending on implementation
families prioritized:
  budget_conservation
  smooth_random_potential
  locality_only
  constraint_template_current comparator

groups_per_family_variant: 24 to 48
design_groups_per_family_variant: 8 to 16
fresh_seeds_per_group: 6
start_samples_list: 2,4,8,16
null_replicates: 13 or 15
workers: machine appropriate
max_runtime_seconds: 28800
shutdown_cushion_seconds: 1800
```

If compute is limited, prioritize:

```text
1. budget_conservation coverage repair and budget-kind sweep
2. smooth_random_potential beta/smoothness sweep
3. locality_only baseline repeat
4. constraint_template comparator repeat
```

## 7. Horizon pairs

Use H128-compatible horizon pairs first.

Required:

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

Optional if coverage is strong across families:

```text
128->256
256->512
```

Do not run H1280 here unless E0/E1/E2 coverage is already stable. The next goal is substrate characterization, not horizon extension.

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

Do not use constraint-template-specific probes to compare grammar-neutral substrate families.

Required flow modes:

```text
constrained_window_flow
one_step_local_flow
```

If naming becomes misleading for untethered substrates, report them as:

```text
window_transport_flow
one_step_transport_flow
```

while retaining backward-compatible aliases.

## 10. Required detector and response gates

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
transport_resolution_mismatch
transport_response_underpowered
```

Required fixture contract:

```text
8 / 8 response fixtures must pass before empirical response classes support interpretation.
```

## 11. Coverage and interpretability requirements

The prior powered smoke showed lower matched/interpretable contexts for budget_conservation.

This run must report by substrate family:

```text
matched_interpretable_context_fraction
matrix_coverage_min
undercoverage_fraction_by_horizon
normal_interpretation_fraction_by_horizon
frontier_source_state_count_mean
frontier_target_state_count_mean
row_support_mean
column_support_mean
transport_entropy_mean
largest_entry_mass_share_mean
```

Do not rank a substrate family as strongest based only on aligned amplification if it is undercovered.

Use a two-axis read:

```text
response strength
coverage / interpretability
```

## 12. Required outputs

Core:

```text
transition_energy_characterization_run_config.json
transition_energy_characterization_status.json
transition_energy_characterization_progress_checkpoints.csv
transition_energy_characterization_errors.csv
transition_energy_characterization_output_manifest.json
```

Substrate:

```text
substrate_family_manifest.csv
transition_energy_parameter_summary.csv
substrate_generation_diagnostics.csv
substrate_capacity_by_family.csv
substrate_capacity_by_family_variant.csv
```

Detector:

```text
horizon_transport_matrix_manifest.csv
horizon_transport_coverage.csv
horizon_transport_detector_null_gate_results.csv
horizon_transport_matched_marginal_summary.csv
matched_null_pass_by_substrate_family.csv
matched_null_pass_by_substrate_family_variant.csv
```

Response:

```text
horizon_transport_response_classification.csv
response_by_substrate_family.csv
response_by_substrate_family_variant.csv
response_by_budget_kind.csv
response_by_potential_smoothness.csv
response_by_potential_beta.csv
response_class_by_strength_and_horizon_pair.csv
horizon_response_threshold_table.csv
```

Viscosity/diversity:

```text
transport_viscosity_by_substrate_family.csv
transport_viscosity_by_substrate_family_variant.csv
response_diversity_by_substrate_family.csv
response_diversity_by_substrate_family_variant.csv
```

Final report:

```text
rfs_mb0_transition_energy_substrate_characterization_result.md
```

## 13. Final report requirements

Retain under:

```text
docs/research_notes/validation_results/rfs_mb0_transition_energy_substrate_characterization_result.md
```

Required sections:

```text
1. Executive summary
2. Claim boundary
3. Run shape and artifact policy
4. Substrate family definitions and parameter variants
5. Substrate capacity and coverage
6. Matched marginal detector results by family and variant
7. Response profiles by family and variant
8. Budget-conservation analysis
9. Smooth-potential analysis
10. Locality-only baseline analysis
11. Constraint-template comparator analysis
12. Transport viscosity / response diversity atlas
13. Interpretation: what each substrate law can express
14. Next-action fork
15. Output manifest
```

Executive summary must answer:

```text
Which substrate families generated interpretable horizon transport?
Which families passed matched marginal nulls?
Which families produced aligned amplification, rerouting, reopening, weakening, or collapse?
Did budget-conservation remain strongest after coverage repair?
Did smooth-potential become more interpretable under parameter sweeps?
Did locality-only remain a baseline or become response-bearing?
What should run next?
```

## 14. Decision classes

Allowed:

```text
transition_energy_substrates_characterized
budget_conservation_loadbearing
smooth_potential_loadbearing
locality_only_baseline_confirmed
locality_only_response_bearing
constraint_template_no_longer_primary
max_entropy_transition_ready
substrate_characterization_underpowered
coverage_repair_required
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
implement_max_entropy_local_transition
expand_budget_conservation_family
expand_smooth_potential_family
repair_budget_coverage
repair_smooth_potential_resolution
continue_transition_energy_characterization
write_transition_energy_substrate_atlas_note
pause_substrate_untethering
```

No fork may directly open holdout, graph perturbation, candidate promotion, or Omega/agency/value claims.

## 16. Interpretation guide

### 16.1 Budget-conservation remains strong and covered

Interpretation:

```text
approximate invariants may be a productive generic lawlike ingredient.
```

Next:

```text
expand budget kinds and weights;
consider max-entropy ensemble with budget marginal constraints.
```

### 16.2 Smooth potential becomes strong under parameter sweep

Interpretation:

```text
generic landscape structure may be sufficient for aligned amplification or response diversity.
```

Next:

```text
sweep potential smoothness / beta more finely;
consider max-entropy ensemble with energy marginal constraints.
```

### 16.3 Locality-only remains reopen/diffuse

Interpretation:

```text
bounded local branching alone is not the same object;
additional lawlike structure is loadbearing.
```

Next:

```text
keep locality-only as null baseline.
```

### 16.4 All transition-energy families remain interpretable but different

Interpretation:

```text
the instrument is useful as a substrate-response atlas;
substrate differences are signal, not noise.
```

Next:

```text
write transition-energy substrate atlas note;
move toward max-entropy local transition ensemble.
```

## 17. 3P check

### Principled

The run studies generic transition-law families expressed through explicit transition energy, locality, potential, budget, and roughness.

### Parsimonious

The run keeps the same horizon-transport instrument and matched-null suite while varying substrate law families.

### Predictive

Each substrate family should show a distinctive, measurable response profile if the instrument is working and substrate law matters.

## 18. Bottom line

This run should answer:

```text
What can each transition-energy substrate family express under the same horizon-transport instrument?
```

A successful result earns a transition-energy substrate atlas and possibly a max-entropy local transition ensemble.

It does not earn holdout, graph perturbation, candidate promotion, or Omega claims.

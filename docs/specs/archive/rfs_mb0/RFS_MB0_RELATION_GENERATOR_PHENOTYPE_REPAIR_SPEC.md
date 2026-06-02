# RFS-MB0 Relation Generator Phenotype Repair Spec

Status: Codex implementation/run handoff after candidate phenotype audit sanity result

Purpose: preserve the current action-generated relation generator, repair phenotype interpretation, and run a focused diagnostic pass before deciding whether to scale or pivot.

This is not a substrate replacement. The relation generator currently looks promising enough to keep.

## 0. Current read

The candidate phenotype audit sanity run was useful because it exposed a diagnostic mismatch rather than merely producing another zero-gate result.

Observed:

```text
start_samples = 1, 3, 8 all completed
candidate phenotype rows = 41
most candidates were basin-local or environment-level across start-sample settings
all phenotype rows were labeled roughness_brittle_artifact
score decomposition was constraint-dominated, not roughness-dominated
roughness_decisive_edge_fraction was modest, not dominant
```

Interpretation:

```text
The relation generator appears to produce recurring candidate-window phenotypes.
The current roughness phenotype label is too blunt.
The generator is constraint-dominated and deserves a finer audit.
Do not pivot away from the generator yet.
```

## 1. Core correction

Do not treat roughness-resampled failure as proof of roughness artifact.

Current classifier behavior is too aggressive:

```text
roughness_resampled control failed
  -> roughness_brittle
  -> roughness_brittle_artifact
```

Replace this with a layered interpretation:

```text
roughness_resample_sensitive:
  candidate phenotype changes/fails under roughness resampling

roughness_edge_brittle:
  roughness changes selected top-k edges or near-cutoff edge ordering enough to alter future profile

roughness_artifact:
  candidate is roughness-sensitive, edge/near-cutoff roughness decisive, and does not recur across roughness seeds/strengths

symmetry_breaking_stable:
  candidate needs nonzero roughness but phenotype class recurs across roughness seeds

noise_tolerant:
  candidate persists under small roughness perturbations or degrades smoothly
```

The old label `roughness_brittle_artifact` should be deprecated or reserved only for confirmed roughness artifacts.

## 2. Keep multiple starts mandatory

Multiple starts are now the first non-destructive sanity check.

Required for all candidate runs:

```text
start_samples = 1, 3, 8
```

Optional if cheap:

```text
start_samples = 16
```

Every candidate must report:

```text
start_coverage_class
```

Allowed classes:

```text
start_local
basin_local
environment_level
start_fragile
start_diverse
```

Do not promote or heavily interpret candidates without start coverage.

## 3. Roughness diagnostic repair

Add an explicit roughness module with four components.

### 3.1 Roughness-off replay

For selected environments, rebuild the relation graph with:

```text
roughness_strength = 0.0
```

Compare:

```text
edge set overlap
candidate phenotype overlap
future-profile similarity
window class changes
```

### 3.2 Same-strength roughness reseeding

For the baseline roughness strength, rerun with multiple roughness seeds:

```text
roughness_strength = baseline, usually 0.01
roughness_seed_replicates = 5 if cheap, minimum 3
```

### 3.3 Roughness strength sweep

Required values:

```text
roughness_strength = 0.0, 0.001, 0.003, 0.01, 0.03, 0.05
```

Optional if cheap:

```text
0.10
```

### 3.4 Edge-selection flip analysis

For each roughness perturbation, report:

```text
selected_edge_overlap_vs_baseline
near_cutoff_rank_flip_rate
top_k_boundary_flip_rate
roughness_decisive_selected_edge_fraction
roughness_decisive_near_cutoff_fraction
frontier_similarity_by_H
path_signature_similarity_by_H if available
phenotype_similarity_to_baseline
```

Important: selected-edge roughness decisiveness alone is insufficient. The previous sanity run showed the need to inspect near-cutoff and downstream frontier effects.

## 4. Constraint/score audit repair

Constraint is the main structure-generating mechanism. Audit it directly.

### 4.1 Score decomposition expansion

Current score decomposition sampled selected edges. Expand to include:

```text
selected top-k edges
near-cutoff candidates, e.g. ranks k-2 through k+5
random nonselected candidates
```

Required output:

```text
score_term_decomposition.csv
```

Required columns:

```text
environment_id
parameter_set_id
source_state
target_state
selected_edge
candidate_rank
rank_band

total_score
change_term
constraint_violation_term
constraint_change_term
asymmetry_term
roughness_term

score_margin_to_next
score_margin_to_cutoff
near_tie_flag
roughness_decisive_flag
roughness_decisive_if_resampled_flag
```

### 4.2 Top-k margin diagnostics

Required output:

```text
top_k_margin_summary.csv
```

Columns:

```text
environment_id
parameter_set_id
mean_margin_to_cutoff
median_margin_to_cutoff
q10_margin_to_cutoff
near_tie_rate
near_cutoff_density
roughness_decisive_selected_edge_fraction
roughness_decisive_near_cutoff_fraction
```

### 4.3 Constraint profile diagnostics

Required outputs:

```text
constraint_profile_summary.csv
constraint_scope_overlap_summary.csv
constraint_conflict_summary.csv
constraint_vs_asymmetry_dominance.csv
```

Required diagnostics:

```text
constraint_satisfaction_distribution
constraint_violation_histogram
constraint_profile_entropy
constraint_profile_transition_rate
constraint_conflict_proxy_rate
constraint_scope_overlap_degree
constraint_scope_component_count
constraint_type_mix
mean_constraint_violation_term
mean_constraint_change_term
constraint_term_dominance
asymmetry_term_dominance
roughness_term_dominance
constraint_vs_asymmetry_ratio
```

## 5. Candidate phenotype table repair

Replace the current single harsh phenotype class with a phenotype vector.

Required output:

```text
candidate_phenotype_summary.csv
```

Required fields:

```text
candidate_id
environment_id
parameter_set_id
start_samples
start_coverage_class
window_name
probe_family
horizon_range

triviality_frontier_size_result
triviality_probe_marginal_result
triviality_frontier_plus_probe_result
support_matched_result

constraint_dependency_class
asymmetry_dependency_class
roughness_response_class
roughness_edge_sensitivity_class
roughness_strength_profile_class
start_coverage_class
path_process_class

degree_outdegree_ablation_result
mechanistic_ablation_profile
triviality_profile
support_profile
process_profile

near_tie_dominated_flag
roughness_resample_sensitive_flag
roughness_artifact_flag
symmetry_breaking_stable_flag
noise_tolerant_flag
lockin_prone_flag
shuffle_survivor_audit_required

phenotype_class
phenotype_confidence
recommended_followup
```

### 5.1 Phenotype class examples

Use classes such as:

```text
constraint_dominated_roughness_sensitive
constraint_dependent_environment_level
constraint_dependent_basin_local
support_deformation_environment_level
mixed_support_deformation_basin_local
transition_process_candidate_environment_level
roughness_symmetry_breaking_candidate
roughness_edge_brittle_candidate
confirmed_roughness_artifact
generic_branching_artifact
probe_artifact
start_local_candidate
underdetermined
```

Do not classify all roughness-resample failures as roughness artifacts.

## 6. Corrected control interpretation

The final summary must separate controls into categories.

### 6.1 Triviality controls

```text
frontier_size_only
probe_marginal_only
frontier_size_plus_probe_marginal
```

These test low-level endpoint/probe explanations.

### 6.2 Support controls

```text
signature_support_matched
horizon_local_frontier_matched
window_local_frontier_matched
```

Failing these can mean support-level deformation, not automatic rejection.

### 6.3 Mechanistic ablations

```text
constraint_shuffled
asymmetry_shuffled
```

These test dependence on the substrate-generating mechanisms. Meaningful candidates may be expected to fail them.

### 6.4 Strong relation/graph ablations

```text
current degree_preserving_rewire
out_degree_preserving_random
```

Current `degree_preserving_rewire` should be renamed in outputs as:

```text
out_degree_rewire_without_replacement
```

until a true directed degree-sequence-preserving null exists.

These are destructive ablations, not must-survive robustness gates.

### 6.5 Robustness perturbations

```text
roughness sweep
small edge deletion/rewiring if implemented
start perturbation
```

These should be graded and phenotyped.

## 7. Path/process diagnostics

If tractable in this pass, add path/process summaries for selected candidate environments.

Minimum:

```text
signature_bigram_counts
signature_bigram_entropy
signature_bigram_motif_reuse
```

Preferred:

```text
signature_trigram_counts
path_ngram_entropy
path_language_growth_rate
path_sequence_compression_proxy
forbidden_word_count
```

Add process nulls if cheap:

```text
endpoint_support_matched_path_randomized
transition_support_matched_probability_shuffled
bigram_support_matched_trigram_test
```

Candidate path classes:

```text
support_only
distribution_deformation
transition_process_candidate
path_process_candidate
robust_path_candidate
```

## 8. Reproducibility target

Do not require exact candidate recurrence.

Track phenotype-level recurrence.

Required output:

```text
phenotype_reproducibility_summary.csv
```

Group by:

```text
parameter_region_id
exact_parameter_set
start_coverage_class
probe_family
window_name
roughness_profile_class
phenotype_class
```

Report:

```text
phenotype_recurrence_rate_across_environment_seeds
phenotype_recurrence_rate_across_starts
phenotype_recurrence_rate_across_probe_families
phenotype_recurrence_rate_across_roughness_seeds
phenotype_recurrence_rate_across_roughness_strengths
```

## 9. Suggested run shape

This should be a focused diagnostic, not broad atlas scale.

Suggested:

```text
workers: 18
wall clock: 2-4 hours
coordinate_count: 5
selected parameter regions: from ranked null-repair and sanity audit
parameter_samples: 8-20
seeds_per_parameter_set: 1-2
start_samples_list: 1,3,8
null_replicates: 3-5
roughness_strengths: 0,0.001,0.003,0.01,0.03,0.05
roughness_seed_replicates: 3
score_edge_sample: at least 500, including near-cutoff candidates
stress_sample_count: 80-160
horizon_grid: long_5x or long_10x
```

If runtime is tight, priority order:

```text
1. roughness label repair
2. start-sample sweep
3. roughness-off and roughness-reseed replay
4. near-cutoff score decomposition
5. candidate phenotype vector
6. constraint profile audit
7. phenotype reproducibility summary
8. path/process diagnostics
```

## 10. Final report requirements

Write:

```text
rfs_mb0_relation_generator_phenotype_repair_result.md
```

Must answer:

```text
Does the relation generator still look worth keeping?
Are candidates mostly start-local, basin-local, or environment-level?
Is roughness sensitivity edge-level, near-cutoff, frontier-level, null-rank-level, or phenotype-level?
Are candidates roughness artifacts, symmetry-breaking candidates, or noise-tolerant candidates?
Is the generator constraint-dominated, asymmetry-dominated, or near-tie dominated?
Does constraint dominance produce conflicted but structured corridors or lock-in?
Which phenotype classes recur across starts/seeds/probes/roughness settings?
Do any candidates show path/process structure beyond support deformation?
What should the next pivot be, if any?
```

## 11. Claim boundary

Allowed:

```text
The relation generator produced recurring candidate-window phenotypes under diagnostic audit.
The roughness artifact label was repaired/refined.
We identified whether candidates are start-local, roughness-sensitive, constraint-dominated, or path/process-like.
```

Not allowed unless separately earned:

```text
Omega detected
agency detected
identity detected
valuer detected
viability detected
scientific gate passed
```

## 12. Bottom line

The current relation generator looks good enough to keep.

The next pass should repair the candidate phenotype machinery around it:

```text
multiple starts first
roughness as graded sensitivity
constraint/score audit
near-cutoff edge analysis
phenotype-level reproducibility
path/process diagnostics
```

Only after this should we decide whether to scale, tune generator parameters, or pivot the substrate.

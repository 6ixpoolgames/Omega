# RFS-MB0 Relation Atlas Candidate Phenotype Audit Spec

Status: Codex implementation/run handoff

Purpose: run one disciplined diagnostic pass using the current action-generated relation generator before deciding whether to pivot. This pass incorporates the interpretation corrections discussed after the ranked null-repair result.

This is not a detector-threshold tuning pass and not a new substrate pivot.

## 0. Current read

The action-generated relation generator looks plausible enough to keep for now.

The ranked null-repair run did not pass the scientific gate, but it usefully exposed several interpretation problems:

```text
nulls/controls were being collapsed into one survival table
constraint/asymmetry shuffles were being treated too much like must-survive nulls
roughness was treated as binary resampling instead of a noise/symmetry-breaking profile
start_samples=1 made candidate locality hard to interpret
endpoint/support controls were mixed with process/transition controls
degree_preserving_rewire is currently not a true directed degree-sequence preserving null
```

The next run should determine whether the observed local/window candidates are:

```text
start-local artifacts
roughness/tie-break artifacts
support-only deformation
path/process deformation
constraint/asymmetry-dependent structure
generic branching artifacts
reproducible phenotype classes
```

not whether they survive destructive removal of the mechanisms that generated them.

## 1. Core principle

Do not ask:

```text
Can candidates survive having relation/asymmetry/constraint geometry destroyed?
```

Ask:

```text
What kind of future-landscape deformation is this candidate,
what trivial explanations does it evade,
what mechanisms does it depend on,
and does the phenotype recur across starts/seeds/probes/roughness settings?
```

## 2. Corrected control taxonomy

The output must separate controls into categories.

### 2.1 Triviality controls

These test whether a candidate is explainable by low-level endpoint/probe facts.

```text
frontier_size_only
probe_marginal_only
frontier_size_plus_probe_marginal
```

Candidates should generally survive these for stronger claims.

`probe_marginal_only` is a cheap sanity filter. It may often be too easy and should not dominate interpretation.

### 2.2 Support-level controls

These test whether the signal is primarily about which signatures/futures become reachable.

```text
signature_support_matched
horizon_local_frontier_matched
window_local_frontier_matched
```

Failing these should produce a phenotype such as:

```text
support_deformation_candidate
```

not immediate rejection.

### 2.3 Mechanistic ablations

These disrupt substrate-generating mechanisms.

```text
constraint_shuffled
asymmetry_shuffled
```

These are not must-survive nulls. They answer:

```text
Does the candidate depend on specific local constraint/asymmetry geometry?
```

Expected meaningful candidates may die under these ablations.

If a candidate survives them, flag:

```text
shuffle_survivor_audit_required
```

because it may be trivial graph/probe structure or an unexpectedly generic phenomenon.

### 2.4 Strong graph/relation ablations

Current:

```text
degree_preserving_rewire
out_degree_preserving_random
```

Important naming correction:

Current `degree_preserving_rewire` appears to preserve outgoing target count, not the full directed in/out degree sequence. Treat it as:

```text
out_degree_rewire_without_replacement
```

until a true directed degree-sequence preserving null is implemented.

These are destructive relation ablations. They are useful for detecting generic branching artifacts, but should not be interpreted as must-survive gates for relation-specific candidates.

### 2.5 Robustness perturbations

These should be graded, not binary.

Required:

```text
roughness_strength_sweep
roughness_seed_replicates
start_sample_sensitivity
```

Optional if cheap:

```text
small edge deletion
small edge rewiring
constraint weight perturbation
asymmetry strength perturbation
```

## 3. Multiple starts are mandatory

Before destructive nulls, the first sanity layer is start sensitivity.

Run at minimum:

```text
start_samples = 1
start_samples = 3
start_samples = 8
```

If state count is small enough, optionally run:

```text
start_samples = 16
```

A candidate must be typed by start coverage:

```text
start_local
basin_local
environment_level
start_fragile
start_diverse
```

Definitions:

```text
start_local:
  appears for only one/few starts

basin_local:
  appears for a coherent subset of starts

environment_level:
  appears across many starts

start_fragile:
  disappears when start_samples increases

start_diverse:
  different starts produce different but related phenotype classes
```

Do not promote a candidate without reporting its start phenotype.

## 4. Roughness audit

Roughness is currently a small seeded score perturbation. It may expose fragility in the generator.

Do not treat roughness as one binary shuffle.

Implement a sweep:

```text
roughness_strength: 0.0, 0.001, 0.003, 0.01, 0.03, 0.05
roughness_seed_replicates: at least 3 per strength, 5 if cheap
```

For each candidate phenotype, report:

```text
roughness_strength
roughness_seed
candidate_class
candidate_recurrence_rate
phenotype_similarity_to_baseline
support_deformation_score
transition_deformation_score
path_deformation_score
start_coverage
degradation_slope
collapse_or_lockin_flag
```

Classify roughness response:

```text
roughness_independent
symmetry_breaking_stable
noise_tolerant
noise_sensitive_smooth
roughness_brittle
lockin_prone
```

Interpretation:

```text
roughness_brittle:
  candidate appears only for one exact roughness seed or vanishes under tiny resampling

symmetry_breaking_stable:
  candidate needs nonzero roughness, but same signal class recurs across roughness seeds

noise_tolerant:
  candidate persists across small roughness and degrades gradually

lockin_prone:
  small roughness pushes futures into narrow unrecoverable corridors
```

## 5. Constraint audit

Constraint is the load-bearing structure-generating mechanism. Audit it directly.

For every selected environment/candidate and for a sampled set of ordinary edges, write score-term decompositions.

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
```

Definitions:

```text
constraint_violation_term:
  penalty for target state violating generated local constraints

constraint_change_term:
  penalty for transition changing the vector of constraint satisfaction/violation statuses

roughness_decisive_flag:
  edge selection would change if roughness were set to zero or resampled at same strength
```

Also write:

```text
constraint_profile_summary.csv
constraint_scope_overlap_summary.csv
top_k_margin_summary.csv
roughness_decisive_edges.csv
constraint_vs_asymmetry_dominance.csv
```

Required diagnostics:

```text
constraint_satisfaction_distribution
constraint_violation_histogram
constraint_profile_entropy
constraint_profile_transition_rate
constraint_conflict_rate
constraint_scope_overlap_graph_summary
constraint_component_count
constraint_term_dominance
asymmetry_term_dominance
roughness_term_dominance
top_k_margin_distribution
near_tie_rate
roughness_decisive_edge_fraction
```

## 6. Constraint parameter mini-sweep

Do not pivot the generator yet. Run a small targeted sweep around load-bearing constraint parameters.

Required sweep dimensions:

```text
constraint_strength: 0.25, 0.5, 1.0, 2.0, 4.0
constraint_change_weight: 0.0, 0.1, 0.35, 0.75, 1.5
constraint_density: keep existing values plus focused middle-regime values if already identified
constraint_arity: 2, 3
```

Optional if cheap:

```text
constraint_type_mix:
  mixed
  modular_only
  equality_only
  difference_only
```

Classify generator regimes:

```text
underconstrained_mixing
overconstrained_lockin
smooth_corridor
jumping_between_compatible_states
recoverable_branching
roughness_decisive
asymmetry_dominated
constraint_dominated
```

## 7. Asymmetry audit

Asymmetry is primitive, so do not treat asymmetry shuffle as a must-survive null.

Add asymmetry-strength sensitivity:

```text
asymmetry_strength: 0.0, 0.125, 0.25, 0.5, 0.75
```

Report:

```text
asymmetry_vs_constraint_ratio
asymmetry_lockin_score
reachability_imbalance_by_start
future_entropy_gradient_by_edge
recovery_window_proxy
```

Where:

```text
recovery_window_proxy:
  whether nearby starts or small perturbations reconverge to related future-profile phenotypes
```

## 8. Path/process diagnostics

Endpoint/support deformation is not enough. Add path-level diagnostics for candidate windows.

Required if tractable:

```text
signature_bigram_counts
signature_trigram_counts
path_ngram_entropy
path_motif_reuse
path_language_growth_rate
path_sequence_compression_proxy
forbidden_word_count
```

Add process nulls:

```text
endpoint_support_matched_path_randomized
transition_support_matched_probability_shuffled
bigram_support_matched_trigram_test
frontier_size_matched_path_language_randomized
```

Report candidate levels:

```text
support_deformation_candidate
distribution_deformation_candidate
transition_process_candidate
path_process_candidate
robust_path_candidate
```

Do not require path-process signal for all candidates; use it to phenotype them.

## 9. Candidate phenotype vector

Every candidate should get a row in:

```text
candidate_phenotype_summary.csv
```

Required columns:

```text
candidate_id
environment_id
parameter_set_id
start_id
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
start_coverage_class
path_process_class

degree_outdegree_ablation_result
shuffle_survivor_audit_required
roughness_brittle_flag
near_tie_dominated_flag
lockin_prone_flag

phenotype_class
phenotype_confidence
recommended_followup
```

Candidate phenotype classes may include:

```text
support_only_start_local
distribution_deformation_start_local
constraint_dependent_basin_local
asymmetry_dependent_basin_local
roughness_brittle_artifact
roughness_symmetry_breaking_candidate
path_process_candidate
recoverable_branching_candidate
generic_branching_artifact
probe_artifact
shuffle_survivor_audit_required
underdetermined
```

## 10. Reproducibility target

Do not require exact candidate recurrence.

Require phenotype-level recurrence.

For each parameter regime, report:

```text
phenotype_class_distribution
phenotype_recurrence_rate_across_environment_seeds
phenotype_recurrence_rate_across_starts
phenotype_recurrence_rate_across_probe_families
roughness_response_distribution
path_process_distribution
```

Required output:

```text
phenotype_reproducibility_summary.csv
```

A useful pattern is:

```text
same parameter region repeatedly produces similar phenotype distributions,
even if exact starts/windows/probes differ.
```

## 11. Suggested run shape

This should be a diagnostic pass, not an overnight scale-up.

Suggested:

```text
workers: 18
wall clock: 2-4 hours
n: 5 only for main diagnostic
selected parameter regions: from ranked null-repair run
start_samples: 1, 3, 8
null_replicates: 5
roughness_strength sweep: 0, 0.001, 0.003, 0.01, 0.03, 0.05
roughness_seed_replicates: 3
constraint mini-sweep: focused, not full factorial explosion
stress_sample_count: 80-160
```

If runtime is tight, priority order:

```text
1. start_samples sweep
2. score-term decomposition
3. roughness sweep
4. candidate phenotype table
5. path/process diagnostics
6. constraint/asymmetry mini-sweeps
```

## 12. Required final summary

Write:

```text
rfs_mb0_candidate_phenotype_audit_result.md
```

Must answer:

```text
Are candidates start-local, basin-local, or environment-level?
Are candidates roughness-brittle or noise-tolerant?
How often is roughness decisive in edge selection?
Are top-k margins large or tiny?
Is the generator constraint-dominated, asymmetry-dominated, or near-tie dominated?
Do candidates show only support deformation or path/process deformation?
Which phenotypes recur across parameter regimes?
Which controls indicate triviality versus mechanism dependence?
Should the relation generator be kept, repaired, or pivoted away from?
```

## 13. Claim boundary

Allowed:

```text
We ran a candidate phenotype audit of the action-generated relation atlas.
We classified candidates by start coverage, roughness response, constraint/asymmetry dependence, and path/process evidence.
```

Not allowed unless separately earned:

```text
Omega detected
valuer detected
agent detected
identity detected
viability detected
scientific gate passed
```

## 14. Bottom line

This run should tell us whether the relation generator is producing:

```text
robust future-landscape deformation phenotypes
```

or merely:

```text
start-local, roughness-sensitive, near-tie artifacts.
```

Only after this audit should we decide whether to pivot the relation generator, repair its scoring terms, or scale the atlas.

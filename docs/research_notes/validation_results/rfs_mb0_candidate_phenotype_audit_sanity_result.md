# RFS-MB0 Candidate Phenotype Audit Sanity Result

Date: 2026-05-25

Spec:

```text
docs/RFS_MB0_RELATION_ATLAS_CANDIDATE_PHENOTYPE_AUDIT_SPEC.md
```

Local output:

```text
results/rfs_mb0_relation_atlas/20260525_candidate_phenotype_audit_sanity/
```

## Purpose

This was a tiny technical audit/probe, not a validation run. The aim was to check whether the action-generated relation atlas can expose enough internal structure to phenotype candidate windows before deciding whether to pivot or scale.

The sub-1h priority order was:

1. start-sample sensitivity;
2. score-term decomposition;
3. candidate phenotype table;
4. minimal reproducibility summary.

Full roughness-strength sweeps, path language diagnostics, and constraint/asymmetry mini-sweeps were deferred.

## Implementation

Added:

```text
omega/rfs_mb0_future_landscape/run_candidate_phenotype_audit.py
```

The audit runner performs small `run_relation_atlas` passes at multiple `start_samples` values, then writes:

```text
candidate_phenotype_summary.csv
phenotype_reproducibility_summary.csv
score_term_decomposition.csv
top_k_margin_summary.csv
roughness_decisive_edges.csv
constraint_profile_summary.csv
constraint_scope_overlap_summary.csv
constraint_vs_asymmetry_dominance.csv
summary.md
status.json
```

## Run Shape

```text
workers: 18
parameter_samples per start pass: 4
start_samples: 1, 3, 8
null_replicates: 1
wall-clock budget: 3300 seconds
wall-clock used: about 985 seconds
```

All three start-sample stages completed:

```text
start_samples=1: 4/4 jobs, 4 middle-regime, 0 gate passes
start_samples=3: 4/4 jobs, 4 middle-regime, 0 gate passes
start_samples=8: 4/4 jobs, 4 middle-regime, 0 gate passes
```

Candidate phenotype rows:

```text
41
```

## Start Coverage

```text
environment_level: 33
basin_local: 6
start_fragile: 1
start_local: 1
```

Initial read:

The candidate windows in this small sweep were not mostly start-fragile. Most recurred across the start-sample settings used here.

## Phenotype Classification

Current phenotype table classified:

```text
roughness_brittle_artifact: 41/41
```

But this must be interpreted carefully because score decomposition did not support a simple roughness-dominance story.

Support/path/process summary:

```text
support_deformation: 19
mixed_support_deformation: 14
beyond_support_matched: 8

transition_process_candidate: 32
distribution_deformation_candidate: 9
```

Dependency and ablation summary:

```text
mechanism_dependent on constraint/asymmetry: 41/41
killed_by_out_degree_ablation: 38
mixed_out_degree_ablation: 3
```

## Score-Term Audit

Score decomposition rows:

```text
120
```

Selected edges sampled:

```text
70
```

Top-k margin summary:

```text
near_tie_rate: 0.200
roughness_decisive_edge_fraction: 0.114
mean_score_margin_to_next: 0.358
mean_score_margin_to_cutoff: 0.270
```

Term dominance:

```text
constraint_term_dominance: 1.751
asymmetry_term_dominance: 0.044
roughness_term_dominance: 0.004
dominance_class: constraint_dominated
```

Constraint profile summary:

```text
mean_constraint_violation_term: 1.186
mean_constraint_change_term: 0.565
constraint_conflict_proxy_rate: 0.771
```

## Technical Interpretation

The audit is useful mostly because it exposes a disagreement between diagnostic layers:

```text
candidate phenotype null table: roughness_brittle_artifact
score-term decomposition: constraint-dominated, only ~11% roughness-decisive selected edges
```

This suggests that the current `roughness_resampled` null may be acting as a broad relation-resampling / tie-break perturbation control rather than a clean measure of roughness decisiveness.

The start-sample sweep is more encouraging methodologically:

```text
most candidates were basin-local or environment-level under start_samples 1, 3, 8
```

That does not make them valid, but it reduces concern that the observed windows are only one-start accidents.

## Claim Boundary

This run does not validate Omega, agency, identity, value, or a scientific gate.

Allowed interpretation:

```text
The current relation generator produces recurring candidate-window phenotypes in this tiny audit, but their control taxonomy is unresolved.
```

Not allowed:

```text
scientific gate passed
robust Omega object detected
relation atlas validated
```

## Recommendation

Do not pivot solely on the label `roughness_brittle_artifact`.

Recommended next technical probe:

```text
Split roughness diagnostics into:
1. exact roughness-off replay;
2. same-strength roughness reseeding;
3. small roughness-strength sweep;
4. edge-selection flip rate against top-k margins.
```

The useful immediate target is to determine whether roughness brittleness is real edge-selection fragility or a too-broad null label.

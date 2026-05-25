# RFS-MB0 Relation Generator Phenotype Repair Result

Date: 2026-05-25

Spec:

```text
docs/RFS_MB0_RELATION_GENERATOR_PHENOTYPE_REPAIR_SPEC.md
```

Local output:

```text
results/rfs_mb0_relation_atlas/20260525_relation_generator_phenotype_repair/
```

## Purpose

This was a focused technical audit/probe. It repaired the previous candidate phenotype machinery so roughness-resampled failure no longer automatically becomes `roughness_brittle_artifact`.

The goal was to determine whether the relation generator still looks worth keeping, and whether candidate phenotypes are start-local, roughness artifacts, constraint-dominated structure, or process-like deformation.

## Implementation

Updated:

```text
omega/rfs_mb0_future_landscape/relation_generator.py
omega/rfs_mb0_future_landscape/run_candidate_phenotype_audit.py
```

Key repairs:

- Added explicit roughness replay support via `roughness_seed`.
- Added `roughness_sensitivity_summary.csv`.
- Split roughness into response, edge sensitivity, and strength-profile classes.
- Deprecated the old one-step mapping from roughness-resampled failure to roughness artifact.
- Expanded score-term decomposition around selected, near-cutoff, and tail candidates.
- Added per-environment top-k margin summaries.

## Run Shape

```text
workers requested: 18
parameter_samples per start pass: 8
start_samples: 1, 3, 8
null_replicates: 3
roughness_strengths: 0, 0.001, 0.003, 0.01, 0.03, 0.05
roughness_seed_replicates: 3
score_edge_sample: 500
wall-clock used: about 3396 seconds
```

All start-sample stages completed:

```text
start_samples=1: 8/8 jobs, 8 middle-regime, 0 gate passes
start_samples=3: 8/8 jobs, 8 middle-regime, 0 gate passes
start_samples=8: 8/8 jobs, 8 middle-regime, 0 gate passes
```

Worker-utilization note:

```text
The run requested 18 workers, but each stage only had 8 atlas jobs available.
CPU utilization therefore peaked below full capacity. Future runs should use at
least 18 queued jobs per stage, more seeds, or parallelize roughness replay if
hardware saturation is a goal.
```

## Candidate Phenotypes

Candidate phenotype rows:

```text
88
```

Start coverage:

```text
environment_level: 75
basin_local: 10
start_local: 2
start_fragile: 1
```

Phenotype classes:

```text
constraint_dominated_roughness_sensitive: 62
roughness_edge_brittle_candidate: 25
confirmed_roughness_artifact: 1
```

Roughness edge sensitivity:

```text
roughness_edge_stable: 62
roughness_edge_sensitive: 16
roughness_edge_brittle: 10
```

Roughness strength profile:

```text
noise_tolerant: 69
noise_sensitive_smooth: 9
roughness_strength_brittle: 10
```

This is a substantial correction from the previous audit, where all rows were labeled `roughness_brittle_artifact`.

## Roughness Read

The repaired interpretation is:

```text
roughness-resampled null sensitivity is common,
but confirmed roughness artifact is rare in this pass.
```

Most candidate rows are better described as:

```text
constraint-dominated, roughness-sensitive, but edge-stable/noise-tolerant
```

This means the old roughness label was too broad. It was conflating null-rank sensitivity with actual roughness-driven edge selection.

## Constraint and Score Audit

Score/term dominance:

```text
constraint_term_dominance: 2.739
asymmetry_term_dominance: 0.056
roughness_term_dominance: 0.005
dominance_class: constraint_dominated
```

Constraint profile:

```text
selected edges sampled: 161
mean_constraint_violation_term: 2.189
mean_constraint_change_term: 0.550
constraint_conflict_proxy_rate: 0.882
```

Interpretation:

The generator is strongly constraint-dominated. The high conflict proxy suggests structured but constrained corridors or compatibility conflict, not roughness-dominated arbitrary selection.

## Support and Process Phenotypes

Support controls:

```text
support_deformation: 39
mixed_support_deformation: 29
beyond_support_matched: 20
```

Process classes:

```text
transition_process_candidate: 70
distribution_deformation_candidate: 18
```

This is still not proof of a robust path-process object, because these are lightweight path/process proxies. But it is enough to justify keeping process diagnostics in the next pass.

## Answers

Does the relation generator still look worth keeping?

```text
Yes, for now. The repaired audit indicates recurring candidate phenotypes that are mostly not start-fragile and not simply roughness artifacts.
```

Are candidates mostly start-local, basin-local, or environment-level?

```text
Mostly environment-level under the tested start-sample settings.
```

Is roughness sensitivity edge-level, near-cutoff, frontier-level, null-rank-level, or phenotype-level?

```text
Mostly null-rank/phenotype-level sensitivity, not direct roughness edge dominance. A minority shows edge sensitivity or edge brittleness.
```

Are candidates roughness artifacts, symmetry-breaking candidates, or noise-tolerant candidates?

```text
Only 1/88 rows was classified as confirmed roughness artifact. Most rows were noise-tolerant or edge-stable despite roughness-resampled null sensitivity.
```

Is the generator constraint-dominated, asymmetry-dominated, or near-tie dominated?

```text
Constraint-dominated.
```

Does constraint dominance produce conflicted but structured corridors or lock-in?

```text
The high constraint conflict proxy suggests conflicted structured corridors. This pass did not establish lock-in as the dominant interpretation.
```

Do any candidates show path/process structure beyond support deformation?

```text
Lightweight proxies classify most rows as transition-process candidates, but this needs a dedicated path-language pass.
```

## Claim Boundary

This does not validate Omega, agency, identity, valuerhood, viability, or a scientific gate.

Allowed claim:

```text
The relation generator remains worth keeping for another focused diagnostic pass.
The phenotype machinery is now less misleading about roughness.
```

## Recommendation

Do not pivot the relation generator yet.

Next best probe:

```text
Increase per-stage job count to at least 18 for better CPU saturation, then run a path/process-focused diagnostic on the constraint-dominated, edge-stable/noise-tolerant phenotype subset.
```

Also implement:

```text
true directed degree-sequence preserving null
path bigram/trigram summaries
frontier/path similarity by roughness replay
better roughness replay parallelism
```

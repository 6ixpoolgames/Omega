# RFS-MB0 Relation Atlas Breadth/Null Repair Smoke Result

Date: 2026-05-25

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_RELATION_ATLAS_BREADTH_AND_NULL_REPAIR_SPEC.md
```

Local smoke output:

```text
results/rfs_mb0_relation_atlas/20260525_breadth_null_repair_smoke/
```

## Purpose

This was a tiny implementation smoke for the breadth/null-repair runner. It was not an evidence-bearing validation run.

The goal was to verify that the runner now:

- exits cleanly on a small wall-clock budget;
- writes explicit integrity and coverage outputs;
- uses stratified candidate-window stress selection;
- decomposes the former `frontier_or_probe_marginal` blocker into named diagnostic nulls;
- records that replicate-null uncertainty remains unresolved when no true null replicates are implemented.

## Run Shape

```text
workers: 6
wall-clock budget: 1200 seconds
wall-clock used: about 200 seconds
total environment evaluations: 12
unique parameter sets: 12
unique parameter regions: 12
middle-regime environments: 8
atlas gate passes: 0
```

Stages completed:

```text
A, B, C, E
```

Stage D was not attempted in this tiny smoke.

## New Diagnostic Outputs Verified

The smoke produced:

```text
stage_integrity_report.csv
unique_coverage_summary.csv
repair_stage_e_window_null_stress/window_stress_selection_summary.csv
repair_stage_e_window_null_stress/frontier_probe_null_decomposition.csv
repair_stage_e_window_null_stress/null_replicate_summary.csv
repair_stage_e_window_null_stress/heldout_reproducibility_summary.csv
repair_stage_e_window_null_stress/presentation_perturbation_summary.csv
repair_stage_e_window_null_stress/relation_perturbation_summary.csv
```

## Tiny-Smoke Null Read

The smoke selected 12 candidate windows and wrote 132 null-specific rows.

Candidate-window survival in this tiny smoke:

```text
degree_preserving_rewire: 12/12 survived
out_degree_preserving_random: 12/12 survived
constraint_shuffled: 0/12 survived
asymmetry_shuffled: 0/12 survived
roughness_resampled: 0/12 survived
frontier_size_only: 12/12 survived
probe_marginal_only: 12/12 survived
frontier_size_plus_probe_marginal: 12/12 survived
signature_support_matched: 0/12 survived
horizon_local_frontier_matched: 12/12 survived
window_local_frontier_matched: 12/12 survived
```

Interpretation:

The decomposed diagnostic is working: the prior blunt frontier/probe blocker is no longer a single opaque failure mode. In this tiny smoke, the immediate blocker was signature-support matching plus the existing constraint/asymmetry/roughness shuffles, not frontier size alone or probe marginals alone.

This is not a scientific positive. It is a readiness result for a larger breadth/null-repair run.

## Remaining Limitations

- True null replicates are not implemented yet; `null_replicate_summary.csv` explicitly marks `no_replicate_null_uncertainty`.
- Presentation and relation perturbation files are explicit placeholders unless those perturbation flags are backed by substrate-level perturbation implementation.
- Stage E is diagnostic-only and does not have raw environment files; the integrity report correctly marks missing raw stage files rather than silently treating them as clean completion.

## Recommendation

Proceed to a small-to-medium real run before any overnight-scale run:

```text
workers: 18
stage-b-samples: 80-150
stage-c-samples: 40-80
stage-c-seeds: 2
stress-sample-count: 120-200
wall clock: 30-90 minutes
```

Do not interpret candidate windows as evidence unless they survive the decomposed support/frontier/probe diagnostics, repaired shuffles, fresh-seed grouping, and later true null replicates.

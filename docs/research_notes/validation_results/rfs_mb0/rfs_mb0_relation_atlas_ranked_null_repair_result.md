# RFS-MB0 Relation Atlas Ranked Null-Repair Result

Date: 2026-05-25

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_RELATION_ATLAS_BREADTH_AND_NULL_REPAIR_SPEC.md
```

Local run output:

```text
results/rfs_mb0_relation_atlas/20260525_breadth_null_repair_ranked_real/
```

## Purpose

This was the first real breadth/null-repair pass after adding rank-based null replicate diagnostics. It was still a relation-atlas calibration run, not Omega validation.

The live question was:

```text
Do window-level candidates survive a broader parameter pass once null survival is ranked against replicate null ensembles?
```

## Implementation Update

The runner now supports true null replicate readouts:

- `run_relation_atlas.py` accepts `--null-replicates`.
- Per-horizon profile rows include JS/KL ranks against null replicates.
- Transition summaries include MI/motif ranks against null replicates.
- Stage E switches from threshold-style survival to rank-style survival when replicate ranks are available.
- `null_replicate_summary.csv` reports implemented replicate count and no longer marks unresolved uncertainty when ranks are present.

For this run, requested and implemented null replicates were:

```text
null_replicates: 5
```

## Run Shape

```text
workers: 18
start_samples: 1
wall-clock budget: 5400 seconds
wall-clock used: about 4915 seconds
total environment evaluations: 146
unique parameter sets: 110
unique parameter regions: 110
middle-regime environments: 109
atlas gate passes: 0
```

Stage read:

```text
Stage B broad n=5: 80 environments, 45 middle-regime, 0 gate passes
Stage C core n=5: 66 environments completed before cap, 64 middle-regime, 0 gate passes
Stage D n=6 transfer: skipped/deferred
Stage E window stress: 160 candidate windows, 1760 null-specific rows
```

Stage C was partial because the global cap was reached. Outputs were still salvaged.

## Coverage

```text
total_environment_evaluations: 146
unique_parameter_sets: 110
unique_parameter_regions: 110
exploratory_environment_count: 80
confirmatory_environment_count: 66
fresh_seed_environment_count: 66
transfer_environment_count: 0
```

The run froze 4 confirmatory core regions after Stage B:

```text
shape_selected_core:
  update_footprint 2
  out_degree_target 2
  constraint_density 0.4
  constraint_strength 1

interaction cores:
  out_degree_target 2 x reversibility_fraction 0.25
  out_degree_target 3 x reversibility_fraction 0.25
  out_degree_target 4 x reversibility_fraction 0
```

## Ranked Null Results

Stage E selected 160 structured-candidate windows.

Survival rates under rank-based null criteria:

```text
degree_preserving_rewire: 0/160 survived
out_degree_preserving_random: 2/160 survived
constraint_shuffled: 0/160 survived
asymmetry_shuffled: 0/160 survived
roughness_resampled: 0/160 survived
frontier_size_only: 44/160 survived
probe_marginal_only: 160/160 survived
frontier_size_plus_probe_marginal: 63/160 survived
signature_support_matched: 77/160 survived
horizon_local_frontier_matched: 59/160 survived
window_local_frontier_matched: 62/160 survived
```

Median ranks:

```text
probe_marginal_only:
  JS rank 1.000
  KL rank 1.000
  MI rank 1.000
  motif rank 1.000

signature_support_matched:
  JS rank 0.792
  KL rank 0.790
  MI rank 1.000
  motif rank 1.000

degree_preserving_rewire:
  JS rank 0.616
  KL rank 0.607
  MI rank 1.000
  motif rank 0.910

constraint_shuffled:
  JS rank 0.568
  KL rank 0.572
  MI rank 0.540
  motif rank 0.500

roughness_resampled:
  JS rank 0.240
  KL rank 0.237
  MI rank 0.520
  motif rank 0.480
```

## Reproducibility

Localized reproducibility remained zero:

```text
localized candidate groups: 122
localized_reproducible_candidate: 0
```

Held-out grouping rows were written for:

```text
exact_parameter_set
frozen_region
interaction_region
one_parameter_neighborhood
probe_family
window_name
```

These are grouping diagnostics over the completed run, not proof of held-out invariance.

## Interpretation

The improved rank-based diagnostics sharpen the earlier result.

The window candidates are not merely failing because of probe marginals. Under the decomposed nulls, `probe_marginal_only` was not a blocker in this run.

The candidates are still not robust:

- aggregate atlas gate remained 0;
- degree-preserving and out-degree-preserving ranked nulls killed almost all selected windows;
- constraint/asymmetry/roughness shuffles killed all selected windows;
- frontier/support/local-frontier matched nulls killed a substantial fraction;
- localized reproducibility remained 0.

The most important update is methodological, not evidential: rank-based nulls are now available and materially stricter than the earlier deterministic-null smoke.

## Claim Boundary

This run does not validate Omega, reachable-futures deformation, agency, value, identity, or any scientific gate.

Current status:

```text
relation-atlas substrate calibration: useful
local/window candidate detector: still artifact-prone
aggregate scientific gate: failed
next action: either repair substrate/detector assumptions or treat this branch as a falsifying/diagnostic calibration layer
```

## Recommendation

Do not scale this exact relation-atlas configuration overnight yet.

Recommended next step:

```text
Run a smaller diagnostic branch focused on why degree/out-degree ranked nulls now kill candidates that survived deterministic degree/out-degree nulls.
```

Specifically:

- compare deterministic null metrics against replicate-rank metrics for the same selected windows;
- inspect whether rank failure is driven by JS/KL, MI/motif, or aggregation over windows;
- test whether `start_samples=1` changed candidate behavior too much;
- only then decide whether relation-atlas deserves a larger 12-hour pass.

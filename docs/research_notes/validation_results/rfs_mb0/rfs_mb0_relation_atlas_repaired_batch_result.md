# RFS-MB0 Relation Atlas Repaired Batch Result

Date: 2026-05-23

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_RELATION_ATLAS_BATCH_RUNNER_REPAIR_SPEC.md
```

Primary local result root:

```text
results/rfs_mb0_relation_atlas/
```

Primary local summary:

```text
results/rfs_mb0_relation_atlas/repaired_batch_summary.md
```

## Purpose

This pass repaired the relation-atlas due-diligence machinery before moving to
new substrates or detector families.

It targeted five issues from the audit:

- broad OR-style Stage C targeting;
- incomplete per-null window stress reporting;
- missing parameter interaction trends;
- missing localized candidate reproducibility diagnostics;
- weak reporting of requested vs matched parameter counts.

This was not a detector-threshold tuning pass and not a theory-positive claim.

## Repairs

Implemented:

```text
--parameter-region-mode any|core_only|all
```

with `core_only` used for the due-diligence targeted stages.

Added status/config fields:

```text
parameter_region_mode
raw_parameter_candidates
filtered_parameter_sets
jobs_created
jobs_completed
requested_parameter_samples
```

Added repaired diagnostics:

```text
parameter_interaction_trends.csv
parameter_interaction_trends.md
repair_stage_c_core_regions.json
repair_stage_c_broad_regions.json
window_null_kill_table.csv
localized_candidate_reproducibility.csv
localized_candidate_reproducibility.md
repaired_batch_summary.md
repaired_batch_status.json
```

## Run Shape

Wall clock:

```text
8830 seconds
about 2.45 hours
```

Total completed/partial generated environments:

```text
1040
```

Total middle-regime environments:

```text
871
```

Atlas gate passes:

```text
0
```

Stages:

```text
Stage A: existing trend mining completed
Stage B: broad n=5 completed
Stage C: core_only targeted n=5 partial by time cap
Stage D: core_only n=6 transfer completed
Stage E: per-null window stress completed
```

Stage B broad n=5:

```text
environments: 300
middle-regime: 176
profiles: 49500
errors: 0
atlas gate passes: 0
elapsed: about 2148 seconds
```

Stage C core_only targeted n=5:

```text
requested parameter samples: 500
raw parameter candidates: 1944
filtered parameter sets: 336
jobs created: 672
jobs completed: 660
middle-regime: 620
profiles: 108900
errors: 0
atlas gate passes: 0
status: TIME_LIMIT_REACHED
elapsed: about 5795 seconds
```

Stage D core_only n=6:

```text
requested parameter samples: 80
filtered parameter sets: 80
jobs completed: 80
middle-regime: 75
profiles: 19440
errors: 0
atlas gate passes: 0
elapsed: about 770 seconds
```

## Core Region Selection

Core-only targeting selected four core regions from Stage B trend mining.

The explicit multivariate core region was:

```text
update_footprint: 2
out_degree_target: 2
constraint_density: 0.4
constraint_strength: 1.0
```

Interaction-derived core regions emphasized:

```text
out_degree_target: 2, reversibility_fraction: 0.25
out_degree_target: 3, reversibility_fraction: 0.25
out_degree_target: 4, reversibility_fraction: 0.0
```

These selections were based on environment-shape criteria, not detector passes.

## Interaction Trend Read

Stage B interaction trends again show that relation-atlas behavior is strongly
interaction-shaped.

Notable broad n=5 interaction rates:

```text
out_degree_target=2, reversibility_fraction=0.25:
  middle-regime rate: 1.000
  underconnected: 0.000
  fast saturation: 0.000

out_degree_target=3, reversibility_fraction=0.25:
  middle-regime rate: 0.973

out_degree_target=4, reversibility_fraction=0.0:
  middle-regime rate: 0.955

constraint_density=0.4, constraint_strength=1.0:
  middle-regime rate: 0.781
```

These are exploratory associations only, not causal claims.

## Null-Kill Read

Stage E inspected 200 structured-candidate windows and produced 1200
null-specific rows.

Null survival counts:

```text
degree_preserving_rewire: 200 / 200 survived
out_degree_preserving_random: 200 / 200 survived
constraint_shuffled: 56 / 200 survived
asymmetry_shuffled: 37 / 200 survived
roughness_resampled: 56 / 200 survived
frontier_or_probe_marginal: 0 / 200 survived
```

Dominant kill reasons:

```text
aggregate_gate_not_passed: 549
failed_frontier_probe_marginal: 200
failed_asymmetry_shuffle: 163
failed_constraint_shuffle: 144
failed_roughness_resample: 144
```

Interpretation:

```text
The inspected window candidates are not merely degree or out-degree artifacts.
However, they are still blocked by frontier/probe-marginal diagnostics, by
constraint/asymmetry/roughness shuffles, and by the aggregate gate.
```

## Reproducibility Read

Localized reproducibility diagnostics found:

```text
localized_reproducible_candidate: 0
non-promoting candidate groups inspected: 111
```

Many candidate windows recur locally across related parameter strings, but none
met the diagnostic threshold for localized reproducibility under the repaired
rules.

## Interpretation

This is a successful due-diligence repair pass and another negative scientific
gate result.

The strongest positive result is substrate hygiene:

- core-only targeting produced a much narrower middle-regime sample;
- n=6 core transfer was strong: 75 / 80 middle-regime;
- window candidates are now decomposed by specific null failures.

The strongest negative result is that no candidate currently survives the full
discipline:

- atlas gate passes remain 0;
- frontier/probe-marginal kills every inspected candidate window;
- localized reproducibility remains 0 under repaired diagnostics.

## Recommendation

Do not move to a positive claim.

Next useful work should focus on one of two paths:

- improve the probe/frontier diagnostic layer if the current frontier/probe
  marginal null is too blunt;
- or accept that current candidates are mostly window-local artifacts and move
  to a new substrate/detector family.

In either case, preserve the repaired batch runner as the standard
due-diligence layer for relation-atlas runs.

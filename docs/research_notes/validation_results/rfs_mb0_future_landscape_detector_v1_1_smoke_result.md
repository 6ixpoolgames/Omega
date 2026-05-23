# RFS-MB0 Future Landscape Detector v1.1 Smoke Result

Date: 2026-05-23

Status: detector v1.1 implemented; smoke passed; scientific gate not passed

Result directory:

```text
results/rfs_mb0_future_landscape/20260523_detector_v1_1_smoke/
```

Primary summary:

```text
results/rfs_mb0_future_landscape/20260523_detector_v1_1_smoke/summary.md
```

## Purpose

This run implements the code-audit targets in:

```text
docs/RFS_MB0_FUTURE_LANDSCAPE_V1_1_CODE_TARGETS.md
```

The goal was not to tune detector thresholds. The goal was to prevent isolated local profile hits from becoming family-level structure claims.

## Implementation

Updated:

```text
omega/rfs_mb0_future_landscape/controls.py
omega/rfs_mb0_future_landscape/landscape.py
omega/rfs_mb0_future_landscape/run_smoke.py
```

Added:

```text
local_profile_class_v1_1
aggregate_family_class_v1_1
aggregate_probe_family_class_v1_1
frontier_size matched null column
degree-control local false-positive audit
matched null summary
```

New output files:

```text
aggregate_family_classes.csv
aggregate_probe_family_classes.csv
degree_control_false_positives.csv
matched_null_summary.csv
```

## Run Shape

```text
systems: 33
future profiles: 3696
workers: 18
errors: 0
status: COMPLETED
elapsed: about 42 seconds
```

## Main Read

The v1.1 aggregation repair worked.

Detector v1 still reports local profile-level degree-control hits:

```text
degree_control_local_false_positive_count: 39
```

But v1.1 prevents those local hits from promoting probe-family or family-level claims:

```text
degree_control_probe_family_aggregate_passes: 0
aggregate_structured_family_count: 0
```

Degree-preserving control is now labeled:

```text
aggregate_family_class_v1_1:
  control_local_candidates
```

with:

```text
local_candidate_fraction: 0.096
mean_MI_delta_vs_null: -0.033
median_MI_delta_vs_null: -0.017
mean_motif_delta_vs_null: -0.047
passing_probe_family_count: 0
```

The local false positives are concentrated mostly in pairwise probes:

```text
pairwise_ordered_projection: 20 local hits, aggregate pass 0
pairwise_unordered_multiset: 11 local hits, aggregate pass 0
pairwise_modular_difference: 7 local hits, aggregate pass 0
single_coordinate_projection: 1 local hit, aggregate pass 0
```

## Gate Status

```text
Implementation gate:
  passed

Degree-control aggregate guardrail:
  passed

Scientific gate:
  not passed
```

The scientific gate is not passed because no non-control, non-saturated family receives aggregate `structured_propagation`.

Current aggregate results:

```text
structured_relation:
  saturation_dominated

expanding_relation:
  saturation_dominated

contracting_relation:
  underdetermined

cyclic_relation:
  underdetermined
```

This is the correct conservative outcome for the current substrate.

## Recommendation

Do not scale yet.

The next implementation target should remain substrate/null repair:

1. Add a genuinely distinct frontier-size preserving null if the current marginal proxy is not enough.
2. Add saturation-matched null families before allowing saturated profiles to compete for structure.
3. Consider a non-saturating structured family so the detector can be tested on a positive candidate that is not immediately withheld.
4. Keep local candidates visible but never promote them without aggregate family and probe-family support.

v1.1 is a methodological improvement, not a positive result.

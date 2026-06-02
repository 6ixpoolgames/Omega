# Future Field Atlas Rank-Order Boundary Medium Sweep Result

Status: completed cleanly; pair005-only critical-pair read

Runner: `omega.future_field_atlas.run_coupled_future_field_atlas`

Spec: `docs/specs/current/FUTURE_FIELD_ATLAS_RANK_ORDER_BOUNDARY_MEDIUM_SWEEP_SPEC.md`

## Summary

This pass ran the first medium pair-aware rank-order-boundary sweep:

```text
Run A:
  H64 pair8 breadth

Run B:
  targeted H128 depth for H64-qualifying high-yield pairs
```

The H64 breadth run completed cleanly and found exactly one high-residual,
marginal-preserving pair: `pair005`. The conditional H128 depth pass was
therefore run only for `pair005`; it also completed cleanly and preserved the
same final geometry.

Allowed claim:

```text
Rank-order-boundary alignment is clean across the H64 pair8 design and
reproduces the pair005 marginal-preserving joint-restriction signature. In the
current pair8 set, pair005 remains the only high-residual exemplar.
```

Blocked claims:

```text
Omega validation
agency / identity / valuerhood / value
support / capture / erasure
compatibility detection
interaction detection
broad substrate-general claim
```

## Run A: H64 Pair8

Run directory:

```text
results/future_field_atlas/20260602_rank_order_boundary_h64_pair8_medium/
```

Config:

```text
horizon_max: 64
horizon_schedule: dense
pair_count: 8
workers: 4
raw_topology_output_mode: worker_spool
csv_output_mode: gzip
gzip_compresslevel: 1
joint_selection_family: rank_order_boundary
joint_effective_out_degree: 4
coupling_strength: 0.000
```

Rebuild contract:

```text
source_git_commit: eb594186cc0900be7c135460fc6129afbd2d4e12
source_git_dirty: false
```

Gate results:

```text
status: COMPLETED
pair_count_realized: 8 / 8
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS 3
medium_sweep_interpretation_allowed: 1
elapsed_seconds: 397.633
```

Artifact rows:

```text
joint edge rows: 22,107,242
joint node rows: 3,225,832
profile rows: 1,040
residual rows: 520
marginal rows: 520
marginal projection rows: 1,040
```

Retention:

```text
total output GiB before raw-spool deletion: 1.195870
raw delete candidate GiB: 1.195779
raw spools deleted: yes
```

## H64 Pair Table

At H64:

| pair | residual | joint retention | A retention | B retention | density vs marginal product | product support | coupled support |
|---|---:|---:|---:|---:|---:|---:|---:|
| pair000 | 0.040000 | 0.960000 | 1.000000 | 1.000000 | 0.960000 | 100 | 96 |
| pair001 | 0.050853 | 0.949147 | 1.000000 | 1.000000 | 0.949147 | 8613 | 8175 |
| pair002 | 0.084000 | 0.916000 | 1.000000 | 1.000000 | 0.916000 | 1000 | 916 |
| pair003 | 0.064157 | 0.935843 | 1.000000 | 1.000000 | 0.935843 | 8900 | 8329 |
| pair004 | 0.031818 | 0.968182 | 1.000000 | 1.000000 | 0.968182 | 880 | 852 |
| pair005 | 0.753455 | 0.246545 | 1.000000 | 1.000000 | 0.246545 | 11000 | 2712 |
| pair006 | 0.062222 | 0.937778 | 1.000000 | 1.000000 | 0.937778 | 900 | 844 |
| pair007 | 0.064444 | 0.935556 | 1.000000 | 1.000000 | 0.935556 | 900 | 842 |

Read:

```text
All eight pairs preserve A/B marginals.
Only pair005 is high-residual and joint-restrictive.
The H64 pair8 run does not establish a broad morphology class; it isolates
pair005 as the current critical-pair exemplar.
```

## Comparison To Product And Scalar 0.020

Final-H64 comparison:

| pair | product residual | scalar 0.020 residual | rank-order residual | rank-order A/B retention |
|---|---:|---:|---:|---:|
| pair000 | 0.000000 | 0.030000 | 0.040000 | 1.000000 / 1.000000 |
| pair001 | 0.000000 | 0.048647 | 0.050853 | 1.000000 / 1.000000 |
| pair002 | 0.000000 | 0.061000 | 0.084000 | 1.000000 / 1.000000 |
| pair003 | 0.000000 | 0.066517 | 0.064157 | 1.000000 / 1.000000 |
| pair004 | 0.000000 | 0.026136 | 0.031818 | 1.000000 / 1.000000 |
| pair005 | 0.000000 | 0.752364 | 0.753455 | 1.000000 / 1.000000 |
| pair006 | 0.000000 | 0.050000 | 0.062222 | 1.000000 / 1.000000 |
| pair007 | 0.000000 | 0.040000 | 0.064444 | 1.000000 / 1.000000 |

Interpretation:

```text
Rank-order boundary and scalar mismatch 0.020 have very similar final-H64
pair structure. The ordinal operator reproduces the scalar branch without
using coupling_strength as a tuning knob.
```

## Run B: Targeted H128 Pair005

Only `pair005` satisfied the H64 depth criterion:

```text
joint_support_residual_final >= 0.4
A_marginal_retention_final >= 0.99
B_marginal_retention_final >= 0.99
```

Run directory:

```text
results/future_field_atlas/20260602_rank_order_boundary_h128_pair005_depth/
```

Gate results:

```text
status: COMPLETED
pair_count_realized: 1 / 1
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS 3
medium_sweep_interpretation_allowed: 1
elapsed_seconds: 610.052
source_git_commit: eb594186cc0900be7c135460fc6129afbd2d4e12
source_git_dirty: false
```

Artifact rows:

```text
joint edge rows: 13,406,072
joint node rows: 1,684,965
profile rows: 258
residual rows: 129
marginal rows: 129
marginal projection rows: 258
```

Retention:

```text
total output GiB before raw-spool deletion: 0.709497
raw delete candidate GiB: 0.709464
raw spools deleted: yes
```

At H128:

| pair | residual | joint retention | A retention | B retention | density vs marginal product | product support | coupled support |
|---|---:|---:|---:|---:|---:|---:|---:|
| pair005 | 0.753455 | 0.246545 | 1.000000 | 1.000000 | 0.246545 | 11000 | 2712 |

The final H128 read equals the final H64 read for pair005, indicating the
retained pair005 rank-order geometry is already stable by H64 in this run.

## Horizon Onset

The regenerated morphology atlas reports:

```text
rank_order_boundary_h64_pair8, pair005 vs product:
  first horizon crossing: 1
  max delta horizon: 4

rank_order_boundary_h64_pair8, pair005 vs zero-penalty joint rank-prefix:
  first horizon crossing: 3
  max delta horizon: 16

rank_order_boundary_h128_pair005 vs pair005_h128_c0000:
  first horizon crossing: 3
  max delta horizon: 16
```

This is an early-onset geometric divergence, not a late-horizon surprise.

## Updated Morphology Atlas

The substrate morphology atlas was regenerated:

```text
source_run_count: 29
source_summary_dir_count: 2
manifest_digest: 81257330781d13a4499551a1
```

Output counts:

```text
field_morphology_summary.csv: 294
pair_morphology_summary.csv: 147
operator_sensitivity_summary.csv: 115542
horizon_onset_summary.csv: 1750
observable_geometry_summary.csv: 736
```

Updated next target:

```text
rank_order_boundary_pair005_neighbor_search
```

The morphology target is no longer the medium pair8 sweep; this result
completed that step. The next live question is whether pair005 has neighbors or
is an isolated critical-pair exemplar.

## Mechanism Read

Current read:

```text
Rank-order-boundary alignment is a clean operational mechanism for the pair005
signature.

The current evidence does not yet show a broad rank-order-boundary morphology
class. It shows one robust high-yield exemplar, pair005, with seven H64 controls
remaining low-residual and marginal-preserving.

The H128 depth check confirms pair005 final geometry rather than revealing a
new late-horizon branch.
```

This updates the roadmap:

```text
stop broad H128 for now;
search for pair005-like neighbors or vary observable;
keep rank_order_boundary as the live coupled operator;
keep shared_capacity v1 as a negative control / repair target only.
```

## Recommendation

Next run should not be larger breadth for its own sake. It should be a targeted
neighbor/observable pass:

```text
rank_order_boundary_pair005_neighbor_search:
  find pair005-like neighbors in nearby generator groups or pair geometry;
  include low-residual controls;
  keep product, zero-penalty joint rank-prefix, scalar 0.020, and
  shared_capacity v1 references;
  run H64 first, with targeted H128 only if new high-yield pairs appear.

observable_extension:
  current retained morphology is still symbol_histogram_distance-only.
```

Do not promote to Omega, agency, value, compatibility, support, capture, or
erasure language.

## Claim Boundary

This is a coupled-instrument mechanism-resolution result only. It shows that a
rank-order-native coupled selector remains clean across H64 pair8 and that
pair005 persists under targeted H128. It does not detect interaction,
compatibility, support, capture, erasure, agency, identity, value, or Omega.

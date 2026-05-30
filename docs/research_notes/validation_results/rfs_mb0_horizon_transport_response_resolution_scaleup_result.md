# RFS-MB0 Horizon-Transport Response-Resolution Scaleup Result

Date: 2026-05-31 local / 2026-05-30 UTC  
Spec lineage: `docs/RFS_MB0_HORIZON_TRANSPORT_EXPANSION_SMOKE_SPEC.md`  
Runner: `omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair`  
Local outputs:

- `results/local_runs/20260531_horizon_transport_response_resolution_scaleup_v2/`
- `results/local_runs/20260531_horizon_transport_response_ladder_p015_p02/`

Generated CSV/JSON outputs remain local-only and should not be committed.

## Executive Summary

The horizon-transport scaleup passed the instrument gates again under committed
repo-local inputs, not the prior missing local 192-input bundle. The matched
marginal detector-null gate remained clean at `9` null replicates, both required
probes and both flow modes remained covered, and the response profiles became
more informative than the prior uniformly stable smoke.

At `p <= 0.005`, responses stayed stable. At `p = 0.01`, a minority of
mid/downstream contexts moved from `transport_stable` to
`transport_control_equivalent` through increased spectral mass while preserving
high subspace alignment. A focused `p = 0.015,0.02` ladder made this transition
larger: `50 / 112` perturbation-response rows became
`transport_control_equivalent`, concentrated in `8->16`, `16->24`, and `24->32`
horizon transport.

The run did not produce `transport_weakened`, `transport_rerouted`,
`transport_reopens`, or `transport_collapses`. That is a useful negative result:
the object is robust under the current nonlethal perturbation ladder, and the
instrument can see a mass-growth departure from stable before collapse, but the
current ladder does not yet resolve the full response taxonomy.

This remains an instrument/result-shaping pass only. It is not Omega detection,
agency detection, value detection, holdout scoring, candidate promotion, or
direct channel causality.

## Code Audit Repairs

Before retaining the run, the horizon-transport runner was audited and repaired
in small scope:

- Windows `SIGBREAK` is now handled alongside `SIGINT` and `SIGTERM`.
- Future-level worker exceptions now count the affected jobs as completed with
  errors instead of leaving job accounting inconsistent.
- Cancelled job accounting now counts jobs, not future batches.
- Progress checkpoints now update `pending_jobs_remaining` during the run.
- Response rows now include direct `actual_control_name`,
  `mechanism_control_strength`, and `horizon_pair` fields for easier review.
- Response classification now checks collapse, weakening, and entropy reopening
  before the broad stable gate.
- Response rows now emit `response_flags` such as `aligned`,
  `mass_collapse`, `entropy_reopened`, and `large_entry_response`.

The synthetic fixture smoke still passed after these repairs:

```text
block_transport_signal: passed
marginal_fakeout: passed
corridor_stable_response: passed
trap_collapse_response: passed
```

## Run 1: Response-Resolution Scaleup

Run directory:

```text
results/local_runs/20260531_horizon_transport_response_resolution_scaleup_v2/
```

Shape:

```text
groups: 18
design_groups: 6
holdout_groups: 12
fresh_seeds_per_group: 4
start_samples_list: 2,4,8
probes: constraint_profile_hash,constraint_violation_count_plus_local_tuple
conditions:
  baseline
  small_edge_resample_control: p0.0025,p0.005,p0.01
  asymmetric_edge_flip_control: p0.0025,p0.005,p0.01
workers: 18
null_replicates: 9
```

Completion:

```text
status: COMPLETED
jobs_completed: 1008 / 1008
elapsed_seconds: 58.420
errors: 0
matrix_count: 196
detector_null_rows: 672
matched_marginal_summary_rows: 84
perturbation_response_rows: 168
```

Gates:

```text
matrix coverage: passed, observed 1.0
structure detector-null separation: passed
null replicate power: passed, null_replicates 9
matched marginal detector-null separation: passed, 3/3 families
fixture contract: not required in empirical expansion run
```

Response counts:

| response class | count |
|---|---:|
| transport_stable | 144 |
| transport_control_equivalent | 24 |

By perturbation:

| control | strength | stable | control-equivalent |
|---|---:|---:|---:|
| small_edge_resample_control | 0.0025 | 28 | 0 |
| small_edge_resample_control | 0.005 | 28 | 0 |
| small_edge_resample_control | 0.01 | 16 | 12 |
| asymmetric_edge_flip_control | 0.0025 | 28 | 0 |
| asymmetric_edge_flip_control | 0.005 | 28 | 0 |
| asymmetric_edge_flip_control | 0.01 | 16 | 12 |

Control-equivalent rows were high-alignment, positive-mass-shift cases:

```text
mean alignment: 0.976 average
mass delta fraction: 0.191 average
response magnitude: 0.222 average
entropy delta: 0.027 average
```

## Run 2: Focused p0.015/p0.02 Response Ladder

Run directory:

```text
results/local_runs/20260531_horizon_transport_response_ladder_p015_p02/
```

Shape:

```text
groups: 18
design_groups: 6
holdout_groups: 12
fresh_seeds_per_group: 4
start_samples_list: 2,4,8
probes: constraint_profile_hash,constraint_violation_count_plus_local_tuple
conditions:
  baseline
  small_edge_resample_control: p0.015,p0.02
  asymmetric_edge_flip_control: p0.015,p0.02
workers: 18
null_replicates: 9
```

Completion:

```text
status: COMPLETED
jobs_completed: 720 / 720
elapsed_seconds: 48.371
errors: 0
matrix_count: 140
detector_null_rows: 672
matched_marginal_summary_rows: 84
perturbation_response_rows: 112
```

Gates:

```text
matrix coverage: passed, observed 1.0
structure detector-null separation: passed
null replicate power: passed, null_replicates 9
matched marginal detector-null separation: passed, 3/3 families
fixture contract: not required in empirical expansion run
```

Response counts:

| response class | count |
|---|---:|
| transport_stable | 62 |
| transport_control_equivalent | 50 |

By perturbation:

| control | strength | stable | control-equivalent |
|---|---:|---:|---:|
| small_edge_resample_control | 0.015 | 16 | 12 |
| small_edge_resample_control | 0.02 | 14 | 14 |
| asymmetric_edge_flip_control | 0.015 | 16 | 12 |
| asymmetric_edge_flip_control | 0.02 | 16 | 12 |

By horizon pair:

| horizon pair | stable | control-equivalent |
|---|---:|---:|
| 0->1 | 16 | 0 |
| 1->2 | 16 | 0 |
| 2->4 | 16 | 0 |
| 4->8 | 14 | 2 |
| 8->16 | 0 | 16 |
| 16->24 | 0 | 16 |
| 24->32 | 0 | 16 |

Control-equivalent rows again showed strong mass growth rather than collapse:

```text
mean alignment: 0.908 average
mass delta fraction: 0.398 average
response magnitude: 0.445 average
entropy delta: 0.029 average
```

## Interpretation

The key positive result is persistence of matched-marginal-separated
horizon transport at larger design-set scale. That supports the current
instrument direction: directional horizon transport is a better object than
endpoint support/distribution deformation alone.

The key response-profile result is graded but not fully taxonomic. The
instrument sees:

```text
transport_stable
transport_control_equivalent with positive mass-growth departure
```

It does not yet see:

```text
transport_weakened
transport_rerouted
transport_reopens
transport_collapses
```

The response ladder therefore improves on the prior uniformly stable smoke, but
it does not yet justify graph-channel diagnostics, holdout scoring, or candidate
promotion.

## Recommended Next Step

Next work should target response-profile resolution, not broader claim scale.

Recommended:

```text
1. Add synthetic fixtures for reopens and reroutes, not only stable and collapse.
2. Add a compact response-profile report that separates:
   - mass growth with high alignment
   - mass weakening
   - entropy reopening
   - low-alignment rerouting
3. Run another design-set-only ladder after fixture expansion.
```

Not recommended yet:

```text
direct graph-channel diagnostics
holdout scoring
candidate promotion
Omega / agency / value interpretation
```

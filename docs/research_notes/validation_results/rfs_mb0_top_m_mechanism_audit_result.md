# RFS-MB0 Hard Top-m Mechanism Audit Result

Status: medium sweep completed
Primary medium output: `results/local_runs/20260601_top_m_mechanism_medium_dg12_v2/`
Earlier smoke output: `results/local_runs/20260601_top_m_mechanism_smoke/`
Runner: `omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair`
Spec: `docs/RFS_MB0_TOP_M_MECHANISM_AUDIT_SPEC.md`

## Executive Summary

The hard-top-m mechanism branch is now past the tiny smoke stage. The corrected
medium design-group sweep completed cleanly:

```text
jobs_completed: 8640 / 8640
workers: 18
elapsed_seconds: 213.430
errors: 0
matrix_count: 1980
detector_null_gate_passed: 1
detector_null_replicate_powered: 1
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract_passed: 1
paired_baseline_missing_rows: 0
readiness_level: top_m_pruning_variant_response_bearing
next_action_fork: expand_strict_pruning_controls_and_inspect_deterministic_reproducibility
```

This remains a substrate-mechanism result, not a theory validation result. The
run used the primary `symbol_histogram_distance` invariant, betas `0.075`,
`0.10`, and `0.15`, and the full H128 horizon ladder.

## Main Update

The medium sweep changed the read from the tiny smoke:

```text
deterministic_top_m:
  stable on the broader design-group sweep

top_m_m_minus_1:
  response-bearing across all tested betas, strongest at beta 0.10

top_m_m_plus_1:
  stable despite retaining every deterministic top-m edge

boundary jitter and core/fringe randomization:
  stable
```

The important point is no longer "deterministic top-m itself reproduced the
effect." On broader design groups, it did not. The surviving mechanism signal is
strict pruning: selecting `m-1` lowest-energy edges per state.

## Sampler Response

Primary invariant only:

| sampler_family | response rows | dominant response | aligned fraction |
|---|---:|---|---:|
| deterministic_top_m | 264 | transport_stable | 0.000 |
| top_m_boundary_jitter | 264 | transport_stable | 0.000 |
| top_m_core_preserved_fringe_randomized | 264 | transport_stable | 0.000 |
| top_m_core_randomized_fringe_preserved | 264 | transport_stable | 0.000 |
| top_m_m_minus_1 | 264 | transport_stable | 0.443 |
| top_m_m_plus_1 | 264 | transport_stable | 0.000 |

By beta:

| sampler_family | beta | response rows | dominant response | aligned fraction |
|---|---:|---:|---|---:|
| deterministic_top_m | 0.075 | 88 | transport_stable | 0.000 |
| deterministic_top_m | 0.10 | 88 | transport_stable | 0.000 |
| deterministic_top_m | 0.15 | 88 | transport_stable | 0.000 |
| top_m_m_minus_1 | 0.075 | 88 | transport_stable | 0.352 |
| top_m_m_minus_1 | 0.10 | 88 | transport_amplified_aligned | 0.523 |
| top_m_m_minus_1 | 0.15 | 88 | transport_stable | 0.455 |
| top_m_boundary_jitter | all tested | 264 | transport_stable | 0.000 |
| top_m_core_preserved_fringe_randomized | all tested | 264 | transport_stable | 0.000 |
| top_m_core_randomized_fringe_preserved | all tested | 264 | transport_stable | 0.000 |
| top_m_m_plus_1 | all tested | 264 | transport_stable | 0.000 |

## Edge Diagnostics

Compared against deterministic top-m calibration:

| sampler_family | selected-edge overlap vs top-m | response read |
|---|---:|---|
| deterministic_top_m | 1.000 | stable |
| top_m_boundary_jitter | 0.873-0.874 | stable |
| top_m_core_preserved_fringe_randomized | 0.664-0.668 | stable |
| top_m_core_randomized_fringe_preserved | 0.664-0.669 | stable |
| top_m_m_minus_1 | 0.750 | response-bearing |
| top_m_m_plus_1 | 1.000 | stable |

This argues against a simple selected-edge-overlap explanation. The `m+1`
variant retains all deterministic top-m edges and adds one near-boundary edge,
yet stayed stable. The `m-1` variant keeps a strict top-m subset and responded.

## Interpretation

The useful fork is now:

```text
strict pruning / low-rank edge pressure
```

not:

```text
hard deterministic top-m edge identity by itself
```

This is a stronger and more interesting constraint than the smoke result. It
also means the earlier deterministic-top-m positive should be treated as
design-set sensitive until reproduced or explained.

The current best hypothesis is that reducing out-degree while preserving the
lowest-energy rank core changes horizon transport in a way the detector can see.
That may be an instrument-relevant substrate mechanism, but it is not yet an
Omega-relevant result.

## Recommended Next Step

Do not broaden to MaxEnt yet. The next run should stay mechanistic and resolve
the pruning branch:

```text
strict-pruning ladder:
  m-2
  m-1
  m
  m+1
  m+2

controls:
  random m-1 deletion from top-m
  random m-1 deletion from all candidates
  lowest-rank-core m-1
  highest-rank-within-top-m deletion

required gates:
  paired baselines
  matched marginal nulls
  fixture contract
  full H128 horizon ladder
```

The immediate question is whether the signal is caused by lower out-degree
alone, removing the weakest top-m edge, preserving the strongest rank core, or
some interaction with the response taxonomy.

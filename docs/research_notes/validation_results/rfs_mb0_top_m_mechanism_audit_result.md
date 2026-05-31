# RFS-MB0 Hard Top-m Mechanism Audit Result

Status: small smoke completed  
Raw local output: `results/local_runs/20260601_top_m_mechanism_smoke/`  
Runner: `omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair`  
Spec: `docs/RFS_MB0_TOP_M_MECHANISM_AUDIT_SPEC.md`

## Executive Summary

The small hard-top-m mechanism smoke completed cleanly and passed the required plumbing gates:

```text
jobs_completed: 180 / 180
workers: 18
elapsed_seconds: 8.199
errors: 0
matrix_count: 720
detector_null_gate_passed: 1
detector_null_replicate_powered: 1
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract_passed: 1
paired_baseline_missing_rows: 0
readiness_level: top_m_mechanism_smoke_completed
next_action_fork: run_top_m_mechanism_medium
```

This was a workflow and mechanism-smoke result, not a theory validation result. The run used the primary `symbol_histogram_distance` invariant only, betas `0.075, 0.10, 0.15`, and horizon pairs `4->8`, `8->16`, `16->24`, and `24->32`.

## Sampler Response

Primary invariant only:

| sampler_family | response rows | dominant response | aligned fraction |
|---|---:|---|---:|
| deterministic_top_m | 96 | transport_stable | 0.125 |
| top_m_boundary_jitter | 96 | transport_stable | 0.000 |
| top_m_core_preserved_fringe_randomized | 96 | transport_stable | 0.000 |
| top_m_core_randomized_fringe_preserved | 96 | transport_stable | 0.000 |
| top_m_m_minus_1 | 96 | transport_stable | 0.208 |
| top_m_m_plus_1 | 96 | transport_stable | 0.000 |

By beta:

| sampler_family | beta | response rows | aligned fraction |
|---|---:|---:|---:|
| deterministic_top_m | 0.075 | 32 | 0.125 |
| deterministic_top_m | 0.10 | 32 | 0.250 |
| deterministic_top_m | 0.15 | 32 | 0.000 |
| top_m_m_minus_1 | 0.075 | 32 | 0.250 |
| top_m_m_minus_1 | 0.10 | 32 | 0.250 |
| top_m_m_minus_1 | 0.15 | 32 | 0.125 |
| top_m_boundary_jitter | all tested | 96 | 0.000 |
| top_m_core_preserved_fringe_randomized | all tested | 96 | 0.000 |
| top_m_core_randomized_fringe_preserved | all tested | 96 | 0.000 |
| top_m_m_plus_1 | all tested | 96 | 0.000 |

## Edge / Rank Diagnostics

Compared against deterministic top-m calibration:

| sampler_family | selected-edge overlap vs top-m | rank match error | energy match error | response read |
|---|---:|---:|---:|---|
| deterministic_top_m | 1.000 | 0.000 | 0.000 | reproduced aligned rows |
| top_m_boundary_jitter | 0.855-0.877 | 0.123-0.145 | 0.063-0.065 | stable |
| top_m_core_preserved_fringe_randomized | 0.657-0.689 | 0.311-0.343 | 0.188-0.228 | stable |
| top_m_core_randomized_fringe_preserved | 0.665-0.670 | 0.330-0.335 | 0.278-0.286 | stable |
| top_m_m_minus_1 | 0.750 | 0.000 | 0.107-0.120 | aligned rows present |
| top_m_m_plus_1 | 1.000 | 0.200 | 0.128-0.131 | stable |

## Interpretation

The smoke is underpowered for a final mechanism claim, but it is informative enough to justify a medium run.

The most interesting read is that `top_m_m_minus_1` preserved or strengthened aligned rows while `top_m_m_plus_1` did not. That points away from a simple "more deterministic top-m overlap is enough" explanation: `m+1` retains all top-m edges but stayed stable, while `m-1` keeps a strict subset and responded. The result is consistent with the response depending on sparse strict pruning, out-degree pressure, or a low-rank core effect rather than just selected-edge overlap.

Boundary jitter and the two core/fringe randomization probes stayed stable. At this smoke scale, disrupting near-boundary or core/fringe identity was enough to remove the observed response, but the `m-1` result means the next run should distinguish strict pruning from exact-edge identity.

## Recommended Next Step

Run a medium hard-top-m mechanism audit before any broad MaxEnt expansion:

```text
workers: 18
horizon pairs: full H128 ladder
betas: 0.075, 0.10, 0.15
groups/seeds: increase enough to exceed the smoke threshold
primary invariant: symbol_histogram_distance
required variants:
  deterministic_top_m
  top_m_m_minus_1
  top_m_m_plus_1
  top_m_boundary_jitter
  top_m_core_preserved_fringe_randomized
  top_m_core_randomized_fringe_preserved
extra if cheap:
  m-2 or fractional pruning control
  boundary-jitter window ladder
```

Treat `top_m_m_minus_1` as the current highest-priority branch, but do not interpret it as positive theory evidence until it survives the medium run with paired baselines, matched marginals, and fixture gates intact.

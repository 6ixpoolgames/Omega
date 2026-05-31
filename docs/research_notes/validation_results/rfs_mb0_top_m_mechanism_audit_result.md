# RFS-MB0 Hard Top-m Mechanism Audit Result

Status: upper-medium pruning-resolution sweep completed
Primary upper-medium output: `results/local_runs/20260601_top_m_pruning_resolution_upper_medium/`
Earlier smoke output: `results/local_runs/20260601_top_m_pruning_resolution_smoke/`
Prior medium output: `results/local_runs/20260601_top_m_mechanism_medium_dg12_v2/`
Runner: `omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair`
Spec: `docs/RFS_MB0_TOP_M_MECHANISM_AUDIT_SPEC.md`

## Executive Summary

The hard-top-m mechanism branch has resolved the previous strict-pruning fork
more sharply. The upper-medium sweep completed cleanly:

```text
jobs_completed: 38400 / 38400
workers: 18
elapsed_seconds: 748.307
errors: 0
matrix_count: 6600
detector_null_gate_passed: 1
detector_null_replicate_powered: 1
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract_passed: 1
paired_baseline_missing_rows: 0
readiness_level: top_m_weakest_edge_pruning_loadbearing
next_action_fork: expand_core_fringe_boundary_pruning_controls
```

This remains a substrate-mechanism result, not a theory validation result. The
run used the primary `symbol_histogram_distance` invariant, diagnostic
`hamming_weight_or_nonzero_count`, betas `0.075`, `0.10`, and `0.15`, and the
full H128 horizon ladder.

## Main Update

The prior medium sweep showed that deterministic top-m became stable on broader
design groups while `m-1` strict pruning stayed response-bearing. The
upper-medium pruning-resolution pass now narrows the read:

```text
deterministic_top_m:
  stable

top_m_m_minus_1 / top_m_drop_weakest_from_top_m:
  response-bearing, strongest at beta 0.10 and 0.15

top_m_m_minus_2:
  weaker aligned-amplification echo

top_m_m_plus_1 / top_m_m_plus_2:
  stable despite retaining all deterministic top-m edges

random deletion from top-m:
  stable

random m-1 from all local candidates:
  stable

drop strongest selected top-m edge:
  stable

near-tie jitter:
  stable
```

The best current interpretation is no longer generic lower out-degree. Random
deletion at the same effective degree stayed stable. The live mechanism is a
core/fringe boundary effect: remove the weakest selected top-m edge while
preserving the lowest-energy rank core.

Implementation note: `top_m_m_minus_1` and `top_m_drop_weakest_from_top_m`
are intentionally equivalent controls for the current `m=4` top-m rule. They
are retained under separate labels because the first names the out-degree
ladder and the second names the deletion mechanism.

## Sampler Response

Primary invariant only:

| sampler_family | response rows | dominant response | aligned fraction |
|---|---:|---|---:|
| deterministic_top_m | 264 | transport_stable | 0.000 |
| top_m_drop_strongest_from_top_m | 264 | transport_stable | 0.000 |
| top_m_drop_weakest_from_top_m | 264 | transport_amplified_aligned | 0.549 |
| top_m_m_minus_1 | 264 | transport_amplified_aligned | 0.549 |
| top_m_m_minus_2 | 264 | transport_stable | 0.273 |
| top_m_m_plus_1 | 264 | transport_stable | 0.000 |
| top_m_m_plus_2 | 264 | transport_stable | 0.000 |
| top_m_near_tie_jitter | 264 | transport_stable | 0.000 |
| top_m_random_delete_one_from_top_m | 264 | transport_stable | 0.000 |
| top_m_random_m_minus_1_from_all_local | 264 | transport_stable | 0.000 |

By beta:

| sampler_family | beta | response rows | dominant response | aligned fraction |
|---|---:|---:|---|---:|
| top_m_drop_weakest_from_top_m | 0.075 | 88 | transport_stable | 0.432 |
| top_m_drop_weakest_from_top_m | 0.10 | 88 | transport_amplified_aligned | 0.602 |
| top_m_drop_weakest_from_top_m | 0.15 | 88 | transport_amplified_aligned | 0.614 |
| top_m_m_minus_1 | 0.075 | 88 | transport_stable | 0.432 |
| top_m_m_minus_1 | 0.10 | 88 | transport_amplified_aligned | 0.602 |
| top_m_m_minus_1 | 0.15 | 88 | transport_amplified_aligned | 0.614 |
| top_m_m_minus_2 | 0.075 | 88 | transport_stable | 0.273 |
| top_m_m_minus_2 | 0.10 | 88 | transport_stable | 0.273 |
| top_m_m_minus_2 | 0.15 | 88 | transport_stable | 0.273 |

All other tested top-m controls had aligned fraction `0.000` for the primary
invariant at all tested betas.

## Edge Diagnostics

Compared against deterministic top-m calibration:

| sampler_family | selected-edge overlap vs top-m | selected-edge retention | response read |
|---|---:|---:|---|
| deterministic_top_m | 1.000 | 1.000 | stable |
| top_m_m_minus_1 / drop weakest | 0.750 | 1.000 | response-bearing |
| top_m_m_minus_2 | 0.500 | 1.000 | weak echo |
| top_m_drop_strongest_from_top_m | 0.750 | 1.000 | stable |
| top_m_random_delete_one_from_top_m | 0.750 | 1.000 | stable |
| top_m_m_plus_1 | 1.000 | 0.800 | stable |
| top_m_m_plus_2 | 1.000 | 0.667 | stable |
| top_m_near_tie_jitter | 0.747-0.866 | 0.747-0.866 | stable |
| top_m_random_m_minus_1_from_all_local | 0.297-0.305 | 0.396-0.407 | stable |

This argues against three simple explanations:

```text
hard deterministic top-m identity:
  deterministic_top_m stayed stable

generic lower out-degree:
  random deletion from top-m stayed stable

adding or retaining all top-m edges:
  m+1 and m+2 stayed stable
```

The response depends on which edge is removed, not merely how many edges remain.

## Interpretation

The current live mechanism is:

```text
weakest selected-edge pruning / core-fringe boundary pressure
```

The weaker `m-2` signal suggests a pruning-ladder echo, but the random-deletion
controls make plain capacity pressure less plausible as the main explanation.
The stable strongest-edge deletion is especially useful: preserving the weak
fringe while removing the best selected edge does not reproduce the effect.

This is still instrument/substrate anatomy. It does not license claims about
Omega, agency, identity, valuers, value, holdout readiness, or candidate
promotion.

## Recommended Next Step

Do not broaden to coupled frontier interaction yet. The next pass should stay
mechanistic and refine the boundary:

```text
core/fringe boundary controls:
  vary m and base out-degree target
  test weakest-edge deletion under additional design groups
  split response by horizon pair and perturbation family
  compare one-edge weakest deletion against two-edge weakest deletion
  keep paired baselines, matched marginal nulls, fixture gates, and H128
```

If that remains clean, the coupling primitive should be framed as a shared
successor/core-fringe boundary pressure rather than generic lower out-degree.

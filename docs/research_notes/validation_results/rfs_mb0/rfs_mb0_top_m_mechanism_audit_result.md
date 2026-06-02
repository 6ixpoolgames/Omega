# RFS-MB0 Hard Top-m Mechanism Audit Result

Status: boundary-resolution medium sweep completed
Primary output: `results/local_runs/20260601_top_m_boundary_resolution_medium_v2/`
Prior pruning-resolution output: `results/local_runs/20260601_top_m_pruning_resolution_upper_medium/`
Runner: `omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair`
Spec: `docs/specs/archive/rfs_mb0/RFS_MB0_TOP_M_MECHANISM_AUDIT_SPEC.md`

## Executive Summary

The hard-top-m mechanism branch has resolved the previous core/fringe-boundary
read more sharply. The medium boundary-resolution sweep completed cleanly:

```text
jobs_completed: 20160 / 20160
workers: 18
elapsed_seconds: 346.340
errors: 0
matrix_count: 6655
detector_null_gate_passed: 1
detector_null_replicate_powered: 1
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract_passed: 1
paired_baseline_missing_rows: 0
terminal_saturation_flagged_rows: 0
readiness_level: top_m_fixed_low_rank_core_loadbearing
next_action_fork: carry_shared_low_rank_core_boundary_forward
```

This remains a substrate-mechanism result, not a theory validation result. The
run used the primary `symbol_histogram_distance` invariant, betas `0.075`,
`0.10`, and `0.15`, explicit base `m` values `3,4,5`, and the full H128 horizon
ladder.

## Main Update

The prior pass suggested weakest selected-edge pruning. The new boundary pass
shows the cleaner pattern:

```text
strong response:
  baseline m=3
  m=4 with one weakest selected edge removed
  m=5 with two weakest selected edges removed

stable:
  baseline m=4
  baseline m=5
  m+1 expansion
  random one-edge deletion
  random two-edge deletion
  strongest-edge deletion
```

The useful read is therefore not "delete the weakest fringe" by itself and not
generic lower out-degree. It is:

```text
preserve exactly the low-energy top-3 core
```

The deletion variants responded only when they reduced the selected set to that
same low-rank core. Random deletion at the same effective degree stayed stable,
so the rank identity of the retained core matters.

## Boundary-Control Response

Primary invariant only:

| boundary control | base m | response rows | dominant response | aligned fraction | aligned rows |
|---|---:|---:|---|---:|---:|
| baseline_m | 3 | 264 | transport_amplified_aligned | 0.561 | 148 |
| baseline_m | 4 | 264 | transport_stable | 0.000 | 0 |
| baseline_m | 5 | 264 | transport_stable | 0.000 | 0 |
| drop_one_weakest | 3 | 264 | transport_stable | 0.288 | 76 |
| drop_one_weakest | 4 | 264 | transport_amplified_aligned | 0.561 | 148 |
| drop_one_weakest | 5 | 264 | transport_stable | 0.000 | 0 |
| drop_two_weakest | 3 | 156 | transport_stable | 0.000 | 0 |
| drop_two_weakest | 4 | 264 | transport_stable | 0.288 | 76 |
| drop_two_weakest | 5 | 264 | transport_amplified_aligned | 0.561 | 148 |
| random_drop_one | 3 | 260 | transport_stable | 0.223 | 58 |
| random_drop_one | 4 | 264 | transport_stable | 0.000 | 0 |
| random_drop_one | 5 | 264 | transport_stable | 0.000 | 0 |
| random_drop_two | 3 | 156 | transport_stable | 0.000 | 0 |
| random_drop_two | 4 | 264 | transport_stable | 0.000 | 0 |
| random_drop_two | 5 | 264 | transport_stable | 0.000 | 0 |
| drop_one_strongest | 3 | 264 | transport_stable | 0.174 | 46 |
| drop_one_strongest | 4 | 264 | transport_stable | 0.000 | 0 |
| drop_one_strongest | 5 | 264 | transport_stable | 0.000 | 0 |
| add_one_fringe | 3 | 264 | transport_stable | 0.000 | 0 |
| add_one_fringe | 4 | 264 | transport_stable | 0.000 | 0 |
| add_one_fringe | 5 | 264 | transport_stable | 0.000 | 0 |

Low-fraction rows below the dominant-response threshold should be treated as
weak echoes or taxonomy-sensitive residue, not as promotion evidence by
themselves.

## Horizon And Perturbation Split

Dominant amplified-aligned contexts occur mainly from `16->24` onward:

```text
16->24:   8 positive boundary-control/perturbation cells
24->32:   8
32->48:   8
48->64:   8
64->96:   8
96->128:  8
8->16:    3
```

The response appears under both perturbation families, but the small-edge
resample control is slightly broader:

```text
small_edge_resample_control:
  baseline m=3
  drop_one_weakest m=3 and m=4
  drop_two_weakest m=4 and m=5

asymmetric_edge_flip_control:
  baseline m=3
  drop_one_weakest m=4
  drop_two_weakest m=5
```

For coupled-frontier smoke, carry both perturbation families if cheap; if a
single family is needed, use `small_edge_resample_control` first.

## Interpretation

This pass rules against:

```text
generic lower out-degree:
  random deletion at matched effective degree stayed stable

weakest-edge deletion as a standalone mechanism:
  only weakest deletion that preserved the top-3 core became dominant-positive

expansion / retaining all top-m edges:
  m+1 expansion stayed stable
```

The current live mechanism is:

```text
fixed low-rank core boundary pressure
```

Operationally: the instrument sees horizon-transport response when the
transition relation preserves a compact strongest-rank successor core and
excludes the weak fringe. This is a plausible coupling primitive for the next
branch, but still only as substrate anatomy.

## Recommended Next Step

Stop single-frontier mechanism work unless the next branch contradicts this
read. Move to a coupled-frontier smoke using:

```text
coupling primitive:
  shared low-rank successor core / core-fringe boundary pressure

first target:
  retained top-3 core

horizon emphasis:
  16->24 through 96->128

perturbation emphasis:
  small_edge_resample_control first
  asymmetric_edge_flip_control as companion if affordable

required gates:
  paired baselines
  matched marginal nulls
  fixture contract
  no holdout
  no Omega / agency / value claims
```

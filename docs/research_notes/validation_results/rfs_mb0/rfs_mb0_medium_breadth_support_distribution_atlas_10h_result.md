# RFS-MB0 Medium-Breadth Support/Distribution Atlas 10h Result

Date: 2026-05-26

Primary local output:

```text
results/rfs_mb0_relation_atlas/20260525_medium_breadth_support_distribution_atlas_10h/
```

Primary report:

```text
results/rfs_mb0_relation_atlas/20260525_medium_breadth_support_distribution_atlas_10h/medium_breadth_support_distribution_atlas_report.md
```

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_MEDIUM_BREADTH_SUPPORT_DISTRIBUTION_ATLAS_10H_SPEC.md
```

## Run Shape

```text
workers requested: 18
anchors selected: 16
fresh_seeds_per_variant: 5
start_samples: 3, 8, 16
horizons: 0, 1, 2, 4, 8, 12, 16, 24, 32
sweep jobs requested: 21840
sweep jobs completed: 21840
sweep rows completed: 1769040
rank/effect rows: 39424
errors: 0
wall_clock_seconds: 26700.2
promotion_enabled: false
```

This used about 7.4 hours of the available 10-hour wall-clock budget.

## Headline

The expanded atlas was technically successful, but scientifically conservative.

Atlas band classes:

```text
near_miss_transition_band: 10
stable_fakeout_band: 6
stable_candidate_band: 0
```

Transition classes:

```text
saturation_boundary: 124
candidate_to_fakeout_transition: 78
probe_resolution_boundary: 6
fakeout_to_candidate_transition: 0 in the transition graph
```

Fresh-seed confirmation:

```text
seed_recurrent: 198
seed_fragile_or_absent: 10
```

## Interpretation

The support/distribution branch still has surface area, but the broader run did
not preserve the stronger local-sweep signal as stable candidate bands. The most
honest read is:

```text
near-miss and boundary structure recurs
stable cross-probe candidate bands did not generalize
saturation boundaries dominate the transition map
probe recurrence remains weak
```

Candidate retention rates stayed below stable-band thresholds. The strongest
candidate-rate bands were associated with:

```text
asymmetry_strength: 0.1785
baseline neighborhoods: 0.1782
constraint_change_weight: 0.1663
constraint_strength: 0.1543
constraint_density: 0.1317
out_degree_target: 0.1209
reversibility_fraction: 0.0951
```

These are not validation claims. They are map coordinates for a possible second
local sweep or for a measurement-limits writeup.

## Incomplete Piece

The spec requested limited n=6 transfer. This implementation emitted
`n6_transfer_summary.csv`, but the transfer itself was not run:

```text
transfer_status: not_run
reason: current expanded run used n=5 local neighborhoods; n=6 transfer remains a follow-up allocation
```

If we continue, n=6 transfer should be implemented explicitly rather than hidden
inside the n=5 atlas runner.

## Recommended Next Step

Recommended next step:

```text
broader_atlas_or_second_local_sweep
```

My stricter interpretation is:

```text
second local sweep or measurement-limits note before a broader atlas
```

Rationale: the run found recurring near-miss/boundary behavior, but not stable
candidate bands. The next move should narrow on saturation/probe-resolution
boundaries and test whether any band can become cross-probe recurrent.

## Claim Boundary

Allowed conclusion:

```text
The guided atlas maps recurring near-miss, saturation-boundary, and
probe-resolution-boundary behavior under support/distribution controls.
```

Not allowed:

```text
Omega detected
agency detected
identity detected
valuer detected
viability detected
path-process object detected
scientific gate passed
```

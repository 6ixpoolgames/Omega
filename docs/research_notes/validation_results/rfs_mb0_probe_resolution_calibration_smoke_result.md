# RFS-MB0 Probe Resolution Calibration Smoke Result

Date: 2026-05-25

Primary local output:

```text
results/rfs_mb0_relation_atlas/20260525_probe_resolution_calibration_smoke/
```

Primary report:

```text
results/rfs_mb0_relation_atlas/20260525_probe_resolution_calibration_smoke/probe_resolution_calibration_report.md
```

Spec:

```text
docs/RFS_MB0_PROBE_RESOLUTION_CALIBRATION_SPEC.md
```

## Run Shape

```text
workers requested: 18
jobs queued: 288
jobs completed: 288
errors: 0
candidate environments: 8
start_samples: 3
path_horizons: 4, 8
sample_paths_per_start: 256
path_null_replicates: 3
promotion_enabled: false
wall_clock_seconds: 5.0
```

Probe families included existing low-resolution probes, coordinate tuple probes,
composite probes, constraint-profile probes, relation-role probes, and strict
state controls.

## Headline

The probe-resolution bottleneck is real. Existing low-resolution probes remain
too collision-prone for path-language interpretation. The first neutral
medium-resolution probes reduce collision, especially `coordinate_tuple_k4` and
the equivalent `composite_two_pairs`, but matched controls still often show the
same path metrics. This is not enough for path-process promotion.

Branch recommendation:

```text
B. Downgrade path-process for now and focus on support/distribution deformation taxonomy.
```

This does not mean path metrics are useless. It means they are not yet clean
evidence under the current substrate/probe setup.

## Key Counts

Candidate evidence levels:

```text
probe_resolution_fail_collision: 57
probe_resolution_fail_support_ceiling: 3
probe_resolution_identity_like_only: 47
probe_resolution_pass: 24
probe_resolution_pass_but_control_also_passes: 13
```

Fakeout counts:

```text
probe_collision_fakeout: 114
support_ceiling_fakeout: 106
matched_control_also_passes: 56
low_alphabet_fakeout: 2
underdetermined_path_metric: 116
```

## Probe Resolution Summary

Too collision-prone or otherwise unusable in this smoke:

```text
existing_low__pairwise_equality_indicator
existing_low__pairwise_ordered_projection
constraint_profile_hash
constraint_violation_count
relation_role
```

Usable low-resolution / borderline families:

```text
composite_local_window_plus_constraint_count
constraint_violation_count_plus_local_tuple
```

Medium-resolution families worth retaining only as calibrated diagnostics:

```text
coordinate_tuple_k4
composite_two_pairs
```

Identity-like controls:

```text
full_state_hash
full_state_strict
```

## Interpretation

The prior path-metric failure was not just an implementation artifact. The
existing probes collapse too much of the finite state space, and low-resolution
path language can manufacture recurrence-looking structure. Increasing probe
resolution helps, but the candidate/control separation remains weak and
inconsistent. Several rows that look strong by path null rank are neutralized
by matched controls.

The right move is not to scale this branch immediately. Keep the calibrated
probe machinery, but re-center near-term empirical work on support and
distribution deformation, where the relation-generator branch has shown more
stable structure.

## Claim Boundary

Allowed conclusion:

```text
Probe resolution materially affects path metric interpretability, and current
path-process evidence is not clean enough for promotion.
```

Not allowed:

```text
Omega detected
agency detected
path-process object detected
scientific gate passed
```

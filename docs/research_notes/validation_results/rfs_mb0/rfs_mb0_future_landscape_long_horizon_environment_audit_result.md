# RFS-MB0 Future Landscape Long-Horizon Environment Audit Result

Date: 2026-05-23

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_FUTURE_LANDSCAPE_LONG_HORIZON_ENVIRONMENT_AUDIT.md
```

Primary result directory:

```text
results/rfs_mb0_future_landscape/20260523_long_horizon_100x/
```

## Purpose

This run kept the current RFS-MB0 future-landscape substrate fixed and extended
the horizon grid to test whether the detector was failing because H16 ended too
early.

The audit asked whether longer horizons reveal delayed future-landscape
structure, expose saturation timing, separate control artifacts, or show that
the current environment design is not resolving the intended object.

## Implementation

The future-landscape runner now supports explicit horizon grids:

```text
dense_early
long_5x
long_10x
long_100x
custom --horizons
```

The primary run used `long_100x`:

```text
0,1,2,3,4,5,6,7,8,10,12,16,24,32,48,64,80,96,128,160,224,320,512,768,1024
```

New audit outputs include:

```text
horizon_local_profiles.csv
horizon_local_nulls.csv
horizon_window_summary.csv
aggregate_window_classes.csv
saturation_onset_by_family.csv
viscosity_diagnostics.csv
long_horizon_status.json
```

## Runs

Debug run:

```text
results/rfs_mb0_future_landscape/debug_long_horizon_5x/
families: structured_relation, degree_preserving_control, random_relation_control
seeds_per_family: 1
workers: 4
status: COMPLETED
errors: 0
elapsed: about 47 seconds
```

Initial audit run:

```text
results/rfs_mb0_future_landscape/20260523_long_horizon_5x/
systems: 33
profiles: 3696
workers: 18
status: COMPLETED
errors: 0
elapsed: about 72 seconds
```

Primary stretched audit:

```text
results/rfs_mb0_future_landscape/20260523_long_horizon_100x/
systems: 33
profiles: 3696
workers: 18
status: COMPLETED
errors: 0
elapsed: about 381 seconds
```

## Primary Read

The long-horizon audit did not produce an aggregate scientific pass.

Primary status:

```text
aggregate_structured_family_count: 0
degree_control_local_false_positive_count: 0
degree_control_probe_family_aggregate_passes: 0
status: COMPLETED
errors: 0
```

Family-level classes:

```text
structured_relation: saturation_dominated
expanding_relation: saturation_dominated
degree_preserving_control: control_no_pass
random_relation_control: control_no_pass
coordinate_permutation_control: control_no_pass
fixed_point_control: control_no_pass
phase_cycle_control: control_no_pass
permissive_probe_control: control_no_pass
strict_probe_control: control_no_pass
contracting_relation: underdetermined
cyclic_relation: underdetermined
```

Saturation timing was decisive for the nominal structured families:

```text
structured_relation saturates by about H7
expanding_relation saturates by about H10
random_relation_control saturates by about H5
coordinate_permutation_control saturates by about H7
degree_preserving_control does not fully saturate through H1024
```

The viscosity diagnostic does not support "the horizon was simply too short."
Transition information and separation generally appear immediately at H1, and
the audit did not reveal a delayed long-horizon onset.

Window-local candidate patterns do appear in early/pre-saturation windows, but
they are not clean enough to promote. Similar window-local structure appears in
controls, so the local detector remains diagnostic rather than dispositive.

## Interpretation

This is a useful negative result.

The current detector discipline is behaving conservatively:

- saturated families are withheld;
- control families do not pass the aggregate gate;
- degree-preserving controls no longer promote local hits to aggregate claims;
- long horizons do not reveal a hidden delayed object.

The failure now localizes more strongly to substrate/environment design and
probe/null resolution, not to compute budget or a horizon cutoff at H16.

## Recommendation

Do not scale this exact substrate into a longer overnight run.

The next useful work should either:

- redesign environment families so nominal structured cases remain
  non-saturated for meaningful horizon windows;
- strengthen window-level controls before treating early/pre-saturation windows
  as evidence;
- introduce a different neutral substrate whose reachable-future landscape is
  not dominated by rapid exhaustion, clocks, collapse, or trivial controls.

The current long-horizon machinery should be kept. It is a good diagnostic
layer for the next substrate, but this substrate does not yet resolve the
target object.

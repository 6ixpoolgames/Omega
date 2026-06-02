# RFS-MB0 Future Landscape Detector v1 Smoke Result

Date: 2026-05-23

Status: detector v1 implemented; smoke passed; scientific gate not passed

Result directory:

```text
results/rfs_mb0_future_landscape/20260523_detector_v1_smoke_conservative/
```

Primary summary:

```text
results/rfs_mb0_future_landscape/20260523_detector_v1_smoke_conservative/summary.md
```

## Purpose

This run implements the detector revision specified in:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_FUTURE_LANDSCAPE_DETECTOR_V1_HANDOFF.md
```

The purpose was to preserve the v0 heuristic detector as a known-overcalling baseline, then add a more conservative control-relative detector that depends on matched-null comparison rather than absolute thresholds.

## Implementation

Updated:

```text
omega/rfs_mb0_future_landscape/probes.py
omega/rfs_mb0_future_landscape/controls.py
omega/rfs_mb0_future_landscape/detectors.py
omega/rfs_mb0_future_landscape/landscape.py
omega/rfs_mb0_future_landscape/run_smoke.py
```

New v1 additions:

```text
mechanically generated probes
transition-level signature mutual information
transition conditional entropy
transition entropy-rate proxy
transition grammar-size proxy
transition motif-reuse proxy
random / degree / probe-marginal null bundle
control-relative profile class
saturation diagnostics
```

New output files:

```text
transition_information.csv
probe_summary.csv
null_bundle_summary.csv
control_relative_profile_classes.csv
saturation_summary.csv
```

The old v0 detector is preserved as:

```text
heuristic_profile_class_v0
```

and the v1 detector is reported as:

```text
control_relative_profile_class_v1
```

## Run Shape

```text
systems: 33
future profiles: 3696
families: 11
seeds per family: 3
workers: 18
errors: 0
status: COMPLETED
elapsed: about 44 seconds
```

The larger profile count comes from mechanical probe enumeration at `sigma = 2`.

## Main Read

The implementation gate passed.

The v1 detector is meaningfully stricter than v0:

```text
random_relation_control:
  v1 = saturation_dominated

coordinate_permutation_control:
  v1 = saturation_dominated

expanding_relation:
  v1 = saturation_dominated

structured_relation:
  v1 = saturation_dominated
```

This is the correct conservative behavior because these families saturate the reachable state space in the present finite substrate:

```text
structured_relation reach saturation: 1.000
expanding_relation reach saturation: 1.000
random_relation_control reach saturation: 0.997
coordinate_permutation_control reach saturation: 1.000
```

Without saturation-matched nulls, these should not be called structured.

## Remaining Failure

The scientific gate still does not pass.

The degree-preserving control still produces v1 `structured_propagation` calls:

```text
degree_preserving_control:
  null_mimic: 233
  saturation_dominated: 136
  structured_propagation: 39
```

This is narrower than the v0 failure, but still a real false-positive problem. The current control-relative rule is not yet strong enough against degree-preserving rewiring.

## Gate Status

```text
Mechanically generated probes:
  passed

Transition-level information measures:
  passed

Matched null bundle:
  passed, minimal version

Saturation diagnostics:
  passed

v0 heuristic preserved:
  passed

Random control no longer called structured:
  passed

Saturated structured/relation families withheld:
  passed

Degree-preserving false positives eliminated:
  not passed

Structured future-landscape separation:
  not established
```

## Recommendation

Do not scale yet.

The next revision should focus on the degree-preserving failure mode. Good targets:

1. Add frontier-size-preserving and saturation-matched nulls.
2. Require separation from degree controls at the family/probe-family level, not only per-profile pass counts.
3. Add control-relative ranks by probe family so pairwise ordered projections cannot dominate the decision.
4. Consider making `structured_propagation` a family-level label rather than an individual profile label.

The current v1 result is useful because it moved the failure from broad overcalling to a specific matched-control failure.

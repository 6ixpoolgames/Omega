# RFS-MB0 Deformation Detector Sweep Small Result

Date: 2026-05-25

Primary local output:

```text
results/rfs_mb0_relation_atlas/20260525_deformation_detector_sweep_small/
```

Validation output:

```text
results/rfs_mb0_relation_atlas/20260525_deformation_detector_sweep_validation/
```

Primary report:

```text
results/rfs_mb0_relation_atlas/20260525_deformation_detector_sweep_small/deformation_detector_upgrade_report.md
```

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_DEFORMATION_DETECTOR_AND_LOCAL_SWEEP_SPEC.md
```

## Run Shape

Validation pass:

```text
anchors: 6
fresh_seeds_per_variant: 1
start_samples: 3
horizons: 0,1,2,4,8
workers: 18
sweep jobs completed: 96
errors: 0
```

Small scaled pass:

```text
anchors: 12
fresh_seeds_per_variant: 2
start_samples: 3,8
horizons: 0,1,2,4,8,12,16,24
workers: 18
sweep jobs completed: 576
sweep rows completed: 25344
rank/effect rows: 39424
errors: 0
wall_clock_seconds: 77.7
promotion_enabled: false
```

Path metrics remained parked and did not drive classification.

## Headline

Validation is technically green, and the small scaled pass found local transition
geometry worth following.

Transition classes:

```text
candidate_stable_region: 3
fakeout_to_candidate_transition: 2
candidate_to_fakeout_transition: 7
saturation_boundary: 10
probe_resolution_boundary: 2
```

Recommended next step:

```text
proceed_to_medium_breadth_atlas
```

## Detector Upgrade

The new detector layer writes:

```text
matched_control_bundle.csv
deformation_rank_effect_summary.csv
deformation_margin_sensitivity.csv
support_vs_distribution_separation.csv
```

The upgraded scoring tracks:

```text
candidate-control rank/effect sizes
margin sensitivity over 0.00, 0.01, 0.02, 0.05, 0.10
support-only versus distribution-given-support separation
fakeout penalties and boundary classes
```

## Local Sweep Readout

The small pass selected both candidate and fakeout anchors. Candidate anchors
were mostly knife-edge at the whole-anchor level, but local transition graph
rows included stable candidate regions. Fakeout anchors were not simply dead:
matched-control-equivalent, support-ceiling-limited, and probe-collision-limited
anchors all produced near-miss/fakeout-to-candidate behavior in local variants.

This does not validate the theory, but it does justify a medium-breadth atlas
around the observed local bands rather than another blind sweep.

## Claim Boundary

Allowed conclusion:

```text
The upgraded detector and local sweep workflow works, and local support/
distribution transition geometry is present in the tested neighborhoods.
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

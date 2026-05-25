# RFS-MB0 Support/Distribution Deformation Taxonomy Smoke Result

Date: 2026-05-25

Primary local output:

```text
results/rfs_mb0_relation_atlas/20260525_support_distribution_taxonomy_smoke/
```

Primary report:

```text
results/rfs_mb0_relation_atlas/20260525_support_distribution_taxonomy_smoke/support_distribution_taxonomy_report.md
```

Spec:

```text
docs/RFS_MB0_SUPPORT_DISTRIBUTION_DEFORMATION_TAXONOMY_SPEC.md
```

## Run Shape

```text
workers requested: 18
jobs requested: 288
jobs completed: 288
metric rows completed: 11088
errors: 0
candidate environments selected: 8
start_samples: 3, 8
horizons: 0, 1, 2, 4, 8, 12, 16
promotion_enabled: false
wall_clock_seconds: 30.5
```

This was intentionally a support/distribution run. Path metrics remain parked as
an open thread and did not drive classification.

## Headline

The support/distribution branch is worth continuing, but this smoke is mostly a
control-typing result rather than a strong candidate result.

Candidate summary classes:

```text
matched_control_equivalent: 92
probe_collision_limited: 12
support_ceiling_limited: 7
mixed_support_distribution_candidate: 7
support_deformation_candidate: 2
identity_like_control: 4
underdetermined: 4
```

The candidate-like rows are concentrated in:

```text
coordinate_tuple_k3
coordinate_tuple_k4
constraint_profile_hash
constraint_violation_count_plus_local_tuple
```

## Interpretation

The branch pivot is technically sound. We can now classify support and
distribution deformation with matched controls, start recurrence, probe
diagnostics, mechanism tags, and a preliminary regime map.

The scientific readout is still conservative:

```text
matched controls explain most candidate rows
probe collision and support ceilings remain common
a small set of support/mixed deformation candidates survives as a target for a broader follow-up
```

Recommended next focus:

```text
continue support/distribution taxonomy
```

but broaden the parameter/regime pool rather than returning to path metrics
immediately.

## Implementation Notes

Added:

```text
omega/rfs_mb0_future_landscape/run_support_distribution_taxonomy.py
```

The runner writes the required output contract:

```text
support_distribution_taxonomy_report.md
support_distribution_candidate_summary.csv
support_distribution_metric_by_horizon.csv
support_distribution_metric_by_window.csv
support_distribution_matched_controls.csv
support_distribution_probe_diagnostics.csv
support_distribution_start_recurrence.csv
support_distribution_regime_map.csv
support_distribution_fakeout_summary.csv
support_distribution_mechanism_tags.csv
status.json
```

One workflow issue was caught and repaired during smoke testing:

```text
checkpoint writes were mutating in-memory fakeout labels, inflating fakeout counts.
```

The final runner now keeps matched-control labeling idempotent across checkpoint
writes.

## Claim Boundary

Allowed conclusion:

```text
The support/distribution taxonomy workflow is operational, and a small set of
candidate-like deformation rows remains after matched controls.
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

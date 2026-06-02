# RFS-MB0 Path Metric Calibration Smoke Result

Date: 2026-05-25

Specs:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_PATH_PROCESS_DIAGNOSTIC_SPEC.md
docs/specs/archive/rfs_mb0/RFS_MB0_PATH_PROCESS_DIAGNOSTIC_ADDENDUM_METRIC_CALIBRATION.md
docs/specs/archive/rfs_mb0/RFS_MB0_PATH_METRIC_CALIBRATION_SMOKE_TIGHTENING.md
```

Local output:

```text
results/rfs_mb0_relation_atlas/20260525_path_metric_calibration_smoke/
```

## Purpose

This was a path metric calibration smoke, not a path-process detection run. Promotion was disabled.

The goal was to verify that the runner can produce path metrics, matched controls, probe-collision diagnostics, path-null ranks, effect sizes, and fakeout classes without over-promoting raw path-language structure.

## Implementation

Added:

```text
omega/rfs_mb0_future_landscape/run_path_metric_calibration.py
```

The runner consumes the latest phenotype-repair artifacts, selects candidate rows, attaches matched non-candidate controls where possible, samples path-signature sequences, computes n-gram metrics, runs endpoint/unigram path nulls, and writes fakeout-first outputs.

Minimum required outputs were produced:

```text
path_metric_calibration_report.md
path_metric_calibration_summary.csv
path_fakeout_summary.csv
probe_collision_diagnostics.csv
matched_non_candidate_path_controls.csv
path_null_rank_summary.csv
path_metric_effect_sizes.csv
status.json
```

## Run Shape

```text
workers requested: 18
jobs queued: 32
jobs completed: 32
errors: 0
candidate rows: 14
matched-control rows: 14
same-environment window-control rows: 4
path_horizons: 4, 8
sample_paths_per_start: 256
path_null_replicates: 3
promotion_enabled: false
```

The run finished in about one second because path sampling on the existing n=5 relation systems is cheap relative to atlas generation.

## Headline Result

All candidate rows remained descriptive:

```text
path_descriptive: 14/14 candidate rows
```

Fakeout counts across all rows:

```text
probe_collision_fakeout: 32
support_ceiling_fakeout: 30
matched_control_also_passes: 2
```

Probe collision was extreme:

```text
mean probe_collision_rate: 0.963
min: 0.963
max: 0.967
```

## Matched-Control Read

Candidate rows all had matched controls.

Most candidate rows had higher bigram mutual information than the selected matched control, but the effect is not interpretable as path-process structure because probe collision and support-ceiling fakeouts dominate.

Examples:

```text
candidate_minus_control ranged from about -0.147 to +0.537
matched_control_also_passes occurred on 2 rows
```

Endpoint and unigram path-null ranks were high for candidate rows:

```text
mean endpoint_bigram_mi_rank: 1.0
mean unigram_bigram_mi_rank: 1.0
```

This is not a positive. In this smoke, high null ranks coexist with severe probe-collision fakeouts, which means the path nulls are not sufficient by themselves.

## Interpretation

The smoke succeeded as a calibration audit.

It shows that raw path metrics and simple endpoint/unigram path nulls are too permissive unless probe resolution is handled first. The pairwise projection probes used here collapse a 243-state system into a tiny signature alphabet, so recurrence and bigram structure are cheap.

The immediate blocker is:

```text
probe collision / low effective path alphabet
```

not absence of path organization.

## Claim Boundary

This run does not detect a path-process object, Omega, agency, identity, value, viability, or a scientific gate.

Allowed interpretation:

```text
The initial path metric runner works, but the first calibration smoke demotes all candidate rows to descriptive due to probe-collision and support-ceiling fakeouts.
```

## Recommendation

Do not scale this exact path metric setup yet.

Next technical step:

```text
Add higher-resolution probe families and/or strict-state probe controls, then rerun calibration.
```

Specific repairs:

- diversify candidate selection across probe families instead of letting pairwise ordered projections dominate;
- include higher-arity or composite probes to reduce collision;
- report matched-control effects separately by probe family;
- add low-out-degree/path-count matched controls;
- keep promotion disabled until some rows clear probe-collision and matched-control fakeouts.

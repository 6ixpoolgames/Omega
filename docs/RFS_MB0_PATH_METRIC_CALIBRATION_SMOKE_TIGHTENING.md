# RFS-MB0 Path Metric Calibration Smoke Tightening

Status: implementation tightening after Codex review of path/process addendum

Purpose: make the first path run explicitly calibration-only, with mandatory matched controls and no promotion to path-process candidate status.

This note supplements:

```text
docs/RFS_MB0_PATH_PROCESS_DIAGNOSTIC_SPEC.md
docs/RFS_MB0_PATH_PROCESS_DIAGNOSTIC_ADDENDUM_METRIC_CALIBRATION.md
```

## 0. Core framing

Codex agrees with the revised framing:

```text
Do not run a path/process detection pass yet.
Run a path metric calibration audit first.
```

Raw path-language structure is expected in constrained finite graphs. Therefore the useful question is not:

```text
Do candidate paths have bigrams, trigrams, recurrence, entropy reduction, or compression?
```

The useful question is:

```text
Do the proposed path metrics discriminate candidates from matched fakeouts and non-candidates?
```

## 1. Promotion disabled for first run

For the first calibration smoke, do not emit `path_process_candidate` as an active class.

Allowed labels:

```text
path_descriptive
path_above_endpoint
path_above_unigram
path_above_candidate_selection
path_probe_local
path_start_local
path_fakeout
underdetermined
```

If a row appears to satisfy stronger criteria, write:

```text
provisional_path_process_blocked_by_calibration_policy
```

or:

```text
would_promote_if_enabled = 1
```

but do not promote it.

The first run should calibrate the metrics, not declare path-process positives.

## 2. Matched controls are mandatory

No candidate-only path metrics.

Every candidate path row must have at least one matched middle-regime non-candidate control row.

If no matched control exists, the row must be marked:

```text
descriptive_only_no_matched_control
```

and cannot receive any class stronger than:

```text
path_descriptive
```

Matching should use, as available:

```text
parameter region
state count
out-degree target
constraint density
constraint strength
asymmetry strength
reversibility fraction
roughness strength
start_samples
horizon window
probe family
```

Required output columns:

```text
matched_control_environment_id
matched_control_match_quality
candidate_metric
matched_control_metric
candidate_minus_control
candidate_control_effect_size
candidate_control_rank
```

## 3. Probe collision diagnostics are first-class

Every path metric row must include probe-resolution fields:

```text
probe_signature_alphabet_size
observed_signature_support_size
observed_signature_support_fraction
probe_collision_rate
unigram_entropy_ceiling
bigram_possible_count
bigram_observed_count
bigram_observed_fraction
trigram_possible_count
trigram_observed_count
trigram_observed_fraction
```

Automatic demotion:

```text
If probe_collision_rate is high, or effective alphabet/support is too small,
then demote any path evidence to probe_collision_fakeout unless matched-control
effect size remains strong and the result appears in another probe family.
```

Add flags:

```text
probe_collision_fakeout_flag
low_alphabet_fakeout_flag
support_ceiling_fakeout_flag
```

## 4. Headline output must be fakeout-first

The primary report should be:

```text
path_metric_calibration_report.md
```

not:

```text
path_process_candidate_summary.md
```

The report should lead with:

```text
fakeout counts
matched-control discriminability
probe collision rates
path metric effect sizes
calibration failures
```

Then, only after those, list any provisional interesting rows.

## 5. First smoke run shape

Use a deliberately small calibration smoke.

Recommended:

```text
candidate environments: 6-10
matched non-candidate controls: 6-10
start_samples: 3
path_horizons: 4, 8
sample_paths_per_start: 256
path null replicates: 3
workers: 18
queued jobs: at least 18
wall clock: 20-40 minutes
```

If fewer than 18 jobs are naturally produced, parallelize across:

```text
candidate/control environments
probe families
start groups
path null replicates
roughness replay jobs, if included
```

## 6. Minimum outputs for smoke

Required:

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

Optional in smoke:

```text
same_environment_window_controls.csv
path_roughness_sensitivity_summary.csv
path_process_candidate_summary.csv
```

If `path_process_candidate_summary.csv` is written, it must be clearly marked provisional and promotion-disabled.

## 7. Required fakeout classes

At minimum classify:

```text
probe_collision_fakeout
endpoint_support_fakeout
unigram_marginal_fakeout
low_outdegree_path_fakeout
matched_control_also_passes
start_local_path_fakeout
cycle_or_saturation_path_fakeout
candidate_selection_fakeout
underdetermined_path_metric
```

## 8. Smoke success criteria

The smoke succeeds if it answers:

```text
Can the runner produce path metrics, matched controls, fakeout classes, and probe-collision diagnostics cleanly?
Are path metrics obviously too permissive on matched controls?
Which fakeout modes dominate?
Are any metrics worth scaling?
```

The smoke does not need to find an interesting candidate.

A result with zero provisional positives is acceptable and likely useful.

## 9. Claim boundary

Allowed after the smoke:

```text
We calibrated initial path metrics against matched controls and fakeout diagnostics.
Path metrics appear too permissive / partially discriminative / promising under specified comparisons.
```

Not allowed:

```text
path-process object detected
Omega detected
agency detected
identity detected
valuer detected
viability detected
scientific gate passed
```

## 10. Bottom line

For the first path run:

```text
matched controls mandatory
promotion disabled
probe collision first-class
fakeouts headline the report
small smoke before scale
```

This makes the path/process branch scientifically safer and prevents the original detector-overcall failure from reappearing at the path-language layer.

# RFS-MB0 Path/Process Diagnostic Addendum: Metric Calibration and Fakeout Controls

Status: addendum to `docs/specs/archive/rfs_mb0/RFS_MB0_PATH_PROCESS_DIAGNOSTIC_SPEC.md`

Purpose: address the concern that path metrics may be too permissive. This addendum changes the next run from a path-process detection run into a path-metric calibration audit.

## 0. Immediate correction

Do not treat raw path-language metrics as evidence of path-process structure.

A constrained finite graph will almost always produce:

```text
repeated bigrams
repeated trigrams
lower path entropy
apparent compression
forbidden words
motif reuse
```

Those facts alone are not interesting.

The next run should answer:

```text
Are the proposed path metrics discriminative after matched controls,
probe-collision checks, and fakeout classification?
```

not:

```text
How many candidates pass path-process criteria?
```

## 1. Rename the run objective

Treat the next pass as:

```text
path metric calibration audit
```

not:

```text
path-process detection run
```

The headline output should be:

```text
path_metric_calibration_report
```

not:

```text
path_process_candidate_count
```

Candidate promotion is allowed only if comparative checks are strong. The expected useful result may be a fakeout taxonomy rather than a positive path-process signal.

## 2. Why path metrics are risky

Path metrics are at high risk of overcalling because:

```text
1. finite graphs naturally repeat path words;
2. low out-degree mechanically increases predictability;
3. constraint-dominated generators naturally reduce entropy;
4. small probe alphabets create collisions and fake recurrence;
5. endpoint support restriction mechanically restricts path language;
6. saturation and cycles create strong but trivial n-gram structure;
7. selecting candidate windows first creates winner's-curse effects;
8. roughness or top-k boundaries can create brittle path differences;
9. matched middle-regime non-candidates may show similar path statistics.
```

Therefore raw bigram/trigram recurrence, entropy reduction, or compression proxy is descriptive only.

## 3. Required interpretation ladder

Path evidence must be reported in levels.

```text
path_descriptive:
  raw n-gram recurrence, entropy reduction, or compression proxy observed

path_above_endpoint:
  path metric exceeds endpoint-support matched and unigram-marginal path nulls

path_above_branching:
  path metric exceeds out-degree/path-count matched controls

path_above_candidate_selection:
  path metric exceeds matched non-candidate middle-regime environments

path_recurrent:
  path phenotype recurs across starts, probe families, roughness replays, and fresh seeds where available

path_process_candidate:
  candidate clears the above checks, but remains diagnostic only
```

Only `path_recurrent` and `path_process_candidate` should be treated as strong diagnostic classes.

## 4. Required matched comparisons

Every candidate path metric must be compared against matched controls.

### 4.1 Matched non-candidate environments

For every candidate environment/window/probe family, include a matched non-candidate middle-regime environment with similar:

```text
parameter region
state count
out-degree target
constraint density
constraint strength
asymmetry strength
reversibility fraction
roughness strength
start count
horizon window
probe family
```

Report:

```text
candidate_minus_matched_control
candidate_to_control_rank
candidate_control_effect_size
```

The core comparison is:

```text
candidate path metric - matched non-candidate path metric
```

not the raw path metric.

### 4.2 Same-environment non-candidate windows

Where available, compare candidate windows against non-candidate windows in the same environment.

This controls for generator-specific path regularity.

### 4.3 Same-probe shuffled paths

Shuffle temporal order while preserving path length and observed signatures.

This controls for simple signature frequency effects.

### 4.4 Endpoint-support matched path randomization

Preserve endpoint signature support and path length/count but randomize path order.

Question:

```text
Given the same reachable endpoint signatures, is the temporal/path language organized?
```

### 4.5 Unigram-marginal path shuffle

Preserve path-level signature unigram counts but destroy order.

Question:

```text
Is the signal only path-marginal signature frequency?
```

### 4.6 Bigram-support matched trigram test

Preserve which bigrams occur, then test whether trigram/higher-order continuation structure remains non-null.

Question:

```text
Is there structure beyond one-step transition support?
```

### 4.7 Low-out-degree / path-count matched control

Low out-degree makes path predictability cheap. Include controls matched on:

```text
out-degree
sampled path count
effective branch factor
frontier size by H
```

## 5. Probe collision diagnostics are mandatory

Every path metric row must include probe-resolution diagnostics.

Required columns:

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

If probe collision is high, path recurrence is cheap.

Add flags:

```text
probe_collision_fakeout_flag
low_alphabet_fakeout_flag
support_ceiling_fakeout_flag
```

Do not call a candidate path-process-like if the signal is explained by probe collision.

## 6. Fakeout taxonomy

The next run must explicitly classify false-positive modes.

Add path fakeout classes:

```text
cycle_path_fakeout
low_outdegree_path_fakeout
probe_collision_fakeout
endpoint_support_fakeout
saturation_path_fakeout
candidate_selection_fakeout
roughness_path_fragile
start_local_path_fakeout
matched_control_also_passes
underdetermined_path_metric
```

These are useful results, not mere failures.

The project wants to know:

```text
What looks like it cares, but does not actually sustain future-oriented structure?
```

## 7. Conservative promotion rule

Do not promote from path_descriptive to path_process_candidate unless all are true:

```text
1. not cycle/saturation dominated;
2. not explained by probe collision;
3. not explained by endpoint support alone;
4. not explained by unigram path marginals;
5. not explained by low out-degree / path-count matching;
6. stronger than matched non-candidate middle-regime controls;
7. recurrent across multiple starts;
8. supported by at least two probe families, or explicitly labeled probe-local;
9. stable or smoothly degraded under roughness replay;
10. not just selected-window winner's curse.
```

If any condition fails, assign a lower descriptive class:

```text
support_only
endpoint_distribution_only
path_descriptive_only
path_fakeout
probe_local_path_candidate
start_local_path_candidate
underdetermined
```

## 8. Candidate selection discipline

Avoid selecting only the flashiest candidate windows and then asking whether they look path-structured.

Use a split design:

```text
discovery subset:
  select candidate windows

evaluation subset:
  held-out starts/probes/roughness seeds/path null seeds
```

At minimum, report whether each row is:

```text
discovery_selected
evaluation_heldout
matched_control
```

If full split is too much for this run, mark the run as exploratory and do not promote classes beyond diagnostic status.

## 9. Outputs to add or modify

Add:

```text
path_metric_calibration_report.md
path_metric_calibration_summary.csv
path_fakeout_summary.csv
probe_collision_diagnostics.csv
matched_non_candidate_path_controls.csv
same_environment_window_controls.csv
path_null_rank_summary.csv
path_metric_effect_sizes.csv
```

Modify:

```text
path_process_candidate_summary.csv
```

so it includes:

```text
path_evidence_level
fakeout_class
promotion_blockers
matched_control_effect_size
probe_collision_flag
start_recurrence_flag
roughness_path_stability_class
```

## 10. Final report requirements

The final report must answer:

```text
Are raw path metrics common in matched non-candidates?
Which path metrics, if any, discriminate candidates from matched controls?
Which fakeout modes are most common?
How much apparent path structure is explained by probe collision?
How much is explained by endpoint support or unigram path marginals?
How much is explained by low out-degree/path-count matching?
Do any path phenotypes recur across starts?
Do any recur across probe families?
Do any survive roughness replay in path-language space?
Should path metrics be kept, tightened, or abandoned?
```

## 11. Expected outcomes

Useful negative outcomes include:

```text
all candidates reduce to endpoint/support effects
matched non-candidates show the same path metrics
probe collision explains most apparent recurrence
low out-degree explains predictability
cycle/saturation fakeouts dominate
roughness destroys path-language stability
```

Useful positive-but-diagnostic outcomes include:

```text
candidate beats endpoint and unigram nulls but not matched non-candidates
candidate beats matched non-candidates but only in one probe family
candidate shows bigram structure but no trigram structure
candidate is start-recurrent but roughness path-fragile
candidate is robust in path metrics but support-only in endpoints
```

All of these should be recorded as phenotypes, not discarded.

## 12. Claim boundary

Allowed:

```text
We calibrated path metrics and identified which fakeout modes they are vulnerable to.
A candidate showed path-descriptive structure under specified controls.
A candidate remained support-only or endpoint-distribution-only.
```

Allowed only if earned:

```text
A candidate showed path-process-like structure beyond endpoint, unigram, low-out-degree, matched-control, start, probe, and roughness checks.
```

Not allowed:

```text
Omega detected
agency detected
identity detected
valuer detected
viability detected
scientific gate passed
```

## 13. Bottom line

Codex is right to worry that path metrics may be too permissive.

The next run should not search for path-process passes. It should calibrate the path metrics, classify fakeouts, and identify whether any candidate path signals remain nontrivial after matched comparison.

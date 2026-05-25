# RFS-MB0 Path/Process Diagnostic Spec

Status: Codex implementation/run handoff after relation-generator phenotype repair

Purpose: test whether the current constraint-dominated, edge-stable/noise-tolerant candidate phenotypes contain path/process structure beyond endpoint support and lightweight transition proxies.

This is not a scientific validation run. It is the next diagnostic pass.

## 0. Current context

The latest relation-generator phenotype repair changed the branch interpretation:

```text
relation generator still worth keeping
roughness artifact label mostly repaired
confirmed roughness artifact rare in the tested set
most candidates are constraint-dominated and not start-fragile
many candidates are edge-stable/noise-tolerant despite roughness-resampled null sensitivity
```

The next bottleneck is path/process evidence.

Current process labels such as:

```text
transition_process_candidate
```

are lightweight proxies based on transition MI and motif reuse. They are not enough to claim real path/process organization.

This run should answer:

```text
Given the same endpoint/support-level facts, do candidate environments show non-null organization in the temporal/path language of futures?
```

## 1. Do not pivot the generator yet

Use the current action-generated relation generator.

Do not replace the substrate.

Do not tune detector thresholds to create a pass.

Do not add agents, identity, value, viability, support/recover/degrade labels, or resource coordinates.

## 2. Target candidate subset

Focus on candidate environments/rows from the latest phenotype repair with:

```text
phenotype_class in:
  constraint_dominated_roughness_sensitive
  roughness_edge_brittle_candidate only as contrast, not primary target

roughness_strength_profile_class in:
  noise_tolerant
  noise_sensitive_smooth

start_coverage_class in:
  environment_level
  basin_local

roughness_artifact_flag = 0
```

Primary target:

```text
constraint-dominated, edge-stable/noise-tolerant, environment-level or basin-local candidates
```

Also include matched non-candidate middle-regime environments as controls.

Suggested sample:

```text
candidate environments: 20-40
matched non-candidate middle-regime environments: 20-40
roughness edge-brittle candidates: 5-10 as contrast, if available
```

If the runner cannot easily ingest prior candidate tables, rerun a small phenotype audit first and select targets automatically.

## 3. Multiple starts remain mandatory

Use:

```text
start_samples = 3 and 8
```

If runtime permits:

```text
start_samples = 16
```

Do not interpret path/process signals without start coverage classification.

Report:

```text
start_coverage_class
path_signal_by_start
path_signal_start_recurrence_rate
basin_local_path_signal_flag
environment_level_path_signal_flag
```

## 4. Path sampling / enumeration

For each selected environment, probe family, and start, construct path-signature sequences.

Preferred exact mode for small graphs:

```text
enumerate all paths up to path_horizon where feasible
```

Fallback sampled mode:

```text
sample_paths_per_start = 256, 512, or 1024
```

Required horizons:

```text
path_horizons = 4, 8, 12, 16
```

Optional:

```text
24, 32
```

Use path horizons aligned with early/pre-saturation windows.

For each path, convert states to probe signatures:

```text
s_0, s_1, ..., s_H
```

where `s_t = probe(state_t)`.

## 5. Path-language metrics

Compute for each environment/start/probe/window/path horizon:

### 5.1 N-gram support and counts

```text
signature_unigram_support_size
signature_bigram_support_size
signature_trigram_support_size
signature_4gram_support_size optional
signature_bigram_counts_json optional/sampled
signature_trigram_counts_json optional/sampled
```

### 5.2 N-gram entropy

```text
unigram_entropy
bigram_entropy
trigram_entropy
conditional_entropy_s_next_given_s
conditional_entropy_s_next_given_bigram_context
```

### 5.3 Mutual information / predictive structure

```text
I(S_t ; S_t+1)
I((S_t-1,S_t) ; S_t+1)
predictive_gain_bigram_context = I((S_t-1,S_t);S_t+1) - I(S_t;S_t+1)
```

### 5.4 Motif/path recurrence

```text
path_motif_reuse_rate
repeated_bigram_fraction
repeated_trigram_fraction
forbidden_bigram_count
forbidden_trigram_count
path_language_growth_rate
```

### 5.5 Compression / grammar proxy

Use simple, transparent proxies first:

```text
ngram_compression_proxy
minimum_description_proxy = observed_ngram_support / possible_ngram_support
transition_grammar_size
trigram_extension_count_mean
```

Do not overclaim MDL.

## 6. Support-vs-process decomposition

For each candidate, classify the level of signal:

```text
support_only
endpoint_distribution_deformation
transition_process_candidate
path_process_candidate
robust_path_candidate
underdetermined
```

Definitions:

```text
support_only:
  endpoint/signature support differs, but path n-gram structure is not exceptional

endpoint_distribution_deformation:
  signature frequencies differ beyond support, but path structure remains null-like

transition_process_candidate:
  bigram/one-step path language structure survives relevant process nulls

path_process_candidate:
  trigram/higher-order path structure survives bigram/support-matched process nulls

robust_path_candidate:
  path-process phenotype recurs across starts, probe families, roughness seeds/strengths, and matched controls
```

## 7. Process nulls

Add path/process nulls. Keep categories separate from destructive mechanistic ablations.

### 7.1 Endpoint-support matched path randomized

Preserve:

```text
endpoint signature support
path length
rough path count
```

Destroy:

```text
temporal ordering
transition grammar
```

Question:

```text
Given the same endpoint signatures, is the path language organized?
```

### 7.2 Unigram-marginal path shuffled

Preserve:

```text
overall signature unigram frequencies along sampled/enumerated paths
```

Destroy:

```text
signature order and local transition structure
```

Question:

```text
Is the signal only marginal signature frequency along paths?
```

### 7.3 Bigram-support matched trigram test

Preserve:

```text
which bigrams occur
```

Test:

```text
whether trigram/higher-order continuation structure is non-null
```

Question:

```text
Is there process structure beyond one-step transition support?
```

### 7.4 Transition-probability shuffled null

Preserve:

```text
transition support or coarse transition count totals
```

Destroy/shuffle:

```text
contextual continuation structure
```

Question:

```text
Does future generation depend on ordered process context?
```

### 7.5 Degree/out-degree ablations remain diagnostic only

Do not require path candidates to survive full out-degree randomization or the current `degree_preserving_rewire`.

Report them separately as destructive relation ablations.

Also rename current `degree_preserving_rewire` in reports to:

```text
out_degree_rewire_without_replacement
```

until a true directed degree-sequence preserving rewire exists.

## 8. Roughness interaction

For selected path candidates, reuse the repaired roughness diagnostics.

Report path-language similarity under:

```text
roughness_strength = 0
same-strength roughness reseeds
roughness_strength = 0.001, 0.003, 0.01, 0.03, 0.05
```

Metrics:

```text
path_bigram_jaccard_vs_baseline
path_trigram_jaccard_vs_baseline
path_ngram_distribution_JS_vs_baseline
path_process_class_recurrence_rate
```

Classify:

```text
path_roughness_robust
path_noise_sensitive_smooth
path_roughness_brittle
path_symmetry_breaking_stable
```

## 9. Outputs

Add:

```text
path_language_summary.csv
path_ngram_counts_sample.csv
path_process_null_summary.csv
path_process_candidate_summary.csv
path_start_recurrence_summary.csv
path_roughness_sensitivity_summary.csv
support_vs_process_decomposition.csv
path_process_matched_controls.csv
```

Update or include:

```text
candidate_phenotype_summary.csv
phenotype_reproducibility_summary.csv
relation_generator_phenotype_repair references
```

## 10. Final report

Write:

```text
rfs_mb0_path_process_diagnostic_result.md
```

Must answer:

```text
Do constraint-dominated, edge-stable/noise-tolerant candidates show path-language organization beyond endpoint support?
Are signals bigram-only, or do they extend to trigram/higher-order process structure?
Do path-process signals recur across starts?
Do they recur across probe families?
Do they survive endpoint-support and unigram-marginal path nulls?
Do they survive bigram-support matched trigram tests?
Are they robust to roughness in path-language space?
Are matched middle-regime non-candidates cleanly lower on the same metrics?
What candidate phenotype classes should be promoted, renamed, or demoted?
```

## 11. Suggested run shape

Focused diagnostic, not broad atlas.

Suggested:

```text
workers: 18
wall clock: 2-5 hours
coordinate_count: 5
selected candidate environments: 20-40
matched non-candidate controls: 20-40
start_samples: 3 and 8
path_horizons: 4, 8, 12, 16
sample_paths_per_start: 512 or exact if cheap
null_replicates: 5
roughness_seed_replicates: 3 for selected path candidates
```

If CPU utilization is desired, ensure at least 18 queued jobs per stage by increasing:

```text
selected environments
seeds_per_parameter_set
roughness replay jobs
path null replicate jobs
```

Priority order if runtime is tight:

```text
1. path bigram/trigram summaries
2. endpoint-support matched path null
3. unigram-marginal path shuffle
4. start recurrence
5. matched non-candidate controls
6. roughness path sensitivity
7. higher-order process nulls
```

## 12. Gate discipline

This run may promote candidates into stronger diagnostic classes, but should not declare the scientific gate passed unless separately warranted.

Allowed claims:

```text
path/process structure detected under specified diagnostic controls
candidate remains support-only under path nulls
candidate is bigram-only or trigram/higher-order process-like
candidate path signal is start-recurrent or start-local
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

## 13. Decision outcomes

### 13.1 If path signals survive

If candidates show path-process structure beyond support and matched controls:

```text
keep relation generator
expand path diagnostics
run confirmatory fresh-seed phenotype-level recurrence
begin parameter-regime mapping for path-process candidates
```

### 13.2 If path signals do not survive

If candidates reduce to support/endpoint effects:

```text
keep support-deformation taxonomy
revise candidate labels downward
consider generator parameter sweeps around constraint conflict/continuity
avoid claiming process structure
```

### 13.3 If matched controls also pass

If matched non-candidate controls also show similar path signals:

```text
path metrics are too permissive or generic
repair path nulls before scaling
```

### 13.4 If roughness destroys path signal

If path signal is roughness-brittle:

```text
diagnose whether roughness is causing lock-in, edge instability, or path-language instability
run roughness/constraint/asymmetry interaction sweep before scaling
```

## 14. Bottom line

The current generator is plausibly producing future-landscape deformation phenotypes.

The next run should determine whether those phenotypes are merely endpoint/support effects or whether they contain organized temporal/path-language structure.

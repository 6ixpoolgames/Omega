# RFS-MB0 Relation Atlas Breadth and Null-Repair Spec

Status: next-run implementation spec after auditing `run_relation_atlas_batch.py`

Purpose: improve the next relation-atlas run by fixing remaining diagnostic weaknesses in the staged batch runner and shifting emphasis toward breadth-first phase-space cartography, frontier/probe-marginal null decomposition, and reproducibility.

This is not a detector-threshold tuning pass.

## 0. Current empirical status

The relation-atlas branch has made real methodological progress:

```text
hand-named positive relation families removed
neutral action-generated relation environments implemented
middle-regime environments generated reproducibly
local/window candidates exposed
aggregate atlas gate remains 0
```

The repaired due-diligence batch showed:

```text
candidate windows survive degree and out-degree nulls
candidate windows fail frontier/probe-marginal diagnostics
candidate windows often fail constraint/asymmetry/roughness shuffles
localized reproducibility remains 0
```

The next question is not:

```text
How do we make the detector pass?
```

It is:

```text
Are local/window candidates real future-landscape deformation, or artifacts of
frontier size, probe marginals, window selection, parameter selection, or weak
reproducibility design?
```

## 1. Audit findings from current batch runner

The uploaded `run_relation_atlas_batch.py` is a useful runner, but the next pass should repair several issues before interpreting more local candidates.

### 1.1 Good features to keep

Keep:

```text
staged A/B/C/D/E/F structure
global wall-clock budget
broad n=5 sweep
targeted n=5 fresh-seed follow-up
limited n=6 transfer
parameter trend mining
interaction trend mining
per-null window kill table
localized reproducibility table
strict no-promotion of window-local candidates
```

These are now part of the standard due-diligence layer.

### 1.2 Stage C region selection is still too brittle

Current `select_middle_regions(...)` mostly selects:

```text
best single-parameter marginal values
plus top few pairwise interactions
```

This is good for a smoke, but weak for phase-space cartography.

Risks:

```text
marginal-fallacy risk
interaction effects underrepresented
exploratory regions later read as if confirmatory
core region may be too narrow
broad region may still behave like OR-style targeting if reused incorrectly
```

Required fix:

```text
separate exploratory region discovery from confirmatory region testing
```

Output two explicit region files:

```text
exploratory_regions.json
confirmatory_regions_preregistered.json
```

Confirmatory regions must be frozen before fresh-seed runs.

### 1.3 Stage E window selection is order-biased

Current `write_window_stress(...)` selects:

```python
selected = [...][:200]
```

This means the first 200 matching windows are inspected, which may depend on CSV ordering.

Required fix:

Use stratified selection:

```text
by environment_shape_class
by parameter_region_id
by window_name
by probe_family
by candidate strength quantile
```

Also write:

```text
window_stress_selection_summary.csv
```

with selected vs available counts.

### 1.4 Null survival criterion is too crude

Current survival criterion is approximately:

```text
JS > 0 and MI_delta > 0 and motif_delta > 0
```

This is too permissive for JS and too rigid for MI/motif.

Required fix:

Report separate per-null survival criteria instead of one binary rule:

```text
survives_MI
survives_motif
survives_JS_quantile
survives_KL_quantile
survives_joint_MI_motif
survives_all_declared
```

Use quantile/rank against null replicates if available.

If null replicates are not available, report raw deltas but mark:

```text
no_replicate_null_uncertainty
```

### 1.5 Frontier/probe-marginal null is too monolithic

The current result says candidates are killed by:

```text
frontier_or_probe_marginal
```

This is the live blocker, but it is too blunt. It conflates multiple explanations.

Required decomposition:

```text
frontier_size_only_null
probe_marginal_only_null
frontier_size_plus_probe_marginal_null
signature_support_matched_null
horizon_local_frontier_matched_null
window_local_frontier_matched_null
path_count_matched_null, if path counts exist
```

The next run must report which specific null kills each candidate.

### 1.6 Localized reproducibility is too coarse

Current reproducibility groups by a compact `parameter_region_id` built from pieces of the parameter string.

This is useful, but too approximate.

Required fix:

Group reproducibility at multiple levels:

```text
exact_parameter_set
frozen_region
interaction_region
one-parameter-neighborhood
probe_family
window_name
```

Report reproducibility across:

```text
fresh seeds
held-out starts
held-out probes
held-out null seeds
n=5 to n=6 transfer
```

### 1.7 Total environment counts can be misleading

The final summary sums generated environments across stages:

```text
Stage B + Stage C + Stage D
```

This is fine operationally, but can overstate independent coverage because targeted stages are derived from earlier selection.

Required fix:

Report:

```text
total_environment_evaluations
unique_parameter_sets
unique_parameter_regions
exploratory_environment_count
confirmatory_environment_count
fresh_seed_environment_count
transfer_environment_count
```

### 1.8 Stage status should include input/output integrity checks

If a stage output is missing, later trend functions currently often return empty rows silently.

Required fix:

For every stage, verify required files exist:

```text
environment_shape_summary.csv
relation_atlas_detector_summary.csv
generated_environment_metadata.csv
relation_atlas_window_summary.csv
horizon_local_profiles.csv
transition_information.csv
```

Write:

```text
stage_integrity_report.csv
```

Do not treat a stage as cleanly complete if required diagnostic files are absent.

## 2. Next-run strategy: breadth-first, not larger-state-first

The next run should emphasize breadth across observational axes before raw state-size scaling.

Prioritize breadth across:

```text
parameter regions
seeds
starts
probe families
horizon windows
null models
presentation perturbations
relation perturbations
```

Do not prioritize a single large n=7 or n=8 run yet.

Use n=5 as the fast survey layer and n=6 only as transfer/confirmation.

## 3. Required code changes before next batch

Implement or add flags for:

```text
--selection-mode stratified|top_k|random_seeded
--stress-sample-count
--confirmatory-region-file
--heldout-parameter-seed
--heldout-starts
--heldout-probes
--null-replicates
--presentation-perturbations
--relation-perturbations
```

Add outputs:

```text
stage_integrity_report.csv
window_stress_selection_summary.csv
frontier_probe_null_decomposition.csv
null_replicate_summary.csv
heldout_reproducibility_summary.csv
presentation_perturbation_summary.csv
relation_perturbation_summary.csv
unique_coverage_summary.csv
```

## 4. Null-repair requirements

### 4.1 Decompose frontier/probe-marginal nulls

Add separate null columns:

```text
JS_to_null_frontier_size_only
JS_to_null_probe_marginal_only
JS_to_null_frontier_plus_probe_marginal
JS_to_null_signature_support_matched
JS_to_null_horizon_local_frontier
JS_to_null_window_local_frontier
```

and corresponding:

```text
KL
MI_delta
motif_delta
```

where meaningful.

### 4.2 Add null replicates

For stochastic nulls, run multiple null seeds:

```text
null_replicates: 5 minimum
preferred: 10 if cheap
```

Report:

```text
null_mean
null_std
observed_minus_null_mean
observed_null_z_like_score
observed_null_rank
empirical_p_value_like_rank
```

No formal p-value claim required. This is calibration.

### 4.3 Per-null kill reason must be multi-label

Instead of one `kill_reason`, allow:

```text
failed_MI
failed_motif
failed_JS
failed_KL
failed_frontier_size
failed_probe_marginal
failed_constraint_shuffle
failed_asymmetry_shuffle
failed_roughness_resample
aggregate_gate_not_passed
not_reproducible
```

A candidate window can have multiple blockers.

## 5. Reproducibility requirements

For selected candidate windows, run held-out checks.

### 5.1 Fresh seed reproducibility

For frozen candidate parameter regions:

```text
train/discovery seeds: prior run
confirmatory seeds: new parameter seed and new environment seeds
```

Report:

```text
candidate_window_reappears_rate
same_probe_family_rate
same_window_type_rate
same_null_survival_pattern_rate
```

### 5.2 Held-out starts

Do not use only the default deterministic starts.

Add:

```text
start_set_train
start_set_heldout
```

Report whether candidate windows survive held-out starts.

### 5.3 Held-out probes

Split probes into:

```text
probe_train_families
probe_heldout_families
```

At minimum, ensure a candidate is not carried by a single probe family unless labeled:

```text
probe_family_concentrated_local_candidate
```

### 5.4 n=6 transfer

For selected n=5 regions, run n=6 transfer only as confirmation.

Report:

```text
middle_regime_transfer_rate
candidate_window_transfer_rate
null_survival_transfer_rate
```

## 6. Perturbation and presentation breadth

Add two lightweight breadth tests.

### 6.1 Presentation perturbations

For selected environments:

```text
coordinate relabeling
alphabet relabeling
probe basis swap
```

A robust future-landscape signal should not disappear under mere presentation changes unless the probe itself is presentation-dependent.

Report:

```text
presentation_invariance_score
```

### 6.2 Relation perturbations

For selected environments:

```text
small edge deletion
small edge rewiring
constraint perturbation
asymmetry perturbation
roughness resample
```

Report:

```text
perturbation_sensitivity_curve
```

This is not recovery/support/degrade semantics. It is neutral robustness testing.

## 7. Proposed next batch stages

### Stage A: repaired trend audit

Read the repaired batch outputs and produce:

```text
coverage_summary.csv
unique_coverage_summary.csv
parameter_region_rankings.csv
frontier_probe_blocker_summary.csv
```

### Stage B: broad breadth survey n=5

Run many cheap n=5 samples, but stratify by parameter regions rather than only the current core.

Suggested:

```text
parameter_samples: 500
seeds_per_parameter_set: 1
coordinate_counts: 5
horizon_grid: long_10x
null_replicates: 5 if implemented
```

### Stage C: confirmatory frozen-region fresh-seed n=5

Use a preregistered frozen region file from Stage A/B.

Suggested:

```text
selected regions: 5 to 10
fresh seeds per region: 10 to 20
held-out starts: enabled
held-out probes: enabled
```

### Stage D: null decomposition stress

Apply decomposed frontier/probe nulls to all candidate windows from Stage C.

Required output:

```text
frontier_probe_null_decomposition.csv
```

### Stage E: presentation/perturbation mini-smoke

Run on top candidate regions and matched middle-regime non-candidate controls.

Suggested:

```text
candidate environments: 20
matched non-candidate environments: 20
presentation perturbations: coordinate + alphabet relabeling
relation perturbations: edge deletion 1%, 5%; rewiring 1%, 5%
```

### Stage F: final summary

Must answer:

```text
Are candidate windows reproducible across fresh seeds?
Are they killed by frontier size alone, probe marginals alone, or the combination?
Do they survive held-out starts/probes?
Do they survive presentation changes?
Do they show smooth or brittle perturbation response?
```

## 8. Gate discipline

Scientific gate remains not passed unless all are true:

```text
middle-regime environment
candidate survives decomposed frontier/probe nulls
candidate survives degree/out-degree nulls
candidate survives constraint/asymmetry/roughness nulls or has a clear explanation for sensitivity
candidate appears across fresh seeds
candidate appears across held-out starts
candidate has support from at least two probe families or is explicitly labeled localized/probe-concentrated
candidate transfers or has a documented scaling reason not to transfer
aggregate atlas gate passes
```

If not, report:

```text
implementation/calibration progress only
scientific gate not passed
```

## 9. Expected outcomes

Useful negative outcomes:

```text
frontier_size_only kills everything
probe_marginal_only kills everything
combination kills everything but components do not
candidates fail held-out starts
candidates fail held-out probes
candidates fail presentation relabeling
candidates are brittle under tiny relation perturbation
```

Each failure points to a concrete next fix.

Useful positive-but-not-yet-gate outcomes:

```text
candidate survives degree/out-degree and frontier-size-only but fails probe-marginal
candidate survives frontier/probe nulls but fails constraint shuffle
candidate appears in n=5 but not n=6
candidate appears across starts but only one probe family
```

These should be labeled as local mechanistic clues, not scientific passes.

## 10. Bottom line

The next spec should emphasize breadth and diagnostic decomposition.

Do not make the detector easier.

Make the evidence harder to fake:

```text
stratified windows
replicated nulls
decomposed frontier/probe diagnostics
held-out starts
held-out probes
fresh seeds
presentation perturbations
relation perturbations
unique coverage accounting
```

The target is a phase-space map, not a pass.

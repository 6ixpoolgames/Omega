# RFS-MB0 Relation Atlas Batch-Runner Repair Spec

Status: Codex implementation/run handoff

Purpose: perform due diligence on the action-generated relation atlas before moving on. This is a batch-runner and diagnostics repair pass, not a detector-threshold tuning pass and not a new theory claim.

## 0. Current situation

The 5-hour relation-atlas batch produced a useful negative result:

```text
total generated environments: 1140
total middle-regime environments: 674
atlas_gate_pass_count: 0
```

This was useful because it showed:

```text
neutral relation environments can produce middle-regime worlds;
local/window candidates appear;
aggregate promotion remains blocked;
no scientific gate passes yet.
```

However, code audit found several likely blockers in the batch controller and reporting:

```text
1. Stage C targeting is broader than intended because parameter-region matching is OR-based.
2. Stage E window/null stress is mostly a reporting stub and does not fill per-null blocker columns.
3. Parameter trend mining is one-dimensional and misses interactions.
4. Candidate-window reproducibility is not tracked as a first-class diagnostic.
5. Requested vs matched parameter counts are not visible enough for narrow region selection.
```

Before moving to a new substrate or new detector family, repair these issues and run one due-diligence batch.

## 1. Non-negotiables

Do not:

```text
tune detector thresholds;
promote local/window candidates to scientific positives;
rename localized candidates as Omega-like;
add agents, identities, viable paths, support/recover/degrade labels;
add cost/resource coordinates;
hand-name generated families as structured positives.
```

Keep:

```text
atlas_gate_pass_count
```

as the strict headline scientific gate.

A zero-pass result remains valid if diagnostics improve.

## 2. Repair target A — parameter-region matching semantics

### Problem

`run_relation_atlas.py` currently treats parameter-region files as OR-of-regions. This is fine for broad exploration, but Stage C wrote a combined core region plus multiple single-parameter regions. Because matching is OR-based, targeted Stage C likely sampled anything matching any one of the single-parameter regions, not only the intended joint region.

### Required fix

Add a CLI option:

```text
--parameter-region-mode any|core_only|all
```

Definitions:

```text
any:
  current behavior. Match if params satisfy any region.

core_only:
  match only regions with name == "shape_selected_core" or core == true.
  If no core region exists, fail clearly with NO_JOBS_CORE_REGION_MISSING.

all:
  treat the region list as a conjunction of allowed values by parameter.
  A parameter set must satisfy all constrained parameter keys across the region file.
```

For the due-diligence run, use:

```text
--parameter-region-mode core_only
```

### Required reporting

Add to `config.json` and `relation_atlas_status.json`:

```text
parameter_region_mode
raw_parameter_candidates
filtered_parameter_sets
jobs_created
jobs_completed
requested_parameter_samples
```

If fewer jobs are created than requested, make this explicit in summary.

## 3. Repair target B — real per-null window stress

### Problem

`write_window_stress` currently selects structured-candidate windows, but only fills `degree_null_separation` from a generic `mean_JS_to_null_H`. Columns for constraint-shuffled, asymmetry-shuffled, roughness-resampled, and frontier/probe-marginal separation are blank. The stage cannot answer which null kills candidates.

### Required fix

Make window-level summaries null-specific.

For each candidate window row, compute/report per-null metrics for at least:

```text
degree_preserving_rewire
out_degree_preserving_random
constraint_shuffled
asymmetry_shuffled
roughness_resampled
frontier_or_probe_marginal
```

For each null, report:

```text
JS_to_null_window
KL_to_null_window
MI_delta_vs_null_window
motif_delta_vs_null_window
candidate_survives_null
```

Add output:

```text
window_null_kill_table.csv
```

Required columns:

```text
environment_id
parameter_set_id
window_name
probe_family
candidate_window_class
null_name
JS_to_null_window
KL_to_null_window
MI_delta_vs_null_window
motif_delta_vs_null_window
candidate_survives_null
kill_reason
```

`kill_reason` examples:

```text
failed_degree_null
failed_out_degree_random_null
failed_constraint_shuffle
failed_asymmetry_shuffle
failed_roughness_resample
failed_frontier_probe_marginal
aggregate_gate_not_passed
insufficient_probe_family_support
saturation_window
```

### Minimal survival rule

For diagnostics only, define:

```text
candidate_survives_null = true if:
  MI_delta_vs_null_window > 0
  AND motif_delta_vs_null_window > 0
  AND JS_to_null_window is finite/nonzero
```

Do not use this as a scientific pass. It is only a null-kill diagnostic.

## 4. Repair target C — interaction trend mining

### Problem

Current trend mining is one-parameter-at-a-time. Relation atlas behavior is almost certainly interaction-heavy.

### Required fix

Add interaction trend outputs:

```text
parameter_interaction_trends.csv
parameter_interaction_trends.md
```

Required interactions:

```text
out_degree_target x constraint_density
out_degree_target x reversibility_fraction
update_footprint x constraint_strength
constraint_density x constraint_strength
asymmetry_strength x reversibility_fraction
rewire_probability x constraint_strength
constraint_arity x constraint_density
```

For each interaction value pair, report:

```text
n_environments
middle_regime_rate
fast_saturation_rate
underconnected_rate
cycle_rate
local_candidate_rate
window_candidate_rate
mean_nonsaturation_window_length
mean_saturation_onset_H
mean_MI_delta_vs_null
mean_motif_delta_vs_null
mean_JS_bundle
atlas_gate_pass_rate
```

This is exploratory. Do not make causal claims.

## 5. Repair target D — localized reproducible candidate tracking

### Problem

The current system has only aggregate pass/fail and local/window candidate summaries. It does not track whether the same type of window candidate recurs across fresh seeds in the same parameter region.

### Required fix

Add a non-promoting diagnostic class:

```text
localized_reproducible_candidate
```

This is not `structured_propagation` and not a scientific gate pass.

A parameter region/probe-family/window may receive this diagnostic if:

```text
1. environments are middle_regime_environment;
2. at least N fresh seeds in the same parameter region show candidate windows;
3. candidates occur in the same window type, e.g. early_window or pre_saturation_window;
4. candidates occur in the same probe_family or at least two related probe families;
5. candidate windows survive degree and out_degree_random nulls;
6. candidate windows are then tested against constraint/asymmetry/roughness nulls and their survival/failure is reported.
```

Suggested initial thresholds:

```text
N >= 3 environments
candidate_window_rate >= 0.25 within the parameter region
survives degree/out_degree nulls in >= 0.50 of candidate windows
```

Again: this is a diagnostic, not a pass.

Add outputs:

```text
localized_candidate_reproducibility.csv
localized_candidate_reproducibility.md
```

Required columns:

```text
parameter_region_id
window_name
probe_family
n_environments
candidate_window_count
candidate_window_rate
survives_degree_rate
survives_out_degree_random_rate
survives_constraint_shuffle_rate
survives_asymmetry_shuffle_rate
survives_roughness_resample_rate
localized_reproducible_candidate
dominant_kill_reason
```

## 6. Repair target E — better Stage C region selection

After Stage B trend mining, generate two region files:

```text
stage_c_core_regions.json
stage_c_broad_regions.json
```

### 6.1 Core regions

Core regions should be multivariate combinations selected only by environment shape:

```text
middle_regime_rate
nonsaturation_window_length
not fast saturation
not underconnected
not cycle dominated
```

No detector-pass labels.

Use top interaction trends to construct core regions. Example:

```json
{
  "regions": [
    {
      "name": "shape_selected_core_0",
      "core": true,
      "source": "stage_b_interaction_trends",
      "out_degree_target": [2],
      "constraint_density": [0.25, 0.40],
      "constraint_strength": [1.0],
      "update_footprint": [2],
      "reversibility_fraction": [0.25]
    }
  ]
}
```

### 6.2 Broad regions

Broad regions can keep OR-style single-parameter exploration, but must be marked exploratory.

Due-diligence run should include:

```text
Stage C1: core_only targeted run
Stage C2: broad any-region run only if time remains
```

## 7. Due-diligence run plan

Use a shorter controlled run after code repair.

Suggested stages:

```text
A. Stage B-prime broad n=5, 200-300 environments
B. interaction trend mining
C. Stage C1 core_only targeted n=5, fresh seeds, 300-500 environments
D. Stage E real per-null window stress on candidate windows
E. optional limited n=6 core_only transfer, 40-80 environments
F. final repaired-batch summary
```

Suggested wall clock:

```text
2 to 5 hours
```

Do not run another huge blind batch until the null-kill table is working.

## 8. Suggested CLI after repair

### Broad run

```bash
python -m omega.rfs_mb0_future_landscape.run_relation_atlas \
  --out results/rfs_mb0_relation_atlas/repair_stage_b_broad_n5 \
  --parameter-samples 300 \
  --seeds-per-parameter-set 1 \
  --coordinate-counts 5 \
  --max-state-count 300 \
  --horizon-grid long_10x \
  --workers 18 \
  --max-runtime-seconds 7200
```

### Core-only targeted run

```bash
python -m omega.rfs_mb0_future_landscape.run_relation_atlas \
  --out results/rfs_mb0_relation_atlas/repair_stage_c_core_n5 \
  --parameter-region-file results/rfs_mb0_relation_atlas/repair_stage_c_core_regions.json \
  --parameter-region-mode core_only \
  --parameter-samples 500 \
  --seeds-per-parameter-set 2 \
  --coordinate-counts 5 \
  --max-state-count 300 \
  --horizon-grid long_10x \
  --workers 18 \
  --max-runtime-seconds 9000 \
  --parameter-seed 20260526
```

### Limited n=6 transfer

```bash
python -m omega.rfs_mb0_future_landscape.run_relation_atlas \
  --out results/rfs_mb0_relation_atlas/repair_stage_d_core_n6 \
  --parameter-region-file results/rfs_mb0_relation_atlas/repair_stage_c_core_regions.json \
  --parameter-region-mode core_only \
  --parameter-samples 80 \
  --seeds-per-parameter-set 1 \
  --coordinate-counts 6 \
  --max-state-count 1000 \
  --horizon-grid long_5x \
  --workers 18 \
  --max-runtime-seconds 5400 \
  --parameter-seed 20260527
```

## 9. Summary requirements

The repaired batch summary must answer:

```text
1. Did core_only region targeting create a narrower, reproducible middle-regime sample?
2. Which interaction parameter regions produce middle-regime worlds?
3. Which local/window candidates recur across seeds?
4. Which nulls kill those candidates?
5. Do any candidates survive degree/out-degree nulls but fail constraint/asymmetry/roughness shuffles?
6. Do n=5 core regions transfer to n=6?
7. Is atlas_gate_pass_count still 0?
```

If atlas gate remains 0, state that explicitly.

## 10. Outputs to add

Add or ensure:

```text
parameter_interaction_trends.csv
parameter_interaction_trends.md
stage_c_core_regions.json
stage_c_broad_regions.json
window_null_kill_table.csv
localized_candidate_reproducibility.csv
localized_candidate_reproducibility.md
repaired_batch_summary.md
repaired_batch_status.json
```

## 11. Claim boundary

Allowed:

```text
We repaired batch-runner targeting and null-kill diagnostics.
We tested core-only parameter regions selected by environment shape.
We identified whether candidate windows survive specific matched nulls.
```

Allowed only if supported:

```text
A localized candidate pattern recurred across fresh seeds and survived degree/out-degree nulls.
```

Not allowed unless strict aggregate gate passes:

```text
scientific gate passed
structured propagation detected
Omega detected
valuer detected
agent detected
identity detected
viability detected
```

## 12. Bottom line

Before moving on, repair the due-diligence machinery:

```text
narrow core-only region targeting;
real per-null window kill tables;
interaction trend mining;
localized reproducibility diagnostics.
```

Then run one repaired batch.

The goal is not to get a pass. The goal is to know whether the current zero-pass result is caused by:

```text
weak environments,
null artifacts,
probe mismatch,
or overly global aggregation.
```

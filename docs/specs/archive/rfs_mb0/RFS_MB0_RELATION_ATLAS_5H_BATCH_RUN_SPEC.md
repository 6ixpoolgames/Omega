# RFS-MB0 Relation Atlas 5-Hour Batch Run Spec

Status: Codex implementation/run handoff

Purpose: use a 5-hour workstation-away window to run a disciplined batch of relation-atlas calibration experiments without tuning the detector or claiming scientific success prematurely.

This spec assumes the action-generated relation atlas v0 is implemented and the n=5 calibration smoke has completed.

## 0. Current context

The action-generated relation atlas v0 calibration succeeded as an implementation and substrate-hygiene pass:

```text
generated environments: 50
middle-regime environments: 28
profiles: 8250
errors: 0
atlas_gate_passes: 0
```

This means:

```text
neutral generator works
hand-named positive families were removed
middle-regime environments exist
scientific gate is not passed
```

The next task is not to tune detector thresholds.

The next task is to use a 5-hour wall-clock budget to:

```text
1. map parameter trends;
2. sample more n=5 environments cheaply;
3. target parameter regions that produce middle-regime environments;
4. run limited n=6 follow-up only where justified;
5. stress window-level/null controls;
6. preserve strict aggregate-gate discipline.
```

## 1. Hard wall-clock budget

Total wall clock:

```text
5 hours maximum
```

The runner should enforce a global stop around:

```text
max_runtime_seconds = 18_000
```

Recommended safety cutoff:

```text
17_400 seconds
```

so output writing and summaries complete before the user returns.

All batches must checkpoint independently.

If the final stage is incomplete, partial results are acceptable as long as status files and summaries are written.

## 2. Non-negotiables

Do not:

```text
tune detector thresholds to create a pass
rename local/window candidates as positives
promote any environment without aggregate and probe-family support
add agents, identities, viable paths, support/recover/degrade labels
add cost/resource coordinates
hand-name any generated family as structured/positive
```

Keep:

```text
atlas_gate_pass_count
```

as the headline scientific gate.

A result with zero passes is valid if diagnostics improve.

## 3. Run structure overview

Run a staged batch:

```text
Stage A: summarize existing v0 calibration and extract parameter trends
Stage B: broad n=5 neutral sweep
Stage C: targeted n=5 middle-regime sweep
Stage D: n=6 limited follow-up on selected regions
Stage E: window-level/null stress audit
Stage F: final meta-summary
```

If time becomes constrained, prioritize in this order:

```text
A > B > C > F > E > D
```

Do not sacrifice final summaries.

## 4. Stage A — existing-run trend mining

Input:

```text
results/rfs_mb0_relation_atlas/20260523_action_generated_v0_n5_calibration/
```

Analyze existing outputs, especially:

```text
generated_environment_metadata.csv
environment_shape_summary.csv
environment_shape_classes.csv
relation_parameter_sweep.csv
relation_atlas_detector_summary.csv
relation_atlas_window_summary.csv
relation_atlas_null_summary.csv
aggregate_family_classes.csv
aggregate_probe_family_classes.csv
horizon_window_summary.csv
```

If some filenames differ, use the closest existing atlas outputs.

Produce:

```text
parameter_trends_existing.csv
parameter_trends_existing.md
```

Required trend summaries:

```text
parameter -> environment_shape_class distribution
parameter -> middle_regime_environment rate
parameter -> fast_saturation_environment rate
parameter -> underconnected_environment rate
parameter -> cycle_dominated_environment rate
parameter -> local_only / window-candidate rate
parameter -> mean nonsaturation_window_length
parameter -> mean saturation_onset_H
parameter -> mean largest_scc_fraction
parameter -> mean edge_reciprocity_fraction
parameter -> mean atlas gate score / pass count if available
```

Report coarse associations only. Do not make causal claims.

Recommended derived trend table columns:

```text
parameter_name
parameter_value
n_environments
middle_regime_rate
fast_saturation_rate
underconnected_rate
cycle_rate
underdetermined_rate
local_candidate_rate
mean_nonsaturation_window_length
mean_saturation_onset_H
mean_MI_delta_vs_null
mean_motif_delta_vs_null
mean_JS_bundle
atlas_gate_pass_rate
```

## 5. Stage B — broad n=5 neutral sweep

Purpose:

```text
increase sample size over cheap n=5 environments to stabilize parameter trends
```

Suggested run:

```bash
python -m omega.rfs_mb0_future_landscape.run_relation_atlas \
  --out results/rfs_mb0_relation_atlas/5h_stage_b_broad_n5 \
  --parameter-samples 200 \
  --seeds-per-parameter-set 1 \
  --coordinate-counts 5 \
  --max-state-count 300 \
  --horizon-grid long_10x \
  --workers 18 \
  --max-runtime-seconds 5400
```

If runtime is much faster than expected, allow:

```text
parameter_samples: 300
```

Do not mix n=6 into this stage.

Required outputs:

```text
stage_b_summary.md
stage_b_status.json
stage_b_environment_shape_classes.csv
stage_b_parameter_trends.csv
```

## 6. Stage C — targeted n=5 middle-regime sweep

Purpose:

```text
sample parameter regions that Stage A/B suggest produce middle-regime environments
without selecting for detector pass outcomes.
```

Selection criterion must be based on environment-shape properties, not detector pass labels.

Allowed selection signals:

```text
middle_regime_environment rate
nonsaturation_window_length
not fast_saturation
not collapse
not cycle dominated
largest_scc_fraction not tiny and not immediately full
```

Forbidden selection signals:

```text
atlas_gate_pass
structured_propagation label
local structured candidate count alone
Omega-like interpretation
```

Codex should generate a parameter-region file:

```text
stage_c_selected_parameter_regions.json
```

Then run a targeted sweep with fresh seeds:

```bash
python -m omega.rfs_mb0_future_landscape.run_relation_atlas \
  --out results/rfs_mb0_relation_atlas/5h_stage_c_targeted_n5 \
  --parameter-region-file results/rfs_mb0_relation_atlas/5h_stage_c_selected_parameter_regions.json \
  --parameter-samples 150 \
  --seeds-per-parameter-set 2 \
  --coordinate-counts 5 \
  --max-state-count 300 \
  --horizon-grid long_10x \
  --workers 18 \
  --max-runtime-seconds 5400
```

If `--parameter-region-file` does not exist yet, implement it or emulate it by adding CLI filters for parameter values.

Required outputs:

```text
stage_c_summary.md
stage_c_status.json
stage_c_parameter_trends.csv
stage_c_confirmed_middle_regime_regions.csv
```

## 7. Stage D — limited n=6 follow-up

Purpose:

```text
test whether promising n=5 middle-regime parameter regions remain middle-regime at larger distinction-space size.
```

Only run if Stage B/C leave enough time.

Do not run arbitrary n=6 mixed batches that create stragglers.

Use a small number of selected parameter regions from Stage C.

Suggested run:

```bash
python -m omega.rfs_mb0_future_landscape.run_relation_atlas \
  --out results/rfs_mb0_relation_atlas/5h_stage_d_targeted_n6 \
  --parameter-region-file results/rfs_mb0_relation_atlas/5h_stage_c_selected_parameter_regions.json \
  --parameter-samples 40 \
  --seeds-per-parameter-set 1 \
  --coordinate-counts 6 \
  --max-state-count 1000 \
  --horizon-grid long_5x \
  --workers 18 \
  --max-runtime-seconds 3600
```

If n=6 jobs straggle, stop early and write partial results.

Required output:

```text
stage_d_n6_transfer_summary.md
```

Important readout:

```text
Do n=5 middle-regime parameter regions transfer to n=6,
or do they saturate/collapse/underconnect?
```

## 8. Stage E — window-level/null stress audit

Purpose:

```text
probe whether early/pre-saturation window candidates are real or null artifacts.
```

Run on a small selected subset only:

```text
10 to 20 environments from Stage C
```

Selection basis:

```text
middle-regime environment shape
high nonsaturation_window_length
visible early/pre-saturation local candidates
```

This stage may use local/window candidates for selection, but must mark the run exploratory.

For each selected environment, run stronger window/null audits:

```text
constraint_shuffled
asymmetry_shuffled
roughness_resampled
degree_preserving_rewire
out_degree_preserving_random
frontier/probe-marginal null
```

Required outputs:

```text
stage_e_window_null_stress_summary.csv
stage_e_window_null_stress_summary.md
```

Required columns:

```text
environment_id
parameter_set_id
window_name
probe_family
window_local_candidate_fraction
degree_null_separation
constraint_shuffled_separation
asymmetry_shuffled_separation
roughness_resampled_separation
frontier_null_separation
promote_blocker
```

Do not promote any candidate from this stage unless the existing aggregate gate already supports it.

## 9. Stage F — final 5-hour meta-summary

Always run this even if earlier stages are partial.

Write:

```text
results/rfs_mb0_relation_atlas/5h_batch_summary.md
results/rfs_mb0_relation_atlas/5h_batch_status.json
```

Summary must include:

```text
wall-clock used
stages completed
stages partial
total environments generated
total middle-regime environments
atlas_gate_pass_count
control/null aggregate pass count
best middle-regime parameter regions
parameter trends
n=6 transfer result if run
window/null stress result if run
recommended next step
claim boundary
```

The final status JSON should include:

```json
{
  "status": "COMPLETED_OR_PARTIAL",
  "wall_clock_seconds": 0,
  "stages_completed": [],
  "stages_partial": [],
  "total_generated_environments": 0,
  "total_middle_regime_environments": 0,
  "atlas_gate_pass_count": 0,
  "control_aggregate_pass_count": 0,
  "recommended_next_step": ""
}
```

## 10. If Codex needs to modify code first

Likely helpful additions:

```text
--coordinate-counts
--max-state-count
--parameter-region-file
--parameter-samples
--horizon-grid
--horizons
--global-wall-clock-seconds
--stage-name
```

Already implemented flags may be reused.

Add a meta-runner if useful:

```text
omega/rfs_mb0_future_landscape/run_relation_atlas_batch.py
```

The meta-runner should:

```text
1. start global timer
2. run Stage A
3. run Stage B
4. mine Stage B trends
5. run Stage C
6. optionally run Stage D/E if time remains
7. always write Stage F summary
```

## 11. Parameter trend mining implementation sketch

Use simple grouping, not model-fitting, first.

For each parameter:

```python
for parameter_name in primitive_parameters:
    group by parameter_value
    compute environment_shape_class rates
    compute local_candidate rates
    compute mean/null metrics
```

Optional simple interaction tables:

```text
constraint_density x out_degree_target
constraint_strength x update_footprint
asymmetry_strength x reversibility_fraction
rewire_probability x constraint_strength
```

No black-box optimizer in this pass.

## 12. What would count as useful output?

Useful even with zero scientific passes:

```text
clear parameter regions that produce middle-regime environments
clear parameter regions that saturate/collapse/underconnect
clear evidence that local/window candidates are or are not null artifacts
clear evidence whether n=5 trends transfer to n=6
```

A positive scientific gate would require:

```text
non-control generated environment
middle-regime shape
aggregate structured_propagation
support from multiple probe families
separation from degree, random, constraint-shuffled, asymmetry-shuffled,
roughness-resampled, and frontier/probe-marginal nulls
fresh-seed confirmation
```

Do not expect this in the 5-hour batch.

## 13. Recommended stage time budget

Approximate allocation:

```text
Stage A: 10-20 minutes
Stage B: 60-90 minutes
Stage C: 90-120 minutes
Stage D: 30-60 minutes if time remains
Stage E: 30-45 minutes if time remains
Stage F: always reserve 10-15 minutes
```

If Stage B/C run faster than expected, prefer more Stage C fresh-seed targeted n=5 over arbitrary n=6 expansion.

## 14. Claim boundary

Allowed:

```text
We ran a 5-hour relation-atlas calibration batch.
We identified parameter trends for neutral middle-regime environments.
We tested whether local/window candidates survive matched null stress.
```

Allowed only if supported:

```text
A parameter region reproducibly produced middle-regime environments.
```

Not allowed:

```text
Omega detected
valuer detected
agent detected
identity detected
viability detected
scientific gate passed
```

unless the strict gate conditions are actually met.

## 15. Bottom line

The five-hour batch should not chase a pass.

It should answer:

```text
Which primitive relation parameters produce usable neutral environments,
and are the observed local/window candidates anything more than null artifacts?
```

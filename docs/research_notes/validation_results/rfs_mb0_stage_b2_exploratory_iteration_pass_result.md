# RFS-MB0 Stage B-2 Exploratory Iteration Pass Result

Date: 2026-05-28

Spec:

```text
docs/RFS_MB0_STAGE_B2_EXPLORATORY_ITERATION_PASS_SPEC.md
```

## 1. Claim Boundary

This was an exploratory iteration pass.

It was not holdout validation, candidate promotion, Omega detection, agency
detection, identity detection, or value detection.

Run counters stayed inside the boundary:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## 2. Hardware / Runtime Profile

Hardware profile:

```text
desktop profile
Ryzen 5900X class CPU
RTX 4070 Ti available, not used
workers: 18
job_batch_size: 8
thread caps: OMP/OPENBLAS/MKL/NUMEXPR = 1
```

The main run used the optimized Stage B-2 path:

```text
Stage A control-summary cache: loaded
control_summary_load_seconds: 0.134
metric_output_mode: audit_sample
component_output_mode: audit_sample
marginal_output_mode: summary
count-based online syndrome aggregation: enabled
full metric rows retained in memory: 0
```

Performance:

```text
elapsed_seconds: 28653.366
jobs_completed: 576000 / 576000
throughput: about 20.1 jobs / second
metric_rows_scored: 48384000
component_score_rows_scored: 580608000
errors: 0
```

The previous unoptimized desktop Stage B mechanism smoke completed about 4.6
jobs / second. This pass therefore achieved about 4.4x higher job throughput,
while avoiding full raw component CSV emission.

## 3. Priority Queue Actually Executed

Priority 0 control identity smoke:

```text
results/rfs_mb0_relation_atlas/20260528_stage_b2_optimized_count_contract_smoke_notrack/
status: COMPLETED
jobs_completed: 12 / 12
errors: 0
```

Priority 1 existing-output triage:

```text
results/rfs_mb0_relation_atlas/20260528_stage_b2_existing_output_triage/
status: COMPLETED
stage_a_syndrome_smoke_rows: 179200
stage_b_mechanism_rate_rows: 224
errors: 0
```

Priority 2 gentle mechanism ladder plus Priority 3 entropy-flow-horizon overlay:

```text
results/rfs_mb0_relation_atlas/20260528_stage_b2_exploratory_iteration_8h_gentle_mechanism/
status: COMPLETED
jobs_completed: 576000 / 576000
```

Priority 4 branch-selective extension:

```text
not run as a separate pass
reason: the full gentle mechanism ladder consumed the available wall-clock block
```

The Priority 4 decision is still emitted below from the completed ladder and
overlay outputs.

## 4. Graceful-Exit Status

The main run completed all requested jobs before the hard cap:

```text
status: COMPLETED
finalization_reason: all_jobs_completed
max_runtime_seconds: 28800
shutdown_cushion_seconds: 1800
jobs_cancelled: 0
pending_jobs_remaining: 0
errors: 0
output_manifest.json: present
errors.csv: present and empty
progress checkpoints: 116
```

## 5. Control Identity And Proxy Discipline

Main run control identity:

```text
exact mechanism control conditions: 10
generation-level proxy conditions: 2
topology-level proxy conditions: 11
not-available/baseline conditions: 1
runtime-downgraded intended controls: 0
```

No control exceeded the hard `control_too_destructive` gate in the graph-level
preservation audit. The constraint generation proxies remained
`destructive_underdetermined`, not clean mechanism evidence.

Important implementation caveat:

```text
track_frontier_preservation_metrics: false
track_saturation_timing: false
```

For this long run, destructiveness is graph-level preservation only. Frontier
profile and saturation-timing deltas were intentionally omitted to keep the
8-hour run memory-safe. Strong p0.02 topology reads should therefore be treated
as edge/topology sensitivity, not clean mechanism attribution.

## 6. Existing-Output Triage Summary

Existing Stage A/B triage supported the current priority split:

```text
SYN_A: prioritize_stabilizing_channel_syndrome
SYN_C: prioritize_stabilizing_channel_syndrome
SYN_B: retain_turnover_diffusion_contrast
SYN_D: retain_turnover_diffusion_contrast
```

The top Stage A concentration was not limited to a single syndrome. SYN_B and
SYN_D remained useful as turnover/diffusion contrasts, but not as primary
mechanism targets for this pass.

## 7. Gentle Mechanism Ladder Result

Main decision summary:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag:
  decision_class: edge_roughening_sensitive_syndrome
  baseline_syndrome_rate: 0.02146924603174603
  max_mechanism_dependency_score: 0.500231042927776

SYN_C_low_growth_high_concentration_low_entropy:
  decision_class: edge_roughening_sensitive_syndrome
  baseline_syndrome_rate: 0.03405059523809524
  max_mechanism_dependency_score: 0.4186842641960202

SYN_B_high_turnover_high_offdiag_high_window_delta:
  decision_class: no_resolved_residual
  baseline_syndrome_rate: 0.09655497685185185
  max_mechanism_dependency_score: 0.015337404927868057

SYN_D_high_turnover_high_entropy_low_bottleneck_control:
  decision_class: no_resolved_residual
  baseline_syndrome_rate: 0.03444146825396825
  max_mechanism_dependency_score: 0.01057118990696184
```

The strongest non-destructive rows were topology-level controls:

```text
SYN_A small_edge_resample p0.02:
  baseline 0.021469 -> control 0.010730
  dependency 0.500231

SYN_C small_edge_resample p0.02:
  baseline 0.034051 -> control 0.019794
  dependency 0.418684

SYN_A asymmetric_edge_flip p0.02:
  baseline 0.021469 -> control 0.013832
  dependency 0.355737

SYN_C asymmetric_edge_flip p0.02:
  baseline 0.034051 -> control 0.024157
  dependency 0.290549
```

The exact generator-level roughness-seed and asymmetry-strength controls were
near baseline. That is the central read: the detectable residue currently looks
more like topology/edge-channel sensitivity than clean generator-mechanism
sensitivity.

## 8. Entropy-Flow-Horizon Overlay Result

The overlay showed a coherent monotone topology-control pattern:

```text
small_edge_resample p0.005:
  entropy_spreading
  flow_near_baseline
  horizon_near_baseline

small_edge_resample p0.01:
  entropy_spreading
  flow_near_baseline
  downstream_reopening_hint

small_edge_resample p0.02:
  entropy_spreading
  flow_near_baseline
  downstream_reopening_hint

asymmetric_edge_flip p0.01 / p0.02:
  entropy_spreading
  flow_near_baseline
  downstream_reopening_hint
```

Exact roughness-seed and asymmetry-strength controls were
`entropy_near_baseline`, `flow_near_baseline`, and `horizon_near_baseline`.

## 9. Exploratory Extension Result

No separate Priority 4 extension ran. The completed ladder points to the
appropriate extension:

```text
Priority 4A: channel-edge sensitivity
```

The next pass should distinguish maintained channel structure from generic edge
fragility:

```text
identify high-flow edge/signature-transition sets;
perturb high-flow sets gently;
perturb matched random edge sets;
compare syndrome-rate and horizon-profile changes.
```

## 10. Corridor / Trap / Fakeout Read

Provisional classification:

```text
SYN_A: edge_fragile_deformation, low_smoke confidence
SYN_C: edge_fragile_deformation, low_smoke confidence
SYN_B: underpowered_or_unresolved, low_smoke confidence
SYN_D: underpowered_or_unresolved, low_smoke confidence
```

This should not be read as corridor validation. The topology controls make the
signal intelligible, but not yet specific.

## 11. Parameter-Sweep Read

No separate parameter-neighborhood sweep was run.

The asymmetry-strength ladder behaved like a local parameter sweep and stayed
near baseline:

```text
x0.5, x0.75, x0.9, x1.1, x1.25, x1.5:
  low dependency for SYN_A/SYN_C
  entropy/flow/horizon near baseline
```

This weakens a simple generator-asymmetry explanation for the current A/C
residue.

## 12. Representation-Resolution Read

No representation-resolution diagnostic was run.

The result does not justify opening alphabet expansion yet. If future
channel-edge tests show coherent but weak residues, representation resolution
can be revisited as a diagnostic only.

## 13. Decision Tree Outcome

Recommendation:

```text
recommend channel-specific follow-up
holdout remains blocked
do not promote candidates
do not write full RFS-MB0G gauge-shadow validation yet
```

Reason:

```text
SYN_A/SYN_C remain measurable across a large design-set run;
the strongest effects are non-destructive topology-level edge controls;
the entropy-flow-horizon overlay is coherent for edge perturbations;
exact roughness/asymmetry generator controls are near baseline;
SYN_B/SYN_D do not show resolved residuals.
```

This is progress, but it is not mechanism validation. The immediate next branch
should test whether the edge sensitivity is channel-specific or generic edge
fragility.

## 14. Output Manifest

Retained public/lab note:

```text
docs/research_notes/validation_results/rfs_mb0_stage_b2_exploratory_iteration_pass_result.md
```

Local output directories:

```text
results/rfs_mb0_relation_atlas/20260528_stage_b2_existing_output_triage/
results/rfs_mb0_relation_atlas/20260528_stage_b2_optimized_count_contract_smoke_notrack/
results/rfs_mb0_relation_atlas/20260528_stage_b2_exploratory_iteration_8h_gentle_mechanism/
```

Main output manifest:

```text
stage_b2_run_config.json: present
stage_b2_job_manifest.csv: 576000 rows
stage_b2_progress_checkpoints.csv: 116 rows
stage_b2_control_identity_audit.csv: 24 rows
stage_b2_mechanism_control_system_manifest.csv: 576000 rows
stage_b2_substrate_preservation.csv: 552000 rows
stage_b2_metric_rows.csv: skipped_by_metric_output_mode:audit_sample
stage_b2_metric_rows_audit_sample.csv: 75000 rows
stage_b2_component_scores.csv: skipped_by_component_output_mode:audit_sample
stage_b2_component_scores_audit_sample.csv: 100000 rows
stage_b2_syndrome_rates.csv: 384 rows
stage_b2_dependency_scores.csv: 92 rows
stage_b2_decision_summary.csv: 4 rows
stage_b2_entropy_view_summary.csv: 288 rows
stage_b2_flow_view_summary.csv: 288 rows
stage_b2_horizon_view_summary.csv: 72 rows
stage_b2_entropy_flow_horizon_overlay.csv: 23 rows
stage_b2_corridor_trap_fakeout_summary.csv: 4 rows
errors.csv: 0 rows
status.json: present
output_manifest.json: present
```

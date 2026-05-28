# Omega Running Log

This is the living operational log for the Omega validation workspace. Update it
after every meaningful theory-side decision, probe implementation, or compute
run.

Entries are organized in rough reverse chronological order, with the most recent
patch notes at the top.

## 2026-05-28

### RFS-MB0 Desktop Phase B / Stage A / Stage B Validation

Ran the desktop validation of the regenerated Phase B full-control path,
read-only Stage A syndrome audit, and Stage B mechanism-control smoke.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_desktop_phase_b_stage_a_b_validation_result.md`

Local outputs:

- `results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_phase_b_regenerated_full_controls/`
- `results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_stage_a_regenerated_full_controls/`
- `results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_stage_b_mechanism_smoke/`

Hardware boundary:

```text
desktop profile
Ryzen 5900X class CPU
RTX 4070 Ti available, not needed for this CPU-bound pass
workers: 18
job_batch_size: 4
thread caps: OMP/OPENBLAS/MKL/NUMEXPR = 1
```

Stage 1 regenerated Phase B full controls:

```text
status: COMPLETED
elapsed_seconds: 3959.802
jobs_completed: 1120 / 1120
metric_rows: 134400
control_rows: 13165111
stage_a_control_value_rows: 13163988
errors: 0
full_control_csv_written: 1
row_level_effect_csv_written: 0
holdout_scoring_count: 0
decision_class: phase_c_blocked_no_recurrence
```

Stage A syndrome audit:

```text
status: COMPLETED
elapsed_seconds: 178.609
control_source: phase_b_stage_a_control_values.csv
syndrome_component_rows: 940800
marginal_control_replicates: 500
decision_class: syndrome_smoke_joint_positive_above_marginal_controls
stage_b_allowed: 1
selected_syndrome_ids:
  SYN_A_low_growth_high_bottleneck_low_offdiag
  SYN_B_high_turnover_high_offdiag_high_window_delta
  SYN_C_low_growth_high_concentration_low_entropy
  SYN_D_high_turnover_high_entropy_low_bottleneck_control
```

Stage B mechanism smoke:

```text
status: COMPLETED
elapsed_seconds: 980.677
jobs_completed: 4480 / 4480
metric_rows: 376320
component_score_rows: 2822400
errors: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

Decision read:

```text
All four selected syndromes remain control_too_destructive_underdetermined.
Non-destructive dependency signal appears mainly in SYN_A/SYN_C under
roughness p0.01 and asymmetry p0.01/p0.02.
Most stronger mechanism controls are too destructive for negative
interpretation.
```

Interpretation:

```text
The syndrome branch is now more promising than marginal recurrence, because
Stage A separates preregistered joint signed syndromes from marginal-preserving
controls on regenerated desktop Phase B rows.

The mechanism-control ladder is not yet clean enough. Do not open holdout.
Next work should calibrate gentler preservation-first controls before scaling.
```

### RFS-MB0 Frontier-Transform Stage B Mechanism Smoke on Laptop

Implemented and ran a laptop-local Stage B mechanism-control dependency smoke
after the Stage A addendum gate allowed a mechanism-profile pass.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_laptop_stage_b_mechanism_smoke_30m_result.md`

Primary output:

- `results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_b_mechanism_smoke_30m/`

Input Stage A addendum:

- `results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_a_addendum_laptop_full_control/`

Input Phase B full-control rebuild:

- `results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls/`

Hardware boundary:

```text
laptop profile only
workers: 7
job_batch_size: 2
thread caps: OMP/OPENBLAS/MKL/NUMEXPR/NUMBA = 1
desktop runs should not inherit this profile
```

Claim boundary:

```text
Mechanism-control dependency smoke only.
Not historical desktop full-breadth confirmation.
No holdout scoring, n=6 transfer, alphabet expansion, candidate promotion,
Omega detection, agency detection, identity detection, or value detection.
```

Run status:

```text
status: COMPLETED
elapsed_seconds: 89.283
jobs_completed: 224 / 224
metric_rows: 18816
component_score_rows: 141120
syndrome_rate_rows: 224
dependency_score_rows: 52
decision_rows: 4
errors: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

Decision read:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag:
  control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.026785714285714284

SYN_B_high_turnover_high_offdiag_high_window_delta:
  no_measurable_syndrome
  baseline_syndrome_rate: 0.0

SYN_C_low_growth_high_concentration_low_entropy:
  control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.026785714285714284

SYN_D_high_turnover_high_entropy_low_bottleneck_control:
  no_measurable_syndrome
  baseline_syndrome_rate: 0.0
```

Interpretation:

```text
Mildly promising as an instrumentation target, not a validation result.
SYN_A and SYN_C are measurable and show weak roughness sensitivity under the
gentlest non-destructive roughness control, while gentle asymmetry is generic.
The stronger controls are often substrate-destructive, so negative reads remain
underdetermined. SYN_B and SYN_D were not measurable in this limited Stage B
design.
```

Next step:

```text
Run a Stage B-2 targeted mechanism smoke with gentler preservation-first
control ladders before spending more seeds or opening any holdout path.
```

### RFS-MB0 Frontier-Transform Syndrome Audit Laptop Validation

Ran a laptop-local validation of the new frontier-transform Phase B / Stage A
syndrome audit path.

Retained note:

- `docs/research_notes/validation_results/rfs_mb0_frontier_transform_syndrome_laptop_validation_result.md`

Local outputs:

- `results/local_runs/20260528_laptop_frontier_transform_phase_b_validation_192jobs/`
- `results/local_runs/20260528_laptop_frontier_transform_stage_a_validation_192jobs/`

Claim boundary:

```text
This was a local runner/output-contract validation, not a scientific Phase B
rerun and not a holdout, candidate-promotion, mechanism-dependency, Omega,
agency, identity, or value result.
```

Reason:

```text
The historical Phase B/source CSV directories are ignored and not present in
this laptop clone, so the run regenerated a small fixture-like input bundle
under results/local_runs/ to exercise the implementation path.
```

Laptop profile:

```text
workers: 7
job_batch_size: 2
thread caps: OMP/OPENBLAS/MKL/NUMEXPR/NUMBA = 1
machine: laptop DESKTOP-LVVT7H7, Intel i7-1165G7, Intel Iris Xe, no CUDA
```

Phase B local validation completed:

```text
jobs_completed: 192 / 192
metric_rows: 14336
control_rows: 1245559
errors: 0
holdout_scoring_count: 0
decision_class: phase_c_blocked_no_recurrence
phase_c_ready: 0
```

Stage A syndrome audit completed:

```text
metric_rows: 14336
control_rows: 1245559
syndrome_component_rows: 118272
errors: 0
new_systems_generated: 0
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
```

Stage A emitted a positive preregistered-syndrome readiness row on the local
fixture, selecting:

```text
diffusive_noise_syndrome
recurrence_cascade_syndrome
stabilizing_boundary_syndrome
transition_boundary_syndrome
```

Interpretation:

```text
This validates that the Stage A scoring/readiness path executes on nontrivial
rows. It does not establish that the historical Phase B run contains these
syndromes.
```

CSV hardening added during the validation:

```text
shared frontier-transform read_csv tolerates UTF-8 BOM headers
shared write_csv uses csv.writer with larger buffering instead of DictWriter
Phase B can skip duplicate row-level effect CSVs during validation runs
```

Main observed bottleneck:

```text
phase_b_design_control_rows.csv was about 745 MB.
Worker execution finished quickly; final CSV materialization and Stage A CSV
ingestion dominated wall time.
```

Follow-up compact Stage A control-value contract:

```text
Phase B now emits phase_b_stage_a_control_values.csv.
Stage A prefers that compact table and falls back to phase_b_design_control_rows.csv.
```

Validation on the same 192-job laptop Phase B output:

```text
full debug control CSV: 744725521 bytes
compact Stage A control CSV: 172520869 bytes
phase_b_syndrome_readiness.csv: identical
phase_b_syndrome_smoke.csv: identical
phase_b_syndrome_vs_controls.csv: identical
phase_b_syndrome_component_scores.csv: identical
Stage A elapsed, full source: 470.003 seconds
Stage A elapsed, compact source: 403.329 seconds
```

A compact Phase B rerun with `--skip-full-control-csv` completed cleanly:

```text
jobs_completed: 192 / 192
stage_a_control_value_rows: 1245364
full_control_csv_written: 0
phase_b_design_control_rows.csv: 46 byte sentinel
phase_b_stage_a_control_values.csv: about 172.5 MB
errors: 0
```

Interpretation:

```text
The compact contract removes Stage A's dependency on the full debug control CSV
and preserves syndrome outputs. The next bottleneck is Stage A control-value
grouping/scoring, not just raw CSV emission.
```

Follow-up Stage A scoring optimization:

```text
control buckets are now summarized once
control_mean/control_std are cached per metric/probe/flow/window
percentiles use sorted control values and binary search
control rows are filtered to preregistered syndrome metrics before scoring
```

Validation on the same compact 192-job Phase B output:

```text
pre-cache compact Stage A elapsed: 456.399 seconds
cached compact Stage A elapsed: 8.400 seconds
phase_b_syndrome_readiness.csv: identical
phase_b_syndrome_smoke.csv: identical
phase_b_syndrome_component_scores.csv: identical
```

## 2026-05-27

### RFS-MB0 Frontier-Transform Syndrome and Mechanism-Control Audit Spec

Added the next audit spec after Phase B showed control-equivalent marginal recurrence:

- `docs/RFS_MB0_FRONTIER_TRANSFORM_SYNDROME_AND_MECHANISM_CONTROL_AUDIT_SPEC.md`

Reason:

```text
Phase B did not show absence of all recurrence.
It showed that marginal frontier-transform recurrence is too generic:
raw design-set recurrence appeared, but matched recurrence controls reached the same strongest rate.
```

Core change:

```text
Stop asking only:
  does metric M recur above threshold T?

Ask instead:
  does a preregistered joint signed frontier-transform syndrome recur above controls,
  and does it show the expected dependency profile under constraint/asymmetry/roughness perturbations?
```

The spec defines two stages:

```text
Stage A:
  read-only Phase B postmortem and syndrome smoke on existing rows

Stage B:
  small design-set mechanism-control rerun with roughness/asymmetry/constraint controls where implementable
```

Important interpretation update:

```text
Mechanism controls are dependency tests, not survival tests.
A syndrome killed by constraint/asymmetry perturbation may be mechanism-dependent, not falsified.
```

Still blocked:

```text
holdout Phase C
n=6 transfer
alphabet expansion except optional tiny diagnostic
agent / identity / value labels
Omega-positive claims
```

### RFS-MB0 Frontier-Transform Phase B Design-Set Recurrence

Implemented and ran the larger design-set recurrence pass requested by:

- `docs/RFS_MB0_FRONTIER_TRANSFORM_PHASE_B_10H_DESIGN_RECURRENCE_SPEC.md`

Runner:

- `omega/rfs_mb0_future_landscape/run_frontier_transform_phase_b.py`

Primary retained note:

- `docs/research_notes/validation_results/rfs_mb0_frontier_transform_phase_b_10h_result.md`

Primary output:

- `results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_b_10h/`

Before the primary run, the runner was updated for:

```text
periodic status.json writes
phase_b_progress_checkpoints.csv during execution
SIGINT/SIGTERM/SIGBREAK stop requests
shutdown cushion before wall-clock expiry
normal final artifact generation from completed rows after interruption
```

The repaired smoke completed cleanly:

```text
jobs_completed: 16 / 16
metric_rows: 896
control_rows: 55283
errors: 0
holdout_scoring_count: 0
phase_b_design_recurrence_summary.csv: present
decision_class: phase_c_blocked_no_recurrence
```

Primary Phase B completed cleanly:

```text
jobs_completed: 1120 / 1120
metric_rows: 134400
control_rows: 13165111
errors: 0
elapsed_seconds: 3100.015
holdout_scoring_count: 0
```

Raw design-set recurrence appeared in B0-viable families:

```text
bottleneck observed recurrence mean: 0.2875
support_turnover observed recurrence mean: 0.2600
transition_matrix observed recurrence mean: 0.2417
window_stability observed recurrence mean: 0.1176
```

However, after repairing the matched recurrence-control summary, the strongest rows were control-equivalent:

```text
observed_recurrence_rate: up to 0.6
control_recurrence_mean: matched at 0.6 on strongest rows
recurrence_excess: 0.0
```

Final decision:

```text
decision_class: phase_c_blocked_no_recurrence
phase_c_ready: 0
supporting_metric_family_count: 0
supporting_probe_count: 0
holdout_scoring_count: 0
```

Interpretation:

```text
Do not open frozen holdout Phase C from this result.
Frontier-transform instrumentation remains technically healthy.
The limiting issue is not runtime or workflow; it is control-equivalent recurrence.
Next work should test preregistered joint syndromes and mechanism-dependency controls.
```

### RFS-MB0 Frontier-Transform B0 Control/Flow Repair

Implemented the control/flow semantic repair pass requested by:

- `docs/RFS_MB0_FRONTIER_TRANSFORM_PHASE_B0_CONTROL_FLOW_REPAIR_SPEC.md`

Primary output:

- `results/rfs_mb0_relation_atlas/20260527_frontier_transform_b0/`

B0 changes:

```text
separated constrained_window_flow from one_step_local_flow
removed silent fallback from frontier-window transition flow
reported no-window-target and skipped-state rates
replaced four-integer sketch stability with metric-vector and real distribution stability
computed transform controls rather than only listing them
reported signed and absolute effect directions
kept holdout scoring at zero
```

B0 completed cleanly:

```text
jobs_completed: 160 / 160
metric_rows: 8960
control_rows: 643112
errors: 0
decision_class: phase_b_ready
holdout_scoring_count: 0
```

Viable metric families after B0:

```text
support_turnover
transition_matrix
bottleneck
window_stability
```

Interpretation:

```text
B0 permitted a design-set Phase B recurrence run.
B0 was still not detection or validation.
Holdout Phase C remained frozen.
```

### RFS-MB0 Frontier-Transform Phase A Instrumentation Preflight

After endpoint/quotient probe instrumentation failed to produce adequate independent non-identity axes, the branch pivoted from endpoint-state signatures to frontier-transform metrics.

Spec:

- `docs/RFS_MB0_FRONTIER_TRANSFORM_INSTRUMENTATION_SPEC.md`

Primary output:

- `results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_a/`

New measurement object:

```text
frontier-transform window F_Ha -> F_Hb
```

rather than:

```text
endpoint signature distribution at H
```

Phase A completed cleanly:

```text
jobs_completed: 160 / 160
row_count: 4480
errors: 0
holdout_detection_enabled: false
candidate_detection_enabled: false
```

Viable non-control transform metric families:

```text
growth
support_turnover
transition_matrix
branch_merge
bottleneck
window_stability
```

Interpretation:

```text
Frontier-transform instrumentation was viable enough for B0 control/flow repair.
This was not a detection claim.
```

### RFS-MB0 Instrumentation Branch Pivot

Added and implemented documentation for the instrumentation pivot:

- `docs/RFS_MB0_INSTRUMENTATION_BRANCH_PIVOT_AND_PROBE_PANEL_SPEC.md`
- `docs/RFS_MB0_BOUNDARY_DEFORMATION_GUARDRAIL_AND_QUOTIENT_PROBE_SPEC.md`

Current read at that point:

```text
The substrate is potentially fertile, but the instrumentation is flawed or underpowered.
```

The branch stopped treating the next task as broader search and reframed it as measurement-basis construction.

Important discipline added:

```text
probe preflight before candidate scoring
design/holdout split
threshold selection audit
multiplicity audit
identity leakage reporting
holdout freeze until instrument readiness
```

### RFS-MB0 Detector Instrumentation Repair and Boundary Recurrence

The detector instrumentation repair pass sharpened earlier boundary recurrence results.

Corrected group classes:

```text
independent_axis_recurrent_but_collision_limited: 16
weak_control_bundle_recurrence: 4
clean_recurrent_boundary_candidate: 0
sparse_regime_recurrent_candidate_pending_floor_audit: 0
```

Interpretation:

```text
Recurrent boundary structure is visible.
The main limit is collision/probe resolution, not no signal.
Clean quotient-level deformation was not established.
```

This motivated the instrumentation branch and ultimately the frontier-transform pivot.

## 2026-05-22

### RFS0 Strict Reachable Futures Small Smoke

Implemented the first RFS0 exact finite reachable-futures substrate batch from
`docs/RFS0_STRICT_REACHABLE_FUTURES_BATCH_SPEC.md`.

Code changes:

- added `omega/rfs0/substrate.py`;
- added `omega/rfs0/exact.py`;
- added `omega/rfs0/run_strict_batch.py`;
- added exact reachable sets, finite-horizon viability kernels, capture basins,
  perturbation recovery rates, and strict-future contraction metrics;
- added checkpointed JSONL/CSV/status/summary output after completed jobs;
- added hard-cap timeout salvage that cancels unfinished work and writes partial
  summaries.

Primary result:

- `docs/research_notes/validation_results/rfs0_strict_reachable_futures_small_smoke_result.md`
- `results/rfs0/20260522_strict_reachable_futures_small_smoke/summary.md`

Run shape:

```text
systems:
  108

regimes:
  balanced, permissive, harsh, repair_rich, commit_rich, capacity_tight

controls:
  structured
  dense_permissive_control
  dead_control
  random_edge_control
  shuffled_admissibility_control
  no_perturbation_control

workers:
  18

elapsed:
  about 6 seconds

errors:
  0
```

Timeout salvage test:

```text
cap:
  1 second

completed rows:
  13

status:
  TIMED_OUT

artifact status:
  systems.jsonl, results.csv, summaries, status.json, and summary.md retained
```

Interpretation:

- exact computation is cheap at this scale;
- structured substrate produced sparse nonzero strict kernels in balanced,
  repair-rich, and commit-rich regimes;
- permissive regime and dense control are too large/trivial;
- harsh and capacity-tight regimes collapse to zero strict viability;
- random-edge and shuffled-admissibility controls remain too strong, so control
  separation is not yet adequate;
- contraction events exist, but expansion events are absent under the current
  metric.

Current read:

```text
RFS0 is promising as a measurement floor, but not ready for a longer validation
run as-is. Next small probe should improve control separation, contraction
geometry, and parameter resolution without loosening K_strict just to get more
positives.
```

## 2026-05-21

### VAL1-MF Interference Audit Smoke

Implemented the sampled counterfactual interference audit requested by
`docs/VAL1_MF_INTERFERENCE_AUDIT_SPEC.md`.

Code changes:

- added `omega/val1_mf/run_interference_audit.py`;
- reused the existing two-field generator;
- added coupling masks for uncoupled, full, enable-only, obstruct-only,
  restore-only, commit-only, and shared-capacity-only modes;
- made sampled alive / terminal deltas primary;
- retained raw joint enumeration only as a diagnostic.

Primary result:

- `docs/research_notes/validation_results/val1_mf_interference_audit_smoke_result.md`
- `results/val1_mf/20260521_interference_audit_smoke/summary.md`

Run shape:

```text
paired worlds:
  100

rollout_samples:
  256

horizon:
  d16

workers:
  18

elapsed:
  17.0 seconds

errors:
  0
```

Interpretation:

- sampled counterfactual measurement worked cleanly;
- full coupling improved mean joint alive probability from 0.734 to 0.816;
- `constructive_delta_bin` appeared in 22/100 rows;
- one provisional `A_local_dominance_bin` row appeared;
- no robust destructive or commit/obstruct-driven interference appeared;
- diagnostic enumeration still capped often, but it was no longer the primary
  evidence path.

Current read:

```text
VAL1-MF now has a viable sampled interference measurement pattern.
The visible object is constructive support/recovery, not yet destructive
pseudo-Omega-like interference. The next probe should target destructive
hazards with stricter alive/hazard metrics before scaling.
```

### VAL1-MF Two-Field Compatibility Smoke

Implemented the first minimal multifield compatibility smoke on top of VAL0-G.

Code changes:

- added `omega/val1_mf/coupled_grammar.py`;
- added `omega/val1_mf/metrics.py`;
- added `omega/val1_mf/run_smoke.py`;
- added joint-state enumeration, rollout terminal estimates, compatibility
  ratios, cap-hit reporting, and neutral compatibility bins.

Primary result:

- `docs/research_notes/validation_results/val1_mf_two_field_compatibility_smoke_result.md`
- `results/val1_mf/20260521_two_field_compatibility_smoke_cap4096/summary.md`

Run shape:

```text
paired worlds:
  150

workers:
  18

max_states_per_depth:
  4096

rollout_samples:
  128

elapsed:
  about 79 seconds

errors:
  0
```

Interpretation:

- the smoke completed cleanly and produced nondegenerate bins;
- `mutual_collapse_bin`, `joint_viable_bin`, and `uncoupled_parallel_bin`
  appeared in small non-censored counts;
- the dominant outcome was still `mixed_or_censored_bin`: 142/150 rows;
- aggregate joint cap hit rate was 0.947;
- naive two-field enumeration did not solve the cap problem and likely worsened
  it by multiplying reachable combinations.

Current read:

```text
Do not scale this exact two-field enumerator.
Multifield compatibility remains relevant, but the next probe should switch to
sampled or cap-aware compatibility estimates before a long run.
```

### VAL0-G Neutral Grammar Stability Probe

Implemented the second small VAL0-G forced-fit audit.

Code changes:

- added cap-hit fields through depth 32;
- added `coarse` and `full` signature modes;
- added downstream cut sensitivity alongside initial cut sensitivity;
- added neutral bin labels alongside interpretive class names;
- added signature, cap-hit, and cut-sensitivity summary outputs.

Primary result:

- `docs/research_notes/validation_results/val0_g_neutral_grammar_stability_probe_result.md`
- `results/val0_g/20260521_neutral_grammar_stability_probe_cap2048/summary.md`

Run shape:

```text
neutral_grammar_v1:
  250 seeds

guardrails:
  low_resolution_dense: 50 seeds
  brittle_peak: 50 seeds

signature modes:
  coarse
  full

rows:
  700

errors:
  0

max_states_per_depth:
  2048
```

Interpretation:

- multiple neutral bins appeared again;
- coarse/full signatures agreed at `0.996` for neutral rows;
- cap 512 vs 2048 did not collapse the neutral bin structure;
- high-mass classes remain heavily cap-censored at d16/d32;
- dense and brittle guardrails are cap-saturated and not semantically clean
  under the current classifier;
- downstream cut sensitivity adds useful information but should not yet be
  treated as an ontology-level metric.

Current read:

```text
VAL0-G remains on the right substrate.
The main risk is measurement censoring, not obvious generator fine-tuning.
Do not scale to a full atlas until cap-aware or sampled survival metrics are
added.
```

### VAL0-G Neutral Grammar Geometry Smoke

Implemented the first VAL0-G smoke substrate:

- `omega/val0_g/grammar.py`
- `omega/val0_g/metrics.py`
- `omega/val0_g/run_smoke.py`

Primary result:

- `docs/research_notes/validation_results/val0_g_neutral_grammar_smoke_result.md`
- `results/val0_g/20260521_neutral_grammar_smoke_v2/summary.md`

Run shape:

```text
neutral_grammar_v1:
  50 seeds

guardrails:
  low_resolution_dense: 12 seeds
  brittle_peak: 12 seeds

rows:
  74

errors:
  0
```

Interpretation:

- initial calibration was too expansion-heavy and saturated depth-16 descendant
  mass;
- a minimal v2 calibration broadened lower-enable, higher-obstruction, decay,
  and capacity-pressure regimes;
- v2 produced multiple post-hoc measured geometry classes:
  - `recoverable_basin_like`: 26 / 50 neutral rows;
  - `self_terminating`: 16 / 50 neutral rows;
  - `thin_ridge`: 6 / 50 neutral rows;
  - `deep_corridor_like`: 2 / 50 neutral rows.

Current read:

```text
VAL0-G passed minimal smoke.
It does not validate Omega.
It does justify a slightly larger stability probe with cap-hit reporting,
depth 32 if cheap, and a better brittle/thin-ridge guardrail.
```

### Public Reorientation Around VAL0-G

The public-facing repository orientation was updated after the VAL0-CT geometry
battery.

Current interpretation:

```text
VAL0-CT:
  useful first task-space calibration layer
  R1 anchor advantages reproduced
  dense controls remained clean
  broad held-out / unlabeled generalization not established

VAL0-G:
  current front edge
  neutral grammar geometry atlas
  asks whether recoverable-continuation geometries emerge without outcome labels
```

Reason for pivot:

- the 12h unlabeled geometry battery completed cleanly and preserved guardrails;
- corridor d8 did not survive scale as a robust predictor;
- candidate future-R0 variance was the best surviving weak hook;
- the project should now study geometry emergence directly rather than treating
  R1 victory as the object.

Updated entry points:

- `README.md`
- `docs/roadmaps/OMEGA_EXPERIMENTAL_ROADMAP.md`
- `docs/PUBLIC_RESULTS_INDEX.md`
- `docs/OMEGA_PROJECT_MANUAL.md`
- `docs/research_notes/validation_design/README.md`
- `results/val0_ct/README.md`
- `results/val0_g/README.md`

Next implementation target:

```text
Implement neutral_grammar_v1 smoke:
  survival curves
  descendant mass
  branching reproduction
  terminal probability
  cut sensitivity k=1
  dense/flat guardrail
```

## 2026-05-17

### Root Script Cleanup

Moved historical root-level Python probe scripts into:

- `scripts/historical_probes/`

Added:

- `scripts/historical_probes/README.md`

Reason:

- keep the repository front page clean for public readers;
- make VAL0-CT docs the obvious entry point;
- preserve old scripts for provenance, reproducibility, and failure analysis.

Historical report and log references were updated to point at the new script
paths.

### Root Result Folder Cleanup

Moved tracked historical result folders into:

- `results/historical_probes/`

Moved ignored local smoke, calibration, stress, and scratch result folders into:

- `results/local_runs/`

Added:

- `results/README.md`
- `results/historical_probes/README.md`
- `results/val0_ct/README.md`

Future VAL0-CT outputs should be written under:

```text
results/val0_ct/<timestamp-or-run-id>/
```

Do not add new root-level `*_results` folders.

### Public Reorientation Around VAL0-CT

The public-facing repository orientation was updated to make the Constructor
Theory / VAL0-CT pivot explicit.

Updated entry points:

- `README.md`
- `docs/roadmaps/OMEGA_EXPERIMENTAL_ROADMAP.md`
- `docs/PUBLIC_RESULTS_INDEX.md`
- `docs/OMEGA_PROJECT_MANUAL.md`
- `docs/current_theory/README.md`
- `docs/research_notes/validation_design/README.md`

Current front-door statement:

```text
VAL0-CT is the current validation target.
It tests whether persistence-conditioned reachability, R1, predicts
long-horizon reachability retention better than raw reachability, R0, and
equal-budget R0-lookahead controls in structured task algebras.
```

Public framing decision:

- COM/fiber work is historical evidence for viable propagation and
  coarse-graining discipline, not the current validation center.
- Trajectory-space probes are negative constraints and fakeout anatomy.
- CA/DAR/DAX probes calibrate the primitive floor rather than validating Omega
  proper.
- DAX-G5's failed held-out prediction is one of the reasons the project moved
  to task-space validation.

Next implementation target:

```text
Implement VAL0-CT smoke, CPU-first, using:
  low_resolution_dense
  structured_asymmetric
  lock_in_seeded

Compare:
  random
  R0
  R0_lookahead
  R1
  pseudo_omega
```

## 2026-05-16

### Formal-Stack Recenter: Primitive Floor to Valuer-Level Omega

New theory notes were added under:

- `docs/research_notes/omega_theory/`
- `docs/research_notes/primitive_branch/`

New canonical entry points:

- `docs/research_notes/omega_theory/formal_stack_v0.md`
- `docs/research_notes/omega_theory/omega_glossary.md`
- `docs/research_notes/omega_theory/omega_as_viable_value_bearing_trajectory_space.md`
- `docs/research_notes/omega_theory/regenerative_filtering_slack_and_parasitic_modes.md`
- `docs/research_notes/primitive_branch/relation_as_historical_binding.md`
- `docs/research_notes/primitive_branch/omega_meets_fep.md`
- `docs/research_notes/primitive_branch/valuerhood_as_recoverable_historical_identity.md`

Current working stack:

```text
distinction
-> asymmetry
-> relation / causal continuity
-> identity
-> recoverability
-> valuerhood
-> viability
-> Omega-compatible viability
-> lushness of value-bearing trajectory space
```

Core thesis now tracked in the manual:

```text
Omega is the asymptotic compatibility structure of value-bearing trajectory
space.
```

Interpretive update:

- Relation is now treated as causal continuity through transformation, not
  merely graph adjacency, neighbor dependence, coupling, or social relation.
- Identity is organized causal continuity through change.
- Recoverability is perturbation-continuability, not exact restoration.
- A valuer is a bounded historical identity for which different continuations
  asymmetrically affect recoverable continuability.
- Viability is a gate; nested, compatible, value-bearing trajectory richness is
  the target.

Consequence for prior executable work:

- COM fiber transport remains the strongest toy-substrate witness for viable
  propagation and coarse-graining discipline.
- Trajectory-space probes remain useful negative constraints and fakeout
  anatomy.
- CA, DAR, and DAX probes are now explicitly primitive-floor calibration unless
  they include minimal valuerhood and recoverable continuability.
- DAX-G5's failed held-out prediction is consistent with this boundary: it
  describes motif ecology in a primitive rule space, not a validation-ready
  Omega detector.

Roadmap decision:

```text
The next Omega-proper validation family should be a minimal valuer-world
benchmark, not another bare cellular or field-dynamics scale-up.
```

Probe V0 target:

- construct minimal self-maintaining valuers;
- include perturbation recovery, path consequence, and action or interaction
  channels;
- measure Omega-level predictors against survival, reward, reachability,
  empowerment, and local-viability baselines;
- include fakeout controls for stasis, clocks, lock-in, externally maintained
  persistence, and high reachability without self-maintenance.

## 2026-05-11

### Progenitor Drafts Added

Added the early theory-side papers to:

- `docs/progenitor_drafts/`

Status:

- drafts only;
- early theoretical provenance;
- not current validation results;
- not final claims about the formal object.

Included PDFs:

- `intelligent_agency_under_computational_irreducibility.pdf`
- `scaling_paper_v2.pdf`
- `telos_2_0_draft.pdf`
- `echo_rosetta_version.pdf`
- `gradient_ethics.pdf`
- `gradient_field_theory_of_value_v51.pdf`

### Current Theory And Trajectory-Space Notes Added

Added the current theory/status draft to:

- `docs/current_theory/omega_signature_v0_1.pdf`

Status:

- current draft artifact;
- not peer reviewed;
- not a validation result by itself;
- best current written entry point into the Omega claim ladder and COM witness.

Added trajectory-space branch notes to:

- `docs/research_notes/trajectory_space/trajectory_space_omega_research_note.pdf`
- `docs/research_notes/trajectory_space/trajectory_space_omega_triage_note.pdf`

Status:

- draft research notes;
- branch-selection/planning artifacts;
- not replacements for the current COM fiber-transport witness.

Framing decision:

- `Project_Omega.pdf` is treated as a current theory/status draft.
- The trajectory-space PDFs are treated as active research branch notes.
- The earlier PDFs remain under `docs/progenitor_drafts/` as historical
  provenance.

### Repository Setup

- Local repo pushed to GitHub:
  - https://github.com/6ixpoolgames/Omega
- Current pushed baseline before this log:
  - `cd0fe04 Initial Omega validation workspace`
  - `88d0fa3 Add Probe 10 COM robustness results`

### Current State

The strongest current toy-substrate object is:

```text
F,T attractive coupling
kappa = center_of_mass
alpha = 0.45, 0.50, 0.525
T = 900, 1500, 2400
```

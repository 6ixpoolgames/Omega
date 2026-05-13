# Public Results Index

This repository intentionally exposes only the most relevant current result
artifacts. Older exploratory outputs remain summarized in the manual/running log
but are not tracked as top-level result folders.

## Current Result Sets

## Theory-Side Progenitor Drafts

Directory:

- `docs/progenitor_drafts/`

Status:

- early theoretical work and drafts only;
- included for provenance;
- not current validation results;
- not a substitute for the executable probe outputs below.

## Current Theory Draft

Directory:

- `docs/current_theory/`

Status:

- current draft/status artifact;
- not peer reviewed;
- not a validation result by itself;
- intended as the main theory-side entry point for the current COM witness and
  claim ladder.

## Trajectory-Space Research Notes

Directory:

- `docs/research_notes/trajectory_space/`

Status:

- draft research notes;
- planning/triage material for a possible trajectory-space branch;
- not a replacement for the current COM fiber-transport witness.

## Primitive-Branch Research Notes

Directory:

- `docs/research_notes/primitive_branch/`

Status:

- active conceptual notes for the distinction/asymmetry/relation branch;
- not validation results by themselves;
- used to motivate DA0b relation-as-connection tests.

### Probe 09: Robust Fiber Reachability

Directory:

- `probe_09_robust_fiber_reachability_results/`

Primary files:

- `summary.json`
- `viable_propagation_summary.csv`
- `baseline_comparisons.csv`
- `bootstrap_intervals.csv`
- `breadth_depth_decomposition.csv`

Reason retained:

- Probe 09 is where the current candidate object was isolated:
  `center_of_mass` multi-step viable propagation through certified fibers.

### Probe 10: COM Robustness, Extended Run

Directory:

- `probe_10_com_viable_propagation_robustness_extended_results/`

Primary files:

- `summary.json`
- `robustness_by_family.csv`
- `robustness_by_variant.csv`
- `propagation_deltas.csv`
- `bootstrap_intervals.csv`
- `perturbation_metadata.csv`

Reason retained:

- This is the broad robustness run with controls across perturbation families.

### Probe 10: Targeted Fragility Refinement

Directory:

- `probe_10_com_targeted_fragility_refinement_results/`

Primary files:

- `summary.json`
- `robustness_by_family.csv`
- `robustness_by_variant.csv`
- `propagation_deltas.csv`
- `bootstrap_intervals.csv`

Reason retained:

- This is the higher-coverage COM-only refinement for the weaker perturbation
  families: noise, potential shape, and time discretization.

### Probe 11: Learned Predictive Kappa

Directory:

- `probe_11_learned_predictive_kappa_revised_results/`

Primary files:

- `summary.json`
- `learned_kappa_validation_loss.csv`
- `learned_kappa_test_propagation.csv`
- `learned_vs_com_comparison.csv`
- `learned_vs_random_matched.csv`
- `learned_label_anatomy.csv`
- `bootstrap_intervals.csv`

Reason retained:

- Probe 11 is the first learned-quotient test. It asks whether a simple
  predictive k-means quotient can discover viable propagation without being
  handed COM bins as labels.

Result in one line:

- The learned quotients found partial propagation-positive structure, but did
  not recover COM as a strong coordinate and mostly underperformed or fragmented
  on heldout moderate perturbations.

### Probe 12: COM Formalization + Learned-Kappa Diagnosis

Directories:

- `probe_12_batch_results/`
- `probe_12a_com_formal_object_audit_results/`
- `probe_12b_learned_kappa_failure_diagnosis_results/`
- `probe_12c_improved_learner_smoke_results/`

Primary files:

- `probe_12_batch_results/batch_summary.json`
- `probe_12_batch_results/recommended_next_step.md`
- `probe_12a_com_formal_object_audit_results/summary.json`
- `probe_12a_com_formal_object_audit_results/com_threshold_sensitivity.csv`
- `probe_12a_com_formal_object_audit_results/com_vs_controls_summary.csv`
- `probe_12b_learned_kappa_failure_diagnosis_results/summary.json`
- `probe_12b_learned_kappa_failure_diagnosis_results/learned_vs_com_anatomy_summary.csv`
- `probe_12c_improved_learner_smoke_results/summary.json`

Reason retained:

- Probe 12 separates the current COM witness from learned-kappa failure modes.
  It is the strongest current bridge between empirical probes and formal object
  definition.

Large local-only files:

- Probe 12A also writes full node, edge, path, and component-projection tables.
  Those are retained locally but not tracked in Git because they are large
  generated anatomy tables, including files above GitHub's normal size limits.

Result in one line:

- COM remains a positive fiber-transport witness; learned k-means mostly fails
  by splitting/merging COM fibers and inflating small-fiber structure; the next
  step is formal COM fiber transport, not scaling learned-kappa.

### Probe T0: Trajectory-Space Branch Triage

Directory:

- `probe_T0_trajectory_space_branch_triage_results/`

Primary files:

- `summary.json`
- `branch_scores.csv`
- `trajectory_concentration.csv`
- `component_balance.csv`
- `predictive_temporal_dependence.csv`
- `baseline_comparisons.csv`
- `bootstrap_intervals.csv`

Reason retained:

- Probe T0 is the first quotient-light trajectory-space branch selector. It
  asks which field-dynamics readouts are worth formalizing next without treating
  the result as a validation claim.

Result in one line:

- The best trajectory-space follow-up is viable trajectory geometry:
  concentration-collapse and component-balance scored highest, while
  hazard/restoration mostly tracked raw viability.

### Probe T1: Viable Trajectory Geometry

Directory:

- `probe_T1_viable_trajectory_geometry_results/`

Primary files:

- `summary.json`
- `geometry_metrics.csv`
- `temporal_geometry.csv`
- `component_balance.csv`
- `null_deltas.csv`
- `metric_correlations.csv`
- `bootstrap_intervals.csv`
- `gpu_timing_diagnostics.csv`

Reason retained:

- Probe T1 is the direct falsification pass for the T0-selected
  trajectory-geometry branch.

Result in one line:

- Simple effective-rank/collapse geometry did not survive the controls:
  component balance failed, noise/time-shuffle controls scored high, and rigid
  collapse exposed scale-invariance in the lead rank metric.

### Probe T1F: Ordered Trajectory Structure Atlas

Directory:

- `probe_T1F_ordered_trajectory_structure_atlas_results/`

Primary files:

- `summary.json`
- `readout_family_scores.csv`
- `ordered_distinction_persistence.csv`
- `temporal_dependence_proxy.csv`
- `component_temporal_continuity.csv`
- `minimal_recoverable_continuation.csv`
- `false_positive_control_results.csv`
- `null_deltas.csv`
- `gpu_timing_diagnostics.csv`

Reason retained:

- Probe T1F is the stricter trajectory-native follow-up after T1. It asks
  whether ordered distinction structure survives the T1 failure modes.

Result in one line:

- Ordered readouts are diagnostically useful and reject noise fakeout, but they
  still fail endpoint/single-component false positives and the global component
  continuity guardrail.

### Probe I0: Invariant Stack Audit

Directory:

- `probe_I0_invariant_stack_audit_results/`

Primary files:

- `summary.json`
- `invariant_scores.csv`
- `stack_ablation_results.csv`
- `known_false_positive_rejection.csv`
- `holdout_generalization.csv`
- `threshold_sensitivity.csv`
- `metric_correlations.csv`
- `gpu_timing_diagnostics.csv`

Reason retained:

- Probe I0 is the final stacked-invariant audit of the trajectory-native branch.
  It tests whether single-Omega-style invariants can jointly reject fakeouts
  while retaining the coupled target condition.

Result in one line:

- The ablation is negative: stronger stacks reject known controls and holdouts,
  but coupled retention collapses to zero, so the trajectory-native invariant
  branch is demoted.

### Probe I0b: Invariant Threshold and Dropout Audit

Directory:

- `probe_I0b_invariant_threshold_dropout_audit_results/`

Primary files:

- `summary.json`
- `closure_recommendation.md`
- `dropout_by_invariant.csv`
- `threshold_family_sensitivity.csv`
- `soft_stack_results.csv`
- `pareto_profile_results.csv`
- `coupled_vs_control_auc.csv`
- `i5_recoverability_audit.csv`
- `i6_horizon_coherence_audit.csv`

Reason retained:

- Probe I0b closes the I0 question cleanly by testing whether the failure was a
  hard-threshold or strict-conjunction artifact.

Result in one line:

- Partial continuous/Pareto separation exists, but no hard or soft stack meets
  the branch-reopen criteria; close trajectory-native invariants for now.

## Current Public Interpretation

The current executable candidate is:

```text
COM-like multi-step viable propagation through certified fibers
in the F,T attractive multifield toy substrate
```

Probe 11 updates the interpretation:

```text
The COM object remains the stronger analytic coordinate. Simple learned
predictive quotients can see part of the signal, but are not yet a replacement
for COM.
```

Probe 12 updates the project direction:

```text
Formalize the COM fiber-transport witness before broadening the substrate or
scaling learned-kappa methods.
```

Probe T0 adds a parallel roadmap branch:

```text
If we pursue trajectory-space dynamics directly, start with viable trajectory
geometry and keep component-balance as the main non-redundancy guardrail.
```

Probe T1 updates that branch:

```text
Do not scale simple trajectory effective-rank geometry yet. Treat it as a
diagnostic until the failure modes and component-erasure problem are understood.
```

Probe T1F updates it further:

```text
Demote the trajectory-native branch for now. Ordered distinction readouts are
diagnostic, not yet object-defining.
```

Probe I0 closes the current trajectory-native attempt:

```text
The invariant stack rejects fakeouts by becoming too strict. It is not a viable
object witness; return to COM fiber-transport formalization.
```

Probe I0b confirms that closure:

```text
Threshold relaxation recovers some coupled retention but loses control
rejection; soft stacks do not rescue the branch.
```

### Probe 13b: Fiber-Transport False-Positive Refinement

Directory:

- `probe_13b_fiber_transport_false_positive_refinement_results/`

Primary files:

- `summary.json`
- `refined_fiber_transport_summary.csv`
- `component_necessity_results.csv`
- `temporal_edge_order_integrity.csv`
- `within_fiber_diversity.csv`
- `late_horizon_transport_retention.csv`
- `priority_false_positive_results.csv`
- `ablation_results.csv`

Reason retained:

- Probe 13b records the targeted smoke refinement after Probe 13 found that the
  formal fiber-transport definition still admitted key false positives.

Result in one line:

- COM remains base-null positive, but the refined object fails component
  necessity, within-fiber nondegeneracy, and delayed-trap/late-retention
  guardrails at smoke scale.

### Probe DA0: Distinction / Asymmetry / Relation

Directory:

- `probe_DA0_distinction_asymmetry_relation_results/`

Primary files:

- `summary.json`
- `world_configurations.csv`
- `dar_profile_by_world.csv`
- `lineage_metrics.csv`
- `asymmetry_metrics.csv`
- `relation_metrics.csv`
- `structured_richness.csv`
- `ablation_results.csv`
- `control_rejection.csv`

Reason retained:

- Probe DA0 is the first primitive-branch triage after trajectory-native and
  formal fiber-transport routes failed to produce a clean object.

Result in one line:

- Full DAR is the best aggregate smoke world, but the relation-shuffled control
  is not rejected, so the primitive branch is not ready for main-scale
  validation.

### Probe DA0b: Relational Connection and Closure

Directory:

- `probe_DA0b_relational_connection_closure_results/`

Primary files:

- `summary.json`
- `relation_identity_persistence.csv`
- `connection_predictivity.csv`
- `relation_conditioned_lineage.csv`
- `closure_without_lockin.csv`
- `viable_slack_profile.csv`
- `control_rejection.csv`
- `world_rankings.csv`

Reason retained:

- Probe DA0b tests relation as persistent causal-history dependence rather than
  generic coupling.

Result in one line:

- Random-stepwise relation is rejected, but lock-in and independent distinction
  controls dominate key scores, so DA0b is not ready for main-scale validation.

### Probe DA1: Viable Slack Phase Sweep

Directory:

- `probe_DA1_viable_slack_phase_sweep_results/`

Primary files:

- `summary.json`
- `phase_points.csv`
- `phase_classification.csv`
- `relation_lineage_excess.csv`
- `closure_metrics.csv`
- `recoverable_alternatives.csv`
- `lock_in_metrics.csv`
- `control_positions.csv`

Reason retained:

- Probe DA1 tests the explicit phase hypothesis that Omega-like structure may
  live between underconstraint/noise and overconstraint/lock-in.

Result in one line:

- Positive relation-lineage excess appears, but the best point is an extreme and
  controls are not classified correctly; DA1 should not be scaled yet.

### Probe DA1b: Apparent Slack vs Viable Slack

Directory:

- `probe_DA1b_apparent_vs_viable_slack_results/`

Primary files:

- `summary.json`
- `diagnostic_targets.csv`
- `asymmetry_load_bearing.csv`
- `relation_load_bearing.csv`
- `future_distinct_alternatives.csv`
- `dynamic_lock_in.csv`
- `viable_slack_diagnostic_profile.csv`
- `classification_results.csv`
- `control_rejection.csv`

Reason retained:

- Probe DA1b diagnoses whether DA1's alternatives are asymmetric,
  relation-conditioned, future-distinct viable slack, or merely apparent slack
  from symmetry, lock-in, independent sites, or microstate multiplicity.

Result in one line:

- DA1b rejects the prior lock-in and symmetric false positives as viable slack,
  but the extreme corner remains strongest and is itself classified as apparent
  slack; revise the DA1 world design before scaling.

The important public caveat:

```text
These are toy-substrate validation probes. They do not prove the broader Omega
theory. They provide a candidate object, controls, and failure modes.
```

## Why Older Results Are Hidden From The Main Tree

Older probes are valuable internally, but public readers do not need every
intermediate CSV/plot to understand the current state. They are summarized in:

- `docs/OMEGA_PROJECT_MANUAL.md`
- `docs/OMEGA_RUNNING_LOG.md`

If older artifacts need to be restored publicly, they can be regenerated from
the scripts or recovered from local storage/history.

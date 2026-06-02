# Future Field Atlas Substrate Morphology Sweep Spec

Status: completed; retained morphology atlas continues to be regenerated after coupled runs  
Project posture: atlas-first, no Omega claims  
Target package: `omega.future_field_atlas`  
Preferred new utility: `omega.future_field_atlas.substrate_morphology_summary`

## 0. Purpose

Future Field Atlas should now live up to its name.

The next empirical move is not another single-operator ladder and not broad H128
scale expansion. The goal is to map what future-field structures already exist
in the current substrate.

Central question:

```text
What future-field morphology is present in the current finite substrate before
we overfit to a hand-designed coupled operator?
```

This pass should classify raw geometry, not interpret it as Omega, support,
capture, erasure, identity, agency, value, or compatibility.

## 1. Context

Recent coupled runs established:

```text
H64 pair8 broad sweep:
  clean, complete, reconstruction-passing, operationally manageable

H64 coupling ladder:
  zero penalty differed from positive penalty;
  positive strengths 0.05 through 0.50 collapsed at that resolution

H64 mechanism-resolution pass:
  near-zero strengths 0.001 through 0.010 are distinguishable;
  0.020 and 0.050 saturate to the same compact topology digest;
  true product selector differs from zero-penalty joint rank-prefix selection;
  pair005 remains a heavy-pair / critical-pair clue and persists in targeted H128
```

Current interpretation:

```text
The current rank-boundary mismatch operator has taught us about scalar
thresholding and pair heterogeneity, but it should not be treated as the only
source of coupled structure.

Before designing richer operators, we need a morphology map of the substrate.
```

## 2. Claim boundary

Allowed claims:

```text
The sweep maps raw future-field morphology in the current finite substrate.

The sweep identifies field, pair, horizon, observable, and operator regimes that
are geometrically distinct under FFA metrics.

The sweep identifies candidate high-yield regions for later exact operator tests.
```

Blocked claims:

```text
Omega validation
proto-Omega detection
agency
identity
valuerhood
value
support
capture
erasure
compatibility
causal interaction
life / self-replication
candidate promotion
holdout readiness
```

## 3. 3P criteria

### Principled

Map topology and deformation before naming them.

Use declared FFA artifacts:

```text
frontier profiles
rank-boundary geometry
joint-vs-product residuals
marginal retention
composition residuals
artifact completeness
reconstruction audits
formal operator/spec identities
```

### Parsimonious

Prefer postprocessing existing retained outputs first.

Add new scans only where existing data is insufficient.

Do not add semantic labels.

### Predictive / revelatory

The morphology atlas should produce testable next-run targets:

```text
which pairs are heavy / light / joint-restrictive;
which horizons exhibit onset or divergence;
which operators are structurally distinct;
which observables show robust channeling;
which regimes are worth testing with shared-capacity coupling.
```

## 4. Implementation plan

### Phase A: Postprocess existing FFA runs

Build a new utility:

```text
omega.future_field_atlas.substrate_morphology_summary
```

Inputs should be one or more FFA run directories and/or compact retention summary
directories.

Minimum accepted inputs:

```text
single-field H128 calibration summary
coupled H64 broad sweep summary
coupled H64 ladder summary
coupled H64 mechanism-resolution summary
pair005 targeted summaries
```

The utility should not require raw spools if compact summaries are sufficient.

Suggested CLI:

```text
python -m omega.future_field_atlas.substrate_morphology_summary \
  --out results/future_field_atlas/20260602_substrate_morphology_atlas_summary/ \
  --runs <run_or_summary_dir_1> <run_or_summary_dir_2> ... \
  --include-existing-retention-summaries \
  --write-report
```

If exact paths are hard to standardize, support a manifest file:

```text
--run-manifest <path listing run_id, run_kind, local_path, notes>
```

### Phase B: Fill gaps with small targeted scans only if needed

Only if existing summaries cannot answer morphology questions, run targeted H64
scans.

Potential targeted fills:

```text
product_selector H64 pair8 if not already retained
joint_energy_rank_prefix 0.000 H64 pair8
rank_boundary_mismatch 0.020 H64 pair8
pair005 H64/H128 retained summaries
```

Do not run broad H128.

## 5. Required outputs

Create:

```text
field_morphology_summary.csv
pair_morphology_summary.csv
operator_sensitivity_summary.csv
horizon_onset_summary.csv
observable_geometry_summary.csv
pair_class_exemplar_summary.csv
morphology_next_targets.csv
substrate_morphology_manifest.json
substrate_morphology_report.md
```

Optional, if available from existing data:

```text
rank_boundary_offset_morphology.csv
joint_candidate_crossing_morphology.csv
composition_residual_morphology.csv
frontier_growth_regime_summary.csv
```

## 6. Field morphology summary

`field_morphology_summary.csv`

One row per single-field condition/start or equivalent retained unit.

Required columns where available:

```text
run_id
condition_id
start_index
state_space_id
law_id
selection_operator_id
observable_set_id
horizon_max
artifact_completeness_status
reconstruction_audit_status

frontier_count_h0
frontier_count_h_final
frontier_count_max
frontier_growth_ratio_final_vs_h0
frontier_growth_ratio_max_vs_h0
frontier_entropy_final
frontier_entropy_max
component_count_final
component_count_max
largest_component_fraction_final

rank_boundary_inside_fraction_mean
rank_boundary_outside_fraction_mean
transport_composition_residual_mean
transport_composition_residual_max
```

If a field is unavailable from compact summaries, leave blank rather than
recomputing from unavailable raw spools.

## 7. Pair morphology summary

`pair_morphology_summary.csv`

One row per pair per operator/run, with pair-aware metrics.

Required columns:

```text
run_id
pair_id
pair_index
operator_family
coupled_operator_id
joint_selection_family
coupling_strength
horizon_max
artifact_completeness_status
reconstruction_audit_status

product_joint_support_final
coupled_joint_support_final
joint_support_residual_final
joint_support_residual_mean
joint_support_residual_max

joint_retention_final
joint_retention_mean
joint_retention_min

A_marginal_retention_final
B_marginal_retention_final
A_marginal_retention_mean
B_marginal_retention_mean

joint_density_vs_marginal_product_final
joint_density_vs_marginal_product_mean

frontier_node_rows
frontier_edge_rows
output_size_mb_if_available
```

Derived raw morphology classes are allowed if purely descriptive:

```text
pair_size_class:
  light
  medium
  heavy

joint_residual_class:
  low_residual
  medium_residual
  high_residual

marginal_retention_class:
  marginal_preserving
  marginal_loss_A
  marginal_loss_B
  marginal_loss_both

joint_density_class:
  product_dense
  product_sparse
  joint_restrictive
```

Do not use terms:

```text
support
capture
erasure
compatibility
identity
agency
```

## 8. Operator sensitivity summary

`operator_sensitivity_summary.csv`

Compare operators/settings over the same pair/horizon design.

Required comparisons:

```text
product selector
joint_energy_rank_prefix at 0.000
rank_boundary_mismatch at 0.001 / 0.002 / 0.005 / 0.010 / 0.020 / 0.050
rank_boundary_mismatch at 0.25 / 0.50 if retained
```

Required columns:

```text
comparison_id
pair_id
baseline_operator
comparison_operator
baseline_coupling_strength
comparison_coupling_strength
horizon
metric_name
baseline_value
comparison_value
delta
relative_delta
same_compact_digest_flag_if_available
```

At minimum, cover:

```text
joint_support_residual_fraction
joint_retention_fraction
A_marginal_retention_fraction
B_marginal_retention_fraction
coupled_joint_support_count
product_joint_support_count
joint_density_vs_marginal_product
```

## 9. Horizon onset summary

`horizon_onset_summary.csv`

Purpose: identify when deformation appears.

Required columns:

```text
run_id
pair_id
operator_family
coupling_strength
comparison_reference
metric_name
threshold
first_horizon_crossing_threshold
max_delta_horizon
final_horizon_value
max_horizon_value
onset_class
```

Suggested onset classes:

```text
early_onset
mid_onset
late_onset
terminal_only
transient
no_detected_onset
```

Keep these descriptive. Do not interpret them as agency/capture/etc.

## 10. Observable geometry summary

`observable_geometry_summary.csv`

Purpose: assess whether structure is specific to one observable or robust across
declared observables.

Initial observables:

```text
symbol_histogram_distance
hamming_weight_or_nonzero_count if retained
total_coordinate_mass if retained and paired baselines are valid
rank_boundary_offset
frontier component / component id if available
```

Required columns:

```text
observable_id
observable_family
run_id
condition_or_pair_id
horizon_max
geometry_metric
value_mean
value_max
value_final
artifact_completeness_status
notes
```

If only `symbol_histogram_distance` is currently available, the summary should
explicitly report:

```text
observable_coverage: single_observable_only
```

This prevents overclaiming invariant robustness.

## 11. Pair class exemplars

`pair_class_exemplar_summary.csv`

Purpose: identify high-yield examples for future operator tests.

Required columns:

```text
pair_id
class_reason
run_id
operator_family
coupling_strength
horizon
joint_residual
joint_retention
A_marginal_retention
B_marginal_retention
edge_rows
node_rows
recommended_followup
```

Example class reasons:

```text
heaviest_pair
highest_joint_residual
lowest_joint_retention
marginal_preserving_joint_restrictive
stable_low_residual
late_onset_divergence
pair005_like
```

Again, no support/capture/erasure labels.

## 12. Morphology next targets

`morphology_next_targets.csv`

Purpose: convert atlas results into next-run recommendations.

Required columns:

```text
target_id
target_type
reason
recommended_operator
recommended_horizon
recommended_pairs
required_controls
expected_disambiguation
claim_boundary
```

Expected target types:

```text
operator_test
pair_forensics
horizon_depth_check
observable_extension
shared_capacity_candidate
rank_order_native_candidate
```

## 13. Morphology report

`substrate_morphology_report.md`

Suggested structure:

```text
1. Summary
2. Inputs and retained runs
3. Gate and completeness status
4. Field morphology
5. Pair morphology
6. Operator sensitivity
7. Horizon onset
8. Observable coverage
9. Pair exemplars
10. Recommended next targets
11. Claim boundary
```

The report should explicitly answer:

```text
What morphology exists in the current substrate?
Which pairs/operators/horizons are high-yield?
Is pair005 unique or part of a class?
Is current structure observable-specific?
Which operator should be tested next?
```

## 14. Decision logic

### If pair005 is unique

```text
Treat pair005 as a structural artifact / special exemplar.
Do not build the next branch around it.
Use it only as a stress test.
```

### If pair005 belongs to a class

```text
Define the class descriptively.
Use multiple class exemplars in the next operator test.
```

### If most product-vs-coupled structure is joint-only with marginals preserved

```text
Prioritize shared-capacity and rank-order-native operators.
These can test whether joint restriction becomes recoverable/non-erasing or
merely narrowing.
```

Post-smoke update:

```text
shared_capacity v1 was tested and should not be scaled as-is. It produced
marginal pruning followed by dense closure over surviving marginals, not
marginal-preserving joint restriction.

rank_order_boundary was then tested and recovered the small-set
marginal-preserving joint-restriction pattern. The medium sweep and neighbor /
observable sweep are now complete. The current target is rank_order_boundary
class expansion with pair005, pair012, and pair014.
```

### If marginal loss appears under some operators

```text
Flag those regimes for later non-erasure/collapse audits.
Do not call them erasure yet.
```

### If observable coverage is single-observable only

```text
Do not claim invariant robustness.
Recommend an observable-extension pass before theory promotion.
```

### If morphology classes are weak or dominated by frontier size

```text
Treat current substrate as limited.
Do not scale up blindly.
Consider new substrate families or quotient diagnostics.
```

## 15. Optional new operator scan after morphology summary

Only after morphology summary is produced, spec a small shared-capacity operator
smoke.

Post-smoke update:

```text
This was completed in
docs/research_notes/validation_results/future_field_atlas/future_field_atlas_shared_capacity_h64_smoke_result.md.
The follow-up rank_order_boundary smoke was also completed in
docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_h64_smoke_result.md.
The rank_order_boundary medium sweep and neighbor / observable sweep were also
completed. The next operator branch should be rank_order_boundary class
expansion, with marginal-coverage-preserving shared-capacity v2 retained only
as a repair option if finite capacity remains theory-critical.
```

Provisional shared-capacity idea:

```text
product candidates exist as before;
joint future field has a shared continuation budget K;
selection ranks joint candidates by declared energy or boundary ordering;
A and B do not receive independent guaranteed successor budgets.
```

Initial shared-capacity smoke should be:

```text
H64
pair_count: selected 4 to 8 pairs from morphology_next_targets
product selector reference
joint rank-prefix reference
shared-capacity operator
complete artifacts required
pair-aware summary required
```

Do not implement this until morphology atlas indicates target pairs.

## 16. Acceptance criteria

This sweep set succeeds if it produces:

```text
a clean morphology report;
pair-aware morphology classes;
operator sensitivity summary;
horizon onset summary;
observable coverage statement;
next target table;
clear recommendation for either shared-capacity, rank-order-native, or substrate redesign.
```

It fails if:

```text
the report mainly repeats aggregate residuals;
pair005 is overinterpreted;
semantic labels are introduced;
observable coverage is overclaimed;
truncated outputs are treated as interpretable;
or the next operator recommendation is not grounded in morphology.
```

## 17. Summary instruction to Codex

Build a morphology atlas over existing Future Field Atlas outputs.

Do not broaden to H128.

Do not add Omega labels.

Do not interpret support/capture/erasure.

Classify raw geometry only.

Use the result to choose the next operator.

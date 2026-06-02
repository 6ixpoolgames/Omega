# Future Field Atlas Formal Interface Distinction Panel Spec

Status: spec inbox / pending implementation  
Project posture: formal-interface mode, no Omega claims  
Runner target: `omega.future_field_atlas.run_coupled_future_field_atlas`  
Preferred new postprocessor: `omega.future_field_atlas.formal_interface_distinction_panel`

## 0. Purpose

The current Future Field Atlas mechanism branch has largely answered the first
rank-order-boundary question:

```text
rank_order_boundary is no longer a pair005-only artifact;
the current symbol_histogram_distance high-yield representative set is:
  pair005
  pair012
  pair014
  pair026
```

The next useful empirical move for the theory arm is **not** broad H128 and not
another open-ended mechanism hunt.

The goal of this spec is to shift Future Field Atlas into **formal-interface
mode**: emit the first reconstructible finite distinction-measure artifacts and a
compact representative/control panel that can later support identity-decay-null,
maintenance-gap, process-bundle, and compatibility-audit work.

Central question:

```text
Can the current FFA outputs be converted into declared, reconstructible finite
distinction-measure rows over high-yield representatives and controls, with
operator references, horizon persistence, and joint-vs-marginal distinction
retention reported under strict claim boundaries?
```

This is a measurement-interface pass, not a semantic promotion pass.

## 1. Background

The active theory arm now includes:

```text
finite_distinction_measures_v0.md
identity_decay_null_taxonomy_v0.md
compatibility_audit_taxonomy_v0.md
finite_proto_valuer_separation_theorems_v0.md
tiny_transition_system_witnesses_v0.md
```

Those notes require future empirical artifacts such as:

```text
distinction_measure_manifest.csv
distinction_measure_by_horizon.csv
process_bundle_manifest.csv or candidate_designation_manifest.csv
identity_decay_null_manifest.csv
maintenance_gap_by_horizon.csv
perturbation_semantics_manifest.csv
compatibility_audit_summary.csv
```

This spec implements only the first step:

```text
declared finite distinction measures over existing FFA coupled geometry.
```

It does not implement identity-decay nulls, maintenance gaps, self-conditioning,
or compatibility audits yet.

## 2. Claim boundary

Allowed claims:

```text
The pass emits reconstructible finite distinction-measure artifacts for selected
FFA coupled runs.

The pass compares rank_order_boundary high-yield representatives and controls
against product, zero-penalty joint rank-prefix, scalar mismatch 0.020, and
shared_capacity v1 references where available or newly run.

The pass reports whether the marginal-preserving joint-restriction signature is
persistent over horizon and whether it is operator-specific under declared
finite distinction measures.
```

Blocked claims:

```text
Omega validation
proto-valuer detection
valuer detection
agency / identity / value
compatibility detection
support / capture / erasure
interaction detection
identity-decay null success
maintenance-gap success
self-conditioning
holdout readiness
substrate-general theory claim
```

Terminology rule:

```text
Use candidate_designation, representative, control, distinction_measure,
joint_vs_marginal_retention, operator_delta, horizon_persistence.

Do not use proto-valuer, valuer, agent, self, identity, support, capture,
erasure, compatibility, or Omega as output labels.
```

## 3. 3P criteria

### Principled

Use only declared finite distinction measures from `finite_distinction_measures_v0.md`:

```text
binary observable recovery / indicator rows;
frontier or quotient support counts where reconstructible;
persistent / recurrent distinction counts over declared horizon windows;
joint-vs-marginal distinction retention;
measure-plus-reference deltas, but not identity-decay-null gaps.
```

### Parsimonious

Prefer postprocessing existing retained FFA outputs first.

Run new H64 panel cells only when required references are missing for the
representative/control set.

Do not run broad H128.

Do not emit raw spools as retained public artifacts. Compact summaries and exact
rebuild metadata are enough for this pass.

### Predictive / revelatory

The pass should answer:

```text
Do pair005/pair012/pair014/pair026 form a consistent finite distinction-measure
class under rank_order_boundary?

Are low/medium controls separated under the same measures?

Which part of the signal is marginal preservation, joint restriction over
surviving marginals, horizon persistence, or operator-specific delta?

Which formal-interface artifacts are now missing before identity-decay-null or
pre-proto-valuer precursor work can begin?
```

## 4. Candidate panel

Use the current high-yield representative set:

```text
high_yield_representatives:
  pair005
  pair012
  pair014
  pair026
```

Use low/medium controls:

```text
controls:
  pair000
  pair001
  pair002
  pair045
```

Rationale:

```text
pair000/pair001/pair002 are recurring low-residual controls from earlier panel
runs.

pair045 was the highest non-high-yield residual in the pair024-047 class
expansion readout and is a useful medium-near-high control.
```

If local morphology summaries identify a better medium control before running,
Codex may replace `pair045`, but it must record the replacement and reason in the
run manifest.

## 5. Operator reference panel

For each candidate pair where feasible, compare:

```text
product_selector:
  true product-equivalence reference

zero_penalty_joint_rank_prefix:
  zero-penalty joint selector; not product-neutral

scalar_mismatch_0.020:
  previous scalar branch reference

shared_capacity_v1:
  negative-control / repair-target reference; marginal-pruning behavior

rank_order_boundary:
  current live ordinal operator
```

The postprocessor should first search existing retained runs and compact summary
bundles for these operator x pair cells.

Only run missing H64 cells if needed for the representative/control panel.

## 6. Phase A: Postprocess existing retained outputs

Build a new utility:

```text
python -m omega.future_field_atlas.formal_interface_distinction_panel
```

Suggested CLI:

```text
python -m omega.future_field_atlas.formal_interface_distinction_panel \
  --out results/future_field_atlas/20260602_formal_interface_distinction_panel/ \
  --runs <run_or_summary_dir_1> <run_or_summary_dir_2> ... \
  --pairs pair005,pair012,pair014,pair026,pair000,pair001,pair002,pair045 \
  --operator-labels product_selector,zero_penalty_joint_rank_prefix,scalar_mismatch_0.020,shared_capacity_v1,rank_order_boundary \
  --include-existing-retention-summaries \
  --write-report
```

The utility should accept either run directories or compact retention summary
directories. Missing cells should be emitted with status `missing_not_run` rather
than silently omitted.

## 7. Phase B: Run missing H64 representative/control cells only if needed

If Phase A shows missing reference cells that are needed for the panel, run a
compact H64 completion panel.

Use H64 only:

```text
horizon_max: 64
horizon_schedule: dense
groups: 48
fresh_seeds_per_group: 1
start_samples: 1
pair_indexes: 0,1,2,5,12,14,26,45
```

Common component selectors:

```text
selection_operator_a: rank_prefix:m=3
selection_operator_b: rank_subset:m=4:retain=1|2|3:remove=4
macro_invariant_kind: symbol_histogram_distance
macro_invariant_beta_list: 0.10
rank_boundary_k: 3
```

Run only missing operator families from this set:

```text
product
joint_energy_rank_prefix at coupling_strength 0.000
rank_boundary_mismatch / scalar mismatch at coupling_strength 0.020
shared_capacity with joint_effective_out_degree 4
rank_order_boundary with joint_effective_out_degree 4
```

Suggested output naming:

```text
results/future_field_atlas/20260602_formal_interface_panel_<operator_label>_h64_reps_controls/
```

Runtime guidance:

```text
raw_topology_output_mode: worker_spool
csv_output_mode: gzip
gzip_compresslevel: 1
workers: 4-6 depending on local resources
artifact_write_workers: 4
checkpoint_every_pairs: 1
max_runtime_seconds: 7200
shutdown_cushion_seconds: 120
```

Do not run H128 in this spec. H128 is not needed to emit finite distinction
measure panel artifacts.

## 8. Required outputs

Create:

```text
formal_interface_panel_manifest.json
formal_interface_condition_panel.csv
candidate_designation_manifest.csv
distinction_measure_manifest.csv
distinction_measure_by_horizon.csv
joint_vs_marginal_distinction_retention.csv
operator_reference_delta_by_horizon.csv
horizon_signature_persistence.csv
representative_control_signature_summary.csv
formal_interface_missing_cells.csv
formal_interface_report.md
```

If any required input is unavailable, emit an explicit row in
`formal_interface_missing_cells.csv`.

## 9. Candidate designation manifest

`candidate_designation_manifest.csv`

One row per pair designation.

Required columns:

```text
candidate_designation_id
candidate_designation_kind
pair_id
pair_index
representative_class
selection_reason
source_result_note
claim_boundary
```

Allowed `candidate_designation_kind`:

```text
pair_frontier_geometry_token
```

This is not a process bundle, identity, agent, or valuer. It is a finite FFA
geometry token used for distinction-measure reporting.

Suggested `representative_class` values:

```text
high_yield_representative
low_residual_control
medium_near_high_control
```

## 10. Distinction measure manifest

`distinction_measure_manifest.csv`

Required rows:

```text
measure_family: binary_signature_indicator
measure_id: marginal_preserving_joint_restrictive_indicator

measure_family: joint_vs_marginal_retention
measure_id: joint_density_vs_surviving_marginals

measure_family: horizon_persistence
measure_id: high_yield_signature_horizon_persistence

measure_family: operator_delta
measure_id: residual_delta_vs_product
measure_id: residual_delta_vs_zero_penalty_joint_rank_prefix
measure_id: residual_delta_vs_scalar_0.020
measure_id: residual_delta_vs_shared_capacity_v1
```

Required columns:

```text
measure_id
measure_family
observable_id
horizon_regime
thresholds_json
normalization_policy
required_artifacts_json
claim_boundary
```

Threshold defaults:

```text
marginal_preserving:
  A_marginal_retention >= 0.99
  B_marginal_retention >= 0.99

joint_restrictive:
  joint_density_vs_marginal_product <= 0.50

high_residual:
  joint_support_residual_fraction >= 0.40
```

Thresholds must be included in the manifest. If Codex changes thresholds, it must
record the reason and keep old thresholds in the report for sensitivity context.

## 11. Distinction measure by horizon

`distinction_measure_by_horizon.csv`

One row per candidate x operator x horizon x measure.

Required columns:

```text
candidate_designation_id
pair_id
operator_label
run_id
horizon
observable_id
measure_id
measure_value
binary_status
A_marginal_retention
B_marginal_retention
joint_support_residual_fraction
joint_retention_fraction
joint_density_vs_marginal_product
product_joint_support_count
coupled_joint_support_count
artifact_completeness_status
reconstruction_audit_status
source_artifact
```

For measures that are not computable from available artifacts, emit:

```text
binary_status: not_available_from_retained_inputs
```

Do not fill missing values with zeros.

## 12. Joint-vs-marginal distinction retention

`joint_vs_marginal_distinction_retention.csv`

Required columns:

```text
candidate_designation_id
pair_id
operator_label
horizon
A_marginal_retention
B_marginal_retention
joint_density_vs_marginal_product
joint_support_residual_fraction
marginal_preserving_flag
joint_restrictive_flag
product_dense_over_surviving_marginals_flag
signature_class
```

Suggested `signature_class` values:

```text
marginal_preserving_joint_restrictive
marginal_preserving_product_dense
marginal_loss_product_dense
marginal_loss_joint_restrictive
incomplete
```

## 13. Horizon signature persistence

`horizon_signature_persistence.csv`

Required columns:

```text
candidate_designation_id
pair_id
operator_label
window_id
window_start
window_end
horizons_available
horizons_signature_true
signature_fraction
first_horizon_true
last_horizon_true
max_residual_horizon
final_signature_status
```

Required windows:

```text
full_window: 0..64
post_onset_window: first_horizon_true..64 if available
final_quarter_window: 49..64
```

## 14. Operator reference deltas

`operator_reference_delta_by_horizon.csv`

Compare each non-reference operator against the declared references where both
cells are available.

Required comparisons:

```text
rank_order_boundary vs product_selector
rank_order_boundary vs zero_penalty_joint_rank_prefix
rank_order_boundary vs scalar_mismatch_0.020
rank_order_boundary vs shared_capacity_v1
scalar_mismatch_0.020 vs product_selector
shared_capacity_v1 vs product_selector
```

Required columns:

```text
comparison_id
pair_id
horizon
metric_name
left_operator
right_operator
left_value
right_value
delta
relative_delta
both_cells_available
missing_reason
```

Metrics:

```text
joint_support_residual_fraction
joint_retention_fraction
A_marginal_retention_fraction
B_marginal_retention_fraction
joint_density_vs_marginal_product
coupled_joint_support_count
product_joint_support_count
```

## 15. Representative/control summary

`representative_control_signature_summary.csv`

Required columns:

```text
pair_id
representative_class
operator_label
final_residual
final_joint_retention
final_A_retention
final_B_retention
final_joint_density_vs_marginal_product
final_signature_class
full_window_signature_fraction
final_quarter_signature_fraction
comparison_to_rank_order_boundary
summary_read
claim_boundary
```

The report should explicitly answer:

```text
Do all high-yield representatives share the same rank_order_boundary finite
measure signature?

Do the controls remain separated?

Is the signature horizon-persistent or final-only?

Is the rank_order_boundary signature closer to scalar 0.020 or to
shared_capacity v1 under the finite measures?

Which artifacts are missing before identity-decay-null tests could begin?
```

## 16. Formal interface report

`formal_interface_report.md`

Suggested structure:

```text
1. Summary
2. Candidate panel
3. Operator references
4. Artifact gates
5. Distinction measure manifest
6. Joint-vs-marginal retention
7. Horizon persistence
8. Operator deltas
9. Missing cells and limitations
10. Theory-arm interface implications
11. Claim boundary
```

The report must include:

```text
This is not a proto-valuer, valuer, compatibility, support, capture, erasure, or
Omega result.
```

## 17. Gates

Every interpretable run or postprocessed cell must satisfy:

```text
status: COMPLETED
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS
medium_sweep_interpretation_allowed: 1 where applicable
```

Cells failing gates should remain in the output with status `blocked_by_gate`, not
silently disappear.

## 18. Acceptance criteria

This spec succeeds if it produces:

```text
formal interface manifest;
candidate designation manifest;
distinction measure manifest;
distinction measure by horizon table;
joint-vs-marginal distinction retention table;
horizon signature persistence table;
operator reference delta table;
representative/control summary;
formal interface report;
explicit missing-cell report;
strict claim boundary.
```

It fails if:

```text
semantic labels are introduced;
proto-valuer / valuer / compatibility / support / capture / erasure / Omega
language appears in output labels;
missing cells are omitted rather than reported;
truncated or incomplete artifacts are treated as interpretable;
thresholds are changed without manifesting the change;
product selector and zero-penalty joint rank-prefix are conflated;
rank_order_boundary results are promoted beyond finite distinction-measure
geometry.
```

## 19. Summary instruction to Codex

Build the first Formal Interface Distinction Panel for Future Field Atlas.

Start by postprocessing retained compact outputs. Run only missing H64
representative/control cells needed to complete the operator-reference panel.

Emit declared finite distinction-measure artifacts and a report. Do not implement
identity-decay nulls, proto-valuer detection, compatibility audits, or Omega
claims in this pass.

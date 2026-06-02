# RFS-MB0 Stage B-2 Spectral Future-Field Geometry Smoke Spec

Status: preliminary extension spec / spectral audition  
Scope: optional follow-up to Stage B-2 exploratory iteration pass, before channel-edge sensitivity or full gauge-shadow migration  
Claim boundary: no holdout, no candidate promotion, no Omega detection, no agent detection, no identity detection, no valuer detection

## 0. One-sentence purpose

This smoke tests whether the weak Stage B-2 A/C residues point to real structured future-field geometry, or whether the hand-built syndrome vocabulary is only detecting brittle metric artifacts.

In short:

```text
Before migrating the instrument, ask whether spectra see anything worth migrating toward.
```

## 1. Why this exists now

Stage B-2 produced a clean exploratory fork:

```text
SYN_A and SYN_C:
  measurable across a large design-set run;
  edge/topology sensitive;
  exact generator roughness/asymmetry controls near baseline;
  entropy-flow-horizon overlay coherent for topology perturbations;
  not yet channel-specific;
  not yet agency/value/Omega evidence.

SYN_B and SYN_D:
  measurable but no resolved residual in Stage B-2;
  useful as turnover/diffusion contrast syndromes.
```

The hand-built syndrome detector may be pointing at a real deformation mode, but it may also be imposing a brittle vocabulary.

A spectral smoke is the parsimonious next check:

```text
Instead of asking whether a hand-built syndrome recurs,
ask whether the reachable-future field has non-random relational geometry
above controls.
```

This is a geometry detector, not an agency detector.

## 2. Relation to current roadmap

This spec does not replace Stage B-2.

It sits between:

```text
completed Stage B-2 exploratory iteration pass
```

and:

```text
channel-edge sensitivity follow-up
full RFS-MB0G gauge-coherent shadow spec
measurement-limits note
```

Recommended use:

```text
1. Run this spectral smoke.
2. If spectra are promising, use high-loading spectral structures to guide channel-edge sensitivity.
3. If spectra are control-equivalent, do not migrate the instrument yet.
```

## 3. Claim boundary

Allowed claims:

```text
The future field does or does not show structured spectral geometry above controls.
A/C hand-built syndromes do or do not align with spectral geometry.
Spectral geometry is or is not sensitive to topology-level edge perturbation.
Spectral geometry is or is not coherent across frontier, flow, and horizon views.
```

Not allowed:

```text
Omega detected.
Agent detected.
Valuer detected.
Identity detected.
Gauge-coherent shadow validated.
Future-shaping source identified.
Candidate promoted.
Holdout ready.
```

Counters must remain:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## 4. The spectral object

The spectral object is a relational matrix built from the future field.

A future-field matrix should be derived from primitive observables:

```text
distinction:
  states/signatures/transitions can differ

relation:
  states/signatures/transitions co-occur, co-flow, co-recover, or co-collapse

asymmetry:
  those relations have horizon-dependent consequences
```

No semantic labels such as agent, valuer, corridor, trap, or Omega should enter the matrix construction.

Those labels, if used, are downstream interpretations only.

## 5. Matrix families

Run only small, memory-safe matrix families in the first smoke.

### 5.1 Co-frontier matrix

Items:

```text
future signatures
```

Relation:

```text
two signatures are related if they appear in the same frontier context
```

Context examples:

```text
system_id
probe_key
flow_mode
start_index
window
H_a / H_b
mechanism_control_condition
row_kind
```

Purpose:

```text
Detect shape structure in reachable futures.
```

This is the spectral analogue of the entropy / future-shape view.

### 5.2 Co-flow matrix

Items:

```text
signature transitions
```

Example item:

```text
left_signature -> right_signature
```

Relation:

```text
two signature transitions are related if they co-occur in the same frontier-transform context
```

Purpose:

```text
Detect transport / routing structure in the future field.
```

This is the spectral analogue of the flow / channel view.

### 5.3 Horizon-band matrices

For both co-frontier and co-flow, emit separate matrices by horizon band:

```text
short:
  0->1, 1->2, 2->4

middle:
  4->8, 8->16

downstream:
  16->24, 24->32
```

Purpose:

```text
Test whether spectral structure is local, downstream, or horizon-coherent.
```

Do not run a broad long-horizon spectral audit in this smoke.

## 6. Normalization

The primary normalized statistic should compare observed co-occurrence to an independence baseline.

For item counts within a matrix family:

```text
n_i:
  item i occurrence count

n_ij:
  co-occurrence count of items i and j

N:
  context count
```

Convert to probabilities:

```text
P_i = n_i / N
P_j = n_j / N
P_ij = n_ij / N
```

Primary normalized entry:

```text
M_ij = (P_ij - P_i * P_j) / (0.5 * (P_ij + P_i * P_j) + epsilon)
```

Use a small `epsilon` and report it.

This is a bounded normalized co-occurrence statistic. It is not a value score.

Alternative normalizations may be emitted as diagnostics only:

```text
PMI-like log ratio
correlation coefficient
cosine-normalized co-occurrence
raw co-occurrence after marginal filtering
```

Do not choose the normalization after seeing which one looks most positive.

## 7. Controls and residualization

Do not interpret raw spectra alone.

Required comparisons:

```text
observed baseline condition
small_edge_resample controls
asymmetric_edge_flip controls
exact roughness-seed controls, if present
exact or proxy asymmetry-strength controls, if present
neutral/generated controls if available
label-shuffled controls
context-shuffled controls
horizon-order shuffled controls
frontier-size or support-size matched controls where feasible
probe-marginal controls or honest exclusion
```

Two comparison modes should be emitted.

### 7.1 Direct control comparison

Compute spectral summaries for observed and control matrices separately.

Compare:

```text
eigenvalue curves;
positive spectral mass;
effective rank;
spectral gap;
top-k subspace alignment;
localization / participation.
```

### 7.2 Residual matrix comparison

Where control matrices are shape-compatible, compute:

```text
M_residual = M_observed - mean(M_controls)
```

Then run the same spectral summaries on `M_residual`.

If matrices are not shape-compatible due to item-set differences, use aligned item sets or report residualization as unavailable.

Do not silently drop high-mass items without reporting the dropped mass.

## 8. Spectral summaries

For symmetric matrices:

```text
use eigen-decomposition
```

For directed or rectangular matrices:

```text
use singular-value decomposition
```

Do not overinterpret individual eigenvectors.

Primary summaries:

```text
positive_spectral_mass
top_k_eigenvalues_or_singular_values
effective_rank
spectral_gap_k
participation_ratio_top_modes
item_mass_covered_by_matrix
item_count
context_count
control_excess_positive_spectral_mass
control_percentile_positive_spectral_mass
```

Primary cross-view summary:

```text
top_k_subspace_alignment
```

For two top-k subspaces U and V:

```text
alignment(k) = squared_Frobenius_norm(transpose(U) * V) / k
```

Use this for:

```text
observed vs control;
co-frontier vs co-flow;
short vs middle;
middle vs downstream;
baseline vs small_edge_resample;
baseline vs exact generator controls;
probe A vs probe B.
```

## 9. A/C and B/D handling

Primary focus:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag
SYN_C_low_growth_high_concentration_low_entropy
```

Secondary contrast:

```text
SYN_B_high_turnover_high_offdiag_high_window_delta
SYN_D_high_turnover_high_entropy_low_bottleneck_control
```

The spectral smoke should answer:

```text
Do A/C-positive contexts have spectral geometry not seen in A/C-negative or control contexts?

Do B/D contexts have a distinct turnover/diffusion spectral profile, or are they unresolved/noisy?

Do topology controls that reduce A/C also reduce or rotate the relevant spectral subspaces?
```

Do not define spectra using the syndrome labels themselves. Use labels only for post-hoc grouping after the matrix construction is fixed.

## 10. Data sources and memory safety

The Stage B-2 exploratory run used audit-sample output modes and count-based online aggregation. Full raw metric/component rows were not retained.

Therefore the spectral smoke may need its own compact recomputation path.

Allowed modes:

### 10.1 Existing-output mode

Use retained audit samples and summary tables only if they contain enough context to construct matrices.

If not enough context is available, mark:

```text
existing_output_mode_insufficient_for_spectral_matrix
```

and switch to compact recompute mode.

### 10.2 Compact recompute mode

Recompute selected frontier-transform rows and aggregate spectral matrices online.

Rules:

```text
Do not store full raw row tables.
Do not store full dense matrices if item count is large.
Use sparse counts or capped item vocabularies.
Emit item-mass coverage.
Emit dropped-item counts and mass.
Keep diagnostic probes separate or excluded.
```

Recommended first-pass caps:

```text
max_items_per_matrix: 512 to 2048
min_item_count: configurable
max_contexts_per_matrix: configurable
```

If caps discard too much mass, report the matrix as undercovered.

## 11. Probe and view restrictions

Primary probes:

```text
constraint_profile_hash
constraint_violation_count_plus_local_tuple
```

Diagnostic probes:

```text
existing_low
full_state_hash
```

Diagnostic probes must not drive positive spectral conclusions.

If included, they should be labeled:

```text
diagnostic_identity_like_or_low_resolution_probe
```

The first smoke should not add many new probes.

A simple channel/transition-role view may be added only if it is derived mechanically from flow rows and does not install agent/channel labels into the substrate.

## 12. Run shape

The smoke should be small enough to run before any full migration decision.

Suggested shape:

```text
design_groups: 3 to 5
fresh_seeds_per_group: 2 to 4
start_samples_list: 4,8
selected syndromes: A/C primary, B/D contrast
controls: reuse Stage B-2 calibrated controls where possible
horizon bands: short, middle, downstream
```

Suggested wall clock:

```text
max_runtime_seconds: 7200 to 10800
shutdown_cushion_seconds: 900 to 1200
```

If run inside a larger 8-hour block, this smoke should have its own checkpointing and must finalize partial matrices before the outer shutdown cushion.

## 13. Graceful exit requirements

Every spectral runner must support:

```text
status.json at start;
periodic status.json updates;
progress checkpoint CSV;
SIGINT/SIGTERM handling;
partial matrix finalization;
partial spectral summary finalization;
errors.csv;
output_manifest.json;
final report even if partial.
```

Required status fields:

```text
status
phase
started_utc
finished_utc
elapsed_seconds
max_runtime_seconds
shutdown_cushion_seconds
finalization_reason
jobs_requested
jobs_completed
contexts_accumulated
matrix_families_requested
matrix_families_completed
spectral_decompositions_completed
errors
holdout_scoring_count
n6_run_count
alphabet_expansion_count
candidate_promotion_enabled
```

Allowed final statuses:

```text
COMPLETED
PARTIAL_TIME_LIMIT_REACHED
PARTIAL_INTERRUPTED
PARTIAL_EXISTING_OUTPUT_INSUFFICIENT
PARTIAL_MATRIX_UNDERCOVERED
FAILED_WITH_ERRORS
```

## 14. Required outputs

Core config and status:

```text
spectral_future_field_run_config.json
spectral_future_field_status.json
spectral_future_field_progress_checkpoints.csv
errors.csv
output_manifest.json
```

Matrix manifests:

```text
spectral_matrix_manifest.csv
spectral_item_manifest.csv
spectral_context_manifest.csv
spectral_item_coverage.csv
```

Matrix summaries:

```text
cofrontier_matrix_summary.csv
coflow_matrix_summary.csv
horizon_band_matrix_summary.csv
control_matrix_summary.csv
residual_matrix_summary.csv
```

Spectral summaries:

```text
spectral_eigenvalue_summary.csv
spectral_positive_mass_summary.csv
spectral_effective_rank_summary.csv
spectral_participation_summary.csv
spectral_gap_summary.csv
```

Alignment summaries:

```text
spectral_topk_alignment_by_view.csv
spectral_topk_alignment_by_horizon.csv
spectral_topk_alignment_by_control.csv
spectral_topk_alignment_by_probe.csv
spectral_alignment_area_summary.csv
```

Syndrome relation summaries:

```text
spectral_by_syndrome_context.csv
spectral_ac_vs_bd_contrast.csv
spectral_ac_topology_sensitivity.csv
```

Final report:

```text
rfs_mb0_stage_b2_spectral_future_field_geometry_smoke_report.md
```

## 15. Decision classes

Allowed spectral decision classes:

```text
spectral_future_geometry_present
spectral_future_geometry_control_equivalent
spectral_future_geometry_single_view_artifact
spectral_horizon_coherent
spectral_horizon_fragile
spectral_flow_channel_candidate
spectral_saturation_fakeout
spectral_probe_collision_risk
spectral_ac_aligned_with_edge_sensitivity
spectral_ac_not_aligned_with_edge_sensitivity
no_resolved_spectral_structure
matrix_coverage_insufficient
```

Allowed branch recommendations:

```text
recommend_channel_edge_sensitivity_with_spectral_guidance
recommend_full_RFS_MB0G_spectral_gauge_shadow_spec
recommend_syndrome_branch_continue_without_spectral_migration
recommend_measurement_limits_note
recommend_spectral_runner_repair
```

Forbidden decision classes:

```text
Omega_positive
agent_detected
valuer_detected
identity_detected
candidate_promoted
holdout_ready
```

## 16. Pass criteria

A promising spectral smoke requires at least:

```text
1. matrix coverage is adequate;
2. observed spectral summaries exceed label/context-shuffled controls;
3. spectral structure is not explained by frontier-size/support-size controls;
4. top-k subspace alignment is nontrivial across at least two views or horizon bands;
5. A/C edge-sensitive contexts show corresponding spectral change;
6. exact generator controls that stayed near baseline in Stage B-2 also remain near baseline spectrally;
7. diagnostic probes do not drive the positive read.
```

If these pass, the next step should be:

```text
channel-edge sensitivity with spectral high-loading structures;
or a full spectral gauge-coherent shadow spec.
```

## 17. Failure criteria

A spectral smoke should block migration if:

```text
observed spectra are control-equivalent;
top modes are frontier-size or saturation modes;
subspace alignment is single-view only;
A/C syndrome drops are not accompanied by spectral change;
random matched perturbations reproduce the same spectral behavior;
diagnostic probes drive the signal;
matrix coverage is too low.
```

If these occur, recommend:

```text
continue current syndrome branch without spectral migration;
or write a measurement-limits note if syndrome evidence also remains weak.
```

## 18. Interpretation rules

Spectral geometry is not agency.

A positive result means only:

```text
structured future-field geometry was detected above specified controls.
```

It does not mean:

```text
an agent exists;
a valuer exists;
identity was found;
Omega-compatible structure was detected;
value was detected.
```

Further filters are required for agency/value/Omega:

```text
action-channel intervention;
recoverability;
fragility / redundancy;
cost / maintainability;
compatibility across deformers;
cross-scale/horizon persistence.
```

## 19. 3P check

### Principled

The matrix is derived from future-field relations, not semantic labels.

### Parsimonious

One relational matrix family plus spectral summaries may replace many hand-built syndrome components if it works.

### Predictive

Spectral structure from one view, control, or horizon should predict structure in another better than matched nulls.

If spectra do not predict, they are just descriptive geometry.

## 20. Bottom line

This smoke asks whether the instrument should begin migrating from hand-built syndromes toward a canonical spectral detector of future-field geometry.

The desired outcome is a clean fork:

```text
if spectra see structured residual geometry aligned with A/C edge sensitivity:
  use spectra to guide channel-edge sensitivity or write a full spectral gauge spec

if spectra are control-equivalent or undercovered:
  do not migrate; repair or retire the spectral path
```

Do not promote any result from this smoke beyond structured future-field geometry.

# RFS-MB0 Horizon-Transport Spectral Response Repair Spec

Status: incremental instrumentation repair spec  
Scope: next RFS-MB0 spectral branch repair after coflow/control sweep failures  
Claim boundary: no holdout, no candidate promotion, no Omega detection, no agent detection, no identity detection, no valuer detection

## 0. One-sentence purpose

Add the smallest instrument changes needed to test whether horizon-to-horizon transport spectra are a better Omega-native future-field object than static coflow/cofrontier spectra, while enforcing the reoriented control taxonomy:

```text
Null controls test the detector.
Perturbations test the candidate.
Destructive ablation maps viability boundaries; it is not ordinary negative evidence.
```

## 1. Why this repair exists

Recent spectral smokes showed that the current static coflow/cofrontier approach is not yet isolating a robust object:

```text
coflow spectra can be constructed;
coflow direct-control spectral structure appears;
structure-destroying shuffles do not yet separate cleanly;
high-loading item ablation is random-equivalent;
subspace transfer is control-equivalent in current repair smoke;
subspace distributedness reads diffuse/noise-like;
graph perturbation remains blocked.
```

This suggests one or more of the following:

```text
statistic mismatch;
matrix-construction mismatch;
horizon or scale mismatch;
substrate resolution mismatch;
control philosophy drift.
```

This repair addresses the first three while preventing further control philosophy drift.

## 2. Core reorientation

The current spectral branch used mostly static future-field matrices:

```text
cofrontier:
  what future signatures appear together inside a frontier context

coflow:
  what transition items co-occur inside a frontier-transform window
```

These are useful diagnostics, but they may be too static or too broad.

Omega is fundamentally horizon-indexed. The relevant structure may be:

```text
what future structures at an earlier horizon transport into,
open,
close,
route toward,
or collapse into at a later horizon.
```

Therefore this repair adds a directional horizon-transport object:

```text
T_{H_a -> H_b}
```

## 3. Control taxonomy repair

Every control, view, or perturbation row must include:

```text
intervention_class
intervention_family
intervention_name
intervention_strength
interpretation_role
allowed_claim_level
```

Allowed `intervention_class` values:

```text
detector_null_control
gauge_view_control
nonlethal_perturbation
functional_perturbation
lethal_boundary_probe
baseline
```

Allowed `interpretation_role` values:

```text
detector_validity
view_coherence
candidate_response_profile
viability_boundary_mapping
not_interpretable
```

Allowed `allowed_claim_level` values:

```text
detector_null_only
response_profile_only
view_transform_only
viability_boundary_only
instrumentation_only
not_interpretable
```

Hard rule:

```text
A detector-null control may block detector claims.
A perturbation may describe response geometry.
A destructive perturbation may map a viability boundary.
None of these alone detects agency, value, identity, or Omega.
```

## 4. Detector nulls versus candidate perturbations

Reports must separate two sections.

### 4.1 Detector-null section

Question:

```text
Does observed horizon-transport structure separate from null/matched detector artifacts?
```

Examples:

```text
context shuffle;
horizon shuffle;
label shuffle as interpretation control;
frontier-size/support-size match;
probe-marginal match;
saturation timing match;
neutral/fakeout systems.
```

Outputs belong in:

```text
detector_null_summary.csv
detector_null_gate_results.csv
```

### 4.2 Candidate perturbation-response section

Question:

```text
How does the horizon-transport geometry deform under graded perturbation?
```

Examples:

```text
tiny edge roughening;
tiny asymmetry edge flip;
roughness seed proxy if clean;
small constraint-weight jitter if clean;
functional perturbation only in later branches;
lethal perturbation only for boundary mapping.
```

Outputs belong in:

```text
transport_response_profile_summary.csv
transport_perturbation_profile.csv
```

Do not mix these sections into one pass/fail claim.

## 5. New matrix family: horizon_transport

Add a matrix family:

```text
horizon_transport
```

The object is directional and should use SVD by default.

### 5.1 Matrix definition

For each context, build:

```text
T_{H_a -> H_b}
```

Rows:

```text
source-side future structures at H_a
```

Columns:

```text
target-side future structures at H_b
```

Possible row items:

```text
frontier signatures at H_a;
source-side probe signatures;
local flow-role signatures;
start-conditioned future-profile bins;
coarse reachable-region labels.
```

Possible column items:

```text
frontier signatures at H_b;
downstream probe signatures;
target-side future-profile bins;
transport destination signatures;
mechanically derived collapse/reopening labels if available.
```

Entries:

```text
transport count;
transport mass;
conditional probability;
normalized residual transport;
control-relative transport excess.
```

First implementation should start with transport count or transport mass and emit normalization diagnostics separately.

### 5.2 Required metadata

Every matrix row must include:

```text
matrix_id
matrix_family
probe_key
flow_mode
source_horizon_band
target_horizon_band
H_a
H_b
condition_id
intervention_class
intervention_family
intervention_name
intervention_strength
row_item_count
column_item_count
transport_context_count
transport_mass_total
coverage
normalization_kind
```

## 6. Horizon bands

Use a minimal band set first:

```text
short:
  0->1, 1->2, 2->4

middle:
  4->8, 8->16

downstream:
  16->24, 24->32
```

Primary transport objects:

```text
T_short_to_middle
T_middle_to_downstream
```

Optional if cheap:

```text
T_short_to_downstream
```

Do not add long-horizon expansion in the first repair smoke.

## 7. Spectral summaries for horizon transport

Because `horizon_transport` is directional, use singular-value decomposition.

Required summaries:

```text
singular_values_top_k
positive_or_nonzero_spectral_mass
effective_rank
spectral_gap_k
left_subspace_participation
right_subspace_participation
left_loading_entropy
right_loading_entropy
left_top_item_mass_share
right_top_item_mass_share
transport_entropy
transport_concentration
```

Subspace comparisons:

```text
left_subspace_alignment_short_to_middle_vs_middle_to_downstream
right_subspace_alignment_short_to_middle_vs_middle_to_downstream
baseline_to_null_alignment
baseline_to_perturbation_alignment
null_percentile
perturbation_response_magnitude
```

## 8. Detector-null controls for horizon transport

Required first nulls:

```text
context_shuffle_transport_null
horizon_pair_shuffle_transport_null
label_shuffle_transport_interpretation_control
```

Optional if feasible:

```text
row_marginal_matched_transport_null
column_marginal_matched_transport_null
frontier_size_matched_transport_null
probe_marginal_transport_null
```

Important distinction:

```text
label shuffle is a label-interpretation control;
context and horizon-pair shuffles are structure-destroying detector nulls.
```

Detector-null pass/fail must report by matrix/probe/flow/horizon pair, not only as a global aggregate.

Required output:

```text
horizon_transport_detector_null_anatomy.csv
```

Fields:

```text
matrix_id
probe_key
flow_mode
source_horizon_band
target_horizon_band
null_family
null_category
observed_statistic
null_mean
null_std
null_max
observed_percentile_vs_null
expected_direction
separation_margin
null_gate_passed
failure_interpretation
```

Allowed `failure_interpretation` values:

```text
true_control_equivalence
statistic_mismatch
horizon_pair_mismatch
probe_flow_mismatch
underpowered_replicates
insufficient_coverage
passed
```

## 9. Perturbation-response profiles

Run only tiny non-lethal perturbations in the first repair smoke.

Suggested perturbations:

```text
baseline
small_edge_resample_control:p0.0025
small_edge_resample_control:p0.005
asymmetric_edge_flip_control:p0.0025
asymmetric_edge_flip_control:p0.005
```

Optional if clean:

```text
roughness_seed_proxy
very_gentle_constraint_weight_jitter
```

Each perturbation must be labeled:

```text
intervention_class: nonlethal_perturbation
interpretation_role: candidate_response_profile
allowed_claim_level: response_profile_only
```

Do not call these detector-null controls.

## 10. Response classes

For each perturbation, classify the horizon-transport response.

Allowed response classes:

```text
transport_stable
transport_rerouted
transport_weakened
transport_reopens
transport_collapses
transport_control_equivalent
transport_resolution_mismatch
transport_response_underpowered
```

Working definitions:

```text
transport_stable:
  singular subspaces remain aligned and transport mass/concentration changes only mildly

transport_rerouted:
  source/target subspaces shift but downstream transport remains structured

transport_weakened:
  transport spectral mass or concentration decreases without full collapse

transport_reopens:
  local concentration/narrowing is followed by downstream diversification/recovery

transport_collapses:
  downstream transport mass or diversity collapses into narrow/saturated structure

transport_control_equivalent:
  detector nulls reproduce the same transport profile

transport_resolution_mismatch:
  response only appears under one probe/flow/resolution view
```

## 11. Coverage and readiness gates

This repair should not advance to graph perturbation.

Readiness levels:

```text
ready_for_horizon_transport_smoke_expansion
ready_for_fixture_horizon_transport_tests
ready_for_direct_channel_diagnostics
not_ready_repair_required
```

Pass conditions for `ready_for_horizon_transport_smoke_expansion`:

```text
horizon_transport matrices have adequate coverage;
at least one horizon pair separates from detector-null controls;
response profiles under tiny nonlethal perturbations are interpretable;
claim-boundary counters remain zero;
reports separate detector nulls from perturbation responses.
```

Pass conditions for `ready_for_fixture_horizon_transport_tests`:

```text
horizon_transport matrices build successfully but generated substrate remains ambiguous;
fixtures are needed to validate the statistic and response classes.
```

## 12. Required outputs

Core outputs:

```text
horizon_transport_repair_run_config.json
horizon_transport_repair_status.json
horizon_transport_repair_progress_checkpoints.csv
horizon_transport_repair_errors.csv
horizon_transport_repair_output_manifest.json
```

Matrix outputs:

```text
horizon_transport_matrix_manifest.csv
horizon_transport_row_item_manifest.csv
horizon_transport_column_item_manifest.csv
horizon_transport_coverage.csv
horizon_transport_matrix_summary.csv
```

Spectral outputs:

```text
horizon_transport_svd_summary.csv
horizon_transport_subspace_alignment.csv
horizon_transport_participation_summary.csv
horizon_transport_entropy_summary.csv
```

Detector-null outputs:

```text
horizon_transport_detector_null_summary.csv
horizon_transport_detector_null_anatomy.csv
horizon_transport_detector_null_gate_results.csv
```

Perturbation-response outputs:

```text
horizon_transport_perturbation_manifest.csv
horizon_transport_response_profile_summary.csv
horizon_transport_response_classification.csv
```

Final report:

```text
rfs_mb0_horizon_transport_spectral_response_repair_result.md
```

## 13. Final report requirements

The retained report must begin with an executive summary answering:

```text
Did horizon-transport matrices build with adequate coverage?
Did any horizon pair separate from detector-null controls?
Did nonlethal perturbations produce interpretable response profiles?
Were detector-null controls and candidate perturbations kept separate?
What is the next action?
```

Required sections:

```text
1. Executive summary
2. Claim boundary
3. Control taxonomy compliance
4. Horizon-transport matrix construction
5. Detector-null results
6. Perturbation-response results
7. Horizon-pair comparison
8. Readiness levels
9. Next-action fork
10. Output manifest
```

## 14. Next-action forks

Emit exactly one next-action fork:

```text
expand_horizon_transport_smoke
build_horizon_transport_fixtures
narrow_horizon_transport_context
return_to_direct_channel_diagnostics
repair_transport_null_controls
write_measurement_limits_note
```

Fork rules:

```text
expand_horizon_transport_smoke:
  if coverage, detector-null separation, and response profiles are all promising

build_horizon_transport_fixtures:
  if matrices build but generated-substrate interpretation is ambiguous

narrow_horizon_transport_context:
  if one probe/flow/horizon pair is promising but aggregate read is weak

return_to_direct_channel_diagnostics:
  if transport spectra are unhelpful but A/C channel-like topology sensitivity remains live

repair_transport_null_controls:
  if detector nulls are mis-specified or underpowered

write_measurement_limits_note:
  if transport spectra are control-equivalent across contexts
```

## 15. Graceful exit

Runner must support:

```text
status.json at start;
periodic status updates;
progress checkpoint CSV;
SIGINT/SIGTERM handling;
shutdown cushion;
partial matrix finalization;
partial detector-null output;
partial perturbation-response output;
errors.csv;
output_manifest.json;
partial final report.
```

Allowed partial statuses:

```text
COMPLETED
PARTIAL_TIME_LIMIT_REACHED
PARTIAL_INTERRUPTED
PARTIAL_CONTROL_SOURCE_MISSING
PARTIAL_TRANSPORT_MATRIX_UNDERCOVERED
PARTIAL_DETECTOR_NULL_INCOMPLETE
PARTIAL_RESPONSE_PROFILE_INCOMPLETE
FAILED_WITH_ERRORS
```

## 16. 3P check

### Principled

Horizon transport follows from Omega's definition as a horizon-indexed future-field object.

### Parsimonious

The repair adds one directional matrix family rather than a larger hand-built syndrome library.

### Predictive

A useful horizon-transport object should predict downstream branch, recovery, collapse, or rerouting patterns and produce structured perturbation-response profiles.

If it does not predict, do not promote it.

## 17. Bottom line

This repair asks the next narrow question:

```text
Is horizon-to-horizon transport a better spectral object for Omega than static
coflow/cofrontier co-occurrence, and can we measure it without confusing detector
nulls with candidate perturbation responses?
```

No result from this repair is an agency, value, identity, or Omega claim.

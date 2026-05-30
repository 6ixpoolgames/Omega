# RFS-MB0 Horizon-Transport Expansion Smoke Spec

Status: small empirical expansion spec  
Builds on: `docs/RFS_MB0_HORIZON_TRANSPORT_SPECTRAL_RESPONSE_REPAIR_SPEC.md` and `docs/RFS_MB0_HORIZON_TRANSPORT_MATCHED_NULL_AND_FIXTURE_SMOKE_SPEC.md`  
Claim boundary: no holdout scoring, no candidate promotion, no Omega detection, no agency detection, no identity detection, no valuer detection

## 0. One-sentence purpose

Run a slightly larger, still conservative horizon-transport smoke to test whether the directional `horizon_transport` object remains interesting under matched marginal detector nulls and produces interpretable nonlethal perturbation-response profiles.

This is an empirical expansion smoke, not a validation run.

## 1. X-Token note: do not include projection-guided gauge alignment yet

The X-Token paper is methodologically useful for later work because it suggests projection maps between incompatible decompositions, coverage audits before choosing an objective, and relaxed matching when strict equality is too brittle.

However, this run should not implement X-Token-style projection or gauge-alignment machinery.

Reasons:

```text
1. The current live object is horizon transport, not cross-view projection.
2. Projection maps between views require a grounded equivalence relation that we do not yet have.
3. Adding projection now would confound the cleaner question: does horizon transport work at all?
4. The next run should test one repair at a time.
```

For now, X-Token remains a methods note for later:

```text
future possible branch:
  projection-guided gauge alignment between horizon/probe/scale views

not in this run:
  learned or heuristic W matrices between views
```

## 2. Background

The horizon-transport repair added:

```text
matrix_family: horizon_transport
spectral method: SVD
control taxonomy separation:
  detector nulls test the detector
  perturbations describe candidate response geometry
```

The matched-null and fixture repair then added:

```text
row_marginal_matched_transport_null
column_marginal_matched_transport_null
row_column_marginal_matched_transport_null
marginal_residual_fraction
synthetic fixtures:
  block_transport_signal
  marginal_fakeout
  corridor_stable_response
  trap_collapse_response
```

The fixture contract passed 4/4 and the tiny empirical plumbing smoke completed with the matched-marginal gate passing. This means the instrument is ready for a slightly larger horizon-transport smoke.

It does not mean the scientific object has been detected.

## 3. Claim boundary

Allowed claims:

```text
horizon_transport matrices do or do not build with adequate coverage;
matched marginal detector nulls do or do not separate from observed transport;
tiny nonlethal perturbations do or do not produce interpretable transport response profiles;
transport response profiles are stable, weakened, rerouted, reopened, collapsed, control-equivalent, or underpowered;
this branch is or is not ready for fixture expansion, context narrowing, or a larger smoke.
```

Forbidden claims:

```text
Omega detected;
agent detected;
valuer detected;
identity detected;
gauge-coherent shadow validated;
future-shaping source identified;
candidate promoted;
holdout ready;
graph-channel causality shown.
```

Required counters:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## 4. Run scale

This should be larger than the contract smoke but still conservative.

Suggested laptop-safe/default scale:

```text
groups: 4 to 8
design_groups: 2
fresh_seeds_per_group: 2
start_samples_list: 2,4
workers: 7
job_batch_size: 1 or 2
null_replicates: 5
max_runtime_seconds: 7200 to 10800
shutdown_cushion_seconds: 900
```

Suggested small-desktop scale, only if laptop smoke is healthy:

```text
groups: 8 to 12
design_groups: 3
fresh_seeds_per_group: 2 to 3
start_samples_list: 2,4
workers: machine appropriate
null_replicates: 5 to 7
max_runtime_seconds: 14400
shutdown_cushion_seconds: 1200
```

Do not scale beyond this until the expansion smoke report is reviewed.

## 5. Matrix family and horizon pairs

Required matrix family:

```text
horizon_transport
```

Required horizon pairs:

```text
short -> middle
middle -> downstream
```

Optional if cheap:

```text
short -> downstream
```

Use SVD summaries for all directional transport matrices.

Required probes:

```text
constraint_profile_hash
constraint_violation_count_plus_local_tuple
```

Required flow modes:

```text
one_step_local_flow
constrained_window_flow
```

## 6. Detector nulls

Required detector-null families:

```text
context_shuffle_transport_null
horizon_pair_shuffle_transport_null
row_marginal_matched_transport_null
column_marginal_matched_transport_null
row_column_marginal_matched_transport_null
```

Label shuffle may be emitted as a label-interpretation control, but it must not drive the structure-null gate.

Required detector-null statistic:

```text
marginal_residual_fraction
```

Also emit:

```text
singular_spectral_mass
singular_effective_rank
transport_entropy
transport_concentration
left/right subspace alignment statistics
```

Detector-null reporting must be by:

```text
probe_key
flow_mode
source_horizon_band
target_horizon_band
condition_id
null_family
```

Do not report only global aggregate pass/fail.

## 7. Perturbation-response profiles

Run only tiny nonlethal perturbations.

Required conditions:

```text
baseline
small_edge_resample_control:p0.0025
small_edge_resample_control:p0.005
```

Optional if cheap and clean:

```text
asymmetric_edge_flip_control:p0.0025
asymmetric_edge_flip_control:p0.005
roughness_seed_proxy
```

Every perturbation row must be labeled:

```text
intervention_class: nonlethal_perturbation
interpretation_role: candidate_response_profile
allowed_claim_level: response_profile_only
```

Do not treat perturbation-response profiles as detector-null controls.

## 8. Response classes

Emit response classes per perturbation, probe, flow mode, and horizon pair.

Allowed classes:

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

This run should preserve the reorientation:

```text
not:
  survived perturbation = real
  failed perturbation = fake

but:
  perturbation produces a response profile
```

## 9. Primary questions

The expansion smoke should answer:

```text
1. Do horizon-transport matrices remain adequately covered at modestly larger scale?
2. Does observed transport separate from row/column/bimarginal matched detector nulls?
3. Does separation hold across both primary probes or only one?
4. Does separation hold across both flow modes or only one?
5. Are short->middle and middle->downstream transport profiles similar, divergent, or complementary?
6. Are tiny nonlethal perturbation responses mostly stable, rerouted, weakened, reopened, collapsed, or control-equivalent?
7. Does any context deserve narrowing or expansion?
```

## 10. Required outputs

Core outputs:

```text
horizon_transport_expansion_run_config.json
horizon_transport_expansion_status.json
horizon_transport_expansion_progress_checkpoints.csv
horizon_transport_expansion_errors.csv
horizon_transport_expansion_output_manifest.json
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
horizon_transport_matched_marginal_summary.csv
```

Perturbation-response outputs:

```text
horizon_transport_perturbation_manifest.csv
horizon_transport_response_profile_summary.csv
horizon_transport_response_classification.csv
```

Context summaries:

```text
horizon_transport_by_probe_summary.csv
horizon_transport_by_flow_mode_summary.csv
horizon_transport_by_horizon_pair_summary.csv
horizon_transport_context_recommendation.csv
```

Final report:

```text
rfs_mb0_horizon_transport_expansion_smoke_result.md
```

## 11. Required final report

Retain a compact result note under:

```text
docs/research_notes/validation_results/
```

Suggested path:

```text
docs/research_notes/validation_results/rfs_mb0_horizon_transport_expansion_smoke_result.md
```

Required sections:

```text
1. Executive summary
2. Claim boundary
3. Run shape and local artifact policy
4. Matrix coverage
5. Detector-null results
6. Matched marginal null results
7. Perturbation-response profile results
8. Probe / flow / horizon-pair context summary
9. Readiness levels
10. Next-action fork
11. Output manifest
```

The executive summary must answer:

```text
Did horizon transport remain adequately covered?
Did matched marginal detector nulls separate?
Were response profiles interpretable?
Which context, if any, looks most promising?
What should run next?
```

## 12. Readiness levels

Allowed readiness levels:

```text
ready_for_horizon_transport_scaleup
ready_for_horizon_transport_context_narrowing
ready_for_horizon_transport_fixture_expansion
ready_for_direct_channel_diagnostics
not_ready_repair_required
measurement_limits_note_recommended
```

Decision rules:

```text
ready_for_horizon_transport_scaleup:
  adequate coverage;
  matched marginal detector nulls pass in multiple primary contexts;
  response profiles are interpretable;
  null replicate gate powered.

ready_for_horizon_transport_context_narrowing:
  one or two contexts are promising but aggregate read is mixed.

ready_for_horizon_transport_fixture_expansion:
  empirical read is ambiguous but instrument behaves well.

ready_for_direct_channel_diagnostics:
  only if horizon transport remains unhelpful but A/C topology sensitivity remains live.

not_ready_repair_required:
  detector nulls fail, output contract breaks, null replicates underpowered, or coverage is inadequate.

measurement_limits_note_recommended:
  horizon transport is control-equivalent across primary contexts after matched marginal nulls.
```

## 13. Next-action forks

Emit exactly one next-action fork:

```text
expand_horizon_transport_scale
narrow_to_best_horizon_transport_context
build_more_horizon_transport_fixtures
return_to_direct_channel_diagnostics
repair_transport_null_controls
write_horizon_transport_measurement_limits_note
```

No next-action fork may open holdout or graph perturbation directly.

## 14. Graceful exit

Runner must support:

```text
status.json at start;
periodic status updates;
progress checkpoint CSV;
SIGINT/SIGTERM handling;
shutdown cushion;
partial matrix finalization;
partial detector-null output;
partial response-profile output;
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

## 15. What not to include

Do not include in this run:

```text
X-Token-style projection matrices between gauge views;
graph perturbation;
channel-edge targeting;
holdout;
n=6;
alphabet expansion;
full gauge-shadow spec;
agents, valuers, identities, or Omega labels.
```

## 16. 3P check

### Principled

Horizon transport follows from the hypothesis that Omega is a horizon-indexed future-field object.

### Parsimonious

This run expands one directional matrix family and one matched-null suite rather than adding new semantic labels or hand-built candidate categories.

### Predictive

A useful horizon-transport object should continue to separate from matched marginal nulls and produce structured response profiles under tiny nonlethal perturbations.

If it does not, it should not be promoted.

## 17. Bottom line

The next run should ask:

```text
Does the horizon-transport object remain interesting when modestly expanded,
while preserving matched marginal detector nulls and response-profile separation?
```

A positive result earns more horizon-transport work.

It does not earn candidate promotion, graph perturbation, or Omega claims.

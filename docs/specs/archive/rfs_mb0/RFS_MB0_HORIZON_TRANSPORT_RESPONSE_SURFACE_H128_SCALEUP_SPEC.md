# RFS-MB0 Horizon-Transport Response Surface H128 Scaleup Spec

Status: design-set response-surface scaleup spec
Builds on: `docs/specs/archive/rfs_mb0/RFS_MB0_HORIZON_TRANSPORT_EXPANSION_SMOKE_SPEC.md` and `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_horizon_transport_response_resolution_scaleup_result.md`
Claim boundary: no holdout scoring, no candidate promotion, no Omega detection, no agency detection, no identity detection, no valuer detection

## 0. One-sentence purpose

Map the horizon-dependent response surface of matched-marginal-separated horizon transport out to `H=128`, while distinguishing aligned amplification from true control-equivalence and guarding against terminal saturation.

This is a design-set instrument/response-surface run, not a validation run.

## 1. Why this run exists

The response-resolution scaleup produced the strongest horizon-transport signal so far:

```text
matched-marginal-separated horizon transport persisted at larger design-set scale;
small perturbations stayed transport_stable;
stronger p0.015/p0.02 nonlethal perturbations produced high-alignment mass-growth responses;
those responses concentrated in mid/downstream horizon pairs:
  8->16
  16->24
  24->32
```

The current result suggests:

```text
horizon depth is loadbearing;
perturbation changes futures without necessarily destroying them;
response classes need more resolution;
terminal saturation must be measured before longer-horizon evidence is trusted.
```

Therefore this run expands horizon reach to `H=128` and maps the perturbation response surface across strength and horizon depth.

## 2. Claim boundary

Allowed claims:

```text
horizon-transport matrices did or did not build with adequate coverage out to H=128;
matched marginal detector nulls did or did not separate from observed transport;
response classes did or did not vary by perturbation strength and horizon;
terminal saturation did or did not dominate extended horizons;
contexts are or are not worth further scaleup or narrowing.
```

Forbidden claims:

```text
Omega detected;
agent detected;
valuer detected;
identity detected;
candidate promoted;
holdout ready;
graph-channel causality shown;
direct channel diagnostics justified by this run alone.
```

Required counters:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## 3. X-Token and projection-guided alignment exclusion

Do not include X-Token-style projection matrices or projection-guided gauge alignment in this run.

X-Token remains methodologically relevant later for:

```text
projection maps between incompatible gauge views;
coverage audits before choosing alignment objectives;
relaxed matching when exact equality is too brittle.
```

But this run must test one live object:

```text
horizon_transport
```

Do not add view-projection matrices, learned or heuristic `W`, or cross-view projection losses here.

## 4. Required response taxonomy repair

The previous run placed high-alignment mass-growth rows into `transport_control_equivalent`. That name is too broad.

Add a response class:

```text
transport_amplified_aligned
```

Definition:

```text
baseline-to-perturbed subspace alignment remains high;
transport/spectral mass grows substantially;
matched marginal detector nulls still separate;
no collapse;
no weakening;
no rerouting;
no reopening.
```

Reserve:

```text
transport_control_equivalent
```

for cases where detector-null or matched-null controls reproduce the same response profile.

Required response classes after repair:

```text
transport_stable
transport_amplified_aligned
transport_weakened
transport_rerouted
transport_reopens
transport_collapses
transport_control_equivalent
transport_resolution_mismatch
transport_response_underpowered
```

## 5. Required fixture expansion before interpreting new classes

Before treating response classes as meaningful, add or run fixtures for:

```text
transport_amplified_aligned
transport_weakened
transport_rerouted
transport_reopens
```

Existing fixture classes:

```text
block_transport_signal
marginal_fakeout
corridor_stable_response
trap_collapse_response
```

Fixture role:

```text
calibration only;
not empirical evidence;
not Omega evidence;
not candidate evidence.
```

Fixture gate:

```text
If any required new response fixture fails, the empirical response class may be emitted as exploratory_only but must not support scaleup readiness.
```

## 6. Horizon-forward run design

Prioritize horizon surface area even if it costs compute.

Required local horizon pairs:

```text
0->1
1->2
2->4
4->8
8->16
16->24
24->32
```

Required extended horizon pairs, if the runner can build them without undercoverage:

```text
32->48
48->64
64->96
96->128
```

Aggregate horizon bands, if feasible:

```text
short->middle
middle->downstream
downstream->extended
short->extended
```

Extended horizons are diagnostic unless saturation gates pass.

## 7. Terminal saturation diagnostics

Long horizon extension to `H=128` is allowed only with explicit saturation reporting.

Required fields:

```text
horizon_pair
terminal_saturation_flag
frontier_support_saturation
transport_entropy_saturation
row_support_saturation
column_support_saturation
row_column_support_saturation
mass_concentration_saturation
largest_entry_mass_share
row_max_mass_share
column_max_mass_share
transport_entropy
transport_entropy_delta_vs_previous_horizon
support_delta_vs_previous_horizon
horizon_pair_undercoverage_flag
allowed_interpretation_level
```

Allowed `allowed_interpretation_level` values:

```text
normal_horizon_response
terminal_saturation_diagnostic_only
undercovered_diagnostic_only
not_interpretable
```

Rule:

```text
If terminal saturation dominates 64->96 or 96->128, those rows are diagnostic only and cannot support scaleup readiness.
```

## 8. Horizon response threshold table

Emit a threshold table by perturbation family, perturbation strength, probe, and flow mode.

Required fields:

```text
perturbation_family
perturbation_strength
probe_key
flow_mode
first_nonstable_horizon
first_amplified_aligned_horizon
first_weakened_horizon
first_rerouted_horizon
first_reopened_horizon
first_collapsed_horizon
terminal_saturation_horizon
latest_interpretable_horizon
```

This table is more important than a global response-count summary.

## 9. Run scale

Use enough compute to work the hardware, but preserve design-set-only status.

Suggested default:

```text
groups: 36 to 48
design_groups: 12 to 16
fresh_seeds_per_group: 6
start_samples_list: 2,4,8,16
null_replicates: 11 or 15
workers: machine appropriate
max_runtime_seconds: 21600
shutdown_cushion_seconds: 1800
```

If the first run is still trivial and all gates pass, a second same-day run may increase:

```text
groups up to 64;
design_groups up to 20;
fresh_seeds_per_group up to 8;
null_replicates up to 15.
```

Do not change substrate alphabet or open holdout.

## 10. Perturbation ladder

Required perturbation families:

```text
small_edge_resample_control
asymmetric_edge_flip_control
```

Required strengths:

```text
0.006
0.008
0.010
0.012
0.015
0.020
0.030
```

Optional boundary strength:

```text
0.040
```

If `0.040` is included, label it:

```text
intervention_class: lethal_boundary_probe or boundary_probe
interpretation_role: viability_boundary_mapping
allowed_claim_level: viability_boundary_only
```

unless prior rows show it remains within the nonlethal envelope.

## 11. Detector-null controls

Matched marginal detector nulls remain mandatory.

Required detector-null families:

```text
context_shuffle_transport_null
horizon_pair_shuffle_transport_null
row_marginal_matched_transport_null
column_marginal_matched_transport_null
row_column_marginal_matched_transport_null
```

Required detector statistic:

```text
marginal_residual_fraction
```

Also report:

```text
singular_spectral_mass
singular_effective_rank
transport_entropy
transport_concentration
left_subspace_alignment
right_subspace_alignment
```

Detector-null results must be reported by:

```text
probe_key
flow_mode
horizon_pair
condition_id
null_family
```

No global-only pass/fail summary is sufficient.

## 12. Primary outputs

Core outputs:

```text
horizon_transport_h128_run_config.json
horizon_transport_h128_status.json
horizon_transport_h128_progress_checkpoints.csv
horizon_transport_h128_errors.csv
horizon_transport_h128_output_manifest.json
```

Matrix and SVD outputs:

```text
horizon_transport_matrix_manifest.csv
horizon_transport_matrix_summary.csv
horizon_transport_coverage.csv
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

Response outputs:

```text
horizon_transport_perturbation_manifest.csv
horizon_transport_response_profile_summary.csv
horizon_transport_response_classification.csv
horizon_transport_response_flags.csv
response_class_by_strength_and_horizon_pair.csv
horizon_response_threshold_table.csv
```

Saturation outputs:

```text
horizon_transport_terminal_saturation_summary.csv
horizon_transport_saturation_by_horizon_pair.csv
```

Context summaries:

```text
horizon_transport_by_probe_summary.csv
horizon_transport_by_flow_mode_summary.csv
horizon_transport_by_horizon_pair_summary.csv
horizon_transport_context_recommendation.csv
```

Fixture outputs:

```text
horizon_transport_fixture_results.csv
horizon_transport_response_fixture_summary.csv
```

Final report:

```text
rfs_mb0_horizon_transport_response_surface_h128_scaleup_result.md
```

## 13. Final report requirements

Retain a compact result note under:

```text
docs/research_notes/validation_results/rfs_mb0/rfs_mb0_horizon_transport_response_surface_h128_scaleup_result.md
```

Required sections:

```text
1. Executive summary
2. Claim boundary
3. Run shape and local artifact policy
4. Response taxonomy fixture status
5. Matrix coverage and horizon-pair coverage
6. Detector-null and matched-marginal results
7. Terminal saturation diagnostics
8. Response class by strength and horizon pair
9. Horizon response threshold table
10. Probe / flow / horizon context summary
11. Readiness levels
12. Next-action fork
13. Output manifest
```

The executive summary must answer:

```text
Did horizon transport remain matched-marginal-separated out to H=128?
Which horizons remained interpretable versus saturated?
At what horizon did responses become nonstable?
Did transport_amplified_aligned replace the previous control-equivalent bucket?
Did any weakened/rerouted/reopened/collapsed classes appear?
What should run next?
```

## 14. Readiness levels

Allowed readiness levels:

```text
ready_for_horizon_transport_scaleup
ready_for_horizon_transport_context_narrowing
ready_for_response_fixture_repair
ready_for_direct_channel_diagnostics
ready_for_horizon_transport_theory_note
not_ready_repair_required
measurement_limits_note_recommended
```

Decision rules:

```text
ready_for_horizon_transport_scaleup:
  matched marginal nulls pass across multiple primary contexts;
  response classes are interpretable;
  terminal saturation does not dominate the decisive horizons;
  at least one nonstable class is resolved cleanly.

ready_for_horizon_transport_context_narrowing:
  a subset of horizon/probe/flow contexts is promising but aggregate read is mixed.

ready_for_response_fixture_repair:
  empirical response classes appear but fixture support is incomplete or failed.

ready_for_direct_channel_diagnostics:
  only if horizon transport remains matched-null-separated and response profiles suggest localized functional dependence; unlikely from this run alone.

ready_for_horizon_transport_theory_note:
  if H=128 reveals a clear horizon-dependent phase pattern worth documenting before further engineering.

not_ready_repair_required:
  detector nulls fail, output contract breaks, terminal saturation dominates, or coverage is inadequate.

measurement_limits_note_recommended:
  horizon transport becomes control-equivalent or terminally saturated across decisive contexts.
```

## 15. Next-action forks

Emit exactly one next-action fork:

```text
expand_horizon_transport_scale
narrow_to_horizon_response_context
repair_response_taxonomy_fixtures
extend_or_trim_horizon_range
return_to_direct_channel_diagnostics
write_horizon_transport_theory_note
write_horizon_transport_measurement_limits_note
```

No next-action fork may directly open holdout or candidate promotion.

## 16. Graceful exit

Runner must support:

```text
status.json at start;
periodic status updates;
progress checkpoint CSV;
SIGINT/SIGTERM/SIGBREAK handling;
shutdown cushion;
partial matrix finalization;
partial detector-null output;
partial response-profile output;
partial saturation output;
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
PARTIAL_SATURATION_DIAGNOSTIC_INCOMPLETE
FAILED_WITH_ERRORS
```

## 17. What not to include

Do not include:

```text
holdout;
n=6;
alphabet expansion;
X-Token projection maps;
graph perturbation;
direct channel diagnostics;
candidate naming;
Omega/agency/value labels;
full gauge-shadow spec.
```

## 18. 3P check

### Principled

The run treats horizon as a primary axis because Omega is a horizon-indexed future-field object.

### Parsimonious

The run keeps one matrix family, one matched-null suite, one graded perturbation ladder, and a repaired response taxonomy.

### Predictive

A useful horizon-transport object should show systematic response thresholds by perturbation strength and horizon depth, while remaining separated from matched marginal nulls.

If it does not, the branch should narrow, repair, or stop.

## 19. Bottom line

This run should answer:

```text
Does matched-marginal-separated horizon transport show a structured response surface out to H=128,
or does terminal saturation / control equivalence erase the signal?
```

A positive result earns further horizon-transport work.

It does not earn holdout, graph perturbation, candidate promotion, or Omega claims.
